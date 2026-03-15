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
"""Data Access Object for Announcement model"""

import logging
from typing import Optional

from superset.daos.base import BaseDAO
from superset.extensions import db
from superset.models.announcement import Announcement

logger = logging.getLogger(__name__)


class AnnouncementDAO(BaseDAO):
    """Data Access Object for Announcement model"""

    model_cls = Announcement

    @staticmethod
    def create(properties: dict, commit: bool = True) -> Announcement:
        """
        Create a new announcement.

        :param properties: Dictionary of announcement properties
        :param commit: Whether to commit the transaction
        :return: The created Announcement object
        """
        announcement = Announcement(**properties)
        db.session.add(announcement)
        if commit:
            db.session.commit()
        return announcement

    @staticmethod
    def update(
        announcement: Announcement, properties: dict, commit: bool = True
    ) -> Announcement:
        """
        Update an existing announcement.

        :param announcement: The announcement to update
        :param properties: Dictionary of properties to update
        :param commit: Whether to commit the transaction
        :return: The updated Announcement object
        """
        for key, value in properties.items():
            if hasattr(announcement, key):
                setattr(announcement, key, value)
        if commit:
            db.session.commit()
        return announcement

    @staticmethod
    def delete(announcement: Announcement, commit: bool = True) -> None:
        """
        Delete an announcement.

        :param announcement: The announcement to delete
        :param commit: Whether to commit the transaction
        """
        db.session.delete(announcement)
        if commit:
            db.session.commit()

    @staticmethod
    def find_by_id(announcement_id: int) -> Optional[Announcement]:
        """
        Find announcement by ID.

        :param announcement_id: The announcement ID
        :return: Announcement object or None
        """
        return db.session.query(Announcement).filter_by(id=announcement_id).first()

    @staticmethod
    def find_active() -> list[Announcement]:
        """
        Find all active announcements.

        :return: List of active announcements
        """
        from datetime import datetime

        now = datetime.utcnow()
        return (
            db.session.query(Announcement)
            .filter(
                Announcement.status == "Active",
                Announcement.show_banner.is_(True),
                Announcement.start_dttm <= now,
                Announcement.end_dttm >= now,
            )
            .order_by(
                # Order by severity: Critical > Warning > Info > Success
                db.case(
                    (Announcement.severity == "Critical", 1),
                    (Announcement.severity == "Warning", 2),
                    (Announcement.severity == "Info", 3),
                    (Announcement.severity == "Success", 4),
                    else_=5,
                ),
                Announcement.start_dttm.desc(),
            )
            .all()
        )
