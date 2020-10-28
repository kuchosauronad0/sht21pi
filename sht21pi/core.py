#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Andre Poley
@contact: andre.poley@mailbox.org
@copyright: (c) 2019 by Andre Poley, Berkeley
@license: MIT
@version: 0.0.3
@summary: Core component to run the argospi2c module
'''

import sht21pi


def main():
    try:
        sht21pi.StorageHumidityMonitor(1).run()
    except IOError as e:
        raise IOError('\nCannot create connection to i2c. Permission denied. {}'.format(e))


if __name__ == "__main__":
    main()

# vim: fileencoding=utf-8 filetype=python ts=4 expandtab
