const postsService = require('../services/posts.service');

const getAll = async (req, res, next) => {
  try {
    const { page = 1, limit = 10 } = req.query;
    const result = await postsService.getAll(page, limit);
    res.json(result);
  } catch (err) { next(err); }
};

const getById = async (req, res, next) => {
  try {
    const post = await postsService.getById(req.params.id);
    res.json(post);
  } catch (err) { next(err); }
};

const create = async (req, res, next) => {
  try {
    const { title, content } = req.body;
    const post = await postsService.create({
      title,
      content,
      authorUsername: req.user.username,
      userId: req.user.localId || null
    });
    res.status(201).json(post);
  } catch (err) { next(err); }
};

const update = async (req, res, next) => {
  try {
    const post = await postsService.update(req.params.id, req.body, req.user.username);
    res.json(post);
  } catch (err) { next(err); }
};

const remove = async (req, res, next) => {
  try {
    await postsService.remove(req.params.id, req.user.username);
    res.json({ message: 'Post supprimé avec succès.' });
  } catch (err) { next(err); }
};

module.exports = { getAll, getById, create, update, remove };
