"""Client Object to connect to API and relevant Exceptions."""
# Import Built-Ins
import logging, websockets

# Import Third-Party

# Import Homebrew
#from hitbtc.connector import HitBTCConnector
from connector import HitBTCConnector

# Init Logging Facilities
log = logging.getLogger(__name__)


class CredentialsError(ValueError):
    pass


class HitBTC:
    """HitBTC Websocket API Client class.

    Programmed using the official API documentation as a reference.

    Documentation can be found here:
        https://api.hitbtc.com/?python#socket-api-reference

    """

    def __init__( self, key=None, secret=None, raw=None, stdout_only=False, silent=False,
                 url=None, ssl_cert_file=None ):
        """
        Initialize the instance.

        :param key: API Public Key
        :param secret: API Secret Key
        :param raw: Bool, whether or not to unpack data or pass it as is
        :param stdout_only: Bool, passing True will turn off placing data on self.conn.q
        :param silent: Bool, passing True turns off print() arguments
        :param url: URL of the websocket API. Defaults to wss://api.hitbtc.com/api/2/ws
        :param conn_ops: Optional Kwargs to pass to the HitBTCConnector object
        """
        self.conn = HitBTCConnector( url, ssl_cert_file, raw, stdout_only, silent )
        self.key = key
        self.secret = secret

    async def recv(self, block=True, timeout=None):
        """Retrieve data from the connector queue."""
        return await self.conn.recv(block, timeout)

    @property
    def credentials_given(self):
        """Assert if credentials are complete."""
        return self.key and self.secret

    async def connect(self):
        """Start the websocket connection."""
        await self.conn._connect()

    async def stop(self):
        """Stop the websocket connection."""
        await self.conn.stop()

    async def messageLoop( self, __callback ):
        return await self.conn.onMessage( __callback )

    async def recvProcessResponse( self, __callback ):
        await self.conn.recvResponse( __callback )
        

    def is_connected(self):
        return self.conn._is_connected
        
    async def login(self, key=None, secret=None, basic=None, custom_nonce=None):
        """
        Login using the WSS API.

        Offical Endpoint Documentation:
            https://api.hitbtc.com/?python#socket-session-authentication
        """
        if not self.credentials_given and not (key and secret):
            raise CredentialsError("Must give API key and Secret to login to API!")
        else:
            await self.conn.authenticate( key or self.key, secret or self.secret, basic, custom_nonce )

    async def request_currencies(self, custom_id=None, **params):
        """
        Request currencies currently listed at HitBTC.

        Offical Endpoint Documentation:
            https://api.hitbtc.com/?python#get-currencies
        """
        await self.conn.send('getCurrencies', custom_id, **params)

    async def request_symbols(self, custom_id=None, **params):
        """
        Request symbols currently traded at HitBTC.

        Offical Endpoint Documentation:
            https://api.hitbtc.com/?python#get-symbols
        """
        await self.conn.send('getSymbols', custom_id, **params)

    async def request_trades(self, custom_id=None, **params):
        """
        Request trades executed at HitBTC.

        Offical Endpoint Documentation:
            https://api.hitbtc.com/?python#get-trades
        """
        await self.conn.send('getTrades', custom_id=custom_id, **params)

    async def request_balance(self, custom_id=None, **params):
        """
        Request your account's balance.

        This requires you to be logged-in! Call ``login()`` first.

        Offical Endpoint Documentation:
            https://api.hitbtc.com/?python#get-trading-balance
        """
        await self.conn.send('getTradingBalance', custom_id=custom_id, **params)

    async def request_active_orders(self, custom_id=None, **params):
        """
        Request your account's active orders.

        This requires you to be logged-in! Call ``login()`` first!

        Offical Endpoint Documentation:
            https://api.hitbtc.com/?python#get-active-orders-2
        """
        await self.conn.send('getOrders', custom_id=custom_id, **params)

    async def subscribe_reports(self, cancel=False, custom_id=None, **params):
        """
        Request a stream of your account's order activities.

        This requires you to be logged-in! Call ``HitBTC.login()`` first!

        Offical Endpoint Documentation:
            https://api.hitbtc.com/?python#subscribe-to-reports
        """
        method = 'subscribeReports'
        if cancel:
            method = 'un' + method
        await self.conn.send(method, custom_id=custom_id, **params)

    async def subscribe_ticker(self, cancel=False, custom_id=None, **params):
        """Request a stream for ticker data.

        Offical Endpoint Documentation:
            https://api.hitbtc.com/?python#subscribe-to-ticker
        """
        method = 'subscribeTicker'
        if cancel:
            method = 'un' + method
        await self.conn.send(method, custom_id=custom_id, **params)

    async def subscribe_book(self, cancel=False, custom_id=None, **params):
        """Request a stream for order book data.

        Offical Endpoint Documentation:
            https://api.hitbtc.com/?python#subscribe-to-orderbook
        """
        method = 'subscribeOrderbook'
        if cancel:
            method = 'un' + method
        await self.conn.send(method, custom_id=custom_id, **params)

    async def subscribe_trades(self, cancel=False, custom_id=None, **params):
        """Request a stream for trade data.

        Offical Endpoint Documentation:
            https://api.hitbtc.com/?python#subscribe-to-trades
        """
        method = 'subscribeTrades'
        if cancel:
            method = 'un' + method
        await self.conn.send(method, custom_id=custom_id, **params)

    async def subscribe_candles(self, cancel=False, custom_id=None, **params):
        """Request a stream for candle data.

        Offical Endpoint Documentation:
            https://api.hitbtc.com/?python#subscribe-to-candles
        """
        method = 'subscribeCandles'
        if cancel:
            method = 'un' + method
        await self.conn.send(method, custom_id=custom_id, **params)

    async def place_order(self, custom_id=None, **params):
        """
        Place a new order via Websocket.

        Offical Endpoint Documentation:
            https://api.hitbtc.com/?python#place-new-order
        """
        await self.conn.send('newOrder', custom_id=custom_id, **params)

    async def cancel_order(self, custom_id=None, **params):
        """
        Cancel an order via Websocket.

        Offical Endpoint Documentation:
            https://api.hitbtc.com/?python#cancel-order
        """
        await self.conn.send('cancelOrder', custom_id=custom_id, **params)

    async def replace_order(self, custom_id=None, **params):
        """
        Replace an existing order via Websocket.

        Offical Endpoint Documentation:
            https://api.hitbtc.com/?python#cancel-replace-orders
        """
        await self.conn.send('cancelReplaceOrder', custom_id=custom_id, **params)
