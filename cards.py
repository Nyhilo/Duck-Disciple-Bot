from random import randint
from config import CARD_RANKS, CARD_SUITS


class Card:
    def __init__(self, rank_num, suit_num, rank, suit):
        self.rank_num = rank_num
        self.suit_num = suit_num
        self.rank = rank
        self.suit = suit


def draw_random_card_pair_strings(n=1):
    cardstrings = []
    for i in range(n):
        card1 = get_unweighted_card()
        card2 = get_unweighted_card()
        cardstrings.append(_get_card_pair_string(card1, card2))

    cardstring = '\n'.join(cardstrings)

    return ('Rolling some dice and... here are your cards!\n'
            '```\n'
            f'{cardstring}\n'
            '```')


def draw_random_card_strings(n=1):
    cardstrings = []
    for _ in range(n):
        card = get_unweighted_card()
        cardstrings.append(_get_card_string(card))

    numberphrase = 'is your card' if n == 1 else 'are your cards'
    cardstring = '\n'.join(cardstrings)

    return (f'Rolling some dice and... here {numberphrase}!\n'
            '```\n'
            f'{cardstring}\n'
            '```')


def get_unweighted_card():
    rank_count = len(CARD_RANKS)
    suit_count = len(CARD_SUITS)

    rank_num = _roll(rank_count)
    suit_num = _roll(suit_count)

    rank = CARD_RANKS[rank_num-1]
    suit = CARD_SUITS[suit_num-1]

    return Card(rank_num, suit_num, rank, suit)


def _roll(d):
    return randint(1, d)


def _get_card_string(card):
    maxrollcharcount = 2 + 2 + 1
    rollcharcount = len(str(card.rank_num)) + len(str(card.suit_num))
    spaces = maxrollcharcount - rollcharcount

    rollstring = f'[{card.rank_num}][{card.suit_num}]' + ' '*spaces
    cardstring = f'[{card.rank} {card.suit}]'

    return rollstring + cardstring


def _get_card_pair_string(card1, card2):
    maxrollcharcount = 2 + 2 + 2 + 2 + 1
    rolls = [card1.rank_num, card1.suit_num, card2.rank_num, card2.suit_num]
    rollcharcount = sum([len(str(c)) for c in rolls])
    spaces = maxrollcharcount - rollcharcount

    # Makes a string like '[1][13][5][10]   '
    rollstring = ''.join([f'[{r}]' for r in rolls]) + ' '*spaces

    cardstring = f'[{card1.rank} {card1.suit}][{card2.rank} {card2.suit}]'

    return rollstring + cardstring
