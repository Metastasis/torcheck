import asyncio


class AsyncClient:
    def __init__(self, loop, host=None, port=None):
        self.loop = loop
        self.host = host
        self.port = port

    async def send(self, message):
        reader, writer = await asyncio.open_connection(self.host, self.port, loop=self.loop)

        writer.write(message)
        print('Send: {}'.format(message))

        data = await reader.read(100)
        print('Received: {}'.format(data.decode()))

        writer.close()
