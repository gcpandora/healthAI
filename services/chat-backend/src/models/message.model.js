const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');

const Message = sequelize.define('Message', {
  content:        { type: DataTypes.TEXT, allowNull: false },
  senderUsername: { type: DataTypes.STRING, allowNull: false }
}, { tableName: 'messages' });

module.exports = Message;
