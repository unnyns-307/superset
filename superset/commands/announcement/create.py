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
"""Command to create an announcement"""

import logging
from typing import Any

from superset.commands.base import BaseCommand
from superset.commands.announcement.exceptions import (
    AnnouncementCreateFailedError,
    AnnouncementInvalidError,
)
from superset.daos.announcement import AnnouncementDAO
from superset.models.announcement import Announcement

logger = logging.getLogger(__name__)


class CreateAnnouncementCommand(BaseCommand):
    """Command to create an announcement"""

    def __init__(self, data: dict[str, Any]):
        self._properties = data

    def run(self) -> Announcement:
        """
        Execute the create command.

        :return: The created Announcement object
        :raises AnnouncementCreateFailedError: If creation fails
        """
        self.validate()
        try:
            announcement = AnnouncementDAO.create(self._properties)
            logger.info("Created announcement with id %s", announcement.id)
            return announcement
        except Exception as ex:
            logger.exception("Error creating announcement")
            raise AnnouncementCreateFailedError() from ex

    def validate(self) -> None:
        """
        Validate the input data.

        Additional business logic validation can go here.
        Schema validation already happened, this is for complex rules.
        """
        # Add any additional validation logic here
        # For example, check if dates make sense for the business logic
        pass
