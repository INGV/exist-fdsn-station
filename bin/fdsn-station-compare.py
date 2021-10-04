#!/usr/bin/env python
# coding: utf-8
import requests
import difflib, filecmp 
import lxml.etree as ET

import sys, os, time
import getopt
from urllib.parse import urlparse, parse_qs

# Query the station webservice Source, save the response code and file(text or xml) and time 
# Repeat the Query on the station webservice Destination, save the response code and file (text or xml) and time
# find differences among ResponseSource end ResponseDestination,
# Output a line with the summary when OK 
# query  - status of comparison  - time source  - time dest
# Output a multi line when Response differs:
# query  - status of comparison  - time source  - time dest
# differences in diff format for text response
# different tag elements found () if possible

#Source = "webservices.ingv.it"
#SourceURL = "http://"+Source+"/fdsnws/station/1/query/?"

#Destination = "172.17.0.2:8080"
#DestinationURL = "http://"+Destination+"/exist/apps/fdsn-station/fdsnws/station/1/query/?"


def check_format_text(url):
	format_dict={'format': ['text']}
	print("in check_param_value")
	parsed_url = urlparse(url.rstrip("\n"))
	params_dict=parse_qs(parsed_url.query)
	print(params_dict) 
	if( 'format' in params_dict):
		if params_dict['format'] == format_dict['format'] :
			print( "1 true")
			result=True
		else:
			print(params_dict['format'])
			print(format_dict['format'])
			result=False
	else:
		print("3 false")
		result = False
	return result


def get_response( webservicepath, query):
	#print(webservicepath + query)
	response = requests.get( webservicepath + query)
	return response

	
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
	result=1
	Source = 'webservices.ingv.it'
	Destination = '172.17.0.2:8080'
	SourcePrefix = '/exist/apps/fdsn-station'
	DestinationPrefix = '/exist/apps/fdsn-station'
	
	Path = '/tmp'
	Query="level=channel&network=*&format=text&includerestricted=true"
	InputFile=None
	try:
		opts, args = getopt.getopt(argv,"hs:d:o:e:p:f:",["=source","=destination", "=source-prefix","=destination-prefix", "=path", "=file"])
	except getopt.GetoptError:
		print('fdsn-station-compare.py -h -s <source> -o <source-prefix> -d <destination> -e <destination-prefix> -p <path> -q <query> -f <queryfile>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('fdsn-station-compare.py -h -s <source> -o <source-prefix> -d <destination> -e <destination-prefix> -p <path> -q <query> -f <queryfile>')
			print('Example: fdsn-station-compare.py -s webservices.ingv.it -o "" -d 172.17.0.2:8080 -e"/exist/apps/fdsn-station" -p /tmp') 
			sys.exit()
		elif opt in ("-s", "--source"):
			Source = arg
		elif opt in ("-d", "--destination"):
			Destination = arg
		elif opt in ("-o", "--source-prefix"):
			SourcePrefix = arg
		elif opt in ("-e", "--destination-prefix"):
			DestinationPrefix = arg
		elif opt in ("-p", "--path"):
			Path = arg
		elif opt in ("-f", "--file"):
			InputFile = arg			
	#print ('Source is ', Source)
	#print ('Destination is ', Destination)


	if (InputFile):
		with open(InputFile, 'r') as f:
			querylines = f.readlines()

		for Query in querylines:
			result=2
			print(Query+ " " + str(result) )
			
			# webservice SourceURL = "http://"+Source
			SourceURL = "http://"+Source+SourcePrefix
			DestinationURL = "http://"+Destination+DestinationPrefix	
			
			start_time = time.time()
			response_source = get_response( SourceURL, Query.rstrip())
			source_time = time.time()
			response_destination = get_response( DestinationURL, Query.rstrip())
			destination_time = time.time()
			d_interval= (destination_time - source_time)*1000
			s_interval= (source_time - start_time)*1000
			
			#print(type(response_source))
			#print(type(response_destination))

			if ( response_source.status_code == 200  and response_destination.status_code == 200 ): 
				print("Working on responses")
				with open(f'{Path}/source.txt', 'w') as f:
					f.writelines(response_source.text)
					
				with open(f'{Path}/destination.txt', 'w') as f:
					f.writelines(response_destination.text)

				with open(f'{Path}/source.txt', 'r') as f:
					source = f.readlines()

				with open(f'{Path}/destination.txt', 'r') as f:
					destination = f.readlines()
			
				if check_format_text(SourceURL+Query):
				#if True:
					#source = response_source.text
					#destination = response_destination.text
					print("Working on text")
					source.sort()
					destination.sort()

					diff = difflib.unified_diff(source, destination, fromfile='source', tofile='destination', n=0)
					#print(type(diff))
					#print(list(diff))
					with open(f'{Path}/diff.txt', 'w') as f:
						f.writelines(diff)
					
					if len(list(diff)) == 0:
						result=0
					else:
						result=1

				else: 
					print("Working on xml")
					#print(response_destination.text)
					#print(response_source.text)
					#response_source.raw.decode_content = True
					try:
						destination_response_tree = ET.fromstring(bytes(response_destination.text, encoding='utf-8'))
						source_response_tree = ET.fromstring(bytes(response_source.text, encoding='utf-8'))
					
						#from xml.etree.ElementTree import ElementTree
						#tree = ElementTree()	
						#destination_response_tree = tree.parse("my_file.xml")
						
						#for node in destination_response_tree.findall("{http://www.fdsn.org/xml/station/1}Network"):
							#for type in node.getchildren():
								#print(type.text)
						#for node in source_response_tree.findall("{http://www.fdsn.org/xml/station/1}Network"):
							#for type in node.getchildren():
								#print(type.text)					
						#etree.fromstring(bytes(r.text, encoding='utf-8'))
						ET.strip_elements(source_response_tree,'{http://www.fdsn.org/xml/station/1}Source',with_tail=True)    
						ET.strip_elements(source_response_tree,'{http://www.fdsn.org/xml/station/1}Sender',with_tail=True) 					
						ET.strip_elements(source_response_tree,'{http://www.fdsn.org/xml/station/1}Created',with_tail=True)    
						ET.strip_elements(source_response_tree,'{http://www.fdsn.org/xml/station/1}Module',with_tail=True)  
						ET.strip_elements(source_response_tree,'{http://www.fdsn.org/xml/station/1}ModuleURI',with_tail=True)  
						ET.strip_elements(source_response_tree,'{http://www.fdsn.org/xml/station/1}Network/Identifier',with_tail=True)  

						ET.strip_elements(destination_response_tree,'{http://www.fdsn.org/xml/station/1}Source',with_tail=True)    
						ET.strip_elements(destination_response_tree,'{http://www.fdsn.org/xml/station/1}Sender',with_tail=True)    
						ET.strip_elements(destination_response_tree,'{http://www.fdsn.org/xml/station/1}Created',with_tail=True)    
						ET.strip_elements(destination_response_tree,'{http://www.fdsn.org/xml/station/1}Module',with_tail=True)  
						ET.strip_elements(destination_response_tree,'{http://www.fdsn.org/xml/station/1}ModuleURI',with_tail=True)  
						ET.strip_elements(destination_response_tree,'{http://www.fdsn.org/xml/station/1}Network/Identifier',with_tail=True)
						#print(ET.tostring(source_response_tree))
						#print(ET.tostring(destination_response_tree))
					
						#Checking only the Network element after sort
						if (source_response_tree.getchildren().sort() == destination_response_tree.getchildren().sort()):
							result=0
						else:
							result=1
					except TypeError:
						result=1
						print("Waiting for xml, get text")
			elif response_destination == None  and response_source:
				result = 2
			elif response_destination and response_source == None:
				result = 2
			elif response_destination != response_source :
				result = 2
			else:
				result = 0
# Pass: 536.292552947998 - 			
			if result == 0:
				print("Pass: " + str(d_interval) + ' - ' + DestinationURL + Query.rstrip()) 
				print("Pass: " + str(s_interval) + ' - ' + SourceURL + Query.rstrip()) 
			elif result == 1:	
				print("Fail: " + str(d_interval) + ' - '  + DestinationURL + Query.rstrip()) 
				print("Fail: " + str(s_interval)	 + ' - ' + SourceURL + Query.rstrip()) 
			else:
				print("Doubt : " + Query)
	else:
		print('fdsn-station-compare.py -h -s <source> -o <source-prefix> -d <destination> -e <destination-prefix> -p <path> -q <query> -f <queryfile>')

if __name__ == "__main__":
   main(sys.argv[1:])
