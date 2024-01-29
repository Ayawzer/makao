from flask import Flask, render_template, jsonify, request, session
from game.models import Game, Card

app = Flask(__name__)
app.secret_key = 'secret'

game = Game()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gam')
def gam():
    return render_template('game.html')

@app.route('/clear') # Wyczyszczenie sesji - debugging purposes
def clear():
    session.clear()
    return 'OK'

@app.route('/start', methods=['GET'])
def start_game():
    if 'game_state' not in session:
        game.start()
        session['game_state'] = game.get_state()
    else:
        game.set_state(session['game_state'])
    return jsonify(session['game_state'])

@app.route('/new_game', methods=['GET'])
def new_game():
    global game
    session.pop('game_state', None)  # Clear the game state in the session
    game = Game()  # Reassign the global game instance
    game.start()  # Start a new game
    session['game_state'] = game.get_state()  # Save the new game state in the session
    return jsonify(session['game_state'])  # Send the new game state to the frontend

@app.route('/play', methods=['POST'])
def play():
    card_data = request.json.get('card')
    card = Card(card_data['rank'], card_data['suit'])
    return game.play_card(card), game.get_state()

@app.route('/draw', methods=['GET'])
def draw():
    return game.draw_card(), game.get_state()