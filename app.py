from flask import Flask, render_template, jsonify, request, session
from game.models import Game, Card
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'secret'

game = Game()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gam')
def gam():
    return render_template('game.html')

@app.route('/clear')
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

@app.route('/play', methods=['POST'])
def play():
    card_data = request.json.get('card')
    card = Card(card_data['rank'], card_data['suit'])
    return game.play_card(card), game.get_state()

@app.route('/draw', methods=['GET'])
def draw():
    return game.draw_card(), game.get_state()