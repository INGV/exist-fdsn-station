#!/usr/bin/env python
# coding: utf-8
import requests
import difflib, filecmp 
import lxml.etree as ET
import sys, os, time
import getopt
import re

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

def get_station_xml(webservicepath, station):
	query = 'level=response&format=xml&station='+station
	response = requests.get(webservicepath + query)
	with open(station+'.xml', 'w') as f:
		f.write(response.text)

def put_station_xml(webservicepath, station):
    filename = f'{station}.xml'
    files = {'file': (filename, open(filename, 'rb'), 'application/xml')}
    r = requests.put(url=webservicepath,data=open(filename, 'rb'),headers={"Content-Type":"application/octet-stream","filename":filename}) 


def main(argv):

	Source = 'webservices.ingv.it'
	Destination = '172.17.0.2:8080'
	Path = '/tmp'
	Query="level=channel&network=*&format=text&includerestricted=true"
	Stationonly=False
	try:
		opts, args = getopt.getopt(argv,"hs:d:p:q:S",["source=","destination","path","query"])
	except getopt.GetoptError:
		print('fdsn-station-sync.py -s <source> -d <destination> -p <path> -q <query>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('fdsn-station-sync.py -s <source> -d <destination> -p <path> -S')
			print('Example: fdsn-station-sync.py -s webservices.ingv.it -d 172.17.0.2:8080 -p /tmp -q "level=channel&network=*&format=text&includerestricted=true"') 
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
				
	#print ('Source is ', Source)
	#print ('Destination is ', Destination)

	SourceURL = "http://"+Source+"/fdsnws/station/1/query/?"
	DestinationURL = "http://"+Destination+"/exist/apps/fdsn-station/fdsnws/station/1/query/?"	
	
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

#Modified
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
	for station in missing_stationset:
		print('Syncing station ' + station)
		get_station_xml(SourceURL,station)
		time.sleep(2)
		resp = put_station_xml(DestinationURL,station)

	for station in destination_stationset:
		print('Destination station ' + station)

	print('Synced')
	

if __name__ == "__main__":
   main(sys.argv[1:])
