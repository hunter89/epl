import json
import numpy as np
from regression import *
from shotEffectiveness import estimateProbabilities
from Index import *
from collections import OrderedDict
import operator
from teamRating import string_score
import csv

file_pointer = open("/Users/shubhampawar/epl_data/epl_data/epl_data/xml_stats/season16-17/season_stats.json", "rb")

data = json.load(file_pointer, object_pairs_hook=OrderedDict)
total_shots = []
won_contest = []
yellow_card_opp = []
red_card_opp = []
accurate_pass = []
total_tackle_opp= []
touches = []
aerial_won = []

shots = 0
goals = 0
onTarget = 0
saves = 0
blocks = 0


aggregate_stats_dict = dict()
player_stats_dict = dict()
for matchId, value1 in data.iteritems():
    for teamId, value2 in data[matchId].iteritems():
        for key in data[matchId].keys():
            if key != teamId:
                opponent_teamId = key 
        for key in data[matchId][teamId]["aggregate_stats"].keys():
            if key in aggregate_stats_dict.keys():
                aggregate_stats_dict[key] +=1
            else:
                aggregate_stats_dict.update({key: 1})
        total_shots.append(int(data[matchId][teamId]["aggregate_stats"]["total_scoring_att"]))
        
        if "total_scoring_att" in data[matchId][teamId]["aggregate_stats"].keys():
            shots += float(data[matchId][teamId]["aggregate_stats"]["total_scoring_att"])
        if "goals" in data[matchId][teamId]["aggregate_stats"].keys():
            goals += float(data[matchId][teamId]["aggregate_stats"]["goals"])
        if ("ontarget_scoring_att" in data[matchId][teamId]["aggregate_stats"].keys()) and ("blocked_scoring_att" in data[matchId][teamId]["aggregate_stats"].keys()):
            onTarget += float(data[matchId][teamId]["aggregate_stats"]["ontarget_scoring_att"]) + float(data[matchId][teamId]["aggregate_stats"]["blocked_scoring_att"])
        if ("ontarget_scoring_att" in data[matchId][teamId]["aggregate_stats"].keys()) and not("blocked_scoring_att" in data[matchId][teamId]["aggregate_stats"].keys()):
            onTarget += float(data[matchId][teamId]["aggregate_stats"]["ontarget_scoring_att"])
        if not("ontarget_scoring_att" in data[matchId][teamId]["aggregate_stats"].keys()) and ("blocked_scoring_att" in data[matchId][teamId]["aggregate_stats"].keys()):
            onTarget += float(data[matchId][teamId]["aggregate_stats"]["blocked_scoring_att"])
        if ("ontarget_scoring_att" in data[matchId][teamId]["aggregate_stats"].keys()) and ("goals" in data[matchId][teamId]["aggregate_stats"].keys()):
            saves += float(data[matchId][teamId]["aggregate_stats"]["ontarget_scoring_att"]) - float(data[matchId][teamId]["aggregate_stats"]["goals"])
        if ("ontarget_scoring_att" in data[matchId][teamId]["aggregate_stats"].keys()) and not("goals" in data[matchId][teamId]["aggregate_stats"].keys()):
            saves += float(data[matchId][teamId]["aggregate_stats"]["ontarget_scoring_att"])
        if "blocked_scoring_att" in data[matchId][teamId]["aggregate_stats"].keys():
            blocks += float(data[matchId][teamId]["aggregate_stats"]["blocked_scoring_att"])

        won_contest_sum = 0
        yellow_card_opp_sum = 0
        red_card_opp_sum = 0
        accurate_pass_sum = 0
        total_tackle_opp_sum = 0
        touches_sum = 0
        aerial_won_sum = 0

        for player_name, value3 in data[matchId][teamId]["Player_stats"].iteritems():
            for key in data[matchId][teamId]["Player_stats"][player_name]["Match_stats"].keys():
                # if key in player_stats_dict.keys():
                #    player_stats_dict[key] +=1
                # else:
                #    player_stats_dict.update({key: 1})    
                if key == "won_contest":
                        won_contest_sum += float(data[matchId][teamId]["Player_stats"][player_name]["Match_stats"]["won_contest"])
                if key == "accurate_pass":
                    accurate_pass_sum += float(data[matchId][teamId]["Player_stats"][player_name]["Match_stats"]["accurate_pass"])
                if key == "touches":
                    touches_sum += float(data[matchId][teamId]["Player_stats"][player_name]["Match_stats"]["touches"])
                if key == "aerial_won": 
                    aerial_won_sum += float(data[matchId][teamId]["Player_stats"][player_name]["Match_stats"]["aerial_won"])   
            
        won_contest.append(won_contest_sum)
        accurate_pass.append(accurate_pass_sum)
        touches.append(touches_sum)
        aerial_won.append(aerial_won_sum)

        for player_name, value3 in data[matchId][opponent_teamId]["Player_stats"].iteritems():
            for key in data[matchId][opponent_teamId]["Player_stats"][player_name]["Match_stats"].keys():
                if key == "total_tackle":
                    total_tackle_opp_sum += float(data[matchId][opponent_teamId]["Player_stats"][player_name]["Match_stats"]["total_tackle"])
                if key == "yellow_card":
                    yellow_card_opp_sum += float(data[matchId][opponent_teamId]["Player_stats"][player_name]["Match_stats"]["yellow_card"])
                if key == "red_card":
                    red_card_opp_sum += float(data[matchId][opponent_teamId]["Player_stats"][player_name]["Match_stats"]["red_card"])
                if key == "second_yellow":
                    red_card_opp_sum += float(data[matchId][opponent_teamId]["Player_stats"][player_name]["Match_stats"]["second_yellow"])
            
        total_tackle_opp.append(total_tackle_opp_sum)   
        yellow_card_opp.append(yellow_card_opp_sum)
        red_card_opp.append(red_card_opp_sum)

shots_data = np.transpose(np.array([total_shots, won_contest, accurate_pass, total_tackle_opp, aerial_won, yellow_card_opp, red_card_opp]))
#print shots_data.shape
coefficients = shotRegression(shots_data)
#print total_shots[0], won_contest[0], accurate_pass[0], total_tackle[0], touches[0], aerial_won[0], yellow_card_opp[0], red_card_opp[0]
probabilities = estimateProbabilities(shots, goals, onTarget, saves, blocks)

playerMeanContributions = dict()
teamRoster = dict()
playerMatchSummary = dict()
teamMeanContribution = dict()

for matchId, value in data.iteritems():
    estimates = matchEstimates(data[matchId], coefficients, probabilities) 
    playerData = playerPoints(data[matchId], estimates, coefficients, probabilities)
    summary_update(playerMatchSummary, playerData)
    roster_update(teamRoster, playerData)
    aggregate_to_mean_contribution(playerMeanContributions, playerMatchSummary)

match_contributions(teamMeanContribution, playerMeanContributions, teamRoster)

odds_dict = dict()
fp = open('E0.csv', 'rb')
reader = csv.DictReader(fp)
for row in reader:
    if row['HomeTeam'] in odds_dict.keys():
        odds_dict[row['HomeTeam']][row['AwayTeam']] = np.array([float(row['B365H']), float(row['B365D']), float(row['B365A'])])
    else:
        odds_dict[row['HomeTeam']] = {row['AwayTeam']: np.array([float(row['B365H']), float(row['B365D']), float(row['B365A'])])}

fp.close()

matches_pointer = open("/Users/shubhampawar/epl_data/epl_data/epl_data/xml_stats/season16-17/season_match_stats.json", "rb")

matches_data = json.load(matches_pointer, object_pairs_hook=OrderedDict)

win_probabilities_file = "winProbabilitiesFile.csv"
fp = open(win_probabilities_file, "wb")

fp.write("Date, MatchId, home_team_id, home_team_name, away_team_id, away_team_name, half_time_score,, full_time_score,, home_prob, draw_prob, away_prob, home_odds, draw_odds, away_odds, odds_home_prob, odds_draw_prob, odds_away_prob, model_pred, odds_pred, model_correct?, odds_correct?, payout\n")

for matchId, gameStats in matches_data.iteritems():
    home_team_id = matches_data[matchId]["home_team_id"]
    away_team_id = matches_data[matchId]["away_team_id"]
    half_time_score = string_score(matches_data[matchId]["half_time_score"])
    full_time_score = string_score(matches_data[matchId]["full_time_score"])
    home_team_name = matches_data[matchId]["home_team_name"]
    away_team_name = matches_data[matchId]["away_team_name"]
    date = matches_data[matchId]["date_string"]
    if home_team_id == "32":
        home_team_name = "Man United"
    if home_team_id == "167":
        home_team_name = "Man City"
    if away_team_id == "32":
        away_team_name = "Man United"
    if away_team_id == "167":
        away_team_name = "Man City"
    if home_team_id == "175":
        home_team_name = "West Brom"
    if away_team_id == "175":
        away_team_name = "West Brom" 
    result = game_result(home_team_id, away_team_id, teamMeanContribution, coefficients, probabilities)
    required_odds = odds_dict[home_team_name][away_team_name]
    prob_odds_home = 1/required_odds[0]
    prob_odds_draw = 1/required_odds[1]
    prob_odds_away = 1/required_odds[2]
    sum_odds_prob = prob_odds_home + prob_odds_draw + prob_odds_away
    prob_odds_home = prob_odds_home/sum_odds_prob
    prob_odds_draw = prob_odds_draw/sum_odds_prob
    prob_odds_away = prob_odds_away/sum_odds_prob
    if result[0] == max(result):
        model_pred = 0
    if result[1] == max(result):
        model_pred = 1
    if result[2] == max(result):
        model_pred = 2
    if prob_odds_home == max([prob_odds_home, prob_odds_draw, prob_odds_away]):
        odds_pred = 0
    if prob_odds_draw == max([prob_odds_home, prob_odds_draw, prob_odds_away]):
        odds_pred = 1
    if prob_odds_away == max([prob_odds_home, prob_odds_draw, prob_odds_away]):
        odds_pred = 2
    if int(full_time_score[0]) > int(full_time_score[1]):
        actual_result = 0
    if int(full_time_score[0]) == int(full_time_score[1]):
        actual_result = 1
    if int(full_time_score[0]) < int(full_time_score[1]):
        actual_result = 2
    model_correct = 0
    odds_correct = 0
    payout = 0*required_odds[actual_result]
    if actual_result == model_pred:
        model_correct = 1
        payout = 1*required_odds[actual_result]
    if actual_result == odds_pred:
        odds_correct = 1
    fp.write(date + "," + matchId + "," + home_team_id + "," + home_team_name + "," + away_team_id + "," + away_team_name + "," + \
    half_time_score[0] + "," + half_time_score[1] + "," + full_time_score[0] + "," + full_time_score[1] + "," + str(result[0]) + "," \
    + str(result[1]) + "," + str(result[2]) + "," + str(required_odds[0]) + "," + str(required_odds[1]) + "," + str(required_odds[2]) \
    + "," + str(prob_odds_home) + "," + str(prob_odds_draw) + "," + str(prob_odds_away) + "," + str(model_pred) + "," + str(odds_pred)\
    + "," + str(model_correct) + "," + str(odds_correct) + "," + str(payout) + "\n")


fp.close()

