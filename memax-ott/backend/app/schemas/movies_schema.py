"""Compatibility shim for older import path.

Some modules import `app.schemas.movies_schema`. The canonical module is
`app.schemas.movie_schema`.
"""

from .movie_schema import MovieCreate, MovieUpdate

__all__ = ["MovieCreate", "MovieUpdate"]

