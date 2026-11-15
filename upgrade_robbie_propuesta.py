#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Upgrade script for Junior Mission Orión:
Implements the full 6-stage proposal "PROPUESTA: INTEGRACIÓN DE ROBBIE EN JUNIOR MISSION ORIÓN":
1. Official Robbie design (pink axolotl with pixel sunglasses inside his flying saucer with purple lights).
2. Minimized Robbie button in the top-right corner (never covering #fl-skip "Saltar viaje ›" during launch/flight),
   which deploys Robbie's full interactive panel when pressed.
3. High-visibility Speech Bubbles at the bottom-right (abajo a la derecha, inspired by the reference screenshot:
   large Robbie character on the right + wide speech bubble to his left with title "Robbie" and message).
4. Removes "Robbie Chat" from the bottom toolbar (.hud-bottom) during gameplay.
"""

import os
import re
import subprocess

SRC_FILE = "/home/ada/Descargas/Junior_Mission_Orion_Robbie_v16zerolatency.html"
SPRITE_FILE = "/home/ada/Proyectos/projectClaude/robbie_sprite_b64.txt"

# Etiqueta corta de control de versión para cada modificación en ~/Descargas
VERSION_TAG = "v23_multijugador_sync"
VERSIONED_DOWNLOAD_FILE = f"/home/ada/Descargas/Junior_Mission_Orion_{VERSION_TAG}.html"

OUT_FILES = [
    VERSIONED_DOWNLOAD_FILE,
    "/home/ada/Descargas/Junior_Mission_Orion_Robbie_Final.html",
    "/home/ada/Proyectos/projectClaude/Junior_Mission_Orion_Robbie_Final.html",
    "/home/ada/Descargas/Junior_Mission_Orion_Robbie_v16zerolatency.html",
    "/home/ada/Descargas/Junior_Mission_Orion_Robbie.html",
    "/home/ada/Proyectos/projectClaude/index.html",
    "/home/ada/Proyectos/projectClaude/MissionOrion.html",
]

with open(SPRITE_FILE, "r", encoding="utf-8") as f:
    ROBBIE_SPRITE_URI = f.read().strip()

with open(SRC_FILE, "r", encoding="utf-8") as f:
    html = f.read()

START_MARKER = "/* === BEGIN PROPUESTA ROBBIE INTEGRACION === */"
END_MARKER = "/* === END PROPUESTA ROBBIE INTEGRACION === */"

if START_MARKER in html and END_MARKER in html:
    s_idx = html.index(START_MARKER)
    e_idx = html.index(END_MARKER) + len(END_MARKER)
    script_before = html.rfind("<script>", 0, s_idx)
    script_after = html.find("</script>", e_idx)
    if script_before != -1 and script_after != -1 and (s_idx - script_before) < 40:
        html = html[:script_before] + html[script_after + len("</script>"):]
    else:
        html = html[:s_idx] + html[e_idx:]

# Eliminar la entrada de Robbie Chat en el menú inferior (.hud-bottom)
html = html.replace(
    "['robot', __t('Robbie Chat'), 'O', () => UI.openRobiChat()], ",
    ""
).replace(
    "['robot', __t('Robbie Chat'), 'O', () => UI.openRobiChat()],",
    ""
)
html = re.sub(
    r'const\s+GROQ_API_KEY\s*=\s*[^;]+;',
    'const GROQ_API_KEY = (typeof localStorage !== "undefined" && localStorage.getItem("JSM_GROQ_KEY")) || "";',
    html
)

PROPUESTA_SCRIPT = r"""<script>
/* === BEGIN PROPUESTA ROBBIE INTEGRACION === */
/* ============================================================================
   PROPUESTA: INTEGRACIÓN DE ROBBIE EN JUNIOR MISSION ORIÓN (Etapas 1 a 6)
   - Diseño oficial de Robbie (Ajolote con navecita y luces moradas).
   - Botón minimizado en la PARTE SUPERIOR DERECHA (sin tapar el botón Omitir/Saltar
     en el despegue) que al presionarlo despliega el panel completo de Robbie.
   - Globos de texto visibles ABAJO A LA DERECHA (estilo captura de referencia:
     personaje de Robbie a la derecha + globo de diálogo ancho a su izquierda).
   - Entrada de "Robbie Chat" eliminada de la barra de herramientas inferior.
   ============================================================================ */
(function (JSM) {
  'use strict';
  if (!JSM || !JSM.Game) return;
  const G = JSM.Game, U = JSM.U, Sim = JSM.Sim, UI = JSM.UI, D = JSM.Data;
  const THREE = window.THREE;

  const ROBBIE_IMG_SRC = "__ROBBIE_SPRITE_URI__";

  function tr(es, en) {
    try {
      if (JSM.I18N && JSM.I18N.lang && String(JSM.I18N.lang).toLowerCase().indexOf('en') === 0) return en || es;
    } catch (e) {}
    return es;
  }

  /* ==========================================================================
     ETAPA 1: DISEÑO VISUAL OFICIAL DE ROBBIE (AJOLOTE EN NAVECITA)
     ========================================================================== */
  function getRobbieSVG(mood) {
    const m = mood || 'hello';
    const isEmg = m === 'emergency' || m === 'alert' || m === 'warn';
    const isDisc = m === 'discovery' || m === 'celebrate';
    const isFact = m === 'fact' || m === 'curious';

    let badgeExtra = '';
    if (isEmg) {
      badgeExtra = `<circle cx="68" cy="14" r="9" fill="#FF3355" stroke="#181224" stroke-width="2" class="rb-pulse-fast"/><text x="68" y="18" text-anchor="middle" fill="#fff" font-size="12" font-weight="900" font-family="sans-serif">!</text>`;
    } else if (isDisc) {
      badgeExtra = `<circle cx="68" cy="14" r="9" fill="#FFB547" stroke="#181224" stroke-width="2" class="rb-pulse-fast"/><text x="68" y="18" text-anchor="middle" fill="#231400" font-size="11" font-weight="900" font-family="sans-serif">★</text>`;
    } else if (isFact) {
      badgeExtra = `<circle cx="68" cy="14" r="9" fill="#6FB6FF" stroke="#181224" stroke-width="2"/><text x="68" y="18" text-anchor="middle" fill="#04152d" font-size="11" font-weight="900" font-family="sans-serif">?</text>`;
    }

    return `<svg viewBox="0 0 80 80" class="robbie-svg mood-${m}" aria-label="Robbie">
      <g class="rb-ufo-float">
        <image href="${ROBBIE_IMG_SRC}" x="2" y="6" width="76" height="68" preserveAspectRatio="xMidYMid meet" />
      </g>
      ${badgeExtra}
    </svg>`;
  }

  if (JSM.Kids) {
    JSM.Kids.ROBI = getRobbieSVG('hello');
  }
  const chatHeaderRobi = document.querySelector('#modal-robi-chat header .robi');
  if (chatHeaderRobi) {
    chatHeaderRobi.innerHTML = getRobbieSVG('hello');
  }

  /* ==========================================================================
     ETAPA 6 + MODALIDAD EXCLUSIVA ANDROID HORIZONTAL (JSM.Device)
     - Detecta Android exclusivamente (/android/i en userAgent o ?android=1).
     - En Android: fuerza SIEMPRE orientación horizontal (nunca vertical):
       1) Bloqueo nativo screen.orientation.lock('landscape') + Fullscreen.
       2) Si el teléfono Android está físicamente en vertical (rawH > rawW),
          rota automáticamente #app 90° a horizontal (body.android-rotated-90),
          reporta innerWidth = max(rawW, rawH) e innerHeight = min(rawW, rawH)
          a Three.js/WebGL, y remapea coordenadas táctiles para joystick y cámara.
     ========================================================================== */
  const origWDesc = Object.getOwnPropertyDescriptor(window, 'innerWidth');
  const origHDesc = Object.getOwnPropertyDescriptor(window, 'innerHeight');
  const getRawW = () => {
    if (window.visualViewport && window.visualViewport.width) return Math.round(window.visualViewport.width);
    return (origWDesc && origWDesc.get) ? origWDesc.get.call(window) : (document.documentElement.clientWidth || 800);
  };
  const getRawH = () => {
    if (window.visualViewport && window.visualViewport.height) return Math.round(window.visualViewport.height);
    return (origHDesc && origHDesc.get) ? origHDesc.get.call(window) : (document.documentElement.clientHeight || 400);
  };

  const uaString = (navigator.userAgent || '').toLowerCase();
  const isAndroidDevice = /android/i.test(uaString) || /[?&]android=1\b/i.test(window.location.search || '');

  if (isAndroidDevice) {
    try {
      // Meta tags de orientación horizontal para navegadores Android / WebAPK
      ['screen-orientation:landscape', 'x5-orientation:landscape', 'mobile-web-app-capable:yes'].forEach(kv => {
        const [name, content] = kv.split(':');
        const m = document.createElement('meta');
        m.name = name;
        m.content = content;
        document.head.appendChild(m);
      });
      // Forzar que innerWidth siempre sea el lado largo horizontal e innerHeight el corto en Android
      Object.defineProperty(window, 'innerWidth', {
        configurable: true,
        get() { return Math.max(getRawW(), getRawH()); }
      });
      Object.defineProperty(window, 'innerHeight', {
        configurable: true,
        get() { return Math.min(getRawW(), getRawH()); }
      });
    } catch (e) {}
  }

  function lockAndroidLandscape(withFullscreen) {
    if (!isAndroidDevice) return;
    try {
      if (withFullscreen && document.documentElement && document.documentElement.requestFullscreen && !document.fullscreenElement) {
        document.documentElement.requestFullscreen({ navigationUI: 'hide' }).then(() => {
          if (screen.orientation && screen.orientation.lock) {
            screen.orientation.lock('landscape').catch(() => {});
          }
          setTimeout(syncAndroidOrientationState, 60);
        }).catch(() => {});
      }
      if (screen.orientation && screen.orientation.lock) {
        screen.orientation.lock('landscape').catch(() => {});
      }
    } catch (e) {}
  }

  function syncAndroidOrientationState() {
    if (!isAndroidDevice) return;
    const rawW = getRawW();
    const rawH = getRawH();
    const horizW = Math.max(rawW, rawH);
    const horizH = Math.min(rawW, rawH);
    document.documentElement.style.setProperty('--and-w', horizW + 'px');
    document.documentElement.style.setProperty('--and-h', horizH + 'px');
    document.documentElement.style.setProperty('--and-raw-w', rawW + 'px');
    document.documentElement.style.setProperty('--and-raw-h', rawH + 'px');
    document.body.classList.add('is-android', 'is-touch');

    const isPortraitPhysical = rawH > rawW;
    document.body.classList.toggle('android-rotated-90', isPortraitPhysical);

    const app = document.getElementById('app');
    if (app) {
      app.classList.add('is-android', 'is-touch', 'compact', 'wide');
    }
    G.isTouch = true;
    try {
      if (typeof G.bindTouch === 'function' && !G._touchBound) G.bindTouch();
      if (typeof G.resize === 'function') G.resize();
      if (JSM.Menu2D && typeof JSM.Menu2D.resize === 'function') JSM.Menu2D.resize();
    } catch (e) {}
  }

  if (isAndroidDevice) {
    // Remapeo transparente de coordenadas táctiles/puntero cuando el teléfono Android
    // se sostiene verticalmente y #app está rotado 90° en modo horizontal forzado
    const remapPointerEvent = (e) => {
      if (!document.body.classList.contains('android-rotated-90')) return;
      if (e.__androidRemapped) return;
      const sx = e.clientX;
      const sy = e.clientY;
      const rawW = getRawW();
      try {
        Object.defineProperty(e, '__androidRemapped', { value: true });
        Object.defineProperty(e, 'clientX', { configurable: true, get: () => sy });
        Object.defineProperty(e, 'clientY', { configurable: true, get: () => rawW - sx });
      } catch (err) {}
    };
    ['pointerdown', 'pointermove', 'pointerup', 'pointercancel', 'click'].forEach(evName => {
      window.addEventListener(evName, remapPointerEvent, true);
    });

    // Ajustar getBoundingClientRect de los joysticks (#h-joy y #fl-joy) cuando android-rotated-90 está activo
    const origGetBCR = Element.prototype.getBoundingClientRect;
    Element.prototype.getBoundingClientRect = function () {
      const r = origGetBCR.apply(this, arguments);
      if (document.body && document.body.classList.contains('android-rotated-90') && (this.id === 'h-joy' || this.id === 'fl-joy')) {
        const rawW = getRawW();
        return {
          left: r.top,
          right: r.bottom,
          top: rawW - r.right,
          bottom: rawW - r.left,
          width: r.height,
          height: r.width,
          x: r.top,
          y: rawW - r.right
        };
      }
      return r;
    };

    // Envolver Game.resize para que en Android NUNCA active diseño vertical (siempre compact + wide horizontal)
    if (G.resize) {
      const origResize = G.resize;
      G.resize = function () {
        const res = origResize.apply(this, arguments);
        const app = document.getElementById('app');
        if (app) {
          app.classList.add('is-android', 'is-touch', 'compact', 'wide');
        }
        return res;
      };
    }

    // Intentar bloqueo nativo de orientación horizontal en interacciones clave y cambios de pantalla completa
    window.addEventListener('pointerdown', () => lockAndroidLandscape(false), { passive: true });
    document.addEventListener('fullscreenchange', () => {
      lockAndroidLandscape(false);
      setTimeout(syncAndroidOrientationState, 60);
    });
    window.addEventListener('orientationchange', () => setTimeout(syncAndroidOrientationState, 80));
    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', () => syncAndroidOrientationState());
    }
  }

  const Device = JSM.Device = {
    type: 'desktop',
    isAndroid: isAndroidDevice,
    hasTouch: false,
    listeners: [],

    detect() {
      const ua = (navigator.userAgent || '').toLowerCase();
      const coarse = window.matchMedia && window.matchMedia('(pointer: coarse)').matches;
      const touchPoints = navigator.maxTouchPoints || 0;
      const w = window.innerWidth || 1024;
      const h = window.innerHeight || 768;
      const minDim = Math.min(w, h);
      const maxDim = Math.max(w, h);

      const isIPad = /ipad/.test(ua) || (/macintosh/.test(ua) && touchPoints > 1);
      const isTabletUA = isIPad || /tablet|playbook|silk/.test(ua) || (/android/.test(ua) && !/mobile/.test(ua));
      const isMobileUA = /iphone|ipod|windows phone/.test(ua) || (/android/.test(ua) && /mobile/.test(ua));

      this.hasTouch = Boolean(isAndroidDevice || coarse || touchPoints > 0 || 'ontouchstart' in window);

      if (isAndroidDevice) {
        this.type = 'mobile';
      } else if (JSM.Gamepad && JSM.Gamepad.connected) {
        this.type = 'gamepad';
      } else if (isTabletUA || (this.hasTouch && coarse && minDim >= 540 && maxDim >= 760)) {
        this.type = 'tablet';
      } else if (isMobileUA || (this.hasTouch && coarse && minDim < 540)) {
        this.type = 'mobile';
      } else {
        this.type = 'desktop';
      }

      const touchMode = (this.type === 'tablet' || this.type === 'mobile' || isAndroidDevice);
      if (touchMode) {
        G.isTouch = true;
        document.body.classList.add('is-touch');
        const app = document.getElementById('app');
        if (app) app.classList.add('is-touch');
      }
      if (isAndroidDevice) {
        syncAndroidOrientationState();
      }
      document.body.setAttribute('data-device', isAndroidDevice ? 'android' : this.type);
      return this.type;
    },

    getName() {
      if (this.isAndroid) return tr('Android (Modo Horizontal)', 'Android (Landscape Mode)');
      switch (this.type) {
        case 'tablet': return tr('Tableta', 'Tablet');
        case 'mobile': return tr('Dispositivo móvil', 'Mobile device');
        case 'gamepad': return tr('Mando / Control', 'Gamepad');
        default: return tr('Computadora', 'Computer');
      }
    },

    getIcon() {
      if (this.isAndroid) return '🤖';
      switch (this.type) {
        case 'tablet': return '📱';
        case 'mobile': return '📲';
        case 'gamepad': return '🎮';
        default: return '💻';
      }
    },

    getSummary() {
      if (this.isAndroid) {
        return tr(
          'Modo Android Horizontal activo: usa el joystick inferior izquierdo para moverte, los 4 botones táctiles derechos (Usar, Saltar, Escanear, Correr) y desliza la barra central para construir.',
          'Android Landscape Mode active: use the bottom-left joystick to move, the 4 right touch buttons (Use, Jump, Scan, Run), and swipe the bottom toolbar to build.'
        );
      }
      if (this.type === 'tablet' || this.type === 'mobile') {
        const devLabel = this.type === 'tablet' ? tr('tableta', 'tablet') : tr('dispositivo táctil', 'touchscreen');
        return tr(
          `Detecté que juegas en una ${devLabel}: usa el joystick táctil izquierdo para moverte, desliza un dedo para girar la cámara y toca los botones de acción a la derecha.`,
          `I detected you are playing on a ${devLabel}: use the left touch joystick to move, drag with one finger to rotate the camera, and tap the action buttons on the right.`
        );
      }
      if (this.type === 'gamepad') {
        return tr(
          'Detecté tu mando conectado: usa el stick izquierdo para moverte, el derecho para la cámara, (A) para saltar y (X) para interactuar.',
          'Gamepad detected: use the left stick to move, right stick for camera, (A) to jump and (X) to interact.'
        );
      }
      return tr(
        'Detecté que juegas en una computadora: usa WASD o las flechas para moverte, arrastra con el ratón para mirar, E para interactuar y Espacio para saltar.',
        'I detected you are playing on a computer: use WASD or arrow keys to move, drag with the mouse to look around, E to interact and Space to jump.'
      );
    },

    getFlightInstructions(phase) {
      const isTouch = (this.type === 'tablet' || this.type === 'mobile' || this.isAndroid);
      const devName = this.getName();
      if (phase === 'pad') {
        return isTouch
          ? tr(`📱 Modo ${devName}: Toca el botón «DESPEGAR» en pantalla para lanzar la nave Orión.`, `📱 ${devName} Mode: Tap the "LAUNCH" button on screen to launch Orion.`)
          : tr(`💻 Modo ${devName}: Pulsa ESPACIO o haz clic en «DESPEGAR» para iniciar el lanzamiento.`, `💻 ${devName} Mode: Press SPACE or click "LAUNCH" to launch.`);
      }
      if (phase === 'arrive' || phase === 'descent') {
        return isTouch
          ? tr(`📱 Modo ${devName}: Toca «ATERRIZAR» para descender suavemente en la superficie.`, `📱 ${devName} Mode: Tap "LAND" to touch down gently on the surface.`)
          : tr(`💻 Modo ${devName}: Pulsa ESPACIO o haz clic en «ATERRIZAR» para iniciar el descenso.`, `💻 ${devName} Mode: Press SPACE or click "LAND" to begin descent.`);
      }
      return isTouch
        ? tr(`📱 Controles en ${devName}: Usa el joystick táctil inferior izquierdo para guiar la nave Orión por los anillos dorados.`, `📱 ${devName} Controls: Use the bottom-left touch joystick to steer Orion through the golden rings.`)
        : tr(`💻 Controles en ${devName}: Usa WASD o las flechas del teclado para guiar la nave Orión por los anillos dorados.`, `💻 ${devName} Controls: Use WASD or Arrow keys to steer Orion through the golden rings.`);
    },

    getControlsList() {
      if (this.type === 'tablet' || this.type === 'mobile' || this.isAndroid) {
        return [
          [tr('Mover al astronauta / Pilotar nave', 'Move astronaut / Steer ship'), tr('Joystick táctil inferior izquierdo', 'Bottom-left touch joystick')],
          [tr('Girar la cámara 3D', 'Rotate 3D camera'), tr('Deslizar 1 dedo por la escena', 'Drag 1 finger on scene')],
          [tr('Usar / Saltar / Escanear / Correr', 'Use / Jump / Scan / Run'), tr('4 botones táctiles inferiores derechos', '4 bottom-right touch buttons')],
          [tr('Construir / Inventario / Mapa / Ciencia', 'Build / Inventory / Map / Science'), tr('Barra inferior deslizable al centro', 'Center swipeable bottom bar')],
          [tr('Ver barra de necesidades del astronauta', 'View astronaut needs bars'), tr('Tocar retrato arriba a la izquierda', 'Tap top-left astronaut portrait')],
          [tr('Panel e indicaciones de Robbie IA', 'Robbie AI panel & tips'), tr('Botón ROBBIE · IA arriba y globo a la derecha', 'Top ROBBIE · IA button & right speech bubble')]
        ];
      }
      if (this.type === 'gamepad') {
        return [
          [tr('Mover al astronauta / Pilotar nave', 'Move astronaut / Steer ship'), tr('Stick izquierdo', 'Left Stick')],
          [tr('Girar la cámara 3D', 'Rotate 3D camera'), tr('Stick derecho', 'Right Stick')],
          [tr('Usar / Interactuar', 'Use / Interact'), tr('Botón X / Cuadrado', 'X / Square button')],
          [tr('Saltar', 'Jump'), tr('Botón A / Cruz', 'A / Cross button')],
          [tr('Escanear terreno', 'Scan terrain'), tr('Botón Y / Triángulo', 'Y / Triangle button')],
          [tr('Construir módulos', 'Build modules'), tr('LB / RB', 'LB / RB')]
        ];
      }
      return [
        [tr('Mover al astronauta / Pilotar nave', 'Move astronaut / Steer ship'), 'W A S D / ↑ ← ↓ →'],
        [tr('Girar la cámara 3D', 'Rotate 3D camera'), tr('Arrastrar con el ratón o Q / E', 'Mouse drag or Q / E')],
        [tr('Zoom de cámara', 'Camera zoom'), tr('Rueda del ratón', 'Mouse wheel')],
        [tr('Interactuar / Usar módulo o roca', 'Interact / Use module or rock'), tr('Tecla E o Clic sobre el objeto', 'Key E or Click object')],
        [tr('Saltar / Despegar nave Orión', 'Jump / Launch Orion ship'), tr('Barra Espaciadora', 'Spacebar')],
        [tr('Escanear / Construir / Mapa / Misiones', 'Scan / Build / Map / Missions'), 'F / B / M / J'],
        [tr('Panel de Robbie / Preguntar a Robbie', 'Robbie panel / Ask Robbie'), tr('Botón superior derecho o globo inferior derecho', 'Top-right button or bottom-right bubble')]
      ];
    },

    onChange(fn) {
      this.listeners.push(fn);
    },

    notify() {
      const prev = this.type;
      this.detect();
      if (isAndroidDevice) syncAndroidOrientationState();
      if (prev !== this.type) {
        this.listeners.forEach(fn => { try { fn(this.type); } catch (e) {} });
      }
      updateDeviceUI();
    }
  };

  Device.detect();
  window.addEventListener('resize', () => Device.notify());
  window.addEventListener('touchstart', () => {
    if (isAndroidDevice) {
      syncAndroidOrientationState();
    } else if (Device.type === 'desktop') {
      const minDim = Math.min(window.innerWidth || 800, window.innerHeight || 600);
      Device.type = minDim >= 540 ? 'tablet' : 'mobile';
      G.isTouch = true;
      document.body.classList.add('is-touch');
      document.body.setAttribute('data-device', Device.type);
      updateDeviceUI();
    }
  }, { passive: true });
  window.addEventListener('gamepadconnected', () => Device.notify());
  window.addEventListener('gamepaddisconnected', () => Device.notify());

  /* ==========================================================================
     ESTILOS CSS:
     1. Eliminar entrada de Robbie Chat en barra inferior (#t-robot).
     2. Botón minimizado arriba a la derecha (sin tapar #fl-skip en el vuelo).
     3. Globos de texto abajo a la derecha estilo captura de referencia (personaje
        de Robbie grande a la derecha + globo de diálogo ancho a su izquierda).
     ========================================================================== */
  const styleEl = document.createElement('style');
  styleEl.id = 'robbie-propuesta-styles';
  styleEl.textContent = `
    /* Eliminar definitivamente la entrada de Robbie Chat de la barra inferior al jugar
       y eliminar todas las tarjetas antiguas (.educard, #guidebub, .robbie-bubble)
       para que JAMÁS se dupliquen detrás del globo nuevo de Robbie */
    #t-robot, .hud-bottom [data-tool="robot"],
    .educard, #hud .educard, #guidebub, .robbie-bubble {
      display: none !important;
      opacity: 0 !important;
      pointer-events: none !important;
      visibility: hidden !important;
    }

    /* Animaciones del personaje oficial de Robbie */
    .robbie-svg {
      width: 100%;
      height: 100%;
      display: block;
      overflow: visible;
      filter: drop-shadow(0 6px 16px rgba(184, 69, 255, 0.52));
    }
    .robbie-svg.mood-emergency {
      filter: drop-shadow(0 0 18px rgba(255, 51, 85, 0.9));
    }
    .robbie-svg.mood-discovery {
      filter: drop-shadow(0 0 18px rgba(255, 181, 71, 0.9));
    }
    .robbie-svg .rb-ufo-float {
      transform-origin: 40px 42px;
      animation: rbUfoHover 2.4s ease-in-out infinite;
    }
    .robbie-svg .rb-pulse-fast {
      animation: rbPulseFast 0.8s ease-in-out infinite;
    }
    @keyframes rbUfoHover {
      0%, 100% { transform: translateY(0px) rotate(0deg); }
      50% { transform: translateY(-3.5px) rotate(-1.5deg); }
    }
    @keyframes rbPulseFast {
      50% { transform: scale(1.16); }
    }

    /* ============================================================
       BOTÓN MINIMIZADO DE ROBBIE EN LA PARTE SUPERIOR DERECHA
       ============================================================ */
    .robbie-min-btn {
      appearance: none;
      display: inline-flex;
      align-items: center;
      gap: 9px;
      padding: 5px 13px 5px 7px;
      border-radius: 999px;
      background: linear-gradient(145deg, rgba(14, 20, 44, 0.92), rgba(9, 13, 30, 0.96));
      border: 1.5px solid rgba(184, 77, 255, 0.68);
      box-shadow: 0 10px 26px rgba(0, 0, 0, 0.55), 0 0 18px rgba(184, 77, 255, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.14);
      color: var(--ink);
      cursor: pointer;
      backdrop-filter: blur(12px);
      transition: transform 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
      pointer-events: auto;
      user-select: none;
    }
    .robbie-min-btn:hover {
      transform: translateY(-2px) scale(1.02);
      border-color: rgba(70, 227, 198, 0.88);
      box-shadow: 0 14px 32px rgba(0, 0, 0, 0.65), 0 0 24px rgba(70, 227, 198, 0.35);
    }
    .robbie-min-btn .rb-ico {
      width: 44px;
      height: 40px;
      flex: none;
      display: block;
    }
    .robbie-min-btn .rb-meta {
      display: flex;
      flex-direction: column;
      align-items: flex-start;
      line-height: 1.15;
      text-align: left;
    }
    .robbie-min-btn .rb-meta b {
      font-family: var(--display);
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.04em;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .robbie-min-btn .rb-meta b i {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--mint);
      box-shadow: 0 0 8px var(--mint);
      display: inline-block;
    }
    .robbie-min-btn .rb-meta small {
      font-size: 10px;
      color: #d0c0ff;
      font-weight: 600;
    }
    .robbie-min-btn .rb-caret {
      font-size: 11px;
      color: var(--mint);
      margin-left: 2px;
      transition: transform 0.2s ease;
    }
    .robbie-open .robbie-min-btn .rb-caret {
      transform: rotate(180deg);
    }

    /* ============================================================
       MENÚ PRINCIPAL: TÍTULO A LA IZQUIERDA Y ROBBIE A LA DERECHA
       (Posiciones invertidas respecto a cuando #menu > * los hacía
       elementos flex relativos)
       ============================================================ */
    #menu.m2,
    body.vm #menu {
      justify-content: flex-start !important;
      padding-left: max(36px, 6vw) !important;
      padding-right: max(24px, 4vw) !important;
    }
    #menu .m2col,
    body.vm #menu .m2col {
      position: relative !important;
      align-items: flex-start !important;
      text-align: left !important;
      margin: auto auto auto 0 !important;
      max-width: 540px !important;
      z-index: 22;
    }
    @media (max-width: 820px) {
      #menu.m2,
      body.vm #menu {
        padding-left: 20px !important;
      }
    }

    /* ============================================================
       PANEL DESPLEGABLE SUPERIOR DERECHO (MENÚ, VUELO Y PARTIDA)
       ============================================================ */
    #robbie-menu-right,
    #menu > #robbie-menu-right {
      position: absolute !important;
      top: calc(58px + env(safe-area-inset-top, 0px)) !important;
      right: max(18px, env(safe-area-inset-right, 0px)) !important;
      left: auto !important;
      bottom: auto !important;
      z-index: 30 !important;
      display: flex !important;
      flex-direction: column !important;
      align-items: flex-end !important;
      gap: 10px !important;
      pointer-events: none !important;
      transition: opacity .35s ease, transform .35s ease;
    }
    #robbie-menu-right > * {
      pointer-events: auto !important;
    }
    body.title-on #robbie-menu-right,
    body.title-on #robbie-menu-speech {
      opacity: 0 !important;
      pointer-events: none !important;
      transform: translateY(10px) scale(0.95);
    }
    .rm-card {
      width: min(390px, calc(100vw - 32px));
      background: linear-gradient(160deg, rgba(14, 20, 46, 0.96), rgba(8, 12, 28, 0.98));
      border: 1.5px solid rgba(184, 77, 255, 0.65);
      border-radius: 22px;
      padding: 16px 18px;
      box-shadow: 0 22px 60px rgba(0, 0, 0, 0.72), 0 0 32px rgba(184, 77, 255, 0.22);
      backdrop-filter: blur(16px);
      display: grid;
      gap: 12px;
      color: var(--ink);
      transform-origin: top right;
      animation: rbPanelDeploy 0.24s cubic-bezier(0.2, 1.25, 0.4, 1);
    }
    #robbie-menu-right.minimized .rm-card {
      display: none !important;
    }
    @keyframes rbPanelDeploy {
      from { opacity: 0; transform: translateY(-8px) scale(0.92); }
      to { opacity: 1; transform: translateY(0) scale(1); }
    }
    .rm-top {
      display: grid;
      grid-template-columns: 98px 1fr auto;
      gap: 12px;
      align-items: center;
    }
    .rm-close {
      appearance: none;
      border: 1px solid rgba(255, 255, 255, 0.14);
      background: rgba(255, 255, 255, 0.06);
      color: var(--muted);
      width: 28px;
      height: 28px;
      border-radius: 50%;
      font-size: 13px;
      cursor: pointer;
      display: grid;
      place-items: center;
      align-self: start;
    }
    .rm-close:hover {
      color: #fff;
      background: rgba(255, 255, 255, 0.16);
    }
    .rm-stage {
      position: relative;
      width: 98px;
      height: 92px;
      border-radius: 18px;
      background: radial-gradient(circle at 50% 42%, rgba(184, 77, 255, 0.28), rgba(14, 20, 48, 0.94) 74%);
      border: 1.5px solid rgba(184, 77, 255, 0.55);
      box-shadow: inset 0 0 18px rgba(184, 77, 255, 0.24);
      overflow: hidden;
      display: grid;
      place-items: center;
      cursor: pointer;
    }
    .rm-stage .rm-svg-fallback {
      width: 88px;
      height: 82px;
    }
    .rm-stage-tag {
      position: absolute;
      bottom: 4px;
      left: 50%;
      transform: translateX(-50%);
      background: rgba(8, 12, 28, 0.9);
      border: 1px solid rgba(184, 77, 255, 0.55);
      color: #e4b8ff;
      font-family: var(--display);
      font-size: 8.5px;
      font-weight: 700;
      letter-spacing: .08em;
      padding: 1.5px 6px;
      border-radius: 999px;
      white-space: nowrap;
      text-transform: uppercase;
    }
    .rm-identity {
      display: grid;
      gap: 3px;
    }
    .rm-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-family: var(--display);
      font-size: 10px;
      font-weight: 700;
      letter-spacing: .08em;
      text-transform: uppercase;
      color: var(--mint);
    }
    .rm-badge i {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: var(--mint);
      box-shadow: 0 0 10px var(--mint);
      display: inline-block;
    }
    .rm-identity h3 {
      font-family: var(--display);
      font-size: 19px;
      font-weight: 700;
      margin: 0;
      color: #fff;
    }
    .rm-identity p {
      margin: 0;
      font-size: 12px;
      line-height: 1.36;
      color: #c5d4f5;
    }
    .rm-device {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding: 8px 12px;
      border-radius: 12px;
      background: rgba(70, 227, 198, 0.09);
      border: 1px solid rgba(70, 227, 198, 0.32);
      font-size: 12px;
      color: #d6f7ef;
    }
    .rm-device b {
      color: var(--mint);
      font-family: var(--display);
    }
    .rm-actions {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 7px;
    }
    .rm-btn {
      appearance: none;
      border: 1px solid rgba(150, 178, 255, 0.28);
      background: rgba(255, 255, 255, 0.05);
      color: var(--ink);
      border-radius: 11px;
      padding: 8px 8px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 5px;
      transition: all .15s ease;
      text-align: center;
    }
    .rm-btn:hover {
      border-color: var(--mint);
      background: rgba(70, 227, 198, 0.15);
      transform: translateY(-1px);
    }
    .rm-btn.primary {
      background: rgba(184, 77, 255, 0.22);
      border-color: rgba(184, 77, 255, 0.65);
      color: #f6eaff;
    }

    /* Botón minimizado arriba a la derecha en Partida (#robbie-top-panel) */
    #robbie-top-panel {
      position: absolute;
      top: calc(12px + env(safe-area-inset-top, 0px));
      right: calc(236px + env(safe-area-inset-right, 0px));
      z-index: 32;
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: 8px;
      pointer-events: none;
    }
    #robbie-top-panel > * {
      pointer-events: auto;
    }
    #robbie-top-panel.minimized .rm-card {
      display: none !important;
    }
    @media (max-width: 760px) {
      #robbie-top-panel {
        right: calc(174px + env(safe-area-inset-right, 0px));
      }
    }

    /* Botón minimizado arriba a la derecha en el Despegue/Vuelo (#fl-robi-top)
       Ubicado DEBAJO del botón Omitir/Saltar viaje (#fl-skip está en top: 12px)
       para que JAMÁS lo tape */
    #fl-robi-top {
      position: absolute;
      top: calc(56px + env(safe-area-inset-top, 0px));
      right: max(14px, env(safe-area-inset-right, 0px));
      z-index: 30;
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: 8px;
      pointer-events: none;
    }
    #fl-robi-top > * {
      pointer-events: auto;
    }
    #fl-robi-top.minimized .rm-card {
      display: none !important;
    }

    /* ========================================================================
       GLOBOS DE TEXTO ABAJO A LA DERECHA (ESTILO CAPTURA DE REFERENCIA)
       Personaje grande de Robbie en la esquina inferior derecha y un globo de
       diálogo amplio, claro y muy visible a su izquierda apuntando hacia él.
       ======================================================================== */
    .robbie-speech-dock,
    #menu > #robbie-menu-speech,
    #hud > #robbie-companion {
      position: absolute !important;
      left: auto !important;
      top: auto !important;
      right: max(20px, env(safe-area-inset-right, 0px)) !important;
      bottom: calc(24px + env(safe-area-inset-bottom, 0px)) !important;
      z-index: 29 !important;
      display: flex !important;
      align-items: flex-end !important;
      justify-content: flex-end !important;
      gap: 6px !important;
      max-width: min(620px, calc(100vw - 24px)) !important;
      pointer-events: none !important;
      transition: opacity 0.28s ease, transform 0.28s cubic-bezier(0.2, 1.25, 0.4, 1);
    }
    .robbie-speech-dock > * {
      pointer-events: auto;
    }
    .robbie-speech-dock.hidden-dock {
      opacity: 0 !important;
      pointer-events: none !important;
      transform: translateY(14px) scale(0.95);
    }
    .robbie-speech-dock.hidden-dock > * {
      pointer-events: none !important;
    }

    /* En partida (#hud), elevar ligeramente si la pantalla es estrecha para no tocar la barra central */
    #hud .robbie-speech-dock {
      bottom: calc(18px + env(safe-area-inset-bottom, 0px));
    }
    @media (max-width: 1420px) {
      #hud .robbie-speech-dock {
        bottom: calc(var(--stack, 98px) + 10px + env(safe-area-inset-bottom, 0px));
      }
    }
    #hud.building .robbie-speech-dock {
      bottom: calc(var(--stack, 98px) + 168px + env(safe-area-inset-bottom, 0px));
    }

    /* En vuelo (#flight), el contenedor .fl-robi es el dock inferior derecho */
    #flight .fl-robi,
    #flight[data-state^="pad"] .fl-robi,
    #flight[data-state="count"] .fl-robi {
      position: absolute !important;
      left: auto !important;
      right: max(18px, env(safe-area-inset-right, 0px)) !important;
      bottom: calc(22px + env(safe-area-inset-bottom, 0px)) !important;
      transform: none !important;
      opacity: 1 !important;
      width: auto !important;
      max-width: min(600px, calc(100vw - 28px)) !important;
      padding: 0 !important;
      background: transparent !important;
      border: 0 !important;
      box-shadow: none !important;
      display: flex !important;
      flex-direction: row !important;
      align-items: flex-end !important;
      justify-content: flex-end !important;
      gap: 6px !important;
      pointer-events: none !important;
      z-index: 26 !important;
    }
    /* Durante el vuelo en el espacio donde aparecen los botones TURBO y VISTA abajo a la derecha,
       subimos el globo de Robbie justo encima de ellos para que no se estorben */
    #flight[data-state="space"] .fl-robi,
    #flight[data-state="approach"] .fl-robi,
    #flight[data-state="arrive"] .fl-robi {
      bottom: calc(114px + env(safe-area-inset-bottom, 0px)) !important;
    }
    #flight .fl-robi > * {
      pointer-events: auto !important;
    }
    #flight .fl-robi.hidden-dock,
    body.is-android #flight .fl-robi.hidden-dock {
      display: none !important;
      opacity: 0 !important;
      pointer-events: none !important;
    }
    #flight .fl-robi.hidden-dock > * {
      pointer-events: none !important;
    }

    /* Caja del Globo de Texto (inspirada en la captura: ancha, limpia, título centrado arriba y cola a la derecha) */
    .rb-speech-box {
      position: relative;
      width: min(440px, calc(100vw - 145px));
      background: linear-gradient(180deg, rgba(20, 29, 64, 0.97) 0%, rgba(11, 17, 40, 0.98) 100%);
      border: 2px solid rgba(184, 77, 255, 0.78);
      border-radius: 22px;
      padding: 13px 18px 12px;
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.68), 0 0 26px rgba(184, 77, 255, 0.24), inset 0 1px 0 rgba(255, 255, 255, 0.22);
      color: #ffffff;
      text-align: center;
      display: grid;
      gap: 5px;
      animation: rbBubbleIn 0.26s cubic-bezier(0.2, 1.3, 0.4, 1);
    }
    /* Cola triangular apuntando hacia Robbie a la derecha (como en la captura de referencia) */
    .rb-speech-box::after {
      content: "";
      position: absolute;
      right: -13px;
      bottom: 24px;
      width: 0;
      height: 0;
      border-top: 10px solid transparent;
      border-bottom: 6px solid transparent;
      border-left: 14px solid rgba(184, 77, 255, 0.82);
      filter: drop-shadow(3px 2px 4px rgba(0, 0, 0, 0.4));
    }
    @keyframes rbBubbleIn {
      from { opacity: 0; transform: translateX(12px) scale(0.94); }
      to { opacity: 1; transform: translateX(0) scale(1); }
    }

    /* Variantes de color del globo según la situación */
    .cat-emergency .rb-speech-box {
      border-color: #FF4D6D;
      background: linear-gradient(180deg, rgba(72, 14, 30, 0.97) 0%, rgba(38, 8, 18, 0.98) 100%);
      box-shadow: 0 16px 42px rgba(255, 45, 85, 0.5), 0 0 30px rgba(255, 77, 109, 0.45);
      animation: rbBubbleIn 0.25s ease-out, rcEmgPulse 1.4s infinite;
    }
    .cat-emergency .rb-speech-box::after {
      border-left-color: #FF4D6D;
    }
    .cat-discovery .rb-speech-box {
      border-color: #FFB547;
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.68), 0 0 28px rgba(255, 181, 71, 0.35);
    }
    .cat-discovery .rb-speech-box::after {
      border-left-color: #FFB547;
    }
    .cat-fact .rb-speech-box {
      border-color: #46E3C6;
    }
    .cat-fact .rb-speech-box::after {
      border-left-color: #46E3C6;
    }
    @keyframes rcEmgPulse {
      50% { box-shadow: 0 16px 46px rgba(255, 45, 85, 0.75), 0 0 38px rgba(255, 93, 115, 0.65); }
    }

    /* Encabezado del globo con el nombre "Robbie" en dorado destacado (como "Deus" en la captura) */
    .rb-speech-header {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      position: relative;
      padding-right: 30px;
    }
    .rb-speech-name {
      font-family: var(--display);
      font-size: 18px;
      font-weight: 800;
      letter-spacing: 0.03em;
      color: #FFB547;
      text-shadow: 0 2px 8px rgba(0, 0, 0, 0.75), 0 0 12px rgba(255, 181, 71, 0.35);
      margin: 0;
    }
    .rb-speech-badge {
      font-family: var(--display);
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      padding: 2px 8px;
      border-radius: 999px;
      background: rgba(184, 77, 255, 0.22);
      color: #e8c5ff;
      border: 1px solid rgba(184, 77, 255, 0.45);
      white-space: nowrap;
    }
    .cat-emergency .rb-speech-badge {
      background: rgba(255, 77, 109, 0.28);
      color: #ffb3c1;
      border-color: rgba(255, 77, 109, 0.6);
    }
    .cat-discovery .rb-speech-badge {
      background: rgba(255, 181, 71, 0.25);
      color: #ffe0a3;
      border-color: rgba(255, 181, 71, 0.6);
    }
    .rb-speech-close {
      position: absolute;
      right: -2px;
      top: -2px;
      appearance: none;
      border: 1px solid rgba(255, 255, 255, 0.16);
      background: rgba(255, 255, 255, 0.12);
      color: #fff;
      width: 26px;
      height: 26px;
      border-radius: 50%;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      display: grid;
      place-items: center;
      z-index: 10;
      pointer-events: auto !important;
      touch-action: manipulation;
    }
    .rb-speech-close:hover,
    .rb-speech-close:active {
      color: #fff;
      background: rgba(255, 77, 109, 0.45);
      border-color: rgba(255, 77, 109, 0.7);
    }

    /* Texto del mensaje dentro del globo */
    .rb-speech-text,
    #flight #fl-say {
      margin: 0 !important;
      font-size: 14px !important;
      line-height: 1.44 !important;
      font-weight: 600 !important;
      color: #f4f7ff !important;
      text-align: center !important;
    }
    .rb-speech-sub {
      font-size: 11.5px;
      color: #b8cdf8;
      margin-top: 1px;
    }

    /* Botones rápidos discretos en la base del globo */
    .rb-speech-foot {
      display: flex;
      align-items: center;
      justify-content: center;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 4px;
    }
    .rb-speech-foot button {
      appearance: none;
      border: 1px solid rgba(150, 178, 255, 0.32);
      background: rgba(255, 255, 255, 0.07);
      color: #eaf2ff;
      border-radius: 999px;
      padding: 4px 11px;
      font-size: 11.5px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .rb-speech-foot button:hover {
      border-color: var(--mint);
      background: rgba(70, 227, 198, 0.2);
      transform: translateY(-1px);
    }

    /* Personaje grande de Robbie en la esquina inferior derecha junto al globo */
    .rb-speech-char {
      appearance: none;
      border: 0;
      background: transparent;
      width: 112px;
      height: 102px;
      padding: 0;
      flex: none;
      cursor: pointer;
      position: relative;
      transition: transform 0.2s ease;
    }
    .rb-speech-char:hover {
      transform: scale(1.06) translateY(-2px);
    }
    @media (max-width: 640px) {
      .rb-speech-char {
        width: 82px;
        height: 76px;
      }
      .rb-speech-box {
        width: min(320px, calc(100vw - 110px));
        padding: 10px 14px;
      }
    }

    /* Sugerencias rápidas dentro del chat de Robbie */
    .robi-quick-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      padding: 0 18px 10px;
    }
    .robi-chip {
      appearance: none;
      border: 1px solid rgba(70, 227, 198, 0.4);
      background: rgba(70, 227, 198, 0.1);
      color: #d9fff7;
      border-radius: 999px;
      padding: 5px 10px;
      font-size: 11.5px;
      font-weight: 600;
      cursor: pointer;
    }
    .robi-chip:hover {
      background: rgba(70, 227, 198, 0.24);
    }

    /* ==========================================================================
       MODALIDAD ANDROID HORIZONTAL FORZADA Y UX MÓVIL ERGONÓMICA (SOLO ANDROID)
       ========================================================================== */
    body.is-android {
      overflow: hidden !important;
      touch-action: none;
      user-select: none;
      -webkit-user-select: none;
    }

    /* Garantizar con máxima especificidad que cualquier capa con .hidden o [hidden]
       permanezca 100% oculta en Android (evita que #creator aparezca sobre #menu) */
    body.is-android .hidden,
    body.is-android #app .hidden,
    body.is-android #creator.hidden,
    body.is-android #flight.hidden,
    body.is-android #hud.hidden,
    body.is-android #menu.hidden,
    body.is-android #loading.hidden,
    body.is-android [hidden]:not([hidden=until-found i]) {
      display: none !important;
    }

    /* Cuando el teléfono Android está físicamente en vertical (rawH > rawW),
       rotamos #app 90 grados usando las medidas exactas visibles (--and-w / --and-h)
       para que SIEMPRE se vea y use en horizontal sin recortarse por la barra de Chrome */
    body.is-android.android-rotated-90 #app {
      position: fixed !important;
      top: 0 !important;
      left: var(--and-h, 100vw) !important;
      width: var(--and-w, 100dvh) !important;
      height: var(--and-h, 100vw) !important;
      transform-origin: top left !important;
      transform: rotate(90deg) !important;
      overflow: hidden !important;
    }

    body.is-android:not(.android-rotated-90) #app {
      position: fixed !important;
      top: 0 !important;
      left: 0 !important;
      width: var(--and-w, 100vw) !important;
      height: var(--and-h, 100dvh) !important;
      overflow: hidden !important;
    }

    /* --- 0. PANTALLA DE TÍTULO (#title) EN ANDROID HORIZONTAL --- */
    body.is-android #title .t-bar {
      height: 6% !important;
    }
    body.is-android #title .t-box {
      gap: 4px !important;
    }
    body.is-android #title .t-logo {
      width: 52px !important;
    }
    body.is-android #title .t-kick {
      font-size: 11px !important;
    }
    body.is-android #title h1 {
      font-size: clamp(26px, 5vw, 40px) !important;
    }
    body.is-android #title .t-press {
      margin-top: 8px !important;
      font-size: 11.5px !important;
    }
    body.is-android #title .t-ver {
      bottom: 6px !important;
      font-size: 9px !important;
    }

    /* --- 1. MENÚ PRINCIPAL (#menu) EN ANDROID HORIZONTAL --- */
    body.is-android #menu,
    body.is-android #menu.m2,
    body.is-android.vm #menu {
      padding: 10px 16px !important;
      align-items: center !important;
      justify-content: flex-start !important;
      overflow: hidden !important;
    }
    body.is-android #menu .m2col,
    body.is-android.vm #menu .m2col {
      margin: auto auto auto 0 !important;
      width: min(540px, 60%) !important;
      max-width: 60% !important;
      max-height: calc(var(--and-h, 340px) - 16px) !important;
      align-items: flex-start !important;
      text-align: left !important;
      gap: 6px !important;
      justify-content: center !important;
    }
    body.is-android #menu .m2patch,
    body.is-android #menu .m2badge,
    body.is-android #menu .m2sub,
    body.is-android #menu .m2foot {
      display: none !important;
    }
    body.is-android #menu .m2kick {
      font-size: 10.5px !important;
      letter-spacing: 0.35em !important;
      padding-left: 0 !important;
    }
    body.is-android #menu .m2title {
      font-size: clamp(22px, 4.2vw, 32px) !important;
      line-height: 0.95 !important;
      margin: 0 0 2px 0 !important;
    }
    /* Cuadrícula amplia y cómoda de 6 columnas:
       - Botones principales (CONTINUAR / NUEVA PARTIDA) ocupan 3 columnas cada uno (2 por fila) con altura 46px.
       - Botones secundarios ocupan 2 columnas cada uno (3 por fila) con separación de 8pxx10px y tarjetas bien definidas. */
    body.is-android #menu .vmenu {
      display: grid !important;
      grid-template-columns: repeat(6, minmax(0, 1fr)) !important;
      gap: 8px 10px !important;
      width: 100% !important;
      max-width: 100% !important;
      margin-top: 2px !important;
    }
    body.is-android #menu .vmenu .vitem {
      padding: 7px 10px !important;
      min-height: 35px !important;
      font-size: 10.5px !important;
      letter-spacing: 0.04em !important;
      border-radius: 11px !important;
      background: rgba(14, 22, 48, 0.72) !important;
      border: 1px solid rgba(130, 165, 255, 0.24) !important;
      border-left: 3px solid rgba(111, 182, 255, 0.6) !important;
      justify-content: flex-start !important;
      text-align: left !important;
      gap: 7px !important;
    }
    body.is-android #menu .vmenu .vitem .vtxt {
      align-items: flex-start !important;
    }
    body.is-android #menu .vmenu .vitem small {
      font-size: 9px !important;
      line-height: 1.15 !important;
      margin-top: 2px !important;
    }
    body.is-android #menu .vmenu .vitem svg {
      width: 15px !important;
      height: 15px !important;
      flex: none !important;
    }
    body.is-android #menu .vmenu .vitem.m2btn {
      grid-column: span 3 !important;
      padding: 9px 12px !important;
      min-height: 46px !important;
      font-size: 11.5px !important;
      border-radius: 12px !important;
      background: linear-gradient(90deg, rgba(70, 227, 198, 0.18), rgba(16, 24, 52, 0.85)) !important;
      border: 1px solid rgba(70, 227, 198, 0.42) !important;
      border-left: 3.5px solid #46E3C6 !important;
    }
    body.is-android #menu .vmenu .vitem.m2btn.primary,
    body.is-android #menu .vmenu .vitem.m2btn.lead {
      background: linear-gradient(90deg, rgba(255, 181, 71, 0.26), rgba(16, 24, 52, 0.88)) !important;
      border: 1px solid rgba(255, 181, 71, 0.5) !important;
      border-left: 3.5px solid #FFB547 !important;
    }
    body.is-android #menu .vmenu .vitem.m2chip {
      grid-column: span 2 !important;
      padding: 7px 9px !important;
      min-height: 35px !important;
      font-size: 10px !important;
    }
    body.is-android #menu .vmenu .vitem[hidden] {
      display: none !important;
    }

    /* Derecha del Menú Principal en Android:
       Arriba a la derecha: Selector de idioma compacto (ES | EN) + Botón ROBBIE IA a su izquierda sin solaparse.
       Abajo a la derecha: Globo de bienvenida de Robbie compacto. */
    body.is-android #menu .m2lang {
      top: 10px !important;
      right: 12px !important;
      left: auto !important;
    }
    body.is-android #menu .m2lang .langsw {
      padding: 2px !important;
    }
    body.is-android #menu .m2lang .langsw button {
      min-height: 28px !important;
      padding: 4px 10px !important;
      font-size: 10.5px !important;
      min-width: 38px !important;
      justify-content: center !important;
    }
    body.is-android #menu .m2lang .langsw button span {
      display: none !important;
    }
    body.is-android #menu > #robbie-menu-right {
      top: 10px !important;
      right: 108px !important;
      bottom: auto !important;
      left: auto !important;
    }
    body.is-android .robbie-min-btn {
      padding: 4px 10px 4px 6px !important;
      gap: 6px !important;
    }
    body.is-android .robbie-min-btn .rb-ico {
      width: 26px !important;
      height: 24px !important;
    }
    body.is-android .robbie-min-btn .rb-meta b {
      font-size: 10.5px !important;
    }
    body.is-android .robbie-min-btn .rb-meta small {
      display: none !important;
    }
    body.is-android .rm-card {
      width: min(330px, calc(var(--and-w, 640px) - 20px)) !important;
      max-height: calc(var(--and-h, 340px) - 52px) !important;
      overflow-y: auto !important;
      padding: 10px 12px !important;
      gap: 8px !important;
    }
    body.is-android .rm-top {
      grid-template-columns: 64px 1fr auto !important;
      gap: 8px !important;
    }
    body.is-android .rm-stage {
      width: 64px !important;
      height: 60px !important;
    }
    body.is-android .rm-stage .rm-svg-fallback {
      width: 56px !important;
      height: 52px !important;
    }
    body.is-android .rm-identity h3 {
      font-size: 14px !important;
    }
    body.is-android .rm-identity p {
      font-size: 10.5px !important;
    }

    body.is-android #menu > #robbie-menu-speech {
      bottom: 10px !important;
      right: 12px !important;
      top: auto !important;
      left: auto !important;
      max-width: min(330px, 37%) !important;
      gap: 6px !important;
    }
    body.is-android #menu > #robbie-menu-speech .rb-speech-box {
      width: min(265px, 100%) !important;
      padding: 8px 10px !important;
      border-radius: 14px !important;
    }
    body.is-android #menu > #robbie-menu-speech .rb-speech-header {
      margin-bottom: 3px !important;
      gap: 5px !important;
      padding-right: 28px !important;
    }
    body.is-android #menu > #robbie-menu-speech .rb-speech-name {
      font-size: 12.5px !important;
    }
    body.is-android #menu > #robbie-menu-speech .rb-speech-badge {
      font-size: 7.5px !important;
      padding: 1.5px 5px !important;
    }
    body.is-android #menu > #robbie-menu-speech .rb-speech-text {
      font-size: 10.5px !important;
      line-height: 1.25 !important;
    }
    body.is-android #menu > #robbie-menu-speech .rb-speech-foot {
      display: grid !important;
      grid-template-columns: 1fr 1fr !important;
      margin-top: 6px !important;
      gap: 4px !important;
    }
    body.is-android #menu > #robbie-menu-speech #robbie-menu-next {
      grid-column: 1 / -1 !important;
    }
    body.is-android #menu > #robbie-menu-speech .rb-speech-foot button {
      padding: 4px 6px !important;
      font-size: 9.5px !important;
      justify-content: center !important;
    }
    body.is-android #menu > #robbie-menu-speech .rb-speech-char {
      width: 52px !important;
      height: 48px !important;
      flex: none !important;
    }

    /* --- 2. CREADOR DE PERSONAJE (#creator:not(.hidden)) EN ANDROID HORIZONTAL --- */
    body.is-android #creator:not(.hidden) {
      display: grid !important;
      grid-template-columns: minmax(230px, 45%) 1fr !important;
      grid-template-rows: 1fr !important;
    }
    body.is-android #creator .side {
      order: 1 !important;
      grid-column: 1 !important;
      grid-row: 1 !important;
      margin: 6px 0 6px 8px !important;
      max-height: calc(var(--and-h, 340px) - 12px) !important;
    }
    body.is-android #creator .stage {
      order: 2 !important;
      grid-column: 2 !important;
      grid-row: 1 !important;
    }
    body.is-android #creator .side header {
      padding: 6px 12px 4px !important;
      gap: 1px !important;
    }
    body.is-android #creator .side header .label {
      font-size: 9px !important;
    }
    body.is-android #creator #cr-title {
      font-size: 14px !important;
    }
    body.is-android #creator #cr-tabs {
      padding: 0 10px !important;
      margin-bottom: 6px !important;
      gap: 4px !important;
      flex-wrap: nowrap !important;
      overflow-x: auto !important;
      scrollbar-width: none !important;
    }
    body.is-android #creator #cr-tabs::-webkit-scrollbar {
      display: none !important;
    }
    body.is-android #creator #cr-tabs button {
      padding: 4px 8px !important;
      font-size: 10.5px !important;
      flex: none !important;
    }
    body.is-android #creator #cr-body {
      padding: 0 10px 6px !important;
    }
    body.is-android #creator .opt-group {
      padding: 6px 0 !important;
      gap: 4px !important;
    }
    body.is-android #creator .sw {
      width: 22px !important;
      height: 22px !important;
    }
    body.is-android #creator .pill {
      padding: 4px 8px !important;
      font-size: 10.5px !important;
    }
    body.is-android #creator .side footer {
      padding: 6px 10px !important;
      gap: 6px !important;
    }
    body.is-android #creator .side footer .btn {
      padding: 5px 10px !important;
      font-size: 11px !important;
    }
    body.is-android #creator .stage .hint {
      display: none !important;
    }
    body.is-android #creator .stage .animbar {
      bottom: 6px !important;
      padding: 4px 6px !important;
      gap: 4px !important;
      flex-wrap: nowrap !important;
      overflow-x: auto !important;
      max-width: calc(100% - 12px) !important;
    }

    /* --- 3. VUELO / DESPEGUE (#flight) EN ANDROID HORIZONTAL --- */
    body.is-android #flight .fl-top {
      top: 6px !important;
      gap: 4px !important;
    }
    body.is-android #flight .fl-tag {
      display: none !important;
    }
    body.is-android #flight .fl-route {
      width: min(340px, 52%) !important;
      padding: 4px 10px !important;
    }
    body.is-android #flight .fl-stats > div {
      padding: 2px 7px !important;
      min-width: 0 !important;
    }
    body.is-android #flight .fl-stats b {
      font-size: 11.5px !important;
    }
    body.is-android #flight .fl-skip {
      top: 6px !important;
      right: 8px !important;
      bottom: auto !important;
      padding: 5px 10px !important;
      font-size: 11px !important;
    }
    body.is-android #flight #fl-robi-top {
      top: 38px !important;
      right: 8px !important;
      bottom: auto !important;
    }
    body.is-android #flight .fl-check {
      top: 8px !important;
      left: 8px !important;
      bottom: auto !important;
      padding: 6px 10px !important;
      gap: 3px !important;
    }
    body.is-android #flight .fl-check li {
      font-size: 11px !important;
    }
    body.is-android #flight .fl-go {
      bottom: 8px !important;
      padding: 8px 18px !important;
      min-width: 220px !important;
    }
    body.is-android #flight .fl-go b {
      font-size: 16px !important;
    }
    body.is-android #flight[data-state="space"] .fl-joy {
      display: block !important;
      left: 12px !important;
      bottom: 12px !important;
      width: 96px !important;
      height: 96px !important;
    }
    body.is-android #flight .fl-joy i {
      width: 40px !important;
      height: 40px !important;
      margin: -20px !important;
    }
    body.is-android #flight[data-state="space"] .fl-btns {
      display: flex !important;
      right: 12px !important;
      bottom: 12px !important;
      gap: 8px !important;
    }
    body.is-android #flight .fl-btns button {
      width: 56px !important;
      height: 56px !important;
    }
    body.is-android #flight #fl-boost {
      width: 64px !important;
      height: 64px !important;
    }
    body.is-android #flight .fl-robi,
    body.is-android #flight[data-state^="pad"] .fl-robi,
    body.is-android #flight[data-state="count"] .fl-robi {
      right: 10px !important;
      left: auto !important;
      bottom: 10px !important;
      width: auto !important;
      max-width: min(320px, 46%) !important;
      padding: 0 !important;
      gap: 6px !important;
    }
    body.is-android #flight[data-state="space"] .fl-robi,
    body.is-android #flight[data-state="approach"] .fl-robi,
    body.is-android #flight[data-state="arrive"] .fl-robi {
      bottom: 84px !important;
    }
    body.is-android #flight .fl-robi .rb-speech-box {
      width: min(245px, 100%) !important;
      padding: 8px 10px !important;
      border-radius: 14px !important;
    }
    body.is-android #flight .fl-robi .rb-speech-header {
      margin-bottom: 3px !important;
      gap: 5px !important;
      padding-right: 28px !important;
    }
    body.is-android #flight .fl-robi .rb-speech-name {
      font-size: 12px !important;
    }
    body.is-android #flight .fl-robi .rb-speech-badge {
      font-size: 7.5px !important;
      padding: 1.5px 5px !important;
    }
    body.is-android #flight .fl-robi #fl-say {
      font-size: 10.5px !important;
      line-height: 1.25 !important;
    }
    body.is-android #flight .fl-robi .rb-speech-foot {
      margin-top: 6px !important;
      gap: 4px !important;
    }
    body.is-android #flight .fl-robi .rb-speech-foot button {
      padding: 3px 6px !important;
      font-size: 9px !important;
      flex: 1 1 auto !important;
      justify-content: center !important;
    }
    body.is-android #flight .fl-robi .rb-speech-char {
      width: 52px !important;
      height: 48px !important;
      flex: none !important;
    }

    /* --- 4. HUD DE JUEGO (#hud) EN ANDROID HORIZONTAL --- */
    /* Esquina superior izquierda: Retrato circular + Necesidades desplegables */
    body.is-android #hud .hud-tl {
      top: 6px !important;
      left: 6px !important;
      width: auto !important;
      gap: 0 !important;
    }
    body.is-android #hud .who {
      padding: 3px !important;
      border-radius: 999px !important;
      gap: 0 !important;
    }
    body.is-android #hud .who .meta {
      display: none !important;
    }
    body.is-android #hud .portrait {
      width: 40px !important;
      height: 40px !important;
    }
    body.is-android #hud .needs {
      display: none !important;
      position: absolute !important;
      top: 48px !important;
      left: 0 !important;
      width: 230px !important;
      max-height: calc(var(--and-h, 340px) - 56px) !important;
      overflow-y: auto !important;
      z-index: 25 !important;
      padding: 8px 10px !important;
    }
    body.is-android #hud.needs-open .needs {
      display: grid !important;
    }

    /* Centro superior: Barra de recursos vitales */
    body.is-android #hud .hud-top {
      top: 6px !important;
      bottom: auto !important;
      left: 54px !important;
      right: 225px !important;
      transform: none !important;
      max-width: none !important;
      padding: 3px 6px !important;
      gap: 2px !important;
      flex-wrap: nowrap !important;
      overflow-x: auto !important;
      scrollbar-width: none !important;
    }
    body.is-android #hud .hud-top::-webkit-scrollbar {
      display: none !important;
    }
    body.is-android #hud.building .hud-top {
      display: none !important;
    }
    body.is-android #hud .res {
      padding: 2px 4px !important;
      gap: 3px !important;
      flex-direction: row !important;
      align-items: center !important;
      flex: 1 0 auto !important;
    }
    body.is-android #hud .res .icon {
      width: 14px !important;
      height: 14px !important;
    }
    body.is-android #hud .res .val {
      font-size: 11px !important;
    }
    body.is-android #hud .res .rate {
      display: none !important;
    }

    /* Derecha superior: Reloj Solar + Botón ROBBIE IA debajo del reloj */
    body.is-android #hud .hud-tr {
      top: 6px !important;
      right: 6px !important;
      width: auto !important;
      display: flex !important;
      gap: 4px !important;
      align-items: center !important;
    }
    body.is-android #hud #minimap {
      display: none !important;
    }
    body.is-android #hud .clock {
      display: flex !important;
      align-items: center !important;
      gap: 6px !important;
      padding: 4px 8px !important;
      border-radius: 999px !important;
      width: auto !important;
    }
    body.is-android #hud .clock .t {
      font-size: 14px !important;
    }
    body.is-android #hud .clock #h-day {
      font-size: 9px !important;
      max-width: 72px !important;
    }
    body.is-android #hud .speed button {
      padding: 2px 5px !important;
      font-size: 10px !important;
    }
    body.is-android #hud #robbie-top-panel {
      top: 42px !important;
      right: 6px !important;
      left: auto !important;
      bottom: auto !important;
    }

    /* Esquina inferior izquierda: Joystick táctil ergonómico */
    body.is-android #hud:not(.sheet):not(.building) .joy {
      display: block !important;
      left: 10px !important;
      bottom: 10px !important;
      width: 92px !important;
      height: 92px !important;
    }
    body.is-android #hud .joy i {
      width: 38px !important;
      height: 38px !important;
      margin: -19px !important;
    }

    /* Esquina inferior derecha: Cuadrícula 2x2 de botones de acción para el pulgar derecho */
    body.is-android #hud:not(.sheet):not(.building) .touchbtns {
      display: grid !important;
      grid-template-columns: repeat(2, 46px) !important;
      gap: 6px !important;
      right: 10px !important;
      bottom: 10px !important;
    }
    body.is-android #hud .touchbtns button {
      width: 46px !important;
      height: 46px !important;
      font-size: 10px !important;
    }

    /* Centro inferior (entre el joystick y los botones de acción): Dock de herramientas deslizable */
    body.is-android #hud .hud-bottom {
      bottom: 8px !important;
      left: 112px !important;
      right: 114px !important;
      transform: none !important;
      width: auto !important;
      max-width: none !important;
      padding: 3px 6px !important;
      gap: 2px !important;
      overflow-x: auto !important;
      justify-content: flex-start !important;
      scrollbar-width: none !important;
    }
    body.is-android #hud .hud-bottom::-webkit-scrollbar {
      display: none !important;
    }
    body.is-android #hud #t-heart,
    body.is-android #hud #t-research,
    body.is-android #hud #t-scan,
    body.is-android #hud #t-camera {
      display: grid !important;
    }
    body.is-android #hud .tool {
      min-width: 48px !important;
      flex: 0 0 auto !important;
      padding: 4px 5px !important;
    }
    body.is-android #hud .tool .icon {
      width: 16px !important;
      height: 16px !important;
    }
    body.is-android #hud .tool span:not(.icon):not(.kbd) {
      display: block !important;
      font-size: 8.5px !important;
    }
    body.is-android #hud .tool .kbd {
      display: none !important;
    }

    /* Barra de construcción y menús contextuales en Android */
    body.is-android #hud .buildbar:not(.hidden) {
      bottom: 56px !important;
      left: 10px !important;
      right: 10px !important;
      transform: none !important;
      width: auto !important;
      padding: 6px 8px !important;
      gap: 4px !important;
    }
    body.is-android #hud .bcard {
      width: 96px !important;
      padding: 5px !important;
    }
    body.is-android #hud .bcard canvas {
      height: 38px !important;
    }
    body.is-android #hud .ctxmenu:not(.hidden),
    body.is-android #hud .dialog:not(.hidden) {
      left: 50% !important;
      right: auto !important;
      transform: translateX(-50%) !important;
      width: min(420px, calc(var(--and-w, 640px) - 24px)) !important;
      bottom: 58px !important;
      max-height: calc(var(--and-h, 340px) - 104px) !important;
    }
    body.is-android #hud .prompt:not(.hidden),
    body.is-android #hud .actbar:not(.hidden) {
      left: 50% !important;
      transform: translateX(-50%) !important;
      bottom: 60px !important;
      max-width: calc(var(--and-w, 640px) - 230px) !important;
      font-size: 11.5px !important;
      padding: 5px 10px !important;
    }

    /* Globos de texto de Robbie en HUD de Android (abajo a la derecha, encima de los botones de acción) */
    body.is-android #hud > #robbie-companion {
      bottom: 112px !important;
      right: 8px !important;
      left: auto !important;
      top: auto !important;
      max-width: min(310px, 46%) !important;
      gap: 6px !important;
    }
    body.is-android #hud > #robbie-companion .rb-speech-box {
      width: min(235px, 100%) !important;
      padding: 7px 10px !important;
      border-radius: 14px !important;
    }
    body.is-android #hud > #robbie-companion .rb-speech-name {
      font-size: 12px !important;
    }
    body.is-android #hud > #robbie-companion .rb-speech-text {
      font-size: 10px !important;
      line-height: 1.22 !important;
    }
    body.is-android #hud > #robbie-companion .rb-speech-foot {
      margin-top: 5px !important;
      gap: 4px !important;
    }
    body.is-android #hud > #robbie-companion .rb-speech-foot button {
      padding: 3px 6px !important;
      font-size: 9px !important;
    }
    body.is-android #hud > #robbie-companion .rb-speech-char {
      width: 52px !important;
      height: 48px !important;
    }

    /* Modales y Chat de Robbie adaptados a la altura horizontal de Android */
    body.is-android .modal-back:not(.hidden) {
      padding: 6px !important;
    }
    body.is-android .modal {
      width: min(560px, calc(var(--and-w, 640px) - 16px)) !important;
      max-height: calc(var(--and-h, 340px) - 12px) !important;
    }
    body.is-android .modal header {
      padding: 8px 12px !important;
    }
    body.is-android .modal header h2 {
      font-size: 15px !important;
    }
    body.is-android .modal .body {
      padding: 8px 12px !important;
    }
    body.is-android .modal footer {
      padding: 6px 12px !important;
    }
    body.is-android #modal-robi-chat .body {
      height: calc(var(--and-h, 340px) - 70px) !important;
      max-height: calc(var(--and-h, 340px) - 70px) !important;
      gap: 6px !important;
    }
  `;
  (document.body || document.head).appendChild(styleEl);

  /* ==========================================================================
     BANCO DE MENSAJES DE ROBBIE (ETAPAS 3, 4 Y 5)
     ========================================================================== */
  const GREETING_LINES = [
    () => tr('«¡Hola, astronauta! Soy Robbie, tu compañero de viaje.»', '"Hello, astronaut! I am Robbie, your travel companion."'),
    () => tr('«Puedes preguntarme cualquier duda que tengas sobre la misión.»', '"You can ask me any question you have about the mission."'),
    () => Device.getSummary()
  ];

  const SPACE_FUN_FACTS = [
    {
      title: 'Dato curioso · Nave Orión',
      text: 'La cápsula Orión de la NASA viaja a más de 39,000 km/h para recorrer los 384,400 km entre la Tierra y la Luna, ¡y su escudo térmico soporta 2,760 °C!'
    },
    {
      title: 'Dato curioso · Hielo en el Polo Sur Lunar',
      text: 'En el fondo de los cráteres oscuros del Polo Sur de la Luna hay hielo de agua de hace miles de millones de años. ¡Con él producimos agua potable y oxígeno!'
    },
    {
      title: 'Dato curioso · Gravedad Lunar',
      text: 'En la Luna pesas solo 1/6 de lo que pesas en la Tierra. ¡Por eso puedes dar saltos mucho más altos con tu traje espacial!'
    },
    {
      title: 'Dato curioso · El Regolito Lunar',
      text: 'El suelo lunar se llama regolito. Está formado por roca pulverizada por meteoritos y sirve para fabricar bloques y proteger los hábitats contra la radiación.'
    },
    {
      title: 'Dato curioso · Reciclaje de Agua NASA',
      text: 'En las misiones espaciales reales de la NASA se recicla más del 93% del agua (¡incluyendo la humedad del aire y el sudor!) para que cada gota cuente.'
    },
    {
      title: 'Dato curioso · Cultivos Espaciales',
      text: 'Los invernaderos espaciales usan luces LED rojas y azules para cultivar lechugas, rábanos y papas sin tierra, renovando el oxígeno y mejorando el ánimo.'
    },
    {
      title: 'Dato curioso · Tormentas Solares',
      text: 'Como la Luna no tiene atmósfera espesa ni campo magnético global, los astronautas se refugian dentro del hábitat cuando el Sol lanza una tormenta solar.'
    }
  ];

  const DISCOVERY_TEXTS = {
    rock: '«¡Buen trabajo! Has descubierto algo nuevo.» Encontraste minerales lunares ricos en titanio, hierro y silicio para construir módulos de la base.',
    ice: '«¡Buen trabajo! Has descubierto algo nuevo.» Hallaste hielo de agua pura: al fundirlo y usar electrólisis obtenemos agua potable y oxígeno respirable.',
    soil: '«¡Buen trabajo! Has descubierto algo nuevo.» Recolectaste regolito espacial: una vez lavado en el laboratorio sirve para cultivar plantas en el invernadero.',
    solar: '«¡Buen trabajo! Has descubierto algo nuevo.» El Panel Solar transforma la luz del Sol en electricidad para alimentar el soporte vital de toda la colonia.',
    oxygen: '«¡Buen trabajo! Has descubierto algo nuevo.» El Generador de O₂ separa las moléculas de agua en oxígeno para respirar e hidrógeno.',
    water: '«¡Buen trabajo! Has descubierto algo nuevo.» El Extractor y Reciclador de Agua purifica el hielo extraído para mantener hidratada a la tripulación.',
    greenhouse: '«¡Buen trabajo! Has descubierto algo nuevo.» El Invernadero Hidropónico produce alimentos frescos, captura CO₂ y alegra a los astronautas.',
    habitat: '«¡Buen trabajo! Has descubierto algo nuevo.» El Hábitat Presurizado protege a la tripulación del vacío espacial y de la radiación solar.',
    battery: '«¡Buen trabajo! Has descubierto algo nuevo.» El Banco de Baterías almacena energía eléctrica para que la base funcione durante las noches o tormentas.',
    research: '«¡Buen trabajo! Has descubierto algo nuevo.» El Laboratorio de Investigación analiza muestras de suelo y desbloquea nuevas tecnologías de la NASA.',
    antenna: '«¡Buen trabajo! Has descubierto algo nuevo.» La Antena de Comunicaciones mantiene el enlace directo con el Control de Misión en la Tierra.',
    launchpad: '«¡Buen trabajo! Has descubierto algo nuevo.» La Plataforma de Lanzamiento permite preparar cohetes hacia nuevas misiones en Marte.'
  };

  /* ==========================================================================
     ETAPA 2: MENÚ PRINCIPAL
     - Arriba a la derecha: Botón minimizado que despliega el panel de Robbie.
     - Abajo a la derecha: Globo de texto visible con Robbie (estilo captura).
     ========================================================================== */
  let menuGreetingIdx = 0;

  function buildMenuRightPanel() {
    const menu = document.getElementById('menu');
    if (!menu || document.getElementById('robbie-menu-right')) return;

    // 1. Botón minimizado + Panel desplegable en la PARTE SUPERIOR DERECHA
    const wrap = document.createElement('aside');
    wrap.id = 'robbie-menu-right';
    wrap.className = 'minimized';
    wrap.setAttribute('aria-label', 'Panel de Robbie');
    wrap.innerHTML = `
      <button type="button" class="robbie-min-btn" id="robbie-menu-toggle" title="Presiona para desplegar el panel de Robbie">
        <span class="rb-ico" id="robbie-menu-btn-ico">${getRobbieSVG('hello')}</span>
        <span class="rb-meta">
          <b><i></i> ROBBIE · IA</b>
          <small>Panel de compañero</small>
        </span>
        <span class="rb-caret">▾</span>
      </button>
      <div class="rm-card" id="robbie-menu-card">
        <div class="rm-top">
          <div class="rm-stage" id="robbie-menu-stage" title="Haz clic para que Robbie te salude">
            <div class="rm-svg-fallback" id="robbie-menu-svg">${getRobbieSVG('hello')}</div>
            <span class="rm-stage-tag">IA · ORIÓN</span>
          </div>
          <div class="rm-identity">
            <span class="rm-badge"><i></i> COMPAÑERO DE AVENTURA</span>
            <h3>¡Hola, soy Robbie!</h3>
            <p>Inteligencia artificial de <b>Junior Mission Orión</b>. Te acompaño en el menú, en la nave Orión y en toda la misión.</p>
          </div>
          <button type="button" class="rm-close" id="robbie-menu-close" title="Minimizar panel">✕</button>
        </div>
        <div class="rm-device" id="robbie-menu-device">
          <span id="robbie-menu-device-lbl">💻 Dispositivo detectado: <b>Computadora</b></span>
          <span style="font-size:11px;opacity:.85" id="robbie-menu-device-hint">Controles adaptados</span>
        </div>
        <div class="rm-actions">
          <button type="button" class="rm-btn primary" id="rm-btn-ask">💬 Preguntar duda</button>
          <button type="button" class="rm-btn" id="rm-btn-controls">🎮 Controles</button>
          <button type="button" class="rm-btn" id="rm-btn-fact">🌟 Dato curioso</button>
        </div>
      </div>
    `;
    menu.appendChild(wrap);

    // 2. Globo de texto visible ABAJO A LA DERECHA (estilo captura de referencia)
    const speechDock = document.createElement('div');
    speechDock.id = 'robbie-menu-speech';
    speechDock.className = 'robbie-speech-dock';
    speechDock.innerHTML = `
      <div class="rb-speech-box">
        <div class="rb-speech-header">
          <h4 class="rb-speech-name">Robbie</h4>
          <span class="rb-speech-badge" id="rm-speech-badge">Compañero de viaje</span>
          <button type="button" class="rb-speech-close" id="rm-speech-close" title="Ocultar globo">✕</button>
        </div>
        <p class="rb-speech-text" id="robbie-menu-bubble-txt">«¡Hola, astronauta! Soy Robbie, tu compañero de viaje. Puedes preguntarme cualquier duda que tengas.»</p>
        <div class="rb-speech-foot">
          <button type="button" id="robbie-menu-next">Siguiente consejo ▸</button>
          <button type="button" id="rm-speech-fact">🌟 Dato curioso</button>
          <button type="button" id="rm-speech-ask">💬 Preguntar duda</button>
        </div>
      </div>
      <button type="button" class="rb-speech-char" id="rm-speech-char" title="Hablar con Robbie">
        ${getRobbieSVG('hello')}
      </button>
    `;
    menu.appendChild(speechDock);

    const toggleMenuPanel = () => {
      try { JSM.Audio && JSM.Audio.sfx && JSM.Audio.sfx('click'); } catch (e) {}
      const isMin = wrap.classList.toggle('minimized');
      wrap.classList.toggle('robbie-open', !isMin);
      speechDock.classList.remove('hidden-dock');
    };

    document.getElementById('robbie-menu-toggle').addEventListener('click', toggleMenuPanel);
    document.getElementById('robbie-menu-close').addEventListener('click', () => {
      wrap.classList.add('minimized');
      wrap.classList.remove('robbie-open');
    });
    const closeMenuSpeech = (e) => {
      if (e) { e.preventDefault(); e.stopPropagation(); }
      speechDock.classList.add('hidden-dock');
    };
    const rmCloseBtn = document.getElementById('rm-speech-close');
    if (rmCloseBtn) {
      rmCloseBtn.addEventListener('click', closeMenuSpeech);
      rmCloseBtn.addEventListener('pointerdown', closeMenuSpeech);
    }

    const setMenuBubble = (text, mood, badgeText) => {
      speechDock.classList.remove('hidden-dock');
      const txtEl = document.getElementById('robbie-menu-bubble-txt');
      const badgeEl = document.getElementById('rm-speech-badge');
      const charEl = document.getElementById('rm-speech-char');
      const svgEl = document.getElementById('robbie-menu-svg');
      const btnIco = document.getElementById('robbie-menu-btn-ico');
      if (txtEl) txtEl.textContent = text;
      if (badgeEl && badgeText) badgeEl.textContent = badgeText;
      if (charEl) charEl.innerHTML = getRobbieSVG(mood || 'hello');
      if (svgEl) svgEl.innerHTML = getRobbieSVG(mood || 'hello');
      if (btnIco) btnIco.innerHTML = getRobbieSVG(mood || 'hello');
    };

    const cycleGreeting = () => {
      try { JSM.Audio && JSM.Audio.sfx && JSM.Audio.sfx('click'); } catch (e) {}
      menuGreetingIdx = (menuGreetingIdx + 1) % GREETING_LINES.length;
      setMenuBubble(GREETING_LINES[menuGreetingIdx](), 'hello', 'Compañero de viaje');
    };
    document.getElementById('robbie-menu-next').addEventListener('click', cycleGreeting);
    document.getElementById('robbie-menu-stage').addEventListener('click', cycleGreeting);
    document.getElementById('rm-speech-char').addEventListener('click', cycleGreeting);

    let factIdx = 0;
    const showMenuFact = () => {
      try { JSM.Audio && JSM.Audio.sfx && JSM.Audio.sfx('click'); } catch (e) {}
      const f = SPACE_FUN_FACTS[factIdx % SPACE_FUN_FACTS.length];
      factIdx++;
      setMenuBubble(`${f.text}`, 'fact', `🌟 ${f.title}`);
    };
    document.getElementById('rm-btn-fact').addEventListener('click', showMenuFact);
    document.getElementById('rm-speech-fact').addEventListener('click', showMenuFact);

    const openAsk = () => {
      try { JSM.Audio && JSM.Audio.sfx && JSM.Audio.sfx('click'); } catch (e) {}
      openRobbieChatModal();
    };
    document.getElementById('rm-btn-ask').addEventListener('click', openAsk);
    document.getElementById('rm-speech-ask').addEventListener('click', openAsk);

    document.getElementById('rm-btn-controls').addEventListener('click', () => {
      try { JSM.Audio && JSM.Audio.sfx && JSM.Audio.sfx('click'); } catch (e) {}
      setMenuBubble(Device.getSummary(), 'hello', `${Device.getIcon()} Controles · ${Device.getName()}`);
      if (JSM.Menu && JSM.Menu.howTo) JSM.Menu.howTo();
    });

    const menuHints = {
      'm-continue': '«¡Continuemos tu misión espacial donde la dejaste, astronauta!»',
      'm-new': '«¡Hola, astronauta! Aquí diseñaremos tu traje y despegaremos juntos de la Tierra a la Luna en la nave Orión.»',
      'm-scen': '«Elige entre entrenamiento lunar, construir la base en el Polo Sur de la Luna o viajar a Marte.»',
      'm-how': '«Aquí te explico paso a paso cómo jugar con controles adaptados a tu dispositivo.»',
      'm-opt': '«Configura el sonido, el idioma, el multijugador y cómo quieres que te acompañe.»'
    };
    Object.keys(menuHints).forEach(id => {
      const b = document.getElementById(id);
      if (b) {
        b.addEventListener('mouseenter', () => setMenuBubble(menuHints[id], 'hello', 'Consejo de Robbie'));
      }
    });

    updateDeviceUI();
  }

  function updateDeviceUI() {
    const lbl = document.getElementById('robbie-menu-device-lbl');
    const hint = document.getElementById('robbie-menu-device-hint');
    if (lbl) {
      lbl.innerHTML = `${Device.getIcon()} ${tr('Dispositivo detectado:', 'Detected device:')} <b>${Device.getName()}</b>`;
    }
    if (hint) {
      hint.textContent = (Device.type === 'tablet' || Device.type === 'mobile')
        ? tr('Controles táctiles activos', 'Touch controls active')
        : (Device.type === 'gamepad' ? tr('Mando conectado', 'Gamepad connected') : tr('Teclado + Ratón activos', 'Keyboard + Mouse active'));
    }
    const hudDevLbl = document.getElementById('robbie-hud-device-lbl');
    if (hudDevLbl) {
      hudDevLbl.innerHTML = `${Device.getIcon()} ${tr('Dispositivo:', 'Device:')} <b>${Device.getName()}</b>`;
    }
    const flHelp = document.getElementById('fl-help');
    if (flHelp && JSM.Flight) {
      flHelp.textContent = Device.getFlightInstructions(JSM.Flight.phase || 'space');
    }
  }

  /* ==========================================================================
     ETAPA 3: INCORPORAR A ROBBIE EN EL VIAJE DE LA TIERRA A LA LUNA
     - Modelo 3D dentro de la Cabina 3D de la nave Orión
     - En #flight:
       · Botón minimizado arriba a la derecha DEBAJO de #fl-skip ("Saltar viaje ›")
         para NO taparlo jamás.
       · Globo de texto de Robbie ABAJO A LA DERECHA (estilo captura).
     ========================================================================== */
  function createRobbie3D() {
    const group = new THREE.Group();
    group.name = 'robbie-axolotl-ufo';

    const craft = new THREE.Group();
    craft.position.y = 0.68;
    group.add(craft);

    const skinMat      = new THREE.MeshStandardMaterial({ color: 0xf7b2c4, roughness: 0.45, metalness: 0.05 });
    const cheekMat     = new THREE.MeshStandardMaterial({ color: 0xf07ca0, roughness: 0.5 });
    const gillMat      = new THREE.MeshStandardMaterial({ color: 0xff4f79, roughness: 0.42 });
    const gillDarkMat  = new THREE.MeshStandardMaterial({ color: 0xd9325e, roughness: 0.45 });
    const saucerMat    = new THREE.MeshStandardMaterial({ color: 0x7b80a6, roughness: 0.3, metalness: 0.68 });
    const saucerRimMat = new THREE.MeshStandardMaterial({ color: 0x999fc2, roughness: 0.28, metalness: 0.72 });
    const domeMat      = new THREE.MeshStandardMaterial({ color: 0x3b55b8, roughness: 0.08, metalness: 0.15, transparent: true, opacity: 0.32, depthWrite: false });
    const shineMat     = new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.88 });
    const glassBlack   = new THREE.MeshStandardMaterial({ color: 0x0d0b14, roughness: 0.18, metalness: 0.5 });
    const pixelWhite   = new THREE.MeshBasicMaterial({ color: 0xffffff });
    const lightPurple  = new THREE.MeshStandardMaterial({ color: 0xd86eff, emissive: 0xb845ff, emissiveIntensity: 1.6, roughness: 0.2 });
    const lightCore    = new THREE.MeshBasicMaterial({ color: 0xffe6ff });

    const ufoBody = new THREE.Mesh(new THREE.SphereGeometry(0.46, 24, 16), saucerMat);
    ufoBody.scale.set(1.18, 0.34, 1.12);
    ufoBody.position.y = -0.12;
    craft.add(ufoBody);

    const ufoCollar = new THREE.Mesh(new THREE.TorusGeometry(0.33, 0.055, 12, 28), saucerRimMat);
    ufoCollar.rotation.x = Math.PI / 2;
    ufoCollar.position.y = -0.01;
    craft.add(ufoCollar);

    const ufoBottom = new THREE.Mesh(new THREE.SphereGeometry(0.22, 18, 12), lightPurple);
    ufoBottom.scale.set(1.1, 0.65, 1.1);
    ufoBottom.position.y = -0.25;
    craft.add(ufoBottom);

    [-0.55, 0, 0.55, Math.PI - 0.55, Math.PI, Math.PI + 0.55].forEach((ang) => {
      const lg = new THREE.Group();
      const rx = Math.sin(ang) * 0.49;
      const rz = Math.cos(ang) * 0.46;
      const outer = new THREE.Mesh(new THREE.SphereGeometry(0.058, 12, 10), lightPurple);
      outer.scale.set(1.2, 0.85, 0.6);
      const inner = new THREE.Mesh(new THREE.SphereGeometry(0.032, 10, 8), lightCore);
      inner.position.z = 0.025;
      lg.add(outer, inner);
      lg.position.set(rx, -0.12, rz);
      lg.lookAt(rx * 2, -0.12, rz * 2);
      craft.add(lg);
    });

    const head = new THREE.Mesh(new THREE.SphereGeometry(0.28, 22, 18), skinMat);
    head.scale.set(1.12, 0.96, 1.0);
    head.position.set(0, 0.14, 0);
    craft.add(head);

    [-1, 1].forEach(s => {
      const cheek = new THREE.Mesh(new THREE.SphereGeometry(0.048, 10, 8), cheekMat);
      cheek.scale.set(1.3, 0.75, 0.5);
      cheek.position.set(s * 0.21, 0.1, 0.22);
      craft.add(cheek);
    });

    const paws = [];
    [-1, 1].forEach(s => {
      const paw = new THREE.Mesh(new THREE.SphereGeometry(0.068, 12, 10), skinMat);
      paw.scale.set(1.25, 0.72, 1.05);
      paw.position.set(s * 0.15, 0.03, 0.31);
      craft.add(paw);
      paws.push(paw);
    });

    const gills = [];
    [-1, 1].forEach(side => {
      const sideGroup = new THREE.Group();
      sideGroup.position.set(side * 0.28, 0.16, -0.02);
      for (let i = 0; i < 3; i++) {
        const branch = new THREE.Group();
        const stem = new THREE.Mesh(new THREE.CylinderGeometry(0.036, 0.028, 0.19, 8), i === 2 ? gillDarkMat : gillMat);
        stem.rotation.z = side * (Math.PI / 2 - 0.28 + i * 0.28);
        stem.position.set(side * 0.09, (1 - i) * 0.075, 0);
        branch.add(stem);
        const tip = new THREE.Mesh(new THREE.SphereGeometry(0.042, 8, 8), gillMat);
        tip.position.set(side * 0.17, (1 - i) * 0.095, 0);
        tip.scale.set(1.1, 0.85, 0.65);
        branch.add(tip);
        sideGroup.add(branch);
      }
      craft.add(sideGroup);
      gills.push(sideGroup);
    });

    const glasses = new THREE.Group();
    const topBar = new THREE.Mesh(new THREE.BoxGeometry(0.50, 0.028, 0.035), glassBlack);
    topBar.position.set(0, 0.23, 0.265);
    glasses.add(topBar);
    [-1, 1].forEach(s => {
      const lens = new THREE.Mesh(new THREE.BoxGeometry(0.19, 0.105, 0.032), glassBlack);
      lens.position.set(s * 0.125, 0.185, 0.265);
      glasses.add(lens);
      const p1 = new THREE.Mesh(new THREE.BoxGeometry(0.032, 0.032, 0.01), pixelWhite);
      p1.position.set(s * 0.125 - 0.035, 0.20, 0.282);
      const p2 = new THREE.Mesh(new THREE.BoxGeometry(0.032, 0.032, 0.01), pixelWhite);
      p2.position.set(s * 0.125 - 0.003, 0.17, 0.282);
      glasses.add(p1, p2);
    });
    craft.add(glasses);

    const mouthGroup = new THREE.Group();
    [-1, 1].forEach(s => {
      const arc = new THREE.Mesh(new THREE.TorusGeometry(0.028, 0.0085, 6, 12, Math.PI), glassBlack);
      arc.position.set(s * 0.028, 0.105, 0.275);
      arc.rotation.z = Math.PI;
      mouthGroup.add(arc);
    });
    craft.add(mouthGroup);

    const dome = new THREE.Mesh(new THREE.SphereGeometry(0.34, 22, 16, 0, Math.PI * 2, 0, Math.PI * 0.58), domeMat);
    dome.position.set(0, 0.02, 0);
    dome.scale.set(1.06, 1.08, 1.02);
    craft.add(dome);

    const domeShine = new THREE.Mesh(new THREE.SphereGeometry(0.045, 10, 8), shineMat);
    domeShine.scale.set(1.6, 0.7, 0.3);
    domeShine.position.set(-0.14, 0.29, 0.25);
    domeShine.rotation.z = 0.45;
    craft.add(domeShine);

    return {
      group,
      t: 0,
      setExpression(expr) {
        if (expr === 'preocupado' || expr === 'emergency') {
          lightPurple.color.setHex(0xff4d6d);
          lightPurple.emissive.setHex(0xff1e42);
        } else if (expr === 'entusiasmado' || expr === 'discovery') {
          lightPurple.color.setHex(0xffd25a);
          lightPurple.emissive.setHex(0xff9a1f);
        } else {
          lightPurple.color.setHex(0xd86eff);
          lightPurple.emissive.setHex(0xb845ff);
        }
      },
      animate(dt, mode, speed) {
        const sp = speed || 1;
        this.t += dt * sp;
        const t = this.t;
        craft.position.y = 0.68 + Math.sin(t * 2.6) * 0.045;
        craft.rotation.z = Math.sin(t * 1.7) * 0.055;
        craft.rotation.x = Math.cos(t * 1.3) * 0.035;
        if (gills[0]) gills[0].rotation.z = Math.sin(t * 3.2) * 0.08;
        if (gills[1]) gills[1].rotation.z = -Math.sin(t * 3.2) * 0.08;
        if (paws[1]) {
          paws[1].position.y = (mode === 'wave') ? (0.06 + Math.abs(Math.sin(t * 6)) * 0.06) : 0.03;
        }
        lightPurple.emissiveIntensity = 1.25 + Math.sin(t * 4.5) * 0.45;
      },
      dispose() {
        group.traverse(o => {
          if (o.geometry) o.geometry.dispose();
          if (o.material) {
            if (Array.isArray(o.material)) o.material.forEach(m => m.dispose());
            else o.material.dispose();
          }
        });
      }
    };
  }
  if (JSM.Robbie) JSM.Robbie.createModel = createRobbie3D;

  if (JSM.Interior && JSM.Interior.buildCabin) {
    const origBuildCabin = JSM.Interior.buildCabin;
    JSM.Interior.buildCabin = function (look) {
      const C = origBuildCabin.apply(this, arguments);
      try {
        if (C && C.astros && C.astros.length >= 3 && C.scene && C.R && C.R.seats) {
          const seatIdx = 0;
          const oldAstro = C.astros[seatIdx];
          if (oldAstro && oldAstro.group) {
            C.scene.remove(oldAstro.group);
            if (oldAstro.dispose) oldAstro.dispose();
          }
          const robbie3D = createRobbie3D();
          const [sx, sz] = C.R.seats[seatIdx];
          robbie3D.group.position.set(sx, 0.08, sz);
          robbie3D.group.rotation.y = Math.PI - 0.25;
          C.scene.add(robbie3D.group);
          C.astros[seatIdx] = robbie3D;

          const origCabinUpdate = C.update;
          C.update = function (dt, shake) {
            origCabinUpdate.apply(this, arguments);
            try { robbie3D.animate(dt, 'wave', 1.1); } catch (e) {}
          };
        }
      } catch (e) {}
      return C;
    };
  }

  if (JSM.Interior && JSM.Interior.ROOMS && JSM.Interior.ROOMS.orion) {
    const origOrionRoom = JSM.Interior.ROOMS.orion;
    JSM.Interior.ROOMS.orion = function (c) {
      const R = origOrionRoom.apply(this, arguments);
      try {
        const robbieCabin = createRobbie3D();
        robbieCabin.group.position.set(-1.2, 0.05, -0.4);
        robbieCabin.group.rotation.y = 0.35;
        R.g.add(robbieCabin.group);
        R.anim.push((dt) => {
          try { robbieCabin.animate(dt, 'wave', 0.9); } catch (e) {}
        });
        R.hotspot(-1.2, 0.35, tr('Hablar con Robbie (Compañero de viaje)', 'Talk to Robbie (Travel companion)'), [], { x: -1.2, z: -0.4 });
      } catch (e) {}
      return R;
    };
  }

  /* ---------- UI de Robbie en el Despegue y Viaje (#flight) ---------- */
  function upgradeFlightCompanionUI() {
    const flightEl = document.getElementById('flight');
    const flRobi = document.querySelector('#flight .fl-robi');
    if (!flightEl || !flRobi || flRobi.dataset.upgraded === '1') return;
    flRobi.dataset.upgraded = '1';

    const existingSay = document.getElementById('fl-say');
    const currentText = (existingSay && existingSay.innerHTML) ? existingSay.innerHTML : '«¡Hola, astronauta! Soy Robbie, tu compañero de viaje.»';

    // 1. Botón minimizado en la parte superior derecha DEBAJO de #fl-skip ("Saltar viaje ›")
    if (!document.getElementById('fl-robi-top')) {
      const topWrap = document.createElement('div');
      topWrap.id = 'fl-robi-top';
      topWrap.className = 'minimized';
      topWrap.innerHTML = `
        <button type="button" class="robbie-min-btn" id="fl-robi-toggle" title="Presiona para abrir el panel de Robbie">
          <span class="rb-ico">${getRobbieSVG('hello')}</span>
          <span class="rb-meta">
            <b><i></i> ROBBIE · ORIÓN</b>
            <small>Copiloto en cabina</small>
          </span>
          <span class="rb-caret">▾</span>
        </button>
        <div class="rm-card" id="fl-robi-top-card">
          <div class="rm-top">
            <div class="rm-stage">
              <div class="rm-svg-fallback">${getRobbieSVG('hello')}</div>
              <span class="rm-stage-tag">CABINA ORIÓN</span>
            </div>
            <div class="rm-identity">
              <span class="rm-badge"><i></i> COMPAÑERO DE VUELO</span>
              <h3>Robbie en Cabina</h3>
              <p id="fl-robi-device-tip">${Device.getFlightInstructions(JSM.Flight ? JSM.Flight.phase : 'pad')}</p>
            </div>
            <button type="button" class="rm-close" id="fl-robi-top-close" title="Minimizar">✕</button>
          </div>
          <div class="rm-actions">
            <button type="button" class="rm-btn primary" id="fl-top-ask">💬 Preguntar</button>
            <button type="button" class="rm-btn" id="fl-top-fact">🌟 Dato curioso</button>
            <button type="button" class="rm-btn" id="fl-top-show-bub">💬 Mostrar globo</button>
          </div>
        </div>
      `;
      flightEl.appendChild(topWrap);

      document.getElementById('fl-robi-toggle').addEventListener('click', (e) => {
        e.stopPropagation();
        const isMin = topWrap.classList.toggle('minimized');
        topWrap.classList.toggle('robbie-open', !isMin);
      });
      document.getElementById('fl-robi-top-close').addEventListener('click', (e) => {
        e.stopPropagation();
        topWrap.classList.add('minimized');
        topWrap.classList.remove('robbie-open');
      });
      document.getElementById('fl-top-ask').addEventListener('click', (e) => {
        e.stopPropagation();
        openRobbieChatModal();
      });
      document.getElementById('fl-top-show-bub').addEventListener('click', (e) => {
        e.stopPropagation();
        flRobi.classList.remove('hidden-dock');
        flRobi.style.removeProperty('display');
      });
    }

    // 2. Globo de texto ABAJO A LA DERECHA (estilo captura de referencia) con #fl-say adentro
    flRobi.classList.add('robbie-speech-dock');
    flRobi.innerHTML = `
      <div class="rb-speech-box">
        <div class="rb-speech-header">
          <h4 class="rb-speech-name">Robbie</h4>
          <span class="rb-speech-badge">Copiloto · Nave Orión</span>
          <button type="button" class="rb-speech-close" id="fl-speech-close" title="Ocultar globo">✕</button>
        </div>
        <p id="fl-say">${currentText}</p>
        <div class="rb-speech-foot">
          <button type="button" id="fl-btn-fact">🌟 Dato curioso</button>
          <button type="button" id="fl-btn-ask">💬 Preguntar duda</button>
        </div>
      </div>
      <button type="button" class="rb-speech-char" id="fl-robi-avatar" title="Robbie Copiloto">
        ${getRobbieSVG('hello')}
      </button>
    `;

    let fIdx = 0;
    const triggerFlightFact = (e) => {
      if (e) e.stopPropagation();
      flRobi.classList.remove('hidden-dock');
      flRobi.style.removeProperty('display');
      const f = SPACE_FUN_FACTS[fIdx % SPACE_FUN_FACTS.length];
      fIdx++;
      const sayEl = document.getElementById('fl-say');
      const avEl = document.getElementById('fl-robi-avatar');
      if (sayEl) sayEl.textContent = `🌟 ${f.title}: ${f.text}`;
      if (avEl) avEl.innerHTML = getRobbieSVG('fact');
    };
    document.getElementById('fl-btn-fact').addEventListener('click', triggerFlightFact);
    document.getElementById('fl-robi-avatar').addEventListener('click', triggerFlightFact);
    const topFactBtn = document.getElementById('fl-top-fact');
    if (topFactBtn) topFactBtn.addEventListener('click', triggerFlightFact);

    document.getElementById('fl-btn-ask').addEventListener('click', (e) => {
      e.stopPropagation();
      openRobbieChatModal();
    });
    const closeFlightBubble = (e) => {
      if (e) { e.preventDefault(); e.stopPropagation(); }
      flRobi.classList.add('hidden-dock');
      flRobi.style.setProperty('display', 'none', 'important');
    };
    const flCloseBtn = document.getElementById('fl-speech-close');
    if (flCloseBtn) {
      flCloseBtn.addEventListener('click', closeFlightBubble);
      flCloseBtn.addEventListener('pointerdown', closeFlightBubble);
    }
  }

  if (JSM.Flight && JSM.Flight.start) {
    const origFlightStart = JSM.Flight.start;
    JSM.Flight.start = function (opts) {
      Device.detect();
      const res = origFlightStart.apply(this, arguments);
      const applyFlightRobbie = () => {
        upgradeFlightCompanionUI();
        const flRobi = document.querySelector('#flight .fl-robi');
        if (flRobi && !flRobi.classList.contains('hidden-dock')) {
          flRobi.style.removeProperty('display');
        }
        const sayEl = document.getElementById('fl-say');
        const subEl = document.getElementById('fl-robi-device-tip');
        const helpEl = document.getElementById('fl-help');
        const goSmall = document.querySelector('#fl-go small');
        const landSmall = document.querySelector('#fl-land small');
        const isTouch = (Device.type === 'tablet' || Device.type === 'mobile');

        if (sayEl && !sayEl.textContent.trim()) {
          sayEl.textContent = tr(
            '«¡Hola, astronauta! Soy Robbie, tu compañero de viaje.» Estoy contigo dentro de la nave Orión.',
            '"Hello, astronaut! I am Robbie, your travel companion." I am right here with you inside Orion.'
          );
        }
        if (subEl) subEl.textContent = Device.getFlightInstructions(JSM.Flight.phase || 'pad');
        if (helpEl) helpEl.textContent = Device.getFlightInstructions(JSM.Flight.phase || 'pad');
        if (goSmall) goSmall.textContent = isTouch ? tr('Toca aquí para despegar', 'Tap here to launch') : tr('Pulsa ESPACIO o haz clic aquí', 'Press SPACE or click here');
        if (landSmall) landSmall.textContent = isTouch ? tr('Toca aquí para aterrizar', 'Tap here to land') : tr('Pulsa ESPACIO o haz clic aquí', 'Press SPACE or click here');
      };
      applyFlightRobbie();
      setTimeout(applyFlightRobbie, 50);
      return res;
    };

    if (JSM.Flight.finish) {
      const origFlightFinish = JSM.Flight.finish;
      JSM.Flight.finish = function (skipped) {
        if (!document.getElementById('fl-say') && JSM.Flight.el) {
          const dummy = document.createElement('p');
          dummy.id = 'fl-say';
          JSM.Flight.el.appendChild(dummy);
        }
        return origFlightFinish.apply(this, arguments);
      };
    }

    if (JSM.Flight.update) {
      let lastFlightPhase = '';
      const origFlightUpdate = JSM.Flight.update;
      JSM.Flight.update = function (dt) {
        const r = origFlightUpdate.apply(this, arguments);
        const ph = JSM.Flight.phase || '';
        if (ph !== lastFlightPhase) {
          lastFlightPhase = ph;
          const subEl = document.getElementById('fl-robi-device-tip');
          const helpEl = document.getElementById('fl-help');
          const instr = Device.getFlightInstructions(ph);
          if (subEl) subEl.textContent = instr;
          if (helpEl) helpEl.textContent = instr;
        }
        return r;
      };
    }
  }

  /* ==========================================================================
     ETAPAS 4 Y 5: EN PARTIDA (#hud)
     1. Botón minimizado arriba a la derecha (#robbie-top-panel) que despliega el
        panel actual de Robbie al presionarlo.
     2. Globo de texto visible ABAJO A LA DERECHA (#robbie-companion, estilo
        captura de referencia) para bienvenida, datos curiosos, descubrimientos
        y señales de emergencia.
     ========================================================================== */
  const seenDiscoveries = new Set();
  const seenBuildings = new Set();
  let hudHideTimer = null;

  function ensureCompanionDOM() {
    const hud = document.getElementById('hud');
    if (!hud) return null;

    // Eliminar cualquier botón residual de Robbie Chat en la barra inferior
    const oldTool = document.getElementById('t-robot');
    if (oldTool) oldTool.remove();

    let speechEl = document.getElementById('robbie-companion');
    if (speechEl) return speechEl;

    // 1. Botón minimizado + Panel desplegable ARRIBA A LA DERECHA
    const topPanel = document.createElement('aside');
    topPanel.id = 'robbie-top-panel';
    topPanel.className = 'minimized';
    topPanel.innerHTML = `
      <button type="button" class="robbie-min-btn" id="rc-top-toggle" title="Presiona para desplegar el panel de Robbie">
        <span class="rb-ico" id="rc-top-ico">${getRobbieSVG('hello')}</span>
        <span class="rb-meta">
          <b><i></i> ROBBIE · IA</b>
          <small id="rc-top-sub">Compañero de viaje</small>
        </span>
        <span class="rb-caret">▾</span>
      </button>
      <div class="rm-card" id="rc-top-card">
        <div class="rm-top">
          <div class="rm-stage" id="rc-top-stage">
            <div class="rm-svg-fallback" id="rc-top-stage-svg">${getRobbieSVG('hello')}</div>
            <span class="rm-stage-tag">IA · ORIÓN</span>
          </div>
          <div class="rm-identity">
            <span class="rm-badge"><i></i> PANEL DE ROBBIE</span>
            <h3>¡Hola, astronauta!</h3>
            <p>Soy Robbie, tu compañero de viaje. Pregúntame dudas, revisa tus controles o descubre datos espaciales.</p>
          </div>
          <button type="button" class="rm-close" id="rc-top-close" title="Minimizar panel">✕</button>
        </div>
        <div class="rm-device">
          <span id="robbie-hud-device-lbl">${Device.getIcon()} Dispositivo: <b>${Device.getName()}</b></span>
          <span style="font-size:11px;opacity:.85">Adaptado</span>
        </div>
        <div class="rm-actions">
          <button type="button" class="rm-btn primary" id="rc-top-ask">💬 Preguntar duda</button>
          <button type="button" class="rm-btn" id="rc-top-controls">🎮 Controles</button>
          <button type="button" class="rm-btn" id="rc-top-fact">🌟 Dato curioso</button>
        </div>
      </div>
    `;
    hud.appendChild(topPanel);

    // 2. Globo de texto visible ABAJO A LA DERECHA (estilo captura de referencia)
    speechEl = document.createElement('div');
    speechEl.id = 'robbie-companion';
    speechEl.className = 'robbie-speech-dock cat-welcome';
    speechEl.innerHTML = `
      <div class="rb-speech-box" id="rc-bubble">
        <div class="rb-speech-header">
          <h4 class="rb-speech-name" id="rc-title">Robbie</h4>
          <span class="rb-speech-badge" id="rc-cat">Compañero de viaje</span>
          <button type="button" class="rb-speech-close" id="rc-close" title="Ocultar globo">✕</button>
        </div>
        <p class="rb-speech-text" id="rc-text">«¡Hola, astronauta! Soy Robbie, tu compañero de viaje. Puedes preguntarme cualquier duda que tengas.»</p>
        <div class="rb-speech-foot">
          <button type="button" id="rc-btn-fact">🌟 Dato curioso</button>
          <button type="button" id="rc-btn-controls">🎮 Controles (${Device.getName()})</button>
          <button type="button" id="rc-btn-ask">💬 Preguntar duda</button>
        </div>
      </div>
      <button type="button" class="rb-speech-char" id="rc-avatar-btn" title="Hablar con Robbie">
        ${getRobbieSVG('hello')}
      </button>
    `;
    hud.appendChild(speechEl);

    const toggleTopPanel = (e) => {
      if (e) e.stopPropagation();
      try { JSM.Audio && JSM.Audio.sfx && JSM.Audio.sfx('click'); } catch (err) {}
      const isMin = topPanel.classList.toggle('minimized');
      topPanel.classList.toggle('robbie-open', !isMin);
      speechEl.classList.remove('hidden-dock');
    };

    document.getElementById('rc-top-toggle').addEventListener('click', toggleTopPanel);
    document.getElementById('rc-top-close').addEventListener('click', (e) => {
      e.stopPropagation();
      topPanel.classList.add('minimized');
      topPanel.classList.remove('robbie-open');
    });

    const closeHudSpeech = (e) => {
      if (e) { e.preventDefault(); e.stopPropagation(); }
      speechEl.classList.add('hidden-dock');
    };
    const rcCloseBtn = document.getElementById('rc-close');
    if (rcCloseBtn) {
      rcCloseBtn.addEventListener('click', closeHudSpeech);
      rcCloseBtn.addEventListener('pointerdown', closeHudSpeech);
    }

    let hudFactIdx = 0;
    const triggerHudFact = () => {
      try { JSM.Audio && JSM.Audio.sfx && JSM.Audio.sfx('click'); } catch (err) {}
      const f = SPACE_FUN_FACTS[hudFactIdx % SPACE_FUN_FACTS.length];
      hudFactIdx++;
      showRobbieSpeech({
        category: 'fact',
        badge: `🌟 ${f.title}`,
        title: 'Robbie',
        text: f.text,
        mood: 'fact'
      });
    };

    document.getElementById('rc-btn-fact').addEventListener('click', triggerHudFact);
    document.getElementById('rc-top-fact').addEventListener('click', triggerHudFact);
    document.getElementById('rc-avatar-btn').addEventListener('click', () => {
      if (speechEl.classList.contains('hidden-dock')) {
        speechEl.classList.remove('hidden-dock');
      } else {
        triggerHudFact();
      }
    });

    const triggerHudControls = () => {
      try { JSM.Audio && JSM.Audio.sfx && JSM.Audio.sfx('click'); } catch (err) {}
      showRobbieSpeech({
        category: 'welcome',
        badge: `${Device.getIcon()} Controles · ${Device.getName()}`,
        title: 'Robbie',
        text: Device.getSummary(),
        mood: 'hello'
      });
    };
    document.getElementById('rc-btn-controls').addEventListener('click', triggerHudControls);
    document.getElementById('rc-top-controls').addEventListener('click', () => {
      triggerHudControls();
      if (JSM.Menu && JSM.Menu.howTo) JSM.Menu.howTo();
    });

    document.getElementById('rc-btn-ask').addEventListener('click', () => openRobbieChatModal());
    document.getElementById('rc-top-ask').addEventListener('click', () => openRobbieChatModal());

    return speechEl;
  }

  function showRobbieSpeech(opts) {
    const el = ensureCompanionDOM();
    if (!el) return;
    const cat = opts.category || 'welcome';
    el.className = 'robbie-speech-dock cat-' + cat;
    el.classList.remove('hidden-dock');

    const catEl = document.getElementById('rc-cat');
    const titleEl = document.getElementById('rc-title');
    const textEl = document.getElementById('rc-text');
    const charBtn = document.getElementById('rc-avatar-btn');
    const topIco = document.getElementById('rc-top-ico');
    const topStageSvg = document.getElementById('rc-top-stage-svg');
    const topSub = document.getElementById('rc-top-sub');
    const ctrlBtn = document.getElementById('rc-btn-controls');

    if (catEl) catEl.textContent = opts.badge || 'Compañero de viaje';
    if (titleEl) titleEl.textContent = 'Robbie';
    const fullText = (opts.title && opts.title !== 'Robbie' && !opts.text.includes(opts.title))
      ? `${opts.title} ${opts.text || ''}`
      : (opts.text || '');
    if (textEl) textEl.textContent = fullText;
    if (charBtn) charBtn.innerHTML = getRobbieSVG(opts.mood || 'hello');
    if (topIco) topIco.innerHTML = getRobbieSVG(opts.mood || 'hello');
    if (topStageSvg) topStageSvg.innerHTML = getRobbieSVG(opts.mood || 'hello');
    if (topSub) {
      topSub.textContent = cat === 'emergency'
        ? '¡Alerta de emergencia!'
        : (cat === 'discovery' ? '¡Nuevo descubrimiento!' : (cat === 'fact' ? 'Dato curioso' : 'Compañero de viaje'));
    }
    if (ctrlBtn) ctrlBtn.textContent = `🎮 Controles (${Device.getName()})`;

    if (hudHideTimer) clearTimeout(hudHideTimer);
    const dur = opts.duration || (cat === 'emergency' ? 22000 : 16000);
    hudHideTimer = setTimeout(() => {
      if (el && !el.matches(':hover')) {
        el.classList.add('hidden-dock');
      }
    }, dur);
  }

  if (JSM.Robbie) {
    JSM.Robbie.speak = showRobbieSpeech;
    JSM.Robbie.svg = getRobbieSVG;
  }

  if (G.settings && !G.settings.robbieModeUserSet) {
    G.settings.robbieMode = 'chat';
  }

  /* ---------- Bienvenida al iniciar la partida ---------- */
  const origStartPlay = G.startPlay;
  if (origStartPlay) {
    G.startPlay = function () {
      Device.detect();
      const r = origStartPlay.apply(this, arguments);
      setTimeout(() => {
        ensureCompanionDOM();
        showRobbieSpeech({
          category: 'welcome',
          badge: '👋 Bienvenida a la misión',
          title: '«¡Hola, astronauta! Soy Robbie, tu compañero de viaje.»',
          text: `«Puedes preguntarme cualquier duda que tengas.» ${Device.getSummary()}`,
          mood: 'hello',
          duration: 18000
        });
      }, 650);
      return r;
    };
  }

  /* ---------- Datos Curiosos, Señales de Emergencia y Descubrimientos (SIN DUPLICADOS) ---------- */
  if (UI.eduCard) {
    UI.eduCard = function (title, text) {
      // Eliminar cualquier tarjeta antigua .educard para evitar duplicados
      document.querySelectorAll('.educard, #guidebub').forEach(el => el.remove());
      const hud = document.getElementById('hud');
      if (hud) hud.classList.remove('edu-open');
      showRobbieSpeech({
        category: 'fact',
        badge: '🌟 Dato curioso espacial',
        title: title || '',
        text: text || '',
        mood: 'fact',
        duration: 16000
      });
    };
  }

  // Redirigir también JSM.Guides.say al nuevo globo de Robbie y eliminar #guidebub antiguo
  if (JSM.Guides && JSM.Guides.say) {
    JSM.Guides.say = function (who, text, o) {
      document.querySelectorAll('#guidebub, .educard').forEach(el => el.remove());
      if (JSM.Guides.isOff && JSM.Guides.isOff()) return false;
      const msg = (text && ( tr(text.es, text.en) )) || String(text || '');
      if (!msg) return false;
      showRobbieSpeech({
        category: 'welcome',
        badge: '💡 Consejo de misión',
        title: '',
        text: msg,
        mood: 'hello',
        duration: 14000
      });
      return true;
    };
  }

  /* ==========================================================================
     FONDO DEL ESPACIO DINÁMICO EN LA SELECCIÓN / PERSONALIZACIÓN DE PERSONAJE
     (Game.buildCreatorScene y Game.updateCreator)
     ========================================================================== */
  function makeNebulaSkyTexture() {
    const c = document.createElement('canvas');
    c.width = 1024;
    c.height = 512;
    const ctx = c.getContext('2d');
    const bg = ctx.createLinearGradient(0, 0, 0, 512);
    bg.addColorStop(0, '#040614');
    bg.addColorStop(0.45, '#0b1030');
    bg.addColorStop(0.75, '#170d38');
    bg.addColorStop(1, '#050716');
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, 1024, 512);

    // Nebulosas cósmicas brillantes (morado, cian, azul y dorado)
    const clouds = [
      [220, 180, 210, 'rgba(184, 77, 255, 0.28)'],
      [540, 230, 260, 'rgba(70, 227, 198, 0.20)'],
      [820, 160, 220, 'rgba(111, 182, 255, 0.25)'],
      [380, 320, 190, 'rgba(255, 110, 180, 0.18)'],
      [700, 310, 210, 'rgba(140, 82, 255, 0.24)']
    ];
    clouds.forEach(([x, y, r, col]) => {
      const g = ctx.createRadialGradient(x, y, 8, x, y, r);
      g.addColorStop(0, col);
      g.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = g;
      ctx.fillRect(0, 0, 1024, 512);
    });

    // Miles de microestrellas en la bóveda celeste
    for (let i = 0; i < 900; i++) {
      const x = Math.random() * 1024;
      const y = Math.random() * 512;
      const s = Math.random() < 0.12 ? 2.1 : 1.1;
      ctx.fillStyle = Math.random() < 0.2 ? '#b8e4ff' : (Math.random() < 0.15 ? '#ffdca8' : '#ffffff');
      ctx.globalAlpha = 0.35 + Math.random() * 0.65;
      ctx.fillRect(x, y, s, s);
    }
    ctx.globalAlpha = 1;
    const tex = new THREE.CanvasTexture(c);
    tex.encoding = THREE.sRGBEncoding;
    return tex;
  }

  function enhanceCreatorScene() {
    if (!G || !THREE) return;
    G.buildCreatorScene = function () {
      const prevAstro = (G.cr && G.cr.astro) ? G.cr.astro : null;
      const prevLook = (G.cr && G.cr.look) ? G.cr.look : null;

      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x050818);
      // Sin niebla espesa para que el espacio profundo, los planetas y las estrellas brillen con nitidez
      scene.fog = null;

      const cam = new THREE.PerspectiveCamera(36, innerWidth / innerHeight, 0.05, 160);
      scene.add(new THREE.HemisphereLight(0xd4e4ff, 0x1c1436, 0.85));

      const key = new THREE.DirectionalLight(0xfff3e0, 1.85);
      key.position.set(3, 5, 4);
      key.castShadow = true;
      key.shadow.mapSize.set(1024, 1024);
      Object.assign(key.shadow.camera, { left: -3, right: 3, top: 3, bottom: -3 });
      scene.add(key);

      const rim = new THREE.DirectionalLight(0x46E3C6, 1.35);
      rim.position.set(-4, 3, -4);
      scene.add(rim);

      const rim2 = new THREE.DirectionalLight(0xb84dff, 1.1);
      rim2.position.set(4, 2, -3);
      scene.add(rim2);

      // Plataforma holográfica espacial bajo el astronauta
      const floor = new THREE.Mesh(
        new THREE.CylinderGeometry(2.2, 2.45, 0.3, 64),
        new THREE.MeshStandardMaterial({ color: 0x161f48, roughness: 0.32, metalness: 0.72 })
      );
      floor.position.y = -0.15;
      floor.receiveShadow = true;
      scene.add(floor);

      const ring = new THREE.Mesh(
        new THREE.TorusGeometry(2.26, 0.028, 10, 96),
        new THREE.MeshBasicMaterial({ color: 0x46E3C6 })
      );
      ring.rotation.x = Math.PI / 2;
      ring.position.y = 0.01;
      scene.add(ring);

      const ring2 = new THREE.Mesh(
        new THREE.TorusGeometry(1.65, 0.018, 8, 96),
        new THREE.MeshBasicMaterial({ color: 0xb84dff })
      );
      ring2.rotation.x = Math.PI / 2;
      ring2.position.y = 0.02;
      scene.add(ring2);

      const ring3 = new THREE.Mesh(
        new THREE.TorusGeometry(2.75, 0.012, 8, 96),
        new THREE.MeshBasicMaterial({ color: 0xFFB547, transparent: true, opacity: 0.65 })
      );
      ring3.rotation.x = Math.PI / 2;
      ring3.position.y = -0.02;
      scene.add(ring3);

      // 1. Bóveda de nebulosa espacial dinámica
      const skyDome = new THREE.Mesh(
        new THREE.SphereGeometry(68, 40, 24),
        new THREE.MeshBasicMaterial({ map: makeNebulaSkyTexture(), side: THREE.BackSide })
      );
      scene.add(skyDome);

      // 2. Campo de estrellas 3D multicapa en movimiento
      const makeStarLayer = (count, radiusMin, radiusMax, size, colHex) => {
        const geo = new THREE.BufferGeometry();
        const pos = new Float32Array(count * 3);
        for (let i = 0; i < count; i++) {
          const r = radiusMin + Math.random() * (radiusMax - radiusMin);
          const theta = Math.random() * Math.PI * 2;
          const phi = Math.acos(2 * Math.random() - 1);
          pos[i * 3]     = r * Math.sin(phi) * Math.cos(theta);
          pos[i * 3 + 1] = r * Math.cos(phi) * 0.65 + 1.5;
          pos[i * 3 + 2] = -Math.abs(r * Math.sin(phi) * Math.sin(theta)) - 3;
        }
        geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
        const mat = new THREE.PointsMaterial({ size, color: colHex, transparent: true, opacity: 0.92 });
        const pts = new THREE.Points(geo, mat);
        scene.add(pts);
        return pts;
      };
      const starsWhite  = makeStarLayer(1100, 12, 52, 0.085, 0xffffff);
      const starsCyan   = makeStarLayer(320, 9, 38, 0.11, 0x46E3C6);
      const starsPurple = makeStarLayer(280, 10, 42, 0.12, 0xd88cff);

      // 3. Planeta Tierra girando en el fondo + Luna en órbita
      const earthGroup = new THREE.Group();
      earthGroup.position.set(-4.8, 2.7, -14.5);
      const earthTex = (U && U.planetTex) ? U.planetTex('earth') : null;
      const earth = new THREE.Mesh(
        new THREE.SphereGeometry(2.35, 32, 24),
        new THREE.MeshStandardMaterial({ map: earthTex, roughness: 0.65, metalness: 0.08, color: earthTex ? 0xffffff : 0x2e6fd9 })
      );
      earthGroup.add(earth);
      const atmo = new THREE.Mesh(
        new THREE.SphereGeometry(2.52, 28, 20),
        new THREE.MeshBasicMaterial({ color: 0x55b4ff, transparent: true, opacity: 0.18, side: THREE.BackSide })
      );
      earthGroup.add(atmo);

      const moonPivot = new THREE.Group();
      moonPivot.rotation.z = 0.28;
      const moonTex = (U && U.planetTex) ? U.planetTex('moon') : null;
      const moon = new THREE.Mesh(
        new THREE.SphereGeometry(0.58, 24, 18),
        new THREE.MeshStandardMaterial({ map: moonTex, roughness: 0.85, color: moonTex ? 0xffffff : 0xcfd4e0 })
      );
      moon.position.set(3.8, 0.3, 0);
      moonPivot.add(moon);
      earthGroup.add(moonPivot);
      scene.add(earthGroup);

      // 4. Planeta con anillos cósmicos a la derecha y Marte en la lejanía
      const ringedGroup = new THREE.Group();
      ringedGroup.position.set(5.4, 3.1, -17.5);
      const marsTex = (U && U.planetTex) ? U.planetTex('mars') : null;
      const ringedPlanet = new THREE.Mesh(
        new THREE.SphereGeometry(1.75, 28, 20),
        new THREE.MeshStandardMaterial({ map: marsTex, roughness: 0.6, color: 0xe695ff })
      );
      ringedGroup.add(ringedPlanet);
      const pRing = new THREE.Mesh(
        new THREE.RingGeometry(2.25, 3.45, 48),
        new THREE.MeshBasicMaterial({ color: 0xb86bff, side: THREE.DoubleSide, transparent: true, opacity: 0.55 })
      );
      pRing.rotation.x = Math.PI * 0.38;
      pRing.rotation.y = -0.35;
      ringedGroup.add(pRing);
      scene.add(ringedGroup);

      // 5. Estrella fugaz / cometa dinámico
      const cometGeo = new THREE.SphereGeometry(0.08, 8, 8);
      const cometMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
      const comet = new THREE.Mesh(cometGeo, cometMat);
      const trail = new THREE.Mesh(
        new THREE.ConeGeometry(0.06, 1.8, 8),
        new THREE.MeshBasicMaterial({ color: 0x70e8ff, transparent: true, opacity: 0.55 })
      );
      trail.rotation.z = -Math.PI / 2;
      trail.position.x = -0.9;
      comet.add(trail);
      comet.position.set(-14, 5.5, -16);
      scene.add(comet);

      G.cr = {
        scene, cam, yaw: 0.35, zoom: 5.4, anim: 'idle',
        astro: prevAstro, look: prevLook,
        ring, ring2, ring3,
        skyDome, starsWhite, starsCyan, starsPurple,
        earth, moonPivot, ringedPlanet, pRing, comet,
        t: 0, jumpT: 0
      };
      if (prevAstro && prevAstro.group) {
        scene.add(prevAstro.group);
      }
    };

    const origUpdateCreator = G.updateCreator;
    G.updateCreator = function (dt) {
      if (origUpdateCreator) origUpdateCreator.apply(this, arguments);
      const cr = G.cr;
      if (!cr) return;
      // En Android horizontal mantenemos el astronauta centrado en la mitad derecha (sin desplazarlo hacia arriba)
      if (Device.isAndroid && cr.cam && G.renderer) {
        const Wd = window.innerWidth;
        const Hd = window.innerHeight;
        if (cr.zoom > 6.8) cr.zoom = 5.3;
        cr.cam.aspect = Wd / Hd;
        const ox = -Math.min(180, Wd * 0.18);
        cr.cam.setViewOffset(Wd, Hd, ox, 0, Wd, Hd);
        cr.cam.updateProjectionMatrix();
      }
      // Animar el fondo del espacio dinámico en tiempo real
      if (cr.skyDome) cr.skyDome.rotation.y += dt * 0.018;
      if (cr.ring2) cr.ring2.rotation.z -= dt * 0.45;
      if (cr.ring3) cr.ring3.rotation.z += dt * 0.22;
      if (cr.starsWhite) cr.starsWhite.rotation.y += dt * 0.025;
      if (cr.starsCyan) {
        cr.starsCyan.rotation.y -= dt * 0.038;
        cr.starsCyan.position.y = Math.sin(cr.t * 0.9) * 0.25;
      }
      if (cr.starsPurple) {
        cr.starsPurple.rotation.y += dt * 0.05;
      }
      if (cr.earth) cr.earth.rotation.y += dt * 0.22;
      if (cr.moonPivot) cr.moonPivot.rotation.y += dt * 0.55;
      if (cr.ringedPlanet) cr.ringedPlanet.rotation.y -= dt * 0.18;
      if (cr.pRing) cr.pRing.rotation.z += dt * 0.25;
      if (cr.comet) {
        const cycle = (cr.t * 3.8) % 28;
        cr.comet.position.x = -14 + cycle * 1.3;
        cr.comet.position.y = 6.2 - cycle * 0.18;
        cr.comet.visible = cycle < 22;
      }
    };

    // Si Game.cr ya había sido inicializado antes, reconstruir ahora mismo con el fondo espacial dinámico
    if (G.cr) {
      G.buildCreatorScene();
    }
  }
  enhanceCreatorScene();

  if (Sim && Sim.on) {
    Sim.on('emergency:start', (em) => {
      if (!em) return;
      showRobbieSpeech({
        category: 'emergency',
        badge: '🚨 Señal de emergencia',
        title: '«Atención, astronauta: se ha detectado una situación de emergencia.»',
        text: `${em.title}: ${em.symptom || ''} Recomendación: ${em.fix || 'Revisa los módulos críticos inmediatamente.'}`,
        mood: 'emergency',
        duration: 22000
      });
    });

    Sim.on('emergency', (ev) => {
      const msg = (ev && ev.msg) ? ev.msg : 'Un módulo crítico requiere reparación con tu herramienta.';
      showRobbieSpeech({
        category: 'emergency',
        badge: '🚨 Señal de emergencia',
        title: '«Atención, astronauta: se ha detectado una situación de emergencia.»',
        text: `${msg} Recomendación: acércate al módulo con ícono de alerta y repáralo para estabilizar la colonia.`,
        mood: 'emergency',
        duration: 20000
      });
    });

    Sim.on('broken', (b) => {
      const bDef = (b && b.type && D.BUILDINGS && D.BUILDINGS[b.type]) ? D.BUILDINGS[b.type] : null;
      const bName = bDef ? bDef.name : 'un sistema de la base';
      showRobbieSpeech({
        category: 'emergency',
        badge: '⚠️ Advertencia de sistema',
        title: '«Atención, astronauta: se ha detectado una situación de emergencia.»',
        text: `Se averió ${bName}. Recomendación: dirígete al módulo y selecciona «Reparar» antes de que bajen las reservas.`,
        mood: 'emergency',
        duration: 18000
      });
    });

    Sim.on('storm', (st) => {
      if (st && st.on) {
        showRobbieSpeech({
          category: 'emergency',
          badge: '🌪️ Alerta meteorológica',
          title: '«Atención, astronauta: se ha detectado una situación de emergencia.»',
          text: 'Tormenta espacial activa: los paneles solares producen menos energía. Recomendación: revisa tus baterías y resguárdate en el hábitat.',
          mood: 'emergency',
          duration: 18000
        });
      }
    });

    Sim.on('discovery', (d) => {
      const title = (d && d.title) ? d.title : 'Nuevo hallazgo espacial';
      const text = (d && d.text) ? d.text : 'Analiza este hallazgo en tu laboratorio para impulsar la misión.';
      showRobbieSpeech({
        category: 'discovery',
        badge: '✨ ¡Nuevo descubrimiento!',
        title: '«¡Buen trabajo! Has descubierto algo nuevo.»',
        text: `${title}: ${text}`,
        mood: 'discovery',
        duration: 16000
      });
    });

    Sim.on('building:placed', (b) => {
      if (!b || !b.type) return;
      const key = 'b_' + b.type;
      if (seenBuildings.has(key)) return;
      seenBuildings.add(key);
      const custom = DISCOVERY_TEXTS[b.type];
      const bDef = (D.BUILDINGS && D.BUILDINGS[b.type]) ? D.BUILDINGS[b.type] : null;
      const text = custom || (`«¡Buen trabajo! Has descubierto algo nuevo.» Pusiste en marcha ${bDef ? bDef.name : b.type}: ${bDef && bDef.edu ? bDef.edu : 'un sistema clave para la supervivencia espacial.'}`);
      showRobbieSpeech({
        category: 'discovery',
        badge: '🔬 Descubrimiento de sistema',
        title: '«¡Buen trabajo! Has descubierto algo nuevo.»',
        text: text.replace(/^«¡Buen trabajo! Has descubierto algo nuevo\.»\s*/, ''),
        mood: 'discovery',
        duration: 16000
      });
    });

    Sim.on('real:studied', (item) => {
      const name = (item && item.name) ? item.name : 'Tecnología real de la NASA';
      const summary = (item && item.summary) ? item.summary : '';
      showRobbieSpeech({
        category: 'discovery',
        badge: '🛰️ Descubrimiento NASA',
        title: '«¡Buen trabajo! Has descubierto algo nuevo.»',
        text: `${name}: ${summary}`,
        mood: 'discovery',
        duration: 16000
      });
    });
  }

  if (G.completeAction) {
    const origCompleteAction = G.completeAction;
    G.completeAction = function (a) {
      const r = origCompleteAction.apply(this, arguments);
      try {
        if (a && a.id === 'mine' && a.target && a.target.kind) {
          const k = a.target.kind;
          if (!seenDiscoveries.has(k) && DISCOVERY_TEXTS[k]) {
            seenDiscoveries.add(k);
            showRobbieSpeech({
              category: 'discovery',
              badge: '⛏️ Nuevo elemento encontrado',
              title: '«¡Buen trabajo! Has descubierto algo nuevo.»',
              text: DISCOVERY_TEXTS[k].replace(/^«¡Buen trabajo! Has descubierto algo nuevo\.»\s*/, ''),
              mood: 'discovery',
              duration: 16000
            });
          }
        } else if (a && a.id === 'inspect' && a.target && a.target.type) {
          const t = a.target.type;
          const key = 'insp_' + t;
          if (!seenDiscoveries.has(key) && DISCOVERY_TEXTS[t]) {
            seenDiscoveries.add(key);
            showRobbieSpeech({
              category: 'discovery',
              badge: '🔍 Funcionamiento descubierto',
              title: '«¡Buen trabajo! Has descubierto algo nuevo.»',
              text: DISCOVERY_TEXTS[t].replace(/^«¡Buen trabajo! Has descubierto algo nuevo\.»\s*/, ''),
              mood: 'discovery',
              duration: 16000
            });
          }
        }
      } catch (e) {}
      return r;
    };
  }

  let lastCritAlert = 0;
  setInterval(() => {
    if (G.mode !== 'play' || !Sim || !Sim.g || !Sim.g.res) return;
    const now = Date.now();
    if (now - lastCritAlert < 45000) return;
    const res = Sim.g.res;
    if (res.oxygen < 22) {
      lastCritAlert = now;
      showRobbieSpeech({
        category: 'emergency',
        badge: '🚨 Emergencia de oxígeno',
        title: '«Atención, astronauta: se ha detectado una situación de emergencia.»',
        text: `El oxígeno cayó al ${Math.round(res.oxygen)}%. Recomendación: revisa que el Generador de O₂ tenga energía y agua suficiente o construye uno adicional.`,
        mood: 'emergency',
        duration: 18000
      });
    } else if (res.power < 18) {
      lastCritAlert = now;
      showRobbieSpeech({
        category: 'emergency',
        badge: '🚨 Emergencia de energía',
        title: '«Atención, astronauta: se ha detectado una situación de emergencia.»',
        text: `La energía eléctrica está en ${Math.round(res.power)}%. Recomendación: construye o repara Paneles Solares y Baterías para evitar apagones en la base.`,
        mood: 'emergency',
        duration: 18000
      });
    } else if (res.water < 18) {
      lastCritAlert = now;
      showRobbieSpeech({
        category: 'emergency',
        badge: '🚨 Emergencia de agua',
        title: '«Atención, astronauta: se ha detectado una situación de emergencia.»',
        text: `Las reservas de agua bajaron al ${Math.round(res.water)}%. Recomendación: extrae hielo de los cráteres azules o revisa el Extractor de Agua.`,
        mood: 'emergency',
        duration: 18000
      });
    }
  }, 6000);

  /* ==========================================================================
     ETAPA 6: ADAPTAR EL MODAL "CÓMO JUGAR" (M.howTo) SEGÚN EL DISPOSITIVO
     ========================================================================== */
  if (JSM.Menu && JSM.Menu.howTo) {
    JSM.Menu.howTo = function () {
      Device.detect();
      const body = document.createElement('div');
      body.style.display = 'grid';
      body.style.gap = '12px';

      const robbieIntro = document.createElement('div');
      robbieIntro.className = 'card';
      robbieIntro.style.borderColor = 'rgba(184,77,255,.55)';
      robbieIntro.style.background = 'rgba(184,77,255,.08)';
      robbieIntro.innerHTML = `
        <div style="display:flex;gap:12px;align-items:center">
          <div style="width:62px;height:58px;flex:none">${getRobbieSVG('hello')}</div>
          <div>
            <div class="label" style="color:var(--mint)">${Device.getIcon()} DISPOSITIVO DETECTADO: ${Device.getName().toUpperCase()}</div>
            <h3 style="margin:2px 0 4px">«¡Hola, astronauta! Soy Robbie, tu compañero de viaje.»</h3>
            <p style="margin:0;color:#d9fff7">${Device.getSummary()}</p>
          </div>
        </div>
      `;
      body.appendChild(robbieIntro);

      const ctrlCard = document.createElement('div');
      ctrlCard.className = 'card';
      ctrlCard.innerHTML = `<h3>${Device.getIcon()} ${tr('Controles adaptados para tu', 'Controls adapted for your')} ${Device.getName()}</h3>`;
      Device.getControlsList().forEach(([action, control]) => {
        const r = document.createElement('div');
        r.className = 'kv';
        r.innerHTML = `<span>${action}</span><span class="kbd">${control}</span>`;
        ctrlCard.appendChild(r);
      });
      body.appendChild(ctrlCard);

      const guideGrid = document.createElement('div');
      guideGrid.className = 'grid c2';
      const sections = [
        [
          tr('1. Viaje Tierra → Luna', '1. Earth → Moon Journey'),
          tr('Despegarás junto a Robbie dentro de la nave Orión. Guíala a través de los anillos de trayectoria y aluniza suavemente en el Polo Sur Lunar.', 'Launch alongside Robbie inside the Orion spacecraft. Steer through the trajectory rings and land gently on the Lunar South Pole.')
        ],
        [
          tr('2. Soporte vital de la base', '2. Base Life Support'),
          tr('Tu colonia necesita Energía (Paneles Solares y Baterías), Agua (hielo lunar) y Oxígeno (Generador de O₂) además de alimentos del Invernadero.', 'Your colony needs Power (Solar Panels & Batteries), Water (lunar ice) and Oxygen (O₂ Generator) plus food from the Greenhouse.')
        ],
        [
          tr('3. Descubrimientos y Datos Curiosos', '3. Discoveries & Fun Facts'),
          tr('Explora rocas, hielo, regolito y módulos reales de la NASA. Robbie aparecerá abajo a la derecha con sus globos de texto para explicarte cada hallazgo.', 'Explore rocks, ice, regolith and real NASA modules. Robbie will appear at the bottom-right with speech bubbles to explain every discovery.')
        ],
        [
          tr('4. Señales de Emergencia', '4. Emergency Signals'),
          tr('Si ocurre una tormenta solar, avería o baja crítica de recursos, Robbie te avisará en su globo de texto con la recomendación exacta.', 'If a solar storm, breakdown or critical resource drop occurs, Robbie will alert you in his speech bubble with the exact recommendation.')
        ]
      ];
      sections.forEach(([t, p]) => {
        const c = document.createElement('div');
        c.className = 'card';
        c.innerHTML = `<h3>${t}</h3><p>${p}</p>`;
        guideGrid.appendChild(c);
      });
      body.appendChild(guideGrid);

      const closeBtn = document.createElement('button');
      closeBtn.className = 'btn primary';
      closeBtn.textContent = tr('¡Entendido, gracias Robbie!', 'Got it, thanks Robbie!');
      closeBtn.onclick = () => UI.closeModal();
      UI.modal(tr('Cómo jugar · Guía de Robbie', 'How to Play · Robbie Guide'), body, { wide: true, foot: [closeBtn] });
    };
  }

  /* ==========================================================================
     MODAL DE CHAT CON ROBBIE
     ========================================================================== */
  function openRobbieChatModal() {
    const modal = document.getElementById('modal-robi-chat');
    if (!modal) return;
    modal.classList.remove('hidden');

    const box = modal.querySelector('.modal');
    const foot = modal.querySelector('footer');
    if (box && foot && !box.querySelector('.robi-quick-chips')) {
      const chips = document.createElement('div');
      chips.className = 'robi-quick-chips';
      const questions = [
        '¿Cómo juego en mi dispositivo?',
        '¿Cómo produzco agua y oxígeno en la Luna?',
        '¿Qué hago en una emergencia?',
        'Cuéntame un dato curioso de la nave Orión'
      ];
      questions.forEach(q => {
        const b = document.createElement('button');
        b.type = 'button';
        b.className = 'robi-chip';
        b.textContent = q;
        b.addEventListener('click', () => {
          const inp = document.getElementById('robi-chat-input');
          const send = document.getElementById('robi-chat-send');
          if (inp && send) {
            inp.value = q;
            send.click();
          }
        });
        chips.appendChild(b);
      });
      box.insertBefore(chips, foot);
    }
    if (typeof window.renderRobiChatLog === 'function') {
      const logEl = document.getElementById('robi-chat-log');
      if (logEl && !logEl.innerHTML.trim()) window.renderRobiChatLog();
    }
  }
  UI.openRobiChat = openRobbieChatModal;

  function initPropuesta() {
    Device.detect();
    buildMenuRightPanel();
    upgradeFlightCompanionUI();
    const oldTool = document.getElementById('t-robot');
    if (oldTool) oldTool.remove();
    if (G.mode === 'play') ensureCompanionDOM();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => setTimeout(initPropuesta, 120));
  } else {
    setTimeout(initPropuesta, 120);
  }

  console.log('[JSM.Robbie Propuesta] Globos abajo a la derecha + botón superior derecho activos.');
})(window.JSM);
/* === END PROPUESTA ROBBIE INTEGRACION === */
</script>
""".replace("__ROBBIE_SPRITE_URI__", ROBBIE_SPRITE_URI)

assert "</body></html>" in html, "Could not find closing </body></html> tag"
html = html.replace(
    "$('#fl-say').parentNode.classList.remove('show');",
    "if ($('#fl-say') && $('#fl-say').parentNode) $('#fl-say').parentNode.classList.remove('show');"
)
html = html.replace(
    "R.astro = RobbieAstronaut();",
    "R.astro = (R.createModel ? R.createModel() : RobbieAstronaut());"
)
from mp_sync_patch import apply_mp_patch
html = apply_mp_patch(html)
html_out = html.replace("</body></html>", PROPUESTA_SCRIPT + "\n</body></html>")

for path in OUT_FILES:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"Updated: {path} ({len(html_out)} bytes)")

try:
    subprocess.Popen(
        ["xdg-open", VERSIONED_DOWNLOAD_FILE],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    print(f"Opened in browser: {VERSIONED_DOWNLOAD_FILE}")
except Exception as e:
    print(f"Could not open browser automatically: {e}")
