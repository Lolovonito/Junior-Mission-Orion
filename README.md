# 🚀 Junior Mission Orión — Los Choyeros Galácticos

![Versión](https://img.shields.io/badge/versi%C3%B3n-v29.0%20Robbie%20AI%20%26%20F%C3%ADsica%20Artemis-b84dff?style=for-the-badge)
![NASA Space Apps](https://img.shields.io/badge/NASA%20Space%20Apps-Junior%20Astronaut%20Mission%20Trainer-ffb547?style=for-the-badge)
![Three.js](https://img.shields.io/badge/Motor%203D-Three.js%20r128%20WebGL-46e3c6?style=for-the-badge)
![HTML5](https://img.shields.io/badge/Despliegue-Single--File%20HTML5%20%2B%20Rust%20.exe-6fb6ff?style=for-the-badge)

**Junior Mission Orión** es un simulador espacial educativo interactivo en 3D desarrollado para el reto **Junior Astronaut Mission Trainer (NASA Space Apps Challenge 2026)** por el equipo **Los Choyeros Galácticos**.

Permite a niñas, niños, jóvenes y entusiastas del espacio personalizar a su astronauta, despegar desde la Tierra en la cápsula **Orión**, navegar hacia el **Polo Sur de la Luna (Cresta Shackleton)** y **Marte**, construir una colonia autosustentable con datos científicos reales de la NASA y aprender en todo momento junto a **Robbie**, el ajolote espacial con inteligencia artificial.

---

## 🎬 Tráiler del Proyecto (30 s)

* **Archivo en el repositorio:** [`video/trailer_junior_mission_orion_en_30s.mp4`](./video/trailer_junior_mission_orion_en_30s.mp4) (`5.7 MB`)
* **Descarga directa (Release `v29.0.2`):** [Descargar `trailer_junior_mission_orion_en_30s.mp4`](https://github.com/Lolovonito/Junior-Mission-Orion/releases/download/v29.0.2/trailer_junior_mission_orion_en_30s.mp4)

https://github.com/Lolovonito/Junior-Mission-Orion/releases/download/v29.0.2/trailer_junior_mission_orion_en_30s.mp4

> **Descargas `v29.0.2`:** [Jugar en línea](https://orionbeta-165b9.web.app/) · [Android `.apk`](https://github.com/Lolovonito/Junior-Mission-Orion/releases/download/v29.0.2/JMO.apk) · [Windows PC `.exe`](https://github.com/Lolovonito/Junior-Mission-Orion/releases/download/v29.0.2/Junior_Mission_Orion_v29_RobbieAI.exe) · [Landing ES](https://junior-mission-orion.web.app/) · [Landing EN](https://junior-mision-orion.web.app/)

---

## 🆕 Novedades de la versión `v29.0` (Robbie AI + Datos Curiosos + Física Realista Fase 1 + App Rust)

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
   - Binario nativo para Windows (`.exe` sin ventana de consola, usando **WebView2** mediante `tao` + `wry` y servidor HTTP loopback integrado con persistencia de partidas en `localStorage`).

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

El proyecto está empaquetado como una aplicación **100% autocontenida (Single-File HTML5)** sin dependencias externas obligatorias para que funcione de inmediato en cualquier navegador moderno, incluso sin servidor complejo:

- [`index.html`](./index.html) — Versión principal (`v29.0`) lista para abrir en el navegador o servir en web.
- [`Junior_Mission_Orion_v29_RobbieAI.html`](./Junior_Mission_Orion_v29_RobbieAI.html) / [`Junior_Mission_Orion_Robbie_Final.html`](./Junior_Mission_Orion_Robbie_Final.html) / [`MissionOrion.html`](./MissionOrion.html) — Copias autocontenidas de distribución directa.
- [`desktop-rust/`](./desktop-rust/) — Proyecto Rust (`tao` + `wry` WebView2) para compilar el ejecutable nativo `.exe` incrustando el HTML.
- [`video/trailer_junior_mission_orion_en_30s.mp4`](./video/trailer_junior_mission_orion_en_30s.mp4) — Tráiler oficial del proyecto en inglés (`30 s`, MP4).
- [`Junior_Mission_Orion_v28_multijugador.html`](./Junior_Mission_Orion_v28_multijugador.html) — Versión anterior archivada (`v28.0`).
- [`upgrade_robbie_propuesta.py`](./upgrade_robbie_propuesta.py) — Script automatizado de integración de las 6 etapas de Robbie, escenario espacial dinámico y empaquetado de versiones.

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
