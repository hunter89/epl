import scrapy
import scrapy_splash
import csv
import sys

class matches(scrapy.Spider):
    name = 'matchesLinks'
    allowed_domains = ["whoscored.com"]
    start_urls = ['https://www.whoscored.com/Regions/252/Tournaments/2/Seasons/6335/England-Premier-League']

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy_splash.SplashRequest(url=url, callback=self.parse,
                args={
                    # set rendering arguments
                    'html': 1,
                    'wait': 5,
                },
                endpoint= 'render.html',
            )
    
    def parse(self, response):
        filename = 'matches_data.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('saved file %s\n' % filename)
