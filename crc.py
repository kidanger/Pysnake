#!/usr/bin/env python
# -*- coding:Utf-8 -*-


from binascii import crc32


USE = 1


def get_crc(s):
   if USE == 1:
      crc = get_crc1(s)
   elif USE == 2:
      crc = get_crc2(s)
   return str(crc)

def get_crc1(s):
   return crc32(s) & 0xffffffff
   

def get_crc2(s):
   return abs(crc32(s))




def main():
   print get_crc("test")
   return 0

if __name__ == '__main__': main()
