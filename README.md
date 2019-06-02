# Repository for storage temperature humidity monitor

## Installation:
```
git clone https://github.com/kuchosauronad0/sht21pi.git
cd sht21pi
sudo python setup.py install
sudo make install
```


### Usage:
You can run the module with
`python -m sht21pi.core -c /etc/sht21pi/sht21pi.conf`
OR
activate and enable the systemd unit so that it is started after reboot with
`sudo systemctl start sht21pi; sudo systemctl enable sht21pi`

### Troubleshooting:
```
# detect devices:
sudo i2cdetect -y 0
sudo i2cdetect -y 1
# run the unittest:
python -m unittest sht21pi.core
```
