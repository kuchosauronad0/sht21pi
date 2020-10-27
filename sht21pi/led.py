#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Andre Poley
@contact: andre.poley@mailbox.org
@copyright: (c) 2019 by Andre Poley, Berkeley
@license: MIT
@version: 0.0.3
@summary: Class to update the ws2811x GRB leds. Needs privileged hardware access or else will cause Error -9.
'''
import sys
import time
import logging

import _rpi_ws281x as ws

_LED_CHANNEL    = 0
_LED_COUNT      = 4         # How many LEDs to light.
_LED_FREQ_HZ    = 800000    # Frequency of the LED signal.  Should be 800khz or 400khz.
_LED_DMA_NUM    = 10        # DMA channel to use, can be 0-14.
_LED_GPIO       = 18        # GPIO connected to the LED signal line.  Must support PWM!
_LED_BRIGHTNESS = 63        # Set to 0 for darkest and 255 for brightest
_LED_INVERT     = 0         # Set to 1 to invert the LED signal, good if using NPN
_LED_COLOURS_LIST = [0x000000, 0x050000, 0x101000, 0x006463]  # Colours are GRB
_LEDS_HUMIDITY_THRESHOLD = float(1.)


class Argospi2cWS2811x:

    def __init__(self):
        self.debug()

    def get_channel(self):
        return _LED_CHANNEL

    def get_count(self):
        return _LED_COUNT

    def get_freq(self):
        return _LED_FREQ_HZ

    def get_dma(self):
        return _LED_DMA_NUM

    def get_gpio(self):
        return _LED_GPIO

    def get_brightness(self):
        return _LED_BRIGHTNESS

    def get_invert(self):
        return _LED_INVERT

    def get_color(self, color):
        return _LED_COLOURS_LIST[color]

    def set_leds(self, status):
        """ Set the color according to the humidity threshold
        In the optimal state when no threshold is reached the
        led is turned off.
        @param status: An integer array with 4 integers between 0 and 4
        @type status: int[4]
        @return: None
        """
        leds = ws.new_ws2811_t()
        channel = ws.ws2811_channel_get(leds, self.get_channel())
        ws.ws2811_channel_t_count_set(channel, self.get_count())
        ws.ws2811_channel_t_gpionum_set(channel, self.get_gpio())
        ws.ws2811_channel_t_invert_set(channel, self.get_invert())
        ws.ws2811_channel_t_brightness_set(channel, self.get_brightness())
        ws.ws2811_t_freq_set(leds, self.get_freq())
        ws.ws2811_t_dmanum_set(leds, self.get_dma())
        try:
            resp = ws.ws2811_init(leds)
        except Exception as err:
            raise RuntimeError('ws2811_init failed with code {0} ({1}) {}', resp, err)
        finally:
            if resp != ws.WS2811_SUCCESS:
                ws.ws2811_get_return_t_str(resp)
        try:
            for i in range(self.get_count()):
                ws.ws2811_led_set(channel, i, self.get_color(status[i]))
            resp = ws.ws2811_render(leds)
            if resp != ws.WS2811_SUCCESS:
                ws.ws2811_get_return_t_str(resp)
            time.sleep(0.015)
        except Exception as err:
            raise RuntimeError('ws2811_render failed with code {0} ({1})'.format(resp, err))
        finally:
            logging.getLogger().info("LED status:\t\t\t{}".format(status))
            ws.ws2811_fini(leds)
            ws.delete_ws2811_t(leds)

    def debug(self):
        """ Print configuration to application log if debug level is set to DEBUG
        @return: None
        """
        logging.getLogger().debug('LEDS_HUMIDITY_THRESHOLD:\t{}'.format(_LEDS_HUMIDITY_THRESHOLD))
        logging.getLogger().debug('_LED_CHANNEL\t\t\t{}'.format(_LED_CHANNEL))
        logging.getLogger().debug('_LED_COUNT\t\t\t{}'.format(_LED_COUNT))
        logging.getLogger().debug('_LED_GPIO\t\t\t{}'.format(_LED_GPIO))
        logging.getLogger().debug('_LED_INVERT\t\t\t{}'.format(_LED_INVERT))
        logging.getLogger().debug('_LED_BRIGHTNESS\t\t{}'.format(_LED_BRIGHTNESS))
        logging.getLogger().debug('_LED_FREQ_HZ\t\t\t{}'.format(_LED_FREQ_HZ))
        logging.getLogger().debug('_LED_DMA_NUM\t\t\t{}'.format(_LED_DMA_NUM))


def main():
    """
    Test the led if the method is called outside of the core module.
    The color array has one extra color.
    """
    try:
        status = [0, 1, 2, 3]
        ledTest = Argospi2cWS2811x()
        ledTest.set_leds(status)
    except IOError as e:
        print("I/OError: {}".format(e))
    except Exception:
        print("Unexpected Error:", sys.exc_info()[0])
        raise


if __name__ == "__main__":
    main()

# vim: fileencoding=utf-8 filetype=python ts=4 expandtab
