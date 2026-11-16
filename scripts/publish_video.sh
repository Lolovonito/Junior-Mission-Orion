#!/usr/bin/env bash
set -euo pipefail

# Uso: ./scripts/publish_video.sh <ruta_video> [tag_release] [nombre_asset]
if [ "$#" -lt 1 ]; then
  echo "Uso: $0 <ruta_video> [tag_release (default: v29.0.2)] [nombre_asset]" >&2
  exit 1
fi

VIDEO_SRC="$(realpath "$1")"
TAG="${2:-v29.0.2}"
ASSET_NAME="${3:-$(basename "$VIDEO_SRC")}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_SLUG="Lolovonito/Junior-Mission-Orion"
GIT_LIMIT_BYTES=$((95 * 1024 * 1024)) # Margen seguro bajo el límite de 100 MB de GitHub

if [ ! -f "$VIDEO_SRC" ]; then
  echo "Error: no existe el archivo '$VIDEO_SRC'" >&2
  exit 1
fi

SIZE_BYTES=$(stat -c '%s' "$VIDEO_SRC")
SIZE_MB=$(python3 -c "print(f'{${SIZE_BYTES} / 1048576:.2f}')")
echo "Video: $VIDEO_SRC ($SIZE_MB MiB)"

cd "$REPO_ROOT"

# 1. Guardar y commitear en el repo dentro de video/ si cabe bajo el límite de GitHub Git
if [ "$SIZE_BYTES" -le "$GIT_LIMIT_BYTES" ]; then
  mkdir -p "$REPO_ROOT/video"
  DEST_PATH="$REPO_ROOT/video/$ASSET_NAME"
  if [ "$VIDEO_SRC" != "$DEST_PATH" ]; then
    cp -f "$VIDEO_SRC" "$DEST_PATH"
  fi
  git add "video/$ASSET_NAME"
  if ! git diff --cached --quiet; then
    git commit -m "media: agregar video del proyecto ($ASSET_NAME)"
  fi
  echo "Intentando push del repositorio hacia origin/main..."
  if ! git push origin main; then
    echo "AVISO: git push origin main falló (si GitHub Push Protection bloqueó un commit previo con secreto, autorízalo o limpia el historial antes de reintentar git push)." >&2
  fi
else
  echo "AVISO: '$ASSET_NAME' pesa ${SIZE_MB} MiB (> 95 MiB). Se omite el commit en Git para no exceder el límite de 100 MiB de GitHub y se subirá solo a GitHub Releases (hasta 2 GiB)." >&2
fi

# 2. Subir el video como asset a la GitHub Release indicada
TOKEN=$(printf 'protocol=https\nhost=github.com\n\n' | git credential fill | sed -n 's/^password=//p')
if [ -z "$TOKEN" ]; then
  echo "Error: no se encontró token de GitHub en git credential fill" >&2
  exit 1
fi

python3 - "$REPO_SLUG" "$TAG" "$VIDEO_SRC" "$ASSET_NAME" "$TOKEN" <<'PY'
import json, mimetypes, os, sys, urllib.error, urllib.parse, urllib.request

slug, tag, src_path, asset_name, token = sys.argv[1:6]
api = f"https://api.github.com/repos/{slug}"
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "jmo-video-publisher",
}

def req(url, method="GET", data=None, extra=None):
    h = dict(headers)
    if extra:
        h.update(extra)
    r = urllib.request.Request(url, data=data, headers=h, method=method)
    with urllib.request.urlopen(r, timeout=300) as resp:
        raw = resp.read()
        return json.loads(raw.decode()) if raw else None

try:
    rel = req(f"{api}/releases/tags/{urllib.parse.quote(tag)}")
    print(f"Usando release existente: {tag} (ID {rel['id']})")
except urllib.error.HTTPError as e:
    if e.code != 404:
        raise
    payload = {
        "tag_name": tag,
        "target_commitish": "main",
        "name": f"{tag} — Video del proyecto Junior Mission Orión",
        "body": f"Release {tag} con el video del proyecto (`{asset_name}`).",
        "draft": False,
        "prerelease": False,
    }
    rel = req(f"{api}/releases", method="POST",
              data=json.dumps(payload).encode(),
              extra={"Content-Type": "application/json"})
    print(f"Release creada: {rel['html_url']} (ID {rel['id']})")

rel_id = rel["id"]
for a in rel.get("assets", []):
    if a["name"] == asset_name:
        req(f"{api}/releases/assets/{a['id']}", method="DELETE")
        print(f"Asset previo eliminado: {asset_name} (ID {a['id']})")

ctype = mimetypes.guess_type(asset_name)[0] or "video/mp4"
video_bytes = open(src_path, "rb").read()
up_url = f"https://uploads.github.com/repos/{slug}/releases/{rel_id}/assets?name={urllib.parse.quote(asset_name)}"
up = req(up_url, method="POST", data=video_bytes, extra={"Content-Type": ctype})
print(f"Video subido a Release {tag}: {up['browser_download_url']} ({up['size']} bytes)")
PY
