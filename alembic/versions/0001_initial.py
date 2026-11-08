"""Initial local domain, approvals, executions and messages.

Revision ID: 0001_initial
Revises:
"""

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tasks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("priority", sa.String(16), nullable=False),
        sa.Column("due_at", sa.String(40)),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.Column("updated_at", sa.String(40), nullable=False),
    )
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("start_at", sa.String(40), nullable=False),
        sa.Column("end_at", sa.String(40), nullable=False),
        sa.Column("timezone", sa.String(100), nullable=False),
        sa.Column("location", sa.String(200)),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("created_at", sa.String(40), nullable=False),
    )
    op.create_table(
        "reminders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("message", sa.String(500), nullable=False),
        sa.Column("scheduled_at", sa.String(40), nullable=False),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("tasks.id")),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("events.id")),
        sa.Column("delivered_at", sa.String(40)),
        sa.Column("created_at", sa.String(40), nullable=False),
    )
    op.create_table(
        "approvals",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tool_name", sa.String(80), nullable=False),
        sa.Column("arguments_json", sa.Text(), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("expires_at", sa.String(40), nullable=False),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.Column("decided_at", sa.String(40)),
    )
    op.create_table(
        "tool_executions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("outcome", sa.String(40), nullable=False),
        sa.Column("approval_id", sa.String(36)),
        sa.Column("created_at", sa.String(40), nullable=False),
    )
    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("role", sa.String(12), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.String(40), nullable=False),
    )


def downgrade():
    for name in ("messages", "tool_executions", "approvals", "reminders",
                 "events", "tasks"):
        op.drop_table(name)
