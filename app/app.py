from flask import Flask, render_template, request
app = Flask(__name__)
import main

@app.route('/')
def hello_world():
    return 'Hello, Docker!'

@app.route('/matches', methods=['GET'])
def get_matches1():
    print("GET matches")
    return render_template('index.html', matches=[])

@app.route('/matches', methods=['POST'])
def get_matches2():
    print("POST matches")
    season = []
    league = []
    season.append(request.form.get('season'))
    league.append(request.form.get('league'))
    team = request.form.get('team')
    if team == "":
        team = None
    print("team: " + str(team))
    #seasons.append("now")
    #leagues.append("england/premier-league")

    matches = main.load_matches(season, league, team)
    print("matches lenght: " + str(len(matches)))
    if len(matches) == 1:
        matches = matches[0]
    
    print("matches lenght: " + str(len(matches)))
    print(matches)
    return render_template('index.html', matches=matches)