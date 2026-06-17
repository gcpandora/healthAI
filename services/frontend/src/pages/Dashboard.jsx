import { useEffect, useState } from "react";
import { usersAPI, exercisesAPI, nutritionAPI } from "../services/api";
import Card from "../components/Card";

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        console.log("[Dashboard] Fetching data...");

        // Charger les utilisateurs, exercices, et aliments
        const [usersRes, exercisesRes, nutritionRes] = await Promise.all([
          usersAPI.getUsers({ limit: 1000 }),
          exercisesAPI.getExercises({ limit: 1000 }),
          nutritionAPI.getNutritionItems({ limit: 1000 })
        ]);

        const users = usersRes.data?.items || usersRes.data || [];
        const exercises = exercisesRes.data || [];
        const nutrition = nutritionRes.data || [];

        console.log("[Dashboard] Data loaded:", { users: users.length, exercises: exercises.length, nutrition: nutrition.length });

        // Calculer les métriques
        let total_weight = 0;
        let total_height = 0;
        const plans = {};
        const genders = {};
        let user_count_with_weight = 0;
        let user_count_with_height = 0;

        /*users.forEach(user => {
          // Plans
          plans[user.plan] = (plans[user.plan] || 0) + 1;
          
          // Genders
          genders[user.gender] = (genders[user.gender] || 0) + 1;
          
          // Weight & Height
          if (user.weight_kg) {
            total_weight += user.weight_kg;
            user_count_with_weight++;
          }
          if (user.height_cm) {
            total_height += user.height_cm;
            user_count_with_height++;
          }
        });*/
        //j'ai modifier le code car weight_kg et height_cm sont des string dans la base de données, il faut les parser en float pour faire les calculs correctement. J'ai aussi ajouté une vérification pour s'assurer que les valeurs sont des nombres valides avant de les inclure dans les totaux.
        users.forEach(user => {
          plans[user.plan] = (plans[user.plan] || 0) + 1;
          genders[user.gender] = (genders[user.gender] || 0) + 1;
          const weight = parseFloat(user.weight_kg);
          if (!isNaN(weight) && weight > 0) {
            total_weight += weight;
            user_count_with_weight++;
          }
        
          const height = parseFloat(user.height_cm);
          if (!isNaN(height) && height > 0) {
            total_height += height;
            user_count_with_height++;
          }
        }); 

        const metrics = {
          total_users: users.length,
          total_exercises: exercises.length,
          total_nutrition_items: nutrition.length,
          avg_weight: user_count_with_weight > 0 ? (total_weight / user_count_with_weight).toFixed(1) : 0,
          avg_height: user_count_with_height > 0 ? (total_height / user_count_with_height).toFixed(1) : 0,
          users_by_plan: plans,
          users_by_gender: genders
        };

        console.log("[Dashboard] Metrics:", metrics);
        setData(metrics);
        setError(null);
      } catch (err) {
        console.error("[Dashboard] Error:", err);
        setError("Erreur au chargement des données du dashboard");
        setData({
          total_users: 0,
          total_exercises: 0,
          total_nutrition_items: 0,
          avg_weight: 0,
          avg_height: 0,
          users_by_plan: {},
          users_by_gender: {}
        });
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleExport = () => {
    if (!data) return;

    const csvContent = [
      ["Metric", "Value"],
      ["Total Users", data.total_users || 0],
      ["Total Exercises", data.total_exercises || 0],
      ["Total Nutrition Items", data.total_nutrition_items || 0],
      ["Avg Weight (kg)", data.avg_weight || 0],
      ["Avg Height (cm)", data.avg_height || 0],
      ["Plans", JSON.stringify(data.users_by_plan)],
      ["Genders", JSON.stringify(data.users_by_gender)],
      ["Export Date", new Date().toISOString()]
    ].map(row => row.join(",")).join("\n");

    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `health-dashboard-${new Date().toISOString().split("T")[0]}.csv`;
    link.click();
    URL.revokeObjectURL(url);
  };

  if (loading) return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
      <p style={{ fontSize: "18px", color: "#666" }}>Loading Dashboard...</p>
    </div>
  );

  if (error) return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
      <p style={{ fontSize: "18px", color: "#e74c3c" }}>{error}</p>
    </div>
  );

  return (
    <div style={{ padding: "32px", backgroundColor: "#f8f9fa", minHeight: "100vh" }}>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "32px" }}>
        <div>
          <h1 style={{ margin: "0 0 8px 0", fontSize: "32px", fontWeight: "700", color: "#1a1a1a" }}>
            Dashboard
          </h1>
          <p style={{ margin: "0", color: "#7f8c8d", fontSize: "14px" }}>
            Last updated: {new Date().toLocaleDateString()}
          </p>
        </div>
        <button 
          onClick={handleExport}
          style={{
            padding: "12px 24px",
            backgroundColor: "#3498db",
            color: "white",
            border: "none",
            borderRadius: "8px",
            cursor: "pointer",
            fontSize: "14px",
            fontWeight: "600",
            transition: "all 0.3s ease",
            boxShadow: "0 2px 6px rgba(52, 152, 219, 0.2)"
          }}
          onMouseOver={(e) => {
            e.target.style.backgroundColor = "#2980b9";
            e.target.style.boxShadow = "0 4px 12px rgba(52, 152, 219, 0.3)";
          }}
          onMouseOut={(e) => {
            e.target.style.backgroundColor = "#3498db";
            e.target.style.boxShadow = "0 2px 6px rgba(52, 152, 219, 0.2)";
          }}
        >
          📊 Export Data (CSV)
        </button>
      </div>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
        gap: "20px",
        marginBottom: "32px"
      }}>
        <Card title="👥 Total Users" value={data?.total_users || 0} icon="👥" />
        <Card title="💪 Exercises Available" value={data?.total_exercises || 0} icon="💪" />
        <Card title="🍎 Nutrition Items" value={data?.total_nutrition_items || 0} icon="🍎" />
        <Card title="⚖️ Avg Weight (kg)" value={data?.avg_weight || 0} icon="⚖️" />
        <Card title="📏 Avg Height (cm)" value={data?.avg_height || 0} icon="📏" />
      </div>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
        gap: "20px",
        marginBottom: "32px"
      }}>
        <div style={{
          background: "white",
          padding: "24px",
          borderRadius: "12px",
          boxShadow: "0 2px 8px rgba(0, 0, 0, 0.08)"
        }}>
          <h3 style={{ margin: "0 0 16px 0", fontSize: "16px", fontWeight: "600", color: "#1a1a1a" }}>
            📊 Users by Plan
          </h3>
          {Object.entries(data?.users_by_plan || {}).map(([plan, count]) => (
            <div key={plan} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid #f0f0f0" }}>
              <span style={{ color: "#666", fontSize: "14px" }}>{plan}</span>
              <span style={{ fontWeight: "600", color: "#2980b9" }}>{count}</span>
            </div>
          ))}
        </div>

        <div style={{
          background: "white",
          padding: "24px",
          borderRadius: "12px",
          boxShadow: "0 2px 8px rgba(0, 0, 0, 0.08)"
        }}>
          <h3 style={{ margin: "0 0 16px 0", fontSize: "16px", fontWeight: "600", color: "#1a1a1a" }}>
            👨‍👩 Users by Gender
          </h3>
          {Object.entries(data?.users_by_gender || {}).map(([gender, count]) => (
            <div key={gender} style={{ display: "flex", justifyContent: "space-between", padding: "8px 0", borderBottom: "1px solid #f0f0f0" }}>
              <span style={{ color: "#666", fontSize: "14px" }}>{gender || "Not specified"}</span>
              <span style={{ fontWeight: "600", color: "#27ae60" }}>{count}</span>
            </div>
          ))}
        </div>

        <div style={{
          background: "white",
          padding: "24px",
          borderRadius: "12px",
          boxShadow: "0 2px 8px rgba(0, 0, 0, 0.08)"
        }}>
          <h3 style={{ margin: "0 0 16px 0", fontSize: "16px", fontWeight: "600", color: "#1a1a1a" }}>
            📈 Quick Stats
          </h3>
          <div style={{ display: "flex", flexDirection: "column", gap: "12px" }}>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ color: "#666" }}>Active Users:</span>
              <span style={{ fontWeight: "600", color: "#e74c3c" }}>{data?.total_users || 0}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ color: "#666" }}>Total Resources:</span>
              <span style={{ fontWeight: "600", color: "#9b59b6" }}>{(data?.total_exercises || 0) + (data?.total_nutrition_items || 0)}</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <span style={{ color: "#666" }}>System Status:</span>
              <span style={{ fontWeight: "600", color: "#27ae60" }}>✓ Operational</span>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}