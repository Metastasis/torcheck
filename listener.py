from stem import StreamPurpose, CircStatus
from stem.control import Controller, EventType
from sys import exit


def stream_cb(event):
    if event.purpose != StreamPurpose.USER:
        return

    print('[circiut_id-stream_id] {}-{}'.format(event.circ_id, event.id))
    print('status is {}'.format(event.status))
    print('requester is {}'.format(event.source_addr))
    print('destination is {}'.format(event.target))
    print('reason is {}'.format(event.reason))
    print('remote reason is {}'.format(event.remote_reason))
    print()


def circ_cb(event):
    print('status: {}'.format(event.status))
    print('path: {}'.format(event.path))
    print('purpose: {}'.format(event.purpose))
    print()


if __name__ == '__main__':
    with Controller.from_port(port=9051) as ctrl:
        ctrl.authenticate()

        ctrl.add_event_listener(circ_cb, EventType.CIRC)

        try:
            while True:
                pass
        except KeyboardInterrupt:
            print('Exiting')
            ctrl.remove_event_listener(stream_cb)
            exit(1)
