# Copyright (C) 2019 Intel Corporation
#  
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  
# http://www.apache.org/licenses/LICENSE-2.0
#  
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions
# and limitations under the License.
#  
#
# SPDX-License-Identifier: Apache-2.0

from requests import get


def build_prometheus_url(prometheus, name, build_number):
    url = _PROMETHEUS_URL_TPL.format(
        prometheus=prometheus,
        path=_PROMETHEUS_QUERY_PATH,
        name=name,
        build_number=build_number
    )
    return url


def fetch_metrics(url):
    response = get(url)
    response.raise_for_status()
    return response.json()


def _parse_anomalies():
    pass


_PROMETHEUS_QUERY_PATH = "/api/v1/query"
_PROMETHEUS_URL_TPL = '{prometheus}{path}?query={name}{{build_number="{build_number}"}}'