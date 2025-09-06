"""songdocs placeholder revision

Revision ID: 0002_songdocs
Revises: 0001_initial
Create Date: 2025-09-06
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_songdocs"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op placeholder to satisfy prior DB revision; future changes can build on this
    pass


def downgrade() -> None:
    # No-op
    pass
