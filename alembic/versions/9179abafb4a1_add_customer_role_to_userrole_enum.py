"""add_customer_role_to_userrole_enum

Revision ID: 9179abafb4a1
Revises: be3e1738eca0
Create Date: 2026-08-11 20:53:07.339028

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '9179abafb4a1'
down_revision: Union[str, Sequence[str], None] = 'be3e1738eca0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'CUSTOMER'")
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
