# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class MatchItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    matchId = Field()
    homeTeamId = Field()
    awayTeamId = Field()

    home_player_id = Field()
    home_player_name = Field()
    home_player_total_shots = Field()
    home_player_shots_on_target = Field()
    home_player_keypasses = Field()
    home_player_PA = Field()
    home_player_aerial_duel = Field()
    home_player_touches = Field()
    home_player_dribble = Field()

    away_player_id = Field()
    away_player_name = Field()
    away_player_total_shots = Field()
    away_player_shots_on_target = Field()
    away_player_keypasses = Field()
    away_player_PA = Field()
    away_player_aerial_duel = Field()
    away_player_touches = Field()
