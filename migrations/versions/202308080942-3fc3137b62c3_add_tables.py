"""add_tables

Revision ID: 3fc3137b62c3
Revises: 0dcabf316ab9
Create Date: 2023-08-08 09:42:15.151173+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3fc3137b62c3"
down_revision = "0dcabf316ab9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("password", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_table(
        "project_users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("project_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.Enum("owner", "admin", "user", name="projectrole"), server_default="user", nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="cascade"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="cascade"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "service_users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("service", sa.Enum("datalake", "template", name="service"), nullable=False),
        sa.Column("project_user_id", sa.UUID(), nullable=False),
        sa.Column(
            "role", sa.Enum("read", "write", "comment", name="servicerole"), server_default="read", nullable=False
        ),
        sa.ForeignKeyConstraint(["project_user_id"], ["project_users.id"], ondelete="cascade"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("service"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("service_users")
    op.drop_table("project_users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    # ### end Alembic commands ###
