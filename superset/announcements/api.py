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
"""Announcements REST API"""

import logging
from typing import Any

from flask import request, Response
from flask_appbuilder.api import expose, permission_name, protect, rison, safe
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_babel import ngettext
from marshmallow import ValidationError

from superset.announcements.schemas import (
    AnnouncementPostSchema,
    AnnouncementPutSchema,
    get_delete_ids_schema,
    openapi_spec_methods_override,
)
from superset.commands.announcement.create import CreateAnnouncementCommand
from superset.commands.announcement.delete import DeleteAnnouncementCommand
from superset.commands.announcement.exceptions import (
    AnnouncementCreateFailedError,
    AnnouncementDeleteFailedError,
    AnnouncementDeleteIntegrityError,
    AnnouncementInvalidError,
    AnnouncementNotFoundError,
    AnnouncementUpdateFailedError,
)
from superset.commands.announcement.update import UpdateAnnouncementCommand
from superset.constants import MODEL_API_RW_METHOD_PERMISSION_MAP, RouteMethod
from superset.extensions import event_logger
from superset.models.announcement import Announcement
from superset.views.base_api import (
    BaseSupersetModelRestApi,
    requires_json,
    statsd_metrics,
)

logger = logging.getLogger(__name__)


class AnnouncementRestApi(BaseSupersetModelRestApi):
    datamodel = SQLAInterface(Announcement)

    include_route_methods = RouteMethod.REST_MODEL_VIEW_CRUD_SET | {
        RouteMethod.RELATED,
        "bulk_delete",  # not using RouteMethod since locally defined
    }
    class_permission_name = "Announcement"
    method_permission_name = MODEL_API_RW_METHOD_PERMISSION_MAP

    resource_name = "announcement"
    allow_browser_login = True

    show_columns = [
        "id",
        "title",
        "message",
        "severity",
        "category",
        "start_dttm",
        "end_dttm",
        "status",
        "show_banner",
        "allow_dismiss",
        "created_on",
        "changed_on",
    ]
    list_columns = [
        "id",
        "title",
        "message",
        "severity",
        "category",
        "start_dttm",
        "end_dttm",
        "status",
        "show_banner",
        "allow_dismiss",
        "created_by.first_name",
        "created_by.last_name",
        "changed_by.first_name",
        "changed_by.last_name",
        "changed_on",
        "changed_on_delta_humanized",
        "created_on",
    ]
    add_columns = [
        "title",
        "message",
        "severity",
        "category",
        "start_dttm",
        "end_dttm",
        "status",
        "show_banner",
        "allow_dismiss",
    ]
    edit_columns = add_columns
    add_model_schema = AnnouncementPostSchema()
    edit_model_schema = AnnouncementPutSchema()

    order_columns = [
        "title",
        "severity",
        "category",
        "start_dttm",
        "end_dttm",
        "status",
        "created_by.first_name",
        "changed_by.first_name",
        "changed_on",
        "changed_on_delta_humanized",
        "created_on",
    ]

    apispec_parameter_schemas = {
        "get_delete_ids_schema": get_delete_ids_schema,
    }
    openapi_spec_tag = "Announcements"
    openapi_spec_methods = openapi_spec_methods_override

    @expose("/<int:pk>", methods=("DELETE",))
    @protect()
    @safe
    @statsd_metrics
    @event_logger.log_this_with_context(
        action=lambda self, *args, **kwargs: f"{self.__class__.__name__}.delete",
        log_to_statsd=False,
    )
    @permission_name("delete")
    def delete(self, pk: int) -> Response:
        """Delete an announcement.
        ---
        delete:
          summary: Delete an announcement
          parameters:
          - in: path
            schema:
              type: integer
            name: pk
            description: The announcement ID
          responses:
            200:
              description: Item deleted
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      message:
                        type: string
            404:
              $ref: '#/components/responses/404'
            422:
              $ref: '#/components/responses/422'
            500:
              $ref: '#/components/responses/500'
        """
        try:
            DeleteAnnouncementCommand([pk]).run()
            return self.response(200, message="OK")
        except AnnouncementNotFoundError:
            return self.response_404()
        except AnnouncementDeleteIntegrityError as ex:
            return self.response_422(message=str(ex))
        except AnnouncementDeleteFailedError as ex:
            logger.error(
                "Error deleting announcement %s: %s",
                self.__class__.__name__,
                str(ex),
                exc_info=True,
            )
            return self.response_422(message=str(ex))

    @expose("/", methods=("POST",))
    @protect()
    @safe
    @statsd_metrics
    @permission_name("post")
    @event_logger.log_this_with_context(
        action=lambda self, *args, **kwargs: f"{self.__class__.__name__}.post",
        log_to_statsd=False,
    )
    @requires_json
    def post(self) -> Response:
        """Create a new announcement.
        ---
        post:
          summary: Create a new announcement
          requestBody:
            description: Announcement schema
            required: true
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/{{self.__class__.__name__}}.post'
          responses:
            201:
              description: Announcement added
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      id:
                        type: number
                      result:
                        $ref: '#/components/schemas/{{self.__class__.__name__}}.post'
            400:
              $ref: '#/components/responses/400'
            401:
              $ref: '#/components/responses/401'
            404:
              $ref: '#/components/responses/404'
            500:
              $ref: '#/components/responses/500'
        """
        try:
            item = self.add_model_schema.load(request.json)
        except ValidationError as error:
            return self.response_400(message=error.messages)
        try:
            new_model = CreateAnnouncementCommand(item).run()
            return self.response(201, id=new_model.id, result=item)
        except AnnouncementNotFoundError as ex:
            return self.response_400(message=str(ex))
        except AnnouncementInvalidError as ex:
            return self.response_422(message=ex.normalized_messages())
        except AnnouncementCreateFailedError as ex:
            logger.error(
                "Error creating announcement %s: %s",
                self.__class__.__name__,
                str(ex),
                exc_info=True,
            )
            return self.response_422(message=str(ex))

    @expose("/<int:pk>", methods=("PUT",))
    @protect()
    @safe
    @statsd_metrics
    @permission_name("put")
    @event_logger.log_this_with_context(
        action=lambda self, *args, **kwargs: f"{self.__class__.__name__}.put",
        log_to_statsd=False,
    )
    @requires_json
    def put(self, pk: int) -> Response:
        """Update an announcement.
        ---
        put:
          summary: Update an announcement
          parameters:
          - in: path
            schema:
              type: integer
            name: pk
            description: The announcement ID
          requestBody:
            description: Announcement schema
            required: true
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/{{self.__class__.__name__}}.put'
          responses:
            200:
              description: Announcement changed
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      id:
                        type: number
                      result:
                        $ref: '#/components/schemas/{{self.__class__.__name__}}.put'
            400:
              $ref: '#/components/responses/400'
            401:
              $ref: '#/components/responses/401'
            404:
              $ref: '#/components/responses/404'
            500:
              $ref: '#/components/responses/500'
        """
        try:
            item = self.edit_model_schema.load(request.json)
        except ValidationError as error:
            return self.response_400(message=error.messages)
        try:
            new_model = UpdateAnnouncementCommand(pk, item).run()
            return self.response(200, id=new_model.id, result=item)
        except AnnouncementNotFoundError:
            return self.response_404()
        except AnnouncementInvalidError as ex:
            return self.response_422(message=ex.normalized_messages())
        except AnnouncementUpdateFailedError as ex:
            logger.error(
                "Error updating announcement %s: %s",
                self.__class__.__name__,
                str(ex),
                exc_info=True,
            )
            return self.response_422(message=str(ex))

    @expose("/", methods=("DELETE",))
    @protect()
    @safe
    @statsd_metrics
    @rison(get_delete_ids_schema)
    @event_logger.log_this_with_context(
        action=lambda self, *args, **kwargs: f"{self.__class__.__name__}.bulk_delete",
        log_to_statsd=False,
    )
    def bulk_delete(self, **kwargs: Any) -> Response:
        """Bulk delete announcements.
        ---
        delete:
          summary: Delete multiple announcements in a bulk operation
          parameters:
          - in: query
            name: q
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/get_delete_ids_schema'
          responses:
            200:
              description: Announcements bulk delete
              content:
                application/json:
                  schema:
                    type: object
                    properties:
                      message:
                        type: string
            401:
              $ref: '#/components/responses/401'
            404:
              $ref: '#/components/responses/404'
            422:
              $ref: '#/components/responses/422'
            500:
              $ref: '#/components/responses/500'
        """
        item_ids = kwargs["rison"]
        try:
            DeleteAnnouncementCommand(item_ids).run()
            return self.response(
                200,
                message=ngettext(
                    "Deleted %(num)d announcement",
                    "Deleted %(num)d announcements",
                    num=len(item_ids),
                ),
            )
        except AnnouncementNotFoundError:
            return self.response_404()
        except AnnouncementDeleteIntegrityError as ex:
            return self.response_422(message=str(ex))
        except AnnouncementDeleteFailedError as ex:
            return self.response_422(message=str(ex))
