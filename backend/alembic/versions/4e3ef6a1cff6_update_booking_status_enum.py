"""Update booking status enum

Revision ID: 4e3ef6a1cff6
Revises: eaad13cf1911
Create Date: 2026-06-21 07:42:26.851940
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op



# revision identifiers, used by Alembic.
revision: str = '4e3ef6a1cff6'
down_revision: Union[str, None] = '2fff20ce2c7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing values to booking_status_enum
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE booking_status_enum ADD VALUE IF NOT EXISTS 'PAYMENT_AUTHORIZED'")
        op.execute("ALTER TYPE booking_status_enum ADD VALUE IF NOT EXISTS 'DISPATCHING'")
        op.execute("ALTER TYPE booking_status_enum ADD VALUE IF NOT EXISTS 'DRIVER_EN_ROUTE'")
        op.execute("ALTER TYPE booking_status_enum ADD VALUE IF NOT EXISTS 'DRIVER_ARRIVED'")
        op.execute("ALTER TYPE booking_status_enum ADD VALUE IF NOT EXISTS 'PASSENGER_PICKED'")


def downgrade() -> None:
    pass
