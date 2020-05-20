import os, struct, sys, argparse, lzma

#CONSTANTS
PART_MAGIC = 0x58881688
PART_EXT_MAGIC = 0x58891689
PART_HDR_DATA_SIZE = 512
CHK_HDR_SIZE = 512

def fix_cstr(name):
    return name.decode('utf-8').rstrip('\x00')

class Modem:
    def __init__(self, fstream):
        global args
        self.verbose = args.verbose
        self.file = fstream
        self.partitions = {}

    def stream_unpack(self, fmt, max_size = 0):
        size = struct.calcsize(fmt)
        data = self.file.read(size)
        res = struct.unpack(fmt, data)
        if max_size > size:
            self.file.read(max_size - size)
        return res
    
    def parse_partitions(self):
        img_list_end = 0
        while not img_list_end:
            magic, dsize, name, ext_magic, img_type, img_list_end, align_size = self.get_partition_header()
            if not self.verify_part_header(magic, dsize, ext_magic):
                raise Exception('Invalid partition header')
            name = fix_cstr(name)
            self.partitions[name] = (self.file.tell(), dsize)
            if dsize % align_size:
                dsize += align_size - (dsize % align_size)
            self.file.seek(dsize, 1)
    
    def get_partition_header(self):
        magic, dsize, name, _, _, ext_magic, _, _, img_type, img_list_end, align_size = self.stream_unpack('II32sIIIIIIII', PART_HDR_DATA_SIZE)
        return magic, dsize, name, ext_magic, img_type, img_list_end, align_size
    
    def verify_part_header(self, magic, dsize, ext_magic):
        return magic == PART_MAGIC and dsize != 0 and ext_magic == PART_EXT_MAGIC
    
    def get_partition_info(self, name):
        if not name in self.partitions:
            raise Exception('Unable to find %s partition within image file' % name)
        return self.partitions[name]
        
    def get_partition_data(self, name):
        pos, size = self.get_partition_info(name)
        self.file.seek(pos)
        return self.file.read(size)
        
    def extract_modem_rom(self):
        rom = self.get_partition_data('md1rom')
        with open('modem.bin', 'wb') as f:
            f.write(rom)
            
    def decompress(self, data):
        return lzma.decompress(data)
    
    def extract_dbginfo(self):
        dbginfo = self.get_partition_data('md1_dbginfo')
        dbginfo = self.decompress(dbginfo)
        with open('modem_dbginfo', 'wb') as f:
            f.write(dbginfo[0x10:])
    
    def unpack(self, dst = 'modem'):
        self.parse_partitions()
        self.extract_modem_rom()
        self.extract_dbginfo()

def main():
    global args
    args = parseArgs()

    path = args.modem_bin
    fmw = open(path, 'rb')

    mod = Modem(fmw)
    mod.unpack()

    fmw.close()

def parseArgs():
    parser = argparse.ArgumentParser(description = 'Extract modem and debug info from image')
    parser.add_argument('modem_bin',  help='Modem image file')
    return parser.parse_args()

if __name__ == '__main__':
    main()

#find md1rom


#find md1dbg

#ungzip md1dbg

