from stem import StreamPurpose
from stem.control import Controller, EventType


def stream_cb(event):
    if event.purpose != StreamPurpose.USER:
        return

    print('[circiut_id-stream_id] {}-{}'.format(event.curc_id, event.id))
    print('requester is {}. ({}:{})'.format(event.source_addr, event.source_address, event.source_port))
    print('destination is {}. ({}:{})'.format(event.target, event.target_address, event.target_port))


with Controller.from_port(port=9051) as ctrl:
    ctrl.authenticate()

    ctrl.add_event_listener(stream_cb, EventType.STREAM)
