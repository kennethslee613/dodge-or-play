import requests
import time
from datetime import datetime, timedelta
import csv
import pymysql
import sys

API_KEY = 'RGAPI-8ca6183f-9a94-4bd8-8be5-ce93d361b1dd'
PLAYER_USERNAME = 'FredericaxSbK'
TEAMMATES = []
API_KEY_PARAM = {'api_key': API_KEY}
RANKED_QUEUE_ID = 420
RANKED_QUEUE_NAME = 'RANKED_SOLO_5x5'

def getChallengerPlayers():
    try:
        getChallengerPlayers = 'https://na1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5'
        challengerPlayersResponse = requests.get(url = getChallengerPlayers, params=API_KEY_PARAM).json()
        time.sleep(1.3)
        challengerPlayers = []
        for player in challengerPlayersResponse['entries']:
            challengerPlayers.append(player['summonerId'])
        return challengerPlayers
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as e:
        print('Something went wrong in getChallengerPlayers:')
        print(challengerPlayersResponse)
        print(e)
        sys.exit(2)

def getAccountId(summonerId):
    try:
        getSummoner = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/{0:s}'.format(summonerId)
        summoner = requests.get(url = getSummoner, params=API_KEY_PARAM).json()
        time.sleep(1.3)
        accountId = summoner['accountId']
        return accountId
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as e:
        print('Something went wrong in getSummonerId():')
        print(summoner)
        print(e)
        sys.exit(2)

def getMatchIdsOfPlayer(accountId):
    try:
        getAllMatches = 'https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/{0:s}'.format(accountId)
        allMatchesResponse = requests.get(url = getAllMatches, params=API_KEY_PARAM).json()
        time.sleep(1.3)
        allMatches = allMatchesResponse['matches']
        rankedMatches = []
        for match in allMatches:
            if match['queue'] == RANKED_QUEUE_ID:
                rankedMatches.append({
                    'gameId': match['gameId'],
                    'timestamp': match['timestamp']
                })
        return rankedMatches

    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as e:
        print('Something went wrong in getSummonerId():')
        print(allMatchesResponse)
        print(e)
        sys.exit(2)

def goThroughMatchesGivenPlayer(connection, challengerPlayers):
    try:
        cursor = connection.cursor()
        for summonerId in challengerPlayers:
            accountId = getAccountId(summonerId)
            rankedMatches = getMatchIdsOfPlayer(accountId)
            # match: {'gameId', 'timestamp'}
            for match in rankedMatches:
                gameId, timestamp = match['gameId'], match['timestamp']
                query = 'SELECT * FROM matches WHERE gameId = "%s";'
                cursor.execute(query, (gameId))
                response = cursor.fetchall()
                # If this game hasn't been added yet
                if response == ():
                    
                    query = 'INSERT INTO matches (gameId) VALUES ("%s");'
                    try:
                        cursor.execute(query, (gameId))
                    except Exception as e:
                        connection.rollback()
                        print('Insert into matches table has failed:')
                        print(e)
                        sys.exit(2)
                    finally:
                        connection.commit()
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as e:
        print('Something went wrong in goThroughMatchesGivenPlayer():')
        print(e)
        sys.exit(2)
    finally:
        cursor.close()

def RESET_DATABASE(connection):
    try:
        cancel = input('Running this function will reset the database. Enter \'y\' to continue. Any other input will cancel the reset: ')
        if cancel != 'y':
            raise Exception('Hard reset has been cancelled')
        cursor = connection.cursor()
        query = 'DELETE FROM matches'
        cursor.execute(query)
    except Exception as e:
        connection.rollback()
        print('Hard reset failed:')
        print(e)
        sys.exit(2)
    finally:
        connection.commit()
        cursor.close()
        print('Hard reset successful.')

if __name__ == '__main__':
    try:
        with open('DB_INFO.txt', 'r') as key:
            DB_INFO = [line.rstrip('\n') for line in key]

        connection = pymysql.connect(host=DB_INFO[0],
            port=int(DB_INFO[1]),
            user=DB_INFO[2],
            password=DB_INFO[3],
            db=DB_INFO[4],
            charset='utf8mb4')

        # RESET_DATABASE(connection)

        challengerPlayers = getChallengerPlayers()
        goThroughMatchesGivenPlayer(connection, challengerPlayers)
    except (KeyboardInterrupt, SystemExit):
        raise
    except Exception as e:
        print('Something went wrong in main:')
        print(e)
    finally:
        connection.close()