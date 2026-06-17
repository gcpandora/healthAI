export default function ModalHeader({ title, subtitle, onClose }) {
  return (
    <div style={{ padding: "20px 24px", borderBottom: "1px solid #e5e7eb", textAlign: "center", position: "relative" }}>
      <h3 style={{ margin: "0 0 10px 0" }}>{title}</h3>
      <p style={{ margin: 0, color: "#6b7280" }}>{subtitle}</p>
      <button
        onClick={onClose}
        style={{
          position: "absolute",
          top: "16px",
          right: "16px",
          background: "none",
          border: "none",
          fontSize: "18px",
          cursor: "pointer"
        }}
      >
        ✕
      </button>
    </div>
  );
}