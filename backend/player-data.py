import requests
import time
from datetime import datetime, timedelta
import csv
from itertools import chain

API_KEY = 'RGAPI-66a35f77-83ec-4371-9b1a-5895d60f01b8'
PLAYER_USERNAME = 'FredericaxSbK'
TEAMMATES = []
API_KEY_PARAM = {'api_key': API_KEY}
RANKED_QUEUE_ID = 420
RANKED_QUEUE_NAME = 'RANKED_SOLO_5x5'

# Get summoner's id
def getSummonerId(username):
  try:
    getSummoner = 'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{0:s}'.format(username)
    summoner = requests.get(url = getSummoner, params=API_KEY_PARAM).json()
    time.sleep(1.3)
    encryptedSummonerId = summoner['id']
    encryptedAccountId = summoner['accountId']
    return encryptedSummonerId, encryptedAccountId
  except:
    print('Something went wrong in getSummonerId():')
    print(summoner)

def getSummonerWinRate(encryptedSummonerId):
  try:
    # Get summoner's wins, losses, and winrate
    getSummonerDetails = 'https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{0:s}'.format(encryptedSummonerId)
    summonerQueueTypeDetails = requests.get(url = getSummonerDetails, params=API_KEY_PARAM).json()
    time.sleep(1.3)
    for queueTypeDetails in summonerQueueTypeDetails:
      if queueTypeDetails['queueType'] == RANKED_QUEUE_NAME:
        summonerDetails = queueTypeDetails
    summonerWins = summonerDetails['wins']
    summonerLosses = summonerDetails['losses']
    summonerWinRate = summonerWins / (summonerWins + summonerLosses)
    return summonerWinRate
  except:
    print('Something went wrong in getSummonerWinRate():')
    print(summonerQueueTypeDetails)

def getSummonerMatchData(encryptedAccountId, numOfMatches, datetime=datetime.now()):
  try:
    # Get summoner's matches data
    getAllMatches = 'https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/{0:s}'.format(encryptedAccountId)
    oneWeekAgo = int(round((datetime - timedelta(days=7)).timestamp() * 1000))
    allMatchesResponse = requests.get(url = getAllMatches, params={'api_key': API_KEY, 'beginTime': oneWeekAgo}).json()
    time.sleep(1.3)
    allMatches = allMatchesResponse['matches']
    rankedMatches = []
    # example = allMatches[0]
    for i in range(len(allMatches)):
      match = allMatches[i]
      getMatchDetails = 'https://na1.api.riotgames.com/lol/match/v4/matches/{0:d}'.format(match['gameId'])
      matchDetailsResponse = requests.get(url = getMatchDetails, params=API_KEY_PARAM).json()
      time.sleep(1.3)
      if matchDetailsResponse['queueId'] == RANKED_QUEUE_ID:
        rankedMatches.append({
          'gameDuration': matchDetailsResponse['gameDuration'],
          'participants': matchDetailsResponse['participants'],
          'participantIdentities': matchDetailsResponse['participantIdentities']
        })
      if len(rankedMatches) == numOfMatches:
        break
    print(rankedMatches)
    return rankedMatches
  except:
    print('Something went wrong in getSummonerMatchData:')
    print('Input: {0}'.format(encryptedAccountId))
    print(allMatchesResponse)

def organizeMatchData(rankedMatches, encryptedSummonerId):
  # Organize match data
  matchPlayerDetails = []
  matchDetails = []
  # firstBloodAssist, firstBloodKill, firstInhibitorAssist, firstInhibitorKill, firstTowerAssist, firstTowerKill, win into bool
  statsDetails = ['assists', 'champLevel', 'damageDealtToObjectives', 'damageDealtToTurrets', 'damageSelfMitigated', 'deaths', 'doubleKills', 'firstBloodAssist', 
                  'firstBloodKill', 'firstInhibitorAssist', 'firstInhibitorKill', 'firstTowerAssist', 'firstTowerKill', 'goldEarned', 'goldSpent', 'inhibitorKills', 
                  'killingSprees', 'kills', 'largestKillingSpree', 'largestMultiKill', 'longestTimeSpentLiving', 'magicDamageDealt', 'magicDamageDealtToChampions', 
                  'magicalDamageTaken', 'neutralMinionsKilled', 'neutralMinionsKilledEnemyJungle', 'neutralMinionsKilledTeamJungle', 'pentaKills', 
                  'physicalDamageDealt', 'physicalDamageDealtToChampions', 'physicalDamageTaken', 'quadraKills', 'timeCCingOthers', 'totalDamageDealt', 
                  'totalDamageDealtToChampions', 'totalDamageTaken', 'totalHeal', 'totalMinionsKilled', 'totalTimeCrowdControlDealt', 'tripleKills', 
                  'trueDamageDealt', 'trueDamageDealtToChampions', 'trueDamageTaken', 'turretKills', 'unrealKills', 'visionScore', 'visionWardsBoughtInGame', 
                  'wardsPlaced', 'win']
  lane = {'NONE': None, 'TOP': 1, 'JUNGLE': 2, 'MIDDLE': 3, 'BOTTOM': 4}
  for rankedMatch in rankedMatches:
    for player in rankedMatch['participantIdentities']:
      if player['player']['summonerId'] == encryptedSummonerId:
        participantId = player['participantId']
        break
    for player in rankedMatch['participants']:
      if player['participantId'] == participantId:
        matchDetails.append(rankedMatch['gameDuration'])
        matchDetails.append(player['championId'])
        matchDetails.append(lane[player['timeline']['lane']])
        for statsDetail in statsDetails:
          matchDetails.append(player['stats'].get(statsDetail))
        matchPlayerDetails.append(player)
        break
  return matchDetails

def getMatchDetailsFromUsername(username):
  encryptedSummonerId, encryptedAccountId = getSummonerId(username)
  summonerWinRate = getSummonerWinRate(encryptedSummonerId)
  print(summonerWinRate)
  summonerRankedMatches = getSummonerMatchData(encryptedAccountId, 3)
  summonerMatchDetails = organizeMatchData(summonerRankedMatches, encryptedSummonerId)
  summonerMatchDetails.append(summonerWinRate)
  return summonerMatchDetails

### TRAINING METHODS

def getSummonerMatchIds(encryptedAccountId, numOfMatches):
  try:
    # Get summoner's matches data
    getAllMatches = 'https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/{0:s}'.format(encryptedAccountId)
    allMatchesResponse = requests.get(url = getAllMatches, params=API_KEY_PARAM).json()
    time.sleep(1.3)
    allMatches = allMatchesResponse['matches']
    rankedMatches = []
    # example = allMatches[0]
    for match in allMatches:
      if match['queue'] == RANKED_QUEUE_ID:
        rankedMatches.append((match['gameId'], match['timestamp']))
      if len(rankedMatches) == numOfMatches:
        break
    return rankedMatches
  except:
    print('Something went wrong in getSummonerMatchIds:')
    print(allMatchesResponse)

def getPlayersInMatch(matchId, encryptedAccountId):
  getMatchDetails = 'https://na1.api.riotgames.com/lol/match/v4/matches/{0:d}'.format(matchId)
  matchDetailsResponse = requests.get(url = getMatchDetails, params=API_KEY_PARAM).json()
  time.sleep(1.3)
  team1 = []
  team2 = []
  team = 0
  win = False
  for i in range(10):
    player = matchDetailsResponse['participants'][i]
    currentEncryptedAccountId, currentEncryptedSummonerId = matchDetailsResponse['participantIdentities'][player['participantId'] - 1]['player']['accountId'], matchDetailsResponse['participantIdentities'][player['participantId'] - 1]['player']['summonerId']
    if player['teamId'] == 100:
      team1.append((currentEncryptedAccountId, currentEncryptedSummonerId))
    elif player['teamId'] == 200:
      team2.append((currentEncryptedAccountId, currentEncryptedSummonerId))
    if currentEncryptedAccountId == encryptedAccountId:
      win = player['stats']['win']
      team = player['teamId']
  if team == 100:
    return team1, win
  elif team == 200:
    return team2, win

def getChallengerPlayers():
  try:
    getChallengerPlayers = 'https://na1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5'
    challengerPlayersResponse = requests.get(url = getChallengerPlayers, params=API_KEY_PARAM).json()
    time.sleep(1.3)
    challengerPlayers = []
    for player in challengerPlayersResponse['entries']:
      challengerPlayers.append(player['summonerName'])
    return challengerPlayers
  except:
    print('Something went wrong in getChallengerPlayers:')
    print(challengerPlayersResponse)

def getTrainingData():
  f= open("lol.txt","w+")
  with open('test-data.csv', mode='w') as testData:
    dataWriter = csv.writer(testData, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    challengerPlayersUsernames = getChallengerPlayers()
    for username in challengerPlayersUsernames:
      encryptedSummonerId, encryptedAccountId = getSummonerId(username)
      print(encryptedAccountId, username)
      rankedMatches = getSummonerMatchIds(encryptedAccountId, 1)
      for matchId, timestamp in rankedMatches:
        data = []
        teamEncryptedAccountIds, win = getPlayersInMatch(matchId, encryptedAccountId)
        for teamMemberEncryptedAccountId, teamMemberEncryptedSummonerId in teamEncryptedAccountIds:
          summonerMatchData = getSummonerMatchData(teamMemberEncryptedAccountId, 3, datetime.fromtimestamp(timestamp/1000.0))
          organizedData = organizeMatchData(summonerMatchData, teamMemberEncryptedSummonerId)
          data.append(organizedData)
        f.write(str(data))
        flatData = list(chain.from_iterable(data))
        dataWriter.writerow(flatData)
  f.close()
  

        

getTrainingData()