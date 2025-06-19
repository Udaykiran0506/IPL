import pandas as pd

def get_all_teams(match_info_df):
    teams = pd.concat([match_info_df['team1'], match_info_df['team2']]).unique()
    return sorted(teams.tolist()) + ['All Teams']

def get_team_analytics(team, match_data_df, match_info_df):
    try:
        # Filter match_data directly
        if team != 'All Teams':
            team_data = match_data_df[
                (match_data_df['batting_team'] == team) | (match_data_df['bowling_team'] == team)
            ]
        else:
            team_data = match_data_df

        if team_data.empty:
            raise ValueError(f"No data found for team: {team}")

        total_runs = team_data['runs_off_bat'].sum()
        total_balls = team_data.shape[0]
        run_rate = round(total_runs / (total_balls / 6), 2) if total_balls > 0 else 0

        return {
            "Total Matches": int(team_data['match_id'].nunique()),
            "Total Runs": int(total_runs),
            "Total Wickets": int(team_data['wicket_type'].notnull().sum()),
            "Total Fours": int((team_data['runs_off_bat'] == 4).sum()),
            "Total Sixes": int((team_data['runs_off_bat'] == 6).sum()),
            "Average Run Rate": run_rate
        }

    except Exception as e:
        print(f"❌ Error in get_team_analytics for team {team}: {e}")
        raise
