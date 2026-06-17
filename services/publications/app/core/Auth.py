"""
COUCHE AUTH — Identification de l'utilisateur courant.

VERSION TEMPORAIRE : on lit l'id dans le header X-User-Id pour qu'Hélie
puisse tester sans le vrai JWT. Quand ta tâche "Authentification JWT
partagée" sera prête, on remplacera le corps de cette fonction par la
validation du token HS256 (réutilisant le secret de l'API :8000) —
la signature ne changera pas, donc les routes ne bougeront pas.
"""
from fastapi import Header

DEFAULT_USER = "11111111-1111-1111-1111-111111111111"  # Tojo, par défaut


def current_user(x_user_id: str = Header(default=DEFAULT_USER)) -> str:
    # FUTUR : décoder le JWT, vérifier signature HS256, extraire le sub
    #   payload = jwt.decode(token, SECRET, algorithms=["HS256"])
    #   return payload["sub"]
    return x_user_id