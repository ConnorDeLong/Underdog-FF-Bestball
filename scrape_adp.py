"""
Module is responsible for scraping the Underdog's ADP data
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import numpy as np
import time
from datetime import date
import os

''' NOTES
    - A player will ALWAYS have an ADP, but not necessarily a bye (not on a team). This means that WebElement that is
    assigned to the "elem_bye_adps" variable doesn't always follow the "bye" then "adp" order
    - ASSUMING that every player has a position - this is currently the case, but might not be in the future 
    (doubt it though)
    - Headless option doesn't seem to return anything for the main data elements
'''

def create_webdriver(url, chromedriver_path, username, password):
    driver = webdriver.Chrome(chromedriver_path)
    driver.get(url)
    
    elem = driver.find_elements_by_class_name('styles__field__3fmc7')[0]
    elem.clear()
    elem.send_keys(username)
    elem.send_keys(Keys.RETURN)
    
    elem = driver.find_elements_by_class_name('styles__field__3fmc7')[1]
    elem.clear()
    elem.send_keys(password)
    elem.send_keys(Keys.RETURN)
    
    return driver


class ScrapeAdp():
    
    def __init__(self, url, chromedriver_path, username, password, driver=None):
        
        self.url = url
        self.chromedriver_path = chromedriver_path
        self.username = username
        self.password = password
        
        if driver is None:
            self.driver = self._create_webdriver()
            
            # Need to allow the driver time to fully process the request
            time.sleep(10)
        else:
            self.driver = driver
            
        self.df_adp = None
        
    def scrape_adp(self):
        ''' Creates a dataframe containing the ADP data '''
        
        initial_df = self._process_all_players_data()
        final_df = self._clean_df(initial_df)
        
        self.df_adp = final_df.copy()
        
        self._test_data_assumptions(final_df)
        
        return final_df
    
    def _test_data_assumptions(self, df):
        ''' Prints out how some high level checks align with assumptions about the data '''
        df = df.copy()
        
        position_count = len(df.groupby(['Position'], as_index=False)['Position'].size())
        team_count = len(df.groupby(['Team'], as_index=False)['Team'].size())
        
        if team_count == 33:
            print('All teams are represented in the data')
        elif team_count > 33:
            print('Teams field contains too many unique values')
        elif team_count < 33:
            print('Not all teams are represented in the data')
            
        if position_count == 4:
            print('All positions are represented in the data')
        else:
            print('There is a problem with the Positions field')
    
    def _process_player_data(self, elem_player) -> list:
        ''' Pulls out the Player name, Position, Bye, and ADP for a web element representing an individual player '''
        
        class_name_player_name = 'styles__playerName__1EFeQ'
        class_name_position = 'styles__playerPosition__2KPHG'
        class_name_bye_adps = 'styles__statValue__3BAOt'
        class_name_bye_adp_ids = 'styles__statKey__1xe-s'    
        
        player_name = elem_player.find_elements_by_class_name(class_name_player_name)[0].text
        player_pos = elem_player.find_elements_by_class_name(class_name_position)[0].text
        player_pos = player_pos.replace('\n', ' - ')
        
        elem_bye_adps = elem_player.find_elements_by_class_name(class_name_bye_adps)
        elem_bye_adp_ids = elem_player.find_elements_by_class_name(class_name_bye_adp_ids)
        
        # Set the variables for instances where these aren't available
        player_bye = 0
        player_adp = 9999
        for bye_adp_index in range(len(elem_bye_adp_ids)):
            if elem_bye_adp_ids[bye_adp_index].text == 'Bye':
                player_bye = elem_bye_adps[bye_adp_index].text
                
            elif elem_bye_adp_ids[bye_adp_index].text == 'ADP':
                player_adp = elem_bye_adps[bye_adp_index].text
    
        player_data = [player_name, player_pos, player_bye, player_adp]
        
        return player_data
    
    def _process_all_players_data(self) -> pd.DataFrame:
        
        class_name_all_players = 'styles__playerCellWrapper__1cf1R'
        
        elem_all_players = self.driver.find_elements_by_class_name(class_name_all_players)
        
        all_player_data = []
        for rank, elem_player in enumerate(elem_all_players):
            player_data = self._process_player_data(elem_player)
            
            # Add a rank variable to the front of the list
            rank_list = [rank]
            rank_list.extend(player_data)
            
            all_player_data.append(rank_list)
            
        cols = ['Rank', 'Player', 'Position/Team', 'Bye', 'ADP']
        final_df = pd.DataFrame(all_player_data, columns=cols)
        
        return final_df
    
    def _clean_df(self, df):
        
        df = df.copy()
        
        # Replacing ADP with Rank when the ADP is missing
        df['ADP'] = np.where(df['ADP'] == '-', df['Rank'], df['ADP'])
        df['ADP'] = np.where(df['ADP'] == 9999, df['Rank'], df['ADP'])
        
        # Create index to slice the Position/Team column
        df['pos_team_slice_index'] = df['Position/Team'].str.find(' - ')
        df.loc[df['pos_team_slice_index'] == -1, 'pos_team_slice_index'] = df['Position/Team'].str.len()
    
        # Split out the 'Position/Team' column
        df['Position'] = df.apply(lambda x: x['Position/Team'][0:x['pos_team_slice_index']], 1)
        df.loc[df['Position/Team'].str.len() != df['pos_team_slice_index'], 'Team'] = df.apply(
            lambda x: x['Position/Team'][x['pos_team_slice_index'] + 3:], 1)
        
        # Just going to assume no player will ever have dual position eligibility
        df['Position'] = df.apply(lambda x: x['Position'][0:2], 1)
        
        final_cols = ['Rank', 'Player', 'Position', 'Team', 'Bye', 'ADP']
        df = df[final_cols]
        
        return df
    
    def _create_webdriver(self):
        driver = webdriver.Chrome(self.chromedriver_path)
        driver.get(self.url)
        
        elem = driver.find_elements_by_class_name('styles__field__3fmc7')[0]
        elem.clear()
        elem.send_keys(self.username)
        elem.send_keys(Keys.RETURN)
        
        elem = driver.find_elements_by_class_name('styles__field__3fmc7')[1]
        elem.clear()
        elem.send_keys(self.password)
        elem.send_keys(Keys.RETURN)
        
        return driver  


if __name__ == '__main__':
    
    import underdog_login_credentials
    
    url = "https://underdogfantasy.com/rankings/NFL/87a5caba-d5d7-46d9-a798-018d7c116213"    
    chromedriver_path = r"C:\Users\conde\chromedriver\chromedriver.exe"
    username = underdog_login_credentials.USERNAME
    password = underdog_login_credentials.PASSWORD

    adp_scraper = ScrapeAdp(url, chromedriver_path, username, password)
    df_adp = adp_scraper.scrape_adp()
    
    print(df_adp)
