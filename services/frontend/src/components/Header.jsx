import { useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import AuthModal from "./AuthModal";

export default function Header() {
  const { user, logout, isAuthenticated } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  const getGenderEmoji = (gender) => {
    switch (gender) {
      case "male":
        return "♂️";
      case "female":
        return "♀️";
      case "other":
        return "⚧️";
      default:
        return "👤";
    }
  };

  const handleLogout = () => {
    logout();
    setShowProfileMenu(false);
  };

  return (
    <>
      <header
        style={{
          background: "white",
          padding: "16px 32px",
          boxShadow: "0 2px 4px rgba(0, 0, 0, 0.06)",
          borderBottom: "1px solid rgba(0, 0, 0, 0.05)",
          position: "sticky",
          top: 0,
          zIndex: 100,
        }}
      >
        <div
          style={{
            maxWidth: "1400px",
            margin: "0 auto",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
            <h1 style={{ margin: "0", fontSize: "24px", fontWeight: "700", color: "#2c3e50" }}>
              HealthAI
            </h1>
            <span
              style={{
                background: "linear-gradient(135deg, #3498db, #2980b9)",
                color: "white",
                padding: "4px 12px",
                borderRadius: "20px",
                fontSize: "12px",
                fontWeight: "600",
              }}
            >
              Dashboard
            </span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
            {isAuthenticated ? (
              <div style={{ position: "relative" }}>
                <button
                  onClick={() => setShowProfileMenu(!showProfileMenu)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "8px",
                    padding: "8px 16px",
                    background: "transparent",
                    border: "1px solid #e2e8f0",
                    borderRadius: "8px",
                    cursor: "pointer",
                    fontSize: "14px",
                    fontWeight: "500",
                    color: "#2c3e50",
                    transition: "all 0.2s ease",
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.borderColor = "#3498db";
                    e.target.style.boxShadow = "0 0 0 2px rgba(52, 152, 219, 0.1)";
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.borderColor = "#e2e8f0";
                    e.target.style.boxShadow = "none";
                  }}
                >
                  <span style={{ fontSize: "16px" }}>
                    {getGenderEmoji(user?.gender)}
                  </span>
                  <span>{user?.first_name} {user?.last_name}</span>
                  <span style={{ fontSize: "12px", color: "#7f8c8d" }}>
                    ▼
                  </span>
                </button>

                {showProfileMenu && (
                  <div
                    style={{
                      position: "absolute",
                      top: "100%",
                      right: 0,
                      background: "white",
                      border: "1px solid #e2e8f0",
                      borderRadius: "8px",
                      boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
                      minWidth: "220px",
                      zIndex: 1000,
                      marginTop: "8px",
                    }}
                  >
                    <div style={{ padding: "16px", borderBottom: "1px solid #f1f5f9" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "8px" }}>
                        <span style={{ fontSize: "20px" }}>{getGenderEmoji(user?.gender)}</span>
                        <div>
                          <div style={{ fontWeight: "600", color: "#2c3e50" }}>
                            {user?.first_name} {user?.last_name}
                          </div>
                          <div style={{ fontSize: "12px", color: "#7f8c8d" }}>
                            {user?.email}
                          </div>
                        </div>
                      </div>
                      <div style={{ fontSize: "12px", color: "#7f8c8d", marginBottom: "6px" }}>
                        {user?.weight && user?.height ? `${user.weight}kg • ${user.height}cm` : "Profil incomplet"}
                      </div>
                      <div style={{ fontSize: "12px", color: "#2d6cdf", fontWeight: 700 }}>
                        Plan : {user?.plan ? user.plan : "Freemium"}
                      </div>
                    </div>

                    <button
                      onClick={handleLogout}
                      style={{
                        width: "100%",
                        padding: "12px 16px",
                        background: "transparent",
                        border: "none",
                        textAlign: "left",
                        cursor: "pointer",
                        color: "#e74c3c",
                        fontSize: "14px",
                        fontWeight: "500",
                        borderRadius: "0 0 8px 8px",
                        transition: "background 0.2s ease",
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.background = "#fee2e2";
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.background = "transparent";
                      }}
                    >
                      Déconnexion
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <button
                onClick={() => setShowAuthModal(true)}
                style={{
                  padding: "10px 20px",
                  backgroundColor: "#3498db",
                  color: "white",
                  border: "none",
                  borderRadius: "8px",
                  cursor: "pointer",
                  fontSize: "14px",
                  fontWeight: "600",
                  transition: "all 0.2s ease",
                  boxShadow: "0 2px 6px rgba(52, 152, 219, 0.2)",
                }}
                onMouseEnter={(e) => {
                  e.target.style.backgroundColor = "#2980b9";
                  e.target.style.boxShadow = "0 4px 12px rgba(52, 152, 219, 0.3)";
                }}
                onMouseOut={(e) => {
                  e.target.style.backgroundColor = "#3498db";
                  e.target.style.boxShadow = "0 2px 6px rgba(52, 152, 219, 0.2)";
                }}
              >
                Sign In
              </button>
            )}
          </div>
        </div>
      </header>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
      />

      {showProfileMenu && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            zIndex: 50,
          }}
          onClick={() => setShowProfileMenu(false)}
        />
      )}
    </>
  );
}