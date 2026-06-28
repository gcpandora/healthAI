import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
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

function Avatar({ src, name, size = 44 }) {
  const colors = ["#3498db", "#2ecc71", "#e67e22", "#9b59b6", "#1abc9c"];
  const color = colors[(name || "").charCodeAt(0) % colors.length];
  if (src) {
    return (
      <img
        src={src}
        alt={name}
        style={{ width: size, height: size, borderRadius: "50%", objectFit: "cover", flexShrink: 0 }}
      />
    );
  }
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: "50%",
        background: color,
        color: "white",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontWeight: "700",
        fontSize: size * 0.36,
        flexShrink: 0,
      }}
    >
      {initials(name)}
    </div>
  );
}

const MAX_CHARS = 500;

export default function CreatePost() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const fileRef = useRef(null);

  const [content, setContent] = useState("");
  const [mediaFile, setMediaFile] = useState(null);
  const [mediaPreview, setMediaPreview] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const displayName = user?.display_name || user?.username || `${user?.first_name || ""} ${user?.last_name || ""}`.trim() || "Moi";

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const allowed = ["image/jpeg", "image/png", "image/gif", "image/webp", "video/mp4"];
    if (!allowed.includes(file.type)) {
      setError("Format non supporté. Utilisez JPG, PNG, GIF, WEBP ou MP4.");
      return;
    }
    if (file.size > 20 * 1024 * 1024) {
      setError("Fichier trop volumineux (max 20 Mo).");
      return;
    }

    setError(null);
    setMediaFile(file);
    setMediaPreview(URL.createObjectURL(file));
  };

  const removeMedia = () => {
    setMediaFile(null);
    if (mediaPreview) URL.revokeObjectURL(mediaPreview);
    setMediaPreview(null);
    if (fileRef.current) fileRef.current.value = "";
  };

  const handleSubmit = async () => {
    if (!content.trim() && !mediaFile) {
      setError("Ajoutez du texte ou une image avant de publier.");
      return;
    }
    setError(null);
    setSubmitting(true);

    try {
      let mediaUrls = [];

      // Upload du média en premier si présent
      if (mediaFile) {
        const uploadRes = await postsAPI.uploadMedia(mediaFile);
        const url = uploadRes.data?.url || uploadRes.data?.media_url;
        if (url) mediaUrls.push(url);
      }

      await postsAPI.createPost({
        content: content.trim(),
        media_urls: mediaUrls,
      });

      navigate("/feed");
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Erreur lors de la publication. Vérifiez que l'API publications (port 8003) est démarrée."
      );
      setSubmitting(false);
    }
  };

  const isVideo = mediaFile?.type?.startsWith("video/");

  return (
    <div style={{ maxWidth: "680px", margin: "0 auto", padding: "28px 16px" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "24px" }}>
        <button
          onClick={() => navigate("/feed")}
          style={{
            background: "transparent",
            border: "none",
            cursor: "pointer",
            fontSize: "20px",
            color: "#64748b",
            padding: "4px 8px",
            borderRadius: "8px",
          }}
        >
          ←
        </button>
        <h1 style={{ margin: 0, fontSize: "22px", fontWeight: "800", color: "#1e293b" }}>
          Nouvelle publication
        </h1>
      </div>

      <div
        style={{
          background: "white",
          borderRadius: "16px",
          padding: "24px",
          boxShadow: "0 2px 12px rgba(0,0,0,0.08)",
          border: "1px solid #f1f5f9",
        }}
      >
        {/* Auteur */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px", marginBottom: "16px" }}>
          <Avatar name={displayName} src={user?.avatar_url} size={44} />
          <div>
            <div style={{ fontWeight: "700", fontSize: "15px", color: "#1e293b" }}>{displayName}</div>
            <div style={{ fontSize: "12px", color: "#94a3b8" }}>Publication publique</div>
          </div>
        </div>

        {/* Textarea */}
        <textarea
          value={content}
          onChange={(e) => {
            if (e.target.value.length <= MAX_CHARS) setContent(e.target.value);
          }}
          placeholder="Partagez votre progression, vos succès, vos conseils…"
          rows={5}
          style={{
            width: "100%",
            padding: "14px",
            border: "1px solid #e2e8f0",
            borderRadius: "12px",
            fontSize: "15px",
            lineHeight: "1.6",
            color: "#1e293b",
            resize: "vertical",
            outline: "none",
            boxSizing: "border-box",
            fontFamily: "inherit",
            transition: "border-color 0.2s",
          }}
          onFocus={(e) => (e.target.style.borderColor = "#3498db")}
          onBlur={(e) => (e.target.style.borderColor = "#e2e8f0")}
        />
        <div
          style={{
            textAlign: "right",
            fontSize: "12px",
            color: content.length > MAX_CHARS * 0.85 ? "#e74c3c" : "#94a3b8",
            marginTop: "4px",
          }}
        >
          {content.length} / {MAX_CHARS}
        </div>

        {/* Prévisualisation média */}
        {mediaPreview && (
          <div
            style={{
              position: "relative",
              marginTop: "14px",
              borderRadius: "12px",
              overflow: "hidden",
              border: "1px solid #e2e8f0",
            }}
          >
            {isVideo ? (
              <video
                src={mediaPreview}
                controls
                style={{ width: "100%", maxHeight: "320px", display: "block" }}
              />
            ) : (
              <img
                src={mediaPreview}
                alt="preview"
                style={{ width: "100%", maxHeight: "320px", objectFit: "cover", display: "block" }}
              />
            )}
            <button
              onClick={removeMedia}
              title="Supprimer le média"
              style={{
                position: "absolute",
                top: "8px",
                right: "8px",
                background: "rgba(0,0,0,0.6)",
                border: "none",
                borderRadius: "50%",
                width: "30px",
                height: "30px",
                cursor: "pointer",
                color: "white",
                fontSize: "16px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
            >
              ✕
            </button>
          </div>
        )}

        {/* Erreur */}
        {error && (
          <div
            style={{
              marginTop: "12px",
              padding: "10px 14px",
              background: "#fef2f2",
              border: "1px solid #fecaca",
              borderRadius: "8px",
              color: "#dc2626",
              fontSize: "13px",
            }}
          >
            ⚠️ {error}
          </div>
        )}

        {/* Barre d'actions */}
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginTop: "16px",
            paddingTop: "16px",
            borderTop: "1px solid #f1f5f9",
          }}
        >
          {/* Ajouter media */}
          <div style={{ display: "flex", gap: "8px" }}>
            <input
              ref={fileRef}
              type="file"
              accept="image/jpeg,image/png,image/gif,image/webp,video/mp4"
              onChange={handleFileChange}
              style={{ display: "none" }}
              id="media-upload"
            />
            <label
              htmlFor="media-upload"
              style={{
                display: "flex",
                alignItems: "center",
                gap: "6px",
                padding: "8px 14px",
                background: "#f8fafc",
                border: "1px solid #e2e8f0",
                borderRadius: "8px",
                cursor: "pointer",
                fontSize: "14px",
                color: "#475569",
                fontWeight: "600",
                userSelect: "none",
              }}
            >
              <span style={{ fontSize: "18px" }}>📷</span>
              Photo / Vidéo
            </label>
          </div>

          {/* Actions */}
          <div style={{ display: "flex", gap: "10px" }}>
            <button
              onClick={() => navigate("/feed")}
              style={{
                padding: "10px 18px",
                background: "transparent",
                border: "1px solid #e2e8f0",
                borderRadius: "10px",
                cursor: "pointer",
                fontSize: "14px",
                color: "#64748b",
                fontWeight: "600",
              }}
            >
              Annuler
            </button>
            <button
              onClick={handleSubmit}
              disabled={submitting || (!content.trim() && !mediaFile)}
              style={{
                padding: "10px 22px",
                background:
                  submitting || (!content.trim() && !mediaFile)
                    ? "#e2e8f0"
                    : "linear-gradient(135deg, #3498db, #2980b9)",
                color:
                  submitting || (!content.trim() && !mediaFile) ? "#94a3b8" : "white",
                border: "none",
                borderRadius: "10px",
                cursor:
                  submitting || (!content.trim() && !mediaFile) ? "default" : "pointer",
                fontWeight: "700",
                fontSize: "14px",
                boxShadow:
                  submitting || (!content.trim() && !mediaFile)
                    ? "none"
                    : "0 2px 8px rgba(52,152,219,0.3)",
                transition: "all 0.2s",
              }}
            >
              {submitting ? "Publication…" : "Publier"}
            </button>
          </div>
        </div>
      </div>

      {/* Tips */}
      <div
        style={{
          marginTop: "16px",
          padding: "14px 18px",
          background: "#f0fdf4",
          borderRadius: "10px",
          border: "1px solid #bbf7d0",
        }}
      >
        <p style={{ margin: 0, fontSize: "13px", color: "#15803d", lineHeight: "1.6" }}>
          💡 <strong>Idées de partage :</strong> votre objectif du jour, une recette healthy, un PR en salle, vos conseils nutrition…
        </p>
      </div>
    </div>
  );
}
