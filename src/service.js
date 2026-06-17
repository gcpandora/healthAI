const fs   = require("fs");
const csv  = require("csv-parser");
const pool = require("./db");

// ═══════════════════════════════════════════════════════════════
// UTILITAIRE — Lire un fichier CSV et retourner les lignes
// ═══════════════════════════════════════════════════════════════
function lireCSV(ruta) {
    return new Promise((resolve, reject) => {
        const resultados = [];
        fs.createReadStream(ruta)
            .pipe(csv())
            .on("data", (data) => resultados.push(data))
            .on("end",  () => resolve(resultados))
            .on("error", reject);
    });
}

// ═══════════════════════════════════════════════════════════════
// 1. INSERTION — Table foods
//    Source : daily_food_nutrition_bdd.csv
//    Colonnes : food_item, category, calories_kcal, protein_g,
//               carbohydrates_g, fat_g, fiber_g, sugars_g,
//               sodium_mg, cholesterol_mg, meal_type, water_intake_ml
// ═══════════════════════════════════════════════════════════════
async function insertarFoods(ruta) {
    console.log(" Lecture :", ruta);
    const filas = await lireCSV(ruta);

    await pool.query("DELETE FROM nutrition_logs");
    await pool.query("DELETE FROM foods");

    const repasMap = {
        "Breakfast": "petit_dejeuner",
        "Lunch":     "dejeuner",
        "Dinner":    "diner",
        "Snack":     "collation"
    };

    let ok = 0, err = 0;

    for (let f of filas) {
        try {
            await pool.query(
                `INSERT INTO foods 
                (nom, categorie, calories_kcal, proteines_g, glucides_g, lipides_g,
                 fibres_g, sucres_g, sodium_mg, cholesterol_mg, type_repas, water_intake_ml, source_donnee)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                [
                    f["food_item"]          || null,
                    f["category"]           || null,
                    parseFloat(f["calories_kcal"])    || 0,
                    parseFloat(f["protein_g"])        || 0,
                    parseFloat(f["carbohydrates_g"])  || 0,
                    parseFloat(f["fat_g"])            || 0,
                    parseFloat(f["fiber_g"])          || 0,
                    parseFloat(f["sugars_g"])         || 0,
                    parseFloat(f["sodium_mg"])        || 0,
                    parseFloat(f["cholesterol_mg"])   || 0,
                    repasMap[f["meal_type"]] || "collation",
                    parseFloat(f["water_intake_ml"])  || 0,
                    "kaggle_daily_food_bdd"
                ]
            );
            ok++;
        } catch (e) {
            console.warn("   Ligne ignorée (foods):", f["food_item"], "→", e.message);
            err++;
        }
    }
    console.log(`foods : ${ok} insérés, ${err} erreurs`);
}

// ═══════════════════════════════════════════════════════════════
// 2. INSERTION — Table users + biometrics
//    Source : gym_members_exercise_bdd.csv  (973 lignes)
//             gym_members_synthetic_bdd.csv (1800 lignes)
//    Colonnes : age, gender, weight_kg, height_m, max_bpm, avg_bpm,
//               resting_bpm, session_duration_hours, calories_burned,
//               workout_type, fat_percentage, water_intake_liters,
//               workout_frequency_days/week, experience_level, bmi
// ═══════════════════════════════════════════════════════════════
async function insertarUsers(rutaExercise, rutaSynthetic) {
    await pool.query("DELETE FROM activity_logs");
    await pool.query("DELETE FROM biometrics");
    await pool.query("DELETE FROM user_goals");
    await pool.query("DELETE FROM health_profiles");
    await pool.query("DELETE FROM users");

    const sources = [];
    if (rutaExercise) {
        console.log(" Lecture :", rutaExercise);
        sources.push(...await lireCSV(rutaExercise));
    }
    if (rutaSynthetic) {
        console.log(" Lecture :", rutaSynthetic);
        sources.push(...await lireCSV(rutaSynthetic));
    }

    let ok = 0, err = 0;

    for (let i = 0; i < sources.length; i++) {
        const f     = sources[i];
        const email = `user${i + 1}@healthai.com`;

        const exp    = parseFloat(f["experience_level"] || 1);
        const niveau = exp <= 1 ? "debutant" : exp <= 2 ? "intermediaire" : "avance";

        const genreRaw = (f["gender"] || "").trim();
        const genre    = genreRaw === "Male" ? "M" : genreRaw === "Female" ? "F" : "autre";

        const hauteurM = parseFloat(f["height_m"] || 0);
        const tailleCm = hauteurM > 0 ? Math.round(hauteurM * 100) : null;
        const poids    = parseFloat(f["weight_kg"] || 0) || null;
        const age      = parseInt(f["age"]         || 0) || null;
        const water    = parseFloat(f["water_intake_liters"] || 0) || null;
        const freq     = parseInt(f["workout_frequency_days/week"] || 0) || null;

        try {
            await pool.query(
                `INSERT INTO users (email, age, genre, poids_kg, taille_cm, niveau_fitness, water_intake_liters, workout_frequency)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
                [email, age, genre, poids, tailleCm, niveau, water, freq]
            );

            await pool.query(
                `INSERT INTO biometrics (user_id, date_mesure, poids_kg, bpm_moyen, bpm_max, bpm_repos, bmi, body_fat_pct)
                 VALUES ((SELECT id FROM users WHERE email = ? LIMIT 1), CURDATE(), ?, ?, ?, ?, ?, ?)`,
                [
                    email,
                    poids,
                    parseFloat(f["avg_bpm"])        || null,
                    parseFloat(f["max_bpm"])        || null,
                    parseFloat(f["resting_bpm"])    || null,
                    parseFloat(f["bmi"])            || null,
                    parseFloat(f["fat_percentage"]) || null,
                ]
            );

            ok++;
        } catch (e) {
            console.warn("     User ignoré:", email, "→", e.message);
            err++;
        }
    }
    console.log(` users + biometrics : ${ok} insérés, ${err} erreurs`);
}

// ═══════════════════════════════════════════════════════════════
// 3. INSERTION — Tables health_profiles + user_goals
//    Source : diet_recommendations_bdd.csv
//    Toutes les colonnes sont maintenant exploitées
// ═══════════════════════════════════════════════════════════════
async function insertarUserGoals(ruta) {
    console.log(" Lecture :", ruta);
    const filas = await lireCSV(ruta);

    const [[{ total }]] = await pool.query("SELECT COUNT(*) AS total FROM users");

    // Mappings
    const severityMap = {
        "mild": "Mild", "moderate": "Moderate", "severe": "Severe"
    };
    const activityMap = {
        "low": "Low", "moderate": "Moderate", "high": "High"
    };
    const objectifMap = {
        "weight_loss": "perte_poids", "loss": "perte_poids",
        "muscle_gain": "prise_masse", "gain": "prise_masse",
        "balanced":    "equilibre",
        "low_carb":    "maintien",
        "high_protein":"prise_masse",
        "diabetic":    "maintien",
        "heart_healthy":"maintien",
        "sleep":       "sommeil"
    };

    let ok = 0, err = 0;

    for (let i = 0; i < Math.min(filas.length, total); i++) {
        const f     = filas[i];
        const email = `user${i + 1}@healthai.com`;

        const recRaw  = (f["diet_recommendation"] || "").toLowerCase().replace(/ /g, "_");
        const diseaseRaw = (f["disease_type"] || "").toLowerCase();
        let objectif  = objectifMap[recRaw]
                     || (diseaseRaw.includes("obes") ? "perte_poids" : null)
                     || (diseaseRaw.includes("sleep") ? "sommeil" : null)
                     || "maintien";

        const calories  = parseFloat(f["daily_caloric_intake"] || 0) || null;
        const severity  = severityMap[(f["severity"] || "").toLowerCase()] || "Mild";
        const activity  = activityMap[(f["physical_activity_level"] || "").toLowerCase()] || "Moderate";
        const chol      = parseFloat(f["cholesterol_mg/dl"] || 0) || null;
        const bp        = parseInt(f["blood_pressure_mmhg"]  || 0) || null;
        const glucose   = parseFloat(f["glucose_mg/dl"]      || 0) || null;
        const restrict  = f["dietary_restrictions"] || null;
        const allergies = f["allergies"]            || null;
        const cuisine   = f["preferred_cuisine"]    || null;
        const exHours   = parseFloat(f["weekly_exercise_hours"]            || 0) || null;
        const adherence = parseFloat(f["adherence_to_diet_plan"]           || 0) || null;
        const imbalance = parseFloat(f["dietary_nutrient_imbalance_score"] || 0) || null;
        const dietRec   = f["diet_recommendation"] || null;

        try {
            // health_profiles — toutes les données médicales
            await pool.query(
                `INSERT INTO health_profiles
                 (user_id, disease_type, severity, physical_activity_level,
                  cholesterol_mg_dl, blood_pressure_mmhg, glucose_mg_dl,
                  dietary_restrictions, allergies, preferred_cuisine,
                  weekly_exercise_hours, adherence_to_diet_plan,
                  dietary_nutrient_imbalance_score, diet_recommendation)
                 VALUES ((SELECT id FROM users WHERE email = ? LIMIT 1),
                         ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                [email, f["disease_type"] || null, severity, activity,
                 chol, bp, glucose, restrict, allergies, cuisine,
                 exHours, adherence, imbalance, dietRec]
            );

            // user_goals — objectif + calorie cible
            await pool.query(
                `INSERT INTO user_goals (user_id, type_objectif, valeur_cible, date_debut, date_fin)
                 VALUES ((SELECT id FROM users WHERE email = ? LIMIT 1),
                         ?, ?, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 90 DAY))`,
                [email, objectif, calories]
            );

            ok++;
        } catch (e) {
            console.warn("     Goal/Profile ignoré:", email, "→", e.message);
            err++;
        }
    }
    console.log(` health_profiles + user_goals : ${ok} insérés, ${err} erreurs`);
}

// ═══════════════════════════════════════════════════════════════
// 4. INSERTION — Table exercises + activity_logs
//    Source : gym_members_exercise_bdd.csv + gym_members_synthetic_bdd.csv
// ═══════════════════════════════════════════════════════════════
async function insertarActivity(rutaExercise, rutaSynthetic) {
    const sources = [];
    if (rutaExercise) sources.push(...await lireCSV(rutaExercise));
    if (rutaSynthetic) sources.push(...await lireCSV(rutaSynthetic));

    // Exercices uniques
    const exercicesUniques = [...new Set(
        sources.map(f => f["workout_type"]).filter(Boolean)
    )];

    for (let ex of exercicesUniques) {
        try {
            await pool.query(
                `INSERT IGNORE INTO exercises (nom, type_exercice, muscle_cible, equipement, niveau)
                 VALUES (?, 'cardio_muscu', 'multiple', 'variable', 'intermediaire')`,
                [ex]
            );
        } catch (e) {
            console.warn("     Exercice ignoré:", ex);
        }
    }
    console.log(` exercises : ${exercicesUniques.length} types insérés`);

    let ok = 0, err = 0;
    for (let i = 0; i < sources.length; i++) {
        const f        = sources[i];
        const email    = `user${i + 1}@healthai.com`;
        const exercice = f["workout_type"] || null;
        const dureeH   = parseFloat(f["session_duration_hours"] || 0);
        const dureeMin = dureeH > 0 ? Math.round(dureeH * 60) : null;
        const calories = parseFloat(f["calories_burned"] || 0) || null;

        try {
            await pool.query(
                `INSERT INTO activity_logs (user_id, exercise_id, date_seance, duree_min, calories_brulees)
                 VALUES (
                     (SELECT id FROM users     WHERE email = ? LIMIT 1),
                     (SELECT id FROM exercises WHERE nom   = ? LIMIT 1),
                     CURDATE(), ?, ?
                 )`,
                [email, exercice, dureeMin, calories]
            );
            ok++;
        } catch (e) {
            console.warn("     Activity ignorée:", email, "→", e.message);
            err++;
        }
    }
    console.log(` activity_logs : ${ok} insérés, ${err} erreurs`);
}

// ═══════════════════════════════════════════════════════════════
// 5. INSERTION — Table nutrition_logs
//    Source : daily_food_nutrition_bdd.csv
// ═══════════════════════════════════════════════════════════════
async function insertarNutritionLogs(ruta) {
    console.log(" Lecture :", ruta);
    const filas = await lireCSV(ruta);

    const repasMap = {
        "Breakfast": "petit_dejeuner",
        "Lunch":     "dejeuner",
        "Dinner":    "diner",
        "Snack":     "collation"
    };

    const [[{ total }]] = await pool.query("SELECT COUNT(*) AS total FROM users");

    let ok = 0, err = 0;
    const today = new Date().toISOString().split("T")[0];

    for (let i = 0; i < filas.length; i++) {
        const f       = filas[i];
        const userNum = (i % total) + 1;
        const email   = `user${userNum}@healthai.com`;
        const nomFood = f["food_item"] || null;
        const repas   = repasMap[f["meal_type"]] || "collation";

        try {
            await pool.query(
                `INSERT INTO nutrition_logs (user_id, food_id, date_repas, repas, quantite_g)
                 VALUES (
                     (SELECT id FROM users WHERE email = ? LIMIT 1),
                     (SELECT id FROM foods WHERE nom   = ? LIMIT 1),
                     ?, ?, 150.00
                 )`,
                [email, nomFood, today, repas]
            );
            ok++;
        } catch (e) {
            console.warn("     Nutrition log ignoré ligne", i, "→", e.message);
            err++;
        }
    }
    console.log(` nutrition_logs : ${ok} insérés, ${err} erreurs`);
}

// ═══════════════════════════════════════════════════════════════
// VÉRIFICATION FINALE
// ═══════════════════════════════════════════════════════════════
async function verificationFinale() {
    const tables = [
        "users", "biometrics", "foods", "health_profiles",
        "user_goals", "exercises", "activity_logs", "nutrition_logs"
    ];
    console.log("\n── Vérification finale ──");
    for (let t of tables) {
        const [[{ nb }]] = await pool.query(`SELECT COUNT(*) AS nb FROM ${t}`);
        console.log(`   ${t.padEnd(25)} : ${nb} lignes`);
    }
}

module.exports = {
    insertarFoods,
    insertarUsers,
    insertarUserGoals,
    insertarActivity,
    insertarNutritionLogs,
    verificationFinale
};
