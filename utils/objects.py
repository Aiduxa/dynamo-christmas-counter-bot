__all__ = ["User", "Server"]

from dataclasses import dataclass

from datetime import datetime

@dataclass
class Server:
    
    id: int

    christmas_countdown_channel_id: int
    christmas_countdown_message_id: int

    created_at: datetime

@dataclass
class User:

    id: int

    created_at: datetime

