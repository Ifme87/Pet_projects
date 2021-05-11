#!/usr/bin/env python3

import ipaddress

ip = input('Enter IPv6 to parse: ')
domain_name = input('Enter domain name: ')
ip_formatted = ipaddress.ip_address(ip).reverse_pointer
result = "{}. IN PTR {}.".format(ip_formatted, domain_name)

print('\n' + result + '\n')
