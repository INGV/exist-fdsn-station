#!/usr/bin/env python
# coding: utf-8
import requests
import difflib, filecmp
import sys, os, time
import getopt
import re
import lxml.etree as ET
from xmldiff import main as xmlmain
from xmldiff import  formatting
from requests.auth import HTTPBasicAuth
from urllib.parse import urlparse, ParseResult
import pathlib

import AlternateNetworks as AN
import config as cfg

# Take all station file from a directory and sync an exist-fdsn-station database.
# Create a SourceList examining the files in the source path.
# Repeat on the station webservice Destination extracting in DestinationList
# Save the lists in files, sort them and save the sorted lists
# find differences among ResponseSource end ResponseDestination and
# extract a list of stations to download from Source: SourceChangedStations
# extract a list of stations TODO remove form Destination and log them
# for each station in SourceChangedStations
#    download station xml file at level response in a temporary path
#    PUT the file to Destination
# TODO at the end send an email with the log
# TODO split in queries for network - station to help find differences

#Source = "webservices.ingv.it"
#SourceURL = "http://"+Source+"/fdsnws/station/1/query/?"

#Destination = "172.17.0.2:8080"
#DestinationURL = "http://"+Destination+"/exist/apps/fdsn-station/fdsnws/station/1/query/?"

#Build a list with scnl for network, querying station webservice
def build_scnl_lists( webservicepath, query):

	scnl=[]
	url_request=webservicepath + query
	#print(webservicepath + query)
	response = requests.get(url_request)
	if response.status_code==200 :
		root = ET.fromstring(response.content)
		#print(response.content)
		for child in root.iter('*'):
			# print("At network level: " + child.tag)
			if child.tag == '{http://www.fdsn.org/xml/station/1}Network' :
				netcode=child.attrib.get('code')
				netstartDate=fix_dates(child.attrib.get('startDate'))
				if netstartDate != "None":
					startendquery=f'&starttime={netstartDate}'
				netendDate=fix_dates(child.attrib.get('endDate'))
				if netendDate != "None":
					startendquery += f'&endtime={netendDate}'
				#print(startendquery)
				netidentifier=""
				netdescription=""
				for elem in child.iter('*'):
					#print(elem.tag)
					if elem.tag == '{http://www.fdsn.org/xml/station/1}Description' :
						netdescription=elem.text
						#print( f'rete: {netcode} startDate: {netstartDate} endDate: {netendDate}\n description: {netdescription}')
					if elem.tag == '{http://www.fdsn.org/xml/station/1}Identifier' :
						netidentifier=elem.text
						#print(f'identifier: {netidentifier}')
				query=f'{webservicepath}level=channel&net={netcode}&format=xml&nodata=404'+startendquery
				#debug
				print(query)
				stationxml = requests.get(query)
				if stationxml.status_code == 200:
					s = ET.fromstring(stationxml.content)
				#debug print (s)
					stationlist=[]
					for element in s.iter():
						if element.tag == "{http://www.fdsn.org/xml/station/1}Station":
							#print("%s - %s" % (element.tag, element.text))
							stationcode=element.attrib.get('code')
							stationstartDate=fix_dates(element.attrib.get('startDate'))
							stationendDate=fix_dates(element.attrib.get('endDate'))
							# print(stationcode)
							#stationlist.append(stationcode)
							for child in element.iter('*'):
								if child.tag == "{http://www.fdsn.org/xml/station/1}Channel":
									channelcode=child.attrib.get('code')
									channellocation=child.attrib.get('location')
									# print(channelcode)
									channelstartDate=fix_dates(child.attrib.get('startDate'))
									# print(channelstartDate)
									channelendDate=fix_dates(child.attrib.get('endDate'))
									# print(channelendDate)
									stationlist.append((netcode, stationcode, netstartDate, netendDate, netidentifier, netdescription,  stationstartDate, stationendDate, channelcode, channellocation, channelstartDate, channelendDate))
							scnl += stationlist
				else :
					print(f"station status_code {stationxml.status_code} for {query} ")

	else :
		if response.status_code == 204:
			print(f"Nodata on source")
	#print (scnl)
	return scnl

#Given a path look for scnl defined in the contained xml files
def build_scnl_lists_from_files( dir_path, Provider, network_code):

	scnl=[]
	# url_request=webservicepath + query
	#response = requests.get(url_request)
	# to store file names
	#print(dir_path)
	res = []

	# construct path object
	d = pathlib.Path(dir_path)
	# print(d.glob("**/*.xml"))


	stationlist = []
	# iterate directory
	for entry in d.iterdir():
		# check if it a file
		if entry.is_file() and entry.match(f'{Provider}*.xml'):
			with open(entry, 'rb') as f:
				content = f.read()
			root = ET.fromstring(content)
			for child in root.iter('*'):
				if child.tag == '{http://www.fdsn.org/xml/station/1}Network' :
					netcode = child.attrib.get('code')
					if netcode == network_code or network_code=="*":
						# print(entry)
						netstartDate = fix_dates(child.attrib.get('startDate'))
						netendDate = fix_dates(child.attrib.get('endDate'))
						description = child.attrib.get('description')
						for element in child.iter():
							if element.tag == "{http://www.fdsn.org/xml/station/1}Station":
								#print("%s - %s" % (element.tag, element.text))
								stationcode = element.attrib.get('code')
								stationstartDate = fix_dates(element.attrib.get('startDate'))
								stationendDate = fix_dates(element.attrib.get('endDate'))
								for e in element.iter('*'):
									if e.tag == "{http://www.fdsn.org/xml/station/1}Channel":
										channelcode= e.attrib.get('code')
										channellocation = e.attrib.get('location')
										# print(channelcode)
										channelstartDate = fix_dates(e.attrib.get('startDate'))
										# print(channelstartDate)
										channelendDate = fix_dates(e.attrib.get('endDate'))
										# print(channelendDate)
										stationlist.append((netcode,stationcode,netstartDate,netendDate,stationstartDate,stationendDate,channelcode,channellocation,channelstartDate,channelendDate))
	scnl=stationlist

	if scnl == []:
	 		print(f"Nodata on disk for network {network_code}")
#	else:
#		print(scnl)
	return scnl


#Build a dictionary with only network codes
def build_network_lists(webservice_path, query):

	print(webservice_path + query)
	network_list=[]
	response = requests.get( webservice_path + query)
	if response.status_code == 200:
		root = ET.fromstring(response.content)
		#print(response.content)
		for child in root.iter('*'):
#		print("At network level: " + child.tag)
			if child.tag == '{http://www.fdsn.org/xml/station/1}Network' :
				netcode=child.attrib.get('code')
				# print ( f'rete: {netcode} ')
				network_list.append(netcode)
	# print(networklist)

	return network_list

#Build a dictionary with only network codes
def build_network_lists_from_files(dir_path):

	network_list = []
	#print(dir_path)
	res = []

	# construct path object
	d = pathlib.Path(dir_path)
	#print(d.glob("**/*.xml"))

	# iterate directory
	for entry in d.iterdir():
		# check if it a file
		if entry.is_file() and entry.match("*.xml"):
			#print(entry)
			with open(entry, 'rb') as f:
				content = f.read()
			root = ET.fromstring(content)
			for child in root.iter('*'):
				if child.tag == '{http://www.fdsn.org/xml/station/1}Network' :
					netcode = child.attrib.get('code')
					# print ( f'rete: {netcode} ')
					if netcode not in network_list:
						network_list.append(netcode)
#	print(network_list)

	return network_list


def get_station_xml(webservicepath, Provider, station, path):
	filename = f'{path}/{Provider}{station}.xml'
	query = 'level=response&format=xml&station='+station
	response = requests.get(webservicepath + query)
	if response.status_code == 200:
		if response.encoding != 'utf-8':
			response.encoding = 'utf-8'
		with open(filename, 'w', encoding='utf-8') as f :
			f.write(response.text)
		return True
	else :
		if response.status_code == 204:
			print(f"Nodata on source")
			return False


def get_station_xml_from_files(dir_path, Provider, station, path):
	filename = f'{path}/{Provider}{station}.xml'

	# construct path object
	d = pathlib.Path(dir_path)

	# iterate directory
	for entry in d.iterdir():
		# check if it is a file matching station
#if entry.is_file() and entry.match("*" + station + ".xml"):
		if entry.is_file() and entry.match(f'{Provider}{station}.xml'):
			print(entry)
			with open(entry, encoding='utf-8') as f:
				content = f.read()
			with open(filename, 'w', encoding='utf-8' ) as f:
				f.write(content)


def put_station_xml(webservicepath, Provider, station, path):
	filename = f'{Provider}{station}.xml'
	filepath = f'{path}/{filename}'
	print(webservicepath + " " + Provider + " " + station + " " +path)
	r = requests.put(url=webservicepath,data=open(filepath, 'rb'),headers={"Content-Type":"application/octet-stream","filename":filename}, auth = HTTPBasicAuth(cfg.AdminUser, cfg.AdminPassword))
	if not r.status_code == 200 :
		print(f"Error: {r.status_code}")
		print(r.headers)
		return False
	else:
		return True

def delete_station_xml(webservicepath, Provider, station):
	filename = f'{Provider}{station}.xml'
	r = requests.delete(url=webservicepath,headers={"filename":filename}, auth = HTTPBasicAuth(cfg.AdminUser, cfg.AdminPassword))
	return r.status_code

def fix_dates(date) :
	return re.sub("Z","",str(date))


def main(argv):

	Source = 'webservices.ingv.it'
	Destination = '172.17.0.2:8080'
	Path = '/tmp'
	Query="level=channel&network=*&format=xml&includerestricted=true"
	Stationonly=False
	virtualNetworks=False
	CheckSensorDescription=False
	LeaveUnmatched=False
	ExistDBSource=False
	ExistDBDestination=False
	Provider=""
	SourcePath=""
	Station=""
	OK=True

	try:
		opts, args = getopt.getopt(argv,"s:d:p:q:P:f:cexlhvS",["source=","destination=","path=","query=", "provider=", "force-station=", "check_sensor_desc", "existdb-source", "existdb-destination","leave_unmatched", "help"])
	except getopt.GetoptError:
		print('try fdsn-station-sync.py --help')
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-s", "--source"):
			Source = arg
		elif opt in ("-d", "--destination"):
			Destination = arg
		elif opt in ("-p", "--path"):
			Path = arg
		elif opt in ("-q", "--query"):
			Query = arg
		elif opt in ("-P", "--provider"):
			Provider = arg + "_"
		elif opt in ("-f", "--force-station"):
			Station = arg
		elif opt in ("-S"):
			Stationonly = True
		elif opt in ("-v"):
			virtualNetworks = True
		elif opt in ("-c", "--check_sensor_desc"):
			CheckSensorDescription = True
		elif opt in ("-l", "--leave_unmatched"):
			LeaveUnmatched = True
		elif opt in ("-e", "--existdb-source"):
			ExistDBSource = True
		elif opt in ("-x", "--existdb-destination"):
			ExistDBDestination = True
		elif opt in ("-h", "--help"):
			print('fdsn-station-sync.py -s|--source <source> -d|--destination <destination> -e|--existdb-source -x|--existdb-destination  -p <path> -q <query> -v -S -l ')
			print('Example 1: fdsn-station-sync-xml.py -v -s https://webservices.ingv.it -d http://172.17.0.2:8080 -p /tmp -q "level=channel&network=*&format=xml&includerestricted=true"')
			print('Example 2: fdsn-station-sync-xml.py -s file:///opt/Station -d http://127.0.0.1:80  -p /tmp  -x -P INGV -l"')
			print('Example 3: fdsn-station-sync-xml.py -s https://webservices.ingv.it -d http://172.17.0.2:8080 -p /tmp --force-station="ACER,AMUR" ')
			sys.exit()

	#print(Source + " " + Destination + " " + Path)
	if virtualNetworks == True:
		AN.build_alternate_network_file(url='http://webservices.ingv.it/ingvws/virtualnetwork/1/codes',filename=f'{Path}/AlternateNetwork.xml')
		networks=AN.build_alternate_network_lists(filename=f'{Path}/AlternateNetwork.xml')
	#print ('Source is ', Source)
	#print ('Destination is ', Destination)
	print("Provider: " + Provider)
	source_parse: ParseResult = urlparse(Source)
	if source_parse.scheme.startswith('http'):
		if ExistDBSource:
			SourceURL = Source+"/exist/apps/fdsn-station/fdsnws/station/1/query?"
		else:
			SourceURL = Source+"/fdsnws/station/1/query?"
		print(f'Reading from {SourceURL}')
	if source_parse.scheme == 'file':
		SourcePath = source_parse.path
		print(f'Reading from {SourcePath}')
	if ExistDBDestination:
		DestinationURL = Destination+"/exist/apps/fdsn-station/fdsnws/station/1/query?"
	else:
		DestinationURL = Destination+"/fdsnws/station/1/query?"
	print(f'Writing into {DestinationURL}')

	if Station == "":

		if SourcePath == "":
			SourceNetworks = build_network_lists(SourceURL,Query)
		else:
			SourceNetworks = build_network_lists_from_files(SourcePath)


		DestinationNetworks = build_network_lists(DestinationURL, Query)
		if not LeaveUnmatched:
			AllnetworksList = list(set(SourceNetworks + DestinationNetworks))
		else:
			setSN = set(SourceNetworks)
			setDN = set(DestinationNetworks)
			AllnetworksList = list(setDN.intersection(setSN))

		#TODO option to manage
		# if SourcePath != "":
		# 	SourceNetworks="*"

		for netcode in AllnetworksList :

			if SourcePath == "":
				print(f'Elaborating network {netcode} on source')
				SourceSCNL = build_scnl_lists(SourceURL,f"level=network&network={netcode}")
			else:
				SourceSCNL = build_scnl_lists_from_files(SourcePath, Provider, netcode)
			setSourceSCNL = set(SourceSCNL)
			if setSourceSCNL or (not LeaveUnmatched):
				print(f'Elaborating network {netcode} on destination')
				DestinationSCNL = build_scnl_lists(DestinationURL, f"level=network&network={netcode}")
				#print("Set source")
				#print(setSourceSCNL)
				setDestinationSCNL = set(DestinationSCNL)
				#print("Set dest")
				#print(setDestinationSCNL)
				if setSourceSCNL == setDestinationSCNL:
					print(f"{netcode} in sync")
				else:
					# print(f"Differences in {netcode} source dest")
					#Source > Dest
					setMissingOnDest=setSourceSCNL - setDestinationSCNL
					#print("Missing on dest")
					#print(setMissingOnDest)
					missing_stationset=set()
					destination_stationset=set()
					#debug_stationset=set()
					for scnl in setMissingOnDest:
						missing_stationset.add("".join(scnl[1:2]))
						#debug_stationset.add(scnl)
					#print("missing")
					#print(missing_stationset)
					#print(debug_stationset)
					#Dest > Source
					setMissingOnSource = set()
					setMissingOnSource = setDestinationSCNL - setSourceSCNL
					#print("Missing on source")
					#print(setMissingOnSource)

					for scnl in setMissingOnSource:
						destination_stationset.add("".join(scnl[1:2]))

						#debug_stationset.add(scnl)
					#print(setMissingOnSource)
					#print(debug_stationset)
					#if  len(destination_stationset) >0 :


					if ( len(destination_stationset) >0  and (not LeaveUnmatched)) :
						print("Some station on destination differ from source")
						print(destination_stationset)
						print('Removing unmatched stations from destination')
						removed_stationset=set()
						for station in destination_stationset:
							print('Trying removing station '  + Provider+station +' on destination ' + Destination)
							resp = delete_station_xml(DestinationURL,Provider,station)
							if resp == 200:
								removed_stationset.add(station)
							else:
								OK &= resp
								print(f'Failed removing, provider and station mismatch {resp}' )
						#for station in destination_stationset:
						for station in removed_stationset:
							print('Attempting to revive station ' + Provider+station)
							if SourcePath == "":
								resp = get_station_xml(SourceURL,Provider,station,Path)
								OK &= resp

							else:
								get_station_xml_from_files(SourcePath,Provider,station,Path)
							if virtualNetworks == True:
								#	add in station file the alternate snippet
								AN.add_virtual_networks(Path+"/"+Provider+station+'.xml',station,networks,Path+"/"+'AlternateNetwork.xml')
								#time.sleep(1)
							resp = put_station_xml(DestinationURL,Provider,station,Path)
							OK &= resp
					#stations with missing channels
					for station in missing_stationset:
						print('Syncing station ' + Provider + station)
						if SourcePath == "":
							get_station_xml(SourceURL, Provider, station, Path)
						else:
							get_station_xml_from_files(SourcePath, Provider, station, Path)
						if virtualNetworks == True:
							#	add in station file the alternate snippet
							AN.add_virtual_networks(Path+"/"+Provider+station+'.xml',station,networks,Path+"/"+'AlternateNetwork.xml')
						#time.sleep(1)
						resp: bool = put_station_xml(DestinationURL,Provider,station,Path)
						OK &= resp

	#
	#



	else:
		print(f'Requested to upload: {Station}')
		stationlist = Station.split(',')
		#print(f'Forcing upload of {Station}')

		missing_stationset = set(stationlist)
		#missing_stationset.add(Station)

		for station in missing_stationset :
			read_station = False
			print('Syncing station ' + Provider + station)
			if SourcePath == "" :
	#			print('Getting from network')
				read_station = get_station_xml(SourceURL, Provider, station, Path)
			else :
	#			print('Getting from filesystem')
				read_station = get_station_xml_from_files(SourcePath, Provider, station, Path)
			if virtualNetworks == True and read_station :
			#	add in station file the alternate snippet
				AN.add_virtual_networks(Path + "/" + Provider + station + '.xml', station, networks, Path + "/" + 'AlternateNetwork.xml')
				print(f'Forcing upload of {station}')
			if read_station:
				resp: bool = put_station_xml(DestinationURL, Provider, station, Path)
				OK &= resp
			else:
				OK = False
				print(f'An error occurred processing {station}')


	if OK :
		print('Synced')
	else :
		print('Synced, with errors')

if __name__ == "__main__":
	main(sys.argv[1:])

