#!/usr/bin/env python3

from pexpect import pxssh
import argparse
import pexpect
import sys

# For reading configuration file.
import os
from dotenv import Dotenv


class ApInit:
    def __init__(self):
        # Loads configuration file.

        dotenv = Dotenv(os.path.join(os.path.dirname(__file__), ".env"))
        os.environ.update(dotenv)

        self.ap_target = os.environ.get("AP_IP")
        self.ZD_IP = os.environ.get("ZONEDIRECTOR_IP")
        self.gateway = os.environ.get("AP_GATEWAY_IP")
        self.vlan = int(os.environ.get("AP_MGNT_VLAN"))
        self.username = os.environ.get("AP_USERNAME")
        self.passwd = os.environ.get("AP_PASSWORD")

        parser = argparse.ArgumentParser(
            description="Deploy ZoneFlex AP configurations"
        )
        parser.add_argument(
            "name",
            type=str,
            help="Device name"
        )
        parser.add_argument(
            "identifier",
            type=int,
            help="Product Number last 3 digits"
        )
        args = parser.parse_args()

        # Handles product ID and transfer to IP.
        self.name = args.name
        self.ID = args.identifier
        self.IDtoIP()

        print("AP target:", self.ap_target)
        print("Zone director:", self.ZD_IP)
        print("Vlan:", self.vlan)
        print("Assigned IP:", self.IP)

    def run(self):
        with pexpect.spawn(
            "ssh -o StrictHostKeyChecking=no %s" % self.ap_target
        ) as ssh:
            # Real login here.
            ssh.expect([ "login" ])
            ssh.sendline(self.username)
            ssh.expect([ "password" ])
            ssh.sendline(self.passwd)

            # Sets up interface.
            ssh.expect([ "rkscli:" ])
            ssh.sendline("set interface eth0 type vlan-trunk untag 1")
            ssh.expect([ "OK" ])

            ssh.expect([ "rkscli:" ])
            ssh.sendline("set interface eth1 type vlan-trunk untag 1")
            ssh.expect([ "OK" ])

            ssh.expect([ "rkscli:" ])
            ssh.sendline("set director ip %s" % self.ZD_IP)
            ssh.expect([ "OK" ])

            ssh.expect([ "rkscli:" ])
            ssh.sendline(
                "set ipaddr wan vlan %d %s 255.255.248.0 %s"
                % (self.vlan, self.IP, self.gateway)
            )
            ssh.expect([ "OK" ])

            ssh.expect([ "rkscli:" ])
            ssh.sendline("set ipmode wan ipv4")
            ssh.expect([ "OK" ])

            ssh.expect([ "rkscli:" ])
            ssh.sendline("set director ip %s" % self.ZD_IP)
            ssh.expect([ "OK" ])

            ssh.expect([ "rkscli:" ])
            ssh.sendline("set device-name %s" % self.name)
            ssh.expect([ "OK" ])

            ssh.expect([ "rkscli:" ])
            ssh.sendline("reboot")
            ssh.expect([ "OK" ])

            print('The AP has been rebooted')

            pexpect.spawn("ssh-keygen -R %s" % self.ap_target).close()

    def IDtoIP(self):
        div = 8 + self.ID // 256
        remainder = self.ID % 256
        self.IP = "10.3.%d.%d" % (div, remainder)


if __name__ == '__main__':
    initer = ApInit()
    initer.run()

