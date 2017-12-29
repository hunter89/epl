import numpy as np
from collections import OrderedDict
from scipy.stats import skew
import matplotlib.pyplot as plt

fp = open("playerStartsMeanContributions.csv", "rb")
playerMeanContributions = {}

count = 0
for line in fp:
    if count == 0:
        count += 1
        continue
    data = line.split(",")
    playerId = data[0]
    playerMeanContributions[playerId] = np.array([])
    for col in data[1:]:
        contribution = float(col)
        playerMeanContributions[playerId] = np.append(playerMeanContributions[playerId], contribution)
fp.close()

def predictor(rosterfile):

    fp = open(rosterfile, "rb")

    match = OrderedDict()
    count = 0
    escapes = ''.join([chr(char) for char in range(1,32)])


    for line in fp:
        data = line.split(",")
        team = data[0]
        player = data[1].translate(None, escapes)
        position = data[2].translate(None, escapes)

        if team in match.keys():
            match[team]["players"].append(player)
            match[team]["position"].append(position)
        else :
            match[team] = {"players": [player], "position":[position]}

    fp.close()
    
    contribution_dict = OrderedDict()
    match_contribution = {"home":{}, "away":{}} 
    team_name = "home"
    for team, value in match.iteritems():
        count = 0
        for player in value["players"]:
            if (value["position"][value["players"].index(player)] == "D"):
                isDefender = 1
            else:
                isDefender = 0
            if count == 0:
                count += 1
                contribution_dict[team] = playerMeanContributions[player]
                match_contribution[team_name].update({player : playerMeanContributions[player]})
                match_contribution[team_name][player] = np.append(match_contribution[team_name][player], isDefender)
                continue
            else :
                contribution_dict[team] = contribution_dict[team] + playerMeanContributions[player]
                match_contribution[team_name].update({player : playerMeanContributions[player]})
                match_contribution[team_name][player] = np.append(match_contribution[team_name][player], isDefender)
                 
        team_name = "away"
    
    count = 0
    for team, contribution in contribution_dict.iteritems():
        if count == 0:
            home_team_id = team
            home_team_contribution = contribution
            count += 1
        else:
            away_team_id = team
            away_team_contribution = contribution

    fp = open("info_file.csv", "rb")
    fp.readline()
    coefs = fp.readline().split(',')
    fp.readline()
    probs = fp.readline().split(',')
    fp.close()

    expectedshots_home = float(coefs[0]) + float(coefs[1])*home_team_contribution[0] + float(coefs[2])*home_team_contribution[1] + \
    float(coefs[3])*away_team_contribution[5] + float(coefs[4])*home_team_contribution[3] + float(coefs[5])*away_team_contribution[6] + \
    float(coefs[6])*away_team_contribution[7]

    expectedshots_away = float(coefs[0]) + float(coefs[1])*away_team_contribution[0] + float(coefs[2])*away_team_contribution[1] + \
    float(coefs[3])*home_team_contribution[5] + float(coefs[4])*away_team_contribution[3] + float(coefs[5])*home_team_contribution[6] + \
    float(coefs[6])*home_team_contribution[7]

    # home advantage
    expectedshots_home = 1.2*expectedshots_home 

    expectedshots = np.array([expectedshots_home, expectedshots_away])
    lambda_ = float(probs[0])*expectedshots

    factors_dict = {}
    for team, player_list in match_contribution.iteritems():
        factors_dict[team] = {}
        goal_factor_sum = 0
        assist_factor_sum = 0
        shot_factor_sum = 0
        cross_factor_sum = 0
        tackle_factor_sum = 0
        for player, contribution in match_contribution[team].iteritems():
            goal_factor_sum = goal_factor_sum + contribution[8]
            assist_factor_sum = assist_factor_sum + contribution[9]
            shot_factor_sum = shot_factor_sum + contribution[10]
            cross_factor_sum = cross_factor_sum + contribution[11]
            tackle_factor_sum = tackle_factor_sum + contribution[12] 
        factors_dict[team].update({"goal_factor_sum": goal_factor_sum, "assist_factor_sum": assist_factor_sum, "shot_factor_sum" : shot_factor_sum, "cross_factor_sum" : cross_factor_sum, "tackle_factor_sum": tackle_factor_sum})
    
    points_scenario = {}

    for i in range(1000):
        goals = np.random.poisson(lam = (lambda_[0], lambda_[1]))

        probabilities_dict = {}
        player_points = {"home": {"players":[], "points": np.array([])}, "away": {"players":[], "points": np.array([])}}
        for team, value in match_contribution.iteritems():
            probabilities_dict[team] = {"Player": [], "goal_probs": [], "assist_probs": [], "shot_probs": [], "cross_probs": [], "tackle_probs": [], "yellow_probs": []}
            if team == "home":
                goals_team = goals[0]
                goals_opp = goals[1]
                shots_team = expectedshots_home - goals_team
                tackles_team = home_team_contribution[5]
                
            else:
                goals_team = goals[1]
                goals_opp = goals[0]
                shots_team = expectedshots_away - goals_team
                tackles_team = away_team_contribution[5]
                

            if goals_team >= 2:
                assists_team = np.random.randint(goals_team - 2, goals_team + 1)
            else :
                assists_team = np.random.randint(goals_team + 1)
            
            crosses_team = 1.6*shots_team
            clean_sheet = (goals_opp == 0)
            win = (goals_team > goals_opp)
            defender_array = np.array([])
            yellows_array = np.array([])
            for player, contribution in value.iteritems():
                
                defender_array = np.append(defender_array, contribution[13])

                yellows_array = np.append(yellows_array, [np.random.binomial(1, contribution[6])])

                if contribution[4] >= 0.5:
                    goalkeeper = player
                    saves = np.random.poisson(contribution[4])
                    gk_pts = 2*saves - 2*goals_opp + 5*clean_sheet + 5*win
                    
                
                player_goal_prob = contribution[8]/factors_dict[team]["goal_factor_sum"]
                player_assist_prob = contribution[9]/factors_dict[team]["assist_factor_sum"]
                player_shot_prob = contribution[10]/factors_dict[team]["shot_factor_sum"]
                player_cross_prob = contribution[11]/factors_dict[team]["cross_factor_sum"]
                player_tackle_prob = contribution[12]/factors_dict[team]["tackle_factor_sum"]
                

                probabilities_dict[team]["Player"].append(player)
                probabilities_dict[team]["goal_probs"].append(player_goal_prob)
                probabilities_dict[team]["assist_probs"].append(player_assist_prob)
                probabilities_dict[team]["shot_probs"].append(player_shot_prob)
                probabilities_dict[team]["cross_probs"].append(player_cross_prob)
                probabilities_dict[team]["tackle_probs"].append(player_tackle_prob)
                    

            goals_array = np.random.multinomial(goals_team, probabilities_dict[team]["goal_probs"])
            assists_array = np.random.multinomial(assists_team, probabilities_dict[team]["goal_probs"])
            shots_array = np.random.multinomial(shots_team, probabilities_dict[team]["goal_probs"])
            cross_array = np.random.multinomial(crosses_team, probabilities_dict[team]["cross_probs"])
            tackles_array = np.random.multinomial(tackles_team, probabilities_dict[team]["tackle_probs"])
            interceptions_array = np.random.multinomial(tackles_team*1.5, probabilities_dict[team]["tackle_probs"])
            shots_ot_array = np.random.binomial(shots_array, 0.6)
            shots_array = shots_array


            # points except for goalkeeper
            points = goals_array*10 + assists_array*6 + shots_array*1 + shots_ot_array*1 + cross_array*0.75 + tackles_array*1 + interceptions_array*1.5 - yellows_array*1.5 + clean_sheet*defender_array*3
            
            # goalkeeper index
            goalkeeper_index = probabilities_dict[team]["Player"].index(goalkeeper)
            points[goalkeeper_index] = points[goalkeeper_index] + gk_pts

            player_points[team].update({"players": probabilities_dict[team]["Player"], "points": points})
            
            for i in range(len(player_points[team]["players"])):
                if player_points[team]["players"][i] in points_scenario.keys():
                    points_scenario[player_points[team]["players"][i]].append(player_points[team]["points"][i])
                else:
                    points_scenario[player_points[team]["players"][i]] = [player_points[team]["points"][i]]
    
    return points_scenario
    ''' 
    m = np.array([])
    fp = open("fantasyPointsPred.csv", "wb")
    count = 0
    player_list = []
    for player, point_list in points_scenario.iteritems():
        player_list.append(player)   
        player_mean_pts = np.mean(np.array(point_list))
        player_median_pts = np.median(np.array(point_list))
        fp.write(player + "," + str(player_mean_pts) + "," + str(player_median_pts) + "\n")
        if count == 0:
            m = [np.array(point_list)]
            count = 1
        else:
            m = np.append(m, [np.array(point_list)], axis = 0)
    fp.close()

    cov_mat = np.cov(m)

    fp = open("fantansyPlayerCovariance.csv", "wb")
    for player in player_list:
            fp.write("," + player)
    fp.write("\n")
    for i in range(len(player_list)):
        fp.write(player_list[i])
        for j in range(cov_mat.shape[1]):
            if (i == j):
                fp.write("," + "0")
            else:
                fp.write("," + str(cov_mat[i,j]))
            
        fp.write("\n")

    fp.close()
 '''

