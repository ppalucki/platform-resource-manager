from prm.accuracy import fetch_metrics


for attempt in range(0, 100):
    anomalies = fetch_metrics('http://100.64.176.12:9090/api/v1/query?query=anomaly{build_number="12",build_scenario="llc",build_commit="e94bd53edb51de03f9fb6372b6bb84eb9a9c385f"}')
    print('Looking for anomalies... Attempt {}'.format(attempt + 1))
    if anomalies['data']['result']:
        print('Found anomaly')
        break
else:
    print('No anomalies')
