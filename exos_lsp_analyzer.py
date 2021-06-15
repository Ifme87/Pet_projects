#!/usr/bin/env python3

import subprocess
import sys
import re
import time
from pprint import pprint

#/work/netconf/save/

def vpn(node, vpn_name):
	directory = f'~/Downloads/{node}.cfg'
	'''regular expressions'''
	regex_ip = re.compile('.*peer ((\w+.){3}(\w+))')
	regex_lsp = re.compile('.* lsp "(\S+)" .*')
	'''generate strings with peers of VPN'''
	peers = subprocess.run([f'grep " l2vpn.* {vpn_name} .*peer" {directory}'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')
	peers = peers.stdout.split('\n')
	'''eject dest IPs from strings'''
	dest_ips_of_vpn = []
	for i in peers:
		match_peer = re.match(regex_ip, i)
		if match_peer:
			dest_ips_of_vpn.append(match_peer.group(1))
	dest_ips_of_vpn = set(dest_ips_of_vpn)
	'''resolve unique dest IPs into LSPs'''
	lsps_of_vpn = []
	for dest_ip in dest_ips_of_vpn:
		out = subprocess.run([f'grep "rsvp-te.*destin" {directory} | grep "{dest_ip}"'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')
		out = out.stdout.split('\n')
		for lsp_vpn in out:
			match_lsp = re.match(regex_lsp, lsp_vpn)
			if match_lsp and transport_check(match_lsp.group(1), vpn_name):
				lsps_of_vpn.append(match_lsp.group(1))
	'''generate tree of VPNs LSPs > PATHs > Hops'''
	result_vpn = dict()
	for lsps in lsps_of_vpn:
		result_vpn.update(lsp(node, lsps))
	return result_vpn

'''check if lsp "transport vpn-traffic allow assigned-only"'''
def transport_check(lsp_name, vpn_name):
	directory = f'~/Downloads/{node}.cfg'
	out = subprocess.run([f'grep \"{lsp_name}\" {directory} | grep "transport vpn"'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')	
	out2 = subprocess.run([f'grep {vpn_name} {directory} | grep "add mpls lsp {lsp_name}"'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')	
	if out.stdout and not out2.stdout:
		return False
	else:
		return True
		
		
def lsp(node, lsp_name):
	directory = f'~/Downloads/{node}.cfg'
	regex_path = re.compile('.*add path "*(\S+?)"* .*')
	'''generate strings with LSP'''
	out = subprocess.run([f'grep \"{lsp_name}\" {directory}'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')	
	out = out.stdout.split('\n')
	'''eject PATH names from strings'''
	paths = []
	for path1 in out:
		match = re.match(regex_path, path1)
		if match:
			paths.append(match.group(1))
	'''generate tree LSPs > PATHs > hops'''
	result = {}
	for path1 in paths:
		hops = path(node, path1)
		result[path1] = hops
	lsp = {}
	lsp[lsp_name] = result	
	return lsp

	
def path(node, path_name):
	directory = f'~/Downloads/{node}.cfg'
	regex_hops = re.compile('.*ero include ((\w+.){3}(\w+))\/(\w+) .*(order \w+)')
	hops_path = subprocess.run([f'grep " rsvp-te.*add ero " {directory} | grep " {path_name} "'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')
	hops_path = hops_path.stdout.split('\n')
	hops_to_resolve = []
	for hop in hops_path:	
		match_hop = re.match(regex_hops, hop)
		if match_hop:
			hops_to_resolve.append(match_hop.group(1))
	return resolve_ip(node, hops_to_resolve)
	
		
def resolve_ip(node, ips_to_resolve):
	directory = f'~/Downloads/{node}.cfg'
	regex_name = re.compile('.*pointer (\S+?-\S+?-\S+?..)')
	regex_lo0 = re.compile('.*lo0 ipaddress ((\w+.){3}(\w+)).*')
	hops_resolved = []			
	for ip in ips_to_resolve:
		domain_name = subprocess.run([f'host {ip}'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')
		time.sleep(0.1)
		match_dn = re.match(regex_name, domain_name.stdout)
		if match_dn:
			lo0 = subprocess.run([f'grep "lo0 ipaddress" ~/Downloads/{match_dn.group(1)}.cfg'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')
			match_lo0 = re.match(regex_lo0, lo0.stdout)
			hops_resolved.append(f'{match_dn.group(1)}, hop {ip}, lo0 {match_lo0.group(1)}')
		else:
			hops_resolved.append(f'no name, hop {ip}')
	return hops_resolved
	

if __name__ == "__main__":
	'''
	Info:
	
	Arg 1: Switch name
	Arg 2: Analysed object
		-'v' is for VPN
		-'l' is for LSP
		-'p' is for PATH
	Arf 3: Object name
	Names should be FULL
	==============================
	-check vpn section (too long)
	-add extended mode (to check ldp)
	-add cisco and juniper
	-add option 'all lsps/paths'
	'''
	 
	node = sys.argv[1]
	obj_for_analisys = sys.argv[2]
	obj_name = sys.argv[3]

	
	if obj_for_analisys == 'v':
		if obj_name == 'a':
			print("Key 'all' for LSPs and PATHs only ")
		else:
			pprint(vpn(node, obj_name), width=120)
	if obj_for_analisys == 'l':
		if obj_name == 'a':
			pass
			#make 'all' option
		else:
			pprint(lsp(node, obj_name), width=120)
	if obj_for_analisys == 'p':
		if obj_name == 'a':
			pass
			#make all option
		else:
			pprint(path(node, obj_name), width=120)
