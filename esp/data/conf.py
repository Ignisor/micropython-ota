SSID = '[ssid]'
PASSWORD = '[pass]'
CONNECT_RETRIES = 10
CONNECTION_TIME = 6.0

LED_PIN = 2

ERROR_LOG_FILENAME = 'error.log'

try:
    from .local_conf import *
except ImportError:
    pass
