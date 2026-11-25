# 🚀 Junior Mission Orión — Los Choyeros Galácticos

![Versión](https://img.shields.io/badge/versi%C3%B3n-v30.1%20Seguridad%20%2B%20Explorador%20NASA%2FCSA-b84dff?style=for-the-badge)
![NASA Space Apps](https://img.shields.io/badge/NASA%20Space%20Apps-Junior%20Astronaut%20Mission%20Trainer-ffb547?style=for-the-badge)
![Three.js](https://img.shields.io/badge/Motor%203D-Three.js%20r128%20WebGL-46e3c6?style=for-the-badge)
![HTML5](https://img.shields.io/badge/Despliegue-B%C3%B3veda%20Cifrada%20%2B%20Rust%20.exe-6fb6ff?style=for-the-badge)

**Junior Mission Orión** es un simulador espacial educativo interactivo en 3D desarrollado para el reto **Junior Astronaut Mission Trainer (NASA Space Apps Challenge 2026)** por el equipo **Los Choyeros Galácticos**.

Permite a niñas, niños (7–12 años), jóvenes y docentes personalizar a su astronauta, despegar desde la Tierra en la cápsula **Orión**, navegar hacia el **Polo Sur de la Luna (Cresta Shackleton)** y **Marte**, construir una colonia autosustentable con datos científicos reales de los recursos oficiales de la NASA y la CSA, y aprender en todo momento junto a **Robbie**, el ajolote espacial con inteligencia artificial (chat en línea + motor 100 % offline verificado).

---

## 🔒 Novedades de Seguridad `v30.1.0` (Protección Anti-Ingeniería Inversa Web + `.exe`)

1. **🛡️ Bóveda Web Cifrada y Autodestructiva (`JSM Web Vault`):**
   - Eliminación completa de secretos en texto plano del código fuente y compilación mediante [`scripts/build_security.py`](./scripts/build_security.py) (minificación léxica de JS/CSS + compresión **Deflate RFC 1951** + cifrado de flujo **ChaCha20** con clave aleatoria dividida en 4 fragmentos XOR/rotación y verificación de integridad **FNV-1a**).
   - Ejecución síncrona en memoria y purga inmediata de todos los nodos `<script>` del DOM (`document.scripts.length === 0`), borrado en RAM de buffers temporales (`fill(0)`) y ofuscación de cadenas sensibles en el módulo modular y las páginas de aterrizaje.
2. **🧱 Escudo Activo en Cliente y Sello de Partidas (`JSM Security Shield`):**
   - Bloqueo preventivo de menú contextual, arrastre, atajos de inspección (`F12`, `Ctrl+Shift+I/J/C/K`, `Ctrl+U/S/P`), neutralización de salida de consola en producción (`console.log/info/debug/dir/table`) y detector calibrado de herramientas de desarrollo acopladas en escritorio.
   - Firma criptográfica de integridad **MAC de 64 bits** en `localStorage` (`JSM.Store`) para claves `jsm_save*` que detecta manipulaciones manuales conservando compatibilidad de migración con partidas previas.
   - Cabeceras HTTP de seguridad estrictas en Firebase Hosting (`Content-Security-Policy`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`, `Cross-Origin-Opener-Policy`).
3. **🔐 Ejecutable Nativo Windows Blindado ([`desktop-rust/`](./desktop-rust/)):**
   - Payload incrustado y cifrado en tiempo de compilación con **ChaCha20 (RFC 8439)** + clave dividida (`SHARE_A` / `SHARE_B`) + **MAC de 256 bits** verificado al servir y limpiado inmediatamente de memoria con escritura volátil (`write_volatile` + `compiler_fence`).
   - Servidor HTTP loopback (`127.0.0.1`) autenticado mediante token efímero de un solo uso (`__jmo_auth`) que entrega una cookie `HttpOnly; SameSite=Strict` a WebView2 y rechaza conexiones locales externas con `403 Forbidden`.
   - Bloqueo nativo de WebView2 (`with_devtools(false)`, `with_hotkeys_zoom(false)`, `with_browser_accelerator_keys(false)`, `with_default_context_menus(false)`, filtro estricto de navegación) y mitigaciones PE de Windows (`/DYNAMICBASE`, `/HIGHENTROPYVA`, `/NXCOMPAT`, `/DEBUG:NONE`, remapeo de rutas y `strip = "symbols"`).
   - Detección anti-debugging nativa en Windows (`IsDebuggerPresent`, `CheckRemoteDebuggerPresent`, resolución dinámica ofuscada de `NtQueryInformationProcess` para `ProcessDebugPort` / `ProcessDebugObjectHandle` e inspección de registros hardware `Dr0..Dr3`).

---

## 🆕 Novedades de la versión `v30.0` (Modo Explorador Infantil + Integración Real de Recursos NASA/CSA)

1. **🌟 Perfil Pedagógico Infantil por Niveles (`Explorador 7–10 años` por defecto · `Cadete 10–12` · `Artemis Avanzado`):**
   - **HUD simplificado:** En Modo Explorador solo muestra **4 recursos vitales** (Oxígeno, Agua, Comida, Energía) + **Escudo Solar (RadLab/DONKI)** y desbloquea los botones de herramientas de forma progresiva por misión (*scaffolding*).
   - **3 Pilares de Salud Humana (NASA OSDR):** Sustituye los 7 medidores cotidianos por **Fuerza** (huesos/músculos), **Descanso** (sueño espacial) y **Ánimo/Defensas**.
   - **Matemáticas accesibles:** Oculta fórmulas universitarias (`Δv = ve·ln(m₀/m₁)`, `cos(θ)`) dentro de un desplegable opcional *«Ver fórmula real NASA (Avanzado / Profes)»*.
2. **🛰️ Congruencia Real con los 6 Recursos Oficiales de NASA Space Apps 2026 (Híbrido Online + Offline):**
   - **NASA DONKI:** Tormentas solares reales (en vivo vía `api.nasa.gov/DONKI/FLR` + catálogo histórico real offline) con alerta de 20 s, fase activa y refugio en Hábitat.
   - **RadLab (OSDR Radiation Dosimetry):** Dosímetro solar real (`mSv/día`) y activación del **blindaje 3D con regolito (`b.shielded`)** que bloquea el **85 %** de radiación en tormentas y ahorra **40 %** de calefacción.
   - **NASA OSDR:** Mecánicas activas de ejercicio diario en Gimnasio, sueño circadiano en Dormitorio y bienestar nutricional.
   - **NASA Mars Trek & Moon Trek:** Zonas reales seleccionables (*Cresta Shackleton, Cráter con Hielo, Tubo de Lava, Valles Marineris, Jezero, Gale*) con ventajas y compensaciones reales.
   - **NASA Open APIs (APOD & Mars Rover Photos):** Galería real en el Diario NASA (`N`) y en el Telescopio, con respaldo verificado sin conexión.
   - **Agencia Espacial Canadiense (CSA):** Cultivos lunares en el Invernadero (*Lechuga espacial, Rábanos rápidos, Fresas*) y conexión educativa con comunidades remotas en la Tierra.
3. **🤖 Robbie IA Unificado (Online Intacto + Motor 100 % Offline NASA):**
   - Conserva intacto el chat IA en línea y suma un **motor offline inteligente (`RobbieOfflineBrain`)** que responde con el estado real de tu colonia y los recursos NASA/CSA cuando no hay internet o el usuario activa el modo *Solo Offline NASA*.
   - Corrección de contradicciones numéricas (`RES_EDU`, reciclaje de agua ISS unificado al **98 %**) y reactivación de los avisos automáticos de Robbie por eventos del juego.
4. **🛠️ Flujo Modular + Verificación E2E y Seguridad Automatizada:**
   - Módulo fuente protegido en [`src/orion_nasa_kids_v30.js`](./src/orion_nasa_kids_v30.js), sincronizador [`scripts/sync_v30.py`](./scripts/sync_v30.py), empaquetador cifrado [`scripts/build_security.py`](./scripts/build_security.py), pruebas E2E en Chromium headless [`scripts/verify_v30.py`](./scripts/verify_v30.py) y auditoría de seguridad [`scripts/verify_security.py`](./scripts/verify_security.py).

---

## 🎬 Tráiler del Proyecto (30 s)

* **Archivo en el repositorio:** [`video/trailer_junior_mission_orion_30s.mp4`](./video/trailer_junior_mission_orion_30s.mp4) (`5.81 MiB`)
* **Descarga directa (Release `v30.1.0`):** [Descargar `trailer_junior_mission_orion_30s.mp4`](https://github.com/Lolovonito/Junior-Mission-Orion/releases/download/v30.1.0/trailer_junior_mission_orion_30s.mp4)

https://github.com/Lolovonito/Junior-Mission-Orion/releases/download/v30.1.0/trailer_junior_mission_orion_30s.mp4

> **Descargas `v30.1.0`:** [Jugar en línea](https://orionbeta-165b9.web.app/) · [Android `.apk`](https://github.com/Lolovonito/Junior-Mission-Orion/releases/download/v30.1.0/JMO.apk) · [Windows PC `.exe`](https://github.com/Lolovonito/Junior-Mission-Orion/releases/download/v30.1.0/Junior_Mission_Orion_v30.1_Secure.exe) · [Landing ES](https://junior-mission-orion.web.app/) · [Landing EN](https://junior-mision-orion.web.app/)

---

## 🆕 Novedades heredadas de `v29.0` (Robbie AI + Datos Curiosos + Física Realista Fase 1 + App Rust)

1. **🤖 Robbie IA (`RobbieAI` + Tips Dinámicos):**
   - Chat interactivo conectado a API (`Groq openai/gpt-oss-120b`, configurable con `localStorage.JSM_GROQ_KEY`) y enfocado en las mecánicas de **Junior Mission Orión** y los recursos oficiales de **NASA Space Apps Challenge 2026** (NASA Open APIs, DONKI, OSDR, RadLab, Mars Trek y CSA), con formato legible y modos configurables (`chat`, `both`, `physical`).
   - Nueva sección **Datos curiosos** en Opciones para elegir entre consejos del juego, datos espaciales reales de la NASA o curiosidades generadas dinámicamente por Robbie.
2. **🌖 Física de Superficie Realista Compartida (`JSM_SHARED.PHYS` — Solo y Multijugador):**
   - **Polo Sur Lunar · Cresta Shackleton (Artemis):** Modo **Cadete** (`~19 h` de luz rasante y `~5 h` de eclipse por ciclo) y modo **Artemis realista** (eclipses de `24–72 h` u opción **Ecuador** de `29.53 días`).
   - **Cráteres en Sombra Permanente (PSR a `−233 °C / 40 K`):** Zonas criogénicas alrededor del hielo que aumentan la demanda térmica y de $\text{O}_2$ del traje (`×1.35`).
   - **Aislamiento MLI y Reactor Kilopower (`fission`):** Carga de calefacción en módulos presurizados (`0.008 kW/°C` bajo `20 °C`, `−40 %` con regolito) y **Reactor de Fisión Kilopower** (`10 kW` constantes 24/7, requiere `20` de investigación).
   - **Clima Marciano ($\tau$) y Polvo en Paneles:** Atenuación exponencial por opacidad óptica $\tau$ y acumulación progresiva de polvo limpiable con `clean`.
   - **Gravedad y Locomoción Calibrada (`G_SCALE = 1.4`, `JUMP_V = 3.55`):** Alturas de salto reales proporcionales (`0.46 m` Tierra, `1.2 m` Marte, `2.8 m` Luna) y caminata/trote calibrados (`3.0 / 5.0 m/s`, `×0.85` lunar).
3. **🖥️ Lanzador Nativo de Escritorio en Rust ([`desktop-rust/`](./desktop-rust/)):**
   - Binario nativo para Windows (`.exe` sin ventana de consola, usando **WebView2** mediante `tao` + `wry`, bóveda cifrada ChaCha20 y servidor HTTP loopback autenticado con persistencia de partidas en `localStorage`).

## ✨ Novedades heredadas de `v28.0` (Multijugador + Colisiones SDF + Android Horizontal)

1. **🤝 Multijugador Cooperativo Sincronizado en Tiempo Real (`v28`):**
   - **Sincronización completa de acciones y animaciones (`ANIMS` + `FX`):** Los jugadores en la misma partida ven en tiempo real cuando un compañero extrae rocas, recolecta hielo lunar o muestras de suelo, repara módulos, investiga, descansa, saluda, observa con el telescopio o usa objetos/habilidades.
   - **Misiones de colonia compartidas (`MISSIONS`):** El progreso y las recompensas de las 8 misiones principales se sincronizan entre todos los astronautas del equipo.
   - **Recursos del terreno sincronizados (`mine` / `mined`):** Las rocas, depósitos de hielo y puntos de muestreo extraídos por cualquier jugador se actualizan para todo el equipo (incluyendo a quienes se unen o reconectan con la partida ya iniciada) y reaparecen de forma coordinada.
   - **Conexión flexible (Online por código de 5 letras, P2P WebRTC, Pestañas locales y LAN):** Soporte mediante señalización redundante (`PeerJS` + `ntfy`), enlaces de invitación directa (`?sala=ABCDE`), códigos QR y reconexión automática conservando lugar y rol.
2. **📐 Colisiones de Silueta Real 3D (Campos de Distancia con Signo — SDF):**
   - Cada edificio y estructura mide automáticamente su geometría 3D real para calcular su silueta exacta (sin «hitboxes» circulares invisibles) y la altura real de su techo, permitiendo caminar alrededor de las paredes reales e incluso subir sobre estructuras bajas.
3. **📱 Modo Android Horizontal Forzado y UI Móvil Optimizada:**
   - En dispositivos Android la interfaz se adapta automáticamente a formato horizontal (*landscape*) a pantalla completa usando `visualViewport`, con controles táctiles ergonómicos, menú principal espacioso y cierre táctil inmediato de los globos de Robbie durante el despegue y la exploración.

---

## ✨ Características Principales

### 1. 🛸 Robbie · Compañero de Viaje con IA (Diseño Oficial de Los Choyeros Galácticos)
- **Identidad visual oficial:** Robbie es el ajolote astronauta con gafas de sol pixeladas a bordo de su platillo volador con luces moradas.
- **Presencia en todas las etapas:**
  - **Menú Principal:** Botón minimizado `ROBBIE · IA` en la esquina superior derecha (desplegable a su panel completo) y globo de diálogo interactivo en la esquina inferior derecha, con el título y menú de navegación en el lado izquierdo.
  - **Viaje Tierra → Luna (Cabina Orión):** Robbie acompaña físicamente al jugador en 3D dentro de la cabina de la nave Orión y ofrece guía de vuelo en tiempo real sin obstruir el botón de *Saltar viaje*.
  - **Exploración y Construcción en Superficie:** Globos de diálogo de alta visibilidad en la esquina inferior derecha y compañero 3D en superficie.
- **Asistente IA Integrado:** Responde dudas sobre soporte vital, radiación, energía, cultivo hidropónico y ciencia espacial de la NASA.

### 2. 🧑‍🚀 Creador de Astronautas con Escenario Espacial Dinámico 3D
- Personalización completa del traje espacial, casco, complexión, colores y animaciones.
- **Fondo cósmico 3D en tiempo real:** Nebulosa galáctica profunda, 3 capas de estrellas con paralaje, planeta Tierra con atmósfera y Luna en órbita, planeta anillado, cometa fugaz y anillos holográficos sobre la plataforma.

### 3. 🌍➡️🌕 Vuelo Espacial en la Nave Orión
- Secuencia completa de lanzamiento, ascenso orbital, crucero translunar por anillos de trayectoria y alunizaje suave.
- Vista conmutable entre **Exterior 3D** y **Cabina 3D** junto a Robbie.

### 4. 🏗️ Colonia Lunar y Marciana (Ciencia Real de la NASA)
- **Soporte Vital Integrado:**
  - ⚡ **Energía:** Paneles solares y bancos de baterías para superar la noche lunar y tormentas solares.
  - 💧 **Agua:** Extracción y purificación de hielo de agua de los cráteres permanentemente sombreados del Polo Sur Lunar (reciclaje estilo ECLSS de la NASA).
  - 🫧 **Oxígeno:** Generación de $\text{O}_2$ mediante electrólisis del agua e invernaderos hidropónicos.
  - 🌱 **Alimentos y Bienestar:** Cultivo espacial sin suelo con iluminación LED fotosintética.
- **Sistema Educativo Proactivo:**
  - **Datos curiosos periódicos** de la NASA.
  - **Explicación de descubrimientos** al escanear o recolectar rocas de titanio/silicio, hielo lunar, regolito y al construir cada módulo.
  - **Alertas de emergencia** con diagnóstico del problema y recomendación de acción inmediata.

### 5. 🎮 Detección Automática de Dispositivo y Multijugador
- Adaptación automática de controles e instrucciones de Robbie para **Computadora (Teclado + Ratón)**, **Tableta / Móvil (Joystick y botones táctiles)** y **Mando / Gamepad**.
- **Modo Multijugador:** Salas cooperativas con código rápido, enlace directo y código QR para construir la base en equipo.
- **Bilingüe en tiempo real:** Español (`es-MX`) e Inglés (`en-US`) sin recargar ni perder el progreso.

---

## 🕹️ Controles Rápidos

| Acción | Computadora (Teclado / Ratón) | Tableta / Móvil (Táctil) | Mando (Gamepad) |
| :--- | :--- | :--- | :--- |
| **Mover astronauta / Pilotar nave** | `W` `A` `S` `D` o Flechas `↑` `←` `↓` `→` | Joystick táctil izquierdo | Stick izquierdo |
| **Girar cámara 3D** | Arrastrar con el ratón o `Q` / `E` | Deslizar con 1 dedo | Stick derecho |
| **Zoom de cámara** | Rueda del ratón | Pellizcar con 2 dedos | Gatillos |
| **Interactuar / Usar módulo** | Tecla `E` o Clic sobre el objeto | Botón táctil «Usar» o tocar objeto | Botón `X` / Cuadrado |
| **Saltar / Despegar nave Orión** | `Barra Espaciadora` | Botón táctil «Saltar» / «Despegar» | Botón `A` / Cruz |
| **Construir / Mapa / Misiones / Escanear** | `B` / `M` / `J` / `F` | Barra de herramientas inferior | `LB` / `RB` / `Y` |
| **Hablar con Robbie / Ver consejos** | Botón `ROBBIE · IA` (arriba der.) o globo (abajo der.) | Tocar botón `ROBBIE · IA` o globo | Acceso rápido en interfaz |

---

## 📦 Estructura del Proyecto y Ejecución

El proyecto está empaquetado como una aplicación **100 % autocontenida (Single-File HTML5)** protegida mediante bóveda cifrada sin dependencias externas obligatorias:

- [`index.html`](./index.html) — Versión principal protegida (`v30.1.0`) lista para abrir en el navegador o servir en web.
- [`Junior_Mission_Orion_v29_RobbieAI.html`](./Junior_Mission_Orion_v29_RobbieAI.html) / [`Junior_Mission_Orion_Robbie_Final.html`](./Junior_Mission_Orion_Robbie_Final.html) / [`MissionOrion.html`](./MissionOrion.html) — Copias autocontenidas de distribución directa.
- [`desktop-rust/`](./desktop-rust/) — Proyecto Rust (`tao` + `wry` WebView2) para compilar el ejecutable nativo `.exe` con bóveda ChaCha20, servidor autenticado y anti-debugging.
- [`scripts/build_security.py`](./scripts/build_security.py) / [`scripts/verify_security.py`](./scripts/verify_security.py) — Empaquetado anti-ingeniería inversa y auditoría de seguridad Web + `.exe`.
- [`scripts/sync_v30.py`](./scripts/sync_v30.py) / [`scripts/verify_v30.py`](./scripts/verify_v30.py) — Sincronizador modular y suite de pruebas E2E en Chromium headless.
- [`web_landing/`](./web_landing/) / [`web_landing_en/`](./web_landing_en/) — Sitios web promocionales (ES / EN) con cabeceras CSP y JS protegido.
- [`video/trailer_junior_mission_orion_30s.mp4`](./video/trailer_junior_mission_orion_30s.mp4) — Tráiler oficial del proyecto (`30 s`, MP4).

### Cómo ejecutarlo
1. **Apertura directa:** Haz doble clic sobre `index.html` o `Junior_Mission_Orion_Robbie_Final.html` para abrirlo directamente en cualquier navegador con soporte WebGL2 (Chrome, Brave, Edge, Firefox, Safari).
2. **Servidor local (opcional):**
   ```bash
   python3 -m http.server 8765
   # Abre http://localhost:8765 en tu navegador
   ```
3. **Compilar `.exe` nativo con Rust (desde Linux o Windows):**
   ```bash
   cd desktop-rust
   # Cross-compilación desde Linux con cargo-xwin (CRT estático sin depender de VCRUNTIME140.dll):
   cargo-xwin build --release --target x86_64-pc-windows-msvc --cross-compiler clang
   ```

---

## 📄 Créditos y Referencias Científicas
- **Equipo:** Los Choyeros Galácticos
- **Reto:** [NASA Space Apps Challenge — Junior Astronaut Mission Trainer](https://www.spaceappschallenge.org/2026/challenges/junior-astronaut-mission-trainer/?tab=resources)
- **Datos científicos:** Basado en recursos educativos públicos de la NASA sobre la cápsula Orión, el programa Artemis, soporte vital (ECLSS) y exploración del Polo Sur Lunar y Marte.
- *Proyecto educativo independiente; no utiliza logotipos ni marcas registradas oficiales de la NASA.*
