const initDB = require("./init_db");
const {
    insertarFoods,
    insertarUsers,
    insertarUserGoals,
    insertarActivity,
    insertarNutritionLogs,
    verificationFinale
} = require("./service");

async function lancer() {
    try {
         console.log("\n                                                ");
        console.log("  HealthAI Coach — Lancement BDD");
       

        // ÉTAPE 1 — Créer les tables
        console.log("ÉTAPE 1/5 — Initialisation de la base de données...");
        await initDB();

        // ÉTAPE 2 — Charger les aliments
        console.log("\nÉTAPE 2/5 — Chargement des aliments...");
        await insertarFoods("./data/daily_food_nutrition_bdd.csv");

        // ÉTAPE 3 — Charger les utilisateurs + biométrie
        console.log("\nÉTAPE 3/5 — Chargement des utilisateurs + biométrie...");
        await insertarUsers(
            "./data/gym_members_exercise_bdd.csv",
            "./data/gym_members_synthetic_bdd.csv"
        );

        // ÉTAPE 4 — Charger les profils santé + objectifs
        console.log("\nÉTAPE 4/5 — Chargement des profils santé + objectifs...");
        await insertarUserGoals("./data/diet_recommendations_bdd.csv");

        // ÉTAPE 5 — Charger les exercices + activités + nutrition
        console.log("\nÉTAPE 5/5 — Chargement des activités et nutrition...");
        await insertarActivity(
            "./data/gym_members_exercise_bdd.csv",
            "./data/gym_members_synthetic_bdd.csv"
        );
        await insertarNutritionLogs("./data/daily_food_nutrition_bdd.csv");

        // VÉRIFICATION FINALE
        await verificationFinale();

       
        console.log("  BDD prête ");
        

        process.exit(0);

    } catch (error) {
        console.error("\n ERREUR lors du lancement :", error.message);
        process.exit(1);
    }
}

lancer();
