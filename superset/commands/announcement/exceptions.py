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
"""Custom exceptions for announcement commands"""

from superset.commands.exceptions import (
    CommandException,
    CommandInvalidError,
    CreateFailedError,
    DeleteFailedError,
    ForbiddenError,
    UpdateFailedError,
)


class AnnouncementNotFoundError(CommandException):
    """Announcement not found"""

    message = "Announcement not found"


class AnnouncementInvalidError(CommandInvalidError):
    """Announcement has invalid data"""

    message = "Announcement parameters are invalid"


class AnnouncementCreateFailedError(CreateFailedError):
    """Failed to create announcement"""

    message = "Announcement could not be created"


class AnnouncementUpdateFailedError(UpdateFailedError):
    """Failed to update announcement"""

    message = "Announcement could not be updated"


class AnnouncementDeleteFailedError(DeleteFailedError):
    """Failed to delete announcement"""

    message = "Announcement could not be deleted"


class AnnouncementDeleteIntegrityError(DeleteFailedError):
    """Announcement delete failed due to integrity constraint"""

    message = "Announcement could not be deleted due to existing dependencies"


class AnnouncementForbiddenError(ForbiddenError):
    """User doesn't have permission"""

    message = "Insufficient permissions to access announcement"
