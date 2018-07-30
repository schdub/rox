import struct
import sys
import os

__author__ = 'jsbot@ya.ru'

def usage():
    print("""Tool for Safrosoft RoX
usage:
  rox.py --enable_level LVL_FILE [PLAYER [LVL_NAME]]
  rox.py --pack DIR [PAK_FILE]
  rox.py --unpack FILE [DIR]

optional arguments:
  --enable_level LVL_FILE [PLAYER [LVL_NAME]]
                        enable level with NAME (if name not present - will be
                        enabled each level except last one) by PLAYER.
  --pack DIR [PAK_FILE]
                        pack directory DIR into .pak FILE.
  --unpack PAK_FILE [DIR]
                        unpack pak FILE into directory DIR.
""")

def level_enable(file_path, player, level_name):
    if (len(player) > 5):
        player = player[0:5]
    else:
        player = player.ljust(5)
    player = player + '2099:99:99 '

    offsets = []
    with open(file_path, "r+b") as f:
        # collecting levels offsets in file
        levels = []
        while 1:
            # find begin of level
            prev, cur = '  '
            while 1:
                prev = cur 
                cur = f.read(1)
                if not cur: break
                if prev == 's' and cur == '\'': break
            if not cur: break
            levels.append(f.tell())
        # enumerate each level
        offs = 0
        mark = '10'
        for lvl_offset in levels:
            # make sure we don't patch last item
            if offs > 0 and (mark and mark != '20') and (level_name == '' or level_name == name.strip()):
                # do patch
                f.seek(offs + 44)
                f.write(player)
                print(name + ' OK')
            # next levels offset
            offs = lvl_offset
            f.seek(lvl_offset)
            # read name
            name = f.read(30)
            if not name: break
            # read mark
            f.seek(19, 1)
            mark = f.read(2)
            if not mark: break

def pack(in_dir, out_path):
    # get filenames in directory
    files = []
    for (_, _, filenames) in os.walk(in_dir):
        files.extend(filenames)
        break
    offs = 4
    unk = len(files) + offs
    with open(out_path, "wb") as fo:
        fo.write(struct.pack('i', len(files)))      # files count
        for fn in files:
            data = []
            with open(in_dir+'/'+fn, "rb") as f:
                data = f.read()
            offs = offs + len(data) + (len(fn) + 5) * 3
            fo.write(struct.pack('i', offs - unk))  # crc???
            fo.write(struct.pack('i', len(fn)))     # file name length
            fo.write(b'\x00\x00')
            for b in fn:                            # file name
                fo.write(b'\x01\x00')
                fo.write(b)
            fo.write(struct.pack('i', len(data)))   # data length
            fo.write(data)                          # data
            fo.write(b'\x00')
            offs = fo.tell()                        # used for crc calculation
            unk  = unk + (len(fn) * 3)

def unpack(fn, out_dir):
    if not out_dir.endswith('/'):
        out_dir = out_dir + '/'
    try: os.stat(out_dir)
    except: os.mkdir(out_dir) 
    with open(fn, "rb") as f:
        files_count = struct.unpack('i', f.read(4))[0]
        print(files_count)
        for cnt in range(files_count):
            unk = struct.unpack('i', f.read(4))[0] # ???
            name_len = struct.unpack('i', f.read(4))[0]
            #print(name_len * 3)
            f.read(2)                        # 00 00
            name = out_dir
            for i in range(name_len):
                data = f.read(3)             # 01 00 char
                name = name + (data[2])
            #print(name)
            data_size = struct.unpack('i', f.read(4))[0]
            with open(name, "wb") as fo:
                fo.write(f.read(data_size))
            f.read(1)                        # 00
            offs = f.tell()
            print(name)
            #print('%-10s\t%-10s\t%-10s\t%-10s\t%-10s' % (hex(unk), hex(offs), (offs-unk), hex(data_size), name))

if __name__ == '__main__':
    show_usage = True
    if len(sys.argv) >= 3:
        if sys.argv[1] == '--pack':
            show_usage = False
            if len(sys.argv) == 3: sys.argv.append(sys.argv[2] + '.pak')
            pack(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == '--unpack':
            show_usage = False
            if len(sys.argv) == 3: sys.argv.append(sys.argv[2] + '_FILES')
            unpack(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == '--enable_level':
            show_usage = False
            if len(sys.argv) == 3: sys.argv.append('JSBOT')
            if len(sys.argv) == 4: sys.argv.append('')
            level_enable(sys.argv[2], sys.argv[3], sys.argv[4])
    if show_usage:
        usage()
