help:
	@echo "    clean-pyc"
	@echo "        Remove python artifacts."
	@echo "    clean-build"
	@echo "        Remove build artifacts."
	@echo "    clean-module"
	@echo "        Remove etc and systemd artifacts from system."
	@echo "    test"
	@echo "        Run py.test"
	@echo "    run"
	@echo "        Run the sht21pi module on your local machine."

init:
	pip install -r requirements.txt
install:
	python setup.py install
	mkdir /etc/sht21pi
	mkdir /var/log/sht21pi
	cp sht21pi/config/sht21pi.conf /etc/sht21pi
	cp sht21pi/config/sht21pi.service /usr/lib/systemd/system/
	cp sht21pi/config/sht21pi.timer /usr/lib/systemd/system/
run:
	python2.7 -m sht21pi.core -c /etc/sht21pi/sht21pi.conf

clean-pyc:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	name '*~' -exec rm --force  {} 

clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

clean-module:
	rm -rf /etc/sht21pi
	rm /usr/lib/systemd/system/sht21pi.service
	rm /usr/lib/systemd/system/sht21pi.timer 
test:
	py.test tests
