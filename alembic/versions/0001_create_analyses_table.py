"""
Revision ID: 0001_create_analyses_table
Revises: 
Create Date: 2026-01-31 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_analyses_table'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'analyses',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('job_description', sa.Text(collation='utf8mb4_general_ci'), nullable=False),
        sa.Column('risk_score', sa.Integer(), nullable=False),
        sa.Column('risk_level', sa.String(length=10), nullable=False),
        sa.Column('reasons', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4'
    )

def downgrade():
    op.drop_table('analyses')
