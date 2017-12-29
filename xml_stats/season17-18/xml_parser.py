# root[0] has match stats we are interested in
# root[0] has only one child hence we are effectively looking at root[0][0]
# root[0][0] has 2 child nodes; we are interested in only the first child node.
# root[0][0][0] has all the match events, team data and player data for the match
# let's refer to root[0][0][0] as the 'data' node
# data has 3 child nodes and each is explained as below

# data[0] ......
# data[0] has the aggregate match details like home and away team names, their ids, match scores
# let's call data[0] as match_details
# match_details have 15 child nodes; we are interested in 0, 1, 2, 3, 4, 8, 9 and
# they are -- in order - home_team_id, away_team_id, home_team_name, away_team_name, date_string, half_time_score, full_time_score

# data[1] ......
# data[1] has key match events like goals, yellow cards, substitution etc. let's not worry about this for now

##### note event processor is yet to be written as the data I am interested in doesn't demand it.

# data[2] ......
# data[2] has two child nodes one for each team stats starting -- home and away, in order
# let's call data[2] as match_stats
# further, let's call match_stats[0] as home_team_stats and match_stats[1] as away_team_stats
# home_team_stats{[0],[1],[2]} has home_team_id, home_team_name, and home_team_rating(not interested, hence ignored)

# home_team_stats[3] has aggregate team stats with only one child node but subsequent n nodes for that child nodes
# to process all n nodes of home_team_stats[3][0]
# for eg; to process the third node home_team_stats[3][0][2][0].text gives the string for the attribute and 
# home_team_stats[3][0][2][1][0].attrib['value'] gives the value for it; NOTICE the extra dummy node in between

# home_team_stats[4] has 18 child elements for the 18 players in the squad
# to process all the n nodes of home_team_stats[4] for player data
# for every player, first three nodes represent - player_id, player_name, player_rating
# to be processed as home_team_stats[4][i][0].attrib['value'], home_team_stats[4][i][1].text, home_team_stats[4][i][2].attrib['value']
# home_team_stats[4][i][3][0] has key value pairs for stats of each player
# home_team_stats[4][i][4].attrib['value'] gives position value for the player
# home_team_stats[4][i][5].text gives position for the player in formation, can be sub also

# ignore home_team_stats{[5],[6],[7]}

import xml.etree.ElementTree as etree
from collections import OrderedDict
import json
import os
import codecs

files = [f for f in os.listdir('.') if (os.path.isfile and ".xml" in f)]
season_match_details_dict = OrderedDict()
season_match_stats_dict = OrderedDict()

for xml_file in files:
    tree = etree.parse(xml_file)
    root = tree.getroot()

    data = root[0][0][0]
    
    match_details = data[0]
    match_details_dict = OrderedDict([
        ('home_team_id', match_details[0].attrib['value']),
        ('away_team_id', match_details[1].attrib['value']),
        ('home_team_name', match_details[2].text),
        ('away_team_name', match_details[3].text),
        ('date_string', match_details[4].text),
        ('half_time_score', match_details[8].text),
        ('full_time_score', match_details[9].text),
        ])
    
    season_match_details_dict.update([(xml_file[12:-4], match_details_dict)])

    #print match_details_json

    team_stats_dict = OrderedDict()

    for team_stats in data[2]:
        team_id = team_stats[0].attrib['value']
        team_name = team_stats[1].text
        team_rating = team_stats[2].attrib['value']
        thisteam_dict = OrderedDict()

        gen_team_dict = OrderedDict([
            ('team_id', team_id),
            ('team_name', team_name),
            ('team_rating', team_rating),
            ('date', match_details[4].text.split()[0])
        ])

        thisteam_dict.update([("team_details", gen_team_dict)])

        aggregate_team_stats = team_stats[3][0]
        aggregate_team_stats_dict = {stats[0].text: stats[1][0].attrib['value'] for stats in aggregate_team_stats}

        thisteam_dict.update([("aggregate_stats", aggregate_team_stats_dict)])
        #print aggregate_team_stats_dict
        all_player_stats_dict = OrderedDict()

        all_player_stats = team_stats[4]
        for player_stats in all_player_stats:
            player_id = player_stats[0].attrib['value']
            player_name = player_stats[1].text
            try:
                player_rating = player_stats[2].attrib['value']
            except KeyError:
                player_rating = '0'
            player_stats_dict = OrderedDict() 
            


            player_match_stats = player_stats[3][0]
            player_match_stats_dict = {stats[0].text: stats[1][0].attrib['value'] for stats in player_match_stats}  
            
            player_position_value = player_stats[4].attrib['value']
            player_position_info = player_stats[5].text
            gen_player_dict = OrderedDict([
                ('player_id', player_id),
                ('player_name', player_name),
                ('player_position_value', player_position_value),
                ('player_position_info', player_position_info),
                ('player_rating', player_rating)
            ])
            player_stats_dict.update([("player_details", gen_player_dict)])
            player_stats_dict.update([("Match_stats", player_match_stats_dict)])
            all_player_stats_dict.update([(player_name, player_stats_dict)])
        
        thisteam_dict.update([("Player_stats", all_player_stats_dict)])
        team_stats_dict.update([(team_id, thisteam_dict)])
    
    season_match_stats_dict.update([(xml_file[12:-4], team_stats_dict)])

f = codecs.getwriter('utf-8')(open("season_stats.json", "w")) 
json.dump(season_match_stats_dict, f, indent=4, separators=(',', ':'), encoding="utf-8", ensure_ascii=False)
f.close()

f = codecs.getwriter('utf-8')(open("season_match_stats.json", "w"))
json.dump(season_match_details_dict, f, indent=4, separators=(',', ':'), encoding="utf-8", ensure_ascii=False)
f.close()

#    filename = file_address[:-3] + ".json"
#    with open(filename, "wb") as f:
#        json.dump(team_stats_dict, f, indent=4, separators=(',', ':'))



