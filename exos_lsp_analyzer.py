#!/usr/bin/env python3

import subprocess
import sys
import re
from pprint import pprint


def vpn_or_all(node, vpn_name):
	'''regular expressions'''
	regex_ip = re.compile('.* (peer|destination) ((\w+.){3}(\w+))')
	regex_lsp = re.compile('.* lsp "(\S+)" .*')
	if vpn_name == 'a':
		'''generate strings with all peers'''
		peers = subprocess.run([f'grep "rsvp-te.*destin" {directory}{node}.cfg'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')
		peers = peers.stdout.split('\n')
	else:
		'''generate strings with peers of VPN'''
		peers = subprocess.run([f'grep " l2vpn.* {vpn_name} .*peer" {directory}{node}.cfg'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')
		peers = peers.stdout.split('\n')
	'''eject dest IPs from strings'''
	destination_ips = set()
	for i in peers:
		match_peer = re.match(regex_ip, i)
		if match_peer:
			destination_ips.add(match_peer.group(2))
	'''resolve unique dest IPs into LSPs and generate tree for VPN'''
	res_lsps = {}
	for destination_ip in destination_ips:
		dest_ip = destination_ip
		out = subprocess.run([f'grep "rsvp-te.*destin" {directory}{node}.cfg | grep "{dest_ip}"'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')
		if not out.stdout:
			print(f'Destination {dest_ip} via LDP')
			continue
		out = out.stdout.split('\n')
		'''generate tree for VPN'''
		for lsp_string in out:
			match_lsp = re.match(regex_lsp, lsp_string)
			if vpn_name == 'a' and match_lsp: 
				res_lsps.update(lsp(node, match_lsp.group(1)))
			elif match_lsp and transport_check(match_lsp.group(1), vpn_name, dest_ip):
				res_lsps.update(lsp(node, match_lsp.group(1)))
	if res_lsps:
		return res_lsps			


'''check if lsp "transport vpn-traffic allow assigned-only"'''
def transport_check(lsp_name, vpn_name, dest_ip):
	condition1 = subprocess.run([f'grep "\\"{lsp_name}\\"" {directory}{node}.cfg | grep "transport vpn"'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')	
	condition2 = subprocess.run([f'grep \" {vpn_name} \" {directory}{node}.cfg | grep "{dest_ip} add mpls lsp {lsp_name}$"'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')
	condition3 = subprocess.run([f'grep \" {vpn_name} \" {directory}{node}.cfg | grep "{dest_ip} add mpls lsp"'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')
	if condition1.stdout and not condition2.stdout:
		return False
	elif not condition1.stdout and not condition2.stdout and condition3.stdout:
		return False
	else:
		return True
		
		
def lsp(node, lsp_name):
	regex_path = re.compile('.*add path "*(\S+?)"* (\S+)')
	'''generate strings with LSP'''
	out = subprocess.run([f'grep "\\"{lsp_name}\\"" {directory}{node}.cfg'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')
	out = out.stdout.split('\n')
	'''eject PATH names from strings'''
	paths = []
	for path1 in out:
		match = re.match(regex_path, path1)
		if match:
			if match.group(2) == 'primary':
				paths.append('*' + match.group(1))
			else:
				paths.append(match.group(1))
	'''generate tree LSPs > PATHs > hops'''
	result = {}
	for path1 in paths:
		hops = path(node, path1)
		result[path1] = hops
	lsp_res = {}
	lsp_res[lsp_name] = result	
	return lsp_res

	
def path(node, path_name):
	regex_hops = re.compile('.*ero include ((\w+.){3}(\w+))\/(\w+) .*(order \w+)')
	hops_path = subprocess.run([f'grep " rsvp-te.*add ero " {directory}{node}.cfg | grep " {path_name} "'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')
	hops_path = hops_path.stdout.split('\n')
	hops_to_resolve = []
	for hop in hops_path:	
		match_hop = re.match(regex_hops, hop)
		if match_hop:
			hops_to_resolve.append(match_hop.group(1))
	return resolve_ip(node, hops_to_resolve)
	
		
def resolve_ip(node, ips_to_resolve):
	regex_name = re.compile('.*pointer (\S+?-\S+?-\S+?..)')
	regex_lo0 = re.compile('.*lo0 ipaddress ((\w+.){3}(\w+)).*')
	hops_resolved = []			
	for ip in ips_to_resolve:
		domain_name = subprocess.run([f'host {ip}'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')
		match_dn = re.match(regex_name, domain_name.stdout)
		if match_dn:
			lo0 = subprocess.run([f'grep "lo0 ipaddress" {directory}{match_dn.group(1)}.cfg'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')
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
		-'a' is for all LSPs analysis
 		-'v' is for VPN analysis
		-'l' is for LSP analysis
		-'p' is for PATH analysis
	Arg 3: Object name
	
	Names should be FULL!
	'''
	
	'''Node configs dir: '''
	node = ''
	#directory = '/work/netconf/save/'
	directory = '~/Downloads/'
	'''End'''
	
	node = sys.argv[1]
	obj_for_analisys = sys.argv[2]
	if not obj_for_analisys == 'a':
		obj_name = sys.argv[3]

	if obj_for_analisys == 'a':
		pprint(vpn_or_all(node, 'a'), width=120)
	if obj_for_analisys == 'v':
		pprint(vpn_or_all(node, obj_name), width=120)
	if obj_for_analisys == 'l':
		pprint(lsp(node, obj_name), width=120)
	if obj_for_analisys == 'p':
		pprint(path(node, obj_name), width=80)
