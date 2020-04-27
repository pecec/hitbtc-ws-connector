import sys, os, time, pathlib
sys.path.append( '../connector' )
import asyncio
from client import HitBTC
import queue

async def myCallback( _raw ):
    print( str(_raw) )

def my_split( seps, s ):
    res = [s]
    for sep in seps:
        s, res = res, []
        for seq in s:
            res += seq.split(sep)
    i = 0
    while i < len( res ):
        if res[i] == '':
            res.pop(i)
            continue
        i += 1
    return res

def getPubSecKeys( fname ):
    if not os.path.isfile( fname ):
        raise ValueError( 'File doesn\'t exist: %s' % fname )
    f = open( fname, 'r' )
    lines = []
    for line in f:
        cleaned = my_split( '\r\n', line )
        if len( cleaned ) == 0:
            continue
        lines.append( cleaned[0] )
        if len( lines ) >= 2:
            break
    f.close()
    return lines[0], lines[1]
    
async def connectorControlThread( _connector ):
    print( 'counting to 20...' )
    for i in range( 1, 21 ):
        await asyncio.sleep(1)
        print( 'i=%d' % i )
    await _connector.subscribe_ticker( symbol='ETHBTC', cancel = True )
    await asyncio.sleep(2)
    await _connector.stop()

    
"""
    def __init__(self, key=None, secret=None, raw=None, stdout_only=False, silent=False, url=None,
                 **conn_ops):
        
        Initialize the instance.

        :param key: API Public Key
        :param secret: API Secret Key
        :param raw: Bool, whether or not to unpack data or pass it as is
        :param stdout_only: Bool, passing True will turn off placing data on self.conn.q
        :param silent: Bool, passing True turns off print() arguments
        :param url: URL of the websocket API. Defaults to wss://api.hitbtc.com/api/2/ws
        :param conn_ops: Optional Kwargs to pass to the HitBTCConnector object
"""

url = 'wss://api.hitbtc.com/api/2/ws'
certFile = 'hitbtc-com-chain.pem'
keysFile = 'pubseckeys.txt'

pub, sec = getPubSecKeys( keysFile )

if not os.path.isfile( certFile ):
    raise ValueError( 'File doesn\'t exist: %s' % certFile )

hitbtc = HitBTC( pub, sec, False, True, False, url,
                 pathlib.Path(__file__).with_name( certFile ) )

loop = asyncio.get_event_loop()

loop.run_until_complete( hitbtc.connect() )
time.sleep(2)  # Give the socket some time to connect
                         
loop.run_until_complete( hitbtc.login( pub, sec, True ) )
loop.run_until_complete( hitbtc.recvProcessResponse( myCallback ) )
#time.sleep(2)

loop.run_until_complete( hitbtc.subscribe_ticker( symbol='ETHBTC' ) )
loop.run_until_complete( hitbtc.recvProcessResponse( myCallback ) )
#time.sleep(2)


tasks = [
    asyncio.ensure_future( hitbtc.messageLoop( myCallback ) ),
    asyncio.ensure_future( connectorControlThread( hitbtc ) )
    ]

loop.run_until_complete( asyncio.wait( tasks ) )


