#!/usr/bin/env python3

import pexpect
from pexpect import pxssh
import sys

# For reading configuration file.
import os
from dotenv import Dotenv 



class ApInit:
    def __init__ (self):
        # Loads configuration file.

        dotenv = Dotenv(os.path.join(os.path.dirname(__file__), ".env"))
        os.environ.update(dotenv)

        self.ap_target = os.environ.get("TARGET")
        self.dns = [os.environ.get("DNS1"), os.environ.get("DNS2")]
        self.ZD_IP = os.environ.get("ZD_IP") 
        self.vlan = os.environ.get("VLAN")
        self.username = os.environ.get("USER")
        self.passwd = os.environ.get("PASSWORD")

        print("AP target:", self.ap_target)
        print("DNS:", self.dns)
        print("Zone director:", self.ZD_IP)
        print("Vlan:", self.vlan)

        # Handles product ID and transfer to IP.
        if (len(sys.argv) != 2) or (len(sys.argv[1]) != 3):
            print("Usage: ap.set.exp [Product Number last 3 digits]")
            print("ex: ./$SCRIPT 937")
            sys.exit(1)

        self.ID = int(sys.argv[1])
        self.IDtoIP()
        print("IP:", self.IP)

    def run(self):
        keygen = pexpect.spawn("ssh-keygen -R %s" % self.ap_target)
        keygen.close

        try:
            ssh = pexpect.spawn("ssh %s" % self.ap_target)
            ssh.expect(["established"])
            ssh.sendline("yes")
            # Not actually login.

            # Real login here.
            ssh.expect([ "login" ])
            ssh.sendline(self.username)
            ssh.expect([ "password" ])
            ssh.sendline(self.passwd)

            # Sets up interface.
            ssh.expect([ "rkscli:" ])
            ssh.sendline("set interface eth0 type vlan-trunk untag 1")
            print(ssh.after)

            ssh.expect([ "rkscli:" ])
            ssh.sendline("set interface eth1 type vlan-trunk untag 1")
            print(ssh.after)

            # Sets up DNS, ZD and other informations.
            ssh.expect([ "rkscli:" ])
            ssh.sendline([ "set dns %s" % " ".join(self.dns) ])
            print(ssh.after)

            ssh.expect([ "rkscli:" ])
            ssh.sendline("set device-location 3140403020%d" % self.ID)

            ssh.expect([ "rkscli:" ])
            ssh.sendline("set director ip %s" % self.ZD_IP)

            ssh.expect([ "rkscli:" ])
            ssh.sendline("set ipmode wan ipv4")

            ssh.expect([ "rkscli:" ])
            ssh.sendline(
                "set ipaddr wan vlan %d %s 255.255.248.0 10.3.7.254"
                % (self.vlan, self.IP)
            )

            ssh.expect([ "rkscli:" ])
        except:
            print("Exception was thrown")
            print(str(ssh))


    def IDtoIP(self):
        div = 8 + self.ID // 256
        remainder = self.ID % 256
        self.IP = "10.3.%d.%d" % (div, remainder)


if __name__ == '__main__':
    initer = ApInit()
    initer.run()

