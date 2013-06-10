import pyaudio

CHUNK = 16384
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100


THRESHOLD = -10000
MESSAGE_LENGTH = 0.09
ENTIRE_MESSAGE_LENGTH = 0.15

REFERENCE_SIGNAL_FILENAME = 'reference_signal.pkl'
ACTIONS_FILENAME = 'action_definitions.json'

REFERENCE_SINGAL_TIME = 0.015
REFERENCE_INTERP_SAMPLES = 400
REFERENCE_THRESHOLD = 15

DECODE_SEARCH_AREA = 40
BIT_HEADER = 5

ACTIONS = [
    {'name': 'PLAYPAUSE', 'action': 'VK_MEDIA_PLAY_PAUSE'},
    {'name': 'BACK', 'action': 'VK_MEDIA_PREV_TRACK'}, 
    {'name': 'FORWARD', 'action': 'VK_MEDIA_NEXT_TRACK'}, 
    {'name': 'STOP', 'action': 'VK_MEDIA_STOP'}, 
    {'name': 'EJECT', 'action': None}, 
    {'name': 'PAUSE', 'action': 'VK_MEDIA_PLAY_PAUSE'},
]
