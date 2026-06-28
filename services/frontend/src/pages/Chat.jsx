/**
 * Chat.jsx — Messagerie instantanée intégrée à HealthAI
 *
 * Connecte au backend Social Place (port 3000) via Socket.io.
 * Auth : token HS256 HealthAI (localStorage "authToken") → le backend
 * accepte ce token en fallback de Keycloak.
 *
 * Dépendance à ajouter dans frontend/package.json :
 *   "socket.io-client": "^4.7.5"
 */

import { useState, useEffect, useRef, useCallback, useMemo } from "react";
import { io } from "socket.io-client";
import axios from "axios";
import { useAuth } from "../contexts/AuthContext";

// ─── Config ──────────────────────────────────────────────────────────────────

const CHAT_BACKEND = "http://localhost:3000";

// ─── Helpers ──────────────────────────────────────────────────────────────────

function initial(name) {
  return (name || "?")
    .split(" ")
    .filter(Boolean)
    .map((w) => w[0].toUpperCase())
    .slice(0, 2)
    .join("");
}

function fmtTime(iso) {
  if (!iso) return "";
  return new Date(iso).toLocaleTimeString("fr-FR", {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function fmtDate(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  const today = new Date();
  if (d.toDateString() === today.toDateString()) return "Aujourd'hui";
  const yesterday = new Date(today);
  yesterday.setDate(today.getDate() - 1);
  if (d.toDateString() === yesterday.toDateString()) return "Hier";
  return d.toLocaleDateString("fr-FR", { day: "numeric", month: "long" });
}

const AVATAR_COLORS = [
  "#3498db", "#2ecc71", "#e67e22",
  "#9b59b6", "#1abc9c", "#e74c3c",
  "#f39c12", "#16a085",
];

function avatarColor(name) {
  let h = 0;
  for (let i = 0; i < (name || "").length; i++) h += (name || "").charCodeAt(i);
  return AVATAR_COLORS[h % AVATAR_COLORS.length];
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function AvatarBubble({ name, size = 34 }) {
  return (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: "50%",
        background: avatarColor(name),
        color: "#fff",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontWeight: "700",
        fontSize: size * 0.38,
        flexShrink: 0,
        userSelect: "none",
      }}
    >
      {initial(name)}
    </div>
  );
}

// Groups consecutive messages from the same sender
function groupMessages(messages) {
  const groups = [];
  for (const msg of messages) {
    const last = groups[groups.length - 1];
    if (last && last.sender === msg.senderUsername) {
      last.items.push(msg);
    } else {
      groups.push({ sender: msg.senderUsername, items: [msg] });
    }
  }
  return groups;
}

function MessageGroup({ group, isMine }) {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: isMine ? "row-reverse" : "row",
        gap: "10px",
        alignItems: "flex-end",
        marginBottom: "12px",
      }}
    >
      {/* Avatar — only shown for others, aligned to last bubble */}
      {!isMine && <AvatarBubble name={group.sender} size={32} />}

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "2px",
          alignItems: isMine ? "flex-end" : "flex-start",
          maxWidth: "68%",
        }}
      >
        {/* Sender name — only for others, first bubble */}
        {!isMine && (
          <span
            style={{
              fontSize: "11px",
              fontWeight: "700",
              color: avatarColor(group.sender),
              paddingLeft: "2px",
              marginBottom: "2px",
            }}
          >
            {group.sender}
          </span>
        )}

        {group.items.map((msg, i) => (
          <div
            key={msg.id || i}
            title={fmtTime(msg.createdAt)}
            style={{
              padding: "9px 14px",
              borderRadius: isMine
                ? i === 0
                  ? "18px 18px 4px 18px"
                  : i === group.items.length - 1
                  ? "4px 18px 18px 18px"
                  : "4px 18px 4px 18px"
                : i === 0
                ? "18px 18px 18px 4px"
                : i === group.items.length - 1
                ? "18px 18px 18px 18px"
                : "18px 18px 18px 4px",
              background: isMine ? "linear-gradient(135deg, #3498db, #2980b9)" : "#f1f5f9",
              color: isMine ? "#fff" : "#1e293b",
              fontSize: "14px",
              lineHeight: "1.5",
              wordBreak: "break-word",
              boxShadow: isMine
                ? "0 2px 8px rgba(52,152,219,0.25)"
                : "0 1px 3px rgba(0,0,0,0.06)",
              transition: "transform 0.1s",
            }}
          >
            {msg.content}
          </div>
        ))}

        {/* Timestamp on last bubble */}
        <span
          style={{
            fontSize: "10px",
            color: "#94a3b8",
            paddingLeft: "2px",
            paddingRight: "2px",
          }}
        >
          {fmtTime(group.items[group.items.length - 1]?.createdAt)}
        </span>
      </div>
    </div>
  );
}

function TypingDots({ users }) {
  if (!users || users.length === 0) return null;
  const label =
    users.length === 1
      ? `${users[0]} est en train d'écrire`
      : users.length === 2
      ? `${users[0]} et ${users[1]} écrivent`
      : `${users.length} personnes écrivent`;

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: "8px",
        padding: "0 20px 10px",
        fontSize: "12px",
        color: "#94a3b8",
        minHeight: "28px",
      }}
    >
      <style>{`
        @keyframes typingBounce {
          0%,60%,100%{transform:translateY(0)}
          30%{transform:translateY(-5px)}
        }
      `}</style>
      <span style={{ display: "flex", gap: "3px", alignItems: "center" }}>
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            style={{
              display: "inline-block",
              width: "6px",
              height: "6px",
              borderRadius: "50%",
              background: "#3498db",
              animation: `typingBounce 1.2s ease-in-out infinite`,
              animationDelay: `${i * 0.2}s`,
            }}
          />
        ))}
      </span>
      <span style={{ fontStyle: "italic" }}>{label}…</span>
    </div>
  );
}

function CreateChannelModal({ onClose, onCreated, token }) {
  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!name.trim()) return;
    setError(null);
    setLoading(true);
    try {
      const { data } = await axios.post(
        `${CHAT_BACKEND}/api/channels`,
        { name: name.trim(), description: desc.trim() },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      onCreated(data);
      onClose();
    } catch (e) {
      setError(e.response?.data?.message || "Erreur lors de la création.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      onClick={(e) => e.target === e.currentTarget && onClose()}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(15,23,42,0.6)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
        backdropFilter: "blur(4px)",
      }}
    >
      <div
        style={{
          background: "white",
          borderRadius: "16px",
          padding: "28px",
          width: "400px",
          boxShadow: "0 20px 60px rgba(0,0,0,0.2)",
        }}
      >
        <h3 style={{ margin: "0 0 20px", fontSize: "18px", fontWeight: "800", color: "#1e293b" }}>
          Créer un salon
        </h3>

        <label style={{ fontSize: "12px", fontWeight: "700", color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em" }}>
          Nom du salon
        </label>
        <input
          autoFocus
          value={name}
          onChange={(e) => setName(e.target.value.toLowerCase().replace(/\s+/g, "-"))}
          onKeyDown={(e) => e.key === "Enter" && submit()}
          placeholder="ex : nutrition-tips"
          style={{
            display: "block",
            width: "100%",
            padding: "10px 12px",
            border: "1px solid #e2e8f0",
            borderRadius: "8px",
            fontSize: "14px",
            marginTop: "6px",
            marginBottom: "14px",
            boxSizing: "border-box",
            outline: "none",
          }}
        />

        <label style={{ fontSize: "12px", fontWeight: "700", color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em" }}>
          Description (optionnel)
        </label>
        <input
          value={desc}
          onChange={(e) => setDesc(e.target.value)}
          placeholder="De quoi on parle ici ?"
          style={{
            display: "block",
            width: "100%",
            padding: "10px 12px",
            border: "1px solid #e2e8f0",
            borderRadius: "8px",
            fontSize: "14px",
            marginTop: "6px",
            marginBottom: "20px",
            boxSizing: "border-box",
            outline: "none",
          }}
        />

        {error && (
          <p style={{ margin: "0 0 12px", fontSize: "13px", color: "#dc2626" }}>⚠️ {error}</p>
        )}

        <div style={{ display: "flex", gap: "10px", justifyContent: "flex-end" }}>
          <button
            onClick={onClose}
            style={{
              padding: "10px 18px",
              border: "1px solid #e2e8f0",
              background: "white",
              borderRadius: "8px",
              cursor: "pointer",
              fontSize: "14px",
              color: "#64748b",
            }}
          >
            Annuler
          </button>
          <button
            onClick={submit}
            disabled={loading || !name.trim()}
            style={{
              padding: "10px 20px",
              background: !name.trim() || loading ? "#e2e8f0" : "linear-gradient(135deg,#3498db,#2980b9)",
              color: !name.trim() || loading ? "#94a3b8" : "white",
              border: "none",
              borderRadius: "8px",
              cursor: !name.trim() || loading ? "default" : "pointer",
              fontSize: "14px",
              fontWeight: "700",
            }}
          >
            {loading ? "Création…" : "Créer"}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─── Main page ────────────────────────────────────────────────────────────────

export default function Chat() {
  const { user } = useAuth();
  const token = localStorage.getItem("authToken") || "";

  // Derive username from HealthAI user object
  const myUsername = useMemo(
    () =>
      user?.username ||
      [user?.first_name, user?.last_name].filter(Boolean).join(" ") ||
      user?.email?.split("@")[0] ||
      "Utilisateur",
    [user]
  );

  // ── State ──────────────────────────────────────────────────────────────────
  const [channels, setChannels] = useState([]);
  const [activeChannel, setActiveChannel] = useState(null);
  const [messages, setMessages] = useState([]);
  const [onlineUsers, setOnlineUsers] = useState([]);
  const [typingUsers, setTypingUsers] = useState([]);
  const [inputText, setInputText] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [connStatus, setConnStatus] = useState("connecting"); // connecting | connected | error
  const [msgCount, setMsgCount] = useState(0); // unread badge (when panel hidden)

  // ── Refs ───────────────────────────────────────────────────────────────────
  const socketRef = useRef(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const typingTimeout = useRef(null);
  const isTypingRef = useRef(false);
  const activeChannelRef = useRef(null); // for use inside socket callbacks

  // Sync ref with state so socket callbacks always see latest value
  useEffect(() => { activeChannelRef.current = activeChannel; }, [activeChannel]);

  // ── Scroll to bottom ───────────────────────────────────────────────────────
  const scrollBottom = useCallback(() => {
    setTimeout(() => {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 50);
  }, []);

  useEffect(scrollBottom, [messages, scrollBottom]);

  // ── Fetch channels (REST) ──────────────────────────────────────────────────
  const fetchChannels = useCallback(async () => {
    try {
      const { data } = await axios.get(`${CHAT_BACKEND}/api/channels`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setChannels(data);
    } catch {
      // backend may not be ready — retry silently
    }
  }, [token]);

  // ── Socket.io setup ────────────────────────────────────────────────────────
  useEffect(() => {
    const socket = io(CHAT_BACKEND, {
      auth: {
        token,
        username: myUsername, // fallback hint for the backend if JWT lacks it
      },
      transports: ["websocket", "polling"],
      reconnectionAttempts: 5,
      reconnectionDelay: 2000,
    });

    socketRef.current = socket;

    socket.on("connect", () => {
      setConnStatus("connected");
      fetchChannels();
    });

    socket.on("connect_error", () => setConnStatus("error"));
    socket.on("disconnect", () => setConnStatus("connecting"));

    socket.on("online_users", (users) => {
      setOnlineUsers(users);
    });

    socket.on("channel_created", (ch) => {
      setChannels((prev) =>
        prev.find((c) => c.id === ch.id) ? prev : [...prev, ch]
      );
    });

    socket.on("channel_history", ({ channelId, messages: hist }) => {
      if (activeChannelRef.current?.id === channelId) {
        setMessages(hist);
      }
    });

    socket.on("new_message", (msg) => {
      if (activeChannelRef.current?.id === msg.channelId) {
        setMessages((prev) => [...prev, msg]);
      }
    });

    socket.on("typing_users", (users) => {
      setTypingUsers(users.filter((u) => u !== myUsername));
    });

    return () => {
      socket.disconnect();
    };
  }, [token, myUsername, fetchChannels]);

  // ── Select channel ─────────────────────────────────────────────────────────
  const selectChannel = useCallback((channel) => {
    setActiveChannel(channel);
    setMessages([]);
    setTypingUsers([]);
    setMsgCount(0);
    socketRef.current?.emit("join_channel", { channelId: channel.id });
    setTimeout(() => inputRef.current?.focus(), 100);
  }, []);

  // ── Send message ───────────────────────────────────────────────────────────
  const sendMessage = useCallback(() => {
    const text = inputText.trim();
    if (!text || !activeChannel) return;

    // Stop typing indicator
    if (isTypingRef.current) {
      isTypingRef.current = false;
      clearTimeout(typingTimeout.current);
      socketRef.current?.emit("typing_stop", { channelId: activeChannel.id });
    }

    socketRef.current?.emit("send_message", {
      channelId: activeChannel.id,
      content: text,
    });
    setInputText("");
  }, [inputText, activeChannel]);

  // ── Typing events ──────────────────────────────────────────────────────────
  const handleInputChange = useCallback(
    (e) => {
      setInputText(e.target.value);
      if (!activeChannel) return;

      if (!isTypingRef.current) {
        isTypingRef.current = true;
        socketRef.current?.emit("typing_start", { channelId: activeChannel.id });
      }
      clearTimeout(typingTimeout.current);
      typingTimeout.current = setTimeout(() => {
        isTypingRef.current = false;
        socketRef.current?.emit("typing_stop", { channelId: activeChannel.id });
      }, 1500);
    },
    [activeChannel]
  );

  const handleInputBlur = useCallback(() => {
    if (isTypingRef.current && activeChannel) {
      isTypingRef.current = false;
      clearTimeout(typingTimeout.current);
      socketRef.current?.emit("typing_stop", { channelId: activeChannel.id });
    }
  }, [activeChannel]);

  // ── Group messages by consecutive sender ───────────────────────────────────
  const messageGroups = useMemo(() => groupMessages(messages), [messages]);

  // ── Date separators in grouped messages ────────────────────────────────────
  const renderedGroups = useMemo(() => {
    const result = [];
    let lastDate = null;
    for (const group of messageGroups) {
      const firstMsg = group.items[0];
      const dateLabel = fmtDate(firstMsg?.createdAt);
      if (dateLabel && dateLabel !== lastDate) {
        result.push({ type: "date", label: dateLabel, key: `date-${dateLabel}` });
        lastDate = dateLabel;
      }
      result.push({ type: "group", data: group, key: group.items[0]?.id || Math.random() });
    }
    return result;
  }, [messageGroups]);

  // ── Connection status badge ────────────────────────────────────────────────
  const statusDot = {
    connected: { color: "#22c55e", label: "Connecté" },
    connecting: { color: "#f59e0b", label: "Connexion…" },
    error: { color: "#ef4444", label: "Hors ligne" },
  }[connStatus];

  // ── Channel added from modal ───────────────────────────────────────────────
  const handleChannelCreated = useCallback((ch) => {
    setChannels((prev) =>
      prev.find((c) => c.id === ch.id) ? prev : [...prev, ch]
    );
    selectChannel(ch);
  }, [selectChannel]);

  // ─────────────────────────────────────────────────────────────────────────
  // Render
  // ─────────────────────────────────────────────────────────────────────────

  return (
    <div
      style={{
        display: "flex",
        height: "calc(100vh - 70px)", // fills space under the HealthAI header
        overflow: "hidden",
        background: "#f8fafc",
      }}
    >
      {/* ── CHANNEL LIST ─────────────────────────────────────────────────────── */}
      <aside
        style={{
          width: "240px",
          flexShrink: 0,
          background: "linear-gradient(180deg, #1e293b 0%, #0f172a 100%)",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
      >
        {/* Header */}
        <div
          style={{
            padding: "18px 16px 12px",
            borderBottom: "1px solid rgba(255,255,255,0.07)",
          }}
        >
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <span style={{ fontWeight: "800", fontSize: "14px", color: "#f1f5f9", letterSpacing: "0.02em" }}>
              SALONS
            </span>
            <button
              onClick={() => setShowModal(true)}
              title="Créer un salon"
              style={{
                background: "rgba(52,152,219,0.2)",
                border: "1px solid rgba(52,152,219,0.3)",
                color: "#3498db",
                borderRadius: "6px",
                width: "26px",
                height: "26px",
                cursor: "pointer",
                fontSize: "18px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                lineHeight: 1,
              }}
            >
              +
            </button>
          </div>

          {/* Connection status */}
          <div style={{ display: "flex", alignItems: "center", gap: "6px", marginTop: "8px" }}>
            <span
              style={{
                width: "7px",
                height: "7px",
                borderRadius: "50%",
                background: statusDot.color,
                flexShrink: 0,
                boxShadow: connStatus === "connected" ? `0 0 6px ${statusDot.color}` : "none",
              }}
            />
            <span style={{ fontSize: "11px", color: "#64748b" }}>{statusDot.label}</span>
          </div>
        </div>

        {/* Channel items */}
        <div style={{ flex: 1, overflowY: "auto", padding: "8px 6px" }}>
          {channels.length === 0 && connStatus === "connected" ? (
            <p style={{ fontSize: "12px", color: "#475569", textAlign: "center", padding: "20px 10px" }}>
              Aucun salon.<br />Créez-en un !
            </p>
          ) : (
            channels.map((ch) => {
              const isActive = activeChannel?.id === ch.id;
              return (
                <div
                  key={ch.id}
                  onClick={() => selectChannel(ch)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "6px",
                    padding: "9px 12px",
                    borderRadius: "8px",
                    cursor: "pointer",
                    background: isActive ? "rgba(52,152,219,0.18)" : "transparent",
                    border: isActive ? "1px solid rgba(52,152,219,0.3)" : "1px solid transparent",
                    color: isActive ? "#93c5fd" : "#94a3b8",
                    fontWeight: isActive ? "700" : "500",
                    fontSize: "14px",
                    transition: "all 0.15s",
                    marginBottom: "2px",
                  }}
                  onMouseEnter={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.background = "rgba(255,255,255,0.05)";
                      e.currentTarget.style.color = "#cbd5e1";
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isActive) {
                      e.currentTarget.style.background = "transparent";
                      e.currentTarget.style.color = "#94a3b8";
                    }
                  }}
                >
                  <span style={{ color: isActive ? "#3498db" : "#475569", fontWeight: "700", fontSize: "16px" }}>
                    #
                  </span>
                  <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {ch.name}
                  </span>
                </div>
              );
            })
          )}
        </div>

        {/* Current user footer */}
        <div
          style={{
            padding: "12px 16px",
            borderTop: "1px solid rgba(255,255,255,0.07)",
            display: "flex",
            alignItems: "center",
            gap: "10px",
          }}
        >
          <AvatarBubble name={myUsername} size={30} />
          <span
            style={{
              fontSize: "13px",
              fontWeight: "600",
              color: "#94a3b8",
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
          >
            {myUsername}
          </span>
        </div>
      </aside>

      {/* ── MESSAGES AREA ─────────────────────────────────────────────────────── */}
      <main
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
          background: "white",
        }}
      >
        {activeChannel ? (
          <>
            {/* Channel header */}
            <div
              style={{
                padding: "14px 20px",
                borderBottom: "1px solid #f1f5f9",
                background: "white",
                display: "flex",
                alignItems: "center",
                gap: "10px",
                flexShrink: 0,
              }}
            >
              <span style={{ fontSize: "20px", fontWeight: "800", color: "#3498db" }}>#</span>
              <div>
                <h2 style={{ margin: 0, fontSize: "16px", fontWeight: "800", color: "#1e293b" }}>
                  {activeChannel.name}
                </h2>
                {activeChannel.description && (
                  <p style={{ margin: 0, fontSize: "12px", color: "#94a3b8", marginTop: "1px" }}>
                    {activeChannel.description}
                  </p>
                )}
              </div>
              <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: "6px" }}>
                <span style={{ width: "8px", height: "8px", borderRadius: "50%", background: "#22c55e", display: "inline-block" }} />
                <span style={{ fontSize: "12px", color: "#64748b" }}>
                  {onlineUsers.length} en ligne
                </span>
              </div>
            </div>

            {/* Messages scroll area */}
            <div
              style={{
                flex: 1,
                overflowY: "auto",
                padding: "20px 20px 8px",
                display: "flex",
                flexDirection: "column",
              }}
            >
              {messages.length === 0 ? (
                <div
                  style={{
                    flex: 1,
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    justifyContent: "center",
                    color: "#94a3b8",
                    textAlign: "center",
                  }}
                >
                  <div style={{ fontSize: "48px", marginBottom: "12px" }}>🚀</div>
                  <p style={{ margin: 0, fontWeight: "600", color: "#475569" }}>
                    Début de l'historique de <strong>#{activeChannel.name}</strong>
                  </p>
                  <p style={{ margin: "6px 0 0", fontSize: "13px" }}>
                    Soyez le premier à écrire !
                  </p>
                </div>
              ) : (
                <>
                  {renderedGroups.map((item) => {
                    if (item.type === "date") {
                      return (
                        <div
                          key={item.key}
                          style={{
                            textAlign: "center",
                            margin: "16px 0 10px",
                            position: "relative",
                          }}
                        >
                          <span
                            style={{
                              background: "#f1f5f9",
                              padding: "3px 12px",
                              borderRadius: "20px",
                              fontSize: "11px",
                              color: "#64748b",
                              fontWeight: "600",
                            }}
                          >
                            {item.label}
                          </span>
                        </div>
                      );
                    }
                    const isMine = item.data.sender === myUsername;
                    return (
                      <MessageGroup
                        key={item.key}
                        group={item.data}
                        isMine={isMine}
                      />
                    );
                  })}
                  <div ref={messagesEndRef} />
                </>
              )}
            </div>

            {/* Typing indicator */}
            <TypingDots users={typingUsers} />

            {/* Input bar */}
            <div
              style={{
                padding: "0 16px 16px",
                flexShrink: 0,
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  background: "#f8fafc",
                  border: "1.5px solid #e2e8f0",
                  borderRadius: "14px",
                  padding: "10px 14px",
                  transition: "border-color 0.2s",
                }}
                onFocusCapture={(e) => (e.currentTarget.style.borderColor = "#3498db")}
                onBlurCapture={(e) => (e.currentTarget.style.borderColor = "#e2e8f0")}
              >
                <input
                  ref={inputRef}
                  value={inputText}
                  onChange={handleInputChange}
                  onBlur={handleInputBlur}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                      e.preventDefault();
                      sendMessage();
                    }
                  }}
                  placeholder={`Écrire dans #${activeChannel.name}…`}
                  style={{
                    flex: 1,
                    border: "none",
                    background: "transparent",
                    outline: "none",
                    fontSize: "14px",
                    color: "#1e293b",
                  }}
                />
                <button
                  onClick={sendMessage}
                  disabled={!inputText.trim()}
                  style={{
                    background: inputText.trim()
                      ? "linear-gradient(135deg, #3498db, #2980b9)"
                      : "#e2e8f0",
                    border: "none",
                    borderRadius: "10px",
                    width: "36px",
                    height: "36px",
                    cursor: inputText.trim() ? "pointer" : "default",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                    transition: "all 0.2s",
                    boxShadow: inputText.trim() ? "0 2px 8px rgba(52,152,219,0.3)" : "none",
                  }}
                >
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill={inputText.trim() ? "white" : "#94a3b8"}
                  >
                    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
                  </svg>
                </button>
              </div>
            </div>
          </>
        ) : (
          /* Empty state — no channel selected */
          <div
            style={{
              flex: 1,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              textAlign: "center",
              padding: "40px",
              color: "#94a3b8",
            }}
          >
            <div style={{ fontSize: "64px", marginBottom: "16px" }}>💬</div>
            <h2 style={{ margin: "0 0 8px", color: "#1e293b", fontSize: "20px", fontWeight: "800" }}>
              Messagerie HealthAI
            </h2>
            <p style={{ margin: "0 0 24px", fontSize: "14px", lineHeight: "1.6" }}>
              Sélectionnez un salon à gauche pour rejoindre la conversation,<br />
              ou créez un nouveau salon pour votre équipe.
            </p>
            <button
              onClick={() => setShowModal(true)}
              style={{
                padding: "12px 24px",
                background: "linear-gradient(135deg, #3498db, #2980b9)",
                color: "white",
                border: "none",
                borderRadius: "10px",
                cursor: "pointer",
                fontWeight: "700",
                fontSize: "14px",
                boxShadow: "0 4px 14px rgba(52,152,219,0.3)",
              }}
            >
              + Créer un salon
            </button>
          </div>
        )}
      </main>

      {/* ── ONLINE USERS PANEL ───────────────────────────────────────────────── */}
      <aside
        style={{
          width: "196px",
          flexShrink: 0,
          background: "#f8fafc",
          borderLeft: "1px solid #f1f5f9",
          display: "flex",
          flexDirection: "column",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            padding: "18px 16px 12px",
            borderBottom: "1px solid #f1f5f9",
          }}
        >
          <span style={{ fontSize: "11px", fontWeight: "800", color: "#94a3b8", letterSpacing: "0.08em", textTransform: "uppercase" }}>
            EN LIGNE
          </span>
          <span
            style={{
              marginLeft: "8px",
              background: "#22c55e",
              color: "white",
              borderRadius: "10px",
              padding: "1px 7px",
              fontSize: "10px",
              fontWeight: "700",
            }}
          >
            {onlineUsers.length}
          </span>
        </div>

        <div style={{ flex: 1, overflowY: "auto", padding: "8px" }}>
          {onlineUsers.length === 0 ? (
            <p style={{ fontSize: "12px", color: "#cbd5e1", textAlign: "center", padding: "16px 8px" }}>
              Aucun autre utilisateur connecté.
            </p>
          ) : (
            onlineUsers.map((u) => (
              <div
                key={u.keycloakId}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  padding: "7px 8px",
                  borderRadius: "8px",
                  marginBottom: "2px",
                }}
              >
                <div style={{ position: "relative" }}>
                  <AvatarBubble name={u.username} size={28} />
                  <span
                    style={{
                      position: "absolute",
                      bottom: 0,
                      right: 0,
                      width: "8px",
                      height: "8px",
                      borderRadius: "50%",
                      background: "#22c55e",
                      border: "2px solid #f8fafc",
                    }}
                  />
                </div>
                <div
                  style={{
                    overflow: "hidden",
                    flex: 1,
                  }}
                >
                  <div
                    style={{
                      fontSize: "12px",
                      fontWeight: "600",
                      color: u.username === myUsername ? "#3498db" : "#334155",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {u.username}
                    {u.username === myUsername && (
                      <span style={{ fontSize: "10px", color: "#94a3b8", marginLeft: "4px" }}>(moi)</span>
                    )}
                  </div>
                  {u.activeChannelId && (
                    <div style={{ fontSize: "10px", color: "#94a3b8" }}>
                      #{channels.find((c) => c.id === u.activeChannelId)?.name || "..."}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </aside>

      {/* ── Modal création salon ─────────────────────────────────────────────── */}
      {showModal && (
        <CreateChannelModal
          token={token}
          onClose={() => setShowModal(false)}
          onCreated={handleChannelCreated}
        />
      )}
    </div>
  );
}
