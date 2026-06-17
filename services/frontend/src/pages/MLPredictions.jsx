import { useState } from "react";
import { mlAPI } from "../services/api";
import styles from "./MLPredictions.module.css";

// ── Barre de confiance ──────────────────────────────────────────────
function ConfidenceBar({ label, value, color }) {
  const pct = Math.round(value * 100);
  return (
    <div className={styles.bar}>
      <div className={styles.barLabel}>
        <span>{label}</span>
        <strong>{pct}%</strong>
      </div>
      <div className={styles.barTrack}>
        <div className={styles.barFill} style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  );
}

// ── Résultat diète ──────────────────────────────────────────────────
function DietResult({ data }) {
  const colors = { Balanced: "#10b981", Low_Carb: "#f59e0b", Low_Sodium: "#3b82f6" };
  const labels = { Balanced: "Régime équilibré", Low_Carb: "Pauvre en glucides", Low_Sodium: "Pauvre en sodium" };
  return (
    <div className={styles.resultCard}>
      <div className={styles.resultBadge} style={{ background: colors[data.diet_recommendation] ?? "#6366f1" }}>
        {labels[data.diet_recommendation] ?? data.diet_recommendation}
      </div>
      <p className={styles.confidence}>Confiance : <strong>{Math.round(data.confidence * 100)}%</strong></p>
      <div className={styles.bars}>
        {Object.entries(data.probabilities).map(([cls, val]) => (
          <ConfidenceBar key={cls} label={labels[cls] ?? cls} value={val} color={colors[cls] ?? "#6366f1"} />
        ))}
      </div>
      <p className={styles.source}>Modèle : {data.source}</p>
    </div>
  );
}

// ── Résultat fitness ────────────────────────────────────────────────
function FitnessResult({ data }) {
  const colors   = { "Débutant": "#10b981", "Intermédiaire": "#f59e0b", "Avancé": "#ef4444" };
  const icons    = { "Débutant": "🌱", "Intermédiaire": "💪", "Avancé": "🏆" };
  return (
    <div className={styles.resultCard}>
      <div className={styles.resultBadge} style={{ background: colors[data.label] ?? "#6366f1" }}>
        {icons[data.label]} {data.label}
      </div>
      <p className={styles.confidence}>Confiance : <strong>{Math.round(data.confidence * 100)}%</strong></p>
      <div className={styles.bars}>
        {Object.entries(data.probabilities).map(([cls, val]) => (
          <ConfidenceBar key={cls} label={cls} value={val} color={colors[cls] ?? "#6366f1"} />
        ))}
      </div>
      <p className={styles.source}>Modèle : {data.source}</p>
    </div>
  );
}

// ── Formulaire diète ────────────────────────────────────────────────
function DietForm() {
  const [form, setForm] = useState({
    age: "", gender: "Male", weight_kg: "", height_cm: "",
    physical_activity_level: "Moderate", weekly_exercise_hours: "", daily_caloric_intake: "",
  });
  const [status, setStatus] = useState("idle");
  const [result, setResult] = useState(null);
  const [error, setError]   = useState("");

  function set(k, v) { setForm(p => ({ ...p, [k]: v })); }

  async function submit(e) {
    e.preventDefault();
    setStatus("loading"); setError(""); setResult(null);
    try {
      const res = await mlAPI.predictDiet({
        age: Number(form.age), gender: form.gender,
        weight_kg: Number(form.weight_kg), height_cm: Number(form.height_cm),
        physical_activity_level: form.physical_activity_level,
        weekly_exercise_hours: Number(form.weekly_exercise_hours),
        daily_caloric_intake: Number(form.daily_caloric_intake),
      });
      setResult(res.data); setStatus("success");
    } catch {
      setError("Erreur lors de la prédiction. Vérifiez que le service AI-API tourne sur le port 8002.");
      setStatus("error");
    }
  }

  return (
    <div className={styles.tab}>
      <form onSubmit={submit} className={styles.form}>
        <div className={styles.row2}>
          <div className={styles.field}>
            <label>Âge</label>
            <input type="number" value={form.age} onChange={e => set("age", e.target.value)} min={18} max={100} placeholder="35" required />
          </div>
          <div className={styles.field}>
            <label>Genre</label>
            <select value={form.gender} onChange={e => set("gender", e.target.value)}>
              <option value="Male">Homme</option>
              <option value="Female">Femme</option>
            </select>
          </div>
        </div>
        <div className={styles.row2}>
          <div className={styles.field}>
            <label>Poids (kg)</label>
            <input type="number" step="0.1" value={form.weight_kg} onChange={e => set("weight_kg", e.target.value)} placeholder="80" required />
          </div>
          <div className={styles.field}>
            <label>Taille (cm)</label>
            <input type="number" value={form.height_cm} onChange={e => set("height_cm", e.target.value)} placeholder="175" required />
          </div>
        </div>
        <div className={styles.field}>
          <label>Niveau d'activité physique</label>
          <select value={form.physical_activity_level} onChange={e => set("physical_activity_level", e.target.value)}>
            <option value="Active">Actif</option>
            <option value="Moderate">Modéré</option>
            <option value="Sedentary">Sédentaire</option>
          </select>
        </div>
        <div className={styles.row2}>
          <div className={styles.field}>
            <label>Heures d'exercice / semaine</label>
            <input type="number" step="0.5" value={form.weekly_exercise_hours} onChange={e => set("weekly_exercise_hours", e.target.value)} placeholder="4" required />
          </div>
          <div className={styles.field}>
            <label>Apport calorique journalier</label>
            <input type="number" value={form.daily_caloric_intake} onChange={e => set("daily_caloric_intake", e.target.value)} placeholder="2200" required />
          </div>
        </div>
        <button type="submit" className={styles.btn} disabled={status === "loading"}>
          {status === "loading" ? "Analyse en cours…" : "🥗 Prédire mon régime"}
        </button>
      </form>
      {status === "error" && <p className={styles.error}>{error}</p>}
      {status === "success" && result && <DietResult data={result} />}
    </div>
  );
}

// ── Formulaire fitness ──────────────────────────────────────────────
function FitnessForm() {
  const [form, setForm] = useState({
    age: "", gender: "Male", weight_kg: "", height_m: "",
    max_bpm: "", avg_bpm: "", resting_bpm: "",
    session_duration_hours: "", calories_burned: "",
    fat_percentage: "", water_intake_liters: "", workout_frequency: "",
  });
  const [status, setStatus] = useState("idle");
  const [result, setResult] = useState(null);
  const [error, setError]   = useState("");

  function set(k, v) { setForm(p => ({ ...p, [k]: v })); }

  async function submit(e) {
    e.preventDefault();
    setStatus("loading"); setError(""); setResult(null);
    try {
      const res = await mlAPI.predictFitnessLevel({
        age: Number(form.age), gender: form.gender,
        weight_kg: Number(form.weight_kg), height_m: Number(form.height_m),
        max_bpm: Number(form.max_bpm), avg_bpm: Number(form.avg_bpm),
        resting_bpm: Number(form.resting_bpm),
        session_duration_hours: Number(form.session_duration_hours),
        calories_burned: Number(form.calories_burned),
        fat_percentage: Number(form.fat_percentage),
        water_intake_liters: Number(form.water_intake_liters),
        workout_frequency: Number(form.workout_frequency),
      });
      setResult(res.data); setStatus("success");
    } catch {
      setError("Erreur lors de la prédiction. Vérifiez que le service AI-API tourne sur le port 8002.");
      setStatus("error");
    }
  }

  return (
    <div className={styles.tab}>
      <form onSubmit={submit} className={styles.form}>
        <div className={styles.row2}>
          <div className={styles.field}>
            <label>Âge</label>
            <input type="number" value={form.age} onChange={e => set("age", e.target.value)} placeholder="28" required />
          </div>
          <div className={styles.field}>
            <label>Genre</label>
            <select value={form.gender} onChange={e => set("gender", e.target.value)}>
              <option value="Male">Homme</option>
              <option value="Female">Femme</option>
            </select>
          </div>
        </div>
        <div className={styles.row2}>
          <div className={styles.field}>
            <label>Poids (kg)</label>
            <input type="number" step="0.1" value={form.weight_kg} onChange={e => set("weight_kg", e.target.value)} placeholder="70" required />
          </div>
          <div className={styles.field}>
            <label>Taille (m)</label>
            <input type="number" step="0.01" value={form.height_m} onChange={e => set("height_m", e.target.value)} placeholder="1.75" required />
          </div>
        </div>
        <div className={styles.row3}>
          <div className={styles.field}>
            <label>BPM max</label>
            <input type="number" value={form.max_bpm} onChange={e => set("max_bpm", e.target.value)} placeholder="180" required />
          </div>
          <div className={styles.field}>
            <label>BPM moyen</label>
            <input type="number" value={form.avg_bpm} onChange={e => set("avg_bpm", e.target.value)} placeholder="145" required />
          </div>
          <div className={styles.field}>
            <label>BPM repos</label>
            <input type="number" value={form.resting_bpm} onChange={e => set("resting_bpm", e.target.value)} placeholder="60" required />
          </div>
        </div>
        <div className={styles.row2}>
          <div className={styles.field}>
            <label>Durée séance (h)</label>
            <input type="number" step="0.25" value={form.session_duration_hours} onChange={e => set("session_duration_hours", e.target.value)} placeholder="1.0" required />
          </div>
          <div className={styles.field}>
            <label>Calories brûlées / séance</label>
            <input type="number" value={form.calories_burned} onChange={e => set("calories_burned", e.target.value)} placeholder="500" required />
          </div>
        </div>
        <div className={styles.row3}>
          <div className={styles.field}>
            <label>% graisse corporelle</label>
            <input type="number" step="0.1" value={form.fat_percentage} onChange={e => set("fat_percentage", e.target.value)} placeholder="20" required />
          </div>
          <div className={styles.field}>
            <label>Eau / jour (L)</label>
            <input type="number" step="0.1" value={form.water_intake_liters} onChange={e => set("water_intake_liters", e.target.value)} placeholder="2.5" required />
          </div>
          <div className={styles.field}>
            <label>Séances / semaine</label>
            <input type="number" step="0.5" value={form.workout_frequency} onChange={e => set("workout_frequency", e.target.value)} placeholder="4" required />
          </div>
        </div>
        <button type="submit" className={styles.btn} disabled={status === "loading"}>
          {status === "loading" ? "Analyse en cours…" : "🏋️ Prédire mon niveau"}
        </button>
      </form>
      {status === "error" && <p className={styles.error}>{error}</p>}
      {status === "success" && result && <FitnessResult data={result} />}
    </div>
  );
}

// ── Page principale ─────────────────────────────────────────────────
export default function MLPredictions() {
  const [activeTab, setActiveTab] = useState("diet");

  return (
    <main className={styles.page}>
      <header className={styles.pageHeader}>
        <h1 className={styles.pageTitle}>Prédictions ML</h1>
        <p className={styles.pageSubtitle}>
          Modèles Random Forest entraînés sur données réelles — Houssem (ml2)
        </p>
      </header>

      <div className={styles.tabs}>
        <button
          className={`${styles.tabBtn} ${activeTab === "diet" ? styles.tabActive : ""}`}
          onClick={() => setActiveTab("diet")}
        >
          🥗 Recommandation diététique
        </button>
        <button
          className={`${styles.tabBtn} ${activeTab === "fitness" ? styles.tabActive : ""}`}
          onClick={() => setActiveTab("fitness")}
        >
          🏋️ Niveau d'expérience fitness
        </button>
      </div>

      {activeTab === "diet"    && <DietForm />}
      {activeTab === "fitness" && <FitnessForm />}
    </main>
  );
}
