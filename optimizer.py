from rosterMaker import rosterFiles
from fantasy_pred import predictor
import numpy as np
from gurobipy import *

file_list = rosterFiles()

predicted_points = {}
for rosterfile in file_list:
    predicted_points.update({rosterfile[1]: predictor(rosterfile[0])})

num_matches = len(predicted_points.keys())

cov_mat = np.zeros([num_matches*22, num_matches*22])
player_list = []
median_list = []
fp = open("fantasyPointsPred.csv", "wb")
m = np.array([])
match_count = 0
for match_id, point_dict in predicted_points.iteritems():
    count = 0
    temp_mat = np.array([])
    for player, point_list in point_dict.iteritems():
        player_list.append(player)   
        player_mean_pts = np.mean(np.array(point_list))
        player_median_pts = np.median(np.array(point_list))
        median_list.append(player_median_pts)
        fp.write(player + "," + str(player_mean_pts) + "," + str(player_median_pts) + "\n")
        if count == 0:
            temp_mat = [np.array(point_list)]
            count = 1
        else:
            temp_mat = np.append(temp_mat, [np.array(point_list)], axis = 0)
    cov_mat[match_count*22:(match_count + 1)*22, match_count*22:(match_count + 1)*22] = np.cov(temp_mat)
    match_count += 1
fp.close()

    

fp = open("fantasyPlayerCovariance.csv", "wb")
for player in player_list:
        fp.write("," + player)
fp.write("\n")
for i in range(len(player_list)):
    fp.write(player_list[i])
    for j in range(cov_mat.shape[1]):
        # if (i == j):
        #     fp.write("," + "0")
        # else:
        #     fp.write("," + str(cov_mat[i,j]))
        fp.write("," + str(cov_mat[i,j]))            
    fp.write("\n")

fp.close()
fp = open("predicted_lineup.csv", "rb")
escapes = ''.join([chr(char) for char in range(1,32)])
player_dict = {}
team_dict = {}
for line in fp:
    data = line.split(",")
    if data[6] == "1":
        player_dict.update({data[0]: [data[2], data[3], data[5]]})
        if data[5] in team_dict.keys():
            team_dict[data[5]] += 1
        else:
            team_dict.update({data[5]: 1})
fp.close()


try :
    m = Model("lineup")
    player_tuplelist = tuplelist()
    cost_tuplelist = tuplelist()
    for player in player_list:
        if player_dict[player][0] == "M/F":
            t_ = (player, "M", player_dict[player][2])
            player_tuplelist.append(t_)
            t_ = (player, "F", player_dict[player][2])
            player_tuplelist.append(t_)
        else:
            t_ = (player, player_dict[player][0], player_dict[player][2])
            player_tuplelist.append(t_)
    x = m.addVars(player_tuplelist, vtype = GRB.BINARY, name = "x")
    team = m.addVars(team_dict.keys(), vtype = GRB.BINARY, name = "team")
    
    
    salary = {}
    points = {}
    cor = QuadExpr()
    var = QuadExpr()
    lambda_1 = 0.1
    lambda_2 = 0.1
    for t in player_tuplelist:
        salary.update({t : int(player_dict[t[0]][1])})
        points.update({t : median_list[player_list.index(t[0])]})
        for p in player_tuplelist:
            if t[0] != p[0]:
                cor.addTerms(cov_mat[player_list.index(t[0]), player_list.index(p[0])], x[t], x[p])
            else:
                var.addTerms(cov_mat[player_list.index(t[0]), player_list.index(p[0])], x[t], x[p])
    
    
    # set objective to maximize player median points
    m.setObjective(x.prod(points) + lambda_1*cor + lambda_2*var, GRB.MAXIMIZE)
    # constraint for sum of all variables related to player be less than 1
    m.addConstrs((x.sum(player, "*", "*") <= 1 for player in player_list if player_dict[player][0] == "M/F"), name = "duplicity")
    # total number of players is 8
    m.addConstr(x.sum("*", "*", "*") == 8, "total")
    # total of 1 goalkeeper
    m.addConstr(x.sum("*", "GK", "*") == 1, "goalkeeper")
    # atleast 2 defenders
    m.addConstr(x.sum("*", "D", "*") >= 2, "defender")
    # atleast 2 midfielders
    m.addConstr(x.sum("*", "M", "*") >= 2, "midfielder")
    # atleast 2 forwards
    m.addConstr(x.sum("*", "F", "*") >= 2, "forwards")
    
    # dynamic constraint
    # m.addConstr(x.sum("79554", "*", "*") == 0, "player1")
    # m.addConstr(x.sum("3859", "*", "*") == 0, "player2")
    # m.addConstr(x.sum("122945", "*", "*") == 0, "player3")
    # m.addConstr(x.sum("108226", "*", "*") == 0, "player4")
    # m.addConstr(x.sum("106880", "*", "*") == 0, "player5")
    # m.addConstr(x.sum("74921", "*", "*") == 0, "player6")
    # m.addConstr(x.sum("75830", "*", "*") == 0, "player7")
    # m.addConstr(x.sum("110189", "*", "*") == 0, "player8")
    # m.addConstr(x.sum("42248", "*", "*") == 0, "player9")
    # m.addConstr(x.sum("108724", "*", "*") == 0, "player10")
    # m.addConstr(x.sum("78498", "*", "*") == 0, "player11")
    # m.addConstr(x.sum("24711", "*", "*") == 0, "player12")
    # m.addConstr(x.sum("317506", "*", "*") == 0, "player13")
    # m.addConstr(x.sum("8040", "*", "*") == 0, "player14")
    # m.addConstr(x.sum("33404", "*", "*") == 0, "player15")
    # m.addConstr(x.sum("21427", "*", "*") == 0, "player16")
    #m.addConstr(team.sum("*") <= 4, name = "teams_constraint2")

    # more than 3 teams represented
    m.addConstrs((team[t] - x.sum("*", "*", t) <= 0 for t in team_dict.keys()), name = "c0")
    m.addConstrs((100*team[t] - x.sum("*", "*", t) >= 0 for t in team_dict.keys()), name = "c1")
    m.addConstr(team.sum("*") >= 3, name = "teams_constraint")

    # budget constraint
    m.addConstr(x.prod(salary) <= 50000, name = "budget")
    
    m.write("model.lp")
    
    m.optimize()

    for v in m.getVars():
        if v.x > 0:
            print v.varName
        
    print('Obj: %g' % m.objVal)

except GurobiError:
    print("Error Reported")
