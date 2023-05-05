"""empty message

Revision ID: 718072e01290
Revises: 64bbcc41ed12
Create Date: 2023-05-05 20:52:02.796419

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "718072e01290"
down_revision = "64bbcc41ed12"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=60), nullable=True),
        sa.Column("description", sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=60), nullable=True),
        sa.Column("description", sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=60), nullable=True),
        sa.Column("username", sa.String(length=60), nullable=True),
        sa.Column("first_name", sa.String(length=60), nullable=True),
        sa.Column("last_name", sa.String(length=60), nullable=True),
        sa.Column("password_hash", sa.String(length=128), nullable=True),
        sa.Column("department_id", sa.Integer(), nullable=True),
        sa.Column("role_id", sa.Integer(), nullable=True),
        sa.Column("is_admin", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["department_id"],
            ["departments.id"],
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("employees", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_employees_email"), ["email"], unique=True)
        batch_op.create_index(batch_op.f("ix_employees_first_name"), ["first_name"], unique=False)
        batch_op.create_index(batch_op.f("ix_employees_last_name"), ["last_name"], unique=False)
        batch_op.create_index(batch_op.f("ix_employees_username"), ["username"], unique=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("employees", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_employees_username"))
        batch_op.drop_index(batch_op.f("ix_employees_last_name"))
        batch_op.drop_index(batch_op.f("ix_employees_first_name"))
        batch_op.drop_index(batch_op.f("ix_employees_email"))

    op.drop_table("employees")
    op.drop_table("roles")
    op.drop_table("departments")
    # ### end Alembic commands ###
