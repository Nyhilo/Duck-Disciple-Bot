import os
from dotenv import load_dotenv
load_dotenv()


# Discord API related stuff #
PREFIX = '&'

LOG_FILE = 'bot.log'
GENERIC_ERROR = ('Whoops! An error occured while executing this command. You '
                 'should probably tell the bot author about it or something'
                 '...')

# This is set to false to prevent cheating when secretly generating a Sha265
LOG_DEBUG_TO_FILE = os.getenv('DEBUG') == "FALSE"


# General Utility Configurations #
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']
TRUNGIFY_CACHE = 'trungified.png'

SQLITE3_DB_NAME = 'sqlite3.db'
DB_TABLE_REMINDERS_NAME = 'Reminders'

SERVER_ADMIN_IDS = [
    # Me
    116698920515534854,

    # Nomic Moderators
    179409793885143050,
    199307546895450112,
    410992730890698757,
    339046832195764234
]

# Cycle specific configurations #
_phase_two = 'Resolution Phase'
_phase_one = 'Auction Phase'

PHASES_BY_DAY = {
    'Monday': _phase_one,
    'Tuesday': _phase_one,
    'Wednesday': _phase_one,
    'Thursday': _phase_two,
    'Friday': _phase_two,
    'Saturday': _phase_two,
    'Sunday': _phase_two
}

PHASE_CYCLE = {
    _phase_two: _phase_one,
    _phase_one: _phase_two
}

PHASE_START = {
    _phase_two: 'Thursday',
    _phase_one: 'Monday'
}
