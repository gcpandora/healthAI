import { useState } from "react";

export default function Card({ title, value, icon = "📊", children }) {
  const [isHovered, setIsHovered] = useState(false);

  // Si children sont fournis, rendre juste un wrapper de carte
  if (children) {
    return (
      <div 
        style={{
          background: "linear-gradient(135deg, #ffffff 0%, #f5f6fa 100%)",
          padding: "24px",
          borderRadius: "12px",
          boxShadow: "0 2px 8px rgba(0, 0, 0, 0.08)",
          border: "1px solid rgba(52, 152, 219, 0.1)",
        }}
      >
        {children}
      </div>
    );
  }

  return (
    <div 
      style={{
        background: "linear-gradient(135deg, #ffffff 0%, #f5f6fa 100%)",
        padding: "24px",
        borderRadius: "12px",
        boxShadow: isHovered ? "0 8px 24px rgba(52, 152, 219, 0.15)" : "0 2px 8px rgba(0, 0, 0, 0.08)",
        transition: "all 0.3s ease",
        cursor: "pointer",
        border: "1px solid rgba(52, 152, 219, 0.1)",
        transform: isHovered ? "translateY(-4px)" : "translateY(0)"
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <p style={{
            margin: "0 0 12px 0",
            color: "#7f8c8d",
            fontSize: "12px",
            fontWeight: "600",
            textTransform: "uppercase",
            letterSpacing: "0.5px"
          }}>
            {title}
          </p>
          <h2 style={{
            margin: "0",
            fontSize: "28px",
            fontWeight: "700",
            color: "#2c3e50"
          }}>
            {value || "—"}
          </h2>
        </div>
        <span style={{ fontSize: "32px" }}>{icon}</span>
      </div>
    </div>
  );
}