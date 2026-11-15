use std::env;
use std::fs;
use std::path::PathBuf;

fn main() {
    let manifest_dir = PathBuf::from(env::var("CARGO_MANIFEST_DIR").expect("CARGO_MANIFEST_DIR missing"));
    let out_dir = PathBuf::from(env::var("OUT_DIR").expect("OUT_DIR missing"));

    let local_override = manifest_dir.join("assets").join("game.html");
    let repo_html = manifest_dir.parent().map(|p| p.join("index.html"));

    println!("cargo:rerun-if-changed=assets/game.html");
    println!("cargo:rerun-if-changed=../index.html");

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

    let dst = out_dir.join("game.html");
    fs::copy(&src, &dst).expect("Error copiando HTML del juego hacia OUT_DIR");
}
