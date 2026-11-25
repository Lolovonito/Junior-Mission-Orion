#!/usr/bin/env python3
"""Auditoria integral de seguridad y proteccion anti-ingenieria inversa (Web + Git + .exe)."""
import http.server
import json
import os
import socket
import socketserver
import struct
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXE_PATH = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/tmp/Junior_Mission_Orion_v30.1_Secure.exe")

CSP_POLICY = (
    "default-src 'self'; script-src 'self' 'unsafe-inline' blob: https://unpkg.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' data: https://fonts.gstatic.com; "
    "img-src 'self' data: blob: https:; media-src 'self' data: blob: https:; "
    "connect-src 'self' https://api.groq.com https://api.nasa.gov https://apod.nasa.gov https://images-api.nasa.gov "
    "https://ntfy.sh wss://ntfy.sh https://*.peerjs.com wss://*.peerjs.com https://0.peerjs.com wss://0.peerjs.com; "
    "worker-src 'self' blob:; frame-ancestors 'none'; base-uri 'self'; object-src 'none'"
)


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def wd_call(base: str, method: str, path: str, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(
        base + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if data is not None else {},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def js(base: str, sid: str, script: str):
    return wd_call(base, "POST", f"/session/{sid}/execute/sync", {"script": script, "args": []})["value"]


class SecureHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", CSP_POLICY)
        super().end_headers()

    def log_message(self, format, *args):
        pass


def check_repo_secrets_and_html() -> None:
    tracked = subprocess.check_output(["git", "-C", str(ROOT), "ls-files"]).decode("utf-8").splitlines()
    candidates = [ROOT / p for p in tracked] + list((ROOT / "public").glob("*"))
    gk_pfx = "gsk" + "_"
    gk_sym = "GROQ_" + "API_KEY"
    for p in candidates:
        if not p.is_file():
            continue
        if p.suffix.lower() in {".mp4", ".webp", ".jpg", ".png", ".apk", ".exe", ".lock"}:
            continue
        data = p.read_text(encoding="utf-8", errors="ignore")
        assert gk_pfx not in data, f"Secreto {gk_pfx} encontrado en {p}"
        assert gk_sym not in data, f"Identificador {gk_sym} encontrado en {p}"

    for html_path in (ROOT / "index.html", ROOT / "public" / "index.html"):
        txt = html_path.read_text(encoding="utf-8")
        for forbidden in ("PROPUESTA ROBBIE", "ORION V30 NASA KIDS", "ETAPA 6", "RobbieOfflineBrain"):
            assert forbidden not in txt, f"Texto plano '{forbidden}' filtrado en {html_path}"
    print("OK [1/3]: Escaneo de secretos en Git/public e inspeccion estatica HTML sin filtraciones.")


def check_web_dynamic() -> None:
    http_port = free_port()
    wd_port = free_port()
    httpd = socketserver.TCPServer(("127.0.0.1", http_port), SecureHandler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    env = os.environ.copy()
    env["XDG_CONFIG_HOME"] = "/tmp/orion-sec-cfg"
    env["XDG_CACHE_HOME"] = "/tmp/orion-sec-cache"
    env["HOME"] = "/tmp/orion-sec-home"
    for d in (env["XDG_CONFIG_HOME"], env["XDG_CACHE_HOME"], env["HOME"]):
        Path(d).mkdir(parents=True, exist_ok=True)

    wd_proc = subprocess.Popen(
        ["chromedriver", f"--port={wd_port}"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    wd_base = f"http://127.0.0.1:{wd_port}"
    sid = None
    try:
        for _ in range(40):
            try:
                wd_call(wd_base, "GET", "/status")
                break
            except Exception:
                time.sleep(0.2)
        else:
            raise RuntimeError("ChromeDriver no respondio")

        caps = {
            "capabilities": {
                "alwaysMatch": {
                    "browserName": "chrome",
                    "goog:chromeOptions": {
                        "binary": "/usr/bin/chromium",
                        "args": [
                            "--headless=new",
                            "--no-sandbox",
                            "--disable-dev-shm-usage",
                            "--user-data-dir=/tmp/orion-sec-chrome",
                            "--use-gl=angle",
                            "--use-angle=swiftshader",
                            "--enable-unsafe-swiftshader",
                            "--window-size=1366,768",
                        ],
                    },
                    "goog:loggingPrefs": {"browser": "ALL"},
                }
            }
        }
        sid = wd_call(wd_base, "POST", "/session", caps)["value"]["sessionId"]
        wd_call(wd_base, "POST", f"/session/{sid}/url", {"url": f"http://127.0.0.1:{http_port}/index.html"})
        time.sleep(2.5)

        res = js(
            wd_base,
            sid,
            """
            const scriptCount = document.querySelectorAll('script').length;
            const sec = window.JSM && window.JSM.Security;

            const cm = new MouseEvent('contextmenu', { bubbles: true, cancelable: true });
            document.body.dispatchEvent(cm);

            const kdF12 = new KeyboardEvent('keydown', { key: 'F12', keyCode: 123, bubbles: true, cancelable: true });
            document.dispatchEvent(kdF12);
            const kdDev = new KeyboardEvent('keydown', { key: 'I', keyCode: 73, ctrlKey: true, shiftKey: true, bubbles: true, cancelable: true });
            document.dispatchEvent(kdDev);
            const kdSrc = new KeyboardEvent('keydown', { key: 'u', keyCode: 85, ctrlKey: true, bubbles: true, cancelable: true });
            document.dispatchEvent(kdSrc);

            // Prueba MAC en localStorage
            JSM.Store.set('jsm_save_v1', { v: 1, test: 777 });
            const readOk = JSM.Store.get('jsm_save_v1');
            const verifyOk = JSM.Security.verifySaveKey('jsm_save_v1');
            const rawBefore = localStorage.getItem('jsm_save_v1') || '';
            localStorage.setItem('jsm_save_v1', rawBefore.replace('777', '999999'));
            const readTampered = JSM.Store.get('jsm_save_v1');
            const verifyTampered = JSM.Security.verifySaveKey('jsm_save_v1');
            JSM.Store.del('jsm_save_v1');

            return {
              scriptCount,
              secVersion: sec && sec.version,
              secActive: sec && sec.active,
              cmPrevented: cm.defaultPrevented,
              f12Prevented: kdF12.defaultPrevented,
              devPrevented: kdDev.defaultPrevented,
              srcPrevented: kdSrc.defaultPrevented,
              macSetOk: !!(readOk && readOk.test === 777 && verifyOk === true),
              macTamperRejected: readTampered === null && verifyTampered === false,
            };
            """,
        )

        logs = wd_call(wd_base, "POST", f"/session/{sid}/se/log", {"type": "browser"})["value"]
        csp_errors = [l for l in logs if "Content Security Policy" in l.get("message", "")]
        assert res["scriptCount"] == 0, f"Scripts restantes en DOM: {res['scriptCount']}"
        assert res["secVersion"] == "30.1.0" and res["secActive"] is True, f"JSM.Security invalido: {res}"
        assert res["cmPrevented"] is True, "contextmenu no bloqueado"
        assert res["f12Prevented"] is True, "F12 no bloqueado"
        assert res["devPrevented"] is True, "Ctrl+Shift+I no bloqueado"
        assert res["srcPrevented"] is True, "Ctrl+U no bloqueado"
        assert res["macSetOk"] is True, "Fallo en sello MAC de guardado"
        assert res["macTamperRejected"] is True, "No rechazo guardado adulterado"
        assert len(csp_errors) == 0, f"Errores CSP detectados: {csp_errors}"
        print("OK [2/3]: Auditoria dinamica Chromium + CSP + MAC + Shield aprobada:", json.dumps(res))
    finally:
        if sid:
            try:
                wd_call(wd_base, "DELETE", f"/session/{sid}")
            except Exception:
                pass
        wd_proc.terminate()
        try:
            wd_proc.wait(timeout=5)
        except Exception:
            wd_proc.kill()
        httpd.shutdown()
        httpd.server_close()


def check_exe_binary() -> None:
    assert EXE_PATH.is_file(), f"No existe binario .exe en {EXE_PATH}"
    raw = EXE_PATH.read_bytes()
    assert raw[:2] == b"MZ", "Firma MZ invalida"
    pe_off = struct.unpack_from("<I", raw, 0x3C)[0]
    assert raw[pe_off : pe_off + 4] == b"PE\x00\x00", "Firma PE invalida"

    machine, num_sections, _, _, _, opt_size, _ = struct.unpack_from("<HHIIIHH", raw, pe_off + 4)
    assert machine == 0x8664, f"Arquitectura inesperada: 0x{machine:x}"

    opt_off = pe_off + 24
    magic = struct.unpack_from("<H", raw, opt_off)[0]
    assert magic == 0x20B, f"Magic PE32+ esperado (0x20b), obtenido 0x{magic:x}"

    subsystem, dll_chars = struct.unpack_from("<HH", raw, opt_off + 68)
    assert subsystem == 2, f"Subsistema esperado GUI (2), obtenido {subsystem}"
    assert dll_chars & 0x0020, "Falta IMAGE_DLLCHARACTERISTICS_HIGH_ENTROPY_VA"
    assert dll_chars & 0x0040, "Falta IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE"
    assert dll_chars & 0x0100, "Falta IMAGE_DLLCHARACTERISTICS_NX_COMPAT"

    # IMAGE_DIRECTORY_ENTRY_DEBUG = indice 6 en DataDirectory (offset 112 en OptionalHeader64)
    dbg_rva, dbg_size = struct.unpack_from("<II", raw, opt_off + 112 + 6 * 8)
    assert dbg_rva == 0 and dbg_size == 0, f"Directorio Debug/PDB presente: rva={dbg_rva}, size={dbg_size}"

    forbidden = [
        b"<html",
        b"<script",
        b"OrionV30",
        b"RobbieOfflineBrain",
        b"gsk" + b"_",
        b"GROQ_" + b"API_KEY",
        b"/home/ada",
        b".pdb",
        b"NtQueryInformationProcess",
    ]
    for token in forbidden:
        assert token not in raw, f"Cadena ASCII prohibida en .exe: {token!r}"
        utf16 = token.decode("ascii").encode("utf-16le")
        assert utf16 not in raw, f"Cadena UTF-16LE prohibida en .exe: {token!r}"

    print(
        f"OK [3/3]: Auditoria PE y cadenas del .exe aprobada ({len(raw):,} bytes, "
        f"PE32+/AMD64 GUI, ASLR+HEVA+NX, DebugDir=0/0, 0 filtraciones)."
    )


def main() -> int:
    check_repo_secrets_and_html()
    check_web_dynamic()
    check_exe_binary()
    print("\n✅ TODAS LAS AUDITORIAS DE SEGURIDAD (WEB + GIT + .EXE) PASARON.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
