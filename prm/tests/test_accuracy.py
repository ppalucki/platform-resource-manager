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


from json import loads
from unittest.mock import Mock
from os.path import dirname, join

import prm
import pytest
from prm.accuracy import build_prometheus_url, calculate_components, calculate_precision_and_recall


@pytest.mark.parametrize('prometheus,name,build_number,window_size,event_time,tags,expected_url', [
    ('http://10.0.0.1', 'metric_name', 1, None, None, dict(),
     'http://10.0.0.1/api/v1/query?query=metric_name{build_number="1"}'),
    ('http://10.0.0.1', 'metric_name', 1, 5, 10, dict(),
     'http://10.0.0.1/api/v1/query_range?query=metric_name{build_number="1"}'
     '&start=7.5&end=12.5&step=1s'),
    ('http://10.0.0.1', 'metric_name', 1, 5, 10, {"a": "b", "c": "d"},
     'http://10.0.0.1/api/v1/query_range?query=metric_name{build_number="1",a="b",c="d"}'
     '&start=7.5&end=12.5&step=1s')
])
def test_build_prometheus_url(prometheus, name, build_number, window_size,
                              event_time, tags, expected_url):
    assert expected_url == build_prometheus_url(prometheus, name, build_number,
                                                window_size, event_time, tags)


def _dict_from_json(path):
    with open(join(dirname(__file__), path)) as f:
        return loads(f.read())


@pytest.mark.parametrize(
    'anomalies,fetched_data,build_prometheus_url_calls,expected_true_positives,'
    'expected_anomalies_found,expected_real_positives',
    [
        # 3 anomalies, no matching SLO violations and 6 SLO violations overall
        (
                _dict_from_json('accuracy/anomalies.json'),
                [
                    _dict_from_json('accuracy/slo_violations.json'),
                    _dict_from_json('accuracy/empty_results.json'),
                    _dict_from_json('accuracy/empty_results.json'),
                    _dict_from_json('accuracy/empty_results.json'),
                ],
                [
                    [('irrelevant', 'sli>slo', 1),
                     {"window_size": 10, "event_time": 1552484541.644,
                      "tags": {"workload_instance": "cassandra_stress--default--14--9142"}}],
                    [('irrelevant', 'sli>slo', 1),
                     {"window_size": 10, "event_time": 1552484741.644,
                      "tags": {"workload_instance": "twemcache_mutilate--big--14--11213"}}],
                    [('irrelevant', 'sli>slo', 1),
                     {"window_size": 10, "event_time": 1552484941.644,
                      "tags": {"workload_instance": "twemcache_mutilate--big--14--11213"}}],
                ], 0, 3, 6),
        # 3 anomalies, 1 matching SLO violation and 6 SLO violations overall
        (
                _dict_from_json('accuracy/anomalies.json'),
                [
                    _dict_from_json('accuracy/slo_violations.json'),
                    _dict_from_json('accuracy/slo_violation.json'),
                    _dict_from_json('accuracy/empty_results.json'),
                    _dict_from_json('accuracy/empty_results.json'),
                ],
                [
                    [('irrelevant', 'sli>slo', 1),
                     {"window_size": 10, "event_time": 1552484541.644,
                      "tags": {"workload_instance": "cassandra_stress--default--14--9142"}}],
                    [('irrelevant', 'sli>slo', 1),
                     {"window_size": 10, "event_time": 1552484741.644,
                      "tags": {"workload_instance": "twemcache_mutilate--big--14--11213"}}],
                    [('irrelevant', 'sli>slo', 1),
                     {"window_size": 10, "event_time": 1552484941.644,
                      "tags": {"workload_instance": "twemcache_mutilate--big--14--11213"}}],
                ], 1, 3, 6),
        # 3 anomalies, 2 matching SLO violation and 6 SLO violations overall
        (
                _dict_from_json('accuracy/anomalies.json'),
                [
                    _dict_from_json('accuracy/slo_violations.json'),
                    _dict_from_json('accuracy/slo_violation.json'),
                    _dict_from_json('accuracy/slo_violation.json'),
                    _dict_from_json('accuracy/empty_results.json'),
                ],
                [
                    [('irrelevant', 'sli>slo', 1),
                     {"window_size": 10, "event_time": 1552484541.644,
                      "tags": {"workload_instance": "cassandra_stress--default--14--9142"}}],
                    [('irrelevant', 'sli>slo', 1),
                     {"window_size": 10, "event_time": 1552484741.644,
                      "tags": {"workload_instance": "twemcache_mutilate--big--14--11213"}}],
                    [('irrelevant', 'sli>slo', 1),
                     {"window_size": 10, "event_time": 1552484941.644,
                      "tags": {"workload_instance": "twemcache_mutilate--big--14--11213"}}],
                ], 2, 3, 6),
        # no anomalies, no matching SLO violation and 6 SLO violations overall
        (
                _dict_from_json('accuracy/empty_results.json'),
                [
                    _dict_from_json('accuracy/slo_violations.json'),
                ],
                [], 0, 0, 6),
    ])
def test_calculate_components(anomalies, fetched_data, build_prometheus_url_calls,
                              expected_true_positives, expected_anomalies_found,
                              expected_real_positives):
    prm.accuracy.fetch_metrics = Mock(side_effect=fetched_data)
    prm.accuracy.build_prometheus_url = Mock()
    true_positives, anomalies_found, real_positives = calculate_components(anomalies, 'irrelevant',
                                                                           1, 10)

    assert true_positives == expected_true_positives
    assert anomalies_found == expected_anomalies_found
    assert real_positives == expected_real_positives

    # Assert that URL used to fetch all SLO violations is build as expected
    prm.accuracy.build_prometheus_url.assert_any_call('irrelevant', 'sli>slo', 1)
    for call in build_prometheus_url_calls:
        # Assert that URL used to fetch SLO violations for an anomaly is build as expected
        prm.accuracy.build_prometheus_url.assert_any_call(*call[0],
                                                          event_time=call[1]['event_time'],
                                                          window_size=call[1]['window_size'],
                                                          tags=call[1]['tags'])

    # Assert that build_prometheus_url() if no anomalies are found
    if len(build_prometheus_url_calls) == 0:
        prm.accuracy.build_prometheus_url.assert_called_once()


@pytest.mark.parametrize(
    'true_positives,anomaly_count,slo_violations,expected_precision,expected_recall', [
        (0, 0, 6, -1, 0),
        (1, 2, 1, 0.5, 1),
        (1, 2, 4, 0.5, 0.25),
        (0, 1, 0, 0, -1),
        (0, 0, 0, -1, -1),
    ])
def test_calculate_precision_and_recall(true_positives, anomaly_count, slo_violations,
                                        expected_precision, expected_recall):
    precision, recall = calculate_precision_and_recall(true_positives, anomaly_count,
                                                       slo_violations)

    assert precision == expected_precision
    assert recall == expected_recall
