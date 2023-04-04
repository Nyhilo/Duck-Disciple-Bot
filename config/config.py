import os
from dotenv import load_dotenv
load_dotenv()

DEBUG = os.getenv('DEBUG') == 'TRUE'

# Discord API related stuff #
PREFIX = '&'

LOG_FILE = 'log.txt'

# This is set to false to prevent cheating when secretly generating a Sha265
LOG_DEBUG_TO_FILE = True if DEBUG else False


# General Utility Configurations #
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']
CACHE_FOLDER = 'cached'
TRUNGIFY_CACHE = 'cached/out-trungified.png'
SDN_DIR = 'imgs/stopdoingnomic'

SQLITE3_DB_NAME = 'sqlite3.db'
DB_TABLE_REMINDERS_NAME = 'Reminders'
DB_TABLE_POOLS_NAME = 'Pools'
DB_TABLE_POOL_ENTRIES_NAME = 'Pool_Entries'
DB_TABLE_SETTINGS_NAME = 'Settings'

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


CARDS = [
    '<:AceSpades:908571986232479754>',
    '<:2Spades:908571986056323132>',
    '<:3Spades:908571986240897034>',
    '<:4Spades:908571986299592724>',
    '<:6Spades:908571986148597800>',
    '<:6Spades:908571986085699614>',
    '<:7Spades:908571986081513512>',
    '<:8Spades:908571986085707806>',
    '<:9Spades:908571986098257931>',
    '<:10Spades:908571985733353514>',
    '<:JackSpades:908571986131828766>',
    '<:QueenSpades:908571986094096424>',
    '<:KingSpades:908571986102480946>',
    '<:AceHearts:908572014296584202>',
    '<:2Hearts:908572013713588247>',
    '<:3Hearts:908572013902307348>',
    '<:4Hearts:908572013713567785>',
    '<:5Hearts:908572014078484500>',
    '<:6Hearts:908572013906526229>',
    '<:7Hearts:908572014023958569>',
    '<:8Hearts:908572014028161054>',
    '<:9Hearts:908572013977829417>',
    '<:10Hearts:908572014082678794>',
    '<:JackHearts:908572013956833332>',
    '<:QueenHearts:908572013541589013>',
    '<:KingHearts:908572014015557642>',
    '<:AceClubs:908571599849025597>',
    '<:2Clubs:908571599836442644>',
    '<:3Clubs:908571599475712021>',
    '<:4Clubs:908571599819653160>',
    '<:5Clubs:908571599811256330>',
    '<:6Clubs:908571599907749898>',
    '<:7Clubs:908571599832252446>',
    '<:8Clubs:908571599542841345>',
    '<:9Clubs:908571599844802660>',
    '<:10Clubs:908571599656071220>',
    '<:JackClubs:908571599937093642>',
    '<:QueenClubs:908571599857414184>',
    '<:KingClubs:908571599651889205>',
    '<:AceDiamonds:908571635009859635>',
    '<:2Diamonds:908571634741424171>',
    '<:3Diamonds:908571634976313414>',
    '<:4Diamonds:908571634896633906>',
    '<:5Diamonds:908571634896629800>',
    '<:6Diamonds:908571635186040832>',
    '<:7Diamonds:908571635118899230>',
    '<:8Diamonds:908571634917593148>',
    '<:9Diamonds:908571634921775104>',
    '<:10Diamonds:908571635072761899>',
    '<:JackDiamonds:908571635009867836>',
    '<:QueenDiamonds:908571634938552381>',
    '<:KingDiamonds:908571634787581993>',
]

# The maximum character limit in which we attempt to trigger &stopdoingnomic on a message
STOP_DOING_MSG_LEN_LIMIT = 280
STOP_DOING_DEFAULT_CHANCE = 0.3
DEFAULT_STOP_DOING_RESPONSE = 'stop doing nomic.png'


# Voice channels for time-tracking updates
UTC_UPDATE_CHANNEL = 1029079234427244544 if not DEBUG else 1028894151451885638
PHASE_UPDATE_CHANNEL = 1029235284195418192 if not DEBUG else 1029220076097896448
PHASE_END_UPDATE_CHANNEL = 1033465614695673858 if not DEBUG else 1031640532939702363

PHASE_START_DATE = (2022, 12, 23)
LOOP_VALUE = 'Eighth'

# Defines the cycle in which phases are looped starting with the start date
# For instance, a cycle of [3, 2, 2] would have a 3-day Phase I, 2-day Phase II, 2-day Phase III, etc.
PHASE_GROUPS = [2, 3, 2]
