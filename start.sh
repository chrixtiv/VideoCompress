#!/bin/bash

# Fix time issue (needed for Telegram to work)
date -s "$(curl -s --head http://google.com | grep ^Date: | sed 's/Date: //g')"

# Start your bot
python3 -m bot
