#!/usr/bin/env python
#  -*- coding: utf-8 -*-
#ygavrilenko@gmail.com
# very simple linear encoding


def enc(password):
    result = [chr((int(i, 16) ^ 0xb) - 0x4) for i in [hex(ord(i)) for i in password]]
    print ''.join(result)
    return 0
