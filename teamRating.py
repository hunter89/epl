import json
from collections import OrderedDict


def string_score(string1):
    split_score = string1.split(" : ")
    return split_score

file_pointer = open("/Users/shubhampawar/epl_data/epl_data/epl_data/xml_stats/season16-17/season_match_stats.json", "rb")

data = json.load(file_pointer, object_pairs_hook=OrderedDict)

score_file = "scoreFile.csv"
fp = open(score_file, "wb")

fp.write("Date, MatchId, home_team_id, home_team_name, away_team_id, away_team_name, half_time_score,, full_time_score, \n")

for matchId, gameStats in data.iteritems():
    home_team_id = data[matchId]["home_team_id"]
    away_team_id = data[matchId]["away_team_id"]
    half_time_score = string_score(data[matchId]["half_time_score"])
    full_time_score = string_score(data[matchId]["full_time_score"])
    home_team_name = data[matchId]["home_team_name"]
    away_team_name = data[matchId]["away_team_name"]
    date = data[matchId]["date_string"]

    fp.write(date + "," + matchId + "," + home_team_id + "," + home_team_name + "," + away_team_id + "," + away_team_name + "," + \
    half_time_score[0] + "," + half_time_score[1] + "," + full_time_score[0] + "," + full_time_score[1] + "\n")


fp.close()




