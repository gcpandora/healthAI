export default function Table({ data }) {
  console.log("[Table] Rendering with data:", data ? `${data.length} items` : "no data", data);

  if (!data || !data.length) {
    console.log("[Table] No data - showing empty message");
    return (
      <div style={{
        background: "white",
        padding: "40px",
        borderRadius: "12px",
        textAlign: "center",
        color: "#7f8c8d"
      }}>
        <p>No data available</p>
      </div>
    );
  }

  const keys = Object.keys(data[0]);
  console.log("[Table] Keys extracted:", keys);

  return (
    <div style={{
      background: "white",
      borderRadius: "12px",
      overflow: "hidden",
      boxShadow: "0 2px 8px rgba(0, 0, 0, 0.08)"
    }}>
      <table style={{
        width: "100%",
        borderCollapse: "collapse"
      }}>
        <thead>
          <tr style={{
            background: "linear-gradient(135deg, #f8f9fa 0%, #f0f1f3 100%)",
            borderBottom: "2px solid #e2e8f0"
          }}>
            {keys.map(k => (
              <th key={k} style={{
                padding: "16px 12px",
                textAlign: "left",
                fontSize: "12px",
                fontWeight: "600",
                color: "#475569",
                textTransform: "uppercase",
                letterSpacing: "0.5px"
              }}>
                {k}
              </th>
            ))}
          </tr>
        </thead>

        <tbody>
          {data.map((row, i) => {
            console.log(`[Table] Rendering row ${i}:`, row);
            return (
              <tr 
                key={i}
                style={{
                  borderBottom: "1px solid #f1f5f9",
                  transition: "background 0.2s ease"
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = "#f8f9fa"}
                onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
              >
                {keys.map(k => (
                  <td key={k} style={{
                    padding: "14px 12px",
                    color: "#334155",
                    fontSize: "14px"
                  }}>
                    {row[k] ? String(row[k]).substring(0, 50) : "-"}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}