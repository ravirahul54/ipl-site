from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__, template_folder='templates')

# File to store betting data
schedule_file = "ipl_schedule.xlsx"
betting_file = "bets.xlsx"

# Initialize Excel file if not exists
if not os.path.exists(betting_file):
    df = pd.DataFrame(columns=["Username", "Match", "Team", "Amount", "Result", "Profit/Loss"])
    df.to_excel(betting_file, index=False)
    

@app.route('/place_bet', methods=['POST'])
def place_bet():
    """ Store user bets in an Excel file """
    username = request.form['username']
    match = request.form['match']
    team = request.form['team']
    amount = int(request.form['amount'])

    # Read existing bets or create a new DataFrame
    if os.path.exists(betting_file):
        df = pd.read_excel(betting_file)
    else:
        df = pd.DataFrame(columns=["Username", "Match", "Team", "Amount", "Result", "Profit/Loss"])

    # Append the new bet
    new_bet = pd.DataFrame([[username, match, team, amount, None, None]], columns=df.columns)
    df = pd.concat([df, new_bet], ignore_index=True)
    df.to_excel(betting_file, index=False)
    
    return "Bet Placed Successfully!", 200

    # Save the updated data
    df.to_excel(betting_file, index=False)

    return redirect('/')

def load_schedule():
    """Load IPL schedule from Excel and mark today's matches."""
    if os.path.exists(schedule_file):
        df = pd.read_excel(schedule_file)

        # 🔹 Print column names to debug
        print("Excel Columns:", df.columns.tolist())

        # 🔹 Ensure correct column names
        if "Date" not in df.columns or "Day" not in df.columns or "Match" not in df.columns:
            print("ERROR: Missing required columns in schedule.xlsx")
            return [], ""

        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")  # Convert Date format
        today = datetime.today().strftime("%Y-%m-%d")  # Get today's date
        df["Status"] = df["Date"].apply(lambda x: "ongoing" if x == today else "past")

        # 🔹 Print loaded data to debug
        print("Loaded Schedule:", df.head().to_dict(orient="records"))

        schedule = df.to_dict(orient="records")
    else:
        print("ERROR: schedule.xlsx not found")
        schedule = []
        today = ""

    return schedule, today


@app.route('/')
def index():
    schedule, today = load_schedule()
    return render_template("index.html", ipl_schedule=schedule, today=today)

@app.route('/admin', methods=['GET'])
def admin_panel():
    """ Render admin panel to update match results """
    df = pd.read_excel(betting_file)
    return render_template("admin.html", bets=df.to_dict(orient="records"))


@app.route('/update_result', methods=['POST'])
def update_result():
    """ Update match results and calculate winnings """
    match = request.form['match']
    winning_team = request.form['winning_team']

    df = pd.read_excel(betting_file)

    for i, row in df.iterrows():
        if row["Match"] == match:
            if row["Team"] == winning_team:
                df.at[i, "Profit/Loss"] = row["Amount"] * 2  # Win: Double the bet
            else:
                df.at[i, "Profit/Loss"] = -row["Amount"]  # Lose: Lose the bet
            df.at[i, "Result"] = "Win" if row["Team"] == winning_team else "Lose"

    df.to_excel(betting_file, index=False)

    return redirect(url_for('admin_panel'))


@app.route('/leaderboard')
def leaderboard():
    # Load betting data
    if os.path.exists(betting_file):
        df = pd.read_excel(betting_file)
        
        # Convert "Profit/Loss" to numeric (handle NaN values)
        df["Profit/Loss"] = pd.to_numeric(df["Profit/Loss"], errors="coerce").fillna(0)

        # Group by username and calculate total profit/loss
        leaderboard_data = df.groupby("Username", as_index=False)["Profit/Loss"].sum()

        # Sort by profit in descending order (highest profit at the top)
        leaderboard_data = leaderboard_data.sort_values(by="Profit/Loss", ascending=False)
        
        # Convert to dictionary for template rendering
        leaderboard_data = leaderboard_data.to_dict(orient="records")
    else:
        leaderboard_data = []

    return render_template("leaderboard.html", leaderboard=leaderboard_data, enumerate=enumerate)




if __name__ == '__main__':
    app.run(debug=True)