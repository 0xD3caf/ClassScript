# -*- coding: utf-8 -*-

###############NETWORK HOMEWORK######################
##### CSEC-380/480 Security Automation - Ryan Haley####
'''
You have just joined an elite 3-letter government agency’s red team.
On your first assignment, you gain access to a host on the target network,
but are unable to upload or run any unauthorized tools due to strict
application control on the host. You do notice, however, that python is
a whitelisted application on the host. Knowing this, you decide to use
it to do your reconnaissance (scanning) of the network.
 
Create a program that simulates nmap (network scanning tool).
Your program must accept options for IP(s), TCP or UDP,
and port numbers or ranges. The program will then tell the
user which ports are open on the target IP(s). 

You are to scan your Windows 10 host (10.12.0.15) from your Kali system (10.12.0.10) ONLY!!!

Required Conditions (0.75 pts/each - 5 pts total):
	Does it run without errors? 
	Can it successfully scan 1 IP? 
	Can it successfully scan multiple IPs? 
	Can it attempt to identify open/closed UDP ports? 
	Can it identify open/closed TCP ports? 
	Can it successfully scan multiple ports? 
	Does it properly inform the user of findings? 

Bonus Conditions (+3.5 possible):
	Fingerprint any port/service running a webserver (What service and version was discovered). (0.5 pt)
                Inform the user of the type and version server found. (0.5pts)
                If Service is a webserver:
                        Inform the user of the status code returned (for a root request – aka "GET / HTTP/1.1"). (0.5pts)
                        Inform the user of the title of the page found. (0.5pts)
	Option to take a list (txt file) of IPs to scan. (0.5 pts)
	Option to take a timeout value between each port scan. (0.5 pts)
	Option to save results to a  txt file (0.5 pts)
'''

#Mackenzie Summers

'''
FLAGS

-i Single IP
-I IP List

-p Single Port
-P or --ports Port range

-T or --type TCP or UDP specifier

-L or --list Takes the remaning vars as a list to try (INACTIVE)

-F or --file to read IP addrs from

-O or --out File to write results to

-Q or --quiet turns off display of closed ports

-W or --wait gives a time to wait between scans
'''

# COMMAND -i SINGLE_IP {-I[IP_RANGE_START IP_RANGE_END]} -p SINGLE_PORT {-P | --ports [PORT_RANGE_START PORT_RANGE_END]} -T | --type {TCP|UDP} 
																#{-F | --file[FILE_PATH]} {-O | --out[OUTFILE_PATH]} {-Q | --quiet} {-W | --wait [WAIT_TIME]}
#to scan IP lists that are not sequential use the from file option

import argparse
import socket
import requests
from ipaddress import ip_address
import sys
from scapy.all import *

def findIPs(start, end):
    start = ip_address(start)
    end = ip_address(end)
    result = []
    while start <= end:
        result.append(str(start))
        start += 1
    return result


def is_valid_ipv4_address(address):
    try:
        socket.inet_pton(socket.AF_INET, address)
        try:
            socket.inet_aton(address)
        except:
        	return False
        return address.count('.') == 3
    except:  # not a valid address
    	return False

    return True

def scanMe(user_args):
	host_list = []
	port_list = []
	scan_type = "TCP"
	in_file = ""
	out_file = ""
	quiet = False
	timeout = 0

	if user_args.get("wait") != 0:
		timeout = user_args.get("wait")

	if user_args.get("quiet") == True:
		quiet = True

	if user_args.get("out") != None:			#checks for output file
		out_file = user_args.get("out")

	if user_args.get("file") != None:			#checks if Ip addrs should come from file
		in_file = user_args.get("file")

	if user_args.get("type") != None:				#checks for TCp or UDP scan type
		scan_type = user_args.get("type").upper()
	
	if in_file == "":
		if user_args.get("i") != None:				#finds IP addr or IP addr list to target
			host_list.append(user_args.get("i"))
		else:
			host_list_start = user_args.get("I")[0]
			host_list_end = user_args.get("I")[1]
			host_list = findIPs(host_list_start, host_list_end)
	else:
		#read from file
		IP_file = open(in_file)
		for line in IP_file.readlines():
			host_list.append(line.strip("\n"))
		IP_file.close()

	if user_args.get("p") != None:				#finds port or port list to target
		port_list.append(user_args.get("p"))
	else:
		port_list_start = user_args.get("ports")[0]
		port_list_end = user_args.get("ports")[1]
		for port in range(port_list_start, port_list_end + 1):
			port_list.append(port)
	results = {}
	for host in host_list:
		results.update({host: []})
	if scan_type == "TCP":
		for target_host in host_list:			#sets up to do scanning on ports for all targets
			for target_port in port_list:
				try:
					#do the scanning here
					client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					client.connect((target_host, target_port))
					print("test")
					new_host = [target_port, "O"]
					results[target_host].append(new_host)
					time.sleep(timeout)
				except Exception as e:
					new_host = [target_port, "C"]
					results[target_host].append(new_host)
					time.sleep(timeout)
				client.close()
	if scan_type == "UDP":
		for target_host in host_list:			#sets up to do scanning on ports for all targets
			for target_port in port_list:
				try:
					#do the scanning here
					answer = sr1(IP(dst=target_host)/UDP(sport=RandShort(), dport=target_port)/DNS(rd=1,qd=DNSQR(qname="google.com",qtype="A")))
					test = answer.an
					if test == None:
						new_host = [target_port, "C"]
						results[target_host].append(new_host)
						time.sleep(timeout)
					else:
						new_host = [target_port, "O"]
						results[target_host].append(new_host)
						time.sleep(timeout)
				except Exception as t:
					print("test")
					print(t)
					new_host = [target_port, "C"]
					results[target_host].append(new_host)
					time.sleep(timeout)


	if out_file == "":
		print("\nPort Type: {}".format(scan_type))
		print("Target" + " "*(25-6) + "Port" + " "*(25-4) + "Status\n")
		for key in results.keys():
			target_final_list = results.get(key)
			for item in target_final_list:	
				if item[1] == "O":
					print(key + " "*(25 - len(key))+ str(item[0]) + " "*(25 - len(str(item[0]))) + "Open\n")
				elif quiet == False:
					if scan_type == "TCP":
						print(key + " "*(25 - len(key))+ str(item[0]) + " "*(25 - len(str(item[0]))) + "Closed\n")
					else:
						print(key + " "*(25 - len(key))+ str(item[0]) + " "*(25 - len(str(item[0]))) + "Closed/Filtered\n")		

	else:
		f = open(out_file, "w")
		f.write("Port Type: {}\n".format(scan_type))
		f.write("Target" + " "*(25-6) + "Port" + " "*(25-4) + "Status\n")
		for key in results.keys():
			target_final_list = results.get(key)
			for item in target_final_list:
				if item[1] == "O":
					f.write(key + " "*(25 - len(key))+ str(item[0]) + " "*(25 - len(str(item[0]))) + "Open\n")
				elif quiet == False:
					if scan_type == "TCP":
						f.write(key + " "*(25 - len(key))+ str(item[0]) + " "*(25 - len(str(item[0]))) + "Closed\n")
					else:	
						f.write(key + " "*(25 - len(key))+ str(item[0]) + " "*(25 - len(str(item[0]))) + "Closed/Filtered\n")		

	return



parser = argparse.ArgumentParser()
IP_group = parser.add_mutually_exclusive_group()
Port_group = parser.add_mutually_exclusive_group()

IP_group.add_argument("-i", help = "Takes a single IP to scan", metavar = "IP Address") 														#add regex to match only valid IP addrs
IP_group.add_argument("-I", help = "Takes 2 Ip addreses and uses them as a range. WARNING: this will scan many IP addreses", nargs = 2, metavar = "Start/End IP address")

Port_group.add_argument("-p", help = 'The port to be scanned', type=int, choices = range(1,65536), metavar = "{1...65536}")
Port_group.add_argument("-P", "--ports", help = "Give a range of IP addresses, ALL IPs in range will be scanned", type = int, nargs = 2,choices = range(1,65536), metavar = "{1...65535}")

parser.add_argument("-T", "--type", help = "TCP or UDP specifier", choices = ["TCP", "tcp", "UDP", "udp"], metavar = "{TCP | UDP")
parser.add_argument("-Q", "--quiet", help = "removes closed/filtered ports from list", action = "store_true", default = False)
parser.add_argument("-F", "--file", help = "Takes a file to read IP addresses from, One per line")
parser.add_argument("-O", "--out", help = "takes a file location to output results of scan")
parser.add_argument("-W", "--wait", help = "specifies a time to time.sleep between each scan: max of 60 seconds", type = int, choices = range(0, 60), metavar = "{0...60}", default = 0)


args = parser.parse_args()
args_dict = vars(args)
single_IP_check = is_valid_ipv4_address(args.i)
range_IP_check = False
valid = True
if args_dict.get("file") == None:
	try:
		range_IP_check = is_valid_ipv4_address(args_dict.get("I")[0])
		range_IP_check = is_valid_ipv4_address(args_dict.get("I")[1])
	except:
		pass
	if not single_IP_check and not range_IP_check:
		print("There was an invalid IP or there was no IP given")
		valid = False
elif args_dict.get("file") != None:
	file = open(args_dict.get("file"))
	for line in file.readlines():
		if not is_valid_ipv4_address(str(line.strip("\n"))):
			print("The address {} in the file was invalid, please remove this address and try again".format(line.strip("\n")))
			valid = False
	file.close()
if not args.p and not args.ports:	#check for a port
	print("There was no port given, Please enter a port or port range")
	valid = False

if valid == True:
	scanMe(args_dict)


