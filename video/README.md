# Video del Proyecto — Junior Mission Orión

Esta carpeta está preparada para almacenar el video oficial del proyecto dentro del repositorio (`Lolovonito/Junior-Mission-Orion`).

## Cómo publicar un video nuevo (Repo + GitHub Release)

Usa el script incluido en `scripts/publish_video.sh`:

```bash
./scripts/publish_video.sh /ruta/al/video.mp4 v29.0.2
```

- Si el video pesa **≤ 95 MB**, se copia a `video/`, se commitea en `main` y se sube también como asset en la **Release** de GitHub indicada (o crea una nueva si el tag no existe).
- Si el video pesa **> 95 MB** (cerca del límite duro de 100 MB por archivo en Git estándar), se evita romper `git push` y se sube únicamente como asset de la **GitHub Release** (que admite hasta **2 GB** por archivo), o puedes comprimirlo primero a `< 95 MB` / activar `git-lfs`.
