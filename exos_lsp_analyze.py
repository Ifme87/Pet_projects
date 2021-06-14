#!/usr/bin/env python3

import subprocess
import sys
import re
import time
from pprint import pprint


def vpn(node, vpn_name):
	'''regular expressions'''
	regex_ip = re.compile('.*peer ((\w+.){3}(\w+))')
	regex_lsp = re.compile('.* lsp "(\S+)" .*')
	'''looking for all peers of vpn'''
	directory = f'~/Downloads/{node}.cfg'
	peers = subprocess.run([f'grep "l2vpn.*{vpn_name}.*peer" {directory}'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')
	peers = peers.stdout.split('\n')
	lsps_of_vpn = []
	for i in peers:
		match = re.match(regex_ip, i)
		if match:
			out = subprocess.run([f'grep "rsvp-te.*destin" {directory} | grep {match.group(1)}'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')	
			out = out.stdout.split('\n')
			for i in out:
				match_lsp = re.match(regex_lsp, i)
				if match_lsp:
					lsps_of_vpn.append(match_lsp.group(1))
	result_vpn = dict()
	for lsps in lsps_of_vpn:
		result_vpn.update(lsp(node, lsps))
	return result_vpn


def lsp(node, lsp_name):
	regex_path = re.compile('.*add path "*(\S+?)"* .*')
	directory = f'~/Downloads/{node}.cfg'
	out = subprocess.run([f'grep "rsvp-te.*add path" {directory} | grep {lsp_name}'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')	
	out = out.stdout.split('\n')
	paths = []
	for path1 in out:
		match = re.match(regex_path, path1)
		if match:
			paths.append(match.group(1))
	result = {}
	for path1 in paths:
		hops = path(node, path1)
		result[path1] = hops
	lsp = {}
	lsp[lsp_name] = result	
	return lsp

	
def path(node, path_name):
	regex_hops = re.compile('.*ero include ((\w+.){3}(\w+))\/(\w+) .*(order \w+)')
	directory = f'~/Downloads/{node}.cfg'
	hops2 = subprocess.run([f'grep "rsvp-te.*add ero" {directory} | grep {path_name}'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')
	hops2 = hops2.stdout.split('\n')
	ips = []
	for ip in hops2:	
		match = re.match(regex_hops, ip)
		if match:
			ips.append(match.group(1))
	return resolve_ip(ips)
	
		
def resolve_ip(ips_to_resolve):
	regex_name = re.compile('.*pointer (\S+?-\S+?-\S+?..)')
	hops3 = []			
	for ip in ips_to_resolve:
		domain_name = subprocess.run([f'host {ip}'], shell=True, stdout=subprocess.PIPE, encoding='utf-8')
		time.sleep(0.5)
		match = re.match(regex_name, domain_name.stdout)
		if match:
			hops3.append(f'{match.group(1)} ip {ip}')
		else:
			'''add name resolving for grey ips'''
			hops3.append(ip)
	return hops3
	

if __name__ == "__main__":
	'''objects to check:
		-vpn (vpls and vpws)
		-lsp (rsvp-te and ldp)
		-paths
		and hops resolving
	'''
	pprint(vpn('spb-ivc-ts3', 'OTN_1284'))
	#pprint(lsp('spb-ivc-ts3', 'ivcts3_frmntts2'))
	#pprint(path('spb-ivc-ts3', 'path_163_hs2_2_7_26_22'))
	#pprint(resolve_ip('spb-ivc-ts3', 'path_163_hs2_2_7_26_22'))
