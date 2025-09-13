"""Models package that exposes API schemas and (optionally) ORM models.

This package originally only exported Pydantic models (e.g. SongCreate), but
some parts of the codebase import `from app import models` and expect to find
SQLAlchemy ORM classes like `User`. To maintain compatibility, we re-export the
ORM classes from the sibling module `app.models` (the file `models.py`) when
available. This avoids AttributeError: module 'app.models' has no attribute 'User'.
"""

# Export API schema models
from .song import Song, SongCreate, SongUpdate, ImportRequest

# Best-effort export of ORM models from the sibling `models.py` module by path
import importlib.util
import os
from types import ModuleType

User = SongORM = Section = Line = Job = Recording = SongDraft = None  # type: ignore
try:
	here = os.path.dirname(__file__)
	orm_path = os.path.normpath(os.path.join(here, "..", "models.py"))
	if os.path.exists(orm_path):
		spec = importlib.util.spec_from_file_location("app._orm_models", orm_path)
		if spec and spec.loader:
			_orm_models = importlib.util.module_from_spec(spec)  # type: ModuleType
			spec.loader.exec_module(_orm_models)
			# Re-export commonly used ORM classes if present
			User = getattr(_orm_models, "User", None)
			SongORM = getattr(_orm_models, "Song", None)
			Section = getattr(_orm_models, "Section", None)
			Line = getattr(_orm_models, "Line", None)
			Job = getattr(_orm_models, "Job", None)
			Recording = getattr(_orm_models, "Recording", None)
			SongDraft = getattr(_orm_models, "SongDraft", None)
except Exception:
	# If loading fails (e.g., minimal Docker image), keep None placeholders.
	pass

__all__ = [
	"Song",
	"SongCreate",
	"SongUpdate",
	"ImportRequest",
	# ORM exports (may be None in minimal mode)
	"User",
	"SongORM",
	"Section",
	"Line",
	"Job",
	"Recording",
	"SongDraft",
]
