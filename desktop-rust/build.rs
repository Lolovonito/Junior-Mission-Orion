#[path = "src/vault_crypto.rs"]
mod vault_crypto;

use std::env;
use std::fs;
use std::io::Read;
use std::path::PathBuf;

fn fill_random(buf: &mut [u8]) {
    if let Ok(mut f) = fs::File::open("/dev/urandom") {
        if f.read_exact(buf).is_ok() {
            return;
        }
    }
    // Deterministic fallback only if /dev/urandom is unavailable
    let mut state: u64 = 0xA41F_2C9B_53D8_E711
        ^ std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map(|d| d.as_nanos() as u64)
            .unwrap_or(0x1337_BEEF);
    for b in buf.iter_mut() {
        state ^= state << 13;
        state ^= state >> 7;
        state ^= state << 17;
        *b = (state >> 24) as u8;
    }
}

fn fmt_bytes(name: &str, bytes: &[u8]) -> String {
    let items: Vec<String> = bytes.iter().map(|b| format!("0x{b:02x}")).collect();
    format!("pub const {name}: [u8; {}] = [{}];\n", bytes.len(), items.join(", "))
}

fn main() {
    let manifest_dir = PathBuf::from(env::var("CARGO_MANIFEST_DIR").expect("CARGO_MANIFEST_DIR missing"));
    let out_dir = PathBuf::from(env::var("OUT_DIR").expect("OUT_DIR missing"));

    let local_override = manifest_dir.join("assets").join("game.html");
    let repo_html = manifest_dir.parent().map(|p| p.join("index.html"));

    println!("cargo:rerun-if-changed=assets/game.html");
    println!("cargo:rerun-if-changed=../index.html");
    println!("cargo:rerun-if-changed=src/vault_crypto.rs");

    let src = if local_override.exists() {
        local_override
    } else if let Some(ref fallback) = repo_html {
        if fallback.exists() {
            fallback.clone()
        } else {
            panic!("No se encontro assets/game.html ni ../index.html");
        }
    } else {
        panic!("No se encontro HTML fuente para incrustar");
    };

    let mut plain = fs::read(&src).expect("Error leyendo HTML fuente");

    let mut key = [0u8; 32];
    let mut mask = [0u8; 32];
    let mut nonce = [0u8; 12];
    fill_random(&mut key);
    fill_random(&mut mask);
    fill_random(&mut nonce);

    let mut blk0 = vault_crypto::chacha20_block(&key, 0, &nonce);
    let mut mac_key = [0u8; 32];
    mac_key.copy_from_slice(&blk0[..32]);

    let cipher = vault_crypto::chacha20_xor(&key, &nonce, &plain, 1);
    let expected_mac = vault_crypto::compute_mac256(&mac_key, &nonce, plain.len() as u64, &cipher);

    let mut share_a = [0u8; 32];
    for i in 0..32 {
        share_a[i] = (key[i] ^ mask[i]).rotate_left(((i % 7) + 1) as u32);
    }

    fs::write(out_dir.join("vault.bin"), &cipher).expect("Error escribiendo vault.bin");

    let mut meta = String::new();
    meta.push_str(&fmt_bytes("SHARE_A", &share_a));
    meta.push_str(&fmt_bytes("SHARE_B", &mask));
    meta.push_str(&fmt_bytes("NONCE", &nonce));
    meta.push_str(&fmt_bytes("EXPECTED_MAC", &expected_mac));
    meta.push_str(&format!("pub const ORIG_LEN: usize = {};\n", plain.len()));
    fs::write(out_dir.join("vault_meta.rs"), meta).expect("Error escribiendo vault_meta.rs");

    vault_crypto::zeroize_slice(&mut key);
    vault_crypto::zeroize_slice(&mut mac_key);
    vault_crypto::zeroize_slice(&mut blk0);
    vault_crypto::zeroize_slice(&mut plain);
}
