const { Post } = require('../models');

const getAll = async (page = 1, limit = 10) => {
  const offset = (page - 1) * limit;
  const { rows, count } = await Post.findAndCountAll({
    order: [['createdAt', 'DESC']],
    limit: parseInt(limit),
    offset: parseInt(offset)
  });
  return {
    data: rows,
    total: count,
    page: parseInt(page),
    totalPages: Math.ceil(count / limit)
  };
};

const getById = async (id) => {
  const post = await Post.findByPk(id);
  if (!post) throw Object.assign(new Error('Post non trouvé.'), { status: 404 });
  return post;
};

const create = async ({ title, content, authorUsername, userId }) => {
  if (!title || !content) throw Object.assign(new Error('Titre et contenu requis.'), { status: 400 });
  return Post.create({ title: title.trim(), content: content.trim(), authorUsername, userId });
};

const update = async (id, { title, content }, requestingUsername) => {
  const post = await getById(id);
  if (post.authorUsername !== requestingUsername) {
    throw Object.assign(new Error('Vous ne pouvez modifier que vos propres posts.'), { status: 403 });
  }
  if (title)   post.title   = title.trim();
  if (content) post.content = content.trim();
  await post.save();
  return post;
};

const remove = async (id, requestingUsername) => {
  const post = await getById(id);
  if (post.authorUsername !== requestingUsername) {
    throw Object.assign(new Error('Vous ne pouvez supprimer que vos propres posts.'), { status: 403 });
  }
  await post.destroy();
};

module.exports = { getAll, getById, create, update, remove };
