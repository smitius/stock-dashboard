stock-dashboard: dash app to visualize daily stock values

How to run locally on server:

gunicorn index:application --bind=0.0.0.0:80

Startup in jail after start:

chmod 777 /usr/local/etc/rc.d/stock echo 'stock_enable="YES"' >> /etc/rc.conf service stock start

Startup script:

#!/bin/sh

. /etc/rc.subr

GUNICORN=/usr/local/bin/gunicorn ROOT=/root/stockapp

name=stock rcvar=stock_enable

start_cmd="${name}_start" stop_cmd=":"

load_rc_config $name

stock_start() { cd $ROOT exec $GUNICORN index:application --bind=0.0.0.0:80 --daemon & }

run_rc_command "$1"
