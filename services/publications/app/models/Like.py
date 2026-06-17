from dataclasses import dataclass,field,asdict
from datetime import datetime, timezone

import uuid

def _now() -> str:
    return datetime.now(timezone.utc)


@dataclass
class Like:
    post_id: str
    user_id: str
    created_at: str = field(default_factory=_now)
 
    def to_dict(self) -> dict:
        return asdict(self)


