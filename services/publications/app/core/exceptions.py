class NotFoundError(Exception):
    """Ressource introuvable (→ 404)."""

class ForbiddenError(Exception):
    """Action non autorisée pour cet utilisateur (→ 403)."""

class ValidationError(Exception):
    """Données invalides au sens métier (→ 400)."""