#!/bin/bash

# Define storage folder
STORAGEDIR=/storage
# Create folder
sudo mkdir -p ${STORAGEDIR}

# Create disk space
sudo /usr/local/etc/emulab/mkextrafs.pl -f ${STORAGEDIR}

# Redirect some Docker/k8s dirs into our extra storage.
for dir in docker kubelet ; do
    sudo mkdir -p $STORAGEDIR/$dir /var/lib/$dir
    sudo mount -o bind $STORAGEDIR/$dir /var/lib/$dir
done

sudo chmod -R 777 ${STORAGEDIR}