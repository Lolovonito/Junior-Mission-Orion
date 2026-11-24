# Blindaje Integral (Web + `.exe`) — Junior Mission Orión

> **ACCIÓN INMEDIATA REQUERIDA**
> 1. **Revoca y rota la API Key de Groq** (`gsk_TllM5qA7...`) que estaba expuesta en texto plano en `index.html` y las copias HTML del repositorio público. Coloca la nueva clave únicamente con `npx wrangler secret put GROQ_API_KEY` dentro de `cloudflare-worker/`.
> 2. **Pasa el repositorio `Lolovonito/Junior-Mission-Orion` a privado** (`gh repo edit Lolovonito/Junior-Mission-Orion --visibility private`) y retira los HTML originales sin ofuscar de GitHub Releases.

---

## Archivos creados y modificados

- `tools/shield-build.mjs`: Pipeline unificado `--target=web` y `--target=desktop` (sanea secretos, minifica Three.js/diccionario con `terser`, ofusca módulos `JSM.*` con `javascript-obfuscator`, agrega Domain Lock y guardián anti-iframe/anti-DevTools, y empaqueta la web cifrada en AES-256-GCM).
- `tools/verify-shield.mjs`: Verificación de ausencia de fugas, sintaxis `vm.Script`, entropía de `.pak`, roundtrip WebCrypto, autoprueba Ed25519 y chequeo estático de `desktop-rust`.
- `tools/license-keygen.mjs`: Generador de claves y emisor/verificador de licencias Ed25519 offline (`license.key`).
- `firebase.json`: Publicación desde `dist-web/public`, `X-Frame-Options: DENY`, CSP con `frame-ancestors 'none'`, `nosniff` y políticas de caché.
- `cloudflare-worker/robbie-proxy.js` y `cloudflare-worker/wrangler.toml`: Proxy serverless para Robbie IA sin exponer la API key al cliente.
- `desktop-rust/`: Eliminado el servidor HTTP `127.0.0.1:17429`; agregada bóveda cifrada Zlib + ChaCha20-Poly1305 (`build.rs` + `main.rs`), protocolo nativo `orion://`, limpieza de variables `WEBVIEW2_*`, bloqueo de DevTools/contextmenu/aceleradores, anti-debug Windows (`security.rs`) y puerta de licencias Ed25519 opcional `--features license-gate` (`license.rs`).
- `.github/workflows/build-protected-exe.yml`: Flujo de GitHub Actions en `windows-latest` para compilar automáticamente el `.exe` blindado y el paquete Web.

---

## Comandos rápidos

```bash
# 1. Reconstruir y verificar ambos objetivos (opcional: --proxy-url="https://tu-worker.workers.dev")
npm run shield:all
npm run shield:verify

# 2. Subir Web blindada a Firebase Hosting
firebase deploy --only hosting

# 3. Compilar .exe blindado en Windows (o usando GitHub Actions)
cd desktop-rust
cargo build --release --target x86_64-pc-windows-msvc
```
