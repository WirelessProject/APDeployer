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
1. Copy `env.example` to `.env`
2. Set your management vlan and ZoneDirector controller IP in the `.env`.
3. Manully change IP to 192.168.0.x then ssh 192.168.0.1
4. Modify env.example 
	(1) ZONEDIRECTOR_IP = 10.3.7.253 
	(2) AP_MGNT_VLAN = 4
	(3) AP_GATEWAY_IP = 10.3.7.254
5. Run python ap.init.trunk.py (enter last 3 digits of product number)
6. To check if ap is set up successfully just manully change your IP to the same subnet of ap and remember to ssh AP with vlan4
