import { Link, useLocation } from "react-router-dom";
import { useState } from "react";

export default function Sidebar() {
  const location = useLocation();
  const [isOpen, setIsOpen] = useState(true);

  const navItems = [
    { path: "/", label: "Dashboard", icon: "📊" },
    { path: "/users", label: "Users", icon: "👥" },
    { path: "/exercises", label: "Exercises", icon: "💪" },
    { path: "/nutrition", label: "Nutrition", icon: "🥗" },
    { path: "/nutrition-ai", label: "Analyse IA",  icon: "🤖" },
    { path: "/fitness",         label: "Fitness IA",     icon: "🏋️" },
    { path: "/ml-predictions",  label: "Prédictions ML", icon: "🧠" },
    { path: "/data-quality", label: "Data Quality", icon: "✓" },
    { path: "/account", label: "Mon compte", icon: "👤" }
  ];

  return (
    <div style={{
      width: isOpen ? "260px" : "80px",
      background: "linear-gradient(180deg, #1e293b 0%, #0f172a 100%)",
      color: "#fff",
      padding: "20px",
      height: "100vh",
      display: "flex",
      flexDirection: "column",
      transition: "all 0.3s ease",
      boxShadow: "2px 0 8px rgba(0, 0, 0, 0.1)"
    }}>
      <div style={{
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        marginBottom: "30px"
      }}>
        <h2 style={{
          margin: "0",
          fontSize: "20px",
          fontWeight: "700",
          opacity: isOpen ? 1 : 0,
          transition: "opacity 0.3s ease"
        }}>
          HealthAI
        </h2>
        <button
          onClick={() => setIsOpen(!isOpen)}
          style={{
            background: "rgba(255, 255, 255, 0.1)",
            border: "none",
            color: "#fff",
            cursor: "pointer",
            padding: "8px 8px",
            borderRadius: "6px",
            fontSize: "16px"
          }}
        >
          {isOpen ? "←" : "→"}
        </button>
      </div>

      <nav style={{ display: "flex", flexDirection: "column", gap: "8px", flex: 1 }}>
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            style={{
              display: "flex",
              alignItems: "center",
              gap: "12px",
              padding: "12px 16px",
              color: location.pathname === item.path ? "#3498db" : "#cbd5e1",
              textDecoration: "none",
              borderRadius: "8px",
              background: location.pathname === item.path ? "rgba(52, 152, 219, 0.1)" : "transparent",
              border: location.pathname === item.path ? "1px solid rgba(52, 152, 219, 0.3)" : "1px solid transparent",
              transition: "all 0.2s ease",
              cursor: "pointer"
            }}
            onMouseEnter={(e) => {
              if (location.pathname !== item.path) {
                e.currentTarget.style.background = "rgba(255, 255, 255, 0.05)";
              }
            }}
            onMouseLeave={(e) => {
              if (location.pathname !== item.path) {
                e.currentTarget.style.background = "transparent";
              }
            }}
          >
            <span style={{ fontSize: "18px", minWidth: "24px" }}>{item.icon}</span>
            <span style={{
              opacity: isOpen ? 1 : 0,
              transition: "opacity 0.3s ease",
              whiteSpace: "nowrap"
            }}>
              {item.label}
            </span>
          </Link>
        ))}
      </nav>

      <div style={{
        paddingTop: "20px",
        borderTop: "1px solid rgba(255, 255, 255, 0.1)",
        opacity: isOpen ? 1 : 0,
        transition: "opacity 0.3s ease"
      }}>
        <p style={{
          margin: "0",
          fontSize: "12px",
          color: "#94a3b8"
        }}>
          v1.0.0
        </p>
      </div>
    </div>
  );
}