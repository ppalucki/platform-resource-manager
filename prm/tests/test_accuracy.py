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

import pytest
from prm.accuracy import build_prometheus_url


@pytest.mark.parametrize('prometheus,name,build_number,expected_url', [
    ('http://10.0.0.1', 'metric_name', 1,
     'http://10.0.0.1/api/v1/query?query=metric_name{build_number="1"}')
])
def test_build_prometheus_url(prometheus, name, build_number, expected_url):
    assert expected_url == build_prometheus_url(prometheus, name, build_number)
