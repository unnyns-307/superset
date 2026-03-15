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
"""Command to delete announcements"""

import logging

from superset.commands.base import BaseCommand
from superset.commands.announcement.exceptions import (
    AnnouncementDeleteFailedError,
    AnnouncementDeleteIntegrityError,
    AnnouncementNotFoundError,
)
from superset.daos.announcement import AnnouncementDAO

logger = logging.getLogger(__name__)


class DeleteAnnouncementCommand(BaseCommand):
    """Command to delete one or more announcements"""

    def __init__(self, announcement_ids: list[int]):
        self._ids = announcement_ids

    def run(self) -> None:
        """
        Execute the delete command.

        :raises AnnouncementNotFoundError: If any announcement doesn't exist
        :raises AnnouncementDeleteFailedError: If deletion fails
        :raises AnnouncementDeleteIntegrityError: If integrity constraint fails
        """
        self.validate()
        try:
            for announcement_id in self._ids:
                announcement = AnnouncementDAO.find_by_id(announcement_id)
                if announcement:
                    AnnouncementDAO.delete(announcement)
                    logger.info("Deleted announcement with id %s", announcement_id)
        except Exception as ex:
            logger.exception("Error deleting announcements")
            # Check if it's an integrity error
            if "integrity constraint" in str(ex).lower():
                raise AnnouncementDeleteIntegrityError() from ex
            raise AnnouncementDeleteFailedError() from ex

    def validate(self) -> None:
        """
        Validate all announcements exist.

        :raises AnnouncementNotFoundError: If any announcement doesn't exist
        """
        for announcement_id in self._ids:
            announcement = AnnouncementDAO.find_by_id(announcement_id)
            if not announcement:
                raise AnnouncementNotFoundError()
