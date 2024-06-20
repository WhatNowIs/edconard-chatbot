"""Added email template and update OTP schema

Revision ID: d12922852875
Revises: 3a60c2715079
Create Date: 2024-06-19 14:23:59.665394

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd12922852875'
down_revision: Union[str, None] = '3a60c2715079'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('email_templates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('subject', sa.String(), nullable=True),
    sa.Column('content', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_email_templates_id'), 'email_templates', ['id'], unique=False)
    op.create_index(op.f('ix_email_templates_name'), 'email_templates', ['name'], unique=True)
    op.create_table('email_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_email_types_id'), 'email_types', ['id'], unique=False)
    op.create_index(op.f('ix_email_types_type'), 'email_types', ['type'], unique=True)
    op.add_column('otp', sa.Column('email', sa.String(), nullable=True))
    op.add_column('otp', sa.Column('email_template_id', sa.Integer(), nullable=True))
    op.add_column('otp', sa.Column('email_type_id', sa.Integer(), nullable=True))
    op.add_column('otp', sa.Column('expires_at', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_otp_email'), 'otp', ['email'], unique=False)
    op.create_foreign_key(None, 'otp', 'email_types', ['email_type_id'], ['id'])
    op.create_foreign_key(None, 'otp', 'email_templates', ['email_template_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'otp', type_='foreignkey')
    op.drop_constraint(None, 'otp', type_='foreignkey')
    op.drop_index(op.f('ix_otp_email'), table_name='otp')
    op.drop_column('otp', 'expires_at')
    op.drop_column('otp', 'email_type_id')
    op.drop_column('otp', 'email_template_id')
    op.drop_column('otp', 'email')
    op.drop_index(op.f('ix_email_types_type'), table_name='email_types')
    op.drop_index(op.f('ix_email_types_id'), table_name='email_types')
    op.drop_table('email_types')
    op.drop_index(op.f('ix_email_templates_name'), table_name='email_templates')
    op.drop_index(op.f('ix_email_templates_id'), table_name='email_templates')
    op.drop_table('email_templates')
    # ### end Alembic commands ###