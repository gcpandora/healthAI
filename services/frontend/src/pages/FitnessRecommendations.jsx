import { useState, useRef, useEffect, useId } from "react";
import { recommendationsAPI } from "../services/api";
import styles from "./FitnessRecommendations.module.css";

const TIMEOUT_MS = 30_000;

const OBJECTIVES = [
  { value: "weight_loss",    label: "Perte de poids" },
  { value: "muscle_gain",   label: "Prise de masse" },
  { value: "endurance",     label: "Endurance / cardio" },
  { value: "flexibility",   label: "Souplesse / mobilité" },
  { value: "general_health",label: "Forme générale" },
];

const EXPERIENCE_LEVELS = [
  { value: 1, label: "Débutant (< 6 mois)" },
  { value: 2, label: "Intermédiaire (6 mois – 2 ans)" },
  { value: 3, label: "Avancé (> 2 ans)" },
];

const LIMITATIONS_OPTIONS = [
  "Dos / colonne vertébrale","Genoux","Épaules","Hanches","Chevilles","Poignets","Problème cardiovasculaire",
];

const EQUIPMENT_OPTIONS = [
  "Haltères","Barre de traction","Kettlebell","Élastiques","Tapis de yoga","Vélo / rameur","Accès salle de sport",
];

const INITIAL_FORM = {
  objective: "general_health",
  age: "",
  gender: "Male",
  weight_kg: "",
  height_m: "",
  experience_level: 1,
  limitations: [],
  equipment: [],
};

function validateForm(form) {
  const errors = {};
  if (!form.age || form.age < 13 || form.age > 100) errors.age = "Âge invalide (13–100 ans)";
  if (!form.weight_kg || form.weight_kg < 30 || form.weight_kg > 300) errors.weight_kg = "Poids invalide (30–300 kg)";
  if (!form.height_m || form.height_m < 1.0 || form.height_m > 2.5) errors.height_m = "Taille invalide (1,00–2,50 m)";
  return errors;
}

function CheckGroup({ legend, options, selected, onChange }) {
  return (
    <fieldset className={styles.fieldset}>
      <legend className={styles.fieldsetLegend}>{legend}</legend>
      <div className={styles.checkGrid}>
        {options.map((opt) => {
          const val = typeof opt === "object" ? opt.value : opt;
          const lbl = typeof opt === "object" ? opt.label : opt;
          const checked = selected.includes(val);
          return (
            <label key={val} className={`${styles.checkLabel} ${checked ? styles.checkLabelActive : ""}`}>
              <input
                type="checkbox"
                className={styles.srOnly}
                checked={checked}
                onChange={() => onChange(checked ? selected.filter((v) => v !== val) : [...selected, val])}
              />
              <span aria-hidden="true">{checked ? "✓ " : ""}</span>
              {lbl}
            </label>
          );
        })}
      </div>
    </fieldset>
  );
}

function SkeletonPlan() {
  return (
    <div className={styles.skeleton} aria-busy="true" aria-label="Génération du programme en cours…">
      {[100, 60, 80, 50, 90, 70, 55].map((w, i) => (
        <div key={i} className={styles.skeletonLine} style={{ width: `${w}%` }} />
      ))}
    </div>
  );
}

function WorkoutSession({ session, index }) {
  return (
    <article className={styles.sessionCard} aria-label={`Séance ${index + 1}`}>
      <header className={styles.sessionHeader}>
        <span className={styles.sessionNumber} aria-hidden="true">{index + 1}</span>
        <div>
          <h3 className={styles.sessionTitle}>{session.name || `Séance ${index + 1}`}</h3>
          {session.duration_min && (
            <p className={styles.sessionMeta}>⏱ {session.duration_min} min{session.intensity && ` · Intensité : ${session.intensity}`}</p>
          )}
        </div>
      </header>
      {session.exercises?.length > 0 && (
        <ul className={styles.exerciseList} aria-label={`Exercices de la séance ${index + 1}`}>
          {session.exercises.map((ex, j) => (
            <li key={j} className={styles.exerciseItem}>
              <span className={styles.exerciseName}>{ex.name}</span>
              {ex.sets && ex.reps && <span className={styles.exerciseMeta}>{ex.sets}×{ex.reps}</span>}
              {ex.duration_sec && <span className={styles.exerciseMeta}>{ex.duration_sec}s</span>}
              {ex.rest_sec && <span className={styles.exerciseRest}>Repos : {ex.rest_sec}s</span>}
            </li>
          ))}
        </ul>
      )}
      {session.notes && <p className={styles.sessionNotes}>💡 {session.notes}</p>}
    </article>
  );
}

function ProgramResult({ data, isFallback }) {
  return (
    <section className={styles.resultSection} aria-labelledby="program-title">
      <div className={styles.resultHeader}>
        <h2 id="program-title" className={styles.resultTitle}>Votre programme personnalisé</h2>
        {isFallback && <span className={styles.fallbackBadge} role="alert">⚠ Mode dégradé — moteur IA indisponible</span>}
      </div>
      {data.summary && (
        <div className={styles.summaryBox}>
          <p className={styles.summaryText}>{data.summary}</p>
        </div>
      )}
      {(data.weekly_sessions || data.estimated_calories_burn || data.program_duration_weeks) && (
        <div className={styles.statsGrid} aria-label="Statistiques du programme">
          {data.weekly_sessions && (
            <div className={styles.statCard}>
              <strong className={styles.statValue}>{data.weekly_sessions}</strong>
              <span className={styles.statLabel}>séances/semaine</span>
            </div>
          )}
          {data.estimated_calories_burn && (
            <div className={styles.statCard}>
              <strong className={styles.statValue}>{data.estimated_calories_burn}</strong>
              <span className={styles.statLabel}>kcal/semaine estimées</span>
            </div>
          )}
          {data.program_duration_weeks && (
            <div className={styles.statCard}>
              <strong className={styles.statValue}>{data.program_duration_weeks}</strong>
              <span className={styles.statLabel}>semaines</span>
            </div>
          )}
        </div>
      )}
      {data.sessions?.length > 0 ? (
        <div className={styles.sessionsList}>
          {data.sessions.map((session, i) => <WorkoutSession key={i} session={session} index={i} />)}
        </div>
      ) : data.recommendations && (
        <div className={styles.rawRecommendations}>
          {Array.isArray(data.recommendations)
            ? data.recommendations.map((r, i) => <p key={i}>{r}</p>)
            : <p>{data.recommendations}</p>}
        </div>
      )}
      {data.recommendation_id && (
        <p className={styles.recId}>
          ID : <code>{data.recommendation_id}</code>
          {data.stored_in && <span className={styles.storageBadge}> · stocké dans {data.stored_in}</span>}
        </p>
      )}
    </section>
  );
}

export default function FitnessRecommendations() {
  const [form, setForm]         = useState(INITIAL_FORM);
  const [errors, setErrors]     = useState({});
  const [status, setStatus]     = useState("idle");
  const [result, setResult]     = useState(null);
  const [apiError, setApiError] = useState("");
  const [fallback, setFallback] = useState(false);
  const abortRef = useRef(null);
  useEffect(() => () => abortRef.current?.abort(), []);

  function setField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: "" }));
  }

  async function handleSubmit(e) {
    e?.preventDefault();
    if (status === "loading") return;
    const validationErrors = validateForm(form);
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      document.querySelector("[aria-invalid='true']")?.focus();
      return;
    }
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setStatus("loading");
    setApiError("");
    setFallback(false);
    setResult(null);
    try {
      const response = await recommendationsAPI.getRecommendations(
        {
          objective: form.objective,
          age: Number(form.age),
          gender: form.gender,
          weight_kg: Number(form.weight_kg),
          height_m: Number(form.height_m),
          experience_level: Number(form.experience_level),
          limitations: form.limitations,
          equipment: form.equipment,
        },
        { signal: controller.signal, timeout: TIMEOUT_MS }
      );
      setResult(response.data);
      setFallback(response.data.fallback_used ?? false);
      setStatus("success");
    } catch (err) {
      if (err.name === "CanceledError" || err.name === "AbortError") return;
      setStatus("error");
      setApiError(
        err.code === "ECONNABORTED" || err.message?.includes("timeout")
          ? "Le moteur de recommandations met trop de temps à répondre (>30 s)."
          : err.response?.data?.detail || "Erreur lors de la génération du programme."
      );
    }
  }

  function handleReset() {
    setForm(INITIAL_FORM);
    setErrors({});
    setStatus("idle");
    setResult(null);
    setApiError("");
  }

  const formId = useId();

  return (
    <main className={styles.page}>
      <header className={styles.pageHeader}>
        <h1 className={styles.pageTitle}>Recommandations fitness IA</h1>
        <p className={styles.pageSubtitle}>
          Renseignez votre profil pour recevoir un programme d'entraînement personnalisé généré par IA et stocké dans MongoDB.
        </p>
      </header>
      <div className={styles.layout}>
        <section className={styles.formSection} aria-labelledby="form-title">
          <h2 id="form-title" className={styles.sectionHeading}>Votre profil</h2>
          <form id={`${formId}-form`} onSubmit={handleSubmit} noValidate aria-label="Formulaire de profil fitness" className={styles.form}>
            <div className={styles.fieldGroup}>
              <label htmlFor={`${formId}-objective`} className={styles.label}>
                Objectif <span aria-hidden="true" className={styles.required}>*</span>
              </label>
              <select id={`${formId}-objective`} className={styles.select} value={form.objective} onChange={(e) => setField("objective", e.target.value)}>
                {OBJECTIVES.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
              </select>
            </div>
            <div className={styles.row2}>
              <div className={styles.fieldGroup}>
                <label htmlFor={`${formId}-age`} className={styles.label}>
                  Âge <span aria-hidden="true" className={styles.required}>*</span>
                </label>
                <input
                  id={`${formId}-age`} type="number"
                  className={`${styles.input} ${errors.age ? styles.inputError : ""}`}
                  value={form.age} onChange={(e) => setField("age", e.target.value)}
                  min={13} max={100} required aria-invalid={!!errors.age}
                  aria-describedby={errors.age ? `${formId}-age-error` : undefined}
                  placeholder="ex: 28"
                />
                {errors.age && <span id={`${formId}-age-error`} className={styles.fieldError} role="alert">{errors.age}</span>}
              </div>
              <div className={styles.fieldGroup}>
                <fieldset className={styles.inlineFieldset}>
                  <legend className={styles.label}>Genre <span aria-hidden="true" className={styles.required}>*</span></legend>
                  <div className={styles.radioGroup}>
                    {["Male", "Female"].map((g) => (
                      <label key={g} className={`${styles.radioLabel} ${form.gender === g ? styles.radioActive : ""}`}>
                        <input type="radio" name={`${formId}-gender`} value={g} checked={form.gender === g} onChange={() => setField("gender", g)} className={styles.srOnly} />
                        {g === "Male" ? "Homme" : "Femme"}
                      </label>
                    ))}
                  </div>
                </fieldset>
              </div>
            </div>
            <div className={styles.row2}>
              <div className={styles.fieldGroup}>
                <label htmlFor={`${formId}-weight`} className={styles.label}>
                  Poids (kg) <span aria-hidden="true" className={styles.required}>*</span>
                </label>
                <input
                  id={`${formId}-weight`} type="number" step="0.1"
                  className={`${styles.input} ${errors.weight_kg ? styles.inputError : ""}`}
                  value={form.weight_kg} onChange={(e) => setField("weight_kg", e.target.value)}
                  min={30} max={300} required aria-invalid={!!errors.weight_kg}
                  aria-describedby={errors.weight_kg ? `${formId}-weight-error` : undefined}
                  placeholder="ex: 70"
                />
                {errors.weight_kg && <span id={`${formId}-weight-error`} className={styles.fieldError} role="alert">{errors.weight_kg}</span>}
              </div>
              <div className={styles.fieldGroup}>
                <label htmlFor={`${formId}-height`} className={styles.label}>
                  Taille (m) <span aria-hidden="true" className={styles.required}>*</span>
                </label>
                <input
                  id={`${formId}-height`} type="number" step="0.01"
                  className={`${styles.input} ${errors.height_m ? styles.inputError : ""}`}
                  value={form.height_m} onChange={(e) => setField("height_m", e.target.value)}
                  min={1.0} max={2.5} required aria-invalid={!!errors.height_m}
                  aria-describedby={errors.height_m ? `${formId}-height-error` : undefined}
                  placeholder="ex: 1.75"
                />
                {errors.height_m && <span id={`${formId}-height-error`} className={styles.fieldError} role="alert">{errors.height_m}</span>}
              </div>
            </div>
            <div className={styles.fieldGroup}>
              <label htmlFor={`${formId}-exp`} className={styles.label}>Niveau d'expérience</label>
              <select id={`${formId}-exp`} className={styles.select} value={form.experience_level} onChange={(e) => setField("experience_level", Number(e.target.value))}>
                {EXPERIENCE_LEVELS.map((l) => <option key={l.value} value={l.value}>{l.label}</option>)}
              </select>
            </div>
            <CheckGroup legend="Limitations physiques (optionnel)" options={LIMITATIONS_OPTIONS} selected={form.limitations} onChange={(v) => setField("limitations", v)} />
            <CheckGroup legend="Équipement disponible (optionnel)" options={EQUIPMENT_OPTIONS} selected={form.equipment} onChange={(v) => setField("equipment", v)} />
            <div className={styles.formActions}>
              <button type="submit" className={styles.btnPrimary} disabled={status === "loading"} aria-busy={status === "loading"}>
                {status === "loading" ? <><span className={styles.spinner} aria-hidden="true" /> Génération en cours…</> : "💪 Générer mon programme"}
              </button>
              {(status !== "idle" || result) && (
                <button type="button" className={styles.btnSecondary} onClick={handleReset}>Réinitialiser</button>
              )}
            </div>
          </form>
        </section>
        <div className={styles.resultsSection}>
          {status === "idle" && !result && (
            <div className={styles.emptyState} aria-label="En attente de génération">
              <span className={styles.emptyIcon} aria-hidden="true">💪</span>
              <p>Remplissez votre profil et cliquez sur « Générer mon programme »</p>
              <p className={styles.emptyHint}>Le programme est stocké dans MongoDB et personnalisé par IA</p>
            </div>
          )}
          {status === "loading" && <SkeletonPlan />}
          {status === "error" && (
            <div className={styles.alertError} role="alert" aria-live="assertive">
              <strong>❌ Erreur</strong>
              <p>{apiError}</p>
              <p className={styles.fallbackNote}>Vérifiez que le micro-service de recommandations est bien démarré sur le port 8001.</p>
            </div>
          )}
          {status === "success" && result && <ProgramResult data={result} isFallback={fallback} />}
        </div>
      </div>
    </main>
  );
}
