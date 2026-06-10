"""initial tables: tracks, events, users, plans

Revision ID: 0001
Revises:
Create Date: 2026-06-10

"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("rate_limit_per_minute", sa.Integer(), nullable=False),
    )
    op.create_index("ix_plans_name", "plans", ["name"], unique=True)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("plan", sa.String(), sa.ForeignKey("plans.name"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "tracks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("audio_url_hash", sa.String(), nullable=True),
        sa.Column("artist_track_hash", sa.String(), nullable=True),
        sa.Column("artist", sa.String(), nullable=True),
        sa.Column("track", sa.String(), nullable=True),
        sa.Column("key", sa.String(), nullable=True),
        sa.Column("mode", sa.String(), nullable=True),
        sa.Column("bpm", sa.Float(), nullable=True),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("confidence", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_tracks_audio_url_hash", "tracks", ["audio_url_hash"], unique=True)
    op.create_index("ix_tracks_artist_track_hash", "tracks", ["artist_track_hash"], unique=True)

    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_type", sa.String(), nullable=False),
        sa.Column("platform", sa.String(), nullable=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_events_event_type", "events", ["event_type"])


def downgrade() -> None:
    op.drop_table("events")
    op.drop_table("tracks")
    op.drop_table("users")
    op.drop_table("plans")
