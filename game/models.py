import random

SUITS = ['Kier', 'Karo', 'Pik', 'Trefl']
RANKS = ['Ass', '2', '3', '4', '5', '6', '7', '8', '9', '10', 
          'Walet', 'Królowa', 'Król']

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"{self.rank} {self.suit}"
    
    def to_dict(self):
        return {'rank': self.rank, 'suit': self.suit}
    
    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit

class Game:
    def __init__(self):
        self.player_hand = []
        self.computer_hand = []
        self.deck = self.create_deck()
        self.discard_pile = []

    def set_state(self, state_dict):
        #Zapamiętaj stan gry
        self.player_hand = [Card(**card) for card in state_dict['player_hand']]
        self.computer_hand = [Card(**card) for card in state_dict['computer_hand']]
        self.deck = self.create_deck()
        self.discard_pile = [Card(**state_dict['top_discard'])] if state_dict['top_discard'] else []

    def create_deck(self):
        # Stworzenie standardowej talli 52 kart
        return [Card(rank, suit) for suit in SUITS for rank in RANKS]

    def start(self):
         # Potasuj i rozdaj karty
        random.shuffle(self.deck)
        self.deal_cards(5)  # Rozdaj 5 kart graczowi
        self.discard_pile.append(self.deck.pop())  # Stwórz stos odrzuconych kart
        
    def deal_cards(self, number):
        for _ in range(number):
            self.player_hand.append(self.deck.pop())
            self.computer_hand.append(self.deck.pop())

    def computer_turn(self):
        # Wykonaj ruch komputera
        top_card = self.discard_pile[-1]
        for card in self.computer_hand:
            if card.rank == top_card.rank or card.suit == top_card.suit:
                self.computer_hand.remove(card)
                self.discard_pile.append(card)
                if len(self.computer_hand) == 0:
                    return {'success': True, 
                            'message': 'Komputer wygrał!', 
                            **self.get_state()
                        }
                return {'success': True, 
                        'message': 'Komputer zagrał ' + str(card), 
                        **self.get_state()
                    }
        # Jeśli nie ma ruchu, dobierz kartę
        self.computer_hand.append(self.deck.pop())
        return {'success': True, 'message': 'Komputer zaciągnął', **self.get_state()}

    def play_card(self, card):
        random.shuffle(self.deck)
        # Check if the card is in the player's hand
        if card not in self.player_hand: return {'success': False, 'message': 'Nie posadasz tej karty', **self.get_state()}
        # Check if the card can be played
        top_card = self.discard_pile[-1]
        if card.rank != top_card.rank and card.suit != top_card.suit:
            return {'success': False, 'message': 'Karta nie może być zagrana', **self.get_state()}
        # Play the card
        self.player_hand.remove(card)
        self.discard_pile.append(card)
        if len(self.player_hand) == 0:
            return {'success': True, 'message': 'Wygrałeś!', **self.get_state()}
        return {
            'success': True, 
            'message': 'Zagrałeś ' + str(card), 
            'computer_turn': self.computer_turn(),
            **self.get_state()
        }
    
    def draw_card(self):
        random.shuffle(self.deck)
        # Dobierz kartę
        if (len(self.deck) == 0):
            if (len(self.discard_pile) == 1):
                return {'success': False, 'message': 'Nie ma kart do dobierania, zagraj cos na boga', **self.get_state()}
            # Jeśli talia jest pusta, przenieś odrzucone karty do talii
            self.deck = self.discard_pile[:-1]
            self.discard_pile = [self.discard_pile[-1]]
            print('Talia jest pusta, przenoszę odrzucone karty')
        
        self.player_hand.append(self.deck.pop())
        return {
            'success': True, 
            'message': 'Zaciągnąłeś ' + str(self.player_hand[-1]), 
            'computer_turn': self.computer_turn(),
            **self.get_state()
        }
        
    def get_state(self):
        return {
            'player_hand': [card.to_dict() for card in self.player_hand],
            'computer_hand': [card.to_dict() for card in self.computer_hand],
            'top_discard': self.discard_pile[-1].to_dict() if self.discard_pile else None,
        }
