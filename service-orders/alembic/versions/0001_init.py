from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('items', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='created'),
        sa.Column('total_amount', sa.Numeric(12, 2), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        schema='orders',
    )
    op.create_index('ix_orders_user_id', 'orders', ['user_id'], unique=False, schema='orders')
    op.create_foreign_key(
        'fk_orders_user_id_users_users',
        'orders', 'users', ['user_id'], ['id'],
        source_schema='orders', referent_schema='users', ondelete='RESTRICT'
    )


def downgrade() -> None:
    op.drop_constraint('fk_orders_user_id_users_users', 'orders', schema='orders', type_='foreignkey')
    op.drop_index('ix_orders_user_id', table_name='orders', schema='orders')
    op.drop_table('orders', schema='orders')
