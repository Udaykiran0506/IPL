from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS
from utils.analytics import get_team_analytics  # Adjusted to your folder structure

# For plots
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})



# Load data
match_info = pd.read_csv("match_info_data.csv")
match_data = pd.read_csv("match_data.csv", low_memory=False)

# Route: Get all teams
@app.route("/teams")
def get_teams():
    teams = pd.unique(match_info[['team1', 'team2']].values.ravel('K'))
    teams = sorted([team for team in teams if isinstance(team, str)])
    teams.insert(0, "All Teams")
    return jsonify(teams)

# Route: Analytics for a team
@app.route("/analytics")
def team_analytics():
    team = request.args.get("team")
    print("⚠️ Team requested:", team)

    try:
        analytics = get_team_analytics(team, match_data, match_info)
        print("✅ Analytics computed:", analytics)

        clean_analytics = {
            k: int(v) if isinstance(v, (pd.Int64Dtype, pd.Series, pd.Index, float, int)) and float(v).is_integer()
            else float(v) if isinstance(v, float)
            else v
            for k, v in analytics.items()
        }

        return jsonify(clean_analytics)

    except Exception as e:
        import traceback
        traceback.print_exc()  # 👈 prints the full error to terminal
        return jsonify({"error": str(e)}), 500


# Route: Visualizations for a team
@app.route("/visuals")
def team_visuals():
    team = request.args.get("team")
    
    if team == "All Teams":
        df = match_data.copy()
    else:
        df = match_data[(match_data["batting_team"] == team) | (match_data["bowling_team"] == team)]

    plots = {}

    def plot_to_base64(fig):
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        plt.close(fig)
        return encoded

    # Plot 1: Histogram of runs
    fig1 = plt.figure(figsize=(8, 5))
    sns.histplot(df['runs_off_bat'], bins=15, kde=True, color='orange')
    plt.title(f'{team} - Distribution of Runs per Ball')
    plt.xlabel('Runs Off Bat')
    plt.ylabel('Frequency')
    plots["runs_histogram"] = plot_to_base64(fig1)

    # Plot 2: Pie chart of total runs by innings (replaces boxplot)
    fig2 = plt.figure(figsize=(7, 7))
    innings_runs = df.groupby('innings')['runs_off_bat'].sum().sort_index()
    plt.pie(
        innings_runs,
        labels=[f"Innings {i}" for i in innings_runs.index],
        autopct='%1.1f%%',
        startangle=140,
        colors=sns.color_palette("Set2", len(innings_runs))
    )
    plt.title(f'{team} - Total Runs by Innings (Pie Chart)')
    plots["runs_piechart"] = plot_to_base64(fig2)

    # Plot 3: Count plot of extras type (if exists)
    if 'extras_type' in df.columns:
        fig3 = plt.figure(figsize=(8, 5))
        sns.countplot(data=df[df['extras_type'] != 'None'], x='extras_type', palette='pastel')
        plt.title(f'{team} - Extras Type Distribution')
        plt.xticks(rotation=45)
        plots["extras_count"] = plot_to_base64(fig3)

    # Plot 4: Violin plot of runs per innings
    fig4 = plt.figure(figsize=(8, 5))
    sns.violinplot(x='innings', y='runs_off_bat', data=df, palette='muted')
    plt.title(f'{team} - Runs Distribution by Inning (Violin)')
    plots["runs_violin"] = plot_to_base64(fig4)

    return jsonify(plots)

# Route: Top players (batsmen and bowlers) for a team
@app.route("/top-players")
def top_players():
    team = request.args.get("team")

    if team == "All Teams":
        df = match_data.copy()

        # Top batsmen overall
        top_batsmen = (
            df.groupby('striker')['runs_off_bat']
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .reset_index()
            .rename(columns={"striker": "name", "runs_off_bat": "runs"})
            .to_dict(orient="records")
        )

        # Top bowlers overall (excluding run outs)
        valid_wickets = df[
            df['wicket_type'].notna() & 
            (df['wicket_type'] != 'run out')
        ]
        top_bowlers = (
            valid_wickets['bowler']
            .value_counts()
            .head(5)
            .reset_index()
            .rename(columns={"index": "name", "bowler": "wickets"})
            .to_dict(orient="records")
        )
    else:
        df = match_data[
            (match_data["batting_team"] == team) | (match_data["bowling_team"] == team)
        ]

        # Top batsmen for the selected team
        top_batsmen = (
            df[df['batting_team'] == team]
            .groupby('striker')['runs_off_bat']
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .reset_index()
            .rename(columns={"striker": "name", "runs_off_bat": "runs"})
            .to_dict(orient="records")
        )

        # Top bowlers for the selected team
        valid_wickets = df[
            (df['bowling_team'] == team) &
            (df['wicket_type'].notna()) &
            (df['wicket_type'] != 'run out')
        ]
        top_bowlers = (
            valid_wickets['bowler']
            .value_counts()
            .head(5)
            .reset_index()
            .rename(columns={"index": "name", "bowler": "wickets"})
            .to_dict(orient="records")
        )

    return jsonify({
        "top_batsmen": top_batsmen,
        "top_bowlers": top_bowlers
    })



@app.route("/filters")
def get_filters():
    seasons = sorted(match_info['season'].dropna().unique().tolist())
    venues = sorted(match_info['venue'].dropna().unique().tolist())
    opponents = sorted(pd.unique(match_info[['team1', 'team2']].values.ravel('K')))

    return jsonify({
        "seasons": seasons,
        "venues": venues,
        "opponents": opponents
    })


if __name__ == "__main__":
    app.run(debug=True)
