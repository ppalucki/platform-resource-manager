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


import os

from argparse import ArgumentParser

from prm.accuracy import (build_prometheus_url, fetch_metrics,
                          calculate_components, calculate_precision_and_recall)


def main():
    parser = ArgumentParser()
    parser.add_argument('build_number', type=int, help="Jenkins build number",
                        metavar='BUILD_NUMBER')
    parser.add_argument('--prometheus', type=str, default="http://127.0.0.1:9090",
                        help="Prometheus server base URL, eg: http://127.0.0.1:9090")
    parser.add_argument('--window-size', type=float, default=10.0,
                        help="Size of time window used to find SLO violations for each anomaly")
    args = parser.parse_args()

    url = build_prometheus_url(args.prometheus, 'anomaly', args.build_number)
    anomalies = fetch_metrics(url)
    true_positives, anomaly_count, slo_violations = calculate_components(
        anomalies, args.prometheus, args.build_number, args.window_size)
    precision, recall = calculate_precision_and_recall(
        true_positives, anomaly_count, slo_violations)
    print(precision, recall)


def test_integration_accurracy():
    prometheus = os.environ['PROMETHEUS']
    build_number = int(os.environ['BUILD_NUMBER'])
    window_size = 10.0
    url = build_prometheus_url(prometheus, 'anomaly', build_number)
    anomalies = fetch_metrics(url)
    true_positives, anomaly_count, slo_violations = calculate_components(
        anomalies, prometheus, build_number, window_size)
    precision, recall = calculate_precision_and_recall(
        true_positives, anomaly_count, slo_violations)

    assert precision > 0
    assert recall > 0


if __name__ == "__main__":
    main()
