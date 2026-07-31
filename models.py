"""Backward-compatible model imports.

New code should import from :mod:`dietapp.models`.
"""

from dietapp.models import FoodAlternative, StoricoSpesa, User

__all__ = ["FoodAlternative", "StoricoSpesa", "User"]
