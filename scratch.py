
print(response)

print(bearer_token)
headers = {'authorization': bearer_token}
response = requests.get('https://api.underdogfantasy.com/v2/user/slates/87a5caba-d5d7-46d9-a798-018d7c116213/live_drafts?page=2' \
                        , headers=headers
                        )
print(response)    

    
data = response.json()
print(len(data['drafts']))

from scrape_league_data import read_in_site_data

auth_header = {'authorization': bearer_token}
url_leagues_base = 'https://api.underdogfantasy.com/v2/user/slates/87a5caba-d5d7-46d9-a798-018d7c116213/live_drafts'

url_exists = True
i = 1
leagues_json_dict = {}
while url_exists:
    if i == 1:
        url = url_leagues_base
    else:
        url = url_leagues_base + '?page=' + str(i)
        
    leagues = read_in_site_data(url, headers=auth_header)
        
    if len(leagues['drafts']) > 0:
        leagues_json_dict['leagues_' + str(i)] = leagues
    else:
        url_exists = False
        
    i += 1

print(leagues_json_dict)

# print(response.status_code)

# print(data)
# print(len(data['drafts']))
# print(data['drafts'][0])


league_id = 'f75ed573-6a11-4e59-b712-1e8826d05c44'    
# auth_id = 'eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI2ZjIwOWFhNi1jY2ZlLTQwMTEtOTliZi0xODU2M2I4MzhkNDQiLCJzdWIiOiIwMzcxNzEzMS1lMDUzLTQ1MWQtOWJlNi0wOTc1NWY1ODc1YWUiLCJzY3AiOiJ1c2VyIiwiYXVkIjpudWxsLCJpYXQiOjE2MzUzMDY0NjEsImV4cCI6MTYzNzkzNjIwN30.ECGTEyF8dNeYo2FLHO6ayyUhw4Jkb9n5tElSWeYS14E'


url_draft = 'https://api.underdogfantasy.com/v2/drafts/' + league_id
url_weekly_scores = 'https://api.underdogfantasy.com/v2/drafts/' + league_id + '/weekly_scores'

url_players = 'https://stats.underdogfantasy.com/v1/slates/87a5caba-d5d7-46d9-a798-018d7c116213/players'

auth_header = {'authorization': 'Bearer ' + auth_id}

session = requests.session()

# raw = session.get(url_draft, headers=headers).text
raw = session.get(url_players, headers=headers).text

print(raw)


import requests
import json
import datetime

today = datetime.datetime.today()
session = requests.session()

url = "https://hyland.csod.com:443/ux/ats/careersite/4/home?c=hyland"
headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:71.0) Gecko/20100101 Firefox/71.0", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5", "Accept-Encoding": "gzip, deflate", "DNT": "1", "Connection": "close", "Upgrade-Insecure-Requests": "1"}

raw = session.get(url, headers=headers).text
token = raw[raw.index("token")+8:]
print(raw)




# url_draft_json = read_in_site_data(url_draft)
# weekly_scores_json = read_in_site_data(url_weekly_scores, auth_header)

# print(url_draft_json)



# base_url_player_scores = 'https://stats.underdogfantasy.com/v1/weeks/'
# end_url_player_scores = '/scoring_types/ccf300b0-9197-5951-bd96-cba84ad71e86/appearances'
# player_scores_wk_1_id = 78
# urls_player_scores = {'url_player_scores_wk_' + str(i + 1): base_url_player_scores + str(wk_id) + end_url_player_scores 
#                       for i, wk_id in enumerate(range(player_scores_wk_1_id,  player_scores_wk_1_id + 17))}




import requests

headers = {
    'authority': 'api.underdogfantasy.com',
    'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
    'user-longitude': '-79.969023',
    'sec-ch-ua-mobile': '?0',
    'user-latitude': '40.3820326',
    'authorization': '',
    'content-type': 'application/json',
    'accept': 'application/json',
    'referring-link': '',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36',
    'client-version': '202110251202',
    'client-type': 'web',
    'sec-ch-ua-platform': '"Windows"',
    'origin': 'https://underdogfantasy.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://underdogfantasy.com/',
    'accept-language': 'en-US,en;q=0.9',
}


response = requests.post('https://api.underdogfantasy.com/v1/users/sign_in', headers=headers, data=data)

print(response.json())