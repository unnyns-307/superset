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
"""Announcement model for system-wide announcements"""

from typing import Any

from flask_appbuilder import Model
from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, Text

from superset.models.helpers import AuditMixinNullable


class Announcement(Model, AuditMixinNullable):
    """System-wide announcement model for displaying banners and notifications"""

    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(
        Enum("Critical", "Warning", "Info", "Success", name="announcement_severity"),
        nullable=False,
        default="Info",
    )
    category = Column(
        Enum(
            "Maintenance",
            "ProductionIssue",
            "Upgrade",
            "General",
            name="announcement_category",
        ),
        nullable=False,
        default="General",
    )
    start_dttm = Column(DateTime, nullable=False)
    end_dttm = Column(DateTime, nullable=False)
    status = Column(
        Enum("Draft", "Scheduled", "Active", "Expired", name="announcement_status"),
        nullable=False,
        default="Draft",
    )
    show_banner = Column(Boolean, default=True, nullable=False)
    allow_dismiss = Column(Boolean, default=True, nullable=False)

    @property
    def data(self) -> dict[str, Any]:
        """Return announcement data as dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "severity": self.severity,
            "category": self.category,
            "start_dttm": self.start_dttm,
            "end_dttm": self.end_dttm,
            "status": self.status,
            "show_banner": self.show_banner,
            "allow_dismiss": self.allow_dismiss,
            "created_on": self.created_on,
            "changed_on": self.changed_on,
            "created_by": self.created_by.username if self.created_by else None,
            "changed_by": self.changed_by.username if self.changed_by else None,
        }

    def __repr__(self) -> str:
        return f"<Announcement {self.id}: {self.title}>"
