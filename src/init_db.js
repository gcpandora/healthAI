const mysql = require("mysql2/promise");
const fs    = require("fs");
const path  = require("path");

// ── Connexion SANS base de données (pour pouvoir la créer) ────
async function initDB() {
    console.log("\n.");
   // console.log("  HealthAI Coach — Initialisation BDD");
    console.log(".\n");

    // Connexion sans spécifier la base (elle n'existe pas encore)
    const connexion = await mysql.createConnection({
        host:               "localhost",
        user:               "root",
        password:           "",       //  mot de passe WAMP
        port:               3307,
        charset:            "utf8mb4",
        multipleStatements: true      // ← Permet d'exécuter tout le SQL d'un coup
    });

    try {
        // Lire et exécuter le fichier schema.sql
        const sqlPath = path.join(__dirname, "schema.sql");
        const sql     = fs.readFileSync(sqlPath, "utf8");

        console.log(" Exécution de schema.sql...");
        await connexion.query(sql);

       // console.log(" Base de données 'healthai_coach' créée");
       // console.log(" Tables : users, biometrics, foods, exercises,");
       // console.log("            user_goals, activity_logs, nutrition_logs");
       // console.log("\n Initialisation terminée !");
       // console.log(" Lance maintenant : GET /charger-donnees\n");

    } catch (error) {
        console.error(" Erreur lors de l'initialisation :", error.message);
        throw error;
    } finally {
        await connexion.end();
    }
}

module.exports = initDB;
