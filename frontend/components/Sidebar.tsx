"use client";

import { useEffect, useState } from "react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const shortcuts = [
  { key: "Enter", desc: "send" },
  { key: "↑ / ↓", desc: "history" },
  { key: "Ctrl+L", desc: "clear" },
  { key: "Hold mic", desc: "voice" },
];

interface HealthData {
  provider: string;
  model: string;
  memory: boolean;
  voice: boolean;
}

export default function Sidebar() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [backendOk, setBackendOk] = useState<boolean | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function poll() {
      try {
        const res = await fetch(`${API}/health`, { signal: AbortSignal.timeout(3000) });
        if (cancelled) return;
        if (res.ok) {
          const data = await res.json();
          setBackendOk(true);
          setHealth({
            provider: data.provider ?? "unknown",
            model: data.model ?? "unknown",
            memory: data.memory ?? false,
            voice: data.voice ?? false,
          });
        } else {
          setBackendOk(false);
          setHealth(null);
        }
      } catch {
        if (!cancelled) {
          setBackendOk(false);
          setHealth(null);
        }
      }
    }

    poll();
    const id = setInterval(poll, 8000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  return (
    <aside
      className="flex flex-col w-52 shrink-0 h-full"
      style={{ background: "var(--surface)", borderRight: "1px solid var(--border)" }}
    >
      {/* logo */}
      <div className="px-4 py-4 border-b" style={{ borderColor: "var(--border)" }}>
        <div className="flex items-center gap-2">
          <span className="text-base font-bold tracking-widest" style={{ color: "var(--accent)" }}>
            JARVIS
          </span>
          <span className="text-xs px-1 rounded" style={{ background: "var(--border)", color: "var(--text-dim)" }}>
            v0.1
          </span>
        </div>
        <p className="text-xs mt-1" style={{ color: "var(--text-dim)" }}>
          local-first AI
        </p>
      </div>

      {/* status */}
      <div className="px-4 py-3 border-b" style={{ borderColor: "var(--border)" }}>
        <p className="text-xs uppercase tracking-widest mb-2" style={{ color: "var(--text-muted)" }}>
          System
        </p>
        <div className="space-y-2">
          <StatusRow
            label="backend"
            value={backendOk === null ? "…" : backendOk ? "online" : "offline"}
            ok={backendOk === true}
            pending={backendOk === null}
          />
          <StatusRow
            label="provider"
            value={health?.provider ?? (backendOk === false ? "—" : "…")}
            ok={backendOk === true}
            pending={backendOk === null}
          />
          <StatusRow
            label="model"
            value={health?.model ? truncate(health.model, 14) : (backendOk === false ? "—" : "…")}
            ok={backendOk === true}
            pending={backendOk === null}
          />
          <StatusRow
            label="memory"
            value={health ? (health.memory ? "pgvector" : "off") : "…"}
            ok={health?.memory === true}
            pending={backendOk === null}
          />
          <StatusRow
            label="voice"
            value={health ? (health.voice ? "whisper" : "off") : "…"}
            ok={health?.voice === true}
            pending={backendOk === null}
          />
        </div>
      </div>

      {/* session */}
      <div className="px-4 py-3 border-b flex-1" style={{ borderColor: "var(--border)" }}>
        <p className="text-xs uppercase tracking-widest mb-2" style={{ color: "var(--text-muted)" }}>
          Session
        </p>
        <div
          className="text-xs px-2 py-1.5 rounded cursor-default"
          style={{ background: "var(--accent-glow)", color: "var(--accent)", border: "1px solid var(--border)" }}
        >
          ● current
        </div>
      </div>

      {/* shortcuts */}
      <div className="px-4 py-3 border-t" style={{ borderColor: "var(--border)" }}>
        <p className="text-xs uppercase tracking-widest mb-2" style={{ color: "var(--text-muted)" }}>
          Shortcuts
        </p>
        <div className="space-y-1">
          {shortcuts.map((s) => (
            <div key={s.key} className="flex justify-between items-center">
              <kbd
                className="text-xs px-1 rounded"
                style={{ background: "var(--border)", color: "var(--text)" }}
              >
                {s.key}
              </kbd>
              <span className="text-xs" style={{ color: "var(--text-dim)" }}>
                {s.desc}
              </span>
            </div>
          ))}
        </div>
      </div>
    </aside>
  );
}

function truncate(s: string, max: number) {
  return s.length > max ? s.slice(0, max - 1) + "…" : s;
}

function StatusRow({
  label,
  value,
  ok,
  pending,
}: {
  label: string;
  value: string;
  ok: boolean;
  pending?: boolean;
}) {
  const dotColor = pending ? "var(--text-dim)" : ok ? "var(--accent)" : "var(--error)";
  return (
    <div className="flex items-center justify-between">
      <span className="text-xs" style={{ color: "var(--text-dim)" }}>
        {label}
      </span>
      <div className="flex items-center gap-1.5">
        <span
          className="w-1.5 h-1.5 rounded-full"
          style={{ background: dotColor, opacity: pending ? 0.5 : 1 }}
        />
        <span className="text-xs" style={{ color: "var(--text)" }}>
          {value}
        </span>
      </div>
    </div>
  );
}
