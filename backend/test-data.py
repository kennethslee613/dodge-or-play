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
        sys.exit(2)
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
        sys.exit(2)
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
                rankedMatches.append(match['gameId'])
        return rankedMatches

    except (KeyboardInterrupt, SystemExit):
        sys.exit(2)
    except Exception as e:
        print('Something went wrong in getSummonerId():')
        print(allMatchesResponse)
        print(e)
        sys.exit(2)

def organizeMatchData(rankedMatches, summonerId):
    try:
        matchPlayerDetails = []
        matchDetails = []
        # firstBloodAssist, firstBloodKill, firstInhibitorAssist, firstInhibitorKill, firstTowerAssist, firstTowerKill, win into bool
        # statsDetails = ['assists', 'champLevel', 'damageDealtToObjectives', 'damageDealtToTurrets', 'damageSelfMitigated', 'deaths', 'doubleKills', 'firstBloodAssist', 
        #                 'firstBloodKill', 'firstInhibitorAssist', 'firstInhibitorKill', 'firstTowerAssist', 'firstTowerKill', 'goldEarned', 'goldSpent', 'inhibitorKills', 
        #                 'killingSprees', 'kills', 'largestKillingSpree', 'largestMultiKill', 'longestTimeSpentLiving', 'magicDamageDealt', 'magicDamageDealtToChampions', 
        #                 'magicalDamageTaken', 'neutralMinionsKilled', 'neutralMinionsKilledEnemyJungle', 'neutralMinionsKilledTeamJungle', 'pentaKills', 
        #                 'physicalDamageDealt', 'physicalDamageDealtToChampions', 'physicalDamageTaken', 'quadraKills', 'timeCCingOthers', 'totalDamageDealt', 
        #                 'totalDamageDealtToChampions', 'totalDamageTaken', 'totalHeal', 'totalMinionsKilled', 'totalTimeCrowdControlDealt', 'tripleKills', 
        #                 'trueDamageDealt', 'trueDamageDealtToChampions', 'trueDamageTaken', 'turretKills', 'unrealKills', 'visionScore', 'visionWardsBoughtInGame', 
        #                 'wardsPlaced', 'win']
        statsDetails = ['assists', 'damageDealtToTurrets', 'deaths',
            'goldEarned', 'killingSprees', 'kills', 
            'totalDamageDealtToChampions', 'totalMinionsKilled', 
            'totalTimeCrowdControlDealt', 'visionScore',
            'win']
        lane = {'NONE': 0, 'TOP': 1, 'JUNGLE': 2, 'MIDDLE': 3, 'BOTTOM': 4}
        for rankedMatch in rankedMatches:
            for player in rankedMatch['participantIdentities']:
                if player['player']['summonerId'] == summonerId:
                    participantId = player['participantId']
                    break
            for player in rankedMatch['participants']:
                if player['participantId'] == participantId:
                    matchDetails.append(rankedMatch['gameDuration'])
                    matchDetails.append(player['championId'])
                    matchDetails.append(lane[player['timeline']['lane']])
                    for statsDetail in statsDetails:
                        if statsDetail in ['firstBloodAssist', 'firstBloodKill', 'firstInhibitorAssist', 'firstInhibitorKill', 'firstTowerAssist', 'firstTowerKill', 'win']:
                            matchDetails.append(1) if player['stats'].get(statsDetail) == True else matchDetails.append(0)
                        else:
                            matchDetails.append(player['stats'].get(statsDetail))
                    matchPlayerDetails.append(player)
                    break
        while len(matchDetails) < 14:
            matchDetails.append(None)
        return matchDetails
    except (KeyboardInterrupt, SystemExit):
        sys.exit(2)
    except Exception as e:
        print('Something went wrong in organizeMatchData():')
        print(e)
        sys.exit(2)

def getHistoryOfPlayer(accountId, summonerId, datetime):
    try:
        getAllMatches = 'https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/{0:s}'.format(accountId)
        oneWeekAgo = int(round((datetime - timedelta(days=7)).timestamp() * 1000))
        allMatchesResponse = requests.get(url = getAllMatches, params={'api_key': API_KEY, 'beginTime': oneWeekAgo}).json()
        time.sleep(1.3)
        allMatches = allMatchesResponse['matches']
        rankedMatches = []
        for i in range(len(allMatches)):
            match = allMatches[i]
            if match['queue'] == RANKED_QUEUE_ID:
                getMatchDetails = 'https://na1.api.riotgames.com/lol/match/v4/matches/{0:d}'.format(match['gameId'])
                matchDetailsResponse = requests.get(url = getMatchDetails, params=API_KEY_PARAM).json()
                time.sleep(1.3)
                rankedMatches.append({
                'gameDuration': matchDetailsResponse['gameDuration'],
                'participants': matchDetailsResponse['participants'],
                'participantIdentities': matchDetailsResponse['participantIdentities']
                })
            if len(rankedMatches) == 2:
                break
        organizedData = organizeMatchData(rankedMatches, summonerId)
        return organizedData
    except (KeyboardInterrupt, SystemExit):
        sys.exit(2)
    except Exception as e:
        print('Something went wrong in getHistoryOfPlayer():')
        print(e)
        print(allMatchesResponse)

def createGamesData(gameId):
    try:
        getMatchDetails = 'https://na1.api.riotgames.com/lol/match/v4/matches/{0:d}'.format(gameId)
        matchDetailsResponse = requests.get(url = getMatchDetails, params=API_KEY_PARAM).json()
        time.sleep(1.3)
        if matchDetailsResponse['teams'][0]['win'] == 'Win':
            team1Win = 1
            team2Win = 0
        else:
            team1Win = 0
            team2Win = 1
        timestamp = matchDetailsResponse['gameCreation']
        team1 = [{'accountId': player['player']['accountId'], 'summonerId': player['player']['summonerId']} for player in matchDetailsResponse['participantIdentities'][:5]]
        team2 = [{'accountId': player['player']['accountId'], 'summonerId': player['player']['summonerId']} for player in matchDetailsResponse['participantIdentities'][5:]]
        # Do data for team1
        team1History = []
        team2History = []
        try:
            for playerId in team1:
                playerHistory = getHistoryOfPlayer(playerId['accountId'], playerId['summonerId'], datetime.fromtimestamp(timestamp/1000.0))
                team1History = team1History + playerHistory
            for playerId in team2:
                playerHistory = getHistoryOfPlayer(playerId['accountId'], playerId['summonerId'], datetime.fromtimestamp(timestamp/1000.0))
                team2History = team2History + playerHistory
            team1History.append(team1Win)
            team1History.append(str(gameId) + '-1')
            team2History.append(team2Win)
            team2History.append(str(gameId) + '-2')

            return team1History, team2History
        except (KeyboardInterrupt, SystemExit):
            sys.exit(2)
        except Exception as e:
            print('There was an issue getting history of players:')
            print(e)

    except (KeyboardInterrupt, SystemExit):
        sys.exit(2)
    except Exception as e:
        print('Something went wrong in createGamesData():')
        print(matchDetailsResponse)
        print(e)

def storeGamesData(connection, gamesData):
    try:
        cursor = connection.cursor()
        query = 'INSERT INTO testData VALUES ('
        percentS = ['%s' for i in range(142)]
        query += ', '.join(percentS)
        query += ')'
        try:
            cursor.execute(query, gamesData)
        except Exception as e:
            connection.rollback()
            print('Insert into testData table has failed:')
            print(e)
            print(gamesData)
            sys.exit(2)
        finally:
            connection.commit()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(2)
    except Exception as e:
        print('Something went wrong in storeGamesData():')
        print(e)
        sys.exit(2)
    finally:
        cursor.close()

def goThroughMatchesGivenPlayers(connection, challengerPlayers):
    try:
        count = 0
        cursor = connection.cursor()
        for summonerId in challengerPlayers:
            accountId = getAccountId(summonerId)
            rankedMatches = getMatchIdsOfPlayer(accountId)
            for gameId in rankedMatches:
                query = 'SELECT * FROM matches WHERE gameId = "%s";'
                cursor.execute(query, (gameId))
                response = cursor.fetchall()
                # If this game hasn't been added yet
                if response == ():
                    try:
                        gamesData1, gamesData2 = createGamesData(gameId)
                        storeGamesData(connection, gamesData1)
                        storeGamesData(connection, gamesData2)
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
                            count += 2
                            print('Rows added: {0:d}'.format(count), end='\r')
                    except (KeyboardInterrupt, SystemExit):
                        sys.exit(2)
                    except:
                        print('Error with createGamesData')
    except (KeyboardInterrupt, SystemExit):
        sys.exit(2)
    except Exception as e:
        print('Something went wrong in goThroughMatchesGivenPlayers():')
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

['assists', 'damageDealtToTurrets', 'deaths',
            'goldEarned', 'killingSprees', 'kills', 
            'totalDamageDealtToChampions', 'totalMinionsKilled', 
            'totalTimeCrowdControlDealt', 'visionScore',
            'win']
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
        goThroughMatchesGivenPlayers(connection, challengerPlayers)
    except (KeyboardInterrupt, SystemExit):
        sys.exit(2)
    except Exception as e:
        print('Something went wrong in main:')
        print(e)
    finally:
        connection.close()