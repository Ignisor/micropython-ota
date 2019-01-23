import esp; esp.osdebug(None)

import gc

from utils import wifi


wifi.toggle_wifi(True)
is_connected = wifi.connect()

gc.collect()
