const express = require('express');
const router  = express.Router();
const { verifyToken } = require('../middleware/auth.middleware');
const ctrl = require('../controllers/posts.controller');

// GET  /api/posts?page=1&limit=10  — liste paginée (protégé)
router.get('/',    verifyToken, ctrl.getAll);
// GET  /api/posts/:id              — détail (protégé)
router.get('/:id', verifyToken, ctrl.getById);
// POST /api/posts                  — créer (protégé)
router.post('/',   verifyToken, ctrl.create);
// PUT  /api/posts/:id              — remplacer (protégé, auteur seulement)
router.put('/:id', verifyToken, ctrl.update);
// DELETE /api/posts/:id            — supprimer (protégé, auteur seulement)
router.delete('/:id', verifyToken, ctrl.remove);

module.exports = router;
