import { useState, useCallback, useRef, useEffect } from "react";
import { visionAPI } from "../services/api";
import styles from "./NutritionAI.module.css";

const MAX_FILE_SIZE_MB = 5;
const ACCEPTED_TYPES = ["image/jpeg", "image/png", "image/webp", "image/gif"];
const TIMEOUT_MS = 30_000;

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(",")[1]);
    reader.onerror = () => reject(new Error("Lecture fichier échouée"));
    reader.readAsDataURL(file);
  });
}

function MacroBar({ label, value, unit, color, max }) {
  const pct = Math.min(100, Math.round((value / max) * 100));
  return (
    <div className={styles.macroBar} role="meter" aria-valuenow={value} aria-valuemin={0} aria-valuemax={max} aria-label={`${label} : ${value} ${unit}`}>
      <div className={styles.macroLabel}>
        <span>{label}</span>
        <strong>{value} {unit}</strong>
      </div>
      <div className={styles.macroTrack} aria-hidden="true">
        <div className={styles.macroFill} style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  );
}

function BalanceBadge({ balance }) {
  const map = {
    balanced:        { label: "Équilibré ✓",         cls: styles.badgeGreen },
    protein_deficit: { label: "Déficit protéines ↓", cls: styles.badgeOrange },
    carb_excess:     { label: "Excès glucides ↑",    cls: styles.badgeRed },
  };
  const { label, cls } = map[balance] ?? { label: balance, cls: styles.badgeGray };
  return <span className={`${styles.badge} ${cls}`} role="status">{label}</span>;
}

function SkeletonResult() {
  return (
    <div className={styles.skeleton} aria-busy="true" aria-label="Analyse en cours…">
      {[140, 80, 100, 60, 80].map((w, i) => (
        <div key={i} className={styles.skeletonLine} style={{ width: `${w}%` }} />
      ))}
    </div>
  );
}

export default function NutritionAI() {
  const [dragActive, setDragActive] = useState(false);
  const [preview, setPreview]       = useState(null);
  const [file, setFile]             = useState(null);
  const [fileError, setFileError]   = useState("");
  const [status, setStatus]         = useState("idle");
  const [result, setResult]         = useState(null);
  const [apiError, setApiError]     = useState("");
  const [fallback, setFallback]     = useState(false);
  const [remaining, setRemaining]   = useState(null);
  const [historyId, setHistoryId]   = useState("");
  const [historyResult, setHistoryResult] = useState(null);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [historyError, setHistoryError]     = useState("");
  const abortRef = useRef(null);

  useEffect(() => () => abortRef.current?.abort(), []);

  function validateFile(f) {
    if (!ACCEPTED_TYPES.includes(f.type))
      return `Format non supporté. Formats acceptés : JPG, PNG, WEBP, GIF.`;
    if (f.size > MAX_FILE_SIZE_MB * 1024 * 1024)
      return `Fichier trop lourd (max ${MAX_FILE_SIZE_MB} Mo). Le vôtre fait ${(f.size / 1024 / 1024).toFixed(1)} Mo.`;
    return null;
  }

  function handleFile(f) {
    setFileError("");
    const err = validateFile(f);
    if (err) { setFileError(err); return; }
    setFile(f);
    setPreview(URL.createObjectURL(f));
    setResult(null);
    setStatus("idle");
  }

  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    const dropped = e.dataTransfer.files?.[0];
    if (dropped) handleFile(dropped);
  }, []);

  const handleInputChange = (e) => {
    const selected = e.target.files?.[0];
    if (selected) handleFile(selected);
  };

  async function handleAnalyze() {
    if (!file || status === "loading") return;
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setStatus("loading");
    setApiError("");
    setFallback(false);
    setResult(null);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const response = await visionAPI.analyze(
        formData,
        { signal: controller.signal, timeout: TIMEOUT_MS }
      );
      const data = response.data;
      setResult(data);
      setFallback(data.is_fallback ?? false);
      setRemaining(response.headers?.["x-ratelimit-remaining"] ?? null);
      setStatus("success");
    } catch (err) {
      if (err.name === "CanceledError" || err.name === "AbortError") return;
      if (err.response?.status === 429) {
        setStatus("rate_limited");
        setApiError("Quota atteint. Vous pouvez effectuer 10 analyses par heure. Réessayez dans quelques minutes.");
      } else if (err.code === "ECONNABORTED" || err.message?.includes("timeout")) {
        setStatus("error");
        setApiError("L'API met trop de temps à répondre (>30 s). Un résultat dégradé est disponible via le fallback.");
      } else {
        setStatus("error");
        setApiError(err.response?.data?.detail || "Erreur lors de l'analyse. Vérifiez votre connexion et réessayez.");
      }
    }
  }

  async function handleHistoryFetch() {
    if (!historyId.trim()) return;
    setHistoryLoading(true);
    setHistoryError("");
    setHistoryResult(null);
    try {
      const res = await visionAPI.getAnalysis(historyId.trim());
      setHistoryResult(res.data);
    } catch (err) {
      setHistoryError(
        err.response?.status === 404
          ? "Analyse introuvable pour cet identifiant."
          : "Erreur lors de la récupération de l'analyse."
      );
    } finally {
      setHistoryLoading(false);
    }
  }

  function ResultCard({ data, isFallback }) {
    return (
      <section className={styles.resultCard} aria-labelledby="result-title">
        <div className={styles.resultHeader}>
          <h2 id="result-title" className={styles.resultTitle}>Résultats de l'analyse</h2>
          {isFallback ? (
            <span className={styles.fallbackBadge} role="alert">⚠ Mode dégradé — valeurs estimées</span>
          ) : (
            <span className={styles.sourceBadge} role="status">
              ✓ Source : {data.source === "ollama" ? "Ollama LLM" : data.source === "huggingface" ? "HuggingFace" : data.source}
            </span>
          )}
        </div>
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>Aliments détectés</h3>
          <ul className={styles.foodList} aria-label="Liste des aliments identifiés">
            {data.detected_foods?.map((food, i) => (
              <li key={i} className={styles.foodItem}>
                <span className={styles.foodDot} aria-hidden="true">●</span>{food}
              </li>
            ))}
          </ul>
        </div>
        <div className={styles.section}>
          <div className={styles.caloriesRow}>
            <span className={styles.caloriesLabel}>Calories estimées</span>
            <strong className={styles.caloriesValue} aria-label={`${data.nutrition?.calories} kilocalories`}>
              {data.nutrition?.calories} <small>kcal</small>
            </strong>
          </div>
        </div>
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>Macronutriments</h3>
          <div className={styles.macros}>
            <MacroBar label="Protéines" value={data.nutrition?.proteins_g ?? 0} unit="g" color="#3b82f6" max={100} />
            <MacroBar label="Glucides"  value={data.nutrition?.carbs_g   ?? 0} unit="g" color="#f59e0b" max={200} />
            <MacroBar label="Lipides"   value={data.nutrition?.fats_g    ?? 0} unit="g" color="#ef4444" max={80}  />
          </div>
        </div>
        <div className={styles.section}>
          <h3 className={styles.sectionTitle}>Balance nutritionnelle</h3>
          <BalanceBadge balance={data.balance} />
        </div>
        {data.recommendations?.length > 0 && (
          <div className={styles.section}>
            <h3 className={styles.sectionTitle}>Conseils personnalisés</h3>
            <ul className={styles.recommendList} aria-label="Recommandations nutritionnelles">
              {data.recommendations.map((rec, i) => (
                <li key={i} className={styles.recommendItem}><span aria-hidden="true">💡</span> {rec}</li>
              ))}
            </ul>
          </div>
        )}
        {isFallback && (
          <div className={styles.fallbackDetail} role="note">
            <p>🔄 <strong>Cascade IA tentée :</strong> HuggingFace → Ollama → valeurs génériques</p>
            <p>Les services IA (Ollama / HuggingFace) sont indisponibles. Les macros affichées sont des estimations pour un repas moyen équilibré.</p>
          </div>
        )}
        {data.analysis_id && (
          <p className={styles.analysisId}>ID analyse : <code>{data.analysis_id}</code></p>
        )}
      </section>
    );
  }

  return (
    <main className={styles.page}>
      <header className={styles.pageHeader}>
        <h1 className={styles.pageTitle}>Analyse nutritionnelle IA</h1>
        <p className={styles.pageSubtitle}>
          Uploadez une photo de votre repas pour identifier les aliments, calculer les macros et obtenir des conseils personnalisés.
        </p>
      </header>
      <div className={styles.layout}>
        <section className={styles.uploadSection} aria-labelledby="upload-title">
          <h2 id="upload-title" className={styles.sectionHeading}>Photo du repas</h2>
          <div
            className={`${styles.dropZone} ${dragActive ? styles.dropZoneActive : ""} ${fileError ? styles.dropZoneError : ""}`}
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            role="button"
            tabIndex={0}
            aria-label="Zone de dépôt d'image. Appuyez sur Entrée ou Espace pour ouvrir le sélecteur de fichier"
            onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") document.getElementById("file-input").click(); }}
          >
            {preview ? (
              <img src={preview} alt="Aperçu du repas sélectionné" className={styles.preview} />
            ) : (
              <div className={styles.dropPlaceholder} aria-hidden="true">
                <span className={styles.dropIcon}>📷</span>
                <p>Glissez une photo ici</p>
                <p className={styles.dropHint}>ou cliquez pour sélectionner</p>
                <p className={styles.dropFormats}>JPG, PNG, WEBP, GIF — max {MAX_FILE_SIZE_MB} Mo</p>
              </div>
            )}
          </div>
          <label htmlFor="file-input" className={styles.srOnly}>Sélectionner une image</label>
          <input
            id="file-input"
            type="file"
            accept={ACCEPTED_TYPES.join(",")}
            onChange={handleInputChange}
            className={styles.hiddenInput}
            aria-describedby={fileError ? "file-error" : undefined}
          />
          <button type="button" className={styles.btnSecondary} onClick={() => document.getElementById("file-input").click()}>
            📁 Choisir un fichier
          </button>
          {fileError && <p id="file-error" className={styles.errorMsg} role="alert">{fileError}</p>}
          <button
            type="button"
            className={styles.btnPrimary}
            onClick={handleAnalyze}
            disabled={!file || status === "loading"}
            aria-busy={status === "loading"}
            aria-disabled={!file || status === "loading"}
          >
            {status === "loading"
              ? <><span className={styles.spinner} aria-hidden="true" /> Analyse en cours…</>
              : "🔍 Analyser le repas"}
          </button>
          {remaining !== null && (
            <p className={styles.rateInfo} aria-live="polite">Quota restant : {remaining}/10 analyses par heure</p>
          )}
        </section>

        <div className={styles.resultsSection}>
          {status === "idle" && !result && (
            <div className={styles.emptyState} aria-label="Aucune analyse en cours">
              <span className={styles.emptyIcon} aria-hidden="true">🥗</span>
              <p>Uploadez une photo pour démarrer l'analyse</p>
            </div>
          )}
          {status === "loading" && <SkeletonResult />}
          {(status === "error" || status === "rate_limited") && (
            <div
              className={`${styles.alertBox} ${status === "rate_limited" ? styles.alertWarning : styles.alertError}`}
              role="alert"
              aria-live="assertive"
            >
              <strong>{status === "rate_limited" ? "⏳ Quota atteint" : "❌ Erreur"}</strong>
              <p>{apiError}</p>
              {status === "error" && (
                <p className={styles.fallbackNote}>Le backend retourne automatiquement une réponse dégradée — aucune donnée perdue.</p>
              )}
            </div>
          )}
          {status === "success" && result && <ResultCard data={result} isFallback={fallback} />}
        </div>
      </div>

      <section className={styles.historySection} aria-labelledby="history-title">
        <h2 id="history-title" className={styles.sectionHeading}>Récupérer une analyse passée</h2>
        <div className={styles.historyForm}>
          <label htmlFor="history-id" className={styles.historyLabel}>Identifiant d'analyse (UUID)</label>
          <div className={styles.historyRow}>
            <input
              id="history-id"
              type="text"
              className={styles.historyInput}
              value={historyId}
              onChange={(e) => setHistoryId(e.target.value)}
              placeholder="ex: 3f7a1c2d-…"
              aria-describedby={historyError ? "history-error" : undefined}
              onKeyDown={(e) => { if (e.key === "Enter") handleHistoryFetch(); }}
            />
            <button
              type="button"
              className={styles.btnSecondary}
              onClick={handleHistoryFetch}
              disabled={historyLoading || !historyId.trim()}
              aria-busy={historyLoading}
            >
              {historyLoading ? "Chargement…" : "Récupérer"}
            </button>
          </div>
          {historyError && <p id="history-error" className={styles.errorMsg} role="alert">{historyError}</p>}
        </div>
        {historyResult && <ResultCard data={historyResult} isFallback={false} />}
      </section>
    </main>
  );
}
