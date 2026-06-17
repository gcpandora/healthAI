import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export default function Login() {
  const { login, register } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const from = location.state?.from?.pathname || "/";

  const [mode, setMode] = useState("login");
  const [forgotPassword, setForgotPassword] = useState(false);
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

  const updateForm = (field, value) => setForm((p) => ({ ...p, [field]: value }));

  const submit = async (event) => {
    event.preventDefault();
    setStatus(null);

    if (mode === "login") {
      if (forgotPassword) {
        setStatus({ type: "success", text: "Lien de récupération envoyé (mock)." });
        return;
      }

      const response = await login(form.email, form.password);
      if (response.success) {
        navigate(from, { replace: true });
      } else {
        setStatus({ type: "error", text: response.error });
      }
      return;
    }

    const response = await register(form);
    if (response.success) {
      setStatus({ type: "success", text: "Inscription réussie !" });
      setMode("login");
      setForgotPassword(false);
    } else {
      setStatus({ type: "error", text: response.error });
    }
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", justifyContent: "center", alignItems: "center", background: "#f4f6f9", padding: "20px" }}>
      <div style={{ width: "100%", maxWidth: "500px", background: "white", borderRadius: "14px", boxShadow: "0 6px 25px rgba(0,0,0,0.12)", padding: "24px" }}>
        <h2 style={{ marginBottom: "8px" }}>{mode === "login" ? "Connexion" : "Créer un compte"}</h2>
        <p style={{ color: "#6b7280", marginBottom: "20px" }}>
          {mode === "login" ? "Connectez-vous pour accéder à HealthAI" : "Complétez le formulaire pour créer un compte"}
        </p>
        <div style={{ display: "flex", gap: "8px", marginBottom: "20px" }}>
          <button type="button" onClick={() => { setMode("login"); setForgotPassword(false); }} style={{ flex: 1, padding: "10px", borderRadius: "8px", border: mode === "login" ? "2px solid #3498db" : "1px solid #d1d5db", background: mode === "login" ? "#ebf5ff" : "white" }}>
            Connexion
          </button>
          <button type="button" onClick={() => { setMode("register"); setForgotPassword(false); }} style={{ flex: 1, padding: "10px", borderRadius: "8px", border: mode === "register" ? "2px solid #3498db" : "1px solid #d1d5db", background: mode === "register" ? "#ebf5ff" : "white" }}>
            Créer un compte
          </button>
        </div>

        <form onSubmit={submit} style={{ display: "grid", gap: "12px" }}>
          {mode === "register" && (
            <>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                <input value={form.first_name} onChange={(e) => updateForm("first_name", e.target.value)} placeholder="Prénom" required style={{ padding: "10px", borderRadius: "8px", border: "1px solid #d1d5db" }} />
                <input value={form.last_name} onChange={(e) => updateForm("last_name", e.target.value)} placeholder="Nom" required style={{ padding: "10px", borderRadius: "8px", border: "1px solid #d1d5db" }} />
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
                <input value={form.weight} onChange={(e) => updateForm("weight", e.target.value)} type="number" placeholder="Poids (kg)" required style={{ padding: "10px", borderRadius: "8px", border: "1px solid #d1d5db" }} />
                <input value={form.height} onChange={(e) => updateForm("height", e.target.value)} type="number" placeholder="Taille (cm)" required style={{ padding: "10px", borderRadius: "8px", border: "1px solid #d1d5db" }} />
              </div>

              <div style={{ display: "flex", gap: "8px" }}>
                <select value={form.gender} onChange={(e) => updateForm("gender", e.target.value)} style={{ flex: 1, padding: "10px", borderRadius: "8px", border: "1px solid #d1d5db" }}>
                  <option value="male">Homme</option>
                  <option value="female">Femme</option>
                  <option value="other">Autre</option>
                </select>
                <select value={form.plan} onChange={(e) => updateForm("plan", e.target.value)} style={{ flex: 1, padding: "10px", borderRadius: "8px", border: "1px solid #d1d5db" }}>
                  <option value="freemium">Freemium - 0€/mois</option>
                  <option value="premium">Premium - 9,99€/mois</option>
                  <option value="premiumPlus">Premium+ - 19,99€/mois</option>
                  <option value="b2b">B2B - marque blanche</option>
                </select>
              </div>
            </>
          )}

          <input value={form.email} onChange={(e) => updateForm("email", e.target.value)} placeholder="Email" type="email" required style={{ padding: "10px", borderRadius: "8px", border: "1px solid #d1d5db" }} />
          <input value={form.password} onChange={(e) => updateForm("password", e.target.value)} placeholder="Mot de passe" type="password" required style={{ padding: "10px", borderRadius: "8px", border: "1px solid #d1d5db" }} />

          {mode === "login" && (
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <label style={{ display: "flex", alignItems: "center", gap: "6px", fontSize: "14px", cursor: "pointer" }}>
                <input type="checkbox" checked={forgotPassword} onChange={(e) => setForgotPassword(e.target.checked)} />
                Mot de passe oublié
              </label>
            </div>
          )}

          <button type="submit" style={{ padding: "12px", borderRadius: "8px", border: "none", background: "#3498db", color: "white", fontWeight: "700", cursor: "pointer" }}>
            {mode === "login" ? (forgotPassword ? "Réinitialiser le mot de passe" : "Se connecter") : "Créer mon compte"}
          </button>
        </form>

        {status && <p style={{ marginTop: "14px", color: status.type === "error" ? "#e74c3c" : "#2ecc71" }}>{status.text}</p>}

        <p style={{ marginTop: "16px", color: "#6b7280", fontSize: "14px" }}>
          {mode === "login" ? "Pas encore de compte ?" : "Déjà inscrit ?"}
          <button onClick={() => { setMode((m) => (m === "login" ? "register" : "login")); setStatus(null); setForgotPassword(false); }} style={{ marginLeft: "8px", background: "none", border: "none", color: "#3498db", cursor: "pointer", fontWeight: "700" }}>
            {mode === "login" ? "Créer un compte" : "Se connecter"}
          </button>
        </p>
      </div>
    </div>
  );
}