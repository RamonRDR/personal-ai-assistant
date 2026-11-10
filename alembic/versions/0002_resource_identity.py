"""Bind approvals to immutable resource identities on existing databases.

Revision ID: 0002_resource_identity
Revises: 0001_initial
"""

from uuid import uuid4

from alembic import op
import sqlalchemy as sa

revision = "0002_resource_identity"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("tasks", sa.Column("resource_identity", sa.String(36), nullable=True))
    op.add_column("events", sa.Column("resource_identity", sa.String(36), nullable=True))
    op.add_column("approvals", sa.Column("resource_identity", sa.String(36), nullable=True))

    connection = op.get_bind()
    for table in ("tasks", "events"):
        for (identifier,) in connection.execute(sa.text(f"SELECT id FROM {table}")):
            connection.execute(
                sa.text(f"UPDATE {table} SET resource_identity = :identity WHERE id = :id"),
                {"identity": str(uuid4()), "id": identifier},
            )
        op.create_index(f"ix_{table}_resource_identity", table, ["resource_identity"], unique=True)

    # Outstanding legacy approvals lack an identity and must fail closed.


def downgrade():
    for table in ("events", "tasks"):
        op.drop_index(f"ix_{table}_resource_identity", table_name=table)
    op.drop_column("approvals", "resource_identity")
    op.drop_column("events", "resource_identity")
    op.drop_column("tasks", "resource_identity")
