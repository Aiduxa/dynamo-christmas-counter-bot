__all__ = ["Embeds"]

from discord import Embed

from dataclasses import dataclass
from .default import Default, Color

@dataclass
class Embeds:
    set_countdown_channel_embed = Embed(
        title="✅ Channel has been successfully set!",
        description="Christmas countdown has been set to:\n- Channel: %CHANNEL_MENTION% ``(id: %CHANNEL_ID%)``\n- Message: %MESSAGE_LINK%",
        color=Color.GREEN
    )