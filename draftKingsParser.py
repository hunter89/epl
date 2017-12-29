import unicodedata
import re
import numpy as np

fp = open("teamKey.csv", "rb")
team_dict = {}
escapes = ''.join([chr(char) for char in range(1,32)])
for line in fp:
    data = line.split(",")
    team_name = data[0]
    team_id = data[1].translate(None, escapes)
    team_dict.update({team_name: team_id})

fp.close()
fp = open("playerKey.csv", "rb")
player_dict = {}
for line in fp:
    data = line.split(",")
    player_id = data[0]
    player_name = data[1].translate(None, escapes)
    player_dict.update({player_name: player_id})

unidentifiedIgnore = []
fp = open("unidentifiedIgnore.csv", "r")
for line in fp:
    unidentifiedIgnore.append(line.translate(None, escapes))
fp.close()

fp = open("DKSalaries.csv", "rb")
salaries_dict = {}
matches_dict = {}
game_list = np.array([])
unidentified = []
count = 0

for line in fp:
    if count == 0:
        count = 1
        continue
    data = line.replace('"', '').split(",")
    player_name = data[1]
    if player_name.startswith((" ")):
        player_name = player_name[1:]

    position = data[0]
    salary = int(data[2])
    fppg = float(data[4])
    game_string = data[3]
    game_list = np.append(game_list, game_string)
    team = team_dict[data[5].translate(None, escapes)]
    if (player_name in player_dict.keys()):
        salaries_dict.update({player_dict[player_name]: [player_name, position, salary, game_string, team]})
    elif (player_name == 'Pascal Gro\xdf'):
        salaries_dict.update({"71824": [player_name, position, salary, game_string, team]})
    elif (player_name == 'Pierre-Emile H\xf8jbjerg'):
        salaries_dict.update({"101859": [player_name, position, salary, game_string, team]})
    elif (player_name in unidentifiedIgnore):
        continue
    elif fppg == 0 and not(player_name in unidentifiedIgnore):
        unidentifiedIgnore.append(player_name)
        continue
    else:
        unidentified.append(player_name)

fp.close()
print unidentified

 
# fp = open("unidentifiedIgnore.csv", "w")
# for i in unidentifiedIgnore:
#     fp.write(i + "\n")
# fp.close()

 
# fp = open("unidentifiedIgnore.csv", "w")
# for i in unidentified:
#     fp.write(i + "\n")
# fp.close()

game_list = np.unique(game_list)
game_dict = {}
for i in range(len(game_list)):
    game_dict.update({game_list[i]:i})

fp = open("salariesDict.csv", "wb")
for player_id, data in salaries_dict.iteritems():
    data[3] = game_dict[data[3]]
    fp.write(player_id)
    for item in data:
        fp.write("," + str(item))
    fp.write("\n")








