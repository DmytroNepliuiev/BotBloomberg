# client/overlay/auth.py
import webbrowser
import asyncio
import aiohttp
from aiohttp import web
from typing import Optional
from .config import OAUTH_LOGIN_URL, LOCAL_CALLBACK_HOST, LOCAL_CALLBACK_PORT, LOCAL_CALLBACK_URL
from .state_manager import state
import threading

# The client expects backend to redirect to: http://LOCAL_CALLBACK_HOST:LOCAL_CALLBACK_PORT/callback?token=<jwt>
# This module starts a small HTTP server to listen for that callback and capture token.

class OAuthCallbackServer:
    def __init__(self, host=LOCAL_CALLBACK_HOST, port=LOCAL_CALLBACK_PORT):
        self.host = host
        self.port = port
        self._app = web.Application()
        self._runner = None
        self._site = None
        self._token_future: Optional[asyncio.Future] = None

        self._app.router.add_get("/callback", self._handle_callback)

    async def _handle_callback(self, request: web.Request):
        params = request.rel_url.query
        token = params.get("token") or params.get("jwt")
        # For backward compatibility, accept 'token' or 'jwt'
        if token:
            # set token into state
            state.set_token(token)
            # show simple HTML page
            text = "<html><body><h3>Login complete — you can close this window.</h3></body></html>"
            return web.Response(text=text, content_type="text/html")
        else:
            return web.Response(text="Missing token", status=400)

    async def start(self):
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, self.host, self.port)
        await self._site.start()

    async def stop(self):
        if self._runner:
            await self._runner.cleanup()

# Helper to open browser and start local server (runs server in background thread's event loop)
def login_via_browser():
    """
    Opens browser to backend OAuth login. Starts a local aiohttp server to capture callback.
    Assumes backend will redirect to http://LOCAL_CALLBACK_HOST:LOCAL_CALLBACK_PORT/callback?token=<jwt>
    """
    loop = asyncio.new_event_loop()
    server = OAuthCallbackServer()

    def _start_loop():
        asyncio.set_event_loop(loop)
        loop.run_until_complete(server.start())
        loop.run_forever()

    t = threading.Thread(target=_start_loop, daemon=True)
    t.start()

    # open browser to backend's login URL — backend must use redirect_uri matching LOCAL_CALLBACK_URL
    # If backend needs redirect_uri param, append it.
    url = OAUTH_LOGIN_URL
    # If backend supports redirect param:
    if "redirect_uri=" not in url:
        # add redirect param to be safe
        from urllib.parse import urlencode, urlparse, parse_qs, urlunparse, ParseResult
        url = f"{url}?redirect_uri={LOCAL_CALLBACK_URL}"
    webbrowser.open(url)

    # We'll not block here; the callback handler will set token via state.set_token
    # Return thread and loop so caller may stop server if needed
    return t, loop, server
