#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Andre Poley
@contact: andre.poley@mailbox.org
@copyright: (c) 2019 by Andre Poley, Berkeley
@license: MIT
@version: 0.0.3
@summary: read specified i2c address. Returns: epoch, address, temperature, humidity
'''
import sys
import socket
import logging
import time

_SOFTRESET = 0xFE
_I2C_ADDRESS = 0x40
_TRIGGER_TEMPERATURE_NO_HOLD = 0xF3
_TRIGGER_HUMIDITY_NO_HOLD = 0xF5

# datasheet (v4), page 9, table 7, thanks to Martin Milata
# for suggesting the use of these better values
# code copied from https://github.com/mmilata/growd
_TEMPERATURE_WAIT_TIME = 0.086  # (datasheet: typ=66, max=85)
_HUMIDITY_WAIT_TIME = 0.030     # (datasheet: typ=22, max=29)

_SENSORS_PRESENT = 0x0000
_SENSORS_ADDR = []
_SENSORS_MUX1_ADDR = 0x00
_SENSORS_MUX2_ADDR = 0x01


def read_i2c_addr(i2c_addr):    
    """Reads the time, sensor id, temperature and humidity from the address if
    the address defined as a sensors in the configuration file.
    Blocks for 250ms to allow the sensor to return the data
    @param i2c_addr: The i2c address to be read
    @type i2c_addr: int
    @return: array with time, address, temperature and humidity
    @summary: use mux1 for sensors 1-8 and mux2 for the others.
    Substract 8 to match the actual address for the multiplex slave
    """
    logging.getLogger().debug("reading i2c_addr:\t\t{} / {}".format(i2c_addr,hex(i2c_addr)))
    if i2c_addr < 9:
        selectMuxOut(_SENSORS_MUX1_ADDR, i2c_addr) 
    else:
        selectMuxOut(_SENSORS_MUX2_ADDR, i2c_addr-8)
    try:
        temp = read_temperature()
        humi = read_humidity()

        return [int(time.time()), int(i2c_addr), float(temp), float(humi) ]
    except Exception as e:
        raise Exception('Cannot read sensors {}'.format(e))
    finally:
        logging.getLogger().info("Read sensor\t\t\t'{}': {} {}".format(int(i2c_addr), float(temp), float(humi)))

def read_temperature():    
    """Reads the temperature from the sensor.  Note that this call blocks for
    250ms to allow the sensor to return the data
    """
    data = []
    try:
        bus.write_byte(_I2C_ADDRESS, _TRIGGER_TEMPERATURE_NO_HOLD)
        time.sleep(_TEMPERATURE_WAIT_TIME)
        data.append(bus.read_byte(_I2C_ADDRESS))
        data.append(bus.read_byte(_I2C_ADDRESS))
        temp = _get_temperature_from_buffer(data)
    except IOError:
        temp = -400.
        logging.getLogger().error("Cannot read temperature from I2C address: {}".format(self._I2C_ADDRESS), exc_info=True)
        raise IOError("Cannot read temperature from I2C address: {}".format(self._I2C_ADDRESS), exc_info=True)
    finally:
        logging.getLogger().debug("read_temperature:\t\t{}".format(temp))
        return temp

def _get_temperature_from_buffer(data):
    """This function reads the first two bytes of data and 
    returns the temperature in C by using the following function:
    T = =46.82 + (172.72 * (ST/2^16))
    where ST is the value from the sensor
    """
    unadjusted = -46.85 + 175.72*((data[0] << 8) + (data[1] & 0xfc))/(1 << 16)
    return unadjusted
    
def read_humidity():    
    """Reads the humidity from the sensor.  Not that this call blocks 
    for 250ms to allow the sensor to return the data"""
    data = []
    try:
        bus.write_byte(_I2C_ADDRESS, _TRIGGER_HUMIDITY_NO_HOLD)
        time.sleep(_HUMIDITY_WAIT_TIME)
        data.append(bus.read_byte(_I2C_ADDRESS))
        data.append(bus.read_byte(_I2C_ADDRESS))
        temp = _get_humidity_from_buffer(data)
    except IOError as err:
        logging.getLogger().error("Cannot read humidity from I2C address: {}\n{}".format(_I2C_ADDRESS, err), exc_info=True)
        temp = -100. 
        raise IOError("Cannot read humidity from I2C address: {} ({})".format(_I2C_ADDRESS,err))
        sys.exit(1)
    finally:
        logging.getLogger().debug("read_humidity:\t\t{}".format(temp))
        return temp

def _get_humidity_from_buffer(data):
    """This function reads the first two bytes of data and returns 
    the relative humidity in percent by using the following function:
    RH = -6 + (125 * (SRH / 2 ^16))
    where SRH is the value read from the sensor
    """
    unadjusted = -6.0 + 125.0*((data[0] << 8) + (data[1] & 0xfc))/(1 << 16)
    return unadjusted
    
def selectMuxOut(address, index):
    logging.getLogger().debug("MuxOut address:\t\t{} index: {}".format(hex(address),hex(index)))
    if index != 0:
        bus.write_byte(address, 0x01 << (index - 1))
    else:
        bus.write_byte(0x71, 0x00);

def __enter__(self):
    """used to enable python's with statement support"""
    return self

def __exit__(self, type, value, traceback):
    """with support"""
    self.close()

def close(self):
    """Closes the i2c connection"""
    self.bus.close()


def debug():
    logging.getLogger().debug('_SENSORS_PRESENT:\t\t{}'.format(hex(_SENSORS_PRESENT)))
    logging.getLogger().debug('_SENSORS_ADDR:\t\t{}'.format(_SENSORS_ADDR))
    logging.getLogger().debug('_SENSORS_MUX1_ADDR:\t\t{}'.format(hex(_SENSORS_MUX1_ADDR)))
    logging.getLogger().debug('_SENSORS_MUX2_ADDR:\t\t{}'.format(hex(_SENSORS_MUX2_ADDR)))

 # vim: fileencoding=utf-8 filetype=python ts=4 expandtab
