from track.client import AsyncClient
import asyncio


# SERVER = ('localhost', 10101)


def track_flow(receiver, flow):
    src, sport, dst, dport = flow
    message = "TRACK\r\nfrom: {}:{}\r\nto: {}:{}\r\n\r\n".format(src, sport, dst, dport)
    loop = asyncio.get_event_loop()
    host, port = receiver
    client = AsyncClient(loop, host, port)
    coro = client.send(message.encode(encoding='ascii'))
    loop.run_until_complete(coro)
    loop.close()
