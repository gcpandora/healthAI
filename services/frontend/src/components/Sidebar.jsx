import { Link, useLocation } from "react-router-dom";
import { useState } from "react";

export default function Sidebar() {
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(true);

  const sections = [
    {
      label: "GÉNÉRAL",
      items: [
        { path: "/",          label: "Dashboard",      icon: "📊" },
        { path: "/users",     label: "Utilisateurs",   icon: "👥" },
        { path: "/exercises", label: "Exercices",      icon: "💪" },
        { path: "/nutrition", label: "Nutrition",      icon: "🥗" },
      ],
    },
    {
      label: "IA & ML",
      items: [
        { path: "/nutrition-ai",   label: "Analyse IA",     icon: "🤖" },
        { path: "/fitness",        label: "Fitness IA",      icon: "🏋️" },
        { path: "/ml-predictions", label: "Prédictions ML",  icon: "🧠" },
        { path: "/data-quality",   label: "Data Quality",    icon: "✓"  },
      ],
    },
    {
      label: "COMMUNAUTÉ",
      items: [
        { path: "/feed",           label: "Flux social",    icon: "🏠" },
        { path: "/create-post",    label: "Publier",        icon: "✏️" },
        { path: "/chat",           label: "Messagerie",     icon: "💬" },
        { path: "/social-profile", label: "Profil social",  icon: "🪪" },
      ],
    },
    {
      label: "COMPTE",
      items: [
        { path: "/account", label: "Mon compte", icon: "👤" },
      ],
    },
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <div
      style={{
        width: isOpen ? "260px" : "72px",
        background: "linear-gradient(180deg, #1e293b 0%, #0f172a 100%)",
        color: "#fff",
        padding: "20px 10px",
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        transition: "width 0.25s ease",
        boxShadow: "2px 0 10px rgba(0,0,0,0.15)",
        overflowY: "auto",
        overflowX: "hidden",
        flexShrink: 0,
      }}
    >
      {/* Logo + toggle */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: isOpen ? "space-between" : "center",
          marginBottom: "24px",
          paddingLeft: isOpen ? "6px" : "0",
        }}
      >
        {isOpen && (
          <span style={{ fontWeight: "800", fontSize: "18px", letterSpacing: "-0.01em" }}>
            HealthAI
          </span>
        )}
        <button
          onClick={() => setIsOpen(!isOpen)}
          style={{
            background: "rgba(255,255,255,0.08)",
            border: "none",
            color: "#94a3b8",
            cursor: "pointer",
            padding: "7px 8px",
            borderRadius: "8px",
            fontSize: "14px",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexShrink: 0,
            transition: "background 0.15s",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(255,255,255,0.14)")}
          onMouseLeave={(e) => (e.currentTarget.style.background = "rgba(255,255,255,0.08)")}
        >
          {isOpen ? "←" : "→"}
        </button>
      </div>

      {/* Nav sections */}
      <nav style={{ flex: 1, display: "flex", flexDirection: "column", gap: "4px" }}>
        {sections.map((section) => (
          <div key={section.label} style={{ marginBottom: "6px" }}>
            {/* Section label */}
            {isOpen && (
              <div
                style={{
                  fontSize: "10px",
                  fontWeight: "700",
                  letterSpacing: "0.09em",
                  color: "#334155",
                  padding: "8px 12px 4px",
                  textTransform: "uppercase",
                }}
              >
                {section.label}
              </div>
            )}
            {!isOpen && (
              <div style={{ height: "8px" }} />
            )}

            {section.items.map((item) => {
              const active = isActive(item.path);
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  title={!isOpen ? item.label : undefined}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: isOpen ? "10px" : "0",
                    justifyContent: isOpen ? "flex-start" : "center",
                    padding: isOpen ? "9px 12px" : "10px 0",
                    color: active ? "#60a5fa" : "#94a3b8",
                    textDecoration: "none",
                    borderRadius: "8px",
                    background: active ? "rgba(52,152,219,0.14)" : "transparent",
                    border: active ? "1px solid rgba(52,152,219,0.28)" : "1px solid transparent",
                    fontSize: "13.5px",
                    fontWeight: active ? "700" : "500",
                    transition: "all 0.15s",
                    marginBottom: "1px",
                  }}
                  onMouseEnter={(e) => {
                    if (!active) e.currentTarget.style.background = "rgba(255,255,255,0.05)";
                  }}
                  onMouseLeave={(e) => {
                    if (!active) e.currentTarget.style.background = "transparent";
                  }}
                >
                  <span
                    style={{
                      fontSize: "17px",
                      minWidth: isOpen ? "20px" : "auto",
                      textAlign: "center",
                    }}
                  >
                    {item.icon}
                  </span>
                  {isOpen && (
                    <span style={{ whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                      {item.label}
                    </span>
                  )}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>

      {/* Footer version */}
      {isOpen && (
        <div
          style={{
            paddingTop: "12px",
            borderTop: "1px solid rgba(255,255,255,0.06)",
            fontSize: "11px",
            color: "#334155",
            paddingLeft: "12px",
          }}
        >
          v2.1.0 — Communauté
        </div>
      )}
    </div>
  );
}
