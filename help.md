# HELP
All you need to setup your own ransomware analysis tool.

## How to Install and run Cuckoo Sandbox
- Cuckoo Docs:
```https://cuckoo.readthedocs.io/en/latest/```
- Complete guide for setting up and running Cuckoo sandbox locally:
```https://beginninghacking.net/2022/11/16/how-to-setup-your-own-malware-analysis-box-cuckoo-sandbox/```

## Troubleshooting
- Cannot start nested win7 VM in Ubuntu VM
```https://forums.virtualbox.org/viewtopic.php?t=87752``` 
- Setup VirtualBox to be able to communicate with the Cuckoo API from teh host machine:
```https://stackoverflow.com/questions/31922055/bridged-networking-not-working-in-virtualbox-under-windows-10```


## For ME
workon sandbox
vmcloak-vboxnet0
sudo sysctl -w net.ipv4.conf.enp0s3.forwarding=1
sudo iptables -t nat -A POSTROUTING -o enp0s3 -s 192.168.56.0/24 -j MASQUERADE
sudo iptables -P FORWARD DROP
sudo iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT
sudo iptables -A FORWARD -s 192.168.56.0/24 -j ACCEPT


Open terminator and split into 4 windows
in all windows -  workon sandbox
window 1 - cuckoo rooter --sudo --group osboxes
window 2 - cuckoo
window 3 - cuckoo web --host 127.0.0.1 --port 8080


C:\Users\ken20\Downloads\7z2406-x64.exe
/home/osboxes/Downloads/winrar-x64-701.exe

- Shared folder:
```https://www.makeuseof.com/how-to-create-virtualbox-shared-folder-access/```
