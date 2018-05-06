from track.server import AsyncServer
from protocol.parser import Request
from dpkt import UnpackError
import asyncio
import os

SERVER = ('', 10101)

UNKNOWN_RESPONSE = b'Unknown\r\n'
OK = 1


def track_flow(req):
    return OK


handlers = {
    'TRACK': track_flow
}


def is_eof(buf):
    length = len(buf)
    # TODO: check boundaries?
    return buf[length - 4:length] == b'\r\n\r\n'


async def handler_main(reader, writer):
    buf = b''
    while not is_eof(buf):
        data = await reader.read(256)
        buf += data

    res = b'Unknown\r\n'
    status = None
    try:
        req = Request(buf)
    except UnpackError:
        writer.write(UNKNOWN_RESPONSE)
        await writer.drain()
        writer.close()
        return

    if req.method in handlers:
        status = handlers[req.method](req)
    if status == OK:
        res = b'OK\r\n'

    addr = writer.get_extra_info('peername')
    print("Received client from {}".format(addr))
    print("Request: {}".format(req))
    writer.write(res)
    await writer.drain()
    print("Close the client socket")
    writer.close()


async def wakeup():
    # HACK for windows in order to catch KeyboardInterrupt
    while True:
        await asyncio.sleep(1)


if __name__ == '__main__':
    host, port = SERVER
    loop = asyncio.get_event_loop()
    asyncsrv = AsyncServer(loop, host, port, handler=handler_main)
    coro = asyncsrv.start_server_task()
    server = loop.run_until_complete(coro)

    if os.name == 'nt':
        asyncio.async(wakeup())

    # Serve requests until Ctrl+C is pressed
    print('Serving on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

    # Close the server
    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
