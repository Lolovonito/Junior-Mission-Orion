#!/usr/bin/env python3
"""Valida e incrusta orion_nasa_kids_v30.js y aplica build_security.py cuando existe .local_src/."""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCAL_DIR = ROOT / ".local_src"
LOCAL_JS = LOCAL_DIR / "orion_nasa_kids_v30.js"
LOCAL_MASTER = LOCAL_DIR / "index.master.html"
SRC_JS = LOCAL_JS if LOCAL_JS.exists() else (ROOT / "src" / "orion_nasa_kids_v30.js")
INDEX = LOCAL_MASTER if LOCAL_MASTER.exists() else (ROOT / "index.html")
BEGIN = "<!-- BEGIN ORION V30 NASA KIDS -->"
END = "<!-- END ORION V30 NASA KIDS -->"

COPIES = [
    ROOT / "public" / "index.html",
    ROOT / "public" / "Junior_Mission_Orion_v29_RobbieAI.html",
    ROOT / "Junior_Mission_Orion_v29_RobbieAI.html",
    ROOT / "Junior_Mission_Orion_Robbie_Final.html",
    ROOT / "MissionOrion.html",
    ROOT / "desktop-rust" / "assets" / "game.html",
]


def main() -> int:
    if not SRC_JS.exists():
        print(f"ERROR: No existe {SRC_JS}", file=sys.stderr)
        return 1

    # 1. Validar sintaxis JS con Node
    check = subprocess.run(["node", "--check", str(SRC_JS)], capture_output=True, text=True)
    if check.returncode != 0:
        print(f"ERROR de sintaxis en {SRC_JS}:\n" + check.stderr, file=sys.stderr)
        return 1
    print("OK: sintaxis validada en", SRC_JS)

    js_code = SRC_JS.read_text(encoding="utf-8").strip()
    block = f"\n{BEGIN}\n<script>\n{js_code}\n</script>\n{END}\n"

    html = INDEX.read_text(encoding="utf-8")
    if BEGIN in html and END in html:
        pre = html.split(BEGIN, 1)[0].rstrip()
        post = html.split(END, 1)[1].lstrip("\n")
        new_html = pre + "\n" + block.lstrip("\n") + post
    else:
        if "</body>" in html:
            idx = html.rfind("</body>")
            new_html = html[:idx] + block + html[idx:]
        else:
            new_html = html.rstrip() + "\n" + block

    INDEX.write_text(new_html, encoding="utf-8")
    print(f"OK: {INDEX.name} actualizado ({len(new_html):,} bytes)")

    build_sec = ROOT / "scripts" / "build_security.py"
    if LOCAL_MASTER.exists() and build_sec.exists():
        res = subprocess.run([sys.executable, str(build_sec)], check=False)
        return res.returncode

    for dst in COPIES:
        if dst.parent.exists():
            shutil.copy2(INDEX, dst)
            print("OK: sincronizado", dst.relative_to(ROOT))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
