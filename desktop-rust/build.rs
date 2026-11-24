use std::env;
use std::fs;
use std::io::Write;
use std::path::PathBuf;

use chacha20poly1305::aead::{Aead, KeyInit, Payload};
use chacha20poly1305::ChaCha20Poly1305;
use flate2::write::ZlibEncoder;
use flate2::Compression;
use sha2::{Digest, Sha256};

const VAULT_AAD: &[u8] = b"JMO-RUST-VAULT-V1-CHOYEROS";

fn parse_hex_32(text: &str) -> Option<[u8; 32]> {
    let clean: String = text.chars().filter(|c| !c.is_whitespace()).collect();
    if clean.len() != 64 {
        return None;
    }
    let mut out = [0u8; 32];
    for i in 0..32 {
        out[i] = u8::from_str_radix(&clean[i * 2..i * 2 + 2], 16).ok()?;
    }
    Some(out)
}

fn format_byte_array(bytes: &[u8]) -> String {
    let items: Vec<String> = bytes.iter().map(|b| format!("0x{b:02x}")).collect();
    format!("[{}]", items.join(", "))
}

fn main() {
    let manifest_dir =
        PathBuf::from(env::var("CARGO_MANIFEST_DIR").expect("CARGO_MANIFEST_DIR faltante"));
    let out_dir = PathBuf::from(env::var("OUT_DIR").expect("OUT_DIR faltante"));

    let shielded_html = manifest_dir.join("assets").join("game.html");
    let repo_html = manifest_dir.parent().map(|p| p.join("index.html"));
    let pubkey_hex_path = manifest_dir.join("assets").join("license_pubkey.hex");

    println!("cargo:rerun-if-changed=assets/game.html");
    println!("cargo:rerun-if-changed=assets/license_pubkey.hex");
    println!("cargo:rerun-if-changed=../index.html");

    let src = if shielded_html.exists() {
        shielded_html
    } else if let Some(ref fallback) = repo_html {
        if fallback.exists() {
            println!("cargo:warning=No existe desktop-rust/assets/game.html; usando ../index.html sin ofuscar. Ejecuta 'npm run shield:desktop' antes de compilar para produccion.");
            fallback.clone()
        } else {
            panic!("No se encontro assets/game.html ni ../index.html");
        }
    } else {
        panic!("No se encontro HTML fuente para cifrar");
    };

    let plain_bytes = fs::read(&src).expect("Error leyendo HTML del juego");
    let plain_sha: [u8; 32] = Sha256::digest(&plain_bytes).into();

    let mut encoder = ZlibEncoder::new(Vec::new(), Compression::best());
    encoder
        .write_all(&plain_bytes)
        .expect("Error comprimiendo HTML");
    let compressed = encoder.finish().expect("Error finalizando Zlib");

    let mut key = [0u8; 32];
    let mut nonce = [0u8; 12];
    let mut xor_mask = [0u8; 32];
    getrandom::getrandom(&mut key).expect("Error generando clave aleatoria");
    getrandom::getrandom(&mut nonce).expect("Error generando nonce aleatorio");
    getrandom::getrandom(&mut xor_mask).expect("Error generando mascara aleatoria");

    let cipher = ChaCha20Poly1305::new((&key).into());
    let encrypted = cipher
        .encrypt(
            (&nonce).into(),
            Payload {
                msg: &compressed,
                aad: VAULT_AAD,
            },
        )
        .expect("Error cifrando game.vault con ChaCha20Poly1305");

    let mut key_masked = [0u8; 32];
    for i in 0..32 {
        key_masked[i] = key[i] ^ xor_mask[i];
    }

    let license_pubkey = if pubkey_hex_path.exists() {
        let raw = fs::read_to_string(&pubkey_hex_path).expect("Error leyendo license_pubkey.hex");
        parse_hex_32(&raw).expect("assets/license_pubkey.hex debe contener exactamente 64 hex chars (32 bytes Ed25519)")
    } else {
        [0u8; 32]
    };

    fs::write(out_dir.join("game.vault"), &encrypted).expect("Error escribiendo game.vault");

    let meta_rs = format!(
        "// Generado automaticamente en compilacion por build.rs\n\
         pub const VAULT_AAD: &[u8] = b\"JMO-RUST-VAULT-V1-CHOYEROS\";\n\
         pub const VAULT_NONCE: [u8; 12] = {};\n\
         pub const KEY_MASKED_A: [u8; 16] = {};\n\
         pub const KEY_MASKED_B: [u8; 16] = {};\n\
         pub const XOR_MASK_A: [u8; 16] = {};\n\
         pub const XOR_MASK_B: [u8; 16] = {};\n\
         pub const PLAIN_SHA256: [u8; 32] = {};\n\
         #[allow(dead_code)]\n\
         pub const LICENSE_PUBKEY: [u8; 32] = {};\n",
        format_byte_array(&nonce),
        format_byte_array(&key_masked[0..16]),
        format_byte_array(&key_masked[16..32]),
        format_byte_array(&xor_mask[0..16]),
        format_byte_array(&xor_mask[16..32]),
        format_byte_array(&plain_sha),
        format_byte_array(&license_pubkey),
    );

    fs::write(out_dir.join("vault_meta.rs"), meta_rs).expect("Error escribiendo vault_meta.rs");
}
