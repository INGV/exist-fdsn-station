#!/usr/bin/env python
# coding: utf-8
import requests
import difflib, filecmp
import lxml.etree as ET
import sys, os, time
import getopt
import re

import AlternateNetworks as AN

# Contact the station webservice Source, extract all the channel matching the Request in SourceList.
# Repeat on the station webservice Destination extracting in DestinationList
# Save the lists in files, sort them and save the sorted lists
# find differences among ResponseSource end ResponseDestination and
# extract a list of stations to download from Source: SourceChangedStations
# extract a list of stations TODO remove form Destination and log them
# for each station in SourceChangedStations
#    download station xml file at level response in a temporary path
#    PUT the file to Destination
# TODO at the end send an email with the log

#Source = "webservices.ingv.it"
#SourceURL = "http://"+Source+"/fdsnws/station/1/query/?"

#Destination = "172.17.0.2:8080"
#DestinationURL = "http://"+Destination+"/exist/apps/fdsn-station/fdsnws/station/1/query/?"



def get_channel_list( webservicepath, query):
	print(webservicepath + query)
	response = requests.get( webservicepath + query)
	#print(response.text)
	return response.text

def get_station_xml(webservicepath, station, path):
	filename = f'{path}/{station}.xml'
	query = 'level=response&format=xml&station='+station
	response = requests.get(webservicepath + query)
	with open(filename, 'w') as f:
		f.write(response.text)

def put_station_xml(webservicepath, station, path):
	filename = f'{station}.xml'
	filepath = f'{path}/{station}.xml'
	files = {'file': (filepath, open(filepath, 'rb'), 'application/xml')}
	r = requests.put(url=webservicepath,data=open(filepath, 'rb'),headers={"Content-Type":"application/octet-stream","filename":filename})

def delete_station_xml(webservicepath, station):
    filename = f'{station}.xml'
    r = requests.delete(url=webservicepath,headers={"filename":filename})


def main(argv):

	Source = 'webservices.ingv.it'
	Destination = '172.17.0.2:8080'
	Path = '/tmp'
	Query="level=channel&network=*&format=text&includerestricted=true"
	Stationonly=False
	virtualNetworks=False
	CheckSensorDescription=False
	LeaveUnmatched=False
	try:
		opts, args = getopt.getopt(argv,"s:d:p:q:clvhS",["source=","destination=","path=","query=", "check_sensor_desc", "leave_unmatched", "help"])
	except getopt.GetoptError:
		print('try fdsn-station-sync.py --help')
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-h","--help"):
			print('fdsn-station-sync.py -s|--source <source> -d|--destination <destination> -p <path> -q <query> -v -S -l')
			print('Example: fdsn-station-sync.py -v -s webservices.ingv.it -d 172.17.0.2:8080 -p /tmp -q "level=channel&network=*&format=text&includerestricted=true"')
			sys.exit()
		elif opt in ("-s", "--source"):
			Source = arg
		elif opt in ("-d", "--destination"):
			Destination = arg
		elif opt in ("-p", "--path"):
			Path = arg
		elif opt in ("-q", "--query"):
			Query = arg
		elif opt in ("-S"):
			Stationonly = True
		elif opt in ("-v"):
			virtualNetworks = True
		elif opt in ("-c", "--check_sensor_desc"):
			CheckSensorDescription = True
		elif opt in ("-l", "--leave_unmatched"):
			LeaveUnmatched = True

	#print(Source + " " + Destination + " " + Path)
	if virtualNetworks == True:
		AN.build_alternate_network_file(url='http://webservices.ingv.it/ingvws/virtualnetwork/1/codes',filename=f'{Path}/AlternateNetwork.xml')
		networks=AN.build_alternate_network_lists(filename=f'{Path}/AlternateNetwork.xml')
	#print ('Source is ', Source)
	#print ('Destination is ', Destination)

	SourceURL = "http://"+Source+"/fdsnws/station/1/query?"
	DestinationURL = "http://"+Destination+"/exist/apps/fdsn-station/fdsnws/station/1/query?"


	SourceList=get_channel_list(SourceURL,Query)
	DestinationList=get_channel_list(DestinationURL,Query)


	with open(f'{Path}/source.txt', 'w') as f:
		f.writelines(SourceList)

	with open(f'{Path}/destination.txt', 'w') as f:
		f.writelines(DestinationList)

	with open(f'{Path}/source.txt', 'r') as f:
		sourced = f.readlines()

	with open(f'{Path}/destination.txt', 'r') as f:
		destinationd = f.readlines()

#If StationOnly remove all but the station name from the files
	if Stationonly:
		source=list()
		destination=list()
		occur = 2  # on which occourence you want to split
		for line in sourced:

			indices = [x.start() for x in re.finditer('\|', line)]
			part1 = line[0:indices[occur-1]]
			#part2 = line[indices[occur-1]+1:]
			source.append( part1  + "|\n" )

		for line in destinationd:
			indices = [x.start() for x in re.finditer('\|', line)]
			part1 = line[0:indices[occur-1]]
 			#part2 = line[indices[occur-1]+1:]
			destination.append( part1  + "|\n" )

	else:
		#manage to remove the Description field to avoid mismatches among source
		#and destination when writing this info in text format
		#Network|Station|Location|Channel|Latitude|Longitude|Elevation|Depth|Azimuth|Dip|SensorDescription|Scale|ScaleFreq|ScaleUnits|SampleRate|StartTime|EndTime
		#1A|SL01||HHE|7.49227|79.83003|20.0|0.0|90.0|0.0|GFZ:1A2016:CMG-3ESP/60/g=2000|2000000000.0|0.1|M/S|100.0|2016-05-25T00:00:00|2017-06-30T00:00:00

		if not CheckSensorDescription:
			source=list()
			destination=list()
			occur = 10  # on which occourence you want to split
			for line in sourced:
				indices = [x.start() for x in re.finditer('\|', line)]
				part1 = line[0:indices[occur-1]]
				part2 = line[indices[occur]:]
				source.append( part1  + part2 )
			for line in destinationd:
				indices = [x.start() for x in re.finditer('\|', line)]
				part1 = line[0:indices[occur-1]]
				part2 = line[indices[occur]:]
				destination.append( part1  + part2 )
		else:
			source=sourced
			destination=destinationd
#End Modified

	source.sort()
	destination.sort()

	with open(f'{Path}/sorted_source.txt', 'w') as f:
		f.writelines(source)

	with open(f'{Path}/sorted_destination.txt', 'w') as f:
		f.writelines(destination)


	#if ( not filecmp.cmp('sorted_source.txt', 'sorted_destination.txt')) :

	diff = difflib.unified_diff(source, destination, fromfile='source', tofile='destination', n=0)


	with open(f'{Path}/diff.txt', 'w') as f:
		f.writelines(diff)

	with open(f'{Path}/diff.txt', 'r') as fp:
		difflines = fp.readlines()

#stationset the stations that are not on destination selected lines starting with -
	missing_stationset=set()
	destination_stationset=set()
	for line in difflines:
		if (line.startswith('---') or line.startswith('+++') or line.startswith('-#') or line.startswith('+#') ):
			()
		else:
			if (line.startswith('-')):
				tokens=line.split('|',2)
				missing_stationset.add(tokens[1])
			elif (line.startswith('+')):
				tokens=line.split('|',2)
				destination_stationset.add(tokens[1])

			else:
				()

	if ( len(destination_stationset) >0  and (not LeaveUnmatched)) :
		print('Removing unmatched stations from destination')
		for station in destination_stationset:
			print('Removing station '  + station +' on destination ' + Destination)
			resp = delete_station_xml(DestinationURL,station)
		for station in destination_stationset:
			print('Attempting to revive station ' + station)
			get_station_xml(SourceURL,station,Path)
			if virtualNetworks == True:
				#	add in station file the alternate snippet
				AN.add_virtual_networks(Path+"/"+station+'.xml',station,networks,Path+"/"+'AlternateNetwork.xml')
				#time.sleep(1)
				resp = put_station_xml(DestinationURL,station,Path)

	for station in missing_stationset:
		print('Syncing station ' + station)
		get_station_xml(SourceURL,station,Path)
		if virtualNetworks == True:
			#	add in station file the alternate snippet
			AN.add_virtual_networks(Path+"/"+station+'.xml',station,networks,Path+"/"+'AlternateNetwork.xml')
		#time.sleep(1)
		resp = put_station_xml(DestinationURL,station,Path)


	# for station in destination_stationset:
	# 	print('Overwriting station ' + station)
	# 	get_station_xml(SourceURL,station)
	# 	time.sleep(2)
	# 	resp = put_station_xml(DestinationURL,station)



	print('Synced')


if __name__ == "__main__":
   main(sys.argv[1:])
