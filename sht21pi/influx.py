#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Andre Poley
@contact: andre.poley@mailbox.org
@copyright: (c) 2019 by Andre Poley, Berkeley
@license: MIT
@version: 0.0.5
@summary: Write input data to an influxdb
'''
import socket, sys
import logging
import requests

def prepare_data(log_batch):
    """ Prepare the logged data for a batched influx line interface query
    @param log_batch: A group of comma seperated values
    @type log_batch: [[int][int][float][float]]
    """ 
    data=[]
    for i in range(len(log_batch)):
        data.append('{},host={}-{} temperature={},humidity={} {}'.format(_INFLUX_DATABASE,socket.gethostname(),log_batch[i][1],log_batch[i][2],log_batch[i][3],log_batch[i][0]))
    return data

def post_to_database(args):
    """ Post the batched data to the database
    @param args: prepared data
    @type args: str
    """
    params = (
        ('precision', 's'),
        ('db', '{}'.format(_INFLUX_DATABASE)),
    )
    data = ''
    for i in range(len(args)):
        data = "{}\n{}".format(data,args[i])
    try:
        logging.getLogger().debug("Influx query: {}".format(data))
        response = requests.post('http://{}/write'.format(_INFLUX_SERVER), params=params, data=data, verify=False, auth=('{}'.format(_INFLUX_USER), '{}'.format(_INFLUX_PASSWORD)))
    except requests.exceptions.HTTPError as errh:
        print ("Http Error: {}".format(errh))
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting: {}".format(errc))
    except requests.exceptions.Timeout as errt:
        print("Connection Timout: {}".format(errt))
    except requests.exceptions.TooManyRedirects as errr: 
        print("Too many redirects: {}".format(errr))
    except requests.exceptions.RequestException as e:
        # catastrophic error. bail.
        print e
        sys.exit(1)
    finally:
        logging.getLogger().info("Wrote to influx ")

def debug():
    logging.getLogger().debug("_INFLUX_SERVER\t\t{}".format(_INFLUX_SERVER))
    logging.getLogger().debug("_INFLUX_DATABASE\t\t{}".format(_INFLUX_DATABASE))
    logging.getLogger().debug("_INFLUX_USER\t\t\t{}".format(_INFLUX_USER))
    logging.getLogger().debug("_INXLUX_PASSWORD\t\t{}".format(_INFLUX_PASSWORD))
