// Global error handler
function errorMiddleware(err, req, res, next) {
  console.error('Global error:', err.message);
  const status = err.status || 500;
  res.status(status).json({ message: err.message || 'Erreur interne du serveur.' });
}

module.exports = { errorMiddleware };
