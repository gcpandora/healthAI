"""
COUCHE CONTROLLER — Logique métier des profils.
"""
from app.models.Profile import Profile
from app.repository.base import ProfileRepository
from app.core.exceptions import NotFoundError


class ProfileController:
    def __init__(self, profiles: ProfileRepository):
        self.profiles = profiles

    def get_my_profile(self, user_id: str) -> dict:
        profile = self.profiles.get(user_id)
        if not profile:
            raise NotFoundError("Profil introuvable")
        return profile.to_dict()

    def update_my_profile(self, user_id: str, fields: dict) -> dict:
        profile = self.profiles.get(user_id)
        if not profile:
            # Création à la volée si inexistant
            profile = Profile(user_id=user_id, display_name="Nouvel utilisateur")
        # PATCH : on ne touche qu'aux champs réellement fournis
        for key in ("display_name", "avatar_url", "bio"):
            if key in fields and fields[key] is not None:
                setattr(profile, key, fields[key])
        from datetime import datetime, timezone
        profile.updated_at = datetime.now(timezone.utc).isoformat()
        self.profiles.upsert(profile)
        return profile.to_dict()
