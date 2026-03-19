"""add owner_id to clients

Revision ID: a1b2c3d4e5f6
Revises: 351148a6bc96
Create Date: 2026-03-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '351148a6bc96'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'clients',
        sa.Column('owner_id', sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        'fk_clients_owner_id_users',
        'clients', 'users',
        ['owner_id'], ['id'],
    )
    op.create_index('ix_clients_owner_id', 'clients', ['owner_id'], unique=False)
    # Make non-nullable after backfill (new installs will have no existing rows)
    op.alter_column('clients', 'owner_id', nullable=False)


def downgrade() -> None:
    op.drop_index('ix_clients_owner_id', table_name='clients')
    op.drop_constraint('fk_clients_owner_id_users', 'clients', type_='foreignkey')
    op.drop_column('clients', 'owner_id')
