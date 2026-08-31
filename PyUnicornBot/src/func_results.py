from dataclasses import dataclass

@dataclass
class SelectBabyResult:
    selected: bool
    baby_id: int | None
    has_players: bool


@dataclass
class SetNumberResult:
    message: str
    game_ready: bool = False
    chat_id: int | None = None
    first_player_id: int | None = None