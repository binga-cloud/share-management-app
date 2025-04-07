"""Initial migration with proper constraints

Revision ID: d88d1346aee2
Revises: 
Create Date: 2025-04-07 10:11:06.980712

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd88d1346aee2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=100), nullable=False),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('bonus_shares',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('item_name', sa.String(length=100), nullable=False),
    sa.Column('bonus_date', sa.Date(), nullable=False),
    sa.Column('bonus_quantity', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_purchase_user'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('dividend',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('item_name', sa.String(length=100), nullable=False),
    sa.Column('dividend_amount', sa.Float(), nullable=False),
    sa.Column('dividend_date', sa.Date(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_purchase_user'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('ipo_shares',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('item_name', sa.String(length=100), nullable=False),
    sa.Column('ipo_date', sa.Date(), nullable=False),
    sa.Column('ipo_quantity', sa.Integer(), nullable=False),
    sa.Column('ipo_rate', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_purchase_user'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('share_purchase',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('item_name', sa.String(length=100), nullable=False),
    sa.Column('buy_date', sa.Date(), nullable=False),
    sa.Column('buy_quantity', sa.Integer(), nullable=False),
    sa.Column('buy_rate', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_purchase_user'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('share_sale',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('item_name', sa.String(length=100), nullable=False),
    sa.Column('sell_date', sa.Date(), nullable=False),
    sa.Column('sell_quantity', sa.Integer(), nullable=False),
    sa.Column('sell_rate', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_purchase_user'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('share_sale')
    op.drop_table('share_purchase')
    op.drop_table('ipo_shares')
    op.drop_table('dividend')
    op.drop_table('bonus_shares')
    op.drop_table('user')
    op.drop_table('item')
    # ### end Alembic commands ###
