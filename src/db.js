const mysql = require("mysql2/promise");

const pool = mysql.createPool({
    host: "localhost",
    user: "root",
    password: "",          // mot de passe WAMP
    database: "healthai_coach",
    port: 3307,
    charset: "utf8mb4"
});

module.exports = pool;
// Connexion à MariaDB — HealthAI Coach
