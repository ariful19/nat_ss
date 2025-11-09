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

from typing import Any, TYPE_CHECKING

from flask import current_app as app

from sqlalchemy.engine.url import make_url, URL

from superset.commands.database.exceptions import DatabaseInvalidError
from superset.sql.parse import Table

if TYPE_CHECKING:
    from superset.databases.schemas import (
        TableMetadataColumnsResponse,
        TableMetadataForeignKeysIndexesResponse,
        TableMetadataResponse,
    )
    from superset.models.core import Database


def get_foreign_keys_metadata(
    database: Any,
    table: Table,
) -> list[TableMetadataForeignKeysIndexesResponse]:
    foreign_keys = database.get_foreign_keys(table)
    for fk in foreign_keys:
        fk["column_names"] = fk.pop("constrained_columns")
        fk["type"] = "fk"
    return foreign_keys


def get_indexes_metadata(
    database: Any,
    table: Table,
) -> list[TableMetadataForeignKeysIndexesResponse]:
    indexes = database.get_indexes(table)
    for idx in indexes:
        idx["type"] = "index"
    return indexes


def get_col_type(col: dict[Any, Any]) -> str:
    try:
        dtype = f"{col['type']}"
    except Exception:  # pylint: disable=broad-except
        # sqla.types.JSON __str__ has a bug, so using __class__.
        dtype = col["type"].__class__.__name__
    return dtype


def get_table_metadata(database: Any, table: Table) -> TableMetadataResponse:
    """
    Get table metadata information, including type, pk, fks.
    This function raises SQLAlchemyError when a schema is not found.

    :param database: The database model
    :param table: Table instance
    :return: Dict table metadata ready for API response
    """
    keys = []
    columns = database.get_columns(table)
    primary_key = database.get_pk_constraint(table)
    if primary_key and primary_key.get("constrained_columns"):
        primary_key["column_names"] = primary_key.pop("constrained_columns")
        primary_key["type"] = "pk"
        keys += [primary_key]
    foreign_keys = get_foreign_keys_metadata(database, table)
    indexes = get_indexes_metadata(database, table)
    keys += foreign_keys + indexes
    payload_columns: list[TableMetadataColumnsResponse] = []
    table_comment = database.get_table_comment(table)
    for col in columns:
        dtype = get_col_type(col)
        payload_columns.append(
            {
                "name": col["column_name"],
                "type": dtype.split("(")[0] if "(" in dtype else dtype,
                "longType": dtype,
                "keys": [k for k in keys if col["column_name"] in k["column_names"]],
                "comment": col.get("comment"),
            }
        )
    return {
        "name": table.table,
        "columns": payload_columns,
        "selectStar": database.select_star(
            table,
            indent=True,
            cols=columns,
            latest_partition=True,
        ),
        "primaryKey": primary_key,
        "foreignKeys": foreign_keys,
        "indexes": keys,
        "comment": table_comment,
    }


def _normalize_domain(domain: str | None) -> str | None:
    if not domain:
        return None
    return domain.strip().lower()


def get_current_dataset_domain() -> str | None:
    """
    Returns the domain associated with the current session/request if available.
    """
    domain: str | None = None
    try:
        from flask import session

        domain = session.get("userDomain") or session.get("domain")
    except RuntimeError:
        domain = None

    if not domain:
        try:
            from flask import request

            host = request.host or ""
            domain = host.split(":")[0] if host else None
        except RuntimeError:
            domain = None

    return _normalize_domain(domain)


def _get_domain_dataset_config(domain: str | None) -> dict[str, Any] | None:
    domain = _normalize_domain(domain)
    configs: dict[str, Any] = app.config.get("DOMAIN_DATASET_DEFAULTS", {})
    config = None

    if domain and configs:
        config = configs.get(domain)
        if not config:
            # fall back to case-insensitive match without mutating original keys
            lowered_domain = domain.lower()
            for key, value in configs.items():
                if isinstance(key, str) and key.lower() == lowered_domain:
                    config = value
                    break

    if config:
        return dict(config)

    fallback_db = app.config.get("DATASET_CREATION_DEFAULT_DBID")
    fallback_schema = app.config.get("DATASET_CREATION_DEFAULT_SCHEMA")
    if fallback_db is None and fallback_schema is None:
        return None

    return {
        "database": fallback_db,
        "schema": fallback_schema,
    }


def _lookup_database_details(identifier: Any) -> tuple[int | None, str | None]:
    if identifier is None:
        return None, None

    from superset import db as sqla  # pylint: disable=import-outside-toplevel
    from superset.models.core import Database  # pylint: disable=import-outside-toplevel

    def _from_id(db_id: int) -> tuple[int | None, str | None]:
        rec = (
            sqla.session.query(Database.id, Database.database_name)
            .filter(Database.id == db_id)
            .first()
        )
        if rec:
            # rec may be model or tuple depending on dialect
            resolved_id = rec.id if hasattr(rec, "id") else rec[0]
            resolved_name = (
                rec.database_name if hasattr(rec, "database_name") else rec[1]
            )
            return resolved_id, resolved_name
        return None, None

    def _from_name(name: str) -> tuple[int | None, str | None]:
        rec = (
            sqla.session.query(Database.id, Database.database_name)
            .filter(Database.database_name == name)
            .first()
        )
        if rec:
            resolved_id = rec.id if hasattr(rec, "id") else rec[0]
            resolved_name = (
                rec.database_name if hasattr(rec, "database_name") else rec[1]
            )
            return resolved_id, resolved_name
        return None, None

    if isinstance(identifier, dict):
        db_id = identifier.get("id") or identifier.get("db_id") or identifier.get("dbId")
        db_name = (
            identifier.get("name")
            or identifier.get("database_name")
            or identifier.get("db_name")
            or identifier.get("dbName")
        )
        if db_id and db_name:
            return int(db_id), str(db_name)
        if db_id and not db_name:
            return _from_id(int(db_id))
        if db_name and not db_id:
            return _from_name(str(db_name))
        return None, None

    if isinstance(identifier, int):
        return _from_id(identifier)

    if isinstance(identifier, str):
        value = identifier.strip()
        if not value:
            return None, None
        if value.isdigit():
            return _from_id(int(value))
        return _from_name(value)

    return None, None


def _compute_dataset_creation_defaults(domain: str | None) -> dict[str, Any] | None:
    config = _get_domain_dataset_config(domain)
    if not config:
        return None

    schema = config.get("schema")
    db_id = config.get("dbId") or config.get("db_id")
    db_name = config.get("dbName") or config.get("db_name") or config.get("display_name")
    db_identifier = (
        config.get("db")
        or config.get("database")
        or config.get("database_name")
        or config.get("connection")
    )

    lookup_source: Any | None = db_identifier
    if lookup_source is None:
        if db_id and not db_name:
            lookup_source = db_id
        elif db_name and not db_id:
            lookup_source = db_name

    if lookup_source is not None:
        resolved_id, resolved_name = _lookup_database_details(lookup_source)
        db_id = db_id or resolved_id
        db_name = db_name or resolved_name

    result: dict[str, Any] = {}
    if db_id is not None:
        result["dbId"] = int(db_id)
    if db_name:
        result["dbName"] = str(db_name)
    if schema:
        result["schema"] = str(schema)

    return result or None


def resolve_dataset_creation_defaults(domain: str | None = None) -> dict[str, Any] | None:
    """
    Returns the resolved dataset creation defaults for the provided or current domain,
    including dbId/dbName/schema when available.
    """
    normalized_domain = _normalize_domain(domain) or get_current_dataset_domain()
    cache_key = normalized_domain or "__default__"

    try:
        from flask import g

        domain_cache = g.setdefault("_dataset_creation_defaults_cache", {})
    except RuntimeError:
        domain_cache = None

    if domain_cache is not None and cache_key in domain_cache:
        return domain_cache[cache_key]

    resolved = _compute_dataset_creation_defaults(normalized_domain)

    if domain_cache is not None:
        domain_cache[cache_key] = resolved

    return resolved


def matches_dataset_creation_default_database(database: "Database") -> bool:
    defaults = resolve_dataset_creation_defaults()
    if not defaults or "dbId" not in defaults:
        return False
    return database.id == defaults["dbId"]


def matches_dataset_creation_default_schema(schema: str | None) -> bool:
    defaults = resolve_dataset_creation_defaults()
    expected_schema = defaults.get("schema") if defaults else None
    if not expected_schema or not schema:
        return False
    return schema.lower() == expected_schema.lower()


def make_url_safe(raw_url: str | URL) -> URL:
    """
    Wrapper for SQLAlchemy's make_url(), which tends to raise too detailed of
    errors, which inevitably find their way into server logs. ArgumentErrors
    tend to contain usernames and passwords, which makes them non-log-friendly
    :param raw_url:
    :return:
    """

    if isinstance(raw_url, str):
        url = raw_url.strip()
        try:
            return make_url(url)  # noqa
        except Exception as ex:
            raise DatabaseInvalidError() from ex

    else:
        return raw_url
