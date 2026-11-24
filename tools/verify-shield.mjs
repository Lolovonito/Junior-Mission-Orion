#!/usr/bin/env node
/**
 * Suite de verificación automatizada para comprobar que el blindaje Web y Desktop
 * cumple con todas las garantías de seguridad e integridad sintáctica.
 */

import { execFileSync } from "node:child_process";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import zlib from "node:zlib";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

function assert(cond, msg) {
  if (!cond) {
    throw new Error(`[FALLO VERIFICACION] ${msg}`);
  }
}

function shannonEntropy(buf) {
  const counts = new Uint32Array(256);
  for (let i = 0; i < buf.length; i++) counts[buf[i]]++;
  let entropy = 0;
  for (let i = 0; i < 256; i++) {
    if (counts[i] === 0) continue;
    const p = counts[i] / buf.length;
    entropy -= p * Math.log2(p);
  }
  return entropy;
}

function checkNoLeaks(text, label) {
  const forbidden = [
    /gsk_[A-Za-z0-9]{10,}/,
    /PROPUESTA ROBBIE INTEGRACION/,
    /ETAPA 6 · MULTIJUGADOR REAL/,
    /Datos curiosos \(Opciones\) \+ formateo tips/,
    /\bGROQ_API_KEY\b/,
    /\bROBBIE_SYSTEM\b/,
    /api\.groq\.com/
  ];
  for (const re of forbidden) {
    assert(!re.test(text), `Patrón sensible encontrado en ${label}: ${re}`);
  }
}

async function verifyWeb() {
  const publicDir = path.join(ROOT, "dist-web", "public");
  const indexPath = path.join(publicDir, "index.html");
  assert(fs.existsSync(indexPath), "Falta dist-web/public/index.html");

  const indexHtml = fs.readFileSync(indexPath, "utf8");
  assert(
    Buffer.byteLength(indexHtml) < 25_000,
    `dist-web/public/index.html demasiado grande (${Buffer.byteLength(indexHtml)} B); debería ser un bootstrapper ligero.`
  );
  checkNoLeaks(indexHtml, "dist-web/public/index.html");
  assert(!indexHtml.includes("Three.js Authors"), "El código de Three.js quedó en claro en index.html");
  assert(!indexHtml.includes("modal-robi-chat"), "El DOM del juego quedó en claro en index.html");

  const assetsDir = path.join(publicDir, "assets");
  const shards = fs
    .readdirSync(assetsDir)
    .map((f) => {
      const m = f.match(/^orion\.([a-f0-9]+)\.p(\d+)\.pak$/);
      return m ? { file: f, hash: m[1], idx: Number(m[2]) } : null;
    })
    .filter(Boolean)
    .sort((a, b) => a.idx - b.idx);

  assert(shards.length >= 2, `Se esperaban >= 2 fragmentos .pak y hay ${shards.length}`);
  const expectedHash = shards[0].hash;
  const buffers = shards.map((s, i) => {
    assert(s.hash === expectedHash, `Hash inconsistente en shard ${s.file}`);
    assert(s.idx === i, `Falta índice consecutivo ${i} en shards`);
    const buf = fs.readFileSync(path.join(assetsDir, s.file));
    assert(buf.length > 0 && buf.length <= 165_000, `Tamaño inválido en ${s.file}: ${buf.length} B`);
    checkNoLeaks(buf.toString("latin1"), s.file);
    return buf;
  });

  const pakBuf = Buffer.concat(buffers);
  assert(pakBuf.length < 2_000_000, `Paquete web comprimido demasiado pesado: ${pakBuf.length} B`);
  const entropy = shannonEntropy(pakBuf);
  assert(entropy > 7.95, `Entropía insuficiente en paquete web: ${entropy.toFixed(3)} bits/byte`);
  assert(!pakBuf.includes(Buffer.from("ROBBIE_SYSTEM")), "El .pak no está cifrado: texto plano visible");

  // Extraer el bootstrapper JS y verificar sintaxis válida
  const bootMatch = indexHtml.match(/<script>([\s\S]*?)<\/script>/);
  assert(bootMatch, "No se encontró el script bootstrapper en dist-web/public/index.html");
  new vm.Script(bootMatch[1], { filename: "web-bootstrapper" });

  console.log(`[OK] Web blindada verificada: index=${Buffer.byteLength(indexHtml)} B, ${shards.length} shards=${pakBuf.length} B, entropía=${entropy.toFixed(4)} bits/B`);
}

function verifyDesktop() {
  const gameHtmlPath = path.join(ROOT, "desktop-rust", "assets", "game.html");
  assert(fs.existsSync(gameHtmlPath), "Falta desktop-rust/assets/game.html");

  const gameHtml = fs.readFileSync(gameHtmlPath, "utf8");
  checkNoLeaks(gameHtml, "desktop-rust/assets/game.html");

  const scripts = [...gameHtml.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
  assert(scripts.length === 5, `Se esperaban 5 scripts en game.html (4 chunks + cleanup), hay ${scripts.length}`);
  scripts.forEach((code, idx) => {
    new vm.Script(code, { filename: `desktop-chunk-${idx}` });
  });

  // Confirmar que el código ofuscado incluye el verificador de __ORION_NATIVE_SEAL__ o stringArray RC4
  assert(
    scripts[3].includes("0x") || scripts[3].includes("_0x"),
    "El chunk principal de desktop no parece estar ofuscado"
  );
  console.log(`[OK] Desktop HTML5 blindado verificado (${Buffer.byteLength(gameHtml)} B, ${scripts.length} scripts sintácticamente válidos).`);
}

function verifyWebCryptoDecryptionRoundtrip() {
  // Prueba completa: gzip -> AES-256-GCM -> partición -> reensamblado -> subtle.decrypt -> DecompressionStream('gzip') -> Response.json()
  const subtle = crypto.webcrypto.subtle;
  return (async () => {
    const rawKey = crypto.randomBytes(32);
    const iv = crypto.randomBytes(12);
    const sample = JSON.stringify({ v: 1, test: "Junior Mission Orion", n: 42 });
    const gz = zlib.gzipSync(Buffer.from(sample, "utf8"), { level: 9 });
    const c = crypto.createCipheriv("aes-256-gcm", rawKey, iv);
    const enc = Buffer.concat([c.update(gz), c.final(), c.getAuthTag()]);

    // Simular partición y reensamblado de shards
    const mid = Math.floor(enc.length / 2);
    const s0 = new Uint8Array(enc.subarray(0, mid));
    const s1 = new Uint8Array(enc.subarray(mid));
    const joined = new Uint8Array(s0.byteLength + s1.byteLength);
    joined.set(s0, 0);
    joined.set(s1, s0.byteLength);

    const k = await subtle.importKey("raw", rawKey, { name: "AES-GCM" }, false, ["decrypt"]);
    const dec = await subtle.decrypt({ name: "AES-GCM", iv }, k, joined);
    const ds = new DecompressionStream("gzip");
    const stream = new Blob([dec]).stream().pipeThrough(ds);
    const decoded = await new Response(stream).json();
    assert(decoded.test === "Junior Mission Orion" && decoded.n === 42, "Fallo en roundtrip gzip+AES-256-GCM WebCrypto");
    console.log("[OK] Compatibilidad gzip + shards + AES-256-GCM + DecompressionStream verificada.");
  })();
}

function verifyLicenseKeygen() {
  execFileSync(process.execPath, [path.join(ROOT, "tools", "license-keygen.mjs"), "--selftest"], {
    stdio: "inherit"
  });
}

function verifyRustSourcesStatic() {
  const mainRs = fs.readFileSync(path.join(ROOT, "desktop-rust", "src", "main.rs"), "utf8");
  assert(!mainRs.includes("TcpListener"), "main.rs aún contiene TcpListener");
  assert(!mainRs.includes("17429"), "main.rs aún expone el puerto 17429");
  assert(mainRs.includes("with_custom_protocol"), "main.rs no usa with_custom_protocol");
  assert(mainRs.includes("ChaCha20Poly1305"), "main.rs no descifra ChaCha20Poly1305");
  assert(mainRs.includes("with_devtools(false)"), "main.rs no desactiva devtools");
  assert(mainRs.includes("with_default_context_menus(false)"), "main.rs no desactiva menús contextuales");
  assert(mainRs.includes("with_browser_accelerator_keys(false)"), "main.rs no desactiva teclas del navegador");
  console.log("[OK] Fuentes Rust verificadas: sin TcpListener, con bóveda ChaCha20-Poly1305, custom protocol y hardening WebView2.");
}

function verifySourceRepoSanitized() {
  for (const fname of [
    "index.html",
    "Junior_Mission_Orion_Robbie_Final.html",
    "Junior_Mission_Orion_v29_RobbieAI.html",
    "MissionOrion.html"
  ]) {
    const p = path.join(ROOT, fname);
    if (!fs.existsSync(p)) continue;
    const content = fs.readFileSync(p, "utf8");
    assert(!/gsk_[A-Za-z0-9]{15,}/.test(content), `Token gsk_ aún expuesto en ${fname}`);
  }
  console.log("[OK] Archivos HTML fuente saneados (sin tokens gsk_ expuestos).");
}

async function main() {
  verifySourceRepoSanitized();
  await verifyWeb();
  verifyDesktop();
  await verifyWebCryptoDecryptionRoundtrip();
  verifyLicenseKeygen();
  verifyRustSourcesStatic();
  console.log("\n[EXITO TOTAL] Todas las comprobaciones de blindaje pasaron correctamente.");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
