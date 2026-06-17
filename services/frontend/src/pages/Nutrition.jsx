import { useEffect, useState, useCallback } from "react";
import { nutritionAPI } from "../services/api";
import Table from "../components/Table";
import Loader from "../components/Loader";
import Card from "../components/Card";
import styles from "./NutritionExercises.module.css";

export default function Nutrition() {
  const [nutritionItems, setNutritionItems] = useState(null);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    category: "",
    search: ""
  });

  const loadNutritionItems = useCallback(async () => {
    try {
      setLoading(true);
      const params = { limit: 1000 };
      if (filters.category) params.category = filters.category;
      if (filters.search) params.search = filters.search;

      console.log("[Nutrition] Loading with params:", params);
      const response = await nutritionAPI.getNutritionItems(params);
      console.log("[Nutrition] Response received:", response.data);
      
      // Handle both direct arrays and paginated responses
      const data = response.data?.items || response.data || [];
      console.log("[Nutrition] Extracted data:", Array.isArray(data) ? `Array of ${data.length}` : "Not an array");
      console.log("[Nutrition] Setting state with:", data);
      setNutritionItems(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error("[Nutrition] ERROR:", error.response?.status, error.response?.data, error.message);
      setNutritionItems([]);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadNutritionItems();
  }, [filters, loadNutritionItems]);

  const handleFilterChange = (field, value) => {
    setFilters(prev => ({ ...prev, [field]: value }));
  };

  const handleExport = () => {
    if (!nutritionItems || nutritionItems.length === 0) {
      alert("Aucune donnée à exporter");
      return;
    }
    const dataStr = JSON.stringify(nutritionItems, null, 2);
    const dataBlob = new Blob([dataStr], { type: "application/json" });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `nutrition_${new Date().toISOString().split("T")[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  const handleAddNutrition = () => {
    const name = prompt("Nom de l'aliment:");
    if (!name) return;
    const category = prompt("Catégorie:");
    alert("Ajout d'aliments non implémenté dans cette version démo");
  };

  if (loading) return <Loader />;

  return (
    <div className={`space-y-6 ${styles.container}`}>
      <div className={styles.header}>
        <h1 className="text-3xl font-bold text-gray-900">Nutrition</h1>
        <div className={styles.actions}>
          <button
            className={styles.exportBtn}
            onClick={handleExport}
            title="Export nutrition data"
          >
            📥 Export JSON
          </button>
          <button 
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700"
            onClick={handleAddNutrition}
          >
            ➕ Ajouter
          </button>
        </div>
      </div>

      {/* Filtres */}
      <Card>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Catégorie
            </label>
            <select
              value={filters.category}
              onChange={(e) => handleFilterChange("category", e.target.value)}
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            >
              <option value="">Toutes</option>
              <option value="fruits">Fruits</option>
              <option value="vegetables">Légumes</option>
              <option value="proteins">Protéines</option>
              <option value="grains">Céréales</option>
              <option value="dairy">Produits laitiers</option>
              <option value="fats">Matières grasses</option>
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
              placeholder="Nom de l'aliment..."
              className="w-full border border-gray-300 rounded-md px-3 py-2"
            />
          </div>
        </div>
      </Card>

      {/* Liste des aliments */}
      <Card>
        {nutritionItems && nutritionItems.length > 0 ? (
          <>
            {console.log("[Nutrition] Rendering Table with items:", nutritionItems.length)}
            <Table data={nutritionItems} />
          </>
        ) : (
          <>
            {console.log("[Nutrition] NOT rendering Table. nutritionItems state:", nutritionItems)}
            <div className="text-center py-8 text-gray-500">
            Aucun aliment trouvé
          </div>
          </>
        )}
      </Card>
    </div>
  );
}