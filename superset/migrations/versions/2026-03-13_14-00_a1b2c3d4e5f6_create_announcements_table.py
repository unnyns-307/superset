# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""Create announcements table for system-wide announcements

Revision ID: a1b2c3d4e5f6
Revises: 4b2a8c9d3e1f
Create Date: 2026-03-13 14:00:00.000000

"""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
)

from superset.migrations.shared.utils import (
    create_fks_for_table,
    create_index,
    create_table,
    drop_fks_for_table,
    drop_index,
    drop_table,
)

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "4b2a8c9d3e1f"

ANNOUNCEMENTS_TABLE = "announcements"


def upgrade():
    """
    Create announcements table for system-wide announcements.
    
    This table supports:
    - Scheduled announcements with start/end dates
    - Multiple severity levels (Critical, Warning, Info, Success)
    - Categories (Maintenance, ProductionIssue, Upgrade, General)
    - Status tracking (Draft, Scheduled, Active, Expired)
    - Banner display configuration
    """
    
    # Create announcements table
    create_table(
        ANNOUNCEMENTS_TABLE,
        Column("id", Integer, primary_key=True),
        Column("title", String(500), nullable=False),
        Column("message", Text, nullable=False),
        Column(
            "severity",
            String(20),
            nullable=False,
            server_default="Info",
        ),
        Column(
            "category",
            String(20),
            nullable=False,
            server_default="General",
        ),
        Column("start_dttm", DateTime, nullable=False),
        Column("end_dttm", DateTime, nullable=False),
        Column(
            "status",
            String(20),
            nullable=False,
            server_default="Draft",
        ),
        Column("show_banner", Boolean, nullable=False, server_default="1"),
        Column("allow_dismiss", Boolean, nullable=False, server_default="1"),
        # AuditMixinNullable columns
        Column("created_on", DateTime, nullable=True),
        Column("changed_on", DateTime, nullable=True),
        Column("created_by_fk", Integer, nullable=True),
        Column("changed_by_fk", Integer, nullable=True),
    )

    # Create indexes for optimal query performance
    create_index(ANNOUNCEMENTS_TABLE, "idx_announcements_status", ["status"])
    create_index(ANNOUNCEMENTS_TABLE, "idx_announcements_severity", ["severity"])
    create_index(ANNOUNCEMENTS_TABLE, "idx_announcements_start_dttm", ["start_dttm"])
    create_index(ANNOUNCEMENTS_TABLE, "idx_announcements_end_dttm", ["end_dttm"])
    create_index(
        ANNOUNCEMENTS_TABLE,
        "idx_announcements_active",
        ["status", "start_dttm", "end_dttm", "show_banner"],
    )

    # Create foreign key constraints for audit fields
    create_fks_for_table(
        foreign_key_name="fk_announcements_created_by_fk_ab_user",
        table_name=ANNOUNCEMENTS_TABLE,
        referenced_table="ab_user",
        local_cols=["created_by_fk"],
        remote_cols=["id"],
        ondelete="SET NULL",
    )

    create_fks_for_table(
        foreign_key_name="fk_announcements_changed_by_fk_ab_user",
        table_name=ANNOUNCEMENTS_TABLE,
        referenced_table="ab_user",
        local_cols=["changed_by_fk"],
        remote_cols=["id"],
        ondelete="SET NULL",
    )


def downgrade():
    """
    Drop announcements table and all related indexes and foreign keys.
    """
    # Drop foreign keys first
    drop_fks_for_table(
        ANNOUNCEMENTS_TABLE,
        [
            "fk_announcements_created_by_fk_ab_user",
            "fk_announcements_changed_by_fk_ab_user",
        ],
    )

    # Drop indexes
    drop_index(ANNOUNCEMENTS_TABLE, "idx_announcements_status")
    drop_index(ANNOUNCEMENTS_TABLE, "idx_announcements_severity")
    drop_index(ANNOUNCEMENTS_TABLE, "idx_announcements_start_dttm")
    drop_index(ANNOUNCEMENTS_TABLE, "idx_announcements_end_dttm")
    drop_index(ANNOUNCEMENTS_TABLE, "idx_announcements_active")

    # Drop the table
    drop_table(ANNOUNCEMENTS_TABLE)
