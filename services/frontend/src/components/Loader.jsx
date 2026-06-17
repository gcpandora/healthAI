export default function Loader() {
  return (
    <div style={{
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      height: "100vh"
    }}>
      <div style={{
        textAlign: "center"
      }}>
        <div style={{
          width: "50px",
          height: "50px",
          border: "4px solid rgba(52, 152, 219, 0.1)",
          borderTop: "4px solid #3498db",
          borderRadius: "50%",
          animation: "spin 1s linear infinite",
          margin: "0 auto 20px"
        }} />
        <p style={{
          margin: "0",
          color: "#7f8c8d",
          fontSize: "16px"
        }}>
          Loading data...
        </p>
        <style>{`
          @keyframes spin {
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    </div>
  );
}