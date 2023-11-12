__all__ = ['Color', 'Default', 'Emoji']


from datetime import datetime

from dataclasses import dataclass, field

from discord import Object as D_Object


@dataclass
class Color:
	BLURPLE: int = int("5261f8", 16)
	GREEN: int = int("77DD77", 16)
	NEON: int = int("1aff79", 16)
	RED: int = int("a83232", 16)

@dataclass
class Default:
	SERVER: D_Object = D_Object(id=1060218266670346370)
	COLOR: int = Color.NEON
	FOOTER: str = "Dynamo © 2023"
	PREFIX: str = "dyn."

@dataclass
class Emoji:
	SUPER_ACTIVE: str = "<:super_active:1062614609028198410>"
	ACTIVE: str = "<:active:1062614628909187143>"
	ONLINE: str = "<:online:1062614646038732851>"
