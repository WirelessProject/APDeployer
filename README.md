# APDeployer
Script for deploying ZoneFlex AP configurations

Requirements
------------
+ python3
+ python3-pip

Install
-------
```
pip3 install -r requirements.txt
```

Setup
-----
1. Hard reset AP by pressing reset button for longer than six seconds
2. Copy `env.example` to `.env`
3. Modify `.env`: 
	(1) ZONEDIRECTOR_IP = 10.3.7.253 
	(2) AP_MGNT_VLAN = 4
	(3) AP_GATEWAY_IP = 10.3.7.254
4. Manully change your machine's IP to 192.168.0.x and set the netmask to 255.255.255.0
5. Run `python ap.init.trunk.py DEVICE_NAME LAST_3_DIGITS_OF_PRODUCT_NUMBER`
6. To check if ap is set up successfully just manully change your IP to the same subnet of ap and remember to ssh AP with vlan4
