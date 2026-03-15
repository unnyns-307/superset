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
"""Schemas for announcement API validation"""

from marshmallow import fields, Schema, validates_schema, ValidationError
from marshmallow.validate import Length, OneOf

# OpenAPI spec method overrides
openapi_spec_methods_override = {
    "get": {"get": {"summary": "Get an announcement"}},
    "get_list": {
        "get": {
            "summary": "Get a list of announcements",
            "description": "Gets a list of announcements, use Rison or JSON "
            "query parameters for filtering, sorting,"
            " pagination and for selecting specific"
            " columns and metadata.",
        }
    },
    "post": {"post": {"summary": "Create an announcement"}},
    "put": {"put": {"summary": "Update an announcement"}},
    "delete": {"delete": {"summary": "Delete announcement"}},
    "info": {"get": {"summary": "Get metadata information about this API resource"}},
}

get_delete_ids_schema = {"type": "array", "items": {"type": "integer"}}

# Field descriptions
announcement_title = "The announcement title (max 500 characters)"
announcement_message = "The announcement message content"
announcement_severity = "Severity level: Critical, Warning, Info, or Success"
announcement_category = "Category: Maintenance, ProductionIssue, Upgrade, or General"
announcement_start_dttm = "Start date and time (ISO 8601 format)"
announcement_end_dttm = "End date and time (ISO 8601 format)"
announcement_status = "Status: Draft, Scheduled, Active, or Expired"
announcement_show_banner = "Whether to display as a banner"
announcement_allow_dismiss = "Whether users can dismiss the announcement"


class AnnouncementPostSchema(Schema):
    """Schema for creating announcements"""

    title = fields.String(
        metadata={"description": announcement_title},
        required=True,
        validate=[Length(min=1, max=500)],
    )
    message = fields.String(
        metadata={"description": announcement_message},
        required=True,
        validate=[Length(min=1)],
    )
    severity = fields.String(
        metadata={"description": announcement_severity},
        required=True,
        validate=OneOf(["Critical", "Warning", "Info", "Success"]),
    )
    category = fields.String(
        metadata={"description": announcement_category},
        required=True,
        validate=OneOf(["Maintenance", "ProductionIssue", "Upgrade", "General"]),
    )
    start_dttm = fields.DateTime(
        metadata={"description": announcement_start_dttm},
        required=True,
    )
    end_dttm = fields.DateTime(
        metadata={"description": announcement_end_dttm},
        required=True,
    )
    status = fields.String(
        metadata={"description": announcement_status},
        required=False,
        validate=OneOf(["Draft", "Scheduled", "Active", "Expired"]),
        load_default="Draft",
    )
    show_banner = fields.Boolean(
        metadata={"description": announcement_show_banner},
        required=False,
        load_default=True,
    )
    allow_dismiss = fields.Boolean(
        metadata={"description": announcement_allow_dismiss},
        required=False,
        load_default=True,
    )

    @validates_schema
    def validate_dates(self, data, **kwargs):
        """Validate that end_dttm is after start_dttm"""
        if data.get("start_dttm") and data.get("end_dttm"):
            if data["end_dttm"] <= data["start_dttm"]:
                raise ValidationError(
                    "End date must be after start date", field_name="end_dttm"
                )


class AnnouncementPutSchema(Schema):
    """Schema for updating announcements"""

    title = fields.String(
        metadata={"description": announcement_title},
        required=False,
        validate=[Length(min=1, max=500)],
    )
    message = fields.String(
        metadata={"description": announcement_message},
        required=False,
        validate=[Length(min=1)],
    )
    severity = fields.String(
        metadata={"description": announcement_severity},
        required=False,
        validate=OneOf(["Critical", "Warning", "Info", "Success"]),
    )
    category = fields.String(
        metadata={"description": announcement_category},
        required=False,
        validate=OneOf(["Maintenance", "ProductionIssue", "Upgrade", "General"]),
    )
    start_dttm = fields.DateTime(
        metadata={"description": announcement_start_dttm},
        required=False,
    )
    end_dttm = fields.DateTime(
        metadata={"description": announcement_end_dttm},
        required=False,
    )
    status = fields.String(
        metadata={"description": announcement_status},
        required=False,
        validate=OneOf(["Draft", "Scheduled", "Active", "Expired"]),
    )
    show_banner = fields.Boolean(
        metadata={"description": announcement_show_banner},
        required=False,
    )
    allow_dismiss = fields.Boolean(
        metadata={"description": announcement_allow_dismiss},
        required=False,
    )

    @validates_schema
    def validate_dates(self, data, **kwargs):
        """Validate that end_dttm is after start_dttm if both are provided"""
        if "start_dttm" in data and "end_dttm" in data:
            if data["end_dttm"] <= data["start_dttm"]:
                raise ValidationError(
                    "End date must be after start date", field_name="end_dttm"
                )


# Export schemas for use in API
__all__ = [
    "AnnouncementPostSchema",
    "AnnouncementPutSchema",
    "openapi_spec_methods_override",
    "get_delete_ids_schema",
]
