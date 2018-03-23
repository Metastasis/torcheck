def dump(fp, stream):
    if not fp:
        return None

    per_line = 10
    cnt = 0
    line = ''

    for byte in stream:
        try:
            char = byte.encode('ascii')
        except:
            char = byte.hex()

        if char == ' ' or char == '20':
            char = '.'

        cnt = cnt + 1
        line = line + char

        if not (cnt % per_line):
            line = line + '\n'
            fp.write(line)
            cnt = 0
            line = ''
