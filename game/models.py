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
        self.cards_to_draw = 0
        self.computer_skip = 1
        self.player_skip = 1
        self.demanded_rank = None
        self.demanded_turns = 0
        self.demanded_suit = None

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
        
        # Pierwsza karta na stosiee niee może być specjalna
        while True:
            top_card = self.deck.pop()
            if top_card.rank not in ['2', '3', '4', 'Walet', 'Król', 'Ass']:
                self.discard_pile.append(top_card)
                break
            else:
                self.deck.insert(0, top_card)
        random.shuffle(self.deck)
        
    def deal_cards(self, number):
        for _ in range(number):
            self.player_hand.append(self.deck.pop())
            self.computer_hand.append(self.deck.pop())
    
    def computer_turn(self):
        top_card = self.discard_pile[-1]
        playable_cards = [card for card in self.computer_hand if card.rank == top_card.rank or card.suit == top_card.suit]
        special_cards = [card for card in self.computer_hand if card.rank in ['2', '3'] or (card.rank == 'Król') and card.suit in ['Kier', 'Pik']]
        non_special_ranks = ['5', '6', '7', '8', '9', '10', 'Królowa']
        available_ranks = [card.rank for card in self.computer_hand if card.rank in non_special_ranks]

        #Sprawdz czy talia jest pusta
        if (len(self.deck) == 0):
            if (len(self.discard_pile) == 1):
                return {'success': False, 'message': 'Nie ma kart do dobierania, zagraj cos na boga', **self.get_state()}
            
            # Jeśli talia jest pusta, przenieś odrzucone karty do talii
            self.deck = self.discard_pile[:-1]
            self.discard_pile = [self.discard_pile[-1]]
            print('Talia jest pusta, przenoszę odrzucone karty')
        
        if self.demanded_suit:
        # Sprawdz czy komputer ma żądany kolor, jesli tak zagraj, jesli nie ciągnij karte
            demanded_suit_cards = [card for card in self.computer_hand if card.suit == self.demanded_suit]
            if demanded_suit_cards:
            # Jesli kolor pasuje, zagraj karte
                card_to_play = demanded_suit_cards[0]
                self.computer_hand.remove(card_to_play)
                self.discard_pile.append(card_to_play)
                self.demanded_suit = None 
                if card_to_play.rank == '2':
                    self.cards_to_draw += 2
                elif card_to_play.rank == '3':
                    self.cards_to_draw += 3
                elif card_to_play.rank == '4':
                    self.player_skip += 1
                elif card_to_play.rank == 'Król' and card_to_play.suit in ['Kier', 'Pik']:
                    self.cards_to_draw += 5
                elif card_to_play.rank == 'Walet':
                    if available_ranks:
                        demanded_rank = random.choice(available_ranks)
                        self.demanded_rank = demanded_rank
                        self.demanded_turns = 2
                        print(f"Computer demands {demanded_rank} special")
                        message = f'Komputer zagrał {card_to_play} i wybrał {demanded_rank}'
                        return {'success': True, 'message': message, **self.get_state()}
                    else:
                        demanded_rank = random.choice(non_special_ranks)
                        self.demanded_rank = demanded_rank
                        self.demanded_turns = 2
                        print(f"Computer demands {demanded_rank} nospecial")
                        message = f'Komputer zagrał {card_to_play} i wybrał {demanded_rank}'
                        return {'success': True, 'message': message, **self.get_state()}
                elif card_to_play.rank == 'Ass':
                    available_suits = {card.suit for card in self.computer_hand}
                    demanded_suit = random.choice(list(available_suits))
                    self.demanded_suit = demanded_suit
                    message = f'Komputer zagrał {card_to_play} i żąda koloru {demanded_suit}'
                    return {'success': True, 'message': message, **self.get_state()}
                return {'success': True, 'message': f'Komputer zagrał {card_to_play}', **self.get_state()}
            else:
            # Jesli kolor nie pasuje, ciagnij
                message = 'Komputer nie miał ' + self.demanded_suit + ' i zaciągnął kartę.'
                return {'success': True, 'message': message, **self.get_state()}

        #Jesli komp musi skipnac ale ma 4 w rece to zagra ta 4 i przekaze skipniecie dla gracza
        if ([card for card in playable_cards if card.rank == '4']) and self.computer_skip > 1:
            card_to_play = [card for card in playable_cards if card.rank == '4'][0]
            self.computer_hand.remove(card_to_play)
            self.discard_pile.append(card_to_play)
            self.player_skip = self.computer_skip + 1
            self.computer_skip = 1
            return {'success': True, 'message': 'komputer zagrał ' + str(card_to_play) + ' i przekazal skipniecie', **self.get_state()}
        # Sprawdz czy komputer musi skipnac ture
        if self.computer_skip > 1:
            self.computer_skip -= 1
            return {'success': True, 'message': 'kompik czeka jeszcze ' + str(self.computer_skip) + ' tury', **self.get_state()}
        
        # Sprawdz czy komputer ma żądaną karte, jesli tak zagraj ją, jesli nie ciągnij karte
        if self.demanded_turns > 0:
            demanded_cards = [card for card in self.computer_hand if card.rank == self.demanded_rank]
            if demanded_cards:
                card_to_play = demanded_cards[0]
                self.computer_hand.remove(card_to_play)
                self.discard_pile.append(card_to_play)
                # Po ruchu zmniejsz liczbe tur do zagrania zadanej karty, jesli jest 0 to wyzeruj demanded_rank
                self.demanded_turns -= 1
                if self.demanded_turns == 0:
                    self.demanded_rank = None
                message = f'Komputer zagrał {card_to_play}'
                return {'success': True, 'message': message, **self.get_state()}
            else:
                self.computer_hand.append(self.deck.pop())
                req = self.demanded_rank
                # Po zaciagnieciu zmniejsz liczbe tur do zagrania zadanej karty, jesli jest 0 to wyzeruj demanded_rank
                self.demanded_turns -= 1
                if self.demanded_turns == 0:
                    self.demanded_rank = None
                message = f'Komputer nie miał {req} i zaciągnął kartę.'
                return {'success': True, 'message': message, **self.get_state()}

        # Sprawdz czy komp musi wziąc więcej kart
        if self.cards_to_draw > 0 and not any(special_cards):
        # zaciagnij karty
            how_many = self.cards_to_draw
            for _ in range(self.cards_to_draw):
                if (len(self.deck) == 0):
                    # Jeśli talia jest pusta, przenieś odrzucone karty do talii
                    self.deck = self.discard_pile[:-1]
                    self.discard_pile = [self.discard_pile[-1]]
                    print('Talia jest pusta, przenoszę odrzucone karty')
                self.computer_hand.append(self.deck.pop())
                self.cards_to_draw = 0  # reset po zaciągnięciu
                message = 'Komputer zaciągnął ' + str(how_many) + ' karty i przekazał turę.'
        elif self.cards_to_draw > 0 and any(special_cards):
        # zagraj karte specjalna
            card_to_play = special_cards[0]
            self.computer_hand.remove(card_to_play)
            self.discard_pile.append(card_to_play)
            if card_to_play.rank == 'Król':
                self.cards_to_draw += 5
            else:
                self.cards_to_draw += int(card_to_play.rank)
            message = f'oboze Komputer zagrał {card_to_play}'
            print('cooooo', self.cards_to_draw)
        elif playable_cards:
        # Zagraj karte z playable_cards
            card_to_play = playable_cards[0]
            self.computer_hand.remove(card_to_play)
            self.discard_pile.append(card_to_play)
            if card_to_play.rank == '4':
                self.player_skip += 1
            if card_to_play.rank == '2':
                self.cards_to_draw += 2
            elif card_to_play.rank == '3':
                self.cards_to_draw += 3
            elif card_to_play.rank == 'Król' and card_to_play.suit in ['Kier', 'Pik']:
                self.cards_to_draw += 5
            # Jesli zagrany walet wylosuj kartę z dostępnych lub nie, ustaw tury do zagrania zadanej karty na 2
            elif card_to_play.rank == 'Walet':
                if available_ranks:
                    demanded_rank = random.choice(available_ranks)
                    self.demanded_rank = demanded_rank
                    self.demanded_turns = 2
                    print(f"Computer demands {demanded_rank} special")
                    message = f'Komputer zagrał {card_to_play} i wybrał {demanded_rank}'
                    return {'success': True, 'message': message, **self.get_state()}
                else:
                    demanded_rank = random.choice(non_special_ranks)
                    self.demanded_rank = demanded_rank
                    self.demanded_turns = 2
                    print(f"Computer demands {demanded_rank} nospecial")
                    message = f'Komputer zagrał {card_to_play} i wybrał {demanded_rank}'
                    return {'success': True, 'message': message, **self.get_state()}
            elif card_to_play.rank == 'Ass':
                available_suits = {card.suit for card in self.computer_hand}
                demanded_suit = random.choice(list(available_suits))
                self.demanded_suit = demanded_suit
                message = f'Komputer zagrał {card_to_play} i żąda koloru {demanded_suit}'
                return {'success': True, 'message': message, **self.get_state()}
            message = f'Komputer zagrał {card_to_play}'
        else:
            self.computer_hand.append(self.deck.pop())
            message = 'Komputer zaciągnął kartę i przekazał turę.'

        if not self.computer_hand:
            message = 'Komputer wygrał!'

        return {'success': True, 'message': message, **self.get_state()}
        
    def play_card(self, card, demanded_rank=None, demanded_suit=None):
        random.shuffle(self.deck)
        # Sprawdz czy karta jest w rece
        if card not in self.player_hand: return {'success': False, 'message': 'Nie posadasz tej karty', **self.get_state()}

        if self.demanded_suit:
            if card.suit == self.demanded_suit:
                self.player_hand.remove(card)
                self.discard_pile.append(card)
                self.demanded_suit = None
                if len(self.player_hand) == 0:
                    return {'success': True, 'message': 'Wygrałeś!', **self.get_state()}
                if card.rank == '2':
                    self.cards_to_draw += 2
                    print('jaa',self.cards_to_draw)

                if card.rank == '3':
                    self.cards_to_draw += 3
                    print('jaa',self.cards_to_draw)

                if card.rank == 'Król' and card.suit == 'Kier':
                    self.cards_to_draw += 5
                    print('jaa',self.cards_to_draw)
        
                if card.rank == 'Król' and card.suit == 'Pik':
                    self.cards_to_draw += 5
                    print('jaa',self.cards_to_draw)
                # Jesli gracz zagral 4 to dodaj liczbe tru do skipniecia dla komputera
                if card.rank == '4':
                    self.computer_skip += 1
                    return {'success': True, 'message': 'Zagrałeś ' + str(card), 'computer_turn': self.computer_turn(), **self.get_state()}
        # Jesli zagrany walet ustaw demanded_rank na wybrana karte i demanded_turns na 2
                if card.rank == 'Walet':
                    self.demanded_rank = demanded_rank
                    self.demanded_turns = 2
                    return {'success': True, 'message': 'Wybrałeś ' + demanded_rank, 'computer_turn': self.computer_turn(), **self.get_state()}
                if card.rank == 'Ass':
                    self.demanded_suit = demanded_suit
                    return {'success': True, 'message': 'Wybrałeś ' + demanded_suit, 'computer_turn': self.computer_turn(), **self.get_state()}
                return {'success': True, 'message': 'Zagrałeś żądane ' + str(card), 'computer_turn': self.computer_turn(), **self.get_state()}
            else:
                return {'success': False, 'message': 'Musisz zagrać żądany kolor', **self.get_state()}

        # Sprawdz czy gracz musi czekac i czy ma 4 w rece, jesli tak to zagraj 4 i przekaz tury do skipniecia dla komputera
        if card.rank == '4' and self.player_skip > 1:
            self.player_hand.remove(card)
            self.discard_pile.append(card)
            if len(self.player_hand) == 0:
                return {'success': True, 'message': 'Wygrałeś!', **self.get_state()}
            self.computer_skip = self.player_skip + 1
            self.player_skip = 1
            return {'success': True, 'message': 'zagrałeś ' + str(card) + ' i przekazales skipniecie', 'computer_turn': self.computer_turn(), **self.get_state()}

        # Jesli gracz nie ma 4 w rece i musi czekac to nie moze zagrac karty tylko czeka i liczba tur do skipniecia zmniejsza sie
        if self.player_skip > 1:
            print('nieczteryxpp')
            self.player_skip -= 1
            return {'success': True, 'message': 'Czekasz jeszcze ' + str(self.player_skip) + ' tury', 'computer_turn': self.computer_turn(), **self.get_state()}
        
        # Zagraj zadaną karte, zmniejsz liczbe tur do zagrania zadanej karty, jesli jest 0 to wyzeruj demanded_rank
        if self.demanded_turns > 0:
            if card.rank == self.demanded_rank:
                self.player_hand.remove(card)
                self.discard_pile.append(card)
                if len(self.player_hand) == 0:
                    return {'success': True, 'message': 'Wygrałeś!', **self.get_state()}
                self.demanded_turns -= 1
                if self.demanded_turns == 0:
                    self.demanded_rank = None
                return {'success': True, 'message': 'Zagrałeś żądaną ' + str(card), 'computer_turn': self.computer_turn(), **self.get_state()}
            else:
                return {'success': False, 'message': 'Musisz zagrać żądaną kartę', **self.get_state()}

        # Sprawdz czy karta moze byc zagrana
        top_card = self.discard_pile[-1]
        if top_card.rank == '2' or top_card.rank == '3' or (top_card.rank == 'Król' and top_card.suit == 'Kier') or (top_card.rank == 'Król' and top_card.suit == 'Pik'):
            if card.rank == '2' or card.rank == '3' or (card.rank == 'Król' and card.suit == 'Kier') or (card.rank == 'Król' and card.suit == 'Pik'):
                print('hmmm')
                self.player_hand.remove(card)
                self.discard_pile.append(card)
                if len(self.player_hand) == 0:
                    return {'success': True, 'message': 'Wygrałeś!', **self.get_state()}
                if (card.rank == 'Król' and card.suit == 'Kier') or (card.rank == 'Król' and card.suit == 'Pik'):
                    self.cards_to_draw += 5
                else:
                    self.cards_to_draw += int(card.rank)
                print('jaakfkasfa',self.cards_to_draw)
                return {
                    'success': True, 
                    'message': 'debugZagrałeś ' + str(card), 
                    'computer_turn': self.computer_turn(),
                    **self.get_state()
                }
        if card.rank != top_card.rank and card.suit != top_card.suit:
            return {'success': False, 'message': 'Karta nie może być zagrana', **self.get_state()}
        
        # Sprawdz czy karta jest specjalna i czy twoja wybrana moze byc zagrana
        if self.cards_to_draw > 0:
            if not (card.rank in ['2', '3'] or (card.rank == 'Król' and card.suit in ['Kier', 'Pik'])):
                return {'success': False, 'message': 'Musisz zagrać specjalna karte', **self.get_state()}
        
        # Zagraj karte
        self.player_hand.remove(card)
        self.discard_pile.append(card)

        # zagrana 2 przez gracza, wiec dodaj wartosc do cards_to_draw
        if card.rank == '2':
            self.cards_to_draw += 2
            print('jaa',self.cards_to_draw)

        if card.rank == '3':
            self.cards_to_draw += 3
            print('jaa',self.cards_to_draw)

        if card.rank == 'Król' and card.suit == 'Kier':
            self.cards_to_draw += 5
            print('jaa',self.cards_to_draw)
        
        if card.rank == 'Król' and card.suit == 'Pik':
            self.cards_to_draw += 5
            print('jaa',self.cards_to_draw)
        # Jesli gracz zagral 4 to dodaj liczbe tru do skipniecia dla komputera
        if card.rank == '4':
            self.computer_skip += 1
            return {'success': True, 'message': 'Zagrałeś ' + str(card), 'computer_turn': self.computer_turn(), **self.get_state()}
        # Jesli zagrany walet ustaw demanded_rank na wybrana karte i demanded_turns na 2
        if card.rank == 'Walet':
            self.demanded_rank = demanded_rank
            self.demanded_turns = 2
            return {'success': True, 'message': 'Wybrałeś ' + demanded_rank, 'computer_turn': self.computer_turn(), **self.get_state()}

        # Jesli Ass ustaw demanded_suit na wybrany kolor
        if card.rank == 'Ass':
            self.demanded_suit = demanded_suit
            return {'success': True, 'message': 'Wybrałeś ' + demanded_suit, 'computer_turn': self.computer_turn(), **self.get_state()}

        # Sprawdz czy gracz wygral
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
        # Pusta talia
        if (len(self.deck) == 0):
            if (len(self.discard_pile) == 1):
                return {'success': False, 'message': 'Nie ma kart do dobierania, zagraj cos na boga', **self.get_state()}
            
            # Jeśli talia jest pusta, przenieś odrzucone karty do talii
            self.deck = self.discard_pile[:-1]
            self.discard_pile = [self.discard_pile[-1]]
            print('Talia jest pusta, przenoszę odrzucone karty')
        # Jesli gracz musi czekac nie dobieraj karty i wyswietl ile jeszcze czeka
        if self.player_skip > 1:
            self.player_skip -= 1
            return {'success': True, 'message': 'Czekasz jeszcze ' + str(self.player_skip) + ' tury', 'computer_turn': self.computer_turn(), **self.get_state()}
        
        # Jesli gracz nie ma zadanej karty to dobiera karte i zmniejsza liczbe tur do zagrania zadanej karty jesli jest 0 to wyzeruje demanded_rank
        if self.demanded_turns > 0:
            self.player_hand.append(self.deck.pop())
            self.demanded_turns -= 1
            if self.demanded_turns == 0:
                self.demanded_rank = None
            return {
            'success': True, 
            'message': 'Zaciągnąłeś ' + str(self.player_hand[-1]), 
            'computer_turn': self.computer_turn(),
            **self.get_state()
        }

        if self.demanded_suit:
            self.player_hand.append(self.deck.pop())
            self.demanded_suit = None
            return {
            'success': True,
            'message': 'Zaciągnąłeś ' + str(self.player_hand[-1]),
            'computer_turn': self.computer_turn(),
            **self.get_state()
        }

        # Sprawdz czy gracz musi dobrac wiecej kart i dobierz je
        if self.cards_to_draw > 0:
            for _ in range(self.cards_to_draw):
                if (len(self.deck) == 0):
                    # Jeśli talia jest pusta, przenieś odrzucone karty do talii
                    self.deck = self.discard_pile[:-1]
                    self.discard_pile = [self.discard_pile[-1]]
                    print('Talia jest pusta, przenoszę odrzucone karty')
                self.player_hand.append(self.deck.pop())
            how_many = self.cards_to_draw
            self.cards_to_draw = 0
            return {'success': True, 
                    'message': 'Zaciągnąłeś ' + str(how_many) + ' karty',
                    'computer_turn': self.computer_turn(),
                    **self.get_state()
            }
        else:
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