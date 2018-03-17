from stem.control import Controller

with Controller.from_port(port=9051) as ctrl:
    ctrl.authenticate()

    read = ctrl.get_info('traffic/read')
    written = ctrl.get_info('traffic/written')

    print('Read {} bytes. Received {} bytes.'.format(read, written))
