
import requests
import pandas as pd
import time
from pull_bearer_token import pull_bearer_token


class BaseData():
    
    def __init__(self, clear_json_attrs: bool=True, slate_id: str=None):
        self._clear_json_attrs = clear_json_attrs
        
        if slate_id is None:
            self.slate_id = '87a5caba-d5d7-46d9-a798-018d7c116213'
        else:
            self.slate_id = slate_id
            
        self._player_scores_wk_1_id = 78
        self._player_scores_wk_last_id = 78 + 17
    
    def build_all_dfs(self, sleep_time: int=0):
        ''' 
        Overwrites every 'df_' attribute with a df that is created by running the
        'create_' method that matches it. This serves as the primary method 
        for building the dfs associated with the class
        '''
        attrs = [attr for attr in dir(self) if attr.startswith('df_')]
        for attr in attrs:
            method_name = 'create_'+ attr
            self.__dict__[attr] = getattr(self, method_name)()
            
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                pass
        
        if self._clear_json_attrs == True:
            self.clear_json_attrs() 
        
    def clear_json_attrs(self):
        ''' 
        Clears all the atttributes that hold the json data pulled from the API. 
        By default, this is executed when the build_all_dfs method is run
        '''
        attrs = [attr for attr in dir(self) if attr.startswith('json_')]
        for attr in attrs:
            self.__dict__[attr] = {}
    
    def read_in_site_data(self, url, headers: dict=None) -> dict:
        ''' Pulls in the raw data from the API and returns it as a dict '''
        if headers is None:
            headers = {}
        
        response = requests.get(url, headers=headers)
        
        site_data = response.json()
        
        return site_data
    
    def create_scraped_data_df(self, scraped_data: list) -> pd.DataFrame:
        ''' 
        Converts a list of dictionaries into a df where the keys of the dicts are 
        used for the columns and the values are placed in the rows.
        NOTE: this assumes the keys in all dicts are the same.
        '''
        # Get the dicionary keys to identify the columns of the list for each output dict key
        output_data_cols = []
        for output_data_col in scraped_data[0].keys():
            output_data_cols.append(output_data_col)
            
        final_data_dict = {'columns': output_data_cols}
        for data_dict_id, data in enumerate(scraped_data):
            all_data_elements = []
            for output_data_col in output_data_cols:
                try:
                    data_element = data[output_data_col]
                except:
                    # Note: This should probably be conditional on the data type, but just using N/A for now
                    data_element = 'N/A'
                    
                all_data_elements.append(data_element)
            
            final_data_dict[data_dict_id] = all_data_elements
            
        final_data_df = self._convert_data_dict_to_df(final_data_dict)
            
        return final_data_df
    
    def _convert_data_dict_to_df(self, scraped_data_dict: dict) -> pd.DataFrame:
        ''' 
        Converts the dict from the create_scraped_data_dict function to a df 
        NOTE: The input dict takes the following form: 
        {'columns': [<column names>], 1: [<column values>], 2: [<column_values>], ...}
        '''
        
        columns = scraped_data_dict['columns']
        
        data_keys = list(scraped_data_dict.keys())[1:]
        
        data_for_df = []
        for data_key in data_keys:
            data = scraped_data_dict[data_key]
            
            data_for_df.append(data)
            
        final_df = pd.DataFrame(data=data_for_df, columns=columns)
            
        return final_df
    
    def _create_week_id_mapping(self) -> pd.DataFrame:
        ''' Creates a map between the APIs Week ID and the actual Week number '''
        wk_numbers = []
        wk_ids = []
        for wk_number, wk_id in enumerate(range(self._player_scores_wk_1_id, self._player_scores_wk_last_id + 1)):
            wk_numbers.append(wk_number + 1)
            wk_ids.append(wk_id)
            
        mapping = {'week_number': wk_numbers, 'week_id': wk_ids}
        df_mapping = pd.DataFrame(data=mapping)
        
        return df_mapping


class ReferenceData(BaseData):
    ''' Compiles all major reference data into dataframes '''
    
    def __init__(self, clear_json_attrs: bool=True):
        super().__init__(clear_json_attrs=clear_json_attrs)
        
        self._player_scores_wk_1_id = 78
        
        self.url_players = 'https://stats.underdogfantasy.com/v1/slates/' + self.slate_id + '/players'
        self.url_appearances = 'https://stats.underdogfantasy.com/v1/slates/' + self.slate_id + '/scoring_types/ccf300b0-9197-5951-bd96-cba84ad71e86/appearances'
        self.url_teams = 'https://stats.underdogfantasy.com/v1/teams'
        
        base_url_player_scores = 'https://stats.underdogfantasy.com/v1/weeks/'
        end_url_player_scores = '/scoring_types/ccf300b0-9197-5951-bd96-cba84ad71e86/appearances'
        self.urls_player_scores = {'player_scores_wk_' + str(i + 1): base_url_player_scores + str(wk_id) + end_url_player_scores 
                              for i, wk_id in enumerate(range(self._player_scores_wk_1_id,  self._player_scores_wk_1_id + 17))}
        
        self.df_players = pd.DataFrame()
        self.df_appearances = pd.DataFrame()
        self.df_teams = pd.DataFrame()
        self.df_players_master = pd.DataFrame()
        self.df_player_scores = pd.DataFrame()
        
    def build_all_dfs(self):
        attrs = [attr for attr in dir(self) if attr.startswith('df_')]
        for attr in attrs:
            if attr == 'df_players_master':
                pass
            else:
                method_name = 'create_'+ attr
                self.__dict__[attr] = getattr(self, method_name)()
        
        # This ensures the dfs it depends on are created
        self.df_players_master = self.create_df_players_master()
        
        if self._clear_json_attrs == True:
            self.clear_json_attrs()  
        
    def create_df_players(self) -> pd.DataFrame:
        self.json_players = self.read_in_site_data(self.url_players)
        
        initial_scraped_df = self.create_scraped_data_df(self.json_players['players'])
        initial_scraped_df.drop(['image_url'], axis=1, inplace=True)
        initial_scraped_df.rename(columns={'id': 'player_id'}, inplace=True)
        
        return initial_scraped_df
        
    def create_df_appearances(self) -> pd.DataFrame:
        self.json_appearances =self. read_in_site_data(self.url_appearances)
        
        initial_scraped_df = self.create_scraped_data_df(self.json_appearances['appearances'])
        initial_scraped_df.drop(['latest_news_item_updated_at', 'score'], axis=1, inplace=True)
        
        # 'projection' column values are dicitionaries which can be converted to a df and merged
        projection_col = initial_scraped_df['projection'].to_list()
        projection_df = self.create_scraped_data_df(projection_col)
        
        projection_df.drop(['id', 'scoring_type_id'], axis=1, inplace=True)
        projection_df.rename(columns={'points': 'season_projected_points'}, inplace=True)
        
        final_df = pd.merge(initial_scraped_df, projection_df, left_index=True, right_index=True, how='left')
        final_df.drop(['projection'], axis=1, inplace=True)
        
        df_pos_map = self._create_position_mapping(final_df)
        final_df = pd.merge(final_df, df_pos_map, on='position_id', how='left')
        
        final_df.rename(columns={'id': 'appearance_id'}, inplace=True)
        
        return final_df
    
    def create_df_teams(self) -> pd.DataFrame:
        self.json_teams = self.read_in_site_data(self.url_teams)
        
        initial_scraped_df = self.create_scraped_data_df(self.json_teams['teams'])
        
        keep_vars = ['id', 'abbr', 'name']
        final_df = initial_scraped_df[keep_vars].copy()
        
        final_df.rename(columns={'name': 'team_name', 'id': 'team_id'}, inplace=True)
        
        return final_df

    def create_df_players_master(self) -> pd.DataFrame:
        ''' Creates a master lookup for player attributes '''
        
        # Team is more accurate in the df_players data and position from df_appearances
        # reflects the posisiton at the time of the draft
        df_appearances = self.df_appearances.drop(['team_id'], axis=1, inplace=False)
        df_players = self.df_players.drop(['position_id'], axis=1, inplace=False)
        
        final_df = pd.merge(df_appearances, df_players, on='player_id', how='left')
        
        final_df = pd.merge(final_df, self.df_teams, on='team_id', how='left')
        
        return final_df
    
    def create_df_player_scores(self):
        self.json_player_scores = {'player_scores_wk_' + str(i + 1): 
                                    self.read_in_site_data(self.urls_player_scores['player_scores_wk_' + str(i + 1)])
                                    for i, wk_id in enumerate(range(self._player_scores_wk_1_id, self._player_scores_wk_1_id + 17))}
            
        player_scores_df_list = []
        for wk_id in range(1, 18):
            if len(self.json_player_scores['player_scores_wk_' + str(wk_id)]['appearances']) > 0:
                player_scores_json = self.json_player_scores['player_scores_wk_' + str(wk_id)]
                player_scores_df = self._create_df_player_scores_one_wk(player_scores_json['appearances'])
                player_scores_df['week_number'] = wk_id

                player_scores_df_list.append(player_scores_df)
            else:
                pass
            
        player_scores_df = pd.concat(player_scores_df_list)
        player_scores_df.reset_index(inplace=True)
        
        return player_scores_df
        
    def _create_df_player_scores_one_wk(self, scraped_data: list) -> pd.DataFrame:
        ''' 
        Each weeks player scores are contained in its own URL - this creates a df
        of those scores for one week
        '''
        initial_scraped_df = self.create_scraped_data_df(scraped_data)
        initial_scraped_df.drop(['latest_news_item_updated_at'], axis=1, inplace=True)
        
       # 'projection' column values are dicitionaries which can be converted to a df and merged
        projection_col = initial_scraped_df['projection'].to_list()
        projection_df = self.create_scraped_data_df(projection_col)
        
        projection_df = projection_df[['points']]
        projection_df.rename(columns={'points': 'projected_points'}, inplace=True)
        
        score_col = initial_scraped_df['score'].to_list()
        score_df = self.create_scraped_data_df(score_col)
        
        score_df = score_df[['points']]
        score_df.rename(columns={'points': 'actual_points'}, inplace=True)
        
        final_df = pd.merge(initial_scraped_df, projection_df, left_index=True, right_index=True, how='left')
        final_df = pd.merge(final_df, score_df, left_index=True, right_index=True, how='left')

        final_df.drop(['projection', 'score'], axis=1, inplace=True)
        
        return final_df
    
    def _create_position_mapping(self, df_appearances: pd.DataFrame) -> pd.DataFrame:
        ''' 
        Creates df that maps position to position_id since this cant be found in the API
        '''
        df_pos_map = df_appearances.copy()
        
        df_pos_map['position'] = df_pos_map['position_rank'].str[0:2]
        df_pos_map = df_pos_map[['position_id', 'position']].loc[df_pos_map['position'].notnull()]
        df_pos_map = df_pos_map.drop_duplicates(subset=['position', 'position_id'], keep='first')
        
        return df_pos_map


class LeagueData(BaseData):
    ''' Compiles all major league specific data for an individual league in dataframes'''
    
    def __init__(self, league_ids: str, bearer_token: str, clear_json_attrs: bool=True):
        super().__init__(clear_json_attrs=clear_json_attrs)
        
        self.league_ids = league_ids
        self.auth_header = {'authorization': bearer_token}
        
        self.url_drafts = {}
        self.url_weekly_scores = {}
        for league_id in league_ids:
            url_draft = 'https://api.underdogfantasy.com/v2/drafts/' + league_id
            url_weekly_scores = 'https://api.underdogfantasy.com/v1/drafts/' + league_id + '/weekly_scores'
            
            self.url_drafts[league_id] = url_draft
            self.url_weekly_scores[league_id] = url_weekly_scores
        
        self.json_drafts = {}
        self.json_weekly_scores = {}
        
        self.df_drafts = pd.DataFrame()
        self.df_weekly_scores = pd.DataFrame()
        
    def create_df_drafts(self) -> pd.DataFrame:
        dfs = []
        for league_id in self.league_ids:
            df = self._create_df_draft_ind_league(league_id)
            dfs.append(df)
            
        final_df = pd.concat(dfs)
        
        return final_df
    
    def create_df_weekly_scores(self) -> pd.DataFrame:
        dfs = []
        for league_id in self.league_ids:
            df = self._create_df_weekly_scores_ind_league(league_id)
            dfs.append(df)
            
        final_df = pd.concat(dfs)
        final_df.reset_index(inplace=True)
        
        week_mapping = self._create_week_id_mapping()
        final_df = pd.merge(final_df, week_mapping, on='week_id')
        
        return final_df
        
    def _create_df_draft_ind_league(self, league_id) -> pd.DataFrame:
        self.json_drafts[league_id] = self.read_in_site_data(self.url_drafts[league_id], headers=self.auth_header)
        scraped_data = self.json_drafts[league_id]['draft']['picks']
        
        initial_scraped_df = self.create_scraped_data_df(scraped_data)
        initial_scraped_df.drop(['projection_average'], axis=1, inplace=True)
        
        initial_scraped_df['draft_id'] = league_id
        
        return initial_scraped_df
    
    def _create_df_weekly_scores_ind_league(self, league_id) -> pd.DataFrame:
        self.json_weekly_scores[league_id] = self.read_in_site_data(self.url_weekly_scores[league_id], 
                                                                    headers=self.auth_header)
        scraped_data = self.json_weekly_scores[league_id]['draft_weekly_scores']
        
        initial_scraped_df = self.create_scraped_data_df(scraped_data)

        weekly_scores = self._pull_out_weekly_scores(initial_scraped_df)
        
        initial_scraped_df.drop(['week', 'draft_entries_points'], axis=1, inplace=True)
        
        final_scraped_df = pd.merge(left=weekly_scores, right=initial_scraped_df,
                                    on='id', how='left')
        final_scraped_df.drop(['id'], axis=1, inplace=True)
        
        return final_scraped_df
    
    def _pull_out_weekly_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        ''' 
        Each row represents one week where each teams score is contained
        within a dicitonary for that week. This pulls those scores out and 
        puts them in a Team/Week level df
        '''
        
        df = df.copy()
        
        all_weekly_scores = []
        for index, row in df.iterrows():
            row_id = row['id']
            week_id = row['week']['id']
            status = row['week']['status']  
            points_dict = row['draft_entries_points']
            
            for user_id, points in points_dict.items():
                weekly_scores = [row_id, week_id, status, user_id, points]
                
                all_weekly_scores.append(weekly_scores)
                
        columns = ['id', 'week_id', 'status', 'user_id', 'total_points']
        df = pd.DataFrame(data=all_weekly_scores, columns=columns)
        
        return df


class UserData(BaseData):
    
    def __init__(self, bearer_token: str, clear_json_attrs: bool=True):
        super().__init__(clear_json_attrs=clear_json_attrs)
        self.auth_header = {'authorization': bearer_token}
        
        # self.url_base_leagues = 'https://api.underdogfantasy.com/v2/user/slates/' + self.slate_id + '/live_drafts'
        self.url_base_leagues = 'https://api.underdogfantasy.com/v2/user/slates/' + self.slate_id + '/settled_drafts'
        self.url_tourney_league_ids = 'https://api.underdogfantasy.com/v1/user/slates/' + self.slate_id + '/tournament_rounds'
        
        self.json_leagues = {}
        
        self.df_all_leagues = pd.DataFrame()
        
    def create_df_all_leagues(self, league_urls: list=None) -> pd.DataFrame:
        if league_urls is None:
            league_urls = self._create_league_urls()
        
        leagues = []
        for i, league_url in enumerate(league_urls):
            df = self._create_df_leagues(league_url, 'league_' + str(i + 1))
            leagues.append(df)
        
        df_all_leagues = pd.concat(leagues)
        df_all_leagues.reset_index(inplace=True)
        df_all_leagues.drop(columns=['index'], inplace=True)
        
        return df_all_leagues
        
    def _create_df_leagues(self, url_base: str, json_leagues_key: str) -> pd.DataFrame:
        self.json_leagues[json_leagues_key] = self._create_json_leagues(url_base)
        scraped_data = self.json_leagues[json_leagues_key]
        
        leagues_df_list = []
        for leagues_page in scraped_data.values():
            leagues_page_df = self.create_scraped_data_df(leagues_page['drafts'])
            leagues_df_list.append(leagues_page_df)
            
        leagues_df = pd.concat(leagues_df_list)
        
        return leagues_df
    
    def _create_json_leagues(self, url_base: str) -> dict:
        ''' 
        Loops through all the different pages that contain the league level data 
        and stores each as an entry in a dict
        '''
        
        url_exists = True
        i = 1
        leagues_json_dict = {}
        while url_exists:
            if i == 1:
                url = url_base
            else:
                url = url_base + '?page=' + str(i)
                
            leagues = self.read_in_site_data(url, headers=self.auth_header)
                
            if len(leagues['drafts']) > 0:
                leagues_json_dict['page_' + str(i)] = leagues
            else:
                url_exists = False
                
            i += 1
            
        return leagues_json_dict
    
    def _create_df_tourney_league_ids(self) -> pd.DataFrame:
        ''' 
        Tournament leagues (i.e. Puppy 1, Puppy 2, etc.) require the ID of the
        tourney in order to find all entries in it - This creates of all tourney 
        IDs that has at least one entry
        '''
        json_tourney_league_ids = self.read_in_site_data(self.url_tourney_league_ids, headers=self.auth_header)
        scraped_data = json_tourney_league_ids['tournament_rounds']
        
        initial_scraped_df = self.create_scraped_data_df(scraped_data)
        
        # Pulling out the 'id' from the 'tournament' dict in case this is whats needed
        tournament_col = initial_scraped_df['tournament'].to_list()
        tournament_df = self.create_scraped_data_df(tournament_col)
        tournament_df.rename(columns={'id': 'tournament_id'}, inplace=True)        
        tournament_df = tournament_df['tournament_id']

        initial_scraped_df.drop(['tournament'], axis=1, inplace=True)
        final_df = initial_scraped_df.join(tournament_df)
        
        return final_df
    
    def _create_league_urls(self, tourney_league_ids: list=None) -> list:
        ''' 
        Creates a list of all the URLs that contain entries
        '''
        if tourney_league_ids is None:
            tourney_league_ids = list(self._create_df_tourney_league_ids()['id'])
            
        base_url = 'https://api.underdogfantasy.com/v1/user/tournament_rounds/'
        tourney_league_urls = []
        for tourney_league_id in tourney_league_ids:
            tourney_league_url = base_url + tourney_league_id + '/drafts'
            tourney_league_urls.append(tourney_league_url)
            
        tourney_league_urls.append(self.url_base_leagues)
            
        return tourney_league_urls
        

def create_underdog_df_dict(bearer_token: str, sleep_time: int=0) -> dict:
    ''' Creates a dictionary of dfs containing the most relevant UD data '''
    
    ref_data = ReferenceData()
    ref_data.build_all_dfs()
    
    user_data = UserData(bearer_token)
    user_data.build_all_dfs()
    league_ids = list(user_data.df_all_leagues['id'])
    
    league_data = LeagueData(league_ids, bearer_token)
    league_data.build_all_dfs(sleep_time=sleep_time)
    
    df_players_master = ref_data.df_players_master
    df_player_scores = ref_data.df_player_scores
    
    player_vars = ['appearance_id', 'player_id', 'position', 'team_name', 'first_name', 'last_name']
    df_drafts = pd.merge(league_data.df_drafts, df_players_master[player_vars],
                         on='appearance_id', how='left')   
    df_weekly_scores = league_data.df_weekly_scores
    
    final_dict = {'df_players_master': df_players_master, 'df_player_scores': df_player_scores,
                  'df_drafts': df_drafts, 'df_weekly_scores': df_weekly_scores, 
                  'df_league_info': user_data.df_all_leagues}
    
    return final_dict


if __name__ == '__main__':
            
    ##############################################################
    ####################### Get all DFs ##########################
    ##############################################################
    
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.max_columns', 50)
    
    try:
        import underdog_login_credentials
    except:
        pass
    
    ### Variables to change ###
    chromedriver_path = r"C:\Users\conde\chromedriver\chromedriver.exe"
    username = underdog_login_credentials.USERNAME
    password = underdog_login_credentials.PASSWORD
    
    ### Keep as is ###
    url = "https://underdogfantasy.com/lobby"    
    bearer_token = pull_bearer_token(url, chromedriver_path, username, password)
    
    ### Pull all major UD data elements ###
    underdog_data = create_underdog_df_dict(bearer_token, sleep_time=5)
    
    # df_drafts = underdog_data['df_drafts']
    # df_weekly_scores = underdog_data['df_weekly_scores']
    
    # print(df_drafts)
    
    # print(len(df_drafts[['draft_id']].drop_duplicates(subset=['draft_id'], keep='first')))
    
    # draft = df_weekly_scores.loc[df_weekly_scores['draft_id'] == 'd03c5d24-e2b7-40a1-9d17-855a9f925fba']
    # print(draft)
    
    # user_data = UserData(bearer_token)
    
    # urls = user_data._create_league_urls()
    # print(urls)
    
    # tourney_league_ids = user_data._create_df_tourney_league_ids()
    # print(tourney_league_ids)
    
    # json_data = user_data._create_json_leagues(urls[0])
    # json_data_tourneys = user_data._create_json_leagues(urls[1])
    # print(json_data_tourneys)
    
    # user_data.build_all_dfs()
    # league_ids = list(user_data.df_all_leagues['id'])
    
    # print(len(league_ids))
    # print(user_data.df_all_leagues)
    
    # keep_vars = ['draft_id', 'entry_style_id', ]
