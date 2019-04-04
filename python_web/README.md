
## Starting Web
go into folder with main.py
sudo python main.py


## register as service
go into folder with main.py
export p=`pwd`
sudo ln -s ${p}/led.service /etc/systemd/system/led.service

sudo systemctl daemon-reload
sudo systemctl enable led
