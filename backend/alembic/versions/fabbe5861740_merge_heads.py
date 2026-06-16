"""merge heads

Revision ID: fabbe5861740
Revises: 49ba17a6949b, efb62a646b61
Create Date: 2026-06-15 18:57:21.212262
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op



# revision identifiers, used by Alembic.
revision: str = 'fabbe5861740'
down_revision: Union[str, None] = ('49ba17a6949b', 'efb62a646b61')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
