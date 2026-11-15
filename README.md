# 🚀 Junior Mission Orión — Los Choyeros Galácticos

![Versión](https://img.shields.io/badge/versi%C3%B3n-v19.0%20Robbie%20Edition-b84dff?style=for-the-badge)
![NASA Space Apps](https://img.shields.io/badge/NASA%20Space%20Apps-Junior%20Astronaut%20Mission%20Trainer-ffb547?style=for-the-badge)
![Three.js](https://img.shields.io/badge/Motor%203D-Three.js%20r128%20WebGL-46e3c6?style=for-the-badge)
![HTML5](https://img.shields.io/badge/Despliegue-Single--File%20HTML5-6fb6ff?style=for-the-badge)

**Junior Mission Orión** es un simulador espacial educativo interactivo en 3D desarrollado para el reto **Junior Astronaut Mission Trainer (NASA Space Apps Challenge 2026)** por el equipo **Los Choyeros Galácticos**.

Permite a niñas, niños, jóvenes y entusiastas del espacio personalizar a su astronauta, despegar desde la Tierra en la cápsula **Orión**, navegar hacia el **Polo Sur de la Luna** (y **Marte**), construir una colonia autosustentable con datos científicos reales de la NASA y aprender en todo momento junto a **Robbie**, el ajolote espacial con inteligencia artificial.

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

- [`index.html`](./index.html) — Versión principal lista para abrir en el navegador o servir en web.
- [`MissionOrion.html`](./MissionOrion.html) / [`Junior_Mission_Orion_Robbie_Final.html`](./Junior_Mission_Orion_Robbie_Final.html) — Copia autocontenida de distribución directa.
- [`upgrade_robbie_propuesta.py`](./upgrade_robbie_propuesta.py) — Script automatizado de integración de las 6 etapas de Robbie, escenario espacial dinámico y empaquetado de versiones.

### Cómo ejecutarlo
1. **Apertura directa:** Haz doble clic sobre `index.html` o `Junior_Mission_Orion_Robbie_Final.html` para abrirlo directamente en cualquier navegador con soporte WebGL2 (Chrome, Brave, Edge, Firefox, Safari).
2. **Servidor local (opcional):**
   ```bash
   python3 -m http.server 8765
   # Abre http://localhost:8765 en tu navegador
   ```

---

## 📄 Créditos y Referencias Científicas
- **Equipo:** Los Choyeros Galácticos
- **Reto:** [NASA Space Apps Challenge — Junior Astronaut Mission Trainer](https://www.spaceappschallenge.org/2026/challenges/junior-astronaut-mission-trainer/?tab=resources)
- **Datos científicos:** Basado en recursos educativos públicos de la NASA sobre la cápsula Orión, el programa Artemis, soporte vital (ECLSS) y exploración del Polo Sur Lunar y Marte.
- *Proyecto educativo independiente; no utiliza logotipos ni marcas registradas oficiales de la NASA.*
