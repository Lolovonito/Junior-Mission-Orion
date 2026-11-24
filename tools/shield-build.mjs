#!/usr/bin/env node
/**
 * Pipeline de blindaje multicapa para Junior Mission Orión (Web + Desktop .exe)
 *
 * Funciones principales:
 *  1. Sanea cualquier secreto quemado (ej. Groq API Key gsk_...) y redirige Robbie IA al Proxy Worker.
 *  2. Separa librerías gráficas (Three.js/Shaders) y diccionario I18N para mantener 60 FPS en WebGL,
 *     minificándolos con Terser sin inflarlos.
 *  3. Elimina comentarios y ofusca los 44 módulos propietarios JSM.* con javascript-obfuscator
 *     (cifrado RC4 de cadenas, bloqueo de formateo selfDefending, flujo ofuscado y Domain Lock).
 *  4. Inyecta guardián de entorno en tiempo de ejecución (anti-iframe, bloqueo F12/DevTools/clic derecho,
 *     validación de puente nativo __ORION_NATIVE_SEAL__ en modo desktop).
 *  5. En modo web, empaqueta DOM + código en un contenedor cifrado con AES-256-GCM (assets/orion.<hash>.pak)
 *     junto a un index.html bootstrapper mínimo ofuscado que descifra en RAM y revoca Blob URLs al instante.
 */

import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import zlib from "node:zlib";
import { fileURLToPath } from "node:url";
import { minify } from "terser";
import JavaScriptObfuscator from "javascript-obfuscator";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");

const DEFAULT_WEB_DOMAINS = [
  "orionbeta-165b9.web.app",
  "orionbeta-165b9.firebaseapp.com",
  "junior-mission-orion.web.app",
  "junior-mision-orion.web.app"
];

function parseArgs(argv) {
  const opts = {
    target: "web",
    allowLocalhost: false,
    input: path.join(ROOT, "index.html"),
    proxyUrl: process.env.ORION_AI_PROXY_URL || "",
    extraDomains: []
  };
  for (const arg of argv) {
    if (arg.startsWith("--target=")) {
      opts.target = arg.slice("--target=".length).trim();
    } else if (arg === "--allow-localhost") {
      opts.allowLocalhost = true;
    } else if (arg.startsWith("--input=")) {
      opts.input = path.resolve(ROOT, arg.slice("--input=".length).trim());
    } else if (arg.startsWith("--proxy-url=")) {
      opts.proxyUrl = arg.slice("--proxy-url=".length).trim();
    } else if (arg.startsWith("--domains=")) {
      opts.extraDomains = arg
        .slice("--domains=".length)
        .split(",")
        .map((s) => s.trim())
        .filter(Boolean);
    }
  }
  if (opts.target !== "web" && opts.target !== "desktop") {
    throw new Error(`--target inválido: '${opts.target}'. Usa 'web' o 'desktop'.`);
  }
  return opts;
}

function extractHtmlParts(html) {
  const headMatch = html.match(/<head[^>]*>([\s\S]*?)<\/head>/i);
  const bodyOpenMatch = html.match(/<body[^>]*>/i);
  const bodyCloseIdx = html.lastIndexOf("</body>");
  if (!headMatch || !bodyOpenMatch || bodyCloseIdx === -1) {
    throw new Error("El HTML fuente no tiene una estructura <head>/<body> válida.");
  }

  const headInner = headMatch[1];
  const bodyStartIdx = bodyOpenMatch.index + bodyOpenMatch[0].length;

  const scripts = [];
  const scriptRegex = /<script([^>]*)>([\s\S]*?)<\/script>/gi;
  let firstScriptStart = -1;
  let m;
  while ((m = scriptRegex.exec(html)) !== null) {
    if (firstScriptStart === -1) firstScriptStart = m.index;
    scripts.push(m[2]);
  }
  if (scripts.length !== 53) {
    console.warn(`[AVISO] Se esperaban 53 bloques <script> y se encontraron ${scripts.length}. Verificando estructura...`);
  }
  if (firstScriptStart < bodyStartIdx) {
    throw new Error("Se detectaron etiquetas <script> fuera del orden esperado en <body>.");
  }

  let bodyHtml = html.slice(bodyStartIdx, firstScriptStart);
  // Eliminar comentarios HTML que filtran notas del desarrollador
  bodyHtml = bodyHtml.replace(/<!--[\s\S]*?-->/g, "").trim();

  return { headInner, bodyHtml, scripts };
}

function sanitizeSecretsAndPatchAI(code, proxyUrl) {
  let out = code;
  const safeProxy = JSON.stringify(proxyUrl || "");

  // 1. Eliminar la definición con clave Groq quemada (renombrando constantes globales)
  const keyDeclRe =
    /const\s+GROQ_API_KEY\s*=\s*\([^)]*localStorage\.getItem\("JSM_GROQ_KEY"\)\)\s*\|\|\s*"(?:gsk_[A-Za-z0-9]+)?";/;
  if (!keyDeclRe.test(out)) {
    throw new Error("No se encontró el bloque GROQ_API_KEY esperado para sanear.");
  }
  out = out.replace(
    keyDeclRe,
    `const _o_k = (typeof localStorage !== "undefined" && localStorage.getItem("JSM_GROQ_KEY")) || "";\nconst _o_p = (typeof window !== "undefined" && window.ORION_AI_PROXY_URL) || ${safeProxy};`
  );

  // 2. Redirigir endpoint al proxy si no existe clave personal en localStorage
  const urlDeclRe = /const\s+GROQ_API_URL\s*=\s*"https:\/\/api\.groq\.com\/openai\/v1\/chat\/completions";/;
  if (!urlDeclRe.test(out)) {
    throw new Error("No se encontró GROQ_API_URL esperado para redirigir al proxy.");
  }
  out = out.replace(
    urlDeclRe,
    `const _o_u = _o_k ? "https://api.groq.com/openai/v1/chat/completions" : _o_p;`
  );

  // 3. Permitir consulta en chat usando Proxy Worker o modo educativo local si aún no se configura proxy
  const chatCheckRe =
    /if\s*\(!GROQ_API_KEY\)\s*\{\s*throw new Error\('Falta API Key de Groq'\);\s*\}\s*const response = await fetch\(GROQ_API_URL,\s*\{\s*method:\s*"POST",\s*headers:\s*\{\s*"Authorization":\s*"Bearer "\s*\+\s*GROQ_API_KEY,\s*"Content-Type":\s*"application\/json"\s*\},/;
  if (!chatCheckRe.test(out)) {
    throw new Error("No se encontró el bloque fetch del chat de Robbie para parchear.");
  }
  out = out.replace(
    chatCheckRe,
    `const _localRobbieReply = (q) => {
          const s = String(q || "").toLowerCase();
          if (/oxigeno|oxígeno|o2|eclss|respirar|aire/.test(s)) return "En la Luna y Marte no hay aire respirable.\\nUsa el Generador de O2 y los invernaderos hidropónicos para mantener estable el soporte vital estilo ECLSS de la NASA.";
          if (/agua|hielo|crater|cráter|shackleton|polo/.test(s)) return "En el Polo Sur Lunar (Cresta Shackleton) hay hielo de agua atrapado en cráteres en sombra permanente.\\nExtrae hielo con el colector y recíclalo como hace la Estación Espacial Internacional.";
          if (/energia|energía|panel|bateria|batería|kilopower|noche|eclipse|reactor/.test(s)) return "Durante los eclipses lunares los paneles solares dejan de producir.\\nCarga tus baterías de respaldo o investiga el reactor de fisión Kilopower para tener 10 kW constantes.";
          if (/marte|moxie|polvo|tormenta|tau/.test(s)) return "En Marte las tormentas de polvo elevan la opacidad óptica tau y ensucian los paneles solares.\\nUsa limpiar en los paneles y recuerda que el experimento MOXIE de la NASA demostró producir O2 desde el CO2 marciano.";
          if (/radiacion|radiación|regolito|mli|frio|frío|temperatura/.test(s)) return "La radiación espacial y el frío extremo (-233 C en cráteres PSR) exigen buena protección.\\nAñade recubrimiento de regolito y aislamiento MLI a tus módulos para reducir hasta 40% la carga térmica.";
          if (/control|tecla|jugar|multijugador|sala|orion|nave|despeg/.test(s)) return "Muévete con WASD o el joystick táctil, interactúa con E, salta con Espacio y abre construcción con B.\\nPuedes explorar en equipo usando salas multijugador por código de 5 letras o QR.";
          return "¡Hola, astronauta! Estoy en modo de sensores locales.\\nPregúntame sobre oxígeno, agua lunar, paneles y reactor Kilopower, Marte y MOXIE, radiación o controles de Junior Mission Orión.";
        };
        const _orionHeaders = { "Content-Type": "application/json" };
        if (_o_k) {
          _orionHeaders["Authorization"] = "Bearer " + _o_k;
        }
        const _orionFetch = (_o_k || _o_u)
          ? (u, init) => fetch(u, init)
          : async () => new Response(
              JSON.stringify({ choices: [{ finish_reason: "stop", message: { content: _localRobbieReply(userText) } }] }),
              { status: 200, headers: { "Content-Type": "application/json" } }
            );
        const response = await _orionFetch(_o_u, {
          method: "POST",
          headers: _orionHeaders,`
  );

  // 4. Actualizar fetchRobbieTip para soportar proxy serverless además de clave personal
  const tipFetchRe =
    /const key = \(typeof GROQ_API_KEY !== 'undefined' && GROQ_API_KEY\) \|\| '';\s*if \(!key\) return null;\s*const res = await fetch\('https:\/\/api\.groq\.com\/openai\/v1\/chat\/completions',\s*\{\s*method:\s*'POST',\s*headers:\s*\{\s*'Authorization':\s*'Bearer '\s*\+\s*key,\s*'Content-Type':\s*'application\/json'\s*\},/;
  if (!tipFetchRe.test(out)) {
    throw new Error("No se encontró fetchRobbieTip para parchear.");
  }
  out = out.replace(
    tipFetchRe,
    `const key = (typeof _o_k !== 'undefined' && _o_k) || '';
      const proxy = (typeof _o_p !== 'undefined' && _o_p) || '';
      if (!key && !proxy) return null;
      const targetUrl = key ? 'https://api.groq.com/openai/v1/chat/completions' : proxy;
      const tipHeaders = { 'Content-Type': 'application/json' };
      if (key) tipHeaders['Authorization'] = 'Bearer ' + key;
      const res = await fetch(targetUrl, {
        method: 'POST',
        headers: tipHeaders,`
  );

  // 5. Renombrar ROBBIE_SYSTEM y hacer barrido final de tokens gsk_
  out = out.replace(/\bROBBIE_SYSTEM\b/g, "_o_s");
  out = out.replace(/gsk_[A-Za-z0-9]{15,}/g, "");
  return out;
}

function buildRuntimeGuardian({ target, domains }) {
  const allowedDomainsJson = JSON.stringify(domains);
  if (target === "desktop") {
    return `(function(){
  'use strict';
  try {
    var proto = String(location.protocol || '');
    var host = String(location.hostname || '');
    var okHost = (host === 'orion.localhost' || proto === 'orion:');
    var hasSeal = typeof window.__ORION_NATIVE_SEAL__ === 'string' && window.__ORION_NATIVE_SEAL__.length >= 16;
    if (!okHost || !hasSeal) {
      document.documentElement.innerHTML = '';
      throw new Error('Entorno no autorizado');
    }
    window.addEventListener('contextmenu', function(e){ e.preventDefault(); }, true);
    document.addEventListener('keydown', function(e){
      var k = (e.key || '').toUpperCase();
      var c = e.ctrlKey || e.metaKey;
      if (k === 'F12' || (c && e.shiftKey && (k === 'I' || k === 'J' || k === 'C' || k === 'K')) || (c && (k === 'U' || k === 'S' || k === 'P'))) {
        e.preventDefault(); e.stopPropagation();
      }
    }, true);
    window.__ORION_WATERMARK__ = 'JMO-V29-DESKTOP-CHOYEROS';
  } catch (err) { throw err; }
})();\n`;
  }

  return `(function(){
  'use strict';
  try {
    if (window.top !== window.self) {
      try { window.top.location = window.location.href; } catch (_e) {}
      document.documentElement.innerHTML = '';
      throw new Error('Embed bloqueado');
    }
    var allowed = ${allowedDomainsJson};
    var h = String(location.hostname || '').toLowerCase();
    if (allowed.length && allowed.indexOf(h) === -1) {
      document.documentElement.innerHTML = '';
      throw new Error('Dominio no autorizado');
    }
    window.addEventListener('contextmenu', function(e){ e.preventDefault(); }, true);
    document.addEventListener('keydown', function(e){
      var k = (e.key || '').toUpperCase();
      var c = e.ctrlKey || e.metaKey;
      if (k === 'F12' || (c && e.shiftKey && (k === 'I' || k === 'J' || k === 'C' || k === 'K')) || (c && (k === 'U' || k === 'S'))) {
        e.preventDefault(); e.stopPropagation();
      }
    }, true);
    window.__ORION_WATERMARK__ = 'JMO-V29-WEB-CHOYEROS';
  } catch (err) { throw err; }
})();\n`;
}

async function minifyVendor(code, label) {
  const res = await minify(code, {
    compress: {
      passes: 2,
      drop_debugger: true
    },
    mangle: true,
    format: {
      comments: false
    }
  });
  if (!res || typeof res.code !== "string") {
    throw new Error(`Terser falló en ${label}`);
  }
  return res.code;
}

async function stripAndPrepareCore(code, label) {
  // Pre-limpieza con Terser para remover comentarios en español y acortar antes de ofuscar
  const res = await minify(code, {
    compress: {
      passes: 1,
      dead_code: false,
      unused: false
    },
    mangle: false,
    format: {
      comments: false
    }
  });
  if (!res || typeof res.code !== "string") {
    throw new Error(`Terser pre-core falló en ${label}`);
  }
  return res.code;
}

function obfuscateCore(code, { domains, enableDomainLock }) {
  const options = {
    compact: true,
    controlFlowFlattening: true,
    controlFlowFlatteningThreshold: 0.12,
    deadCodeInjection: false,
    debugProtection: false,
    disableConsoleOutput: false,
    identifierNamesGenerator: "hexadecimal",
    log: false,
    numbersToExpressions: false,
    renameGlobals: false,
    selfDefending: true,
    simplify: true,
    splitStrings: true,
    splitStringsChunkLength: 16,
    stringArray: true,
    stringArrayCallsTransform: true,
    stringArrayCallsTransformThreshold: 0.55,
    stringArrayEncoding: ["rc4"],
    stringArrayIndexShift: true,
    stringArrayRotate: true,
    stringArrayShuffle: true,
    stringArrayWrappersCount: 1,
    stringArrayWrappersChainedCalls: true,
    stringArrayWrappersType: "function",
    stringArrayThreshold: 0.65,
    transformObjectKeys: false,
    unicodeEscapeSequence: false
  };

  if (enableDomainLock && domains.length > 0) {
    options.domainLock = domains;
    options.domainLockRedirectUrl = "about:blank";
  }

  return JavaScriptObfuscator.obfuscate(code, options).getObfuscatedCode();
}

function assertValidJsSyntax(code, label) {
  try {
    new vm.Script(code, { filename: label });
  } catch (err) {
    throw new Error(`Error de sintaxis en ${label}: ${err.message}`);
  }
}

function xorAndSplitKey(keyBytes) {
  const mask = crypto.randomBytes(32);
  const masked = Buffer.alloc(32);
  for (let i = 0; i < 32; i++) masked[i] = keyBytes[i] ^ mask[i];
  return {
    mA: Array.from(masked.subarray(0, 16)),
    mB: Array.from(masked.subarray(16, 32)),
    xA: Array.from(mask.subarray(0, 16)),
    xB: Array.from(mask.subarray(16, 32))
  };
}

function buildWebBootstrapper({ shardUrls, keyParts, ivBytes, allowedDomains }) {
  const rawBoot = `(function(){
  'use strict';
  var allowed = ${JSON.stringify(allowedDomains)};
  var host = String(location.hostname || '').toLowerCase();
  function block(msg){
    var el = document.getElementById('boot-status');
    if (el) el.textContent = msg;
    throw new Error(msg);
  }
  if (window.top !== window.self) block('Vista incrustada no permitida.');
  if (navigator.webdriver) block('Automatizacion no permitida.');
  if (allowed.length && allowed.indexOf(host) === -1) block('Dominio no autorizado.');
  if (!window.crypto || !window.crypto.subtle) block('Se requiere HTTPS seguro (WebCrypto).');
  if (typeof DecompressionStream !== 'function') block('Navegador sin soporte de DecompressionStream.');

  window.addEventListener('contextmenu', function(e){ e.preventDefault(); }, true);
  document.addEventListener('keydown', function(e){
    var k = (e.key || '').toUpperCase();
    var c = e.ctrlKey || e.metaKey;
    if (k === 'F12' || (c && e.shiftKey && (k === 'I' || k === 'J' || k === 'C' || k === 'K')) || (c && (k === 'U' || k === 'S'))) {
      e.preventDefault(); e.stopPropagation();
    }
  }, true);

  function installReadyShim() {
    var origDocAdd = document.addEventListener.bind(document);
    document.addEventListener = function(type, listener, opts) {
      if (type === 'DOMContentLoaded' && document.readyState !== 'loading' && typeof listener === 'function') {
        Promise.resolve().then(function(){ listener.call(document, new Event('DOMContentLoaded')); });
        return;
      }
      return origDocAdd(type, listener, opts);
    };
    var origWinAdd = window.addEventListener.bind(window);
    window.addEventListener = function(type, listener, opts) {
      if (type === 'load' && document.readyState === 'complete' && typeof listener === 'function') {
        Promise.resolve().then(function(){ listener.call(window, new Event('load')); });
        return;
      }
      return origWinAdd(type, listener, opts);
    };
  }

  function runChunk(code) {
    return new Promise(function(resolve, reject) {
      var blob = new Blob([code], { type: 'application/javascript' });
      var url = URL.createObjectURL(blob);
      var s = document.createElement('script');
      s.src = url;
      s.onload = function() { URL.revokeObjectURL(url); s.remove(); resolve(); };
      s.onerror = function() { URL.revokeObjectURL(url); s.remove(); reject(new Error('Error cargando modulo')); };
      document.body.appendChild(s);
    });
  }

  (async function boot() {
    try {
      var shards = ${JSON.stringify(shardUrls)};
      var buffers = await Promise.all(shards.map(function(u) {
        return fetch(u, { cache: 'force-cache' }).then(function(r) {
          if (!r.ok) throw new Error('HTTP ' + r.status);
          return r.arrayBuffer();
        });
      }));
      var totalLen = 0;
      for (var b = 0; b < buffers.length; b++) totalLen += buffers[b].byteLength;
      var enc = new Uint8Array(totalLen);
      var offset = 0;
      for (var j = 0; j < buffers.length; j++) {
        enc.set(new Uint8Array(buffers[j]), offset);
        offset += buffers[j].byteLength;
      }
      var mA = ${JSON.stringify(keyParts.mA)};
      var mB = ${JSON.stringify(keyParts.mB)};
      var xA = ${JSON.stringify(keyParts.xA)};
      var xB = ${JSON.stringify(keyParts.xB)};
      var rawKey = new Uint8Array(32);
      for (var i = 0; i < 16; i++) {
        rawKey[i] = mA[i] ^ xA[i];
        rawKey[16 + i] = mB[i] ^ xB[i];
      }
      var iv = new Uint8Array(${JSON.stringify(Array.from(ivBytes))});
      var cryptoKey = await crypto.subtle.importKey('raw', rawKey, { name: 'AES-GCM' }, false, ['decrypt']);
      rawKey.fill(0);
      var plainBuf = await crypto.subtle.decrypt({ name: 'AES-GCM', iv: iv }, cryptoKey, enc);
      var ds = new DecompressionStream('gzip');
      var stream = new Blob([plainBuf]).stream().pipeThrough(ds);
      var payload = await new Response(stream).json();
      installReadyShim();
      document.body.innerHTML = payload.bodyHtml;
      for (var idx = 0; idx < payload.chunks.length; idx++) {
        await runChunk(payload.chunks[idx]);
      }
      document.dispatchEvent(new Event('DOMContentLoaded'));
      window.dispatchEvent(new Event('load'));
    } catch (e) {
      block('Error verificando integridad: ' + (e && e.message ? e.message : e));
    }
  })();
})();`;

  return JavaScriptObfuscator.obfuscate(rawBoot, {
    compact: true,
    controlFlowFlattening: true,
    controlFlowFlatteningThreshold: 0.4,
    identifierNamesGenerator: "hexadecimal",
    numbersToExpressions: true,
    renameGlobals: false,
    selfDefending: true,
    stringArray: true,
    stringArrayEncoding: ["rc4"],
    stringArrayRotate: true,
    stringArrayShuffle: true,
    stringArrayThreshold: 0.85,
    transformObjectKeys: false
  }).getObfuscatedCode();
}

async function run() {
  const opts = parseArgs(process.argv.slice(2));
  const rawHtml = fs.readFileSync(opts.input, "utf8");
  const { headInner, bodyHtml, scripts } = extractHtmlParts(rawHtml);

  const domains = [...new Set([...DEFAULT_WEB_DOMAINS, ...opts.extraDomains])];
  if (opts.allowLocalhost) {
    domains.push("localhost", "127.0.0.1");
  }

  console.log(`[shield-build] Objetivo=${opts.target} | Scripts=${scripts.length} | Localhost=${opts.allowLocalhost}`);

  // Clasificar manteniendo orden de ejecución estricto:
  // Chunk 0: Three.js + Shaders (#0..#6) -> Terser
  // Chunk 1: Sistema central I18N (#7) -> Terser + JSObfuscator
  // Chunk 2: Diccionario I18N en-US (#8) -> Terser
  // Chunk 3: Lógica completa del juego + JSM_SERVER (#9..end) -> Saneamiento + Guardián + Terser + JSObfuscator
  const i18nDictIdx = scripts.findIndex((s) => s.includes("JSM.I18N.addPhrases('en-US'"));
  if (i18nDictIdx !== 8) {
    throw new Error(`El diccionario I18N se esperaba en el índice 8 y está en ${i18nDictIdx}.`);
  }

  const vendorThreeRaw = scripts.slice(0, 7).join(";\n");
  const coreI18nRaw = scripts[7];
  const vendorDictRaw = scripts[8];
  const coreGameRaw = sanitizeSecretsAndPatchAI(scripts.slice(9).join(";\n"), opts.proxyUrl);

  const guardian = buildRuntimeGuardian({ target: opts.target, domains });
  const enableDomainLock = opts.target === "web" && !opts.allowLocalhost;

  console.log("[shield-build] Minificando módulos gráficos y diccionario con Terser...");
  const chunk0 = await minifyVendor(vendorThreeRaw, "vendor-three");
  const chunk2 = await minifyVendor(vendorDictRaw, "vendor-i18n-dict");

  console.log("[shield-build] Preparando y ofuscando núcleo JSM.*...");
  const core1Prepared = await stripAndPrepareCore(coreI18nRaw, "core-i18n");
  const core3Prepared = await stripAndPrepareCore(guardian + "\n" + coreGameRaw, "core-game");

  const chunk1 = obfuscateCore(core1Prepared, { domains, enableDomainLock });
  const chunk3 = obfuscateCore(core3Prepared, { domains, enableDomainLock });

  // Validar sintaxis de los 4 chunks generados
  assertValidJsSyntax(chunk0, "chunk0-three");
  assertValidJsSyntax(chunk1, "chunk1-i18n");
  assertValidJsSyntax(chunk2, "chunk2-dict");
  assertValidJsSyntax(chunk3, "chunk3-core");

  const chunks = [chunk0, chunk1, chunk2, chunk3];

  // Garantizar cero filtraciones de claves Groq
  for (const c of chunks) {
    if (/gsk_[A-Za-z0-9]{10,}/.test(c)) {
      throw new Error("ABORTADO: Se detectó un token gsk_ residual en la salida.");
    }
  }

  if (opts.target === "web") {
    const outPublicDir = path.join(ROOT, "dist-web", "public");
    const outAssetsDir = path.join(outPublicDir, "assets");
    fs.rmSync(outPublicDir, { recursive: true, force: true });
    fs.mkdirSync(outAssetsDir, { recursive: true });

    const payloadJson = JSON.stringify({ v: 1, bodyHtml, chunks });
    const compressedPayload = zlib.gzipSync(Buffer.from(payloadJson, "utf8"), { level: 9 });
    const key = crypto.randomBytes(32);
    const iv = crypto.randomBytes(12);
    const cipher = crypto.createCipheriv("aes-256-gcm", key, iv);
    const encrypted = Buffer.concat([cipher.update(compressedPayload), cipher.final()]);
    const authTag = cipher.getAuthTag();
    const pakBytes = Buffer.concat([encrypted, authTag]);

    const pakHash = crypto.createHash("sha256").update(pakBytes).digest("hex").slice(0, 10);
    const SHARD_SIZE = 160 * 1024; // 160 KiB por fragmento
    const shardUrls = [];
    for (let offset = 0, idx = 0; offset < pakBytes.length; offset += SHARD_SIZE, idx++) {
      const slice = pakBytes.subarray(offset, Math.min(offset + SHARD_SIZE, pakBytes.length));
      const shardName = `orion.${pakHash}.p${idx}.pak`;
      fs.writeFileSync(path.join(outAssetsDir, shardName), slice);
      shardUrls.push(`/assets/${shardName}`);
    }

    const keyParts = xorAndSplitKey(key);
    key.fill(0);

    const bootJs = buildWebBootstrapper({
      shardUrls,
      keyParts,
      ivBytes: iv,
      allowedDomains: domains
    });
    assertValidJsSyntax(bootJs, "web-bootstrapper");

    const webIndexHtml = `<!doctype html><html lang="es"><head>${headInner}<title>Junior Mission Orión</title><style>html,body{margin:0;height:100%;background:#070A16;color:#EEF2FF;font-family:system-ui,sans-serif}.orion-boot{position:fixed;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;text-align:center}.orion-spin{width:38px;height:38px;border:3px solid rgba(111,182,255,.25);border-top-color:#46E3C6;border-radius:50%;animation:sp .9s linear infinite}@keyframes sp{to{transform:rotate(360deg)}}</style></head><body><div class="orion-boot"><div class="orion-spin"></div><div id="boot-status">Iniciando sistemas Orión...</div></div><script>${bootJs}</script></body></html>`;

    fs.writeFileSync(path.join(outPublicDir, "index.html"), webIndexHtml, "utf8");
    console.log(`[OK] Web blindada en dist-web/public/ (index.html=${Buffer.byteLength(webIndexHtml)} B, ${shardUrls.length} shards orion.${pakHash}.p*.pak = ${pakBytes.length} B gzip+AES-GCM)`);
  } else {
    const outDesktopHtml = path.join(ROOT, "desktop-rust", "assets", "game.html");
    fs.mkdirSync(path.dirname(outDesktopHtml), { recursive: true });

    const scriptTags = chunks
      .map((c) => `<script>${c.replace(/<\/script/gi, "<\\/script")}</script>`)
      .join("\n");
    const cleanupTag = `<script>(function(){try{var s=document.querySelectorAll('script');for(var i=0;i<s.length;i++)s[i].remove();}catch(e){}})();</script>`;
    const desktopHtml = `<!doctype html><html><head>${headInner}</head><body>\n${bodyHtml}\n${scriptTags}\n${cleanupTag}\n</body></html>`;

    fs.writeFileSync(outDesktopHtml, desktopHtml, "utf8");
    console.log(`[OK] Desktop HTML5 blindado en desktop-rust/assets/game.html (${Buffer.byteLength(desktopHtml)} B)`);
  }
}

run().catch((err) => {
  console.error("[ERROR shield-build]", err);
  process.exit(1);
});
