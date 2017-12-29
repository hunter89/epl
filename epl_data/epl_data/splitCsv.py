import csv
from splitList import *

match_list_file = 'season14-15.csv'
csvfile = open(match_list_file,'rU')
matches = csv.reader(csvfile,skipinitialspace = True)
url_list = []
count = 0
for row in matches:
        if (count != 0):
            url_list.append(row[0])
        count = count + 1

for i, split_url in enumerate(split_list(url_list, 50)):
    with open(str(str(i) + '.csv'), 'wb') as f:
        
        for url in split_url:
            f.write(url + '\n')
        f.close()