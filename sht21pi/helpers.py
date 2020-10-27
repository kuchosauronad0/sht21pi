#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Andre Poley
@contact: andre.poley@mailbox.org
@copyright: (c) 2019 by Andre Poley, Berkeley
@license: MIT
@version: 0.0.3
@summary: Some helper functions to make life easier
'''
import logging


def debugging():
    """Get some debug info"""
    return True


def to_bool(s):
    if s.upper() == 'TRUE':
        return True
    else:
        return False


def write_log(logfile, message):
    """Write to data log
    @param message: An array with sensors readings to be written to the data log.
    @type message: [[int, int, float, float]]
    @return: None
    """
    try:
        fp = open(logfile, 'a')
        logging.getLogger().info("logging to {}".format(logfile))
        for i in range(len(message)):
            fp.write("{}, {}, {}, {}\n".format(message[i][0], message[i][1], message[i][2], message[i][3]))
    except IOError as e:
        raise IOError("Cannot access file {}".format(e), exc_info=True)
    except UnboundLocalError as e:
        raise UnboundLocalError("{}".format(e))
    finally:
        fp.close()
        logging.getLogger().info("Wrote log", exc_info=False)

# vim: fileencoding=utf-8 filetype=python ts=4 expandtab
