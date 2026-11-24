/**
 * Cloudflare Worker — Proxy seguro para Robbie IA (Junior Mission Orión)
 *
 * Objetivo:
 * - Mantener la API Key de Groq (GROQ_API_KEY) exclusivamente en el servidor.
 * - Aceptar peticiones únicamente desde orígenes oficiales del proyecto.
 * - Aplicar límite de frecuencia por IP, validar modelos y acotar max_tokens.
 */

const ALLOWED_ORIGINS = new Set([
  "https://orionbeta-165b9.web.app",
  "https://orionbeta-165b9.firebaseapp.com",
  "https://junior-mission-orion.web.app",
  "https://junior-mision-orion.web.app",
  "https://orion.localhost",
  "http://orion.localhost"
]);

const ALLOWED_MODELS = new Set([
  "openai/gpt-oss-120b",
  "llama-3.3-70b-versatile",
  "llama-3.1-8b-instant"
]);

// Límite básico en memoria por instancia de Worker (20 peticiones / 60s por IP)
const RATE_WINDOW_MS = 60_000;
const RATE_MAX_REQ = 20;
const rateBuckets = new Map();

function checkRateLimit(ip) {
  const now = Date.now();
  const entry = rateBuckets.get(ip);
  if (!entry || now - entry.start > RATE_WINDOW_MS) {
    rateBuckets.set(ip, { start: now, count: 1 });
    // Limpieza ocasional para evitar crecimiento ilimitado
    if (rateBuckets.size > 5000) {
      for (const [k, v] of rateBuckets) {
        if (now - v.start > RATE_WINDOW_MS) rateBuckets.delete(k);
      }
    }
    return true;
  }
  if (entry.count >= RATE_MAX_REQ) return false;
  entry.count += 1;
  return true;
}

function corsHeaders(origin) {
  const headers = {
    "Vary": "Origin",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-Orion-Client",
    "Access-Control-Max-Age": "86400",
    "Cache-Control": "no-store"
  };
  if (origin && ALLOWED_ORIGINS.has(origin)) {
    headers["Access-Control-Allow-Origin"] = origin;
  }
  return headers;
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const headers = corsHeaders(origin);

    if (request.method === "OPTIONS") {
      if (!ALLOWED_ORIGINS.has(origin)) {
        return new Response("Origen no autorizado", { status: 403 });
      }
      return new Response(null, { status: 204, headers });
    }

    if (request.method !== "POST") {
      return new Response(JSON.stringify({ error: "Método no permitido" }), {
        status: 405,
        headers: { ...headers, "Content-Type": "application/json" }
      });
    }

    if (!ALLOWED_ORIGINS.has(origin)) {
      return new Response(JSON.stringify({ error: "Origen no autorizado" }), {
        status: 403,
        headers: { ...headers, "Content-Type": "application/json" }
      });
    }

    if (!env.GROQ_API_KEY) {
      return new Response(JSON.stringify({ error: "Proxy sin GROQ_API_KEY configurada" }), {
        status: 500,
        headers: { ...headers, "Content-Type": "application/json" }
      });
    }

    const clientIp = request.headers.get("CF-Connecting-IP") || "unknown";
    if (!checkRateLimit(clientIp)) {
      return new Response(JSON.stringify({ error: "Demasiadas consultas, espera un minuto" }), {
        status: 429,
        headers: { ...headers, "Content-Type": "application/json" }
      });
    }

    let payload;
    try {
      payload = await request.json();
    } catch {
      return new Response(JSON.stringify({ error: "JSON inválido" }), {
        status: 400,
        headers: { ...headers, "Content-Type": "application/json" }
      });
    }

    if (!payload || !Array.isArray(payload.messages) || payload.messages.length === 0 || payload.messages.length > 24) {
      return new Response(JSON.stringify({ error: "Formato de mensajes inválido" }), {
        status: 400,
        headers: { ...headers, "Content-Type": "application/json" }
      });
    }

    const model = ALLOWED_MODELS.has(payload.model) ? payload.model : "openai/gpt-oss-120b";
    const maxTokens = Math.min(Math.max(Number(payload.max_tokens) || 512, 32), 1024);
    const temperature = Math.min(Math.max(Number(payload.temperature) || 0.7, 0), 1.2);

    const sanitizedMessages = payload.messages.map((m) => ({
      role: m && (m.role === "system" || m.role === "user" || m.role === "assistant") ? m.role : "user",
      content: String((m && m.content) || "").slice(0, 4000)
    }));

    const upstream = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${env.GROQ_API_KEY}`,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        model,
        messages: sanitizedMessages,
        temperature,
        max_tokens: maxTokens
      })
    });

    const text = await upstream.text();
    return new Response(text, {
      status: upstream.status,
      headers: {
        ...headers,
        "Content-Type": "application/json; charset=utf-8"
      }
    });
  }
};
