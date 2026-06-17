from dataclasses import dataclass,field,asdict
from datetime import datetime, timezone

import uuid

def _now() -> str:
    return datetime.now(timezone.utc)



@dataclass
class Profile:
    user_id: str
    display_name: str
    avatar_url: str |None = None
    bio: str |None = None
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)

    def to_dict(self) -> dict:
        return asdict(self)

