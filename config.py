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

GLOBAL_ADMIN_IDS = [116698920515534854]
SERVER_ADMIN_IDS = {
    # Infinite Nomic
    515560801394753537: [
        179409793885143050,
        199307546895450112,
        410992730890698757,
        339046832195764234
    ],
    # Agora
    724077429412331560: [
        164117897025683456,
        120700893212573696
    ],
    # Diplomacy
    892773002440241153: [
        95923810062053376
    ],
    # Dice
    121129460018708480: [
        116698920515534854,
        331266664270266370,
        231237666597896192,
    ],
    # Test Server
    443181366184640513: [

    ]
}


# Cycle specific configurations #
PHASE_START_DATE = (2021, 11, 1)

_phase_one = 'Phase I'
_phase_two = 'Phase II'

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
