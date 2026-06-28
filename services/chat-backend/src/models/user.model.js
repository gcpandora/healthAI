const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');

const User = sequelize.define('User', {
  username: { type: DataTypes.STRING, allowNull: false, unique: true },
  email:    { type: DataTypes.STRING, allowNull: false, unique: true },
  keycloakId: { type: DataTypes.STRING, allowNull: true, unique: true }
}, { tableName: 'users' });

module.exports = User;
