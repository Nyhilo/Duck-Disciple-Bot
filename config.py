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
LOG_DEBUG_TO_FILE = os.getenv('DEBUG') == "TRUE"


# General Utility Configurations #
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
TRUNGIFY_CACHE = 'trungified.png'


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
