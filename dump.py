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

    if line:
        line = line + '\n'
        fp.write(line)


# if __name__ == '__main__':
#     stream = b'\x31\x32\x34\x43\x39\x33\x67\x68\x69\x50\x78\x77\x66\x33\x29'
#     fname = 'test.txt'
#     with open('./tmp/' + fname, 'w') as fp:
#         dump(fp, stream)
