#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::env;
use std::io::{BufRead, BufReader, Write};
use std::net::{SocketAddr, TcpListener, TcpStream};
use std::path::PathBuf;
use std::process::Command;
use std::thread;
use std::time::Duration;

use tao::dpi::LogicalSize;
use tao::event::{Event, WindowEvent};
use tao::event_loop::{ControlFlow, EventLoop};
use tao::window::WindowBuilder;
use wry::{NewWindowResponse, WebContext, WebViewBuilder};

static GAME_HTML: &[u8] = include_bytes!(concat!(env!("OUT_DIR"), "/game.html"));
const DEFAULT_PORT: u16 = 17429;

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

fn handle_client(mut stream: TcpStream) {
    let _ = stream.set_read_timeout(Some(Duration::from_secs(3)));
    let _ = stream.set_write_timeout(Some(Duration::from_secs(10)));

    let mut reader = BufReader::new(&stream);
    let mut request_line = String::new();
    if reader.read_line(&mut request_line).is_err() || request_line.is_empty() {
        return;
    }

    // Drain headers so WebView2 keeps clean connection lifecycle.
    loop {
        let mut line = String::new();
        match reader.read_line(&mut line) {
            Ok(0) | Err(_) => break,
            Ok(_) if line == "\r\n" || line == "\n" => break,
            Ok(_) => {}
        }
    }

    let path = request_line
        .split_whitespace()
        .nth(1)
        .unwrap_or("/")
        .split('?')
        .next()
        .unwrap_or("/");

    let response = match path {
        "/" | "/index.html" => {
            let header = format!(
                "HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: {}\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n",
                GAME_HTML.len()
            );
            let _ = stream.write_all(header.as_bytes());
            let _ = stream.write_all(GAME_HTML);
            let _ = stream.flush();
            return;
        }
        "/favicon.ico" => {
            b"HTTP/1.1 204 No Content\r\nContent-Length: 0\r\nConnection: close\r\n\r\n".as_slice()
        }
        _ => b"HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n".as_slice(),
    };

    let _ = stream.write_all(response);
    let _ = stream.flush();
}

fn start_http_server() -> SocketAddr {
    let listener = TcpListener::bind(("127.0.0.1", DEFAULT_PORT))
        .or_else(|_| TcpListener::bind(("127.0.0.1", 0)))
        .expect("No se pudo iniciar el servidor local para Junior Mission Orion");
    let addr = listener.local_addr().expect("local_addr");

    thread::spawn(move || {
        for stream in listener.incoming().flatten() {
            thread::spawn(move || handle_client(stream));
        }
    });

    addr
}

fn main() {
    let addr = start_http_server();
    let sala_query = extract_sala_query();
    let app_url = format!("http://{}:{}/{}", addr.ip(), addr.port(), sala_query);

    let data_dir = resolve_data_dir();
    let _ = std::fs::create_dir_all(&data_dir);
    let mut web_context = WebContext::new(Some(data_dir));

    let event_loop = EventLoop::new();
    let window = WindowBuilder::new()
        .with_title("Junior Mission Orión v29 — Los Choyeros Galácticos")
        .with_inner_size(LogicalSize::new(1280.0, 800.0))
        .with_min_inner_size(LogicalSize::new(860.0, 520.0))
        .build(&event_loop)
        .expect("Error creando ventana nativa");

    let builder = WebViewBuilder::new_with_web_context(&mut web_context)
        .with_url(&app_url)
        .with_autoplay(true)
        .with_clipboard(true)
        .with_background_color((7, 10, 22, 255))
        .with_new_window_req_handler(|url, _features| {
            open_external_url(&url);
            NewWindowResponse::Deny
        });

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
