from random import randint
import re
from functools import reduce

from config import (CARD_RANKS, TAROT_RANKS, CARD_SUITS, ARCANA_SUITS, 
                    CARD_RANKS_FORMATS, CARD_SUITS_FORMATS,
                    SCORE_SENATORIAL, SCORE_REGIONALS, SCORE_COLORS)


class Card:
    def __init__(self, rank_num, suit_num, rank, suit, raw_string=None):
        self.rank_num = rank_num
        self.suit_num = suit_num
        self.rank = rank
        self.suit = suit
        self.raw_string = raw_string

    def display_strs(self):
        print(self.suit_num, ARCANA_SUITS, self.suit_num in ARCANA_SUITS)
        if self.suit_num in ARCANA_SUITS:
            return (
                f"[{self.rank_num:>2}][{self.suit_num:>2}]",
                f"[{self.rank}]"
            )
        else:
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
    suit_count = len(CARD_SUITS)
    rank_count = len(CARD_RANKS)
    tarot_count = len(TAROT_RANKS)

    suit_num = _roll(suit_count)
    rank_num = _roll(tarot_count) if suit_num in ARCANA_SUITS else _roll(rank_count)

    print(rank_num, suit_num)

    rank = TAROT_RANKS[rank_num] if suit_num in ARCANA_SUITS else CARD_RANKS[rank_num-1]
    suit = CARD_SUITS[suit_num-1]

    return Card(rank_num, suit_num, rank, suit)


def _roll(d):
    return randint(1, d)


########################
# Hand Scoring/Parsing #
########################

def get_hand_score(handstring):
    cards = parse_hand_string(handstring.strip())
    score, formula = calculate_hand_score(cards)
    return f'{formula} = {score}'


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
        if ',' in handstring:
            cardstrings = handstring.split(', ')
        else:   # elif '\n' in handstring:
            cardstrings = handstring.split('\n')

        if len(re.findall(' of ', cardstrings[0], re.IGNORECASE)) > 1:
            raise ValueError("Either your cards aren't separated by commas or newlines or this isn't a proper hand.")

        cards = [_get_long_format_card(s) for s in cardstrings]

    else:
        # Something oops'd here
        raise ValueError('This appears to be an invalid hand.')

    # Figure out the suit and rank value for each card
    for card in cards:
        rank_num = _get_best_index_match(card.rank, CARD_RANKS_FORMATS)
        if rank_num < 0:
            raise ValueError(f'Was unable to find the rank, "{card.rank}" in "{card.raw_string}"')

        suit_num = _get_best_index_match(card.suit, CARD_SUITS_FORMATS)
        if suit_num < 0:
            raise ValueError(f'Was unable to find the suit, "{card.suit}" in "{card.raw_string}"')

        card.rank_num = rank_num+1
        card.suit_num = suit_num+1

    return cards


def calculate_hand_score(cards):
    # Size of hand
    c = len(cards)

    # Number of Ranks constant
    r = len(CARD_RANKS) + len(TAROT_RANKS)

    # Multipliers
    m_pairs = calculate_multipliers_list(cards)
    mults = [pair[0] for pair in m_pairs]
    m_strs = [pair[1] for pair in m_pairs if pair[1] is not None]

    # High-card constant
    h = calculate_high_card_value(cards)

    m = reduce(lambda x, y: x * y, mults, 1)

    # Return crm+h and string representation of (c*r*(m)) + h
    mult_string = '' if len(m_strs) == 0 else f'*({"*".join(m_strs)})'
    return ((c * r * m) + h), f'({c}*{r}{mult_string}) + {h}'


def calculate_high_card_value(cards):
    return max([card.rank_num for card in cards])


def calculate_multipliers_list(cards):
    multiplier_funcs = [
        mult_paired,
        mult_running,
        mult_senatorial,
        mult_regional,
        mult_monochrome,
        mult_flushed,
    ]

    return [func(cards) for func in multiplier_funcs]


def mult_paired(cards):
    # Group the card types together
    rank_groups = {}
    for card in cards:
        if card.rank_num in rank_groups:
            rank_groups[card.rank_num].append(card)
        else:
            rank_groups[card.rank_num] = [card]

    # Determine if all the groups are the same length
    group_list = list(rank_groups.values())
    valid = all([len(group) == len(group_list[0]) for group in group_list])

    if not valid:
        return (1, None)

    # We only care if the length of a given group is > 1
    if len(group_list[0]) == 1:
        return (1, None)

    # Paired is an additive multiplier
    x = len(group_list)
    y = len(group_list[0])
    return (x + y), f'({x}+{y})'


def mult_running(cards):
    if len(cards) < 3:
        return (1, None)

    ranks = [card.rank_num for card in cards]

    # Sort the list
    ranks.sort()

    # Ensure everything is... ya know, running
    valid = all(i == 0 or ranks[i] == ranks[i-1] + 1 for i, _ in enumerate(ranks))

    if not valid:
        return (1, None)

    high_card = max(ranks)
    return (high_card, str(high_card))


def mult_senatorial(cards):
    suits = [card.rank_num for card in cards]

    valid = True
    for suit in SCORE_SENATORIAL:
        valid = valid and suit in suits

    if not valid:
        return (1, None)

    return (3, '3')


def mult_regional(cards):
    suits = [card.suit_num for card in cards]

    valid = False
    # For each set of valid groups of suits
    for set in SCORE_REGIONALS:
        _valid = True
        invalid_set = [suit for suit in range(1, len(CARD_SUITS)+1) if suit not in set]

        # Check if the hand contains all the valid suits
        for suit in set:
            # If the hand contains a suit that is not in the set, invalidate the set
            _valid = _valid and suit in suits

        # Check that hand does not contain any other suits
        for suit in invalid_set:
            _valid = _valid and not (suit in suits)

        # If any set is valid, then the hand is valid
        if _valid:
            valid = valid or _valid
            break

    if not valid:
        return (1, None)

    return (2, '2')


def mult_monochrome(cards):
    suits = [card.suit_num for card in cards]

    valid = False
    # For each set of valid groups of suits
    for set in SCORE_COLORS:
        _valid = True
        invalid_set = [suit for suit in range(1, len(CARD_SUITS)+1) if suit not in set]

        # Check if the hand contains all the valid suits
        for suit in set:
            # If the hand contains a suit that is not in the set, invalidate the set
            _valid = _valid and suit in suits

        # Check that hand does not contain any other suits
        for suit in invalid_set:
            _valid = _valid and not (suit in suits)

        # If any set is valid, then the hand is valid
        if _valid:
            valid = valid or _valid
            break

    if not valid:
        return (1, None)

    return (3, '3')


def mult_flushed(cards):
    if len(cards) < 4:
        return (1, None)

    valid = all(card.suit_num == cards[0].suit_num for card in cards)

    if not valid:
        return (1, None)

    return (4, '4')


###########
# Helpers #
###########

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
    r = re.compile(r' OF ', flags=re.I)
    splits = r.split(cardstring)
    rank = splits[0]
    suit = splits[1]

    return Card(None, None, rank, suit, cardstring)


def _get_best_index_match(_value, _list):
    value = _value.upper()
    for set in _list:
        match = [i for i in range(len(set)) if set[i] == value]
        if len(match) != 0:
            return match[0]

    return -1
