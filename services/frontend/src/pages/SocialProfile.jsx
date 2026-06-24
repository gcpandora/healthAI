import { useState, useEffect, useRef } from "react";
import { postsAPI } from "../services/api";
import { useAuth } from "../contexts/AuthContext";

function initials(name) {
  return (name || "?")
    .split(" ")
    .map((w) => w[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
}

export default function SocialProfile() {
  const { user } = useAuth();
  const fileRef = useRef(null);

  const [form, setForm] = useState({
    display_name: "",
    bio: "",
  });
  const [avatarUrl, setAvatarUrl] = useState(null);
  const [avatarPreview, setAvatarPreview] = useState(null);
  const [avatarFile, setAvatarFile] = useState(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState(null);

  // Chargement du profil social au montage
  useEffect(() => {
    postsAPI
      .getSocialProfile()
      .then((r) => {
        const p = r.data;
        setForm({
          display_name: p.display_name || "",
          bio: p.bio || "",
        });
        setAvatarUrl(p.avatar_url || null);
      })
      .catch(() => {
        // L'API n'est pas encore disponible — on préremplit depuis le contexte auth
        setForm({
          display_name:
            user?.display_name ||
            `${user?.first_name || ""} ${user?.last_name || ""}`.trim(),
          bio: user?.bio || "",
        });
      })
      .finally(() => setLoading(false));
  }, [user]);

  const handleAvatarChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      setStatus({ type: "error", text: "Seules les images sont acceptées pour l'avatar." });
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setStatus({ type: "error", text: "Image trop volumineuse (max 5 Mo)." });
      return;
    }
    setAvatarFile(file);
    setAvatarPreview(URL.createObjectURL(file));
    setStatus(null);
  };

  const handleSave = async () => {
    if (!form.display_name.trim()) {
      setStatus({ type: "error", text: "Le nom d'affichage est obligatoire." });
      return;
    }
    setSaving(true);
    setStatus(null);

    try {
      let finalAvatarUrl = avatarUrl;

      if (avatarFile) {
        const uploadRes = await postsAPI.uploadMedia(avatarFile);
        finalAvatarUrl = uploadRes.data?.url || uploadRes.data?.media_url || avatarUrl;
      }

      await postsAPI.updateSocialProfile({
        display_name: form.display_name.trim(),
        bio: form.bio.trim(),
        avatar_url: finalAvatarUrl,
      });

      setAvatarUrl(finalAvatarUrl);
      if (avatarPreview) {
        URL.revokeObjectURL(avatarPreview);
        setAvatarPreview(null);
      }
      setAvatarFile(null);

      setStatus({ type: "success", text: "Profil social mis à jour avec succès." });
    } catch (err) {
      setStatus({
        type: "error",
        text:
          err.response?.data?.detail ||
          "Impossible de mettre à jour le profil. Vérifiez que l'API publications (port 8003) est démarrée.",
      });
    } finally {
      setSaving(false);
    }
  };

  const displayedAvatar = avatarPreview || avatarUrl;
  const displayName = form.display_name || user?.first_name || "?";

  const colors = ["#3498db", "#2ecc71", "#e67e22", "#9b59b6", "#1abc9c"];
  const avatarBg = colors[(displayName).charCodeAt(0) % colors.length];

  if (loading) {
    return (
      <div style={{ padding: "60px 16px", textAlign: "center" }}>
        <div
          style={{
            display: "inline-block",
            width: "32px",
            height: "32px",
            border: "3px solid #e2e8f0",
            borderTopColor: "#3498db",
            borderRadius: "50%",
            animation: "spin 0.8s linear infinite",
          }}
        />
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: "680px", margin: "0 auto", padding: "28px 16px" }}>
      <h1 style={{ margin: "0 0 6px", fontSize: "24px", fontWeight: "800", color: "#1e293b" }}>
        Profil social
      </h1>
      <p style={{ margin: "0 0 24px", fontSize: "14px", color: "#94a3b8" }}>
        Ce profil est visible par les autres membres sur le réseau social.
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "20px",
        }}
      >
        {/* Formulaire */}
        <div
          style={{
            background: "white",
            borderRadius: "14px",
            padding: "24px",
            boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
            border: "1px solid #f1f5f9",
          }}
        >
          <h3 style={{ margin: "0 0 18px", fontSize: "16px", color: "#1e293b" }}>
            Modifier le profil
          </h3>

          {/* Avatar */}
          <div style={{ display: "flex", alignItems: "center", gap: "16px", marginBottom: "20px" }}>
            <div style={{ position: "relative" }}>
              {displayedAvatar ? (
                <img
                  src={displayedAvatar}
                  alt="avatar"
                  style={{
                    width: "72px",
                    height: "72px",
                    borderRadius: "50%",
                    objectFit: "cover",
                    border: "3px solid #e2e8f0",
                  }}
                />
              ) : (
                <div
                  style={{
                    width: "72px",
                    height: "72px",
                    borderRadius: "50%",
                    background: avatarBg,
                    color: "white",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontWeight: "800",
                    fontSize: "26px",
                    border: "3px solid #e2e8f0",
                  }}
                >
                  {initials(displayName)}
                </div>
              )}
              <label
                htmlFor="avatar-upload"
                style={{
                  position: "absolute",
                  bottom: 0,
                  right: 0,
                  background: "#3498db",
                  border: "2px solid white",
                  borderRadius: "50%",
                  width: "24px",
                  height: "24px",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  cursor: "pointer",
                  fontSize: "12px",
                }}
                title="Changer l'avatar"
              >
                ✏️
              </label>
              <input
                ref={fileRef}
                id="avatar-upload"
                type="file"
                accept="image/*"
                onChange={handleAvatarChange}
                style={{ display: "none" }}
              />
            </div>
            <div>
              <div style={{ fontWeight: "600", fontSize: "15px", color: "#1e293b" }}>
                {form.display_name || "—"}
              </div>
              <button
                onClick={() => fileRef.current?.click()}
                style={{
                  marginTop: "4px",
                  background: "transparent",
                  border: "none",
                  color: "#3498db",
                  cursor: "pointer",
                  fontSize: "13px",
                  padding: 0,
                }}
              >
                Changer la photo
              </button>
            </div>
          </div>

          {/* Nom d'affichage */}
          <label style={{ display: "block", fontSize: "13px", fontWeight: "600", color: "#475569", marginBottom: "6px" }}>
            Nom d'affichage *
          </label>
          <input
            value={form.display_name}
            onChange={(e) => setForm((p) => ({ ...p, display_name: e.target.value }))}
            placeholder="Votre nom visible par la communauté"
            maxLength={50}
            style={{
              width: "100%",
              padding: "10px 12px",
              border: "1px solid #e2e8f0",
              borderRadius: "8px",
              fontSize: "14px",
              outline: "none",
              boxSizing: "border-box",
              marginBottom: "14px",
            }}
          />

          {/* Bio */}
          <label style={{ display: "block", fontSize: "13px", fontWeight: "600", color: "#475569", marginBottom: "6px" }}>
            Courte bio
          </label>
          <textarea
            value={form.bio}
            onChange={(e) => setForm((p) => ({ ...p, bio: e.target.value }))}
            placeholder="Quelques mots sur vous, vos objectifs…"
            maxLength={160}
            rows={3}
            style={{
              width: "100%",
              padding: "10px 12px",
              border: "1px solid #e2e8f0",
              borderRadius: "8px",
              fontSize: "14px",
              outline: "none",
              resize: "vertical",
              boxSizing: "border-box",
              fontFamily: "inherit",
            }}
          />
          <div style={{ textAlign: "right", fontSize: "11px", color: "#94a3b8", marginTop: "2px" }}>
            {form.bio.length} / 160
          </div>

          {/* Status */}
          {status && (
            <div
              style={{
                marginTop: "12px",
                padding: "10px 14px",
                background: status.type === "error" ? "#fef2f2" : "#f0fdf4",
                border: `1px solid ${status.type === "error" ? "#fecaca" : "#bbf7d0"}`,
                borderRadius: "8px",
                color: status.type === "error" ? "#dc2626" : "#15803d",
                fontSize: "13px",
              }}
            >
              {status.type === "error" ? "⚠️" : "✅"} {status.text}
            </div>
          )}

          <button
            onClick={handleSave}
            disabled={saving}
            style={{
              marginTop: "16px",
              width: "100%",
              padding: "12px",
              background: saving ? "#e2e8f0" : "linear-gradient(135deg, #3498db, #2980b9)",
              color: saving ? "#94a3b8" : "white",
              border: "none",
              borderRadius: "10px",
              fontWeight: "700",
              fontSize: "14px",
              cursor: saving ? "default" : "pointer",
              boxShadow: saving ? "none" : "0 2px 8px rgba(52,152,219,0.25)",
            }}
          >
            {saving ? "Enregistrement…" : "Enregistrer"}
          </button>
        </div>

        {/* Aperçu de la carte profil */}
        <div>
          <div
            style={{
              background: "white",
              borderRadius: "14px",
              padding: "24px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
              border: "1px solid #f1f5f9",
              marginBottom: "16px",
            }}
          >
            <h3 style={{ margin: "0 0 16px", fontSize: "16px", color: "#1e293b" }}>
              Aperçu
            </h3>
            <div style={{ display: "flex", gap: "14px", alignItems: "center" }}>
              {displayedAvatar ? (
                <img
                  src={displayedAvatar}
                  alt="avatar"
                  style={{ width: "56px", height: "56px", borderRadius: "50%", objectFit: "cover" }}
                />
              ) : (
                <div
                  style={{
                    width: "56px",
                    height: "56px",
                    borderRadius: "50%",
                    background: avatarBg,
                    color: "white",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontWeight: "800",
                    fontSize: "20px",
                  }}
                >
                  {initials(displayName)}
                </div>
              )}
              <div>
                <div style={{ fontWeight: "700", fontSize: "16px", color: "#1e293b" }}>
                  {form.display_name || <span style={{ color: "#94a3b8" }}>Nom d'affichage</span>}
                </div>
                <div style={{ fontSize: "13px", color: "#64748b", marginTop: "4px" }}>
                  {form.bio || <span style={{ color: "#cbd5e1" }}>Votre bio…</span>}
                </div>
              </div>
            </div>
          </div>

          <div
            style={{
              padding: "14px 18px",
              background: "#eff6ff",
              borderRadius: "10px",
              border: "1px solid #bfdbfe",
            }}
          >
            <p style={{ margin: 0, fontSize: "13px", color: "#1d4ed8", lineHeight: "1.6" }}>
              ℹ️ Ce nom sera affiché sous chacune de vos publications et commentaires sur le réseau social.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
