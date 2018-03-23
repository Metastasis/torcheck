def dump(fp, stream):
    if not fp:
        return None

    per_line = 10
    cnt = 0
    line = ''

    for byte in bytearray(stream):
        char = chr(byte)

        if char == ' ':
            char = '.'

        cnt = cnt + 1
        line = line + char

        if not (cnt % per_line):
            line = line + '\n'
            fp.write(line)
            cnt = 0
            line = ''
