from random import randint
import re
from config import CARD_RANKS, CARD_SUITS, CARD_RANKS_FORMATS, CARD_SUITS_FORMATS


class Card:
    def __init__(self, rank_num, suit_num, rank, suit, raw_string=None):
        self.rank_num = rank_num
        self.suit_num = suit_num
        self.rank = rank
        self.suit = suit
        self.raw_string = raw_string

    def display_strs(self):
        return (
            f"[{self.rank_num:>2}][{self.suit_num:>2}]",
            f"[{self.rank}{self.suit:>2}]"
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


def get_hand_score(handstring):
    cards = parse_hand_string(handstring.strip())
    print([card.display_strs() for card in cards])


def parse_hand_string(handstring):
    # First we need to determine what format the hand given to us is in
    # We're going to assume that the format of the first card will be the same for all of them
    # Possible formats includ:
    #   Shorthand, no spaces - i.e. [A♥] [K♠]
    #   Shorthand, with spaces - i.e. [A ♥] [K ♠]
    #   Longform, comma separated - i.e. Ace of Hearts, King of Spades
    #   Wiki format - i.e. {{Card|A|H}} {{Card|K|S}}
    #
    #   Additionally, shorthand formats can either use emojis or letter representations

    # Determine hand format
    cards = []
    # Short format
    if handstring[0] == '[':
        cardstrings = re.findall(r'\[.*?\]', handstring)

        # Short format with internal space
        if cardstrings[0].find(' ') > -1:
            cards = [_get_short_spaced_card(s) for s in cardstrings]

        # Short format with no internal space
        else:
            cards = [_get_short_unspaced_card(s) for s in cardstrings]

    # Wiki format
    elif handstring[:2] == '{{':
        cardstrings = re.findall('{{.*?}}', handstring)
        cards = [_get_wiki_format_card(s) for s in cardstrings]

    # Long format (probably)
    elif handstring[0].isalpha() or handstring[0].isdigit():
        cardstrings = handstring.split(', ')
        if len(re.findall(' of ', cardstrings[0], re.IGNORECASE)) > 1:
            raise ValueError("Either your cards aren't separated by commas your this isn't a proper hand.")

        cards = [_get_long_format_card(s) for s in cardstrings]

    else:
        # Something oops'd here
        raise ValueError('This appears to be an invalid hand.')

    # Figure out the suit and rank value for each card
    for card in cards:
        rank_num = _get_best_index_match(card.rank, CARD_RANKS_FORMATS)
        if rank_num < 0:
            raise ValueError(f'Was unable to find the rank for {card.raw_string}')

        suit_num = _get_best_index_match(card.suit, CARD_SUITS_FORMATS)
        if suit_num < 0:
            raise ValueError(f'Was unable to find the suit for {card.raw_string}')

        card.rank_num = rank_num+1
        card.suit_num = suit_num+1

    return cards


def _get_short_spaced_card(cardstring):
    try:
        rank, suit = cardstring.strip('[').strip(']').split(' ')
    except ValueError:
        raise ValueError(f'Error parsing {cardstring}. Is it in the same format as the rest of the hand?')

    return Card(None, None, rank, suit, cardstring)


def _get_short_unspaced_card(cardstring):
    _cardstring = cardstring.strip('[').strip(']')
    rank = _cardstring[0]
    suit = _cardstring[1:]

    return Card(None, None, rank, suit, cardstring)


def _get_wiki_format_card(cardstring):
    try:
        _, rank, suit = cardstring.strip('{').strip('}').split('|')
    except ValueError:
        raise ValueError(f'Error parsing {cardstring}. Is it in the same format as the rest of the hand?')

    return Card(None, None, rank, suit, cardstring)


def _get_long_format_card(cardstring):
    rank = re.search(r'^\w*\b', cardstring, re.IGNORECASE).group()
    suit = re.search(r' of \w*$', cardstring, re.IGNORECASE).group()

    return Card(None, None, rank, suit, cardstring)


def _get_best_index_match(_value, _list):
    value = _value.upper()
    for set in _list:
        match = [i for i in range(len(set)) if set[i] == value]
        if len(match) != 0:
            return match[0]

    return -1
