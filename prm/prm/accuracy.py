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
from math import inf

_PROMETHEUS_QUERY_PATH = "/api/v1/query"
_PROMETHEUS_QUERY_RANGE_PATH = "/api/v1/query_range"
_PROMETHEUS_URL_TPL = '{prometheus}{path}?query={name}{{build_number="{build_number}"'
_PROMETHEUS_TIME_TPL = '&start={start}&end={end}&step=1s'
_PROMETHEUS_TAG_TPL = ',{key}="{value}"'


def build_prometheus_url(prometheus, name, build_number, window_size=None, event_time=None,
                         tags=dict()):
    path = _PROMETHEUS_QUERY_PATH
    time_range = ''

    # Some variables need to be overwritten for range queries.
    if window_size and event_time:
        offset = window_size / 2
        time_range = _PROMETHEUS_TIME_TPL.format(
            start=event_time - offset,
            end=event_time + offset)
        path = _PROMETHEUS_QUERY_RANGE_PATH

    url = _PROMETHEUS_URL_TPL.format(
        prometheus=prometheus,
        path=path,
        name=name,
        build_number=build_number
    )

    # Prepare additional tags for query.
    query_tags = []
    for k, v in tags.items():
        query_tags.append(_PROMETHEUS_TAG_TPL.format(key=k, value=v))
    query_tags_str = ''.join(query_tags)

    # Build final URL from all the components.
    url = ''.join([url, query_tags_str, "}", time_range])

    return url


def fetch_metrics(url):
    response = get(url)
    response.raise_for_status()
    return response.json()


def calculate_components(anomalies, prometheus, build_number, violation_window_size):
    slo_violations_url = build_prometheus_url(prometheus, 'sli>slo', build_number)
    slo_violations_metrics = fetch_metrics(slo_violations_url)
    slo_violations = 0
    for metric in slo_violations_metrics['data']['result']:
        slo_violations += len(metric['values'])

    true_positives = 0
    anomalies_found = 0
    for metric in anomalies['data']['result']:
        for anomaly in metric['values']:
            anomalies_found += 1
            anomaly_slo_violations_url = build_prometheus_url(prometheus, 'sli>slo', build_number, event_time=anomaly[0], window_size=violation_window_size)
            anomaly_slo_violations = fetch_metrics(anomaly_slo_violations_url)
            for _ in anomaly_slo_violations['data']['result']:
                true_positives += 1

            pass

    return true_positives, anomalies_found, slo_violations


def calculate_precision_and_recall(true_positives, anomalies_found, slo_violations):
    precision = 0
    recall = 0
    if anomalies_found == 0:
        precision = -1
    else:
        precision = true_positives/anomalies_found
        
    if slo_violations == 0:
        recall = -1
    else:
        recall = true_positives/slo_violations

    return precision, recall

