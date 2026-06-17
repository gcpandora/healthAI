import { useState } from "react";
import { useAuth } from "../contexts/AuthContext";

const PAYMENT_PLANS = [
  {
    value: "freemium",
    label: "Freemium - gratuit (journal, activité, IMC, tableaux simples)",
    price: "0€/mois",
  },
  {
    value: "premium",
    label: "Premium - 9,99€/mois (recommandations IA, plans nutrition/sportifs)",
    price: "9,99€/mois",
  },
  {
    value: "premiumPlus",
    label: "Premium+ - 19,99€/mois (biométrie, consultations nutritionnistes)",
    price: "19,99€/mois",
  },
  {
    value: "b2b",
    label: "B2B - marque blanche (salles de sport, mutuelles, entreprises)",
    price: "Contact",
  },
];

const GENDERS = [
  { value: "male", label: "Homme" },
  { value: "female", label: "Femme" },
  { value: "other", label: "Autre" },
];

export default function AuthModal({ isOpen, onClose }) {
  const { login, register } = useAuth();
  const [mode, setMode] = useState("login");
  const [status, setStatus] = useState(null);

  const [form, setForm] = useState({
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    gender: "male",
    weight: "",
    height: "",
    plan: "freemium",
  });

  const changeForm = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const submit = async (event) => {
    event.preventDefault();
    setStatus(null);

    if (mode === "login") {
      const result = await login(form.email, form.password);
      if (result.success) {
        setStatus({ type: "success", text: "Connexion réussie" });
        onClose();
      } else {
        setStatus({ type: "error", text: result.error || "Échec de connexion" });
      }
      return;
    }

    // register
    const payload = {
      first_name: form.first_name,
      last_name: form.last_name,
      email: form.email,
      password: form.password,
      gender: form.gender,
      weight: Number(form.weight),
      height: Number(form.height),
      plan: form.plan,
    };

    const result = await register(payload);
    if (result.success) {
      setStatus({ type: "success", text: "Inscription réussie" });
      setMode("login");
      onClose();
    } else {
      setStatus({ type: "error", text: result.error || "Échec de l'inscription" });
    }
  };

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,0.35)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        zIndex: 2000,
      }}
      onClick={onClose}
    >
      <div
        style={{
          width: "min(580px, 90vw)",
          background: "white",
          borderRadius: "12px",
          boxShadow: "0 8px 30px rgba(0,0,0,0.18)",
          overflow: "hidden",
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ padding: "20px 24px", borderBottom: "1px solid #e5e7eb", textAlign: "center" }}>
          <h3 style={{ margin: "0 0 10px 0" }}>{mode === "login" ? "Connexion" : "Créer un compte"}</h3>
          <p style={{ margin: 0, color: "#6b7280" }}>
            {mode === "login" ? "Connectez-vous pour accéder à HealthAI" : "Complétez le formulaire pour créer un compte"}
          </p>
          <button onClick={onClose} style={{ position: "absolute", top: "16px", right: "16px", background: "none", border: "none", fontSize: "18px", cursor: "pointer" }}>✕</button>
        </div>

        <div style={{ padding: "20px 24px" }}>

          <form onSubmit={submit} style={{ display: "grid", gap: "12px" }}>
            {mode === "register" && (
              <>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                  <input
                    placeholder="Prénom"
                    value={form.first_name}
                    onChange={(e) => changeForm("first_name", e.target.value)}
                    required
                    style={{ padding: "10px", border: "1px solid #d1d5db", borderRadius: "8px" }}
                  />
                  <input
                    placeholder="Nom"
                    value={form.last_name}
                    onChange={(e) => changeForm("last_name", e.target.value)}
                    required
                    style={{ padding: "10px", border: "1px solid #d1d5db", borderRadius: "8px" }}
                  />
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                  <input
                    placeholder="Poids (kg)"
                    type="number"
                    min="20"
                    max="300"
                    value={form.weight}
                    onChange={(e) => changeForm("weight", e.target.value)}
                    required
                    style={{ padding: "10px", border: "1px solid #d1d5db", borderRadius: "8px" }}
                  />
                  <input
                    placeholder="Taille (cm)"
                    type="number"
                    min="80"
                    max="250"
                    value={form.height}
                    onChange={(e) => changeForm("height", e.target.value)}
                    required
                    style={{ padding: "10px", border: "1px solid #d1d5db", borderRadius: "8px" }}
                  />
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "10px" }}>
                  {GENDERS.map((g) => (
                    <button
                      key={g.value}
                      type="button"
                      onClick={() => changeForm("gender", g.value)}
                      style={{
                        padding: "10px",
                        border: form.gender === g.value ? "2px solid #3498db" : "1px solid #d1d5db",
                        borderRadius: "8px",
                        background: form.gender === g.value ? "#eaf4ff" : "white",
                        cursor: "pointer",
                      }}
                    >
                      {g.label}
                    </button>
                  ))}
                </div>

                <div>
                  <label style={{ display: "block", marginBottom: "6px", fontSize: "12px", color: "#6b7280" }}>
                    Offre
                  </label>
                  <select
                    value={form.plan}
                    onChange={(e) => changeForm("plan", e.target.value)}
                    required
                    style={{ width: "100%", padding: "10px", border: "1px solid #d1d5db", borderRadius: "8px" }}
                  >
                    {PAYMENT_PLANS.map((plan) => (
                      <option key={plan.value} value={plan.value}>
                        {plan.label}
                      </option>
                    ))}
                  </select>
                </div>
              </>
            )}

            <input
              placeholder="Email"
              type="email"
              value={form.email}
              onChange={(e) => changeForm("email", e.target.value)}
              required
              style={{ padding: "10px", border: "1px solid #d1d5db", borderRadius: "8px" }}
            />
            <input
              placeholder="Mot de passe"
              type="password"
              value={form.password}
              onChange={(e) => changeForm("password", e.target.value)}
              required
              style={{ padding: "10px", border: "1px solid #d1d5db", borderRadius: "8px" }}
            />

            <button
              type="submit"
              style={{
                padding: "12px",
                border: "none",
                borderRadius: "8px",
                background: "#3498db",
                color: "white",
                fontWeight: "700",
                cursor: "pointer",
              }}
            >
              {mode === "login" ? "Se connecter" : "Créer mon compte"}
            </button>
          </form>

          {status && (
            <p style={{ marginTop: "12px", color: status.type === "error" ? "#e74c3c" : "#2ecc71" }}>
              {status.text}
            </p>
          )}

          {mode === "login" ? (
            <p style={{ marginTop: "16px", color: "#6b7280", fontSize: "12px" }}>
              Pas encore de compte ? <button type="button" onClick={() => setMode("register")} style={{ border: "none", background: "none", color: "#3498db", cursor: "pointer" }}>Créez-en un</button>
            </p>
          ) : (
            <p style={{ marginTop: "16px", color: "#6b7280", fontSize: "12px" }}>
              Déjà inscrit(e) ? <button type="button" onClick={() => setMode("login")} style={{ border: "none", background: "none", color: "#3498db", cursor: "pointer" }}>Connectez-vous</button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}