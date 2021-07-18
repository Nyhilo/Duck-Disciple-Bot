from random import randint
from config import CARD_RANKS, CARD_SUITS


class Card:
    def __init__(self, rank_num, suit_num, rank, suit):
        self.rank_num = rank_num
        self.suit_num = suit_num
        self.rank = rank
        self.suit = suit

    def display_strs(self):
        return (
            f"[{self.rank_num:>2}][{self.suit_num}]",
            f"[{self.rank}{self.suit}]"
        )


def draw_random_card_sets(number=1, size=1):
    cardstrings = []
    for _ in range(number):
        numbers = []
        displays = []
        for _ in range(size):
            card = get_unweighted_card()
            n, d = card.display_strs()

            numbers.append(n)
            displays.append(d)

        numstr = " ".join(numbers)
        dispstr = "".join(displays)

        cardstrings.append(f"{numstr}    {dispstr}")

    number_phrase = 'is your card' if number == 1 and size == 1 else 'are your cards'

    cardstring = '\n'.join(cardstrings)

    return(f'Rolling some dice and... here {number_phrase}\n'
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
