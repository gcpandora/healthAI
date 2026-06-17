import { useState } from "react";
import { useAuth } from "../contexts/AuthContext";

const PLANS = [
  { value: "freemium", name: "Freemium", subtitle: "Accès gratuit – fonctionnalités de base", price: "0 €/mois" },
  { value: "premium", name: "Premium", subtitle: "9,99 €/mois – recommandations IA, plans détaillés", price: "9,99 €/mois" },
  { value: "premiumPlus", name: "Premium+", subtitle: "19,99 €/mois – biométrie, consultation nutritionnistes", price: "19,99 €/mois" },
  { value: "b2b", name: "B2B", subtitle: "Marque blanche pour entreprise et mutuelles", price: "Sur devis" },
];

const GENDERS = [
  { value: "male", label: "Homme" },
  { value: "female", label: "Femme" },
  { value: "other", label: "Autre" },
];

export default function Account() {
  const { user, updateProfile, logout } = useAuth();
  const [form, setForm] = useState({
    first_name: user?.first_name || "",
    last_name: user?.last_name || "",
    email: user?.email || "",
    gender: user?.gender || "male",
    weight: user?.weight || "",
    height: user?.height || "",
    plan: user?.plan || "freemium",
  });
  const [status, setStatus] = useState(null);

  const change = (key, value) => setForm((p) => ({ ...p, [key]: value }));

  if (!user) {
    return (
      <div style={{ padding: "32px", background: "white", borderRadius: "12px", boxShadow: "0 2px 8px rgba(0,0,0,0.1)" }}>
        <h2>Mon compte</h2>
        <p>Vous devez être connecté pour accéder à votre profil.</p>
      </div>
    );
  }

  const submit = async (e) => {
    e.preventDefault();
    setStatus(null);

    const payload = {
      first_name: form.first_name,
      last_name: form.last_name,
      email: form.email,
      gender: form.gender,
      weight: Number(form.weight),
      height: Number(form.height),
      plan: form.plan,
    };

    const result = await updateProfile(payload);
    if (result.success) {
      setStatus({ type: "success", text: "Profil mis à jour." });
    } else {
      setStatus({ type: "error", text: result.error || "Échec de la mise à jour" });
    }
  };

  return (
    <div style={{ maxWidth: "900px", margin: "0 auto", padding: "24px" }}>
      <h1>Mon compte</h1>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginTop: "20px" }}>
        <form onSubmit={submit} style={{ background: "white", padding: "20px", borderRadius: "12px", boxShadow: "0 2px 8px rgba(0,0,0,0.08)" }}>
          <h3 style={{ marginBottom: "12px" }}>Informations personnelles</h3>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
            <input placeholder="Prénom" value={form.first_name} onChange={(e) => change("first_name", e.target.value)} required style={{ padding: "10px", border: "1px solid #d1d5db", borderRadius: "8px" }} />
            <input placeholder="Nom" value={form.last_name} onChange={(e) => change("last_name", e.target.value)} required style={{ padding: "10px", border: "1px solid #d1d5db", borderRadius: "8px" }} />
          </div>

          <input type="email" placeholder="Email" value={form.email} onChange={(e) => change("email", e.target.value)} required style={{ marginTop: "12px", padding: "10px", border: "1px solid #d1d5db", borderRadius: "8px" }} />

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", marginTop: "12px" }}>
            <input type="number" placeholder="Poids (kg)" value={form.weight} onChange={(e) => change("weight", e.target.value)} style={{ padding: "10px", border: "1px solid #d1d5db", borderRadius: "8px" }} />
            <input type="number" placeholder="Taille (cm)" value={form.height} onChange={(e) => change("height", e.target.value)} style={{ padding: "10px", border: "1px solid #d1d5db", borderRadius: "8px" }} />
          </div>

          <label style={{ display: "block", marginTop: "12px", marginBottom: "6px", fontWeight: "600" }}>Genre</label>
          <div style={{ display: "flex", gap: "8px" }}>
            {GENDERS.map((g) => (
              <button key={g.value} type="button" onClick={() => change("gender", g.value)} style={{ padding: "8px 12px", borderRadius: "8px", border: form.gender === g.value ? "2px solid #3498db" : "1px solid #d1d5db", background: form.gender === g.value ? "#eff6ff" : "white" }}>
                {g.label}
              </button>
            ))}
          </div>

          <label style={{ display: "block", marginTop: "16px", marginBottom: "6px", fontWeight: "600" }}>Abonnement</label>
          <select value={form.plan} onChange={(e) => change("plan", e.target.value)} style={{ width: "100%", padding: "10px", border: "1px solid #d1d5db", borderRadius: "8px" }}>
            {PLANS.map((plan) => (
              <option key={plan.value} value={plan.value}> {plan.name} ({plan.price}) </option>
            ))}
          </select>

          <button type="submit" style={{ marginTop: "18px", width: "100%", padding: "12px", border: "none", borderRadius: "10px", background: "#3498db", color: "white", fontWeight: "700", cursor: "pointer" }}>
            Enregistrer les modifications
          </button>

          {status && <p style={{ marginTop: "12px", color: status.type === "error" ? "#e74c3c" : "#2ecc71" }}>{status.text}</p>}
        </form>

        <div style={{ background: "white", padding: "20px", borderRadius: "12px", boxShadow: "0 2px 8px rgba(0,0,0,0.08)" }}>
          <h3 style={{ marginBottom: "12px" }}>Résumé de l'utilisateur</h3>
          <p><strong>Nom :</strong> {user?.first_name} {user?.last_name}</p>
          <p><strong>Email :</strong> {user?.email}</p>
          <p><strong>Genre :</strong> {user?.gender}</p>
          <p><strong>Poids :</strong> {user?.weight || "Non défini"} kg</p>
          <p><strong>Taille :</strong> {user?.height || "Non défini"} cm</p>
          <p><strong>Plan :</strong> {user?.plan || "freemium"}</p>

          <h4 style={{ marginTop: "16px" }}>Offres disponibles</h4>
          <ul>
            {PLANS.map((plan) => (
              <li key={plan.value} style={{ marginBottom: "8px" }}>
                <strong>{plan.name}</strong> ({plan.price}) - {plan.subtitle}
              </li>
            ))}
          </ul>

          <button onClick={logout} style={{ marginTop: "16px", width: "100%", padding: "10px", border: "none", borderRadius: "10px", background: "#e74c3c", color: "white", cursor: "pointer" }}>
            Se déconnecter
          </button>
        </div>
      </div>
    </div>
  );
}