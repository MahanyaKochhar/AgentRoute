"""Run paired real HTTP requests and summarize their correlated API metrics."""
import argparse
import json
import math
from pathlib import Path
from statistics import mean, median
from time import perf_counter
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def read_metrics(path):
    records = []
    if path.exists():
        for line in path.read_text().splitlines():
            if ' metrics ' in line:
                records.append(json.loads(line.split(' metrics ', 1)[1]))
    return records


def summarize(runs):
    summaries = {}
    for approach in ('all_tools', 'decisions'):
        group = [run for run in runs if run['approach'] == approach]
        completed = [run for run in group if run['status'] == 'completed' and run['metrics']
                     and run['metrics']['status'] == 'completed']
        summary = {'requests': len(group), 'completed': len(completed),
                   'failed_or_unmeasured': len(group) - len(completed)}
        for field in ('latency_ms', 'first_text_ms', 'model_calls', 'decision_calls',
                      'model_input_tokens', 'model_output_tokens', 'decision_input_tokens',
                      'decision_output_tokens', 'total_input_tokens', 'total_output_tokens'):
            values = [run['metrics'][field] for run in completed
                      if run['metrics'].get(field) is not None]
            summary[field] = {
                'measured_requests': len(values),
                'mean': round(mean(values), 2) if values else None,
                'median': round(median(values), 2) if values else None,
                'p95': sorted(values)[math.ceil(0.95 * len(values)) - 1] if values else None,
            }
        labeled = [run for run in completed if run['expected_tools']]
        summary['exact_tool_match_rate'] = (
            sum(run['exact_tool_match'] for run in labeled) / len(labeled) if labeled else None)
        summaries[approach] = summary
    return summaries


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:8000')
    parser.add_argument('--message', default='Find diabetes trials and publications.')
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--expected-tool', action='append', default=[])
    parser.add_argument('--log-file', type=Path, default=PROJECT_ROOT / 'logs/app.log')
    parser.add_argument('--output', type=Path, default=PROJECT_ROOT / 'logs/comparison.json')
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error('--repeats must be at least 1')

    runs = []
    for repeat in range(args.repeats):
        # Alternate order to reduce warm-up/cache/order bias.
        paths = ['/chat', '/v1/chat'] if repeat % 2 == 0 else ['/v1/chat', '/chat']
        for path in paths:
            started = perf_counter()
            run = {'repeat': repeat + 1, 'path': path,
                   'approach': 'all_tools' if path == '/chat' else 'decisions',
                   'message': args.message, 'expected_tools': args.expected_tool,
                   'status': 'failed', 'metrics': None, 'api_calls': [], 'response_text': ''}
            request = Request(args.base_url.rstrip('/') + path,
                              data=json.dumps({'message': args.message}).encode(),
                              headers={'Content-Type': 'application/json'}, method='POST')
            try:
                with urlopen(request, timeout=300) as response:
                    run['http_status'] = response.status
                    run['request_id'] = response.headers.get('X-Request-ID')
                    sse = response.read().decode().replace('\r\n', '\n')
                for frame in sse.split('\n\n'):
                    if not frame.startswith('event: '):
                        continue
                    event = frame.splitlines()[0].removeprefix('event: ')
                    payload = json.loads(next(line[6:] for line in frame.splitlines()
                                              if line.startswith('data: ')))
                    if event == 'response.output_text.done':
                        run['response_text'] = payload['text']
                    elif event == 'response.completed':
                        run['status'] = 'completed'
                    elif event == 'response.failed':
                        run['error'] = payload['message']
            except (HTTPError, URLError, TimeoutError) as error:
                run['error'] = str(error)
            run['client_latency_ms'] = round((perf_counter() - started) * 1000, 2)
            records = [record for record in read_metrics(args.log_file)
                       if record['request_id'] == run.get('request_id')]
            run['api_calls'] = [record for record in records if record['event'] == 'api.call']
            run['metrics'] = next((record for record in records
                                   if record['event'] == 'request.completed'), None)
            if run['metrics']:
                called = {call['name'] for call in run['metrics']['tool_calls']}
                run['exact_tool_match'] = called == set(args.expected_tool) if args.expected_tool else None
            else:
                run['exact_tool_match'] = None
            runs.append(run)
            print(f"Repeat {repeat + 1} {path}: {run['status']}")

    report = {'message': args.message, 'summary': summarize(runs), 'runs': runs}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print('\nMeans over completed requests (unknown usage is excluded, never treated as zero):')
    print('| Metric | All tools (/chat) | Decisions (/v1/chat) |')
    print('|---|---:|---:|')
    for field in ('latency_ms', 'first_text_ms', 'model_calls', 'decision_calls',
                  'model_input_tokens', 'model_output_tokens', 'decision_input_tokens',
                  'decision_output_tokens', 'total_input_tokens', 'total_output_tokens'):
        values = [report['summary'][approach][field]['mean'] for approach in ('all_tools', 'decisions')]
        print(f"| {field} | {values[0] if values[0] is not None else 'unknown'} | "
              f"{values[1] if values[1] is not None else 'unknown'} |")
    for approach, summary in report['summary'].items():
        print(f"{approach}: {summary['completed']}/{summary['requests']} completed; "
              f"exact tool match rate={summary['exact_tool_match_rate']}")
    print(f'Full report, per-call metrics, and responses: {args.output}')


if __name__ == '__main__':
    main()
