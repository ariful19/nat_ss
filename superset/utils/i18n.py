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

from collections.abc import Mapping
from typing import Any

from flask_babel import get_locale


def get_locale_code() -> str | None:
    """
    Return the active Babel locale as a string (e.g. ``"en"`` or ``"bn"``).

    Returns ``None`` when no locale is active.
    """

    locale = get_locale()
    if not locale:
        return None
    return str(locale)


def normalize_i18n_dict(value: Any) -> dict[str, str]:
    """
    Validate and normalize an i18n dictionary.

    Expected shape: { "<locale>": "<label>" }

    Raises ``ValueError`` if the payload is not a mapping of strings.
    """

    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError("i18n value must be a mapping of locale -> string")

    normalized: dict[str, str] = {}
    for locale_key, label in value.items():
        if not isinstance(locale_key, str):
            raise ValueError("i18n locale keys must be strings")
        if not isinstance(label, str):
            raise ValueError("i18n values must be strings")
        normalized[locale_key] = label
    return normalized


def resolve_i18n_label(
    translations: Mapping[str, str] | None,
    fallback: str | None,
    locale: str | None,
) -> str | None:
    """
    Resolve a translated label with the fallback rule described in
    ``docs/chart-i18n-plan.md``:

    ``label[locale] -> label['en'] -> fallback``.
    """

    if translations:
        if locale and translations.get(locale):
            return translations[locale]
        if translations.get("en"):
            return translations["en"]
    return fallback
