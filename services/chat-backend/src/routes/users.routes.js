const express = require('express');
const router  = express.Router();
const { User } = require('../models');
const { verifyToken } = require('../middleware/auth.middleware');
const { createKeycloakUser, updateKeycloakUser, deleteKeycloakUser } = require('../config/keycloak');
const { Op } = require('sequelize');

// POST /api/users — inscription publique
router.post('/', async (req, res, next) => {
  const { username, email, password } = req.body;
  if (!username || !email || !password)
    return res.status(400).json({ message: 'Veuillez remplir tous les champs.' });
  try {
    const existing = await User.findOne({ where: { [Op.or]: [{ username }, { email }] } });
    if (existing) return res.status(400).json({ message: 'Ce pseudo ou cet email est déjà utilisé.' });

    const keycloakId = await createKeycloakUser(username, email, password);
    const newUser = await User.create({ username, email, keycloakId });
    res.status(201).json({ message: 'Utilisateur créé avec succès !', user: { id: newUser.id, username, email, keycloakId } });
  } catch (err) { next(err); }
});

// GET /api/users — liste (protégé)
router.get('/', verifyToken, async (req, res, next) => {
  try {
    const users = await User.findAll({ attributes: ['id', 'username', 'email', 'keycloakId', 'createdAt'] });
    res.json(users);
  } catch (err) { next(err); }
});

// GET /api/users/:id
router.get('/:id', verifyToken, async (req, res, next) => {
  try {
    const user = await User.findByPk(req.params.id, { attributes: ['id', 'username', 'email', 'keycloakId', 'createdAt'] });
    if (!user) return res.status(404).json({ message: 'Utilisateur non trouvé.' });
    res.json(user);
  } catch (err) { next(err); }
});

// PUT /api/users/:id
router.put('/:id', verifyToken, async (req, res, next) => {
  try {
    const user = await User.findByPk(req.params.id);
    if (!user) return res.status(404).json({ message: 'Utilisateur non trouvé.' });
    const updatedUsername = req.body.username || user.username;
    const updatedEmail    = req.body.email    || user.email;
    await updateKeycloakUser(user.keycloakId, updatedUsername, updatedEmail, req.body.password);
    user.username = updatedUsername;
    user.email    = updatedEmail;
    await user.save();
    res.json({ message: 'Utilisateur mis à jour.', user: { id: user.id, username: user.username, email: user.email } });
  } catch (err) { next(err); }
});

// DELETE /api/users/:id
router.delete('/:id', verifyToken, async (req, res, next) => {
  try {
    const user = await User.findByPk(req.params.id);
    if (!user) return res.status(404).json({ message: 'Utilisateur non trouvé.' });
    await deleteKeycloakUser(user.keycloakId);
    await user.destroy();
    res.json({ message: 'Utilisateur supprimé.' });
  } catch (err) { next(err); }
});

module.exports = router;
