"""initial tables

Revision ID: 0001_initial
Revises: 
Create Date: 2025-09-04
"""
from alembic import op
import sqlalchemy as sa

# Alembic revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )
    op.create_table('songs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('artist', sa.String(length=255), nullable=False, server_default=''),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now())
    )
    op.create_table('sections',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('song_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('order_index', sa.Integer(), nullable=False)
    )
    op.create_table('lines',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('section_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('chords_json', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('order_index', sa.Integer(), nullable=False)
    )

def downgrade() -> None:
    op.drop_table('lines')
    op.drop_table('sections')
    op.drop_table('songs')
    op.drop_table('users')
