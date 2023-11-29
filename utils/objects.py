__all__ = ["User", "Server", "Pet"]

from dataclasses import dataclass

from datetime import datetime

@dataclass
class Server:
    
    id: int

    christmas_countdown_channel_id: int | None
    christmas_countdown_message_id: int | None
    christmas_countdown_enabled: bool

    created_at: datetime

@dataclass
class User:

    id: int

    trivia_points: int
    trivia_ranking: int | None

    balance: int | None

    snowball_hits: int
    snowball_throws: int
    snowball_dodges: int
    snowball_struck: int

    created_at: datetime

@dataclass
class Pet:

    id: int
    name: str

    owner_id: int

    health: int
    hunger: int

    searching: bool
    searching_till: float | None

    last_interaction: float | None
    last_fed: float | None
    created_at: datetime