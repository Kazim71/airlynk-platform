"""add booking geo columns and seed roles

Revision ID: c1a2b3d4e5f6
Revises: 4cb4fdb1e1e5
Create Date: 2026-06-23 18:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c1a2b3d4e5f6"
down_revision: str | None = "4cb4fdb1e1e5"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add geo coordinate columns to bookings table
    op.add_column(
        "bookings",
        sa.Column("pickup_lat", sa.Numeric(10, 6), nullable=False, server_default="0.0"),
    )
    op.add_column(
        "bookings",
        sa.Column("pickup_lng", sa.Numeric(10, 6), nullable=False, server_default="0.0"),
    )
    op.add_column(
        "bookings",
        sa.Column("dropoff_lat", sa.Numeric(10, 6), nullable=False, server_default="0.0"),
    )
    op.add_column(
        "bookings",
        sa.Column("dropoff_lng", sa.Numeric(10, 6), nullable=False, server_default="0.0"),
    )

    # Seed required roles that are missing
    op.execute("""
        INSERT INTO roles (id, name, created_at, updated_at)
        VALUES
            (gen_random_uuid(), 'customer', NOW(), NOW()),
            (gen_random_uuid(), 'driver', NOW(), NOW()),
            (gen_random_uuid(), 'platform_admin', NOW(), NOW()),
            (gen_random_uuid(), 'security_admin', NOW(), NOW())
        ON CONFLICT (name) DO NOTHING;
    """)


def downgrade() -> None:
    op.drop_column("bookings", "dropoff_lng")
    op.drop_column("bookings", "dropoff_lat")
    op.drop_column("bookings", "pickup_lng")
    op.drop_column("bookings", "pickup_lat")

    op.execute("DELETE FROM roles WHERE name IN ('customer', 'driver', 'platform_admin', 'security_admin');")
