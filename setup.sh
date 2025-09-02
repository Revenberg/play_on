#!/bin/bash
set -e
#sudo apt update 
#sudo apt upgrade -y 
#sudo apt install -y git curl python3-pip python3-venv ca-certificates gnupg lsb-release
#curl -fsSL https://get.docker.com | sudo sh
#sudo usermod -aG docker $USER
#sudo pip3 install docker-compose

sudo rm -rf play_on 2>/dev/null 
cd ~
git clone --branch release https://github.com/revenberg/play_on.git

cd ~/play_on/docker
docker compose down

cd ~/play_on
cp update.sh ~/update.sh
chmod +x ~/update.sh

TTY_DEV=$(ls /dev/ttyUSB* | head -n 1 || echo "/dev/ttyUSB0")
echo "TTY_DEVICE=$TTY_DEV" > .env

# Haal het IP-adres van de host op
HOST_IP=$(hostname -I | awk '{print $1}')

# Vervang <HOST_IP> in index.html door het werkelijke IP-adres
sed -i "s/<HOST_IP>/$HOST_IP/g" docker/webserver/index.html

cd docker && docker compose up -d --build --remove-orphans
echo "✅ Installatie voltooid"
