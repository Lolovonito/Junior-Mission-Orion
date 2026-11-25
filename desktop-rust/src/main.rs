#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod vault_crypto;
mod vault_meta {
    include!(concat!(env!("OUT_DIR"), "/vault_meta.rs"));
}

use std::env;
use std::io::{BufRead, BufReader, Write};
use std::net::{SocketAddr, TcpListener, TcpStream};
use std::path::PathBuf;
use std::process::Command;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::Duration;

use tao::dpi::LogicalSize;
use tao::event::{Event, WindowEvent};
use tao::event_loop::{ControlFlow, EventLoop};
use tao::window::WindowBuilder;
use wry::{NewWindowResponse, WebContext, WebViewBuilder};
#[cfg(target_os = "windows")]
use wry::WebViewBuilderExtWindows;

static VAULT_BIN: &[u8] = include_bytes!(concat!(env!("OUT_DIR"), "/vault.bin"));
const DEFAULT_PORT: u16 = 17429;
const CSP_HEADER: &str = "default-src 'self'; script-src 'self' 'unsafe-inline' blob: https://unpkg.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' data: https://fonts.gstatic.com; img-src 'self' data: blob: https:; media-src 'self' data: blob: https:; connect-src 'self' https://api.groq.com https://api.nasa.gov https://apod.nasa.gov https://images-api.nasa.gov https://ntfy.sh wss://ntfy.sh https://*.peerjs.com wss://*.peerjs.com https://0.peerjs.com wss://0.peerjs.com; worker-src 'self' blob:; frame-ancestors 'none'; base-uri 'self'; object-src 'none'";

#[cfg(target_os = "windows")]
mod win_guard {
    use core::ffi::c_void;
    use core::mem::{size_of, zeroed};
    use core::ptr::null_mut;

    #[repr(C, align(16))]
    struct ContextAmd64 {
        p1_home: u64,
        p2_home: u64,
        p3_home: u64,
        p4_home: u64,
        p5_home: u64,
        p6_home: u64,
        context_flags: u32,
        mx_csr: u32,
        seg_cs: u16,
        seg_ds: u16,
        seg_es: u16,
        seg_fs: u16,
        seg_gs: u16,
        seg_ss: u16,
        e_flags: u32,
        dr0: u64,
        dr1: u64,
        dr2: u64,
        dr3: u64,
        dr6: u64,
        dr7: u64,
        _rest: [u8; 1112],
    }

    #[link(name = "kernel32")]
    extern "system" {
        fn IsDebuggerPresent() -> i32;
        fn CheckRemoteDebuggerPresent(h_process: *mut c_void, pb_present: *mut i32) -> i32;
        fn GetCurrentProcess() -> *mut c_void;
        fn GetCurrentThread() -> *mut c_void;
        fn GetThreadContext(h_thread: *mut c_void, lp_context: *mut ContextAmd64) -> i32;
        fn GetModuleHandleW(lp_module_name: *const u16) -> *mut c_void;
        fn GetProcAddress(h_module: *mut c_void, lp_proc_name: *const u8) -> *const c_void;
    }

    #[link(name = "bcrypt")]
    extern "system" {
        fn BCryptGenRandom(
            h_algorithm: *mut c_void,
            pb_buffer: *mut u8,
            cb_buffer: u32,
            dw_flags: u32,
        ) -> i32;
    }

    type NtQueryInfoFn =
        unsafe extern "system" fn(*mut c_void, u32, *mut c_void, u32, *mut u32) -> i32;

    pub fn fill_random(buf: &mut [u8]) {
        const BCRYPT_USE_SYSTEM_PREFERRED_RNG: u32 = 0x0000_0002;
        unsafe {
            let _ = BCryptGenRandom(
                null_mut(),
                buf.as_mut_ptr(),
                buf.len() as u32,
                BCRYPT_USE_SYSTEM_PREFERRED_RNG,
            );
        }
    }

    fn is_analysis_detected() -> bool {
        unsafe {
            if IsDebuggerPresent() != 0 {
                return true;
            }
            let proc_h = GetCurrentProcess();
            let mut remote: i32 = 0;
            if CheckRemoteDebuggerPresent(proc_h, &mut remote) != 0 && remote != 0 {
                return true;
            }

            // Stack-decoded ntdll.dll and NtQueryInformationProcess (omits plaintext from binary strings/IAT)
            const K_DLL: u16 = 0x5A37;
            // "ntdll.dll\0" XOR 0x5A37
            let mut dll_w: [u16; 10] = [
                b'n' as u16 ^ K_DLL,
                b't' as u16 ^ K_DLL,
                b'd' as u16 ^ K_DLL,
                b'l' as u16 ^ K_DLL,
                b'l' as u16 ^ K_DLL,
                b'.' as u16 ^ K_DLL,
                b'd' as u16 ^ K_DLL,
                b'l' as u16 ^ K_DLL,
                b'l' as u16 ^ K_DLL,
                K_DLL,
            ];
            for ch in dll_w.iter_mut() {
                *ch ^= K_DLL;
            }
            let h_nt = GetModuleHandleW(dll_w.as_ptr());
            for ch in dll_w.iter_mut() {
                core::ptr::write_volatile(ch as *mut u16, 0);
            }

            if !h_nt.is_null() {
                const K_FN: u8 = 0x6D;
                // "NtQueryInformationProcess\0"
                let enc_fn: [u8; 26] = [
                    b'N' ^ K_FN, b't' ^ K_FN, b'Q' ^ K_FN, b'u' ^ K_FN, b'e' ^ K_FN,
                    b'r' ^ K_FN, b'y' ^ K_FN, b'I' ^ K_FN, b'n' ^ K_FN, b'f' ^ K_FN,
                    b'o' ^ K_FN, b'r' ^ K_FN, b'm' ^ K_FN, b'a' ^ K_FN, b't' ^ K_FN,
                    b'i' ^ K_FN, b'o' ^ K_FN, b'n' ^ K_FN, b'P' ^ K_FN, b'r' ^ K_FN,
                    b'o' ^ K_FN, b'c' ^ K_FN, b'e' ^ K_FN, b's' ^ K_FN, b's' ^ K_FN,
                    K_FN,
                ];
                let mut fn_buf = [0u8; 26];
                for (dst, src) in fn_buf.iter_mut().zip(enc_fn.iter()) {
                    *dst = *src ^ K_FN;
                }
                let addr = GetProcAddress(h_nt, fn_buf.as_ptr());
                crate::vault_crypto::zeroize_slice(&mut fn_buf);

                if !addr.is_null() {
                    let nt_query: NtQueryInfoFn = core::mem::transmute(addr);
                    let mut dbg_port: usize = 0;
                    let st_port = nt_query(
                        proc_h,
                        7, // ProcessDebugPort
                        (&mut dbg_port as *mut usize).cast::<c_void>(),
                        size_of::<usize>() as u32,
                        null_mut(),
                    );
                    if st_port >= 0 && dbg_port != 0 {
                        return true;
                    }

                    let mut dbg_obj: usize = 0;
                    let st_obj = nt_query(
                        proc_h,
                        30, // ProcessDebugObjectHandle
                        (&mut dbg_obj as *mut usize).cast::<c_void>(),
                        size_of::<usize>() as u32,
                        null_mut(),
                    );
                    if st_obj >= 0 && dbg_obj != 0 {
                        return true;
                    }
                }
            }

            let mut ctx: ContextAmd64 = zeroed();
            ctx.context_flags = 0x0010_0010; // CONTEXT_AMD64 | CONTEXT_DEBUG_REGISTERS
            if GetThreadContext(GetCurrentThread(), &mut ctx) != 0
                && (ctx.dr0 | ctx.dr1 | ctx.dr2 | ctx.dr3) != 0
            {
                return true;
            }
        }
        false
    }

    pub fn enforce_and_spawn() {
        if is_analysis_detected() {
            std::process::exit(0);
        }
        std::thread::spawn(|| loop {
            std::thread::sleep(std::time::Duration::from_millis(1500));
            if is_analysis_detected() {
                std::process::exit(0);
            }
        });
    }
}

#[cfg(not(target_os = "windows"))]
mod win_guard {
    use std::io::Read;
    pub fn fill_random(buf: &mut [u8]) {
        if let Ok(mut f) = std::fs::File::open("/dev/urandom") {
            let _ = f.read_exact(buf);
        }
    }
    pub fn enforce_and_spawn() {}
}

fn gen_hex_token(nbytes: usize) -> String {
    let mut raw = vec![0u8; nbytes];
    win_guard::fill_random(&mut raw);
    let mut s = String::with_capacity(nbytes * 2);
    for b in raw.iter() {
        use std::fmt::Write;
        let _ = write!(&mut s, "{b:02x}");
    }
    crate::vault_crypto::zeroize_slice(&mut raw);
    s
}

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

fn extract_sala_param() -> Option<String> {
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
                return Some(clean);
            }
        }
    }
    None
}

fn decrypt_vault() -> Vec<u8> {
    let mut key = [0u8; 32];
    for i in 0..32 {
        key[i] = vault_meta::SHARE_A[i].rotate_right(((i % 7) + 1) as u32) ^ vault_meta::SHARE_B[i];
    }
    let mut blk0 = vault_crypto::chacha20_block(&key, 0, &vault_meta::NONCE);
    let mut mac_key = [0u8; 32];
    mac_key.copy_from_slice(&blk0[..32]);

    let mac = vault_crypto::compute_mac256(
        &mac_key,
        &vault_meta::NONCE,
        vault_meta::ORIG_LEN as u64,
        VAULT_BIN,
    );

    if !vault_crypto::ct_eq(&mac, &vault_meta::EXPECTED_MAC) {
        vault_crypto::zeroize_slice(&mut key);
        vault_crypto::zeroize_slice(&mut mac_key);
        vault_crypto::zeroize_slice(&mut blk0);
        std::process::exit(0);
    }

    let plain = vault_crypto::chacha20_xor(&key, &vault_meta::NONCE, VAULT_BIN, 1);
    vault_crypto::zeroize_slice(&mut key);
    vault_crypto::zeroize_slice(&mut mac_key);
    vault_crypto::zeroize_slice(&mut blk0);

    if plain.len() != vault_meta::ORIG_LEN {
        std::process::exit(0);
    }
    plain
}

#[derive(Clone)]
struct ServerAuth {
    boot_nonce: String,
    session_cookie: String,
    boot_consumed: Arc<AtomicBool>,
}

fn has_valid_boot_nonce(query: &str, expected: &str) -> bool {
    for pair in query.split('&') {
        if let Some((k, v)) = pair.split_once('=') {
            if k == "__jmo_auth" && vault_crypto::ct_eq(v.as_bytes(), expected.as_bytes()) {
                return true;
            }
        }
    }
    false
}

fn has_valid_session_cookie(cookie_hdr: &str, expected: &str) -> bool {
    for item in cookie_hdr.split(';') {
        if let Some((k, v)) = item.trim().split_once('=') {
            if k.trim() == "__jmo_sid"
                && vault_crypto::ct_eq(v.trim().as_bytes(), expected.as_bytes())
            {
                return true;
            }
        }
    }
    false
}

fn handle_client(mut stream: TcpStream, auth: &ServerAuth) {
    let _ = stream.set_read_timeout(Some(Duration::from_secs(3)));
    let _ = stream.set_write_timeout(Some(Duration::from_secs(10)));

    let mut reader = BufReader::new(&stream);
    let mut request_line = String::new();
    if reader.read_line(&mut request_line).is_err() || request_line.is_empty() {
        return;
    }

    let mut cookie_hdr = String::new();
    let mut host_hdr = String::new();
    for _ in 0..64 {
        let mut line = String::new();
        match reader.read_line(&mut line) {
            Ok(0) | Err(_) => break,
            Ok(_) if line == "\r\n" || line == "\n" => break,
            Ok(_) => {
                if let Some((name, val)) = line.split_once(':') {
                    if name.eq_ignore_ascii_case("cookie") {
                        cookie_hdr = val.trim().to_string();
                    } else if name.eq_ignore_ascii_case("host") {
                        host_hdr = val.trim().to_string();
                    }
                }
            }
        }
    }

    if !host_hdr.is_empty()
        && !(host_hdr.starts_with("127.0.0.1") || host_hdr.starts_with("localhost"))
    {
        let _ = stream.write_all(
            b"HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\nConnection: close\r\n\r\n",
        );
        let _ = stream.flush();
        return;
    }

    let mut parts = request_line.split_whitespace();
    let method = parts.next().unwrap_or("");
    let target = parts.next().unwrap_or("/");
    if method != "GET" {
        let _ = stream.write_all(
            b"HTTP/1.1 405 Method Not Allowed\r\nContent-Length: 0\r\nConnection: close\r\n\r\n",
        );
        let _ = stream.flush();
        return;
    }

    let (path, query) = target.split_once('?').unwrap_or((target, ""));

    match path {
        "/" | "/index.html" => {
            let boot_match = has_valid_boot_nonce(query, &auth.boot_nonce)
                && auth
                    .boot_consumed
                    .compare_exchange(false, true, Ordering::SeqCst, Ordering::SeqCst)
                    .is_ok();
            let sid_match =
                !boot_match && has_valid_session_cookie(&cookie_hdr, &auth.session_cookie);

            if !boot_match && !sid_match {
                let _ = stream.write_all(
                    b"HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\nConnection: close\r\n\r\n",
                );
                let _ = stream.flush();
                return;
            }

            let mut html = decrypt_vault();
            let set_cookie = if boot_match {
                format!(
                    "Set-Cookie: __jmo_sid={}; HttpOnly; SameSite=Strict; Path=/\r\n",
                    auth.session_cookie
                )
            } else {
                String::new()
            };
            let header = format!(
                "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: {}\r\nCache-Control: no-store\r\nX-Content-Type-Options: nosniff\r\nX-Frame-Options: DENY\r\nReferrer-Policy: strict-origin-when-cross-origin\r\nContent-Security-Policy: {}\r\n{}Connection: close\r\n\r\n",
                html.len(),
                CSP_HEADER,
                set_cookie
            );
            let _ = stream.write_all(header.as_bytes());
            let _ = stream.write_all(&html);
            let _ = stream.flush();
            vault_crypto::zeroize_slice(&mut html);
        }
        "/favicon.ico" => {
            let _ = stream.write_all(
                b"HTTP/1.1 204 No Content\r\nContent-Length: 0\r\nConnection: close\r\n\r\n",
            );
            let _ = stream.flush();
        }
        _ => {
            let _ = stream.write_all(
                b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n",
            );
            let _ = stream.flush();
        }
    }
}

fn start_http_server(auth: ServerAuth) -> SocketAddr {
    let listener = TcpListener::bind(("127.0.0.1", DEFAULT_PORT))
        .or_else(|_| TcpListener::bind(("127.0.0.1", 0)))
        .expect("No se pudo iniciar el servidor local para Junior Mission Orion");
    let addr = listener.local_addr().expect("local_addr");

    thread::spawn(move || {
        for stream in listener.incoming().flatten() {
            let auth_c = auth.clone();
            thread::spawn(move || handle_client(stream, &auth_c));
        }
    });

    addr
}

fn main() {
    win_guard::enforce_and_spawn();

    let auth = ServerAuth {
        boot_nonce: gen_hex_token(16),
        session_cookie: gen_hex_token(16),
        boot_consumed: Arc::new(AtomicBool::new(false)),
    };
    let addr = start_http_server(auth.clone());
    let origin = format!("http://{}:{}", addr.ip(), addr.port());
    let app_url = match extract_sala_param() {
        Some(sala) => format!("{}/?sala={}&__jmo_auth={}", origin, sala, auth.boot_nonce),
        None => format!("{}/?__jmo_auth={}", origin, auth.boot_nonce),
    };

    let data_dir = resolve_data_dir();
    let _ = std::fs::create_dir_all(&data_dir);
    let mut web_context = WebContext::new(Some(data_dir));

    let event_loop = EventLoop::new();
    let window = WindowBuilder::new()
        .with_title("Junior Mission Orión v30.1 — Los Choyeros Galácticos")
        .with_inner_size(LogicalSize::new(1280.0, 800.0))
        .with_min_inner_size(LogicalSize::new(860.0, 520.0))
        .build(&event_loop)
        .expect("Error creando ventana nativa");

    let allowed_origin = origin.clone();
    let init_js = "try{const u=new URL(location.href);if(u.searchParams.has('__jmo_auth')){u.searchParams.delete('__jmo_auth');history.replaceState(null,'',u.pathname+u.search+u.hash);}}catch(_){}\ntry{Object.defineProperty(window,'__JMO_DESKTOP_LOCKED',{value:true,writable:false,configurable:false});}catch(_){}";

    let builder = WebViewBuilder::new_with_web_context(&mut web_context)
        .with_url(&app_url)
        .with_devtools(false)
        .with_hotkeys_zoom(false)
        .with_autoplay(true)
        .with_clipboard(true)
        .with_background_color((7, 10, 22, 255))
        .with_initialization_script(init_js)
        .with_navigation_handler(move |url| {
            if url == allowed_origin || url.starts_with(&format!("{allowed_origin}/")) {
                return true;
            }
            if url.starts_with("https://") {
                open_external_url(&url);
            }
            false
        })
        .with_new_window_req_handler(|url, _features| {
            if url.starts_with("https://") {
                open_external_url(&url);
            }
            NewWindowResponse::Deny
        });

    #[cfg(target_os = "windows")]
    let builder = builder
        .with_browser_accelerator_keys(false)
        .with_default_context_menus(false);

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
        Ok(wv) => Some(wv),
        Err(_) => {
            open_external_url(&app_url);
            None
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
