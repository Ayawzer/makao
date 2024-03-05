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

@app.route('/instruction')
def instruction():
    return render_template('instruction.html')

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
    session.pop('game_state', None)  # wyczyść stan gry z sesji
    game = Game()  # Stworzenie nowej gry znowu
    game.start()  # Rozpoczęcie nowej gry
    session['game_state'] = game.get_state()  # Zapisanie stanu gry w sesji
    return jsonify(session['game_state'])  # Zwróć stan gry jako JSON

@app.route('/play', methods=['POST'])
def play():
    card_data = request.json.get('card')
    card = Card(card_data['rank'], card_data['suit'])
    demanded_rank = request.get_json().get('demandedRank')
    demanded_suit = request.get_json().get('demandedSuit')
    print(demanded_rank)
    print(demanded_suit)
    return game.play_card(card, demanded_rank, demanded_suit), game.get_state()

@app.route('/draw', methods=['GET'])
def draw():
    return game.draw_card(), game.get_state()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=12125, debug=True)