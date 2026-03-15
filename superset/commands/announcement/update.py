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
"""Command to update an announcement"""

import logging
from typing import Any

from superset.commands.base import BaseCommand
from superset.commands.announcement.exceptions import (
    AnnouncementNotFoundError,
    AnnouncementUpdateFailedError,
)
from superset.daos.announcement import AnnouncementDAO
from superset.models.announcement import Announcement

logger = logging.getLogger(__name__)


class UpdateAnnouncementCommand(BaseCommand):
    """Command to update an announcement"""

    def __init__(self, announcement_id: int, data: dict[str, Any]):
        self._id = announcement_id
        self._properties = data
        self._announcement: Announcement | None = None

    def run(self) -> Announcement:
        """
        Execute the update command.

        :return: The updated Announcement object
        :raises AnnouncementNotFoundError: If announcement doesn't exist
        :raises AnnouncementUpdateFailedError: If update fails
        """
        self.validate()
        try:
            announcement = AnnouncementDAO.update(self._announcement, self._properties)
            logger.info("Updated announcement with id %s", announcement.id)
            return announcement
        except Exception as ex:
            logger.exception("Error updating announcement %s", self._id)
            raise AnnouncementUpdateFailedError() from ex

    def validate(self) -> None:
        """
        Validate the announcement exists.

        :raises AnnouncementNotFoundError: If announcement doesn't exist
        """
        self._announcement = AnnouncementDAO.find_by_id(self._id)
        if not self._announcement:
            raise AnnouncementNotFoundError()
