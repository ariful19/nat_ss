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
from __future__ import annotations

from typing import Any, List

import sqlalchemy as sqla
from flask import current_app as app, Response, session
from flask_appbuilder.api import expose, safe
from flask_login import current_user

from superset.extensions import db
from superset.models.core import Database
from superset.views.base_api import BaseSupersetApi


class OfficesRestApi(BaseSupersetApi):
    """
    Small helper API that surfaces office options (from a configured database)
    so the Dashboard Properties modal can show a multi-select when available.

    Reads configuration keys from superset_config.py:
      - DATASET_CREATION_DEFAULT_DBID (int id or str database_name)
      - DATASET_CREATION_DEFAULT_SCHEMA (str schema/database name)

    Returns 200 with enabled=False if not properly configured or table missing.
    """

    resource_name = "offices"
    allow_browser_login = True

    # Public for all authenticated roles; no specific permission required.
    @expose("/options", methods=("GET",))
    @safe
    def get_options(self) -> Response:
        # Require an authenticated session, but no specific role permission
        if not current_user or current_user.is_anonymous:
            return self.response(401, message="Unauthorized")
        # Check config presence
        dbid_or_name: Any = app.config.get("DATASET_CREATION_DEFAULT_DBID")
        schema: str | None = app.config.get("DATASET_CREATION_DEFAULT_SCHEMA")
        app.logger.info(f"Fetching office options for DB: {dbid_or_name}, Schema: {schema}")

        if not dbid_or_name or not schema:
            # Not configured – do not show selector
            return self.response(200, result={"enabled": False, "options": []})

        # Resolve Database by id or by name (case-insensitive)
        database: Database | None = None
        try:
            query = db.session.query(Database)
            # Accept numeric strings as ids
            if isinstance(dbid_or_name, int):
                database = query.filter(Database.id == dbid_or_name).one_or_none()
            else:
                value = str(dbid_or_name).strip()
                if value.isdigit():
                    database = (
                        query.filter(Database.id == int(value)).one_or_none()
                    )
                if not database and value:
                    # Case-insensitive match on database_name
                    database = (
                        query.filter(sqla.func.lower(Database.database_name) == value.lower())
                        .one_or_none()
                    )
        except Exception as ex:
            app.logger.exception("Error resolving database for offices: %s", ex)
            database = None

        if not database:
            app.logger.warning(
                "OfficesRestApi: Database not found for value '%s'", dbid_or_name
            )
            return self.response(200, result={"enabled": False, "options": []})

        # Inspect for `offices` table and fetch values
        try:
            # Use the engine context manager properly
            with database.get_sqla_engine(schema=schema) as engine:
                # log resolved DB details (safe)
                app.logger.info(
                    "OfficesRestApi: resolved DB id=%s name=%s",
                    database.id,
                    database.database_name,
                )
                qualified = f"{schema}.offices" if schema else "offices"
                app.logger.info("OfficesRestApi: querying %s", qualified)
                with engine.connect() as conn:
                    rows = conn.execute(
                        sqla.text(f"SELECT id, name FROM {qualified} ORDER BY name")
                    ).fetchall()
            options: List[dict[str, Any]] = [
                {"id": row[0], "label": row[1], "value": row[1]} for row in rows
            ]

            default_office = session.get("officeName")
            return self.response(
                200,
                result={
                    "enabled": True,
                    "options": options,
                    "defaultOffice": default_office,
                },
            )
        except Exception as ex:  # pragma: no cover - defensive fallback
            app.logger.exception("OfficesRestApi: error fetching offices: %s", ex)
            return self.response(200, result={"enabled": False, "options": []})
