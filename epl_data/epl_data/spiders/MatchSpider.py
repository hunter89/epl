import scrapy
import scrapy_splash 
import js2xml
import re
import csv
import sys
import numpy as np
from epl_data.items import MatchItem
import requests



class MatchSpider(scrapy.Spider):
    name = 'Match'
    allowed_domains = ["whoscored.com"]
    match_list_file = '0.csv'
    try:
        csvfile = open(match_list_file,'rU')
        matches = csv.reader(csvfile,skipinitialspace = True) # read the csv file and return a reader object
    except IOError:
        sys.exit("Cannot open file %s\n" % match_list_file)
    start_urls = []
    for row in matches:
        start_urls.append(row[0])
            
    def start_requests(self):
        
        for url in self.start_urls:
            yield scrapy_splash.SplashRequest(url=url, callback=self.parse,
                    args={
                        # set rendering arguments
                        'html': 1,
                        'wait': 10,
                      },
                    endpoint= 'render.html',
                    slot_policy=scrapy_splash.SlotPolicy.SCRAPY_DEFAULT
                ) 


    def parse(self, response):
        
        match = MatchItem()
        
        jscode = response.xpath('//script[contains(., "var matchId")]/text()').extract_first()
        match_details_xml = js2xml.parse(jscode)
        matchId = match_details_xml.xpath('//var[@name="matchId"]/number/attribute::*')
        match["homeTeamId"] = match_details_xml.xpath('//var[@name="homeTeamId"]/number/attribute::*')
        match["awayTeamId"] = match_details_xml.xpath('//var[@name="awayTeamId"]/number/attribute::*')
        

        
        #print matchId, homeTeamId, awayTeamId

        jscode = response.xpath('//script[contains(., "var matchStats")]/text()').extract_first()
        # very important regex for choosing from '[' (including '[') and before ';' (excluding ';')
        # prog = re.compile(r'\[[^;]*(?=;)')
        # which apparently is useless
        #result = re.search(r'\[[^;]*(?=;)', jscode, re.M).group()
        #matchStats = ast.literal_eval(result)
        match["matchId"] = matchId
        match_stats_xml = js2xml.parse(jscode)
        filename = 'match_stats-%s.xml' % matchId[0]
        with open(filename, 'wb') as f:
            f.write(js2xml.pretty_print(match_stats_xml).encode('utf-8'))
            f.close()
        filename = 'whoscored.html' 
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('saved file %s\n' % filename)
        
        ''' url1 = "#live-player-home-summary"
        url2 = "#live-player-home-offensive"
        url3 = "#live-player-home-defensive"
        url4 = "#live-player-home-passing"

        if True:

            # home player summary stats 
            match["home_player_id"] = response.css("div#statistics-table-home-summary > table > tbody > tr > td > a.player-link::attr(href)").re(r'\d+')
            match["home_player_name"] = response.css("div#statistics-table-home-summary > table > tbody > tr > td > a.player-link::text").extract()
            match["home_player_total_shots"] = response.css("div#statistics-table-home-summary > table > tbody > tr > td.ShotsTotal::text").extract()
            match["home_player_shots_on_target"] = response.css("div#statistics-table-home-summary > table > tbody > tr > td.ShotOnTarget::text").extract()
            match["home_player_keypasses"] = response.css("div#statistics-table-home-summary > table > tbody > tr > td.KeyPassTotal::text").extract()
            match["home_player_PA"] = response.css("div#statistics-table-home-summary > table > tbody > tr > td.PassSuccessInMatch::text").extract()
            match["home_player_aerial_duel"] = response.css("div#statistics-table-home-summary > table > tbody > tr > td.DuelAerialWon::text").extract()
            match["home_player_touches"] = response.css("div#statistics-table-home-summary > table > tbody > tr > td.Touches::text").extract()
        if url2 in response.url:
            match["home_player_dribble"] = response.css("div#statistics-table-home-offensive > table > tbody > tr > td.DribbleWon::text").extract()



        # away player stats

        match["away_player_id"] = response.css("div#statistics-table-away-summary > table > tbody > tr > td > a.player-link::attr(href)").re(r'\d+')
        match["away_player_name"] = response.css("div#statistics-table-away-summary > table > tbody > tr > td > a.player-link::text").extract()
        match["away_player_total_shots"] = response.css("div#statistics-table-away-summary > table > tbody > tr > td.ShotsTotal::text").extract()
        match["away_player_shots_on_target"] = response.css("div#statistics-table-away-summary > table > tbody > tr > td.ShotOnTarget::text").extract()
        match["away_player_keypasses"] = response.css("div#statistics-table-away-summary > table > tbody > tr > td.KeyPassTotal::text").extract()
        match["away_player_PA"] = response.css("div#statistics-table-away-summary > table > tbody > tr > td.PassSuccessInMatch::text").extract()
        match["away_player_aerial_duel"] = response.css("div#statistics-table-away-summary > table > tbody > tr > td.DuelAerialWon::text").extract()
        match["away_player_touches"] = response.css("div#statistics-table-away-summary > table > tbody > tr > td.Touches::text").extract() '''

'''         #print home_player_id, home_player_name, home_player__total_shots, home_player__shots_on_target, home_player__keypasses, home_player__PA, home_player__aerial_duel, home_player__touches
        #print away_player_id, away_player_name, away_player_total_shots, away_player_shots_on_target, away_player_keypasses, away_player_PA, away_player_aerial_duel, away_player_touches
        
        yield match '''
        
    

       

    
        