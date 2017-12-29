

fp = open("predicted_lineup.csv", "rb")
escapes = ''.join([chr(char) for char in range(1,32)])
matches_dict = {}
for line in fp:
    data = line.split(",")
    data[7] = data[7].translate(None, escapes)
    if data[6] == "1":
        player_tuple = (data[0], data[2], data[5])    
        if (data[4] in matches_dict.keys()):
            matches_dict[data[4]][data[7]].append(player_tuple)
        else:
            matches_dict.update({data[4]: {'1': [], '0': []}})
            matches_dict[data[4]][data[7]].append(player_tuple)

fp.close()

file_list = []  
for match_id, roster in matches_dict.iteritems():
    match_string = "match" + match_id + ".csv"
    fp = open(match_string, "wb")
    for player_list in roster['1']:
        fp.write(player_list[2] + "," + player_list[0] + "," + player_list[1] + "\n")
    for player_list in roster['0']:
        fp.write(player_list[2] + "," + player_list[0] + "," + player_list[1] + "\n")
    fp.close()
    file_list.append((match_string, match_id))

def rosterFiles():
    return file_list

