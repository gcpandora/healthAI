from dataclasses import dataclass,field,asdict
from datetime import datetime, timezone

import uuid

def _now() -> str:
    return datetime.now(timezone.utc)

def _uuid() ->str:
    return uuid.uuid4()

@dataclass
class Comment:
    
    post_id: str
    user_id: str
    content: str
    id: str = field(default_factory=_uuid)
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)

    def to_dict(self) -> dict:
        return asdict(self)


