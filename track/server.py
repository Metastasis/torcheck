import asyncio


class AsyncServer:
    def __init__(self, loop, host, port, handler=None):
        # get_event_loop() returns singleton
        self.loop = loop
        self.host = host
        self.port = port
        self.handler = handler

    def set_handler(self, handler):
        self.handler = handler

    def start_server_task(self):
        if self.handler is None:
            raise ValueError('You have to specify server\'s handler')
        return asyncio.start_server(self.handler, self.host, self.port, loop=self.loop)
