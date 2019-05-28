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
from unittest.mock import Mock, patch
from os.path import dirname, join
from requests import Response

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
    tags = dict(build_number=build_number, **tags)
    assert expected_url == build_prometheus_url(prometheus, name, tags,
                                                window_size, event_time)


def _dict_from_json(path):
    with open(join(dirname(__file__), path)) as f:
        return loads(f.read())


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


@pytest.mark.parametrize(
    'anomalies,requests,expected_true_positives,expected_anomalies_found,'
    'expected_real_positives',
    [
        # 3 anomalies, no matching SLO violations and 6 SLO violations overall
        (
            _dict_from_json('accuracy/anomalies.json'),
            {
                'irrelevant/api/v1/query_range?query=sli>slo{build_number="1"}'
                '&start=1558960265.3748605&end=1558963865.3748605&step=1s':
                    _dict_from_json('accuracy/slo_violations.json'),
                'irrelevant/api/v1/query_range?query=sli>slo{build_number="1",workload_instance='
                '"cassandra_stress--default--14--9142"}&start=1552484536.644&end=1552484546.644&'
                'step=1s': _dict_from_json('accuracy/empty_results.json'),
                'irrelevant/api/v1/query_range?query=sli>slo{build_number="1",workload_instance='
                '"twemcache_mutilate--big--14--11213"}&start=1552484736.644&end=1552484746.644&'
                'step=1s': _dict_from_json('accuracy/empty_results.json'),
                'irrelevant/api/v1/query_range?query=sli>slo{build_number="1",workload_instance='
                '"twemcache_mutilate--big--14--11213"}&start=1552484936.644&end=1552484946.644&'
                'step=1s': _dict_from_json('accuracy/empty_results.json'),
            }, 0, 3, 6),
        # 3 anomalies, 1 matching SLO violation and 6 SLO violations overall
        (
            _dict_from_json('accuracy/anomalies.json'),
            {
                'irrelevant/api/v1/query_range?query=sli>slo{build_number="1"}'
                '&start=1558960265.3748605&end=1558963865.3748605&step=1s':
                    _dict_from_json('accuracy/slo_violations.json'),
                'irrelevant/api/v1/query_range?query=sli>slo{build_number="1",workload_instance='
                '"cassandra_stress--default--14--9142"}&start=1552484536.644&end=1552484546.644&'
                'step=1s': _dict_from_json('accuracy/slo_violation.json'),
                'irrelevant/api/v1/query_range?query=sli>slo{build_number="1",workload_instance='
                '"twemcache_mutilate--big--14--11213"}&start=1552484736.644&end=1552484746.644&'
                'step=1s': _dict_from_json('accuracy/empty_results.json'),
                'irrelevant/api/v1/query_range?query=sli>slo{build_number="1",workload_instance='
                '"twemcache_mutilate--big--14--11213"}&start=1552484936.644&end=1552484946.644&'
                'step=1s': _dict_from_json('accuracy/empty_results.json'),
            }, 1, 3, 6),
        # 3 anomalies, 2 matching SLO violation and 6 SLO violations overall
        (
            _dict_from_json('accuracy/anomalies.json'),
            {
                'irrelevant/api/v1/query_range?query=sli>slo{build_number="1"}'
                '&start=1558960265.3748605&end=1558963865.3748605&step=1s':
                    _dict_from_json('accuracy/slo_violations.json'),
                'irrelevant/api/v1/query_range?query=sli>slo{build_number="1",workload_instance='
                '"cassandra_stress--default--14--9142"}&start=1552484536.644&end=1552484546.644&'
                'step=1s': _dict_from_json('accuracy/slo_violation.json'),
                'irrelevant/api/v1/query_range?query=sli>slo{build_number="1",workload_instance='
                '"twemcache_mutilate--big--14--11213"}&start=1552484736.644&end=1552484746.644&'
                'step=1s': _dict_from_json('accuracy/slo_violation.json'),
                'irrelevant/api/v1/query_range?query=sli>slo{build_number="1",workload_instance='
                '"twemcache_mutilate--big--14--11213"}&start=1552484936.644&end=1552484946.644&'
                'step=1s': _dict_from_json('accuracy/empty_results.json'),
            }, 2, 3, 6),
        # no anomalies, no matching SLO violation and 6 SLO violations overall
        (
                _dict_from_json('accuracy/empty_results.json'),
                {
                    'irrelevant/api/v1/query_range?query=sli>slo{build_number="1"}'
                    '&start=1558960265.3748605&end=1558963865.3748605&step=1s':
                        _dict_from_json('accuracy/slo_violations.json')
                }, 0, 0, 6),
    ])
@patch('prm.accuracy.time', return_value=1558962065.3748605)
def test_calculate_components(time, anomalies, requests, expected_true_positives,
                              expected_anomalies_found, expected_real_positives):
    print(requests)
    with patch('prm.accuracy.get',
               Mock(side_effect=lambda url: Mock(Response, json=Mock(return_value=requests[url])))):
        true_positives, anomalies_found, real_positives = calculate_components(
            anomalies, 'irrelevant', dict(build_number=1), 10)

    assert true_positives == expected_true_positives
    assert anomalies_found == expected_anomalies_found
    assert real_positives == expected_real_positives
