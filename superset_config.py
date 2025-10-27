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

"""
Local Superset configuration

This file is discovered by Superset via the SUPERSET_CONFIG_PATH environment
variable. It overrides defaults in superset/config.py.

Changes included below reflect local customizations previously made directly
in superset/config.py by ariful19, now moved here to keep the upstream file clean:
 - Enable embedded dashboards (FEATURE_FLAGS["EMBEDDED_SUPERSET"] = True)
 - Extend CORS settings and allow credentials
 - Harden session/CSRF cookies for cross-site embedding
"""

import os
from typing import Any, Dict

# Enable English and Bangla translations using bundled Babel assets
BABEL_DEFAULT_LOCALE = "en"
BABEL_DEFAULT_FOLDER = "superset/translations"
LANGUAGES = {
    "en": {"flag": "us", "name": "English"},
    "bn": {"flag": "bd", "name": "Bangla"},
}

# Use secret from environment if provided (recommended for production)
SECRET_KEY = os.getenv("SUPERSET_SECRET_KEY", "CHANGE_ME_SUPERSET")

# Feature flags overrides
FEATURE_FLAGS = {
    # Enable embedding dashboards via the embedded SDK
    "EMBEDDED_SUPERSET": True,
    # Enable per-dashboard role-based access control
    "DASHBOARD_RBAC": True,
    # Toggle AI chart suggestions (Gemini-backed with fallback)
    # Can be overridden via env var AI_CHART_SUGGESTIONS=0/1/true/false
    "AI_CHART_SUGGESTIONS": os.getenv("AI_CHART_SUGGESTIONS", "1").lower()
    in ("1", "true", "yes", "on"),
    "ENABLE_ECHARTS_TIME_SERIES": True,
    "ENABLE_ADVANCED_DATA_ANALYSIS": True,
    "ENABLE_REACT_CRUD_VIEWS": True,
}

# The name of the admin role in your deployment
# Default upstream is 'Admin'; this instance uses 'Superset Admin'
AUTH_ROLE_ADMIN = "Superset Admin"

# CORS settings overrides
# Note: tailor origins to your environment as needed.
CORS_OPTIONS = {
    "origins": [
        "https://tile.openstreetmap.org",
        "https://tile.osm.ch",
        "http://127.0.0.1:8082",
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    "http://localhost:8000",
    ],
    "supports_credentials": True,
}

# Cookie and CSRF settings for cross-site embedding (requires HTTPS in browsers)
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "None"  # allow cross-site iframes
SESSION_SERVER_SIDE = False
CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = True

# For local HTTP testing you can export SUPERSET_DEV_INSECURE_COOKIES=1
if os.getenv("SUPERSET_DEV_INSECURE_COOKIES") == "1":
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

# Exempt our internal auto-provision login endpoint from CSRF for in-house posting
try:
    from superset.config import WTF_CSRF_EXEMPT_LIST as _EX
except Exception:  # pragma: no cover
    _EX = []

WTF_CSRF_EXEMPT_LIST = list(_EX) + [
    # name follows the module.view.function import path used elsewhere
    "superset.views.core.provision_user_login",
]

# --------------------------------------------------------------------
# Dataset creation defaults (set here, not via env vars).
#
# These values are exposed to the frontend bootstrap under
# `common.dataset_creation_defaults` and used to auto-lock the
# Database and Schema selectors for non-admin users on the
# Create Dataset page. Admins keep full access.
#
# How to configure:
# - Set both to enable locking for non-admins.
# - Leave either as None to disable.
#
# Example:
# DATASET_CREATION_DEFAULT_DBID = 1
# DATASET_CREATION_DEFAULT_SCHEMA = "public"
# --------------------------------------------------------------------
DATASET_CREATION_DEFAULT_DBID: int | None | str = "rms"
DATASET_CREATION_DEFAULT_SCHEMA: str | None = "report_rms"


def _common_overrides(data: Dict[str, Any]) -> Dict[str, Any]:
    """Inject dataset creation defaults into bootstrap common payload.

    Returns a shallow dict to be merged into `bootstrap_data.common`.
    """
    defaults: Dict[str, Any] = {}
    db_id_value = DATASET_CREATION_DEFAULT_DBID
    db_name_value = None

    # Resolve database by name if a string was provided
    try:
        if isinstance(db_id_value, str) and db_id_value:
            from superset.models.core import Database  # type: ignore
            from superset import db as sqla  # type: ignore

            rec = (
                sqla.session.query(Database.id, Database.database_name)
                .filter(Database.database_name == db_id_value)
                .first()
            )
            if rec:
                db_id_value = rec.id if hasattr(rec, "id") else rec[0]
                db_name_value = (
                    rec.database_name if hasattr(rec, "database_name") else rec[1]
                )
        elif isinstance(db_id_value, int):
            # Also fetch name for display, if possible
            from superset.models.core import Database  # type: ignore
            from superset import db as sqla  # type: ignore

            rec = (
                sqla.session.query(Database.id, Database.database_name)
                .filter(Database.id == db_id_value)
                .first()
            )
            if rec:
                db_name_value = (
                    rec.database_name if hasattr(rec, "database_name") else rec[1]
                )
    except Exception:
        # Swallow lookup errors; we simply won't provide defaults then
        pass

    if isinstance(db_id_value, int):
        defaults["dbId"] = db_id_value
        if db_name_value:
            defaults["dbName"] = db_name_value
    if DATASET_CREATION_DEFAULT_SCHEMA:
        defaults["schema"] = DATASET_CREATION_DEFAULT_SCHEMA

    # Only add the key when something is configured
    if defaults:
        return {"dataset_creation_defaults": defaults}
    return {}


# Expose the override hook to Superset so the frontend can read defaults.
COMMON_BOOTSTRAP_OVERRIDES_FUNC = _common_overrides
