"""add_actions_and_impact_records

Revision ID: 4b51ccd67890
Revises: 3ac4acc4cef6
Create Date: 2026-09-01 19:35:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b51ccd67890'
down_revision: Union[str, None] = '3ac4acc4cef6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Actions Table
    op.create_table(
        'actions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('equipment_id', sa.String(length=50), nullable=False),
        sa.Column('recommendation_id', sa.Integer(), nullable=True),
        sa.Column('alert_id', sa.Integer(), nullable=True),
        sa.Column('action_type', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('priority', sa.String(length=50), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('actor', sa.String(length=100), nullable=False),
        sa.Column('payload_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recommendation_id'], ['recommendations.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['alert_id'], ['alerts.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_actions_action_type'), 'actions', ['action_type'], unique=False)
    op.create_index(op.f('ix_actions_created_at'), 'actions', ['created_at'], unique=False)
    op.create_index(op.f('ix_actions_equipment_id'), 'actions', ['equipment_id'], unique=False)
    op.create_index(op.f('ix_actions_id'), 'actions', ['id'], unique=False)
    op.create_index(op.f('ix_actions_priority'), 'actions', ['priority'], unique=False)
    op.create_index(op.f('ix_actions_status'), 'actions', ['status'], unique=False)
    op.create_index(op.f('ix_actions_recommendation_id'), 'actions', ['recommendation_id'], unique=False)
    op.create_index(op.f('ix_actions_alert_id'), 'actions', ['alert_id'], unique=False)

    # 2. Create Impact Records Table
    op.create_table(
        'impact_records',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('action_id', sa.Integer(), nullable=True),
        sa.Column('equipment_id', sa.String(length=50), nullable=False),
        sa.Column('site_id', sa.String(length=50), nullable=True),
        sa.Column('impact_type', sa.String(length=100), nullable=False),
        sa.Column('estimated_amount', sa.Float(), nullable=False),
        sa.Column('realized_amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('calculation_basis', sa.Text(), nullable=False),
        sa.Column('before_state', sa.JSON(), nullable=True),
        sa.Column('after_state', sa.JSON(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['action_id'], ['actions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['equipment_id'], ['equipment.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['site_id'], ['sites.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_impact_records_action_id'), 'impact_records', ['action_id'], unique=False)
    op.create_index(op.f('ix_impact_records_calculated_at'), 'impact_records', ['calculated_at'], unique=False)
    op.create_index(op.f('ix_impact_records_equipment_id'), 'impact_records', ['equipment_id'], unique=False)
    op.create_index(op.f('ix_impact_records_id'), 'impact_records', ['id'], unique=False)
    op.create_index(op.f('ix_impact_records_impact_type'), 'impact_records', ['impact_type'], unique=False)
    op.create_index(op.f('ix_impact_records_site_id'), 'impact_records', ['site_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_impact_records_site_id'), table_name='impact_records')
    op.drop_index(op.f('ix_impact_records_impact_type'), table_name='impact_records')
    op.drop_index(op.f('ix_impact_records_id'), table_name='impact_records')
    op.drop_index(op.f('ix_impact_records_equipment_id'), table_name='impact_records')
    op.drop_index(op.f('ix_impact_records_calculated_at'), table_name='impact_records')
    op.drop_index(op.f('ix_impact_records_action_id'), table_name='impact_records')
    op.drop_table('impact_records')

    op.drop_index(op.f('ix_actions_alert_id'), table_name='actions')
    op.drop_index(op.f('ix_actions_recommendation_id'), table_name='actions')
    op.drop_index(op.f('ix_actions_status'), table_name='actions')
    op.drop_index(op.f('ix_actions_priority'), table_name='actions')
    op.drop_index(op.f('ix_actions_id'), table_name='actions')
    op.drop_index(op.f('ix_actions_equipment_id'), table_name='actions')
    op.drop_index(op.f('ix_actions_created_at'), table_name='actions')
    op.drop_index(op.f('ix_actions_action_type'), table_name='actions')
    op.drop_table('actions')
