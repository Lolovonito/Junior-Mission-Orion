#!/usr/bin/env python3
"""Prueba automatizada E2E de Junior Mission Orión v30.0 (Chromium + ChromeDriver vía HTTP)."""
import http.server
import json
import socket
import socketserver
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


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
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{method} {path} -> {e.code}: {e.read().decode('utf-8', 'replace')[:800]}")


def js(base: str, sid: str, script: str):
    return wd_call(base, "POST", f"/session/{sid}/execute/sync", {"script": script, "args": []})["value"]


CSP_POLICY = (
    "default-src 'self'; script-src 'self' 'unsafe-inline' blob: https://unpkg.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' data: https://fonts.gstatic.com; "
    "img-src 'self' data: blob: https:; media-src 'self' data: blob: https:; "
    "connect-src 'self' https://api.groq.com https://api.nasa.gov https://apod.nasa.gov https://images-api.nasa.gov "
    "https://ntfy.sh wss://ntfy.sh https://*.peerjs.com wss://*.peerjs.com https://0.peerjs.com wss://0.peerjs.com; "
    "worker-src 'self' blob:; frame-ancestors 'none'; base-uri 'self'; object-src 'none'"
)


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", CSP_POLICY)
        super().end_headers()

    def log_message(self, format, *args):
        pass


def main() -> int:
    http_port = free_port()
    wd_port = free_port()

    httpd = socketserver.TCPServer(("127.0.0.1", http_port), QuietHandler)
    t_http = threading.Thread(target=httpd.serve_forever, daemon=True)
    t_http.start()

    import os
    env = os.environ.copy()
    env["XDG_CONFIG_HOME"] = "/tmp/orion-v30-cfg"
    env["XDG_CACHE_HOME"] = "/tmp/orion-v30-cache"
    env["HOME"] = "/tmp/orion-v30-home"
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
        # Esperar a que ChromeDriver esté listo
        for _ in range(40):
            try:
                wd_call(wd_base, "GET", "/status")
                break
            except Exception:
                time.sleep(0.2)
        else:
            raise RuntimeError("ChromeDriver no respondió")

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
                            "--user-data-dir=/tmp/orion-v30-chrome",
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
        sess = wd_call(wd_base, "POST", "/session", caps)
        sid = sess["value"]["sessionId"]

        wd_call(wd_base, "POST", f"/session/{sid}/url", {"url": f"http://127.0.0.1:{http_port}/index.html"})
        time.sleep(2.5)

        results = {}

        # 1. Verificar carga básica y presencia de módulos v30
        results["loaded"] = js(
            wd_base,
            sid,
            """
            return {
              hasJSM: !!window.JSM,
              v30: window.JSM && window.JSM.OrionV30 && window.JSM.OrionV30.version,
              profile: window.JSM && window.JSM.OrionV30 && window.JSM.OrionV30.getProfile(),
              hasOfflineBrain: !!(window.RobbieOfflineBrain && window.RobbieOfflineBrain.answer),
              sources: Object.keys(window.JSM.NASA.SOURCES),
              errors: window.JSM.errors || [],
              bodyClasses: document.body.className
            };
            """,
        )

        # 2. Arrancar partida directamente en la Luna (simulando Nueva Partida)
        results["gameStart"] = js(
            wd_base,
            sid,
            """
            const g = JSM.Sim.newGame(JSM.Data.defaultAppearance());
            JSM.Game.startPlay(g, false);
            JSM.UI.update();
            const topVisible = Array.from(document.querySelectorAll('.hud-top .res'))
              .filter(e => getComputedStyle(e).display !== 'none')
              .map(e => e.dataset.k);
            const toolsVisible = Array.from(document.querySelectorAll('.hud-bottom .tool'))
              .filter(e => getComputedStyle(e).display !== 'none')
              .map(e => e.id);
            const osdrVisible = Array.from(document.querySelectorAll('#h-needs .osdr-row'))
              .filter(e => getComputedStyle(e).display !== 'none')
              .map(e => e.dataset.osdr);
            const simsNeedsVisible = Array.from(document.querySelectorAll('#h-needs .need'))
              .filter(e => getComputedStyle(e).display !== 'none')
              .map(e => e.dataset.k);
            return { topVisible, toolsVisible, osdrVisible, simsNeedsVisible };
            """,
        )

        # 3. Probar Blindaje con Regolito (b.shielded = true + -40% calefacción + malla 3D)
        results["shielding"] = js(
            wd_base,
            sid,
            """
            const g = JSM.Sim.g;
            const col = JSM.Sim.colony(g);
            const hab = { id: 'b-test-hab', type: 'habitat', x: 8, z: 8, rot: 0, color: '#e9edf5', material: 'metal', broken: false };
            col.buildings.push(hab);
            const obj = JSM.Game.addBuildingObj(hab);
            const beforeKw = window.JSM_SHARED.PHYS.thermalKw(-100, hab.shielded, g.sim);
            g.player.inv.regolith = 5;
            const ok = JSM.OrionV30.shieldBuilding(hab);
            const afterKw = window.JSM_SHARED.PHYS.thermalKw(-100, hab.shielded, g.sim);
            const hasDome = !!obj.group.getObjectByName('v30-regolith-shield');
            return { ok, shielded: !!hab.shielded, beforeKw, afterKw, reductionPct: Math.round((1 - afterKw / beforeKw) * 100), hasDome };
            """,
        )

        # 4. Probar Tormenta Solar DONKI (warning -> active -> refugio)
        results["donkiStorm"] = js(
            wd_base,
            sid,
            """
            const triggered = JSM.OrionV30.triggerSolarStorm(true);
            const warnPhase = JSM.Sim.g.solarStorm.phase;
            const bannerText = document.getElementById('v30-solar-banner')?.textContent || '';
            const eventCls = JSM.Sim.g.solarStorm.event?.cls;
            // Avanzar a fase activa
            JSM.Sim.g.solarStorm.leftSec = 0.01;
            JSM.Game.update(0.05);
            const activePhase = JSM.Sim.g.solarStorm.phase;
            const activeBanner = document.getElementById('v30-solar-banner')?.textContent || '';
            // Terminar tormenta
            JSM.Sim.g.solarStorm.leftSec = 0.01;
            JSM.Game.update(0.05);
            const endPhase = JSM.Sim.g.solarStorm.phase;
            return { triggered, warnPhase, eventCls, bannerHasDonki: /DONKI/i.test(bannerText), activePhase, activeBanner: activeBanner.slice(0, 90), endPhase };
            """,
        )

        # 5. Probar Diario NASA (4 pestañas: Base, DONKI/RadLab, Mars/Moon Trek, Fotos NASA/CSA)
        results["nasaModal"] = js(
            wd_base,
            sid,
            r"""
            const tabs = ['base', 'donki', 'trek', 'gallery'];
            const out = {};
            tabs.forEach(t => {
              JSM.UI.openScience(t);
              const txt = (JSM.UI.modalOpen && JSM.UI.modalOpen.m.querySelector('.body')?.textContent) || '';
              out[t] = { len: txt.length, hasKey: t === 'base' ? /DONKI|RadLab|OSDR|CSA/.test(txt) : t === 'donki' ? /RadLab/.test(txt) && /X8\.7|DONKI/.test(txt) : t === 'trek' ? /Jezero/.test(txt) && /Shackleton/.test(txt) : /CSA/.test(txt) && /Orión|Perseverance|APOD/i.test(txt) };
            });
            JSM.UI.closeModal(true);
            return out;
            """,
        )

        # 6. Probar Cultivos CSA, Opciones con 3 perfiles y simplificación de fórmulas en Planificador
        results["csaAndFormulas"] = js(
            wd_base,
            sid,
            r"""
            JSM.OrionV30.openCSACropPicker();
            const csaModal = (JSM.UI.modalOpen && JSM.UI.modalOpen.m.querySelector('.body')?.textContent) || '';
            JSM.UI.closeModal(true);
            JSM.UI.openOptions();
            const optModal = (JSM.UI.modalOpen && JSM.UI.modalOpen.m.querySelector('.body')?.textContent) || '';
            JSM.UI.closeModal(true);
            JSM.UI.openPlanner('mars');
            JSM.UI.update();
            return {
              hasCSA: /Agencia Espacial Canadiense|Canadian Space Agency/i.test(csaModal),
              hasCrops: /Lechuga/.test(csaModal) && /Rábanos/.test(csaModal) && /Fresas/.test(csaModal),
              has3ProfilesInOptions: /Explorador/.test(optModal) && /Cadete/.test(optModal) && /Artemis/.test(optModal),
              unifiedRobbieGuide: !!document.querySelector('#h-guide .robbie .robbie-svg')
            };
            """,
        )
        time.sleep(0.15)
        results["plannerSimplified"] = js(
            wd_base,
            sid,
            """
            const hasCollapsibleFormula = !!(JSM.UI.modalOpen && JSM.UI.modalOpen.m.querySelector('.v30-formula-box'));
            JSM.UI.closeModal(true);
            return { hasCollapsibleFormula };
            """,
        )

        # 7. Probar Motor Offline de Robbie + Modo Solo Offline en el modal de chat
        results["robbieOffline"] = js(
            wd_base,
            sid,
            """
            const a1 = window.RobbieOfflineBrain.answer('¿Qué es DONKI y las tormentas solares?');
            const a2 = window.RobbieOfflineBrain.answer('¿Cómo funciona el blindaje con regolito RadLab?');
            const a3 = window.RobbieOfflineBrain.answer('¿Por qué necesito el gimnasio OSDR?');
            const a4 = window.RobbieOfflineBrain.answer('¿Qué hago ahora?');
            const hasModeToggle = !!document.getElementById('robi-chat-mode');
            const modeBtn = document.getElementById('robi-chat-mode');
            modeBtn.click(); // cambiar a Solo Offline NASA
            document.getElementById('robi-chat-input').value = 'háblame de la comida en la Luna CSA';
            document.getElementById('robi-chat-send').click();
            const chatLog = document.getElementById('robi-chat-log')?.textContent || '';
            return {
              donkiOk: /DONKI/i.test(a1),
              radlabOk: /85 %|85%/.test(a2),
              osdrOk: /OSDR/i.test(a3),
              liveAdviceOk: a4.length > 20,
              hasModeToggle,
              offlineChatRepliedCSA: /CSA/i.test(chatLog)
            };
            """,
        )

        # 8. Verificar cambio de perfil Explorador -> Artemis
        results["profileSwitch"] = js(
            wd_base,
            sid,
            """
            JSM.OrionV30.applyProfile('artemis');
            JSM.UI.update();
            const artemisTools = Array.from(document.querySelectorAll('.hud-bottom .tool'))
              .filter(e => getComputedStyle(e).display !== 'none').length;
            const artemisTop = Array.from(document.querySelectorAll('.hud-top .res'))
              .filter(e => getComputedStyle(e).display !== 'none').length;
            JSM.OrionV30.applyProfile('explorador');
            JSM.UI.update();
            return { artemisTools, artemisTop, restoredProfile: JSM.OrionV30.getProfile() };
            """,
        )

        # 9. Revisar consola del navegador (filtrando errores de red externos esperados sin internet en sandbox)
        logs = wd_call(wd_base, "POST", f"/session/{sid}/se/log", {"type": "browser"})["value"]
        severe = [
            l for l in logs
            if l.get("level") == "SEVERE"
            and "api.nasa.gov" not in l.get("message", "")
            and "fonts.googleapis.com" not in l.get("message", "")
            and "ERR_NAME_NOT_RESOLVED" not in l.get("message", "")
            and "ERR_INTERNET_DISCONNECTED" not in l.get("message", "")
            and "Failed to load resource" not in l.get("message", "")
        ]
        results["severeJsErrors"] = severe
        results["jsmErrors"] = js(wd_base, sid, "return window.JSM.errors || [];")

        print(json.dumps(results, indent=2, ensure_ascii=False))

        # Aserciones clave
        assert results["loaded"]["v30"] == "30.0"
        assert results["loaded"]["profile"] == "explorador"
        assert len(results["loaded"]["sources"]) >= 12
        assert set(results["gameStart"]["topVisible"]) == {"oxygen", "water", "food", "power", "rad"}
        assert results["gameStart"]["osdrVisible"] == ["strength", "rest", "wellness"]
        assert results["gameStart"]["simsNeedsVisible"] == ["oxygen"]
        assert len(results["gameStart"]["toolsVisible"]) == 4
        assert results["shielding"]["ok"] is True
        assert results["shielding"]["reductionPct"] == 40
        assert results["shielding"]["hasDome"] is True
        assert results["donkiStorm"]["triggered"] is True
        assert results["donkiStorm"]["warnPhase"] == "warning"
        assert results["donkiStorm"]["activePhase"] == "active"
        assert results["donkiStorm"]["endPhase"] == "clear"
        assert all(v["hasKey"] for v in results["nasaModal"].values())
        assert results["csaAndFormulas"]["hasCSA"] is True
        assert results["csaAndFormulas"]["hasCrops"] is True
        assert results["csaAndFormulas"]["has3ProfilesInOptions"] is True
        assert results["csaAndFormulas"]["unifiedRobbieGuide"] is True
        assert results["plannerSimplified"]["hasCollapsibleFormula"] is True
        assert all(results["robbieOffline"].values())
        assert results["profileSwitch"]["artemisTools"] >= 9
        assert results["profileSwitch"]["artemisTop"] >= 7
        assert len(results["severeJsErrors"]) == 0, f"Errores JS severos: {results['severeJsErrors']}"
        assert len(results["jsmErrors"]) == 0, f"JSM.errors: {results['jsmErrors']}"

        print("\n✅ TODAS LAS VERIFICACIONES E2E v30.0 PASARON CORRECTAMENTE.")
        return 0
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


if __name__ == "__main__":
    raise SystemExit(main())
