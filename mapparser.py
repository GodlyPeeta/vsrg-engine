def parseMap (map):
    ret = []
    with open(f'maps/{map}/map.txt', 'r') as maptxt:
        object = []
        for l in maptxt:
            if l[:1] == 'L':
                object.append(int(l[-2:-1]) - 1)
            elif l[:1] == 'S':
                ret.append(object)
                object = []
                object.append(int(l[11:-1]))
            elif l[:1] == 'E':
                print("ff")
                object.append(int(l[9:-1]))
                object.append(False)
                object.append(0)
    ret.pop(0)
    return ret

# testing