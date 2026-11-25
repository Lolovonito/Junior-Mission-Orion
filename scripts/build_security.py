#!/usr/bin/env python3
"""Empaquetador de seguridad y proteccion anti-ingenieria inversa para Junior Mission Orion (v30.1.0)."""
import base64
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCAL_DIR = ROOT / ".local_src"
MASTER_HTML = LOCAL_DIR / "index.master.html"
LOCAL_V30_JS = LOCAL_DIR / "orion_nasa_kids_v30.js"

PUBLIC_COPIES = [
    ROOT / "index.html",
    ROOT / "public" / "index.html",
    ROOT / "public" / "Junior_Mission_Orion_v29_RobbieAI.html",
    ROOT / "Junior_Mission_Orion_v29_RobbieAI.html",
    ROOT / "Junior_Mission_Orion_Robbie_Final.html",
    ROOT / "MissionOrion.html",
    ROOT / "desktop-rust" / "assets" / "game.html",
]

REGEX_PREV_KEYWORDS = {
    "return", "throw", "case", "default", "delete", "void", "typeof",
    "in", "instanceof", "new", "yield", "await", "else", "do", "of",
}

NO_SPACE_DELIMS = set(";,.(){}[]=?:!&|<>+-*/%~^")


def node_check(js_code: str, label: str = "script") -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as tf:
        tf.write(js_code)
        tmp_path = tf.name
    try:
        res = subprocess.run(["node", "--check", tmp_path], capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Error de sintaxis JS en {label}:\n{res.stderr[:800]}")
    finally:
        os.unlink(tmp_path)


def minify_css(css: str) -> str:
    out = []
    i = 0
    n = len(css)
    quote = None
    while i < n:
        ch = css[i]
        if quote:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(css[i + 1])
                i += 2
                continue
            if ch == quote:
                quote = None
            i += 1
            continue
        if ch in ("'", '"'):
            quote = ch
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n and css[i + 1] == "*":
            end = css.find("*/", i + 2)
            i = n if end == -1 else end + 2
            continue
        if ch in (" ", "\t", "\r", "\n"):
            while i < n and css[i] in (" ", "\t", "\r", "\n"):
                i += 1
            if out and out[-1] not in (" ", "\n", "{", "}", ";", ",", ">", "+"):
                out.append(" ")
            continue
        if ch in ("{", "}", ";", ",") and out and out[-1] == " ":
            out.pop()
        out.append(ch)
        i += 1
    return "".join(out).strip()


def _is_ident_start(ch: str) -> bool:
    return ch.isalpha() or ch in ("_", "$") or ord(ch) > 127


def _is_ident_part(ch: str) -> bool:
    return ch.isalnum() or ch in ("_", "$") or ord(ch) > 127


def minify_js(code: str) -> str:
    """Minificador lexico de JS seguro para ASI, strings, template literals con ${} y regex."""
    out = []
    i = 0
    n = len(code)
    can_regex = True
    # Stack entries: ('tpl',) when inside template text, or ('expr', brace_depth) inside ${...}
    stack = []
    pending_space = False
    pending_newline = False

    def flush_ws(next_ch: str, next_is_word: bool, next_is_num: bool) -> None:
        nonlocal pending_space, pending_newline
        if not out:
            pending_space = False
            pending_newline = False
            return
        prev_tok = out[-1]
        prev = prev_tok[-1]
        if pending_newline:
            if prev != "\n":
                out.append("\n")
            pending_space = False
            pending_newline = False
            return
        if pending_space:
            prev_word = _is_ident_part(prev)
            if (prev_word and (next_is_word or next_is_num)) or (prev == next_ch and prev in "+-/"):
                out.append(" ")
            elif prev == "/" and next_ch == "*":
                out.append(" ")
            elif prev_tok in REGEX_PREV_KEYWORDS and next_ch == "/":
                out.append(" ")
        pending_space = False

    while i < n:
        # Check if inside template literal text
        if stack and stack[-1] == "tpl":
            ch = code[i]
            if ch == "\\":
                out.append(code[i : i + 2])
                i += 2
                continue
            if ch == "$" and i + 1 < n and code[i + 1] == "{":
                out.append("${")
                i += 2
                stack.append(["expr", 1])
                can_regex = True
                pending_space = False
                pending_newline = False
                continue
            if ch == "`":
                out.append("`")
                i += 1
                stack.pop()
                can_regex = False
                continue
            out.append(ch)
            i += 1
            continue

        ch = code[i]

        # Whitespace
        if ch in (" ", "\t", "\r", "\n"):
            if ch == "\n":
                pending_newline = True
            else:
                pending_space = True
            i += 1
            continue

        # Comments
        if ch == "/" and i + 1 < n:
            nxt = code[i + 1]
            if nxt == "/":
                nl = code.find("\n", i + 2)
                if nl == -1:
                    i = n
                else:
                    pending_newline = True
                    i = nl + 1
                continue
            if nxt == "*":
                end = code.find("*/", i + 2)
                if end == -1:
                    i = n
                else:
                    if "\n" in code[i + 2 : end]:
                        pending_newline = True
                    else:
                        pending_space = True
                    i = end + 2
                continue

        # String literal
        if ch in ("'", '"'):
            flush_ws(ch, False, False)
            q = ch
            start = i
            i += 1
            while i < n:
                c = code[i]
                if c == "\\":
                    i += 2
                    continue
                if c == q:
                    i += 1
                    break
                i += 1
            out.append(code[start:i])
            can_regex = False
            continue

        # Template literal start
        if ch == "`":
            flush_ws(ch, False, False)
            out.append("`")
            i += 1
            stack.append("tpl")
            continue

        # Regex literal vs division
        if ch == "/" and can_regex:
            flush_ws(ch, False, False)
            start = i
            i += 1
            in_class = False
            while i < n:
                c = code[i]
                if c == "\\":
                    i += 2
                    continue
                if c == "[" and not in_class:
                    in_class = True
                    i += 1
                    continue
                if c == "]" and in_class:
                    in_class = False
                    i += 1
                    continue
                if c == "/" and not in_class:
                    i += 1
                    break
                i += 1
            while i < n and code[i].isalpha():
                i += 1
            out.append(code[start:i])
            can_regex = False
            continue

        # Identifier / Keyword
        if _is_ident_start(ch):
            flush_ws(ch, True, False)
            start = i
            i += 1
            while i < n and _is_ident_part(code[i]):
                i += 1
            word = code[start:i]
            out.append(word)
            can_regex = word in REGEX_PREV_KEYWORDS
            continue

        # Number literal
        if ch.isdigit() or (ch == "." and i + 1 < n and code[i + 1].isdigit()):
            flush_ws(ch, False, True)
            start = i
            if ch == "0" and i + 1 < n and code[i + 1] in ("x", "X", "b", "B", "o", "O"):
                i += 2
                while i < n and (code[i].isalnum() or code[i] == "_"):
                    i += 1
            else:
                while i < n and (code[i].isdigit() or code[i] in (".", "_")):
                    i += 1
                if i < n and code[i] in ("e", "E"):
                    i += 1
                    if i < n and code[i] in ("+", "-"):
                        i += 1
                    while i < n and (code[i].isdigit() or code[i] == "_"):
                        i += 1
                if i < n and code[i] == "n":
                    i += 1
            out.append(code[start:i])
            can_regex = False
            continue

        # Operators and punctuation
        flush_ws(ch, False, False)
        if stack and isinstance(stack[-1], list) and stack[-1][0] == "expr":
            if ch == "{":
                stack[-1][1] += 1
            elif ch == "}":
                stack[-1][1] -= 1
                if stack[-1][1] == 0:
                    stack.pop()
                    out.append("}")
                    i += 1
                    continue

        if i + 1 < n and code[i : i + 2] in ("++", "--"):
            out.append(code[i : i + 2])
            i += 2
            can_regex = False
            continue

        if i + 1 < n and code[i : i + 2] == "=>":
            out.append("=>")
            i += 2
            can_regex = True
            continue

        out.append(ch)
        i += 1
        can_regex = ch not in (")", "]")

    res = "".join(out).strip()
    # Collapse leading spaces after newlines that came from blank lines
    res = re.sub(r"\n+", "\n", res)
    return res


def obfuscate_js_strings(code: str, seed_bytes: bytes, max_len: int = 2048, wrap_iife: bool = True) -> str:
    """Codifica literales de cadena de un script usando tabla XOR indexada."""
    literals = []
    out = []
    i = 0
    n = len(code)
    k = seed_bytes

    def enc_str(s: str) -> int:
        raw = s.encode("utf-8")
        idx = len(literals)
        b_enc = [(b ^ k[(idx + j) % len(k)] ^ ((idx * 17 + j * 31 + 73) & 0xFF)) for j, b in enumerate(raw)]
        literals.append(b_enc)
        return idx

    can_regex = True
    stack = []
    while i < n:
        if stack and stack[-1] == "tpl":
            ch = code[i]
            if ch == "\\":
                out.append(code[i : i + 2])
                i += 2
                continue
            if ch == "$" and i + 1 < n and code[i + 1] == "{":
                out.append("${")
                i += 2
                stack.append(["expr", 1])
                can_regex = True
                continue
            if ch == "`":
                out.append("`")
                i += 1
                stack.pop()
                can_regex = False
                continue
            out.append(ch)
            i += 1
            continue

        ch = code[i]
        if ch in ("'", '"'):
            q = ch
            j = i + 1
            buf = []
            ok_plain = True
            while j < n:
                c = code[j]
                if c == "\\":
                    if j + 1 >= n:
                        ok_plain = False
                        break
                    esc = code[j + 1]
                    if esc == "n":
                        buf.append("\n")
                    elif esc == "r":
                        buf.append("\r")
                    elif esc == "t":
                        buf.append("\t")
                    elif esc == "0" and (j + 2 >= n or not code[j + 2].isdigit()):
                        buf.append("\0")
                    elif esc in ("'", '"', "\\", "/"):
                        buf.append(esc)
                    else:
                        ok_plain = False
                        break
                    j += 2
                    continue
                if c == q:
                    j += 1
                    break
                buf.append(c)
                j += 1
            raw_token = code[i:j]
            val = "".join(buf)
            rest = code[j : j + 4].lstrip()
            prev_tail = "".join(out[-12:]).rstrip()
            is_prop_key = rest.startswith(":") and (not prev_tail or prev_tail[-1] in "{,")
            is_case = prev_tail.endswith("case")
            is_directive = val == "use strict"
            if ok_plain and 3 <= len(val) <= max_len and not is_prop_key and not is_case and not is_directive:
                idx = enc_str(val)
                out.append(f"_$({idx})")
                i = j
                can_regex = False
                continue
            else:
                out.append(raw_token)
                i = j
                can_regex = False
                continue

        if ch == "`":
            out.append("`")
            i += 1
            stack.append("tpl")
            continue

        if ch == "/" and can_regex:
            start = i
            i += 1
            in_class = False
            while i < n:
                c = code[i]
                if c == "\\":
                    i += 2
                    continue
                if c == "[" and not in_class:
                    in_class = True
                    i += 1
                    continue
                if c == "]" and in_class:
                    in_class = False
                    i += 1
                    continue
                if c == "/" and not in_class:
                    i += 1
                    break
                i += 1
            while i < n and code[i].isalpha():
                i += 1
            out.append(code[start:i])
            can_regex = False
            continue

        if _is_ident_start(ch):
            start = i
            i += 1
            while i < n and _is_ident_part(code[i]):
                i += 1
            w = code[start:i]
            out.append(w)
            can_regex = w in REGEX_PREV_KEYWORDS
            continue

        if ch.isdigit():
            start = i
            i += 1
            while i < n and (code[i].isalnum() or code[i] in "._"):
                i += 1
            out.append(code[start:i])
            can_regex = False
            continue

        if stack and isinstance(stack[-1], list) and stack[-1][0] == "expr":
            if ch == "{":
                stack[-1][1] += 1
            elif ch == "}":
                stack[-1][1] -= 1
                if stack[-1][1] == 0:
                    stack.pop()
                    out.append("}")
                    i += 1
                    continue

        if i + 1 < n and code[i : i + 2] in ("++", "--"):
            out.append(code[i : i + 2])
            i += 2
            can_regex = False
            continue

        out.append(ch)
        i += 1
        can_regex = ch not in (")", "]")

    key_arr = "[" + ",".join(str(b) for b in k) + "]"
    tbl = "[" + ",".join("[" + ",".join(str(x) for x in arr) + "]" for arr in literals) + "]"
    decoder = (
        f"const _$=((t,k)=>{{const d=new TextDecoder(),c=[];"
        f"return i=>{{if(c[i]!==undefined)return c[i];const a=t[i],u=new Uint8Array(a.length);"
        f"for(let j=0;j<a.length;j++)u[j]=a[j]^k[(i+j)%k.length]^((i*17+j*31+73)&255);"
        f"return(c[i]=d.decode(u));}};}})({tbl},{key_arr});"
    )
    body = decoder + "".join(out)
    return ("(()=>{" + body + "})();") if wrap_iife else body


def _rotl32(x: int, n: int) -> int:
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF


def _qr(s: list, a: int, b: int, c: int, d: int) -> None:
    s[a] = (s[a] + s[b]) & 0xFFFFFFFF; s[d] = _rotl32(s[d] ^ s[a], 16)
    s[c] = (s[c] + s[d]) & 0xFFFFFFFF; s[b] = _rotl32(s[b] ^ s[c], 12)
    s[a] = (s[a] + s[b]) & 0xFFFFFFFF; s[d] = _rotl32(s[d] ^ s[a], 8)
    s[c] = (s[c] + s[d]) & 0xFFFFFFFF; s[b] = _rotl32(s[b] ^ s[c], 7)


def chacha20_block(key: bytes, counter: int, nonce: bytes) -> bytes:
    st = list(struct.unpack("<4I", b"expand 32-byte k"))
    st.extend(struct.unpack("<8I", key))
    st.append(counter & 0xFFFFFFFF)
    st.extend(struct.unpack("<3I", nonce))
    w = list(st)
    for _ in range(10):
        _qr(w, 0, 4, 8, 12); _qr(w, 1, 5, 9, 13); _qr(w, 2, 6, 10, 14); _qr(w, 3, 7, 11, 15)
        _qr(w, 0, 5, 10, 15); _qr(w, 1, 6, 11, 12); _qr(w, 2, 7, 8, 13); _qr(w, 3, 4, 9, 14)
    return struct.pack("<16I", *((w[i] + st[i]) & 0xFFFFFFFF for i in range(16)))


def chacha20_xor(key: bytes, nonce: bytes, data: bytes, start_counter: int = 1) -> bytes:
    out = bytearray(len(data))
    ctr = start_counter
    for off in range(0, len(data), 64):
        blk = chacha20_block(key, ctr, nonce)
        ctr += 1
        chunk = data[off : off + 64]
        for j, b in enumerate(chunk):
            out[off + j] = b ^ blk[j]
    return bytes(out)


def fnv1a_32_keyed(data: bytes, seed_words: tuple) -> int:
    h = (0x811C9DC5 ^ seed_words[0] ^ seed_words[1]) & 0xFFFFFFFF
    for b in data:
        h = ((h ^ b) * 0x01000193) & 0xFFFFFFFF
    h ^= (h >> 16)
    h = (h * (0x85EBCA6B | 1)) & 0xFFFFFFFF
    h ^= (h >> 13)
    return h


def build_bootstrapper_and_shield(scripts_min: list) -> str:
    payload_raw = json.dumps(scripts_min, ensure_ascii=False).encode("utf-8")
    comp = zlib.compressobj(level=9, wbits=-15)
    compressed = comp.compress(payload_raw) + comp.flush()

    key = os.urandom(32)
    nonce = os.urandom(12)
    mac_seed = struct.unpack("<2I", chacha20_block(key, 0, nonce)[:8])
    tag_plain = fnv1a_32_keyed(compressed, mac_seed)
    cipher = chacha20_xor(key, nonce, compressed, start_counter=1)
    b64 = base64.b64encode(cipher).decode("ascii")

    # Split 32-byte key into 4 shards with XOR + bit-rotation
    k_shards = [[], [], [], []]
    for i, byte in enumerate(key):
        s0 = os.urandom(1)[0]
        s1 = os.urandom(1)[0]
        s2 = os.urandom(1)[0]
        rot = (i % 5) + 1
        target = ((byte << rot) | (byte >> (8 - rot))) & 0xFF
        s3 = target ^ s0 ^ s1 ^ s2 ^ ((i * 53 + 19) & 0xFF)
        k_shards[0].append(s0)
        k_shards[1].append(s1)
        k_shards[2].append(s2)
        k_shards[3].append(s3)

    # Storage MAC key (separate 16-byte seed split into 2 shards)
    mac_key = os.urandom(16)
    ms_a = list(os.urandom(16))
    ms_b = [mac_key[i] ^ ms_a[i] ^ ((i * 29 + 7) & 0xFF) for i in range(16)]

    # Split b64 into ~48KB chunks inside array so there is no giant single literal
    chunk_sz = 49152
    chunks = [b64[i : i + chunk_sz] for i in range(0, len(b64), chunk_sz)]

    nonce_arr = list(nonce)
    raw_js = r"""
((_w, _d) => {
  'use strict';
  const _cs = _d.currentScript;
  const _nChk = (fn) => {
    try { return Function.prototype.toString.call(fn).indexOf('[native code]') !== -1; } catch (_) { return false; }
  };
  if (!_nChk(Function.prototype.toString) || !_nChk(_d.createElement) || !_nChk(Node.prototype.appendChild)) {
    throw new Error('SEC_HOOK');
  }

  /* 1) Escudo temprano: consola neutralizada, clic derecho, arrastrar y atajos */
  try {
    const _noop = Object.freeze(() => {});
    ['log', 'info', 'debug', 'dir', 'table'].forEach((m) => {
      try { if (_w.console) _w.console[m] = _noop; } catch (_) {}
    });
  } catch (_) {}

  const _isEditable = (t) => !!(t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable));
  _d.addEventListener('contextmenu', (e) => {
    if (!_isEditable(e.target)) { e.preventDefault(); e.stopPropagation(); }
  }, true);
  _d.addEventListener('dragstart', (e) => { e.preventDefault(); }, true);
  _d.addEventListener('keydown', (e) => {
    const k = String(e.key || '').toUpperCase();
    const kc = e.keyCode || 0;
    const mod = !!(e.ctrlKey || e.metaKey);
    if (k === 'F12' || kc === 123) { e.preventDefault(); e.stopPropagation(); return; }
    if (mod && e.shiftKey && ('IJCKEX'.indexOf(k) >= 0 || kc === 73 || kc === 74 || kc === 67 || kc === 75 || kc === 69)) {
      e.preventDefault(); e.stopPropagation(); return;
    }
    if (mod && !e.shiftKey && !e.altKey && ('USP'.indexOf(k) >= 0 || kc === 85 || kc === 83 || kc === 80)) {
      e.preventDefault(); e.stopPropagation();
    }
  }, true);

  /* 2) ChaCha20 + MAC + InflateRaw (RFC 1951) */
  const _rl = (v, n) => ((v << n) | (v >>> (32 - n))) >>> 0;
  const _qr = (s, a, b, c, d) => {
    s[a] = (s[a] + s[b]) >>> 0; s[d] = _rl(s[d] ^ s[a], 16);
    s[c] = (s[c] + s[d]) >>> 0; s[b] = _rl(s[b] ^ s[c], 12);
    s[a] = (s[a] + s[b]) >>> 0; s[d] = _rl(s[d] ^ s[a], 8);
    s[c] = (s[c] + s[d]) >>> 0; s[b] = _rl(s[b] ^ s[c], 7);
  };
  const _ccBlk = (k32, ctr, n32, out32) => {
    const st = [0x61707865, 0x3320646e, 0x79622d32, 0x6b206574,
      k32[0], k32[1], k32[2], k32[3], k32[4], k32[5], k32[6], k32[7],
      ctr >>> 0, n32[0], n32[1], n32[2]];
    for (let i = 0; i < 16; i++) out32[i] = st[i];
    for (let i = 0; i < 10; i++) {
      _qr(out32, 0, 4, 8, 12); _qr(out32, 1, 5, 9, 13); _qr(out32, 2, 6, 10, 14); _qr(out32, 3, 7, 11, 15);
      _qr(out32, 0, 5, 10, 15); _qr(out32, 1, 6, 11, 12); _qr(out32, 2, 7, 8, 13); _qr(out32, 3, 4, 9, 14);
    }
    for (let i = 0; i < 16; i++) out32[i] = (out32[i] + st[i]) >>> 0;
  };
  const _u8to32 = (u) => {
    const a = new Uint32Array(u.length >> 2);
    for (let i = 0; i < a.length; i++) {
      const j = i << 2;
      a[i] = (u[j] | (u[j + 1] << 8) | (u[j + 2] << 16) | (u[j + 3] << 24)) >>> 0;
    }
    return a;
  };
  const _inflate = (src) => {
    let bp = 0;
    const rb = (n) => {
      let v = 0;
      for (let i = 0; i < n; i++) {
        const idx = bp >> 3;
        v |= ((src[idx] >> (bp & 7)) & 1) << i;
        bp++;
      }
      return v;
    };
    const mkH = (lens) => {
      let maxB = 0;
      for (let i = 0; i < lens.length; i++) if (lens[i] > maxB) maxB = lens[i];
      if (!maxB) return { m: new Int32Array(0), b: 0 };
      const cnt = new Int32Array(maxB + 1);
      for (let i = 0; i < lens.length; i++) if (lens[i]) cnt[lens[i]]++;
      const nxt = new Int32Array(maxB + 1);
      let code = 0;
      for (let b = 1; b <= maxB; b++) { code = (code + cnt[b - 1]) << 1; nxt[b] = code; }
      const tbl = new Int32Array(1 << maxB);
      tbl.fill(-1);
      for (let s = 0; s < lens.length; s++) {
        const l = lens[s];
        if (!l) continue;
        const c = nxt[l]++;
        let rc = 0;
        for (let k = 0; k < l; k++) rc = (rc << 1) | ((c >> k) & 1);
        const step = 1 << l;
        const val = (s << 5) | l;
        for (let p = rc; p < tbl.length; p += step) tbl[p] = val;
      }
      return { m: tbl, b: maxB };
    };
    const dec = (h) => {
      let idx = 0;
      for (let i = 0; i < h.b; i++) {
        const bit = ((bp + i) >> 3) < src.length ? ((src[(bp + i) >> 3] >> ((bp + i) & 7)) & 1) : 0;
        idx |= bit << i;
      }
      const v = h.m[idx];
      bp += (v & 31);
      return v >> 5;
    };
    const fixLit = (() => {
      const l = new Uint8Array(288);
      for (let i = 0; i < 144; i++) l[i] = 8;
      for (let i = 144; i < 256; i++) l[i] = 9;
      for (let i = 256; i < 280; i++) l[i] = 7;
      for (let i = 280; i < 288; i++) l[i] = 8;
      return mkH(l);
    })();
    const fixDist = (() => { const d = new Uint8Array(32); d.fill(5); return mkH(d); })();
    const clOrd = [16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15];
    const lBase = [3,4,5,6,7,8,9,10,11,13,15,17,19,23,27,31,35,43,51,59,67,83,99,115,131,163,195,227,258];
    const lExt = [0,0,0,0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,4,5,5,5,5,0];
    const dBase = [1,2,3,4,5,7,9,13,17,25,33,49,65,97,129,193,257,385,513,769,1025,1537,2049,3073,4097,6145,8193,12289,16385,24577];
    const dExt = [0,0,0,0,1,1,2,2,3,3,4,4,5,5,6,6,7,7,8,8,9,9,10,10,11,11,12,12,13,13];
    let out = new Uint8Array(src.length * 4), op = 0;
    const ensure = (need) => {
      if (op + need <= out.length) return;
      const nb = new Uint8Array(Math.max(out.length * 2, op + need + 4096));
      nb.set(out.subarray(0, op));
      out.fill(0);
      out = nb;
    };
    let bfinal = 0;
    while (!bfinal) {
      bfinal = rb(1);
      const btype = rb(2);
      if (btype === 0) {
        bp = (bp + 7) & ~7;
        const idx = bp >> 3;
        const len = src[idx] | (src[idx + 1] << 8);
        bp += 32;
        ensure(len);
        const s0 = bp >> 3;
        out.set(src.subarray(s0, s0 + len), op);
        op += len;
        bp += len * 8;
      } else {
        let lh, dh;
        if (btype === 1) { lh = fixLit; dh = fixDist; }
        else if (btype === 2) {
          const hlit = rb(5) + 257, hdist = rb(5) + 1, hclen = rb(4) + 4;
          const cl = new Uint8Array(19);
          for (let i = 0; i < hclen; i++) cl[clOrd[i]] = rb(3);
          const ch = mkH(cl);
          const lens = new Uint8Array(hlit + hdist);
          let p = 0;
          while (p < lens.length) {
            const s = dec(ch);
            if (s < 16) lens[p++] = s;
            else {
              let rep = 0, val = 0;
              if (s === 16) { rep = 3 + rb(2); val = lens[p - 1]; }
              else if (s === 17) rep = 3 + rb(3);
              else rep = 11 + rb(7);
              while (rep--) lens[p++] = val;
            }
          }
          lh = mkH(lens.subarray(0, hlit));
          dh = mkH(lens.subarray(hlit));
        } else throw new Error('SEC_INF');
        for (;;) {
          const sym = dec(lh);
          if (sym < 256) { ensure(1); out[op++] = sym; }
          else if (sym === 256) break;
          else {
            const li = sym - 257;
            const len = lBase[li] + rb(lExt[li]);
            const di = dec(dh);
            const dist = dBase[di] + rb(dExt[di]);
            ensure(len);
            for (let k = 0; k < len; k++) { out[op] = out[op - dist]; op++; }
          }
        }
      }
    }
    return out.subarray(0, op);
  };

  /* 3) Descifrado y ejecucion sincrona de la boveda */
  const _s0 = __S0__, _s1 = __S1__, _s2 = __S2__, _s3 = __S3__;
  const _nn = new Uint8Array(__NONCE__);
  const _key = new Uint8Array(32);
  for (let i = 0; i < 32; i++) {
    const x = _s0[i] ^ _s1[i] ^ _s2[i] ^ _s3[i] ^ ((i * 53 + 19) & 255);
    const r = (i % 5) + 1;
    _key[i] = ((x >>> r) | (x << (8 - r))) & 255;
  }
  const _k32 = _u8to32(_key), _n32 = _u8to32(_nn), _b32 = new Uint32Array(16);
  _ccBlk(_k32, 0, _n32, _b32);
  const _mSeed0 = _b32[0], _mSeed1 = _b32[1];

  const _b64Str = __CHUNKS__.join('');
  const _binStr = atob(_b64Str);
  const _buf = new Uint8Array(_binStr.length);
  for (let i = 0; i < _binStr.length; i++) _buf[i] = _binStr.charCodeAt(i);
  const _ks = new Uint8Array(_b32.buffer);
  let _ctr = 1;
  for (let off = 0; off < _buf.length; off += 64) {
    _ccBlk(_k32, _ctr++, _n32, _b32);
    const lim = Math.min(64, _buf.length - off);
    for (let j = 0; j < lim; j++) _buf[off + j] ^= _ks[j];
  }

  let _h = (0x811C9DC5 ^ _mSeed0 ^ _mSeed1) >>> 0;
  for (let i = 0; i < _buf.length; i++) _h = Math.imul(_h ^ _buf[i], 0x01000193) >>> 0;
  _h = (_h ^ (_h >>> 16)) >>> 0;
  _h = Math.imul(_h, 0x85EBCA6B | 1) >>> 0;
  _h = (_h ^ (_h >>> 13)) >>> 0;
  if (_h !== __TAG__) { _key.fill(0); _k32.fill(0); _buf.fill(0); throw new Error('SEC_MAC'); }

  const _plain = _inflate(_buf);
  _buf.fill(0); _key.fill(0); _k32.fill(0); _n32.fill(0); _b32.fill(0); _nn.fill(0);
  const _json = new TextDecoder().decode(_plain);
  _plain.fill(0);
  const _arr = JSON.parse(_json);

  const _head = _d.head || _d.documentElement;
  for (let i = 0; i < _arr.length; i++) {
    const _sc = _d.createElement('script');
    _sc.text = _arr[i];
    _head.appendChild(_sc);
    _sc.remove();
    _arr[i] = '';
  }
  _arr.length = 0;

  /* 4) Sello de integridad MAC para partidas guardadas en localStorage */
  const _ma = __MA__, _mb = __MB__;
  const _mk = new Uint8Array(16);
  for (let i = 0; i < 16; i++) _mk[i] = _ma[i] ^ _mb[i] ^ ((i * 29 + 7) & 255);
  const _mac64 = (txt) => {
    const bytes = new TextEncoder().encode(txt);
    let h1 = 0x811C9DC5, h2 = 0x9E3779B9;
    for (let i = 0; i < bytes.length; i++) {
      const k = _mk[i & 15];
      h1 = Math.imul(h1 ^ bytes[i] ^ k, 0x01000193) >>> 0;
      h2 = Math.imul(h2 ^ (bytes[i] + k), 0x85EBCA6B) >>> 0;
      h1 = ((h1 << 7) | (h1 >>> 25)) >>> 0;
      h2 = ((h2 << 11) | (h2 >>> 21)) >>> 0;
    }
    h1 = Math.imul(h1 ^ (h1 >>> 15), 0x2C1B3C6D) >>> 0;
    h2 = Math.imul(h2 ^ (h2 >>> 13), 0x297A2D39) >>> 0;
    return h1.toString(16).padStart(8, '0') + h2.toString(16).padStart(8, '0');
  };

  if (_w.JSM && _w.JSM.Store) {
    const _st = _w.JSM.Store;
    const _oGet = _st.get.bind(_st), _oSet = _st.set.bind(_st), _oDel = _st.del.bind(_st);
    const _isSaveKey = (k) => /^jsm_save/.test(String(k || ''));
    const _sealMark = (k) => '__jmo_sm_' + k;
    _st.set = (k, v) => {
      if (!_isSaveKey(k)) return _oSet(k, v);
      try {
        const d = JSON.stringify(v);
        const m = _mac64(k + '\0' + d);
        localStorage.setItem(k, JSON.stringify({ __jmo_v: 1, m, d }));
        localStorage.setItem(_sealMark(k), '1');
        return true;
      } catch (_) { return false; }
    };
    _st.get = (k) => {
      if (!_isSaveKey(k)) return _oGet(k);
      try {
        const raw = localStorage.getItem(k);
        if (!raw) return null;
        const p = JSON.parse(raw);
        if (p && p.__jmo_v === 1 && typeof p.m === 'string' && typeof p.d === 'string') {
          if (_mac64(k + '\0' + p.d) !== p.m) return null;
          return JSON.parse(p.d);
        }
        if (localStorage.getItem(_sealMark(k)) === '1') return null;
        _st.set(k, p);
        return p;
      } catch (_) { return null; }
    };
    _st.del = (k) => {
      try { if (_isSaveKey(k)) localStorage.removeItem(_sealMark(k)); } catch (_) {}
      return _oDel(k);
    };
    try {
      Object.defineProperty(_w.JSM, 'Security', {
        value: Object.freeze({
          version: '30.1.0',
          active: true,
          verifySaveKey: (k) => {
            if (!_isSaveKey(k)) return true;
            try {
              const raw = localStorage.getItem(k);
              if (!raw) return false;
              const p = JSON.parse(raw);
              return !!(p && p.__jmo_v === 1 && typeof p.m === 'string' && typeof p.d === 'string' && _mac64(k + '\0' + p.d) === p.m);
            } catch (_) { return false; }
          }
        }),
        writable: false, enumerable: true, configurable: false
      });
    } catch (_) {}
  }

  /* 5) Detector calibrado de DevTools acoplado (solo escritorio con puntero fino) */
  try {
    const _fine = _w.matchMedia && _w.matchMedia('(hover: hover) and (pointer: fine)').matches;
    if (_fine) {
      let _stk = 0, _ov = null, _wasPaused = false;
      const _toggleLock = (on) => {
        if (on) {
          if (!_ov) {
            _ov = _d.createElement('div');
            _ov.id = 'jmo-sec-lock';
            _ov.style.cssText = 'position:fixed;inset:0;z-index:2147483647;background:rgba(4,7,18,.97);color:#eef2ff;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;font-family:system-ui,sans-serif;padding:24px;gap:10px;';
            _ov.innerHTML = '<div style="font-size:34px">🔒</div><strong style="font-size:18px">Escudo de seguridad activo</strong><span style="max-width:440px;opacity:.82;font-size:14px">Cierra las herramientas de desarrollo para continuar la misión.</span>';
            _d.body && _d.body.appendChild(_ov);
          }
          if (_w.JSM && _w.JSM.Game && _w.JSM.Game.mode === 'play' && !_w.JSM.Game.paused) {
            _wasPaused = true;
            _w.JSM.Game.paused = true;
          }
        } else if (_ov) {
          _ov.remove();
          _ov = null;
          if (_wasPaused && _w.JSM && _w.JSM.Game) { _w.JSM.Game.paused = false; _wasPaused = false; }
        }
      };
      setInterval(() => {
        if (_d.fullscreenElement || _d.webkitFullscreenElement) { _stk = 0; _toggleLock(false); return; }
        if (!_w.outerWidth || !_w.outerHeight) { _stk = 0; return; }
        const dw = _w.outerWidth - _w.innerWidth, dh = _w.outerHeight - _w.innerHeight;
        if (dw > 240 || dh > 240) { if (++_stk >= 2) _toggleLock(true); }
        else { _stk = 0; _toggleLock(false); }
      }, 1500);
    }
  } catch (_) {}

  try { _cs && _cs.remove(); } catch (_) {}
})(window, document);
"""
    js_populated = (
        raw_js.replace("__S0__", json.dumps(k_shards[0]))
        .replace("__S1__", json.dumps(k_shards[1]))
        .replace("__S2__", json.dumps(k_shards[2]))
        .replace("__S3__", json.dumps(k_shards[3]))
        .replace("__NONCE__", json.dumps(nonce_arr))
        .replace("__CHUNKS__", json.dumps(chunks))
        .replace("__TAG__", str(tag_plain))
        .replace("__MA__", json.dumps(ms_a))
        .replace("__MB__", json.dumps(ms_b))
    )

    minified = minify_js(js_populated)
    obfuscated = obfuscate_js_strings(minified, os.urandom(16), max_len=512, wrap_iife=True)
    # Mangle internal shield identifier prefixes
    mangle_names = [
        "_nChk", "_noop", "_isEditable", "_rl", "_qr", "_ccBlk", "_u8to32",
        "_inflate", "_mSeed0", "_mSeed1", "_b64Str", "_binStr", "_inflate",
        "_mac64", "_oGet", "_oSet", "_oDel", "_isSaveKey", "_sealMark",
        "_fine", "_toggleLock", "_wasPaused"
    ]
    used = set()
    for idx_m, orig_name in enumerate(dict.fromkeys(mangle_names)):
        new_name = f"_q{idx_m:x}"
        while new_name in used:
            new_name += "x"
        used.add(new_name)
        obfuscated = re.sub(rf"\b{orig_name}\b", new_name, obfuscated)

    node_check(obfuscated, "bootstrapper")
    return obfuscated, compressed, scripts_min


def verify_bootstrapper_in_node(bootstrap_js: str, expected_scripts: list) -> None:
    harness = r"""
const fs = require('fs');
const code = fs.readFileSync(process.argv[1], 'utf8');
const emitted = [];
let removedCurrent = false;
const currentScript = { remove() { removedCurrent = true; } };
const head = {
  appendChild(el) { emitted.push(el.text); }
};
const document = {
  currentScript,
  head,
  documentElement: head,
  createElement(tag) { return { tagName: tag.toUpperCase(), text: '', remove() {} }; },
  addEventListener() {},
  body: { appendChild() {} },
};
const window = { document, console, localStorage: { getItem(){return null;}, setItem(){}, removeItem(){} }, matchMedia(){ return { matches: false }; } };
Object.defineProperty(Node, 'prototype', { value: { appendChild() {} }, configurable: true });
// Note: bootstrapper checks native functions on document.createElement & Node.prototype.appendChild, so only run inflate/crypto path via VM if native checks skipped, OR run full check with native Node functions? Wait: in Node, document.createElement is JS so _nChk would see JS! Let's run a targeted verification or test under Chromium!
"""
    # Use Chromium in verify_v30 + verify_security, and test inflate/chacha parity directly in node!
    pass


def test_crypto_inflate_parity(bootstrap_js: str, expected_scripts: list) -> None:
    """Ejecuta el bloque de descifrado + inflateRaw de bootstrap_js en Node para verificar coincidencia byte a byte."""
    patched = bootstrap_js.replace("throw new Error(_$(1));", "void 0;", 1)
    assert patched != bootstrap_js, "No se pudo aislar el check DOM nativo en el test Node"
    test_script = """
const emitted = [];
let currentRemoved = false;
const fakeStore = new Map();
global.localStorage = {
  getItem: k => fakeStore.has(k) ? fakeStore.get(k) : null,
  setItem: (k, v) => fakeStore.set(String(k), String(v)),
  removeItem: k => fakeStore.delete(String(k)),
};
global.Node = { prototype: { appendChild() {} } };
global.document = {
  currentScript: { remove() { currentRemoved = true; } },
  head: { appendChild(el) { emitted.push(el.text); } },
  documentElement: {},
  createElement(t) { return { text: '', remove() {} }; },
  addEventListener() {},
  body: { appendChild() {} },
};
global.window = {
  document: global.document,
  console: global.console,
  localStorage: global.localStorage,
  matchMedia: () => ({ matches: false }),
};
""" + patched + """
process.stdout.write(JSON.stringify({ count: emitted.length, removed: currentRemoved, scripts: emitted }));
"""
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as tf:
        tf.write(test_script)
        tmp_path = tf.name
    try:
        res = subprocess.run(["node", tmp_path], capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Node parity failed:\n{res.stderr}\n{res.stdout}")
        parsed = json.loads(res.stdout)
        assert parsed["removed"] is True, "document.currentScript.remove() no fue invocado"
        assert parsed["count"] == len(expected_scripts), f"Esperados {len(expected_scripts)} scripts, recibidos {parsed['count']}"
        for idx, (got, exp) in enumerate(zip(parsed["scripts"], expected_scripts)):
            assert got == exp, f"Discrepancia en script [{idx}] tras descifrar e inflar!"
        print(f"OK: paridad byte-a-byte verificada en Node ({len(expected_scripts)} scripts reconstruidos)")
    finally:
        os.unlink(tmp_path)


def build_landing_shield() -> str:
    js = r"""
(() => {
  try {
    const _noop = Object.freeze(() => {});
    ['log', 'info', 'debug', 'dir', 'table'].forEach((m) => { try { console[m] = _noop; } catch (_) {} });
  } catch (_) {}
  const _ed = (t) => !!(t && (t.tagName === 'INPUT' || t.tagName === 'TEXTAREA' || t.isContentEditable));
  document.addEventListener('contextmenu', (e) => { if (!_ed(e.target)) { e.preventDefault(); e.stopPropagation(); } }, true);
  document.addEventListener('dragstart', (e) => { e.preventDefault(); }, true);
  document.addEventListener('keydown', (e) => {
    const k = String(e.key || '').toUpperCase(), kc = e.keyCode || 0, mod = !!(e.ctrlKey || e.metaKey);
    if (k === 'F12' || kc === 123 || (mod && e.shiftKey && 'IJCK'.indexOf(k) >= 0) || (mod && !e.shiftKey && !e.altKey && 'USP'.indexOf(k) >= 0)) {
      e.preventDefault(); e.stopPropagation();
    }
  }, true);
})();
"""
    return minify_js(js)


def main() -> int:
    if not MASTER_HTML.exists():
        print(f"ERROR: Falta {MASTER_HTML}", file=sys.stderr)
        return 1

    html = MASTER_HTML.read_text(encoding="utf-8")
    assert "gsk_" not in html and "GROQ_API_KEY" not in html, "Master HTML aun contiene secretos sin sanear"

    script_matches = list(re.finditer(r"<script([^>]*)>(.*?)</script>", html, re.S | re.I))
    if len(script_matches) != 54:
        print(f"AVISO: Se esperaban 54 bloques <script>, encontrados {len(script_matches)}")

    scripts_min = []
    for idx, m in enumerate(script_matches):
        body = m.group(2)
        min_body = minify_js(body)
        node_check(min_body, f"block[{idx}]")
        scripts_min.append(min_body)
    print(f"OK: {len(scripts_min)} bloques JS minificados y validados con node --check")

    # Prefix HTML before first <script>
    prefix_html = html[: script_matches[0].start()]
    # Minify <style> blocks and strip HTML comments
    prefix_html = re.sub(
        r"<style([^>]*)>(.*?)</style>",
        lambda m: f"<style{m.group(1)}>{minify_css(m.group(2))}</style>",
        prefix_html,
        flags=re.S | re.I,
    )
    prefix_html = re.sub(r"<!--.*?-->", "", prefix_html, flags=re.S)

    bootstrap_js, compressed, _ = build_bootstrapper_and_shield(scripts_min)
    test_crypto_inflate_parity(bootstrap_js, scripts_min)

    final_html = prefix_html.rstrip() + f"\n<script>{bootstrap_js}</script>\n</body></html>"
    assert "gsk_" not in final_html and "GROQ_API_KEY" not in final_html
    assert "BEGIN ORION V30" not in final_html

    for dst in PUBLIC_COPIES:
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(final_html, encoding="utf-8")
        print(f"OK: {dst.relative_to(ROOT)} ({len(final_html):,} bytes)")

    # Compile & obfuscate tracked src/orion_nasa_kids_v30.js
    if LOCAL_V30_JS.exists():
        v30_raw = LOCAL_V30_JS.read_text(encoding="utf-8")
        v30_min = minify_js(v30_raw)
        v30_obf = obfuscate_js_strings(v30_min, hashlib.sha256(b"v30_src_" + os.urandom(8)).digest()[:16])
        node_check(v30_obf, "src/orion_nasa_kids_v30.js")
        out_v30 = ROOT / "src" / "orion_nasa_kids_v30.js"
        out_v30.write_text(v30_obf, encoding="utf-8")
        print(f"OK: {out_v30.relative_to(ROOT)} protegido ({len(v30_obf):,} bytes)")

    # Minify & obfuscate landing JS files
    shield_landing = build_landing_shield()
    for src_dir, dst_dir in [
        (LOCAL_DIR / "web_landing_js", ROOT / "web_landing" / "js"),
        (LOCAL_DIR / "web_landing_en_js", ROOT / "web_landing_en" / "js"),
    ]:
        for name in ("main.js", "space.js"):
            src_f = src_dir / name
            if src_f.exists():
                raw = src_f.read_text(encoding="utf-8")
                mn = minify_js(raw)
                ob = obfuscate_js_strings(mn, os.urandom(16))
                if name == "main.js":
                    ob = shield_landing + "\n" + ob
                node_check(ob, str((dst_dir / name).relative_to(ROOT)))
                (dst_dir / name).write_text(ob, encoding="utf-8")
                print(f"OK: {(dst_dir / name).relative_to(ROOT)} protegido ({len(ob):,} bytes)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
