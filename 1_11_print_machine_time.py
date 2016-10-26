#!/usr/bin/env python
# -*- Coding: UTF-8 -*-
# Python Network Programming Cookbook -- Chapter -1
# This program is optimized for python 3.4
# It may run on any other version with/without modifications.

import ntplib
from time import ctime

def print_time():
    ntp_client = ntplib.NTPClient()
    response = ntp_client.request('pool.ntp.org')

if __name__ == '__main__':
    print_time()
