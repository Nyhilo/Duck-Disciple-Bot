import os
from dotenv import load_dotenv
load_dotenv()

PREFIX = '&'

LOG_FILE = 'bot.log'
GENERIC_ERROR = ('Whoops! An error occured while executing this command. You '
                 'should probably tell the bot author about it or something'
                 '...')

# This is set to false to prevent cheating when secretly generating a Sha265
LOG_DEBUG_TO_FILE = os.getenv('DEBUG') == "TRUE"

# Phases
_phase_bartering = 'Bartering Phase'
_phase_auction = 'Auction Phase'

PHASES_BY_DAY = {
    'Monday': _phase_auction,
    'Tuesday': _phase_auction,
    'Wednesday': _phase_auction,
    'Thursday': _phase_bartering,
    'Friday': _phase_bartering,
    'Saturday': _phase_bartering,
    'Sunday': _phase_bartering
}

PHASE_CYCLE = {
    _phase_bartering: _phase_auction,
    _phase_auction: _phase_bartering
}

PHASE_START = {
    _phase_bartering: 'Thursday',
    _phase_auction: 'Monday'
}

# Cards
CARD_RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'X', 'E', 'D', 'H', 'U', 'O', 'N', 'B', 'R', 'Q', 'K']
CARD_SUITS = ['l', '♦', 'u', '♣', 'a', 'r', 'b', 'd', 's', '♥', 'c', '♠']

# Cards for determining suit/rank value for alternate formats
# Strings should be normalized uppercase before comparing to these
CARD_RANKS_FORMATS = [
    # Default card ranks
    CARD_RANKS,

    # Wiki {{Card}} format
    ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', 'U', 'O', 'N', 'B', 'R', 'Q', 'K'],

    # 10 is also sometimes T
    ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', '11', '12', '13', 'U', 'O', 'N', 'B', 'R', 'Q', 'K'],

    # Long format
    ['ACE',
     'TWO',
     'THREE',
     'FOUR',
     'FIVE',
     'SIX',
     'SEVEN',
     'EIGHT',
     'NINE',
     'TEN',
     'ELEVEN',
     'TWELVE',
     'THIRTEEN',
     'UNTER KNAVE',
     'OBER KNAVE',
     'KNIGHT',
     'BISHOP',
     'ROOK',
     'QUEEN',
     'KING']
]

CARD_SUITS_FORMATS = [
    # Default card suits, normalized uppercase
    [suit.upper() for suit in CARD_SUITS],

    # Wiki format
    ['L', 'D', 'Cp', 'C', 'A', 'R', 'B', 'Sw', 'Sh', 'H', 'Cn', 'S'],

    # Emojis if you like
    ['🍃', '♦', '🥤', '♣', '🌰', '🌹', '🔔', '⚔', '🛡', '♥', '👛', '♠'],
    ['🍂', '💎', '🏆', '♣', '🌰', '🌹', '🛎', '🤺', '🛡', '♥', '💰', '♠'],

    # Long format
    [' OF LEAVES',
     ' OF DIAMONDS',
     ' OF CUPS',
     ' OF CLUBS',
     ' OF ACORNS',
     ' OF ROSES',
     ' OF BELLS',
     ' OF SWORDS',
     ' OF SHIELDS',
     ' OF HEARTS',
     ' OF COINS',
     ' OF SPADES']
]
