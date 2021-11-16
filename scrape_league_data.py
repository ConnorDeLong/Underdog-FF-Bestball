
import requests
import pandas as pd
from pull_bearer_token import pull_bearer_token


def read_in_site_data(url, headers: dict=None) -> dict:
    ''' Read in the data from the site '''
    
    if headers is None:
        headers = {}
    
    response = requests.get(url, headers=headers)
    
    site_data = response.json()
    
    return site_data


def convert_data_dict_to_df(scraped_data_dict: dict) -> pd.DataFrame:
    ''' Converts the dict from the create_scraped_data_dict function to a df '''
    
    columns = scraped_data_dict['columns']
    
    data_keys = list(scraped_data_dict.keys())[1:]
    
    data_for_df = []
    for data_key in data_keys:
        data = scraped_data_dict[data_key]
        
        data_for_df.append(data)
        
    final_df = pd.DataFrame(data=data_for_df, columns=columns)
        
    return final_df


def create_scraped_data_df(scraped_data: list) -> pd.DataFrame:
    ''' 
    Returns a df of all the data elements for each object in a list of dictionaries.
    Final dictionary will have a 'columns' key containing the column names and every other 
    key will be a number >=0
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
        
    final_data_df = convert_data_dict_to_df(final_data_dict)
        
    return final_data_df


class ReferenceData():
    ''' Compiles all major reference data into dataframes '''
    
    def __init__(self):
        
        url_players = 'https://stats.underdogfantasy.com/v1/slates/87a5caba-d5d7-46d9-a798-018d7c116213/players'
        url_appearances = 'https://stats.underdogfantasy.com/v1/slates/87a5caba-d5d7-46d9-a798-018d7c116213/scoring_types/ccf300b0-9197-5951-bd96-cba84ad71e86/appearances'
        url_teams = 'https://stats.underdogfantasy.com/v1/teams'
        
        player_scores_wk_1_id = 78
        base_url_player_scores = 'https://stats.underdogfantasy.com/v1/weeks/'
        end_url_player_scores = '/scoring_types/ccf300b0-9197-5951-bd96-cba84ad71e86/appearances'
        urls_player_scores = {'player_scores_wk_' + str(i + 1): base_url_player_scores + str(wk_id) + end_url_player_scores 
                              for i, wk_id in enumerate(range(player_scores_wk_1_id,  player_scores_wk_1_id + 17))}

        players_json = read_in_site_data(url_players)
        appearances_json = read_in_site_data(url_appearances)
        teams_json = read_in_site_data(url_teams)
        player_scores_json_dict = {'player_scores_wk_' + str(i + 1): 
                                    read_in_site_data(urls_player_scores['player_scores_wk_' + str(i + 1)])
                                    for i, wk_id in enumerate(range(player_scores_wk_1_id, player_scores_wk_1_id + 17))}
        
        self.players_df = self._create_players_df(players_json['players'])
        self.appearances_df = self._create_appearances_df(appearances_json['appearances'])
        self.teams_df = self._create_teams_df(teams_json['teams'])

        player_scores_df_list = []
        for wk_id in range(1, 18):
            if len(player_scores_json_dict['player_scores_wk_' + str(wk_id)]['appearances']) > 0:
                player_scores_json = player_scores_json_dict['player_scores_wk_' + str(wk_id)]
                player_scores_df = self._create_player_scores_one_wk_df(player_scores_json['appearances'])
                player_scores_df['week_number'] = wk_id

                player_scores_df_list.append(player_scores_df)
            else:
                pass

        self.player_scores_df = pd.concat(player_scores_df_list)
        
    def _create_players_df(self, scraped_data: list) -> pd.DataFrame:
        
        initial_scraped_df = create_scraped_data_df(scraped_data)
        initial_scraped_df.drop(['image_url'], axis=1, inplace=True)
        
        return initial_scraped_df
        
    def _create_appearances_df(self, scraped_data: list) -> pd.DataFrame:
        ''' Creates the df from the appearances section of the API '''
        
        initial_scraped_df = create_scraped_data_df(scraped_data)
        initial_scraped_df.drop(['latest_news_item_updated_at'], axis=1, inplace=True)
        
        # 'projection' column values are dicitionaries which can be converted to a df and merged
        projection_col = initial_scraped_df['projection'].to_list()
        projection_df = create_scraped_data_df(projection_col)
        
        projection_df.drop(['id', 'scoring_type_id'], axis=1, inplace=True)
        projection_df.rename(columns={'points': 'projected_points'}, inplace=True)
        
        final_df = pd.merge(initial_scraped_df, projection_df, left_index=True, right_index=True, how='left')

        final_df.drop(['projection'], axis=1, inplace=True)
        
        return final_df
    
    def _create_teams_df(self, scraped_data: list) -> pd.DataFrame:
        
        initial_scraped_df = create_scraped_data_df(scraped_data)
        
        keep_vars = ['id', 'abbr', 'name', 'sport_id']
        final_df = initial_scraped_df[keep_vars]
        
        return final_df
    
    def _create_player_scores_one_wk_df(self, scraped_data: list) -> pd.DataFrame:
        
        initial_scraped_df = create_scraped_data_df(scraped_data)
        initial_scraped_df.drop(['latest_news_item_updated_at'], axis=1, inplace=True)
        
       # 'projection' column values are dicitionaries which can be converted to a df and merged
        projection_col = initial_scraped_df['projection'].to_list()
        projection_df = create_scraped_data_df(projection_col)
        
        projection_df = projection_df[['points']]
        projection_df.rename(columns={'points': 'projected_points'}, inplace=True)
        
        score_col = initial_scraped_df['score'].to_list()
        score_df = create_scraped_data_df(score_col)
        
        score_df = score_df[['points']]
        score_df.rename(columns={'points': 'actual_points'}, inplace=True)
        
        final_df = pd.merge(initial_scraped_df, projection_df, left_index=True, right_index=True, how='left')
        final_df = pd.merge(final_df, score_df, left_index=True, right_index=True, how='left')

        final_df.drop(['projection', 'score'], axis=1, inplace=True)
        
        return final_df


class IndLeagueData():
    ''' Compiles all major league specific data for an individual league in dataframes'''
    
    def __init__(self, league_id: str, bearer_token: str):
        auth_header = {'authorization': bearer_token}
        
        url_draft = 'https://api.underdogfantasy.com/v2/drafts/' + league_id
        url_weekly_scores = 'https://api.underdogfantasy.com/v1/drafts/' + league_id + '/weekly_scores'

        draft_json = read_in_site_data(url_draft, headers=auth_header)
        weekly_scores_json = read_in_site_data(url_weekly_scores, headers=auth_header)
        
        self.league_id = league_id
        
        self.draft_df = self._create_draft_df(draft_json['draft']['picks'])
        self.weekly_scores_df = self._create_weekly_scores_df(weekly_scores_json['draft_weekly_scores'])
        
    def _create_draft_df(self, scraped_data: list) -> pd.DataFrame:
        
        initial_scraped_df = create_scraped_data_df(scraped_data)
        initial_scraped_df.drop(['projection_average'], axis=1, inplace=True)
        
        initial_scraped_df['draft_id'] = self.league_id
        
        return initial_scraped_df
    
    def _create_weekly_scores_df(self, scraped_data: list) -> pd.DataFrame:
        
        initial_scraped_df = create_scraped_data_df(scraped_data)

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


class UserData():
    
    def __init__(self, bearer_token):
        self.auth_header = {'authorization': bearer_token}
        
        url_leagues_base = 'https://api.underdogfantasy.com/v2/user/slates/87a5caba-d5d7-46d9-a798-018d7c116213/live_drafts'
        url_tourney_base = 'https://api.underdogfantasy.com/v1/user/tournament_rounds/83eb0d3c-9699-443b-be6c-f4123bed59e6/drafts'

        leagues_json_dict = self._create_leagues_json_dict(url_leagues_base)
        tourneys_json_dict = self._create_leagues_json_dict(url_tourney_base)
        
        leagues_df = self._create_leagues_df(leagues_json_dict)
        tourneys_df = self._create_leagues_df(tourneys_json_dict)
        
        self.all_leagues_df = pd.concat([leagues_df, tourneys_df])
        self.all_leagues_df.reset_index(inplace=True)
        
    def _create_leagues_df(self, scraped_data: dict) -> pd.DataFrame:
        
        leagues_df_list = []
        for leagues_page in scraped_data.values():
            leagues_page_df = create_scraped_data_df(leagues_page['drafts'])
            leagues_df_list.append(leagues_page_df)
            
        leagues_df = pd.concat(leagues_df_list)
        
        return leagues_df
    
    def _create_leagues_json_dict(self, url_base: str) -> dict:
        ''' Loops through all the different pages that contain the league level data '''
        
        url_exists = True
        i = 1
        leagues_json_dict = {}
        while url_exists:
            if i == 1:
                url = url_base
            else:
                url = url_base + '?page=' + str(i)
                
            leagues = read_in_site_data(url, headers=self.auth_header)
                
            if len(leagues['drafts']) > 0:
                leagues_json_dict['page_' + str(i)] = leagues
            else:
                url_exists = False
                
            i += 1
            
        return leagues_json_dict


if __name__ == '__main__':
        
    ##############################################################
    ####################### Get all DFs ##########################
    ##############################################################
    
    try:
        import underdog_login_credentials
    except:
        pass
    
    pd.set_option('display.max_rows', 50)
    pd.set_option('display.max_columns', 50)
    
    ### Variables to change ###
    chromedriver_path = r"C:\Users\conde\chromedriver\chromedriver.exe"
    username = underdog_login_credentials.USERNAME
    password = underdog_login_credentials.PASSWORD
    league_id = '26db8d07-a2e0-470a-8f41-bc2c1958b034'
    
    ### Keep as is ###
    url = "https://underdogfantasy.com/lobby"    
    bearer_token = pull_bearer_token(url, chromedriver_path, username, password)
    
    ### Create instances of the different data objects ###
    ref_data = ReferenceData()
    league_data = IndLeagueData(league_id, bearer_token)
    user_data = UserData(bearer_token)   
