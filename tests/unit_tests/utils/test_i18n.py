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

import pytest

from superset.utils.i18n import normalize_i18n_dict, resolve_i18n_label


def test_normalize_i18n_dict() -> None:
    payload = {"en": "Sales", "bn": "রাজস্ব"}
    normalized = normalize_i18n_dict(payload)
    assert normalized["en"] == "Sales"
    assert normalized["bn"] == "রাজস্ব"


@pytest.mark.parametrize("payload", ["bad", {"en": 1}, None])
def test_normalize_i18n_dict_rejects(payload) -> None:
    with pytest.raises(ValueError):
        normalize_i18n_dict(payload)


def test_resolve_i18n_label_fallbacks() -> None:
    translations = {"en": "Sales", "bn": "বিক্রয়"}
    assert resolve_i18n_label(translations, "Sales", "bn") == "বিক্রয়"
    assert resolve_i18n_label(translations, "Sales", "fr") == "Sales"
    assert resolve_i18n_label(None, "Default", "bn") == "Default"
