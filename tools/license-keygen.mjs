#!/usr/bin/env node
/**
 * Generador de claves Ed25519 y emisor de licencias offline para Junior Mission Orión (.exe)
 *
 * Uso:
 *   node tools/license-keygen.mjs init
 *     -> Crea keys/orion_license.priv.pem (SECRETO: nunca subir a Git)
 *        y desktop-rust/assets/license_pubkey.hex (para compilar con --features license-gate)
 *
 *   node tools/license-keygen.mjs issue --owner="Escuela Orion" [--days=365] [--hwid=<64hex>] [--out=license.key]
 *     -> Emite un archivo license.key firmado con Ed25519.
 *
 *   node tools/license-keygen.mjs verify <ruta_license.key>
 *     -> Verifica una licencia usando desktop-rust/assets/license_pubkey.hex.
 *
 *   node tools/license-keygen.mjs --selftest
 *     -> Prueba criptográfica temporal sin dejar archivos residuales.
 */

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const PRIV_PATH = path.join(ROOT, "keys", "orion_license.priv.pem");
const PUB_HEX_PATH = path.join(ROOT, "desktop-rust", "assets", "license_pubkey.hex");

function toB64Url(buf) {
  return Buffer.from(buf)
    .toString("base64")
    .replace(/\+/g, "-")
    .replace(/\//g, "_")
    .replace(/=+$/g, "");
}

function fromB64Url(str) {
  const pad = str.length % 4 === 0 ? "" : "=".repeat(4 - (str.length % 4));
  return Buffer.from(str.replace(/-/g, "+").replace(/_/g, "/") + pad, "base64");
}

function extractRawEd25519PubKey(publicKeyObj) {
  // Export SPKI DER (44 bytes: 12-byte ASN.1 header + 32-byte raw Ed25519 public key)
  const spki = publicKeyObj.export({ type: "spki", format: "der" });
  return spki.subarray(spki.length - 32);
}

function spkiFromRawEd25519PubKey(raw32) {
  const header = Buffer.from("302a300506032b6570032100", "hex");
  return crypto.createPublicKey({
    key: Buffer.concat([header, raw32]),
    format: "der",
    type: "spki"
  });
}

function buildToken(privateKeyObj, { owner, days, hwid }) {
  const now = Math.floor(Date.now() / 1000);
  const exp = days > 0 ? now + days * 86400 : 0;
  const nonce = crypto.randomBytes(8).toString("hex");
  const cleanOwner = String(owner || "Invitado").replace(/[\r\n=]/g, " ").trim();
  const cleanHwid = String(hwid || "*").trim().toLowerCase();

  const payload = [
    "v=1",
    "app=junior-mission-orion",
    `owner=${cleanOwner}`,
    `exp=${exp}`,
    `hwid=${cleanHwid}`,
    `nonce=${nonce}`
  ].join("\n");

  const payloadBuf = Buffer.from(payload, "utf8");
  const sigBuf = crypto.sign(null, payloadBuf, privateKeyObj);
  return `ORION1.${toB64Url(payloadBuf)}.${toB64Url(sigBuf)}`;
}

function verifyTokenWithRawPub(token, rawPub32) {
  const parts = String(token || "").trim().split(".");
  if (parts.length !== 3 || parts[0] !== "ORION1") {
    throw new Error("Formato de token inválido (esperado ORION1.payload.firma)");
  }
  const payloadBuf = fromB64Url(parts[1]);
  const sigBuf = fromB64Url(parts[2]);
  const pubObj = spkiFromRawEd25519PubKey(rawPub32);
  const ok = crypto.verify(null, payloadBuf, pubObj, sigBuf);
  if (!ok) {
    throw new Error("Firma Ed25519 inválida");
  }
  const fields = Object.fromEntries(
    payloadBuf
      .toString("utf8")
      .split("\n")
      .filter((l) => l.includes("="))
      .map((l) => {
        const idx = l.indexOf("=");
        return [l.slice(0, idx).trim(), l.slice(idx + 1).trim()];
      })
  );
  if (fields.app !== "junior-mission-orion") {
    throw new Error("La licencia no pertenece a junior-mission-orion");
  }
  const exp = Number(fields.exp || 0);
  if (exp > 0 && Math.floor(Date.now() / 1000) > exp) {
    throw new Error("Licencia expirada");
  }
  return fields;
}

function parseFlags(args) {
  const flags = {};
  for (const arg of args) {
    if (arg.startsWith("--")) {
      const [k, ...rest] = arg.slice(2).split("=");
      flags[k] = rest.length ? rest.join("=") : "true";
    }
  }
  return flags;
}

function runSelfTest() {
  const { publicKey, privateKey } = crypto.generateKeyPairSync("ed25519");
  const rawPub = extractRawEd25519PubKey(publicKey);
  if (rawPub.length !== 32) {
    throw new Error(`Longitud inesperada de clave pública: ${rawPub.length}`);
  }
  const token = buildToken(privateKey, {
    owner: "Test Astronauta",
    days: 30,
    hwid: "*"
  });
  const fields = verifyTokenWithRawPub(token, rawPub);
  if (fields.owner !== "Test Astronauta") {
    throw new Error("Fallo verificando owner del token");
  }
  // Comprobar rechazo de token manipulado
  const tampered = token.slice(0, -2) + (token.endsWith("AA") ? "BB" : "AA");
  let rejected = false;
  try {
    verifyTokenWithRawPub(tampered, rawPub);
  } catch {
    rejected = true;
  }
  if (!rejected) {
    throw new Error("El verificador aceptó una firma alterada");
  }
  console.log("[OK] Selftest Ed25519 superado: generación, firma, verificación y rechazo de manipulación.");
}

const argv = process.argv.slice(2);
if (argv.includes("--selftest")) {
  runSelfTest();
  process.exit(0);
}

const cmd = argv[0];
const flags = parseFlags(argv.slice(1));

if (cmd === "init") {
  if (fs.existsSync(PRIV_PATH) && flags.force !== "true") {
    console.error(`Ya existe ${PRIV_PATH}. Usa --force para sobrescribir (invalidará licencias previas).`);
    process.exit(1);
  }
  fs.mkdirSync(path.dirname(PRIV_PATH), { recursive: true });
  fs.mkdirSync(path.dirname(PUB_HEX_PATH), { recursive: true });
  const { publicKey, privateKey } = crypto.generateKeyPairSync("ed25519");
  const privPem = privateKey.export({ type: "pkcs8", format: "pem" });
  const rawPub = extractRawEd25519PubKey(publicKey);
  fs.writeFileSync(PRIV_PATH, privPem, { mode: 0o600 });
  fs.writeFileSync(PUB_HEX_PATH, rawPub.toString("hex") + "\n", "utf8");
  console.log(`[OK] Clave privada guardada en: ${PRIV_PATH} (NO subir a Git)`);
  console.log(`[OK] Clave pública Ed25519 (32B hex) guardada en: ${PUB_HEX_PATH}`);
} else if (cmd === "issue") {
  if (!fs.existsSync(PRIV_PATH)) {
    console.error(`Falta ${PRIV_PATH}. Ejecuta primero: node tools/license-keygen.mjs init`);
    process.exit(1);
  }
  const privObj = crypto.createPrivateKey(fs.readFileSync(PRIV_PATH, "utf8"));
  const token = buildToken(privObj, {
    owner: flags.owner || "Licencia Oficial",
    days: Number(flags.days || 0),
    hwid: flags.hwid || "*"
  });
  const outPath = path.resolve(ROOT, flags.out || "license.key");
  fs.writeFileSync(outPath, token + "\n", "utf8");
  console.log(`[OK] Licencia firmada generada en: ${outPath}`);
} else if (cmd === "verify") {
  const target = argv[1];
  if (!target || !fs.existsSync(target)) {
    console.error("Uso: node tools/license-keygen.mjs verify <ruta_license.key>");
    process.exit(1);
  }
  if (!fs.existsSync(PUB_HEX_PATH)) {
    console.error(`Falta ${PUB_HEX_PATH}`);
    process.exit(1);
  }
  const rawPub = Buffer.from(fs.readFileSync(PUB_HEX_PATH, "utf8").trim(), "hex");
  const fields = verifyTokenWithRawPub(fs.readFileSync(target, "utf8"), rawPub);
  console.log("[OK] Licencia válida:", fields);
} else {
  console.log("Comandos disponibles: init | issue | verify | --selftest");
}
