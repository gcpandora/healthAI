import { useEffect, useState, useCallback } from "react";
import { exercisesAPI } from "../services/api";
import Table from "../components/Table";
import Loader from "../components/Loader";
import Card from "../components/Card";
import styles from "./NutritionExercises.module.css";

export default function Exercises() {
  const [exercises, setExercises] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    type: "",
    muscle_group: "",
    difficulty: "",
    search: ""
  });

  const loadExercises = useCallback(async () => {
    try {
      setLoading(true);
      const params = { limit: 1000 };
      if (filters.type) params.type = filters.type;
      if (filters.muscle_group) params.muscle_group = filters.muscle_group;
      if (filters.difficulty) params.difficulty = filters.difficulty;
      if (filters.search) params.search = filters.search;

      console.log("[Exercises] Loading with params:", params);
      const response = await exercisesAPI.getExercises(params);
      console.log("[Exercises] Response received:", response.data);
      
      // Handle both direct arrays and paginated responses
      const data = response.data?.items || response.data || [];
      console.log("[Exercises] Extracted data:", Array.isArray(data) ? `Array of ${data.length}` : "Not an array");
      console.log("[Exercises] Setting state with:", data);
      setExercises(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("[Exercises] ERROR:", error.response?.status, error.response?.data, error.message);
      setExercises([]);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadExercises();
  }, [filters, loadExercises]);

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const handleExport = () => {
    if (!exercises || exercises.length === 0) {
      alert("Aucune donnée à exporter");
      return;
    }
    const dataStr = JSON.stringify(exercises, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `exercises_${new Date().toISOString().split("T")[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleAddExercise = () => {
    const name = prompt("Nom de l'exercice:");
    if (!name) return;
    const type = prompt("Type (Strength/Cardio/Flexibility):");
    const muscle = prompt("Groupe musculaire:");
    alert("Ajout d'exercices non implémenté dans cette version démo");
  };

  if (loading) return <Loader />;

  return (
    <div className={`space-y-6 ${styles.container}`}>
      <div className={styles.header}>
        <h1 className="text-3xl font-bold text-gray-900">Exercices</h1>
        <div className={styles.actions}>
          <button
            className={styles.exportBtn}
            onClick={handleExport}
            title="Export exercises data"
          >
            📥 Export JSON
          </button>
          <button 
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            onClick={handleAddExercise}
          >
            ➕ Ajouter
          </button>
        </div>
      </div>

      {/* Filtres */}
      <Card>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Type
            </label>
            <select
              value={filters.type}
              onChange={(e) => handleFilterChange("type", e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">Tous</option>
              <option value="cardio">Cardio</option>
              <option value="strength">Force</option>
              <option value="flexibility">Flexibilité</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Groupe musculaire
            </label>
            <select
              value={filters.muscle_group}
              onChange={(e) => handleFilterChange("muscle_group", e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">Tous</option>
              <option value="chest">Pectoraux</option>
              <option value="back">Dos</option>
              <option value="legs">Jambes</option>
              <option value="arms">Bras</option>
              <option value="shoulders">Épaules</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Difficulté
            </label>
            <select
              value={filters.difficulty}
              onChange={(e) => handleFilterChange("difficulty", e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">Toutes</option>
              <option value="beginner">Débutant</option>
              <option value="intermediate">Intermédiaire</option>
              <option value="advanced">Avancé</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Recherche
            </label>
            <input
              type="text"
              value={filters.search}
              onChange={(e) => handleFilterChange("search", e.target.value)}
              placeholder="Nom de l'exercice..."
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>
        </div>
      </Card>

      {/* Liste des exercices */}
      <Card>
        {exercises && exercises.length > 0 ? (
          <>
            {console.log("[Exercises] Rendering Table with exercises:", exercises.length)}
            <Table data={exercises} />
          </>
        ) : (
          <>
            {console.log("[Exercises] NOT rendering Table. exercises state:", exercises)}
            <div className="text-center py-8 text-gray-500">
            Aucun exercice trouvé
          </div>
          </>
        )}
      </Card>
    </div>
  );
}