import Sidebar from "./Sidebar";
import Header from "./Header";

export default function Layout({ children }) {
  return (
    <div style={{ display: "flex", minHeight: "100vh" }}>
      <Sidebar />
      <div style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        background: "linear-gradient(135deg, #f5f6fa 0%, #f8f9fa 100%)"
      }}>
        <Header />
        <main style={{
          flex: 1,
          overflow: "auto"
        }}>
          {children}
        </main>
      </div>
    </div>
  );
}