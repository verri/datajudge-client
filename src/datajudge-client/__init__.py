import os
import sys
import requests
import argparse
import base64


URL = 'https://datajudge.space/app/api'


def log_and_exit(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    sys.exit(1)


def check_key(apikey):
    if len(apikey) != 32:
        log_and_exit('invalid API key: "{}"'.format(apikey))


def encode_file(filename):
    data = open(filename).read()
    return base64.b64encode(data.encode('utf-8')).decode('ascii')


def leaderboard(args):
    check_key(args.key)

    headers = {'Accept': 'application/json', 'X-Auth': args.key}
    response = requests.get(URL + '/leaderboard', headers=headers)

    if response.status_code != 200:
        log_and_exit('Something went wrong...:\n{}'.format(response.text))

    rank = response.json()
    for submission in rank:
        print(
            args.format.format(
                team=submission["name"],
                score=float(submission["score"]),
                score_type=submission["score_type"],
                timestamp=submission["timestamp"]))


def submit(args):
    check_key(args.key)

    if not os.path.isfile(args.input):
        log_and_exit('{} is not a file'.format(args.input))

    headers = {'Accept': 'application/json', 'X-Auth': args.key}
    data = encode_file(args.input)
    response = requests.post(
        URL + '/submit',
        headers=headers,
        json={
            'data': data})

    if response.status_code != 201:
        log_and_exit('Something went wrong...:\n{}'.format(response.text))

    print(response.json())


def teamname(args):
    check_key(args.key)

    headers = {'Accept': 'application/json', 'X-Auth': args.key}
    response = requests.get(URL + '/teamname', headers=headers)

    if response.status_code != 200:
        log_and_exit('Something went wrong...:\n{}'.format(response.text))

    print(response.text.strip())


def main():
    parser = argparse.ArgumentParser(
        description='Python client cli for Data Judge API')
    parser.add_argument('--key', default=os.getenv('DATA_JUDGE_API_KEY', ''),
                        required=False)
    subparsers = parser.add_subparsers(required=True, metavar='SUBCOMMAND')

    leaderboard_parser = subparsers.add_parser('leaderboard')
    leaderboard_parser.add_argument(
        '--format',
        type=str,
        default='{team:30s}\t{score:10.3f} ({score_type})\t{timestamp}')
    leaderboard_parser.set_defaults(callback=leaderboard)

    submit_parser = subparsers.add_parser('submit')
    submit_parser.add_argument('--input', type=str, required=True)
    submit_parser.set_defaults(callback=submit)

    teamname_parser = subparsers.add_parser('teamname')
    teamname_parser.set_defaults(callback=teamname)

    args = parser.parse_args()
    args.callback(args)
