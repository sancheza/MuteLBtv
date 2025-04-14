import argparse
import requests
from datetime import datetime, timedelta
from time import sleep
from chromecast import get_chromecast
from logger import log
from game import get_feed, is_game_paused, convert_datetime_to_timecode, get_timestamp_from_feed
from schedule import get_game_pk

# Team IDs: https://statsapi.mlb.com/api/v1/teams?sportId=1&season=2025
DEFAULT_TEAM_ID = 121  # Mets
DEFAULT_CHROMECAST_NAME = 'Chromecast Den'
API_POLL_INTERVAL = 5  # seconds


def get_team_id(team_name):
    ''' Get the team ID for a given team name. '''
    url = "https://statsapi.mlb.com/api/v1/teams?sportId=1&season=2025"
    response = requests.get(url)
    teams = response.json()['teams']
    
    for team in teams:
        if team_name.lower() in team['name'].lower() or team_name.lower() in team['teamName'].lower():
            return team['id']
            
    log.error(f"Team '{team_name}' not found. Using default team ID {DEFAULT_TEAM_ID}.")
    return DEFAULT_TEAM_ID


def run(game_pk, chromecast, timecode, verbose=False):
    ''' Get the game feed, determine if the game is mid-inning and update the mute state. '''
    feed = get_feed(game_pk, timecode=timecode)
    log.debug(feed['metaData'])

    timestamp = get_timestamp_from_feed(feed)

    log.info(f'Feed timestamp: {timestamp}')

    if is_game_paused(feed):
        chromecast.set_volume_muted(True)
        if verbose: log.info('Is mid-inning, muting Chromecast\n')
    else:
        chromecast.set_volume_muted(False)
        if verbose: log.info('Is not mid-inning, unmuting Chromecast\n')


def main(game_pk, offset, chromecast_name=DEFAULT_CHROMECAST_NAME, team=None):
    ''' Get the game_pk (if not provided) and execute the `run` function in a loop. '''
    chromecast = get_chromecast(chromecast_name)

    if not game_pk:
        log.info('No game_pk provided. Looking up game information.')
        team_id = get_team_id(team) if team else DEFAULT_TEAM_ID
        game_pk = get_game_pk(date=datetime.now(), team_id=team_id)

    log.info(f'game_pk: {game_pk}')

    while True:
        if offset:
            timestamp = datetime.utcnow() - timedelta(seconds=offset)
            timecode = convert_datetime_to_timecode(timestamp)
        else:
            timecode = None

        run(game_pk, chromecast, timecode, verbose=True)
        sleep(API_POLL_INTERVAL)


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--game_pk', help='The MLB game_pk.')
    parser.add_argument('--offset', type=int, help='The amount of time (in seconds) to delay the feed by, since TV streams are usually delayed.')
    parser.add_argument('--chromecast_name', default=None, help='The name of the Chromecast to use.')
    parser.add_argument('--team', help='The team name to look up game information for.')
    return parser.parse_args()


if __name__ == '__main__':
    ARGS = get_args()
    main(ARGS.game_pk, ARGS.offset, ARGS.chromecast_name, ARGS.team)