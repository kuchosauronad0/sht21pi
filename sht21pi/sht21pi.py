#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Andre Poley
@contact: andre.poley@mailbox.org
@copyright: (c) 2019 by Andre Poley, Berkeley
@license: MIT
@version: 0.0.5
@summary: This module reads up to 16 i2c devices which are sht21 sensors in this case and drives 4 ws2811 leds as visual indicators. Can log to disk and/or influxdb. Once an object is created the configfile will be read, then data for the specified sensors will be collected and lastly the batched data will be logged and/or sent to an influxdb.
'''
import sys,os,logging,time,getopt
import smbus,nclib

import configparser

import helpers
import i2c
import led
import influx

class StorageHumidityMonitor(object):
    """
    This class makes use of 'I2C Humidity Sensors to Raspberry Pi'-Shield  made 
    by Carlos García Argos, Uni Freiburg.    Up  to  16  sensors   can  be read
    with the data either being written to disk or send to an influxdb.
    To  keep  things tidy  the  other methods are defined in their corresponding
    files: {led,i2c,influx}.py

    Resources: 
      http://www.sensirion.com/fileadmin/user_upload/customers/sensirion/Dokumente/Humidity/Sensirion_Humidity_SHT21_Datasheet_V3.pdf
      https://github.com/jaques/sht21_python/blob/master/sht21.py
      Martin Steppuhn's code from http://www.emsystech.de/raspi-sht21
    """

    _LOG_NAME = 'sht21-application.log'
    _TEMPERATURE = []
    _HUMIDITY = []

    def __init__(self, bus_nr):
        """ 
        @param bus_nr: Bus number used on this board. Can be 0 or 1. Default is 1 for raspberry pi.
        @type bus_nr: int
        @summary: Sensors 1-8 use mux1 and 9-16 use mux2. Which one to use is defined
        in the selectMuxOut function with the address for mux2 being substracted by 8
        as to match the analog and digital addresses(9-16 are known as 1-8 to mux2).
        """ 
        configfile = 'sht21pi.conf'
        self._get_configuration()
        i2c._SENSORS_ADDR = []
        logging.basicConfig(filename='{}/{}'.format(self._LOG_DIR,self._LOG_NAME), level=self._LOG_LEVEL)
        self._softreset(bus_nr)
        for i in range(1, 17):
            if ((i2c._SENSORS_PRESENT >> (i - 1))&0x1) == 1:# Add existing sensors to Array _SENSORS_ADDR
               i2c._SENSORS_ADDR.append(i)

    def _softreset(self,bus_nr="1"):
        """
        @param bus_nr: default bus is 1 on this board.
        @type bus_nr: int 
        """
        try: # Soft reset the bus
            i2c.bus = smbus.SMBus(int(bus_nr))
            i2c.bus.write_byte(i2c._I2C_ADDRESS, i2c._SOFTRESET) 
            time.sleep(0.015)
        except IOError as err:
            logging.getLogger().error("Error during initialization: {}".format(err), exc_info=False)
            pass
        except Exception as ere:
            raise Exception("Unexpected Exception {}".format(ere))


    def _get_configuration(self):
        """Try to open a configuration file passed as an argument and fallback
        to the default if none was passed.
        """
        try:# Abort if -c option is used without a filename
            opts, args = getopt.getopt(sys.argv[1:], "c:")
        except getopt.GetoptError as err:
            logging.getLogger().error("Usage: Missing argument -c. Ensure -c file exists", exc_info=False)
            sys.exit(1)
        try: # Open default or -c configuration file
            for opt, arg in opts:
                if opt == '-c':
                    configfile = arg
            with open(configfile) as file:
                pass
        except Exception as e:
            logging.getLogger().error("Unable to open configuration file {}".format(e), exc_info=False)
            raise Exception("Cannot read configuration file {}".format(e),exc_info=False)
            sys.exit(1)
        finally:
           logging.getLogger().info("Got configuration {}".format(configfile) , exc_info=False)
           self._read_configuration(configfile)

    def _read_configuration(self,configfile):
        """Parse a config file
        @param configfile: A file formated for python's configparser
        @type configfile: configuration file
        """
        config = configparser.ConfigParser()
        try:
            config.read(configfile)
            self._INFLUX_ENABLED = helpers.to_bool(config['INFLUX']['enabled']) 
            self._LEDS_ENABLED = helpers.to_bool(config['LEDS']['enabled'])
            self._LOG_FILE = str(config['CONFIGURATION']['log_directory']) + str(config['CONFIGURATION']['log_file'])
            self._LOG_DIR = str(config['CONFIGURATION']['log_directory'])
            self._LOG_ENABLED = helpers.to_bool(config['CONFIGURATION']['log_enabled'])
            self._LOG_LEVEL = str(config['CONFIGURATION']['log_level'])
            i2c._SENSORS_PRESENT = int(config['SENSORS']['present'], 16)
            i2c._SENSORS_MUX1_ADDR = int(config['SENSORS']['mux1_addr'], 16)
            i2c._SENSORS_MUX2_ADDR = int(config['SENSORS']['mux2_addr'], 16)
            led._LEDS_HUMIDITY_THRESHOLD = float(config['LEDS']['humidity_threshold'])
            influx._INFLUX_SERVER = str(config['INFLUX']['server'])
            influx._INFLUX_DATABASE = str(config['INFLUX']['database'])
            influx._INFLUX_USER = str(config['INFLUX']['user'])
            influx._INFLUX_PASSWORD = str(config['INFLUX']['password'])
            logging.getLogger().info("Configuration is done", exc_info=False)
        except KeyError as e:
            raise KeyError("Configuration is missing key {}".format(e))
        try:
            if (influx._INFLUX_USER == 'invalid') and (self._INFLUX_ENABLED):
                sys.exit(1)
        except:
            raise Exception("Please configure the influx username and password before using this software.")

    def __enter__(self):
        """used to enable python's with statement support"""
        return self

    def __exit__(self, type, value, traceback):
        """with support"""
        self.close()

    def close(self):
        """Closes the i2c connection"""
        i2c.bus.close()


    def write_log(self, message):
        """Write to data log
        @param message: An array with sensors readings to be written to the data log.
        @type message: [[int, int, float, float]]
        @return: None
        """
        try:
            fp = open(self._LOG_FILE, 'a')
            for i in range(len(message)) :  
                fp.write("{}, {}, {}, {}\n".format(message[i][0],message[i][1],message[i][2],message[i][3]))
        except IOError as e:
            raise IOError("Cannot access file {}".format(e), exc_info=True)
        finally:
            fp.close()
            logging.getLogger().info("Wrote log", exc_info=False)

    def run(self):
        """
        Run the main loop. Log to application log if debug level is DEBUG.
        Then write to database, log to file, check humidity treshold, update leds. 
        """
        self.debug()
        try:
            log_batch = []
            status = [ 0 ] * led._LED_COUNT

            for i in i2c._SENSORS_ADDR: # Acquire sensor data
                data = i2c.read_i2c_addr(i)
                log_batch.append(data)

            if data[3] > led._LEDS_HUMIDITY_THRESHOLD: # Update the treshold status 
                    status[i%(led._LED_COUNT)] += 1

            if self._LEDS_ENABLED: # Update the leds according to treshold status
                logging.getLogger().info("Updating LEDs", exc_info=False)
                indicator = led.Argospi2cWS2811x()
                indicator.set_leds(status)

            if self._INFLUX_ENABLED: # Write to database
                logging.getLogger().info("Contacting influx", exc_info=False)
                data = influx.prepare_data(log_batch)
                influx.post_to_database(data)

            if self._LOG_ENABLED: # Write to local logfile
                logging.getLogger().info("Log file enabled", exc_info=False)
                helpers.write_log(self._LOG_FILE,log_batch)
        except IndexError:
            logging.getLogger().error("Index out of range.", exc_info=True)
        except IOError, e:
            logging.getLogger().error("Failed to connect to i2c.", exc_info=True)

    def debug(self):
        ''' Print configuration to application log if debug level is set to DEBUG
        @return: None
        '''
        logging.getLogger().debug('\nLOG_ENABLED:\t\t{}'.format(self._LOG_ENABLED))
        logging.getLogger().debug('LOG_FILE:\t\t\t{}'.format(self._LOG_FILE))
        logging.getLogger().debug('LOG_LEVEL:\t\t\t{}'.format(self._LOG_LEVEL))
        logging.getLogger().debug('LEDS_ENABLED:\t\t{}'.format(self._LEDS_ENABLED))
        logging.getLogger().debug('INFLUX_ENABLED:\t\t{}'.format(self._INFLUX_ENABLED))
        i2c.debug()
        influx.debug()

# vim: fileencoding=utf-8 filetype=python ts=4 expandtab
