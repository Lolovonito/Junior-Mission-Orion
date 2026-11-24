#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod security;
#[cfg(feature = "license-gate")]
mod license;

mod vault_meta {
    include!(concat!(env!("OUT_DIR"), "/vault_meta.rs"));
}

use std::borrow::Cow;
use std::env;
use std::io::Read;
use std::path::PathBuf;
use std::process::Command;
use std::sync::Arc;

use chacha20poly1305::aead::{Aead, KeyInit, Payload};
use chacha20poly1305::ChaCha20Poly1305;
use flate2::read::ZlibDecoder;
use sha2::{Digest, Sha256};
use tao::dpi::LogicalSize;
use tao::event::{Event, WindowEvent};
use tao::event_loop::{ControlFlow, EventLoop};
use tao::window::WindowBuilder;
use wry::http::{header, Request, Response, StatusCode};
use wry::{NewWindowResponse, WebContext, WebViewBuilder};
#[cfg(target_os = "windows")]
use wry::WebViewBuilderExtWindows;
use zeroize::Zeroize;

static GAME_VAULT: &[u8] = include_bytes!(concat!(env!("OUT_DIR"), "/game.vault"));

fn resolve_data_dir() -> PathBuf {
    #[cfg(target_os = "windows")]
    {
        if let Ok(local) = env::var("LOCALAPPDATA") {
            return PathBuf::from(local).join("JuniorMissionOrion").join("WebView2");
        }
    }
    #[cfg(not(target_os = "windows"))]
    {
        if let Ok(xdg) = env::var("XDG_DATA_HOME") {
            return PathBuf::from(xdg).join("junior-mission-orion");
        }
        if let Ok(home) = env::var("HOME") {
            return PathBuf::from(home).join(".local/share/junior-mission-orion");
        }
    }
    env::temp_dir().join("JuniorMissionOrion")
}

fn open_external_url(url: &str) {
    if !(url.starts_with("https://") || url.starts_with("http://")) {
        return;
    }
    #[cfg(target_os = "windows")]
    {
        let _ = Command::new("explorer.exe").arg(url).spawn();
    }
    #[cfg(target_os = "linux")]
    {
        let _ = Command::new("xdg-open").arg(url).spawn();
    }
    #[cfg(target_os = "macos")]
    {
        let _ = Command::new("open").arg(url).spawn();
    }
}

fn show_webview_error_and_exit(msg: &str) -> ! {
    #[cfg(target_os = "windows")]
    {
        use std::ffi::OsStr;
        use std::os::windows::ffi::OsStrExt;
        use windows_sys::Win32::UI::WindowsAndMessaging::{MessageBoxW, MB_ICONERROR, MB_OK};

        let title: Vec<u16> = OsStr::new("Junior Mission Orion")
            .encode_wide()
            .chain(std::iter::once(0))
            .collect();
        let body: Vec<u16> = OsStr::new(msg)
            .encode_wide()
            .chain(std::iter::once(0))
            .collect();
        unsafe {
            MessageBoxW(
                std::ptr::null_mut(),
                body.as_ptr(),
                title.as_ptr(),
                MB_OK | MB_ICONERROR,
            );
        }
    }
    #[cfg(not(target_os = "windows"))]
    {
        eprintln!("{msg}");
    }
    std::process::exit(1);
}

fn extract_sala_query() -> String {
    for arg in env::args().skip(1) {
        let trimmed = arg.trim();
        let raw_code = trimmed
            .strip_prefix("--sala=")
            .or_else(|| trimmed.strip_prefix("sala="))
            .or_else(|| trimmed.strip_prefix("?sala="));
        if let Some(code) = raw_code {
            let clean: String = code
                .chars()
                .filter(|c| c.is_ascii_alphanumeric())
                .take(12)
                .collect();
            if !clean.is_empty() {
                return format!("?sala={clean}");
            }
        }
    }
    String::new()
}

fn reconstruct_key() -> [u8; 32] {
    let mut key = [0u8; 32];
    unsafe {
        for i in 0..16 {
            let km = std::ptr::read_volatile(&vault_meta::KEY_MASKED_A[i]);
            let xm = std::ptr::read_volatile(&vault_meta::XOR_MASK_A[i]);
            key[i] = km ^ xm;
        }
        for i in 0..16 {
            let km = std::ptr::read_volatile(&vault_meta::KEY_MASKED_B[i]);
            let xm = std::ptr::read_volatile(&vault_meta::XOR_MASK_B[i]);
            key[16 + i] = km ^ xm;
        }
    }
    key
}

fn decrypt_game_html() -> Vec<u8> {
    let mut key = reconstruct_key();
    let cipher = ChaCha20Poly1305::new((&key).into());
    let decrypted = cipher.decrypt(
        (&vault_meta::VAULT_NONCE).into(),
        Payload {
            msg: GAME_VAULT,
            aad: vault_meta::VAULT_AAD,
        },
    );
    key.zeroize();

    let mut compressed = decrypted.unwrap_or_else(|_| {
        show_webview_error_and_exit("Error de integridad al descifrar los recursos del juego.");
    });

    let mut decoder = ZlibDecoder::new(compressed.as_slice());
    let mut html_bytes = Vec::new();
    let read_res = decoder.read_to_end(&mut html_bytes);
    compressed.zeroize();

    if read_res.is_err() {
        show_webview_error_and_exit("Error descomprimiendo la boveda interna del juego.");
    }

    let digest: [u8; 32] = Sha256::digest(&html_bytes).into();
    if digest != vault_meta::PLAIN_SHA256 {
        html_bytes.zeroize();
        show_webview_error_and_exit("Fallo la verificacion SHA-256 de integridad del juego.");
    }

    html_bytes
}

fn build_init_script(seal_token: &str) -> String {
    format!(
        r#"(function() {{
  'use strict';
  try {{
    Object.defineProperty(window, '__ORION_NATIVE_SEAL__', {{
      value: '{seal_token}',
      writable: false,
      configurable: false,
      enumerable: false
    }});
  }} catch (_e) {{}}
  window.addEventListener('contextmenu', function(e) {{
    e.preventDefault();
  }}, true);
  window.addEventListener('dragstart', function(e) {{
    if (e.target && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {{
      e.preventDefault();
    }}
  }}, true);
  document.addEventListener('keydown', function(e) {{
    var k = (e.key || '').toUpperCase();
    var ctrl = e.ctrlKey || e.metaKey;
    if (
      k === 'F12' ||
      (ctrl && e.shiftKey && (k === 'I' || k === 'J' || k === 'C' || k === 'K')) ||
      (ctrl && (k === 'U' || k === 'S' || k === 'P'))
    ) {{
      e.preventDefault();
      e.stopPropagation();
      return false;
    }}
  }}, true);
}})();"#,
        seal_token = seal_token
    )
}

fn handle_custom_protocol(
    html_bytes: &Arc<Vec<u8>>,
    request: Request<Vec<u8>>,
) -> Response<Cow<'static, [u8]>> {
    let path = request.uri().path();
    match path {
        "/" | "/index.html" => Response::builder()
            .status(StatusCode::OK)
            .header(header::CONTENT_TYPE, "text/html; charset=utf-8")
            .header(header::CACHE_CONTROL, "no-store, no-cache, must-revalidate")
            .header(header::X_CONTENT_TYPE_OPTIONS, "nosniff")
            .header("Content-Security-Policy", "frame-ancestors 'none'")
            .body(Cow::Owned(html_bytes.as_ref().clone()))
            .unwrap(),
        "/favicon.ico" => Response::builder()
            .status(StatusCode::NO_CONTENT)
            .body(Cow::Borrowed(&[]))
            .unwrap(),
        _ => Response::builder()
            .status(StatusCode::NOT_FOUND)
            .header(header::CONTENT_TYPE, "text/plain; charset=utf-8")
            .body(Cow::Borrowed(b"No encontrado"))
            .unwrap(),
    }
}

fn main() {
    security::sanitize_webview_env();
    security::enforce_anti_debug_or_exit();
    security::start_watchdog_thread();

    #[cfg(feature = "license-gate")]
    license::verify_license_or_exit();

    let html_bytes = Arc::new(decrypt_game_html());
    let seal_token = security::generate_runtime_seal();
    let init_script = build_init_script(&seal_token);

    let sala_query = extract_sala_query();
    let app_url = format!("orion://localhost/index.html{sala_query}");

    let data_dir = resolve_data_dir();
    let _ = std::fs::create_dir_all(&data_dir);
    let mut web_context = WebContext::new(Some(data_dir));

    let event_loop = EventLoop::new();
    let window = WindowBuilder::new()
        .with_title("Junior Mission Orion v29 — Los Choyeros Galacticos")
        .with_inner_size(LogicalSize::new(1280.0, 800.0))
        .with_min_inner_size(LogicalSize::new(860.0, 520.0))
        .build(&event_loop)
        .expect("Error creando ventana nativa");

    let html_ref = Arc::clone(&html_bytes);
    let builder = WebViewBuilder::new_with_web_context(&mut web_context)
        .with_devtools(false)
        .with_initialization_script(&init_script)
        .with_custom_protocol("orion".into(), move |_id, req| {
            handle_custom_protocol(&html_ref, req)
        })
        .with_url(&app_url)
        .with_autoplay(true)
        .with_clipboard(true)
        .with_background_color((7, 10, 22, 255))
        .with_new_window_req_handler(|url, _features| {
            open_external_url(&url);
            NewWindowResponse::Deny
        });

    #[cfg(target_os = "windows")]
    let builder = builder
        .with_https_scheme(true)
        .with_default_context_menus(false)
        .with_browser_accelerator_keys(false)
        .with_browser_extensions_enabled(false)
        .with_additional_browser_args("--disable-features=msWebOOUI,msPdfOOUI");

    #[cfg(any(
        target_os = "windows",
        target_os = "macos",
        target_os = "ios",
        target_os = "android"
    ))]
    let webview_res = builder.build(&window);

    #[cfg(not(any(
        target_os = "windows",
        target_os = "macos",
        target_os = "ios",
        target_os = "android"
    )))]
    let webview_res = {
        use tao::platform::unix::WindowExtUnix;
        use wry::WebViewBuilderExtUnix;
        let vbox = window.default_vbox().expect("GTK vbox missing");
        builder.build_gtk(vbox)
    };

    let _webview = match webview_res {
        Ok(wv) => wv,
        Err(err) => {
            show_webview_error_and_exit(&format!(
                "No se pudo iniciar WebView2 para Junior Mission Orion ({err}).\nInstala Microsoft Edge WebView2 Runtime."
            ));
        }
    };

    event_loop.run(move |event, _, control_flow| {
        *control_flow = ControlFlow::Wait;
        if let Event::WindowEvent {
            event: WindowEvent::CloseRequested,
            ..
        } = event
        {
            *control_flow = ControlFlow::Exit;
        }
    });
}
