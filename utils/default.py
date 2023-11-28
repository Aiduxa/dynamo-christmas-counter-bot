__all__ = ['Color', 'Default', 'Emoji', "Variables"]


from datetime import datetime

from dataclasses import dataclass, field

from discord import Object as D_Object
from random import randint


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
	zero: str = "<:zeroz:1179056666956791809>"
	one: str = "<:onez:1179056692374278276>"
	two: str = "<:twoz:1179056707851255869>"
	three: str = "<:threez:1179056733864345712>"
	four: str = "<:fourz:1179056752088596581>"
	five: str = "<:fivez:1179056773848633375>"
	six: str = "<:sixz:1179056797726801972>"
	seven: str = "<:sevenz:1179056815275782235>"
	eight: str = "<:eightz:1179056845290229871>"
	nine: str = "<:ninez:1179056867012530208>"

	PROGRESS_BAR_START_EMPTY: str = "<:5499lb2g:1179063941259853855>"
	PROGRESS_BAR_START_FULL: str = "<:5988lbg:1179063919403347978>"

	PROGRESS_BAR_FULL: str = "<:3451lg:1179064005575327826>"
	PROGRESS_BAR_EMPTY: str = "<:2827l2g:1179064023178809476>"

	PROGRESS_BAR_END_FULL: str = "<:3166lb4g:1179063982733152256>"
	PROGRESS_BAR_END_EMPTY: str = "<:2881lb3g:1179063958888521738>"

@dataclass
class Variables:
	CURRENCY: str = "$"
	PET_FIND_COOLDOWN: float = 86400
	PET_FIND_RETURN: tuple = (250, 1000) 
	PET_FEED_COST: int = 1000