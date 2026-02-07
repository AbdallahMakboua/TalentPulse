"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-02-07
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Teams
    op.create_table(
        'teams',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('department', sa.String(200), server_default=''),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Employees
    op.create_table(
        'employees',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(300), nullable=False),
        sa.Column('email', sa.String(300), unique=True, nullable=False),
        sa.Column('role', sa.String(200), server_default='Individual Contributor'),
        sa.Column('seniority', sa.String(100), server_default='Mid'),
        sa.Column('tenure_months', sa.Integer, server_default='12'),
        sa.Column('team_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('teams.id'), nullable=False),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Weekly signals
    op.create_table(
        'weekly_signals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('week_start', sa.Date, nullable=False),
        sa.Column('tasks_completed', sa.Integer, server_default='0'),
        sa.Column('missed_deadlines', sa.Integer, server_default='0'),
        sa.Column('workload_items', sa.Integer, server_default='0'),
        sa.Column('cycle_time_days', sa.Float, server_default='0'),
        sa.Column('meeting_hours', sa.Float, server_default='0'),
        sa.Column('meeting_count', sa.Integer, server_default='0'),
        sa.Column('avg_meeting_length_min', sa.Float, server_default='0'),
        sa.Column('fragmentation_score', sa.Float, server_default='0'),
        sa.Column('focus_blocks', sa.Integer, server_default='0'),
        sa.Column('response_time_bucket', sa.String(30), server_default='normal'),
        sa.Column('after_hours_events', sa.Integer, server_default='0'),
        sa.Column('unique_collaborators', sa.Integer, server_default='0'),
        sa.Column('cross_team_ratio', sa.Float, server_default='0'),
        sa.Column('support_actions', sa.Integer, server_default='0'),
        sa.Column('learning_hours', sa.Float, server_default='0'),
        sa.Column('stretch_assignments', sa.Integer, server_default='0'),
        sa.Column('skill_progress', sa.Float, server_default='0'),
        sa.Column('data_quality', sa.Float, server_default='1'),
        sa.Column('source', sa.String(50), server_default='demo'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint('employee_id', 'week_start', name='uq_signal_employee_week'),
    )
    op.create_index('ix_signal_week', 'weekly_signals', ['week_start'])

    # Employee scores
    op.create_table(
        'employee_scores',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('week_start', sa.Date, nullable=False),
        sa.Column('burnout_risk', sa.Float, server_default='0'),
        sa.Column('high_pressure', sa.Float, server_default='0'),
        sa.Column('high_potential', sa.Float, server_default='0'),
        sa.Column('performance_degradation', sa.Float, server_default='0'),
        sa.Column('burnout_label', sa.String(20), server_default='Low'),
        sa.Column('pressure_label', sa.String(20), server_default='Low'),
        sa.Column('potential_label', sa.String(20), server_default='Low'),
        sa.Column('degradation_label', sa.String(20), server_default='Low'),
        sa.Column('burnout_explanation', postgresql.JSON, server_default='{}'),
        sa.Column('pressure_explanation', postgresql.JSON, server_default='{}'),
        sa.Column('potential_explanation', postgresql.JSON, server_default='{}'),
        sa.Column('degradation_explanation', postgresql.JSON, server_default='{}'),
        sa.Column('confidence', sa.Float, server_default='0.5'),
        sa.Column('limitations', sa.Text, server_default=''),
        sa.Column('cohort_size', sa.Integer, server_default='0'),
        sa.Column('fairness_warning', sa.Text, server_default=''),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.UniqueConstraint('employee_id', 'week_start', name='uq_score_employee_week'),
    )

    # Employee skills
    op.create_table(
        'employee_skills',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('employee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('employees.id'), nullable=False),
        sa.Column('skill_name', sa.String(200), nullable=False),
        sa.Column('proficiency', sa.Integer, server_default='1'),
        sa.Column('is_growing', sa.Boolean, server_default='false'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # App settings
    op.create_table(
        'app_settings',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('working_hours_start', sa.Integer, server_default='9'),
        sa.Column('working_hours_end', sa.Integer, server_default='18'),
        sa.Column('timezone', sa.String(100), server_default='America/New_York'),
        sa.Column('data_retention_days', sa.Integer, server_default='90'),
        sa.Column('demo_mode', sa.Boolean, server_default='true'),
        sa.Column('enable_graph', sa.Boolean, server_default='false'),
        sa.Column('scoring_weights', postgresql.JSON, server_default='{}'),
        sa.Column('updated_at', sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('app_settings')
    op.drop_table('employee_skills')
    op.drop_table('employee_scores')
    op.drop_index('ix_signal_week')
    op.drop_table('weekly_signals')
    op.drop_table('employees')
    op.drop_table('teams')
