#!/bin/bash
mkdir -p /media/ramdisk/hkclient
cd /media/ramdisk/hkclient; ls -t | tail -n +1234 | xargs -I {} rm {}
sleep 0.1
cd /root
running=`ps -ax | grep -v grep | grep "python" | grep "surveillance.py" | wc -l`
if [ $running -eq 0 ]; then
	echo "Process is not running. "
	./hkclient.py >/dev/null 2>&1 &
fi
