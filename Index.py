from regression import shotRate
import numpy as np
from math import exp, factorial
import operator
import datetime

def matchEstimates(matchData, coefs, probs):

    expectedshots = []
    total_team_touches = []
    for teamId, value1 in matchData.iteritems():
        contributions=[]
        for key in matchData.keys():
            if key != teamId:
                opponent_teamId = key
        won_contest_sum = 0
        yellow_card_opp_sum = 0
        red_card_opp_sum = 0
        accurate_pass_sum = 0
        total_tackle_opp_sum = 0
        touches_sum = 0
        aerial_won_sum = 0
        for player_name, value2 in matchData[teamId]["Player_stats"].iteritems():
            for key in matchData[teamId]["Player_stats"][player_name]["Match_stats"].keys():
                if key == "won_contest":
                    won_contest_sum += float(matchData[teamId]["Player_stats"][player_name]["Match_stats"]["won_contest"])
                if key == "accurate_pass":
                    accurate_pass_sum += float(matchData[teamId]["Player_stats"][player_name]["Match_stats"]["accurate_pass"])
                if key == "touches":
                    touches_sum += float(matchData[teamId]["Player_stats"][player_name]["Match_stats"]["touches"])
                if key == "aerial_won": 
                    aerial_won_sum += float(matchData[teamId]["Player_stats"][player_name]["Match_stats"]["aerial_won"])   
        for player_name, value2 in matchData[opponent_teamId]["Player_stats"].iteritems():
            for key in matchData[opponent_teamId]["Player_stats"][player_name]["Match_stats"].keys():
                if key == "total_tackle":
                    total_tackle_opp_sum += float(matchData[opponent_teamId]["Player_stats"][player_name]["Match_stats"]["total_tackle"])
                if key == "yellow_card":
                    yellow_card_opp_sum += float(matchData[opponent_teamId]["Player_stats"][player_name]["Match_stats"]["yellow_card"])
                if key == "red_card":
                    red_card_opp_sum += float(matchData[opponent_teamId]["Player_stats"][player_name]["Match_stats"]["red_card"])
                if key == "second_yellow":
                    red_card_opp_sum += float(matchData[opponent_teamId]["Player_stats"][player_name]["Match_stats"]["second_yellow"])
        
        contributions.append(won_contest_sum)
        contributions.append(accurate_pass_sum)
        contributions.append(total_tackle_opp_sum)
        contributions.append(aerial_won_sum)
        contributions.append(yellow_card_opp_sum)
        contributions.append(red_card_opp_sum)

        total_team_touches.append(touches_sum)

        regression_pred = coefs[0] + coefs[1]*contributions[0] + coefs[2]*contributions[1] + coefs[3]*contributions[2] \
        + coefs[4]*contributions[3] + coefs[5]*contributions[4] + coefs[6]*contributions[5]
        expectedshots.append(regression_pred)
    expectedshots = np.array(expectedshots)
    lambda_ = probs[0]*expectedshots
    estimates = [lambda_, expectedshots, total_team_touches]
    return estimates

def goalProbabilities(lambda_):
    goal_probabilities = dict()
    sum_prob = 0
    points_home = 0
    points_away = 0
    for i in range(5):
        for j in range(5):
            a = str(j) + "-" + str(i)
            prob = exp(-(lambda_[0] + lambda_[1]))*pow(lambda_[0], j)*pow(lambda_[1], i)/(factorial(j)*factorial(i))
            if j > i:
                points_home += 3*prob
            if j < i:
                points_away += 3*prob
            if j ==i:
                points_away += prob
                points_home += prob
            sum_prob += prob
            goal_probabilities.update({a : prob})

    goal_probabilities = sorted(goal_probabilities.items(), key=operator.itemgetter(1))
    print points_home, points_away

def playerPoints(matchData, estimates, coefs, probs):
    lambda_ = estimates[0]
    expectedshots = estimates[1]
    total_team_touches = estimates[2]
    total_team_touches_home = total_team_touches[0]
    total_team_touches_away = total_team_touches[1]
    derivative_home = 0
    derivative_away = 0
    cross_positions_1 = ["ML", "MR", "AML", "AMR"]
    cross_positions_2 = ["FWL", "FWR", "DR", "DL", "DMR", "DML"]
    
    for i in range(5):
        for j in range(5):
            a = str(j) + "-" + str(i)
            prob = exp(-(lambda_[0] + lambda_[1]))*pow(lambda_[0], j)*pow(lambda_[1], i)/(factorial(j)*factorial(i))
            if j > i:
                derivative_home += prob*(j/lambda_[0] - 1)
            if j < i:
                derivative_away += prob*(i/lambda_[1] - 1)
    exp_pts = dict()            
    # count to keep track of home or away team
    for teamId, value1 in matchData.iteritems():
        clean_sheet_away = 0
        clean_sheet_home = 0
        for key in matchData.keys():
            if key != teamId:
                opponent_teamId = key
        if "goals" in matchData[teamId]["aggregate_stats"].keys():
            home_team_goal = float(matchData[teamId]["aggregate_stats"]["goals"])
        else:
            home_team_goal = 0
            clean_sheet_away = 1
        if "goals" in matchData[opponent_teamId]["aggregate_stats"].keys():
            away_team_goal = float(matchData[opponent_teamId]["aggregate_stats"]["goals"])
        else:
            away_team_goal = 0
            clean_sheet_home = 1
        
        if "total_scoring_att" in matchData[teamId]["aggregate_stats"].keys():
            home_team_shots = float(matchData[teamId]["aggregate_stats"]["total_scoring_att"])
        else:
            home_team_shots = 0
        if "total_scoring_att" in matchData[opponent_teamId]["aggregate_stats"].keys():
            away_team_shots = float(matchData[opponent_teamId]["aggregate_stats"]["total_scoring_att"])
        else:
            away_team_shots = 0
        if "total_tackle" in matchData[teamId]["aggregate_stats"].keys():
            home_team_tackle = float(matchData[teamId]["aggregate_stats"]["total_tackle"])
        else:
            home_team_tackle = 0
        if "total_tackle" in matchData[opponent_teamId]["aggregate_stats"].keys():
            away_team_tackle = float(matchData[opponent_teamId]["aggregate_stats"]["total_tackle"])
        else:
            away_team_tackle = 0
        
        if home_team_goal >= away_team_goal:
            if home_team_goal == away_team_goal:
                game_result_home = 1
                game_result_away = 1
            else:
                game_result_away = 0
                game_result_home = 3
        else:
            game_result_away = 3
            game_result_home = 0
        

        for player_name, value2 in matchData[teamId]["Player_stats"].iteritems():
            player_id = str(matchData[teamId]["Player_stats"][player_name]["player_details"]["player_id"])
            date = datetime.datetime.strptime(matchData[teamId]["team_details"]["date"], "%d/%m/%Y").strftime("%m/%d/%Y")
            won_contest = 0
            yellow_card_opp = 0
            red_card_opp = 0
            accurate_pass = 0
            total_tackle_opp = 0
            touches = 0
            aerial_won = 0
            saves = 0
            goals = 0
            assists = 0
            shots = 0
            cross_factor = 0
            player_position = int(matchData[teamId]["Player_stats"][player_name]["player_details"]["player_position_value"])
            player_position_info = str(matchData[teamId]["Player_stats"][player_name]["player_details"]["player_position_info"])
            if  player_position < 5:
                game_time = 0.85/11
                if player_position == 1:
                    defensive_actions = 0.3
                if player_position == 2:
                    defensive_actions = 0.14
                if player_position == 3 and str(matchData[teamId]["Player_stats"][player_name]["player_details"]["player_position_info"]) == "DMC":
                    defensive_actions = 0.14 
            else:
                game_time = 0.15/7

            if player_position_info in cross_positions_1:
                cross_factor = 0.30
            elif player_position_info in cross_positions_2:
                cross_factor = 0.20
            elif player_position_info == "GK" or player_position_info == "Sub":
                cross_factor = 0
            else :
                cross_factor = 0.05

            for key in matchData[teamId]["Player_stats"][player_name]["Match_stats"].keys():
                if key == "won_contest":
                    won_contest += float(matchData[teamId]["Player_stats"][player_name]["Match_stats"]["won_contest"])
                if key == "accurate_pass":
                    accurate_pass += float(matchData[teamId]["Player_stats"][player_name]["Match_stats"]["accurate_pass"])
                if key == "touches":
                    touches += float(matchData[teamId]["Player_stats"][player_name]["Match_stats"]["touches"])
                if key == "aerial_won": 
                    aerial_won += float(matchData[teamId]["Player_stats"][player_name]["Match_stats"]["aerial_won"])
                if key == "saves":
                    saves += float(matchData[teamId]["Player_stats"][player_name]["Match_stats"]["saves"])
                if key == "total_tackle":
                    total_tackle_opp += float(matchData[teamId]["Player_stats"][player_name]["Match_stats"]["total_tackle"])
                if key == "yellow_card":
                    yellow_card_opp += float(matchData[teamId]["Player_stats"][player_name]["Match_stats"]["yellow_card"])
                if key == "red_card":
                    red_card_opp += float(matchData[teamId]["Player_stats"][player_name]["Match_stats"]["red_card"])
                if key == "second_yellow":
                    red_card_opp += float(matchData[teamId]["Player_stats"][player_name]["Match_stats"]["second_yellow"])
                if key == "goals":
                    goals += float(matchData[teamId]["Player_stats"][player_name]["Match_stats"]["goals"])
                if key == "goal_assist":
                    assists += float(matchData[teamId]["Player_stats"][player_name]["Match_stats"]["goal_assist"])
                if key == "total_scoring_att":
                    shots += float(matchData[teamId]["Player_stats"][player_name]["Match_stats"]["total_scoring_att"])

            touch_factor = touches/total_team_touches_home
            if home_team_goal != 0:
                goal_factor = goals/home_team_goal
                assist_factor =  assists/home_team_goal
            else :
                goal_factor = 0
                assist_factor = 0
            if home_team_shots != 0:
                shot_factor = shots/home_team_shots
            else :
                shot_factor = 0
            if home_team_tackle != 0:
                tackle_factor = total_tackle_opp/home_team_tackle
            else:
                tackle_factor = 0
            contributions = np.array([won_contest, accurate_pass, touch_factor, aerial_won, saves, total_tackle_opp, yellow_card_opp, red_card_opp, goal_factor, assist_factor, shot_factor, cross_factor, tackle_factor])

            exp_pt_1 = 2*derivative_home*probs[0]*(coefs[1]*won_contest + coefs[2]*accurate_pass + coefs[4]*aerial_won) \
            - derivative_away*probs[0]*(coefs[3]*total_tackle_opp + coefs[5]*yellow_card_opp + coefs[6]*red_card_opp) \
            + derivative_away*probs[1]*saves/(expectedshots[1]*probs[2])*1.5
            exp_pt_2 = game_result_home*touch_factor
            exp_pt_3 = 1.37*game_time
            exp_pt_4 = 1.02*goals
            exp_pt_5 = 1.02*assists
            exp_pt_6 = 2.73*defensive_actions*clean_sheet_home
            exp_pt = exp_pt_1 + exp_pt_2*0.25 + exp_pt_3*0.15 + exp_pt_4*0.05 + exp_pt_5*0.05 + exp_pt_6*0.13
            exp_pts.update({player_id : [player_name, teamId, player_position, contributions, [exp_pt], date]})

        for player_name, value2 in matchData[opponent_teamId]["Player_stats"].iteritems():
            player_id = str(matchData[opponent_teamId]["Player_stats"][player_name]["player_details"]["player_id"])
            date = datetime.datetime.strptime(matchData[opponent_teamId]["team_details"]["date"], "%d/%m/%Y").strftime("%m/%d/%Y")
            won_contest = 0
            yellow_card_opp = 0
            red_card_opp = 0
            accurate_pass = 0
            total_tackle_opp = 0
            touches = 0
            aerial_won = 0
            saves = 0
            goals = 0
            assists = 0
            shots = 0
            player_position = int(matchData[opponent_teamId]["Player_stats"][player_name]["player_details"]["player_position_value"])
            player_position_info = str(matchData[opponent_teamId]["Player_stats"][player_name]["player_details"]["player_position_info"])
            if  player_position < 5:
                game_time = 0.85/11
                if player_position == 1:
                    defensive_actions = 0.3
                if player_position == 2:
                    defensive_actions = 0.13
                if player_position == 3 and str(matchData[opponent_teamId]["Player_stats"][player_name]["player_details"]["player_position_info"]) == "DMC":
                    defensive_actions = 0.13

            else:
                game_time = 0.15/7

            if player_position_info in cross_positions_1:
                cross_factor = 0.30
            elif player_position_info in cross_positions_2:
                cross_factor = 0.20
            elif player_position_info == "GK" or player_position_info == "Sub":
                cross_factor = 0
            else :
                cross_factor = 0.05

            for key in matchData[opponent_teamId]["Player_stats"][player_name]["Match_stats"].keys():
                if key == "won_contest":
                    won_contest += float(matchData[opponent_teamId]["Player_stats"][player_name]["Match_stats"]["won_contest"])
                if key == "accurate_pass":
                    accurate_pass += float(matchData[opponent_teamId]["Player_stats"][player_name]["Match_stats"]["accurate_pass"])
                if key == "touches":
                    touches += float(matchData[opponent_teamId]["Player_stats"][player_name]["Match_stats"]["touches"])
                if key == "aerial_won": 
                    aerial_won += float(matchData[opponent_teamId]["Player_stats"][player_name]["Match_stats"]["aerial_won"])
                if key == "saves":
                    saves += float(matchData[opponent_teamId]["Player_stats"][player_name]["Match_stats"]["saves"])
                if key == "total_tackle":
                    total_tackle_opp += float(matchData[opponent_teamId]["Player_stats"][player_name]["Match_stats"]["total_tackle"])
                if key == "yellow_card":
                    yellow_card_opp += float(matchData[opponent_teamId]["Player_stats"][player_name]["Match_stats"]["yellow_card"])
                if key == "red_card":
                    red_card_opp += float(matchData[opponent_teamId]["Player_stats"][player_name]["Match_stats"]["red_card"])
                if key == "second_yellow":
                    red_card_opp += float(matchData[opponent_teamId]["Player_stats"][player_name]["Match_stats"]["second_yellow"])
                if key == "goals":
                    goals += float(matchData[opponent_teamId]["Player_stats"][player_name]["Match_stats"]["goals"])
                if key == "goal_assist":
                    assists += float(matchData[opponent_teamId]["Player_stats"][player_name]["Match_stats"]["goal_assist"])
                if key == "total_scoring_att":
                    shots += float(matchData[opponent_teamId]["Player_stats"][player_name]["Match_stats"]["total_scoring_att"]) 
            
            touch_factor = touches/total_team_touches_away
            if away_team_goal != 0:
                goal_factor = goals/away_team_goal
                assist_factor =  assists/away_team_goal
            else :
                goal_factor = 0
                assist_factor = 0
            if away_team_shots != 0:
                shot_factor = shots/away_team_shots
            else :
                shot_factor = 0
            if away_team_tackle != 0:
                tackle_factor = total_tackle_opp/away_team_tackle
            else:
                tackle_factor = 0
            
            contributions = np.array([won_contest, accurate_pass, touch_factor, aerial_won, saves, total_tackle_opp, yellow_card_opp, red_card_opp, goal_factor, assist_factor, shot_factor, cross_factor, tackle_factor])

            exp_pt_1 = 2*derivative_away*probs[0]*(coefs[1]*won_contest + coefs[2]*accurate_pass + coefs[4]*aerial_won) \
            - derivative_home*probs[0]*(coefs[3]*total_tackle_opp + coefs[5]*yellow_card_opp + coefs[6]*red_card_opp) \
            + derivative_home*saves*probs[1]/(expectedshots[0]*probs[2])*1.5
            exp_pt_2 = game_result_away*touch_factor
            exp_pt_3 = 1.37*game_time
            exp_pt_4 = 1.02*goals
            exp_pt_5 = 1.02*assists
            exp_pt_6 = 2.73*defensive_actions*clean_sheet_away
            exp_pt = exp_pt_1 + exp_pt_2*0.25 + exp_pt_3*0.15 + exp_pt_4*0.05 + exp_pt_5*0.05 + exp_pt_6*0.13
            exp_pts.update({player_id : [player_name, opponent_teamId, player_position, contributions,[exp_pt], date]})

        break
    return exp_pts

def dict_update(dict1, matchUpdate):
    for key, value in matchUpdate.iteritems():
        if key in dict1.keys():
            dict1[key].append(matchUpdate[key][4][0])
        else:
            dict1[key] = matchUpdate[key][4]
def position_update(dict1, matchUpdate):
    # position vector is [others, postion1, position2, position3, position4, position5] 
    for key, value in matchUpdate.iteritems():
        position = int(matchUpdate[key][2])
        if key in dict1.keys():
            dict1[key][position] += 1
        else:
            dict1[key] = []
            for i in range(6):
                if i == position:
                    dict1[key].append(1)
                else:
                    dict1[key].append(0)

def contributions_update(dict1, matchUpdate):
    # contributions vector is [won_contest, accurate_pass, touch_factor, aerial_won, saves, total_tackle_opp, yellow_card_opp, red_card_opp, goals, assists]
    for key, value in matchUpdate.iteritems():
        contributions = matchUpdate[key][3]
        if key in dict1.keys():
            dict1[key] = dict1[key] + contributions
        else:
            dict1[key] = contributions
def player_name_update(dict1, matchUpdate):
    for key, value in matchUpdate.iteritems():
        player_name = matchUpdate[key][0]
        player_team = matchUpdate[key][1]
        if key in dict1.keys():
            if player_team in dict1[key][1].keys():
                dict1[key][1][player_team] += 1

            else:
                dict1[key][1][player_team] = 1

        else:
            dict1[key]=[]
            dict1[key].append(player_name)
            dict1[key].append({player_team: 1})
            
def summary_update(dict_1, matchUpdate):
    for key, value in matchUpdate.iteritems():
        contributions = matchUpdate[key][3]
        position = matchUpdate[key][2]
        pts = matchUpdate[key][4][0]
        date = matchUpdate[key][5]
        updated_array = np.append(contributions, position)
        updated_array = np.append(updated_array, pts)
        if key in dict_1.keys():
            dict_1[key][date] = updated_array
            
        else:
            dict_1[key] = {}
            dict_1[key][date] = updated_array
            
            
def roster_update(dict1, matchUpdate):
    for player_id, value in matchUpdate.iteritems():
        team_id = value[1]
        if team_id in dict1.keys():
            if player_id in dict1[team_id].keys():
                if value[2] < 5:
                    dict1[team_id][player_id][0] += 1/38.0
                else:
                    dict1[team_id][player_id][1] += 1/38.0
            else:
                dict1[team_id][player_id] = [0, 0]
                if value[2] < 5:
                    dict1[team_id][player_id][0] += 1/38.0
                else:
                    dict1[team_id][player_id][1] += 1/38.0
        else:
            dict1[team_id] = dict()
            dict1[team_id][player_id] = [0, 0]
            if value[2] < 5:
                dict1[team_id][player_id][0] += 1/38.0
            else:
                dict1[team_id][player_id][1] += 1/38.0
    


def aggregate_to_mean_contribution(dict1, aggregate_dict):
    for player_id, player_data in aggregate_dict.iteritems():
        beta = 0.9
        num_starts = 0
        num_subs = 0
        sorteddates = aggregate_dict[player_id].keys()
        sorteddates.sort()
        for date in sorteddates:
            match_data = aggregate_dict[player_id][date]
            contribution = match_data[:-2]
            if match_data[-2] < 5:
                if num_starts == 0:
                    player_start = contribution
                    num_starts += 1
                else:
                    player_start = beta*player_start + (1-beta)*contribution
                    num_starts += 1
            else:
                if num_subs == 0:
                    player_sub = contribution
                    num_subs += 1
                else:
                    player_sub = beta*player_sub + (1-beta)*contribution
                    num_subs += 1
        if num_starts > 0:
            player_start = player_start
        else:
            player_start = 0*player_sub
        if num_subs > 0:
            player_sub = player_sub
        else:
            player_sub = 0*player_start
        
        dict1[player_id] = [player_start, player_sub]      

def match_contributions(dict1, mean_contribution_dict, team_roster_dict):
    for team_id, home_players in team_roster_dict.iteritems():
        count_home = 0
        for player, appearances in home_players.iteritems():
            if count_home > 0:
                home_contribution = home_contribution + mean_contribution_dict[player][0][:-5]*appearances[0] \
                + mean_contribution_dict[player][1][:-5]*appearances[1]
            else:
                home_contribution = mean_contribution_dict[player][0][:-5]*appearances[0] \
                + mean_contribution_dict[player][1][:-5]*appearances[1]
            
            count_home += 1
        dict1[team_id] = home_contribution

def game_result(home_team_id, away_team_id, teamMeanContribution_dict, coefs, probs):
    home_team_contribution = teamMeanContribution_dict[home_team_id]
    away_team_contribution = teamMeanContribution_dict[away_team_id]
    
    expectedshots_home = coefs[0] + coefs[1]*home_team_contribution[0] + coefs[2]*home_team_contribution[1] + \
    coefs[3]*away_team_contribution[5] + coefs[4]*home_team_contribution[3] + coefs[5]*away_team_contribution[6] + \
    coefs[6]*away_team_contribution[7]

    expectedshots_away = coefs[0] + coefs[1]*away_team_contribution[0] + coefs[2]*away_team_contribution[1] + \
    coefs[3]*home_team_contribution[5] + coefs[4]*away_team_contribution[3] + coefs[5]*home_team_contribution[6] + \
    coefs[6]*home_team_contribution[7]

    expectedshots = np.array([expectedshots_home, expectedshots_away])
    expectedshots = [1.2, 1]*expectedshots
    lambda_ = probs[0]*expectedshots
    home_win_prob = 0
    draw_prob = 0
    away_win_prob = 0
    
    for i in range(10):
        for j in range(10):
            prob = exp(-(lambda_[0] + lambda_[1]))*pow(lambda_[0], j)*pow(lambda_[1], i)/(factorial(j)*factorial(i))
            if j > i:
                home_win_prob += prob
            if j < i:
                away_win_prob += prob
            if j == i:
                draw_prob += prob
    sum_prob = home_win_prob + away_win_prob + draw_prob
    home_win_prob = home_win_prob/sum_prob
    away_win_prob = away_win_prob/sum_prob
    draw_prob = draw_prob/sum_prob

    return [home_win_prob, draw_prob, away_win_prob]