#! /usr/bin/env python3

import asyncio
import aiohttp
import json
import warnings
import websockets

from .service import Service

__all__ = ["Browser"]

class Browser:

    def __init__(self, loop=None, opts=[]):
        self.service = Service(opts)            
        self.dev_url = self.service.url
        self.tab_id = None
        self._cur_id = 1000
        self.started = False
        self.stopped = False
        self.connected = False
        self.event_handlers = {}
        self.method_results = {}
        self.event_queue = asyncio.Queue()        
        self.loop = loop or asyncio.get_event_loop().set_exception_handler(lambda loop, context: None)        
        self.session = aiohttp.ClientSession(loop=self.loop)

    async def ws_endpoint(self):
        async with self.session.get(f"{self.dev_url}/json/new?") as rp:
            data = await rp.json()
            self.tab_id = data.get('id')
            return data.get('webSocketDebuggerUrl')

    async def close_tab(self):
        async with self.session.get(f"{self.dev_url}/json/close/{self.tab_id}") as rp:
            await rp.text()
            return

    async def ws_send(self, message):
        if 'id' not in message:
            self._cur_id += 1
            message['id'] = self._cur_id
        message_json = json.dumps(message)
        try:
            queue = asyncio.Queue()
            self.method_results[message['id']] = queue
            await self._ws.send(message_json)
            while not self.stopped:
                try:
                    return await asyncio.wait_for(queue.get(), 1)
                except asyncio.TimeoutError:
                    continue
            raise Exception(f"User abort, call stop() when calling {message['method']}")
        finally:
            self.method_results.pop(message['id'])

    async def _recv_loop(self):
        while not self.stopped:
            try:
                message_json = await self._ws.recv()
                message = json.loads(message_json)
            except:
                continue
            if "method" in message:
                await self.event_queue.put(message)
            elif "id" in message:
                if message["id"] in self.method_results:
                    await self.method_results[message['id']].put(message)
            else:
                warnings.warn(f"unknown message: {message}")

    async def _handle_event_loop(self):
        while not self.stopped:
            event = await self.event_queue.get()
            if event['method'] in self.event_handlers:
                try:
                    await self.event_handlers[event['method']](**event['params'])
                except Exception as e:
                    print(f"callback {event['method']} exception")

    async def send(self, _method, *args, **kwargs):
        if not self.started:
            raise Exception("Cannot call method before it is started")
        if args:
            raise Exception("the params should be key=value format")
        if self.stopped:
            raise Exception("browser has been stopped")
        result = await self.ws_send({"method": _method, "params": kwargs})
        if 'result' not in result and 'error' in result:
            warnings.warn(f"{_method} error: {result['error']['message']}")
            raise Exception(f"calling method: {_method} error: {result['error']['message']}")
        return result['result']

    def on(self, event, callback):
        if not callback:
            return self.event_handlers.pop(event, None)
        if not callable(callback):
            raise Exception("callback should be callable")
        self.event_handlers[event] = callback
        return

    async def start(self):
        if self.started:
            return        
        self.stopped = False
        self.started = True
        self.connected = False        
        self._websocket_url = await self.ws_endpoint()        
        self._ws = await websockets.connect(self._websocket_url, loop=self.loop, ping_interval=None)
        if self._ws.open:
            self.connected = True
            self._recv_task = asyncio.ensure_future(self._recv_loop(), loop=self.loop)
            self._handle_event_task = asyncio.ensure_future(self._handle_event_loop(), loop=self.loop)
        return

    async def stop(self):
        if self.stopped:
            return
        if not self.started:
            raise Exception("Browser is not running")
        self.started = False
        self.stopped = True
        if self.connected and self._ws.open:            
            await self._ws.close()
            await self.close_tab()
            self._recv_task.cancel()
            self._handle_event_task.cancel()
            self.connected = False
        self.service.stop()        
        return

    def __str__(self):
        return f'<Browser {self.dev_url}>' 

    __repr__ = __str__    

    async def __aenter__(self):
        return self

    async def __aexit__(self, *excinfo):
        await self.session.close()              
