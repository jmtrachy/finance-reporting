#!/bin/bash

echo "Adding openjdk repository"
sleep 1.5
add-apt-repository -y ppa:openjdk-r/ppa

echo "Adding elastic search repository"
sleep 1.5
echo "deb https://packages.elastic.co/elasticsearch/2.x/debian stable main" | sudo tee -a /etc/apt/sources.list.d/elasticsearch-2.x.list

echo "Adding kibana repository"
sleep 1.5
echo "deb http://packages.elastic.co/kibana/4.5/debian stable main" | sudo tee -a /etc/apt/sources.list

echo "Updating apt-get"
sleep 1.5
apt-get update

echo "Installing java"
sleep 1.5
apt-get install -y --force-yes openjdk-8-jdk
java -version

echo "Installing elasticsearch"
sleep 1.5
apt-get install -y --force-yes elasticsearch

echo "Installing kibana"
sleep 1.5
apt-get install -y --force-yes kibana

echo "Updating rc.d"
sleep 1.5
update-rc.d elasticsearch defaults 95 10
update-rc.d kibana defaults 95 10

echo "Starting elasticsearch"
sleep 1.5
service elasticsearch start

echo "Starting kibana"
sleep 1.5
service kibana start

echo "Adding iptable for port 80"
sleep 1.5
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-ports 5601

echo "exiting bootstrap...."
echo "Don't forget to vi /etc/elasticsearch/elasticsearch.yml, uncomment network.host and set it to _eth0_"
