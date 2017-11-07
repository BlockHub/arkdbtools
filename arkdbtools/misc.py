import logging
import arkdbtools
from datetime import datetime
from arky import api

def get_height():
    api.use('ark')
    height = []
    for p in api.Peer.getPeersList()['peers']:
        height.append(p['height'])
    return max(height)

print(get_height())