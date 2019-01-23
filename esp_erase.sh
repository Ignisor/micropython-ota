#!/bin/bash

sudo .env/bin/esptool.py --port /dev/ttyUSB0 erase_flash
read -p "Replug adapter or reset the board and press enter to continue..."; echo
sudo .env/bin/esptool.py --port /dev/ttyUSB0 write_flash 0 $1
