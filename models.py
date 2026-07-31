"""Backward-compatible model imports.

New code should import from :mod:`dietapp.models`.
"""

from dietapp.models import StoricoSpesa, User

__all__ = ["StoricoSpesa", "User"]
