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
