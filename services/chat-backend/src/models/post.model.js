const { DataTypes } = require('sequelize');
const sequelize = require('../config/db');

const Post = sequelize.define('Post', {
  title:   { type: DataTypes.STRING(200), allowNull: false },
  content: { type: DataTypes.TEXT, allowNull: false },
  authorUsername: { type: DataTypes.STRING, allowNull: false }
}, { tableName: 'posts' });

module.exports = Post;
