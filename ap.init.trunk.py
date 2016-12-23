#!/usr/bin/env python3

from pexpect import pxssh
import argparse
import pexpect
import sys
import hmac
import re

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
        self.lock_secret = os.environ.get("LOCK_SECRET")
        self.lock_digits = int(os.environ.get("LOCK_DIGITS"))

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
            type=str,
            help="Product Number last 3 digits"
        )
        args = parser.parse_args()

        # Handles product ID and transfer to IP.
        self.name = args.name
        self.ID = args.identifier
        assert re.search('^\d{3}$', self.ID), 'Incorrect identifier format'
        self.IDtoIP()

        print("AP target:", self.ap_target)
        print("Zone director:", self.ZD_IP)
        print("Vlan:", self.vlan)
        print("Assigned device name:", self.name)
        print("Assigned IP:", self.IP)
        print("Lock password", self.GenPassword())

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
        id_num = int(self.ID, 10)
        div = 8 + id_num // 256
        remainder = id_num % 256
        self.IP = "10.3.%d.%d" % (div, remainder)

    def GenPassword(self):
        assert self.lock_digits <= 154
        password = ('%0155d' % (int(hmac.new(
            key=self.lock_secret.encode('utf-8'),
            msg=self.ID.encode('utf-8'),
            digestmod='sha512'
        ).hexdigest(), 16)))[-self.lock_digits:]
        return password


if __name__ == '__main__':
    initer = ApInit()
    initer.run()

