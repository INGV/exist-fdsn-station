# Create an xml file containing the AlternateNetwork Elements to be placed in
# StationXML
import requests
import lxml.etree as ET
import sys, os, time
import getopt
import re


def corresponding_keys(val, dictionary):
        keys = []
        for k, v in dictionary.items():
            if val in v:
                keys.append(k)
        return keys

def add_virtual_networks(station_filename: str, station, dictionary,network_filename='AlternateNetwork.xml'):
    """

    :type station_filename: object str path of a StationXML file
    """
    #filename = f'{station}.xml'
    xml_station=open(station_filename,'r')
    stationdata=xml_station.read()
    xml_station.close()
    pattern= r'(<Station.*?)>'

    #guarda nel dictionary e se la stazione fa parte della lista aggiungi lo snippet della rete corrispondente
    #print(dictionary)
    networks= corresponding_keys(station,dictionary)
    #print(networks)

    #use the AlternateNetwork file
    alternate_network_xml = open(network_filename, 'r')
    networkdata = alternate_network_xml.read()
    #print(data)
    root = ET.fromstring(networkdata)
    replacement=""
    fragment='<ingv:AlternateNetworks>'
    #fragment='<ingv:AlternateNetworks xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">'
    #print(fragment)
    for child in root.iter('*'):
        code=""
        #print(child.tag)
        if child.tag == '{https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd}AlternateNetwork' and child.attrib.get('code') in networks:
            type=child.attrib.get('type')
            code=child.attrib.get('code')
            startDate=child.attrib.get('startDate')
            endDate=child.attrib.get('endDate')
            Description=child.findtext('Description')
            #print(Description)
            #description=child.attrib.get('description')
            if endDate != None:
                fragment+=f'<ingv:AlternateNetwork type="{type}" code="{code}" startDate="{startDate}" endDate="{endDate}"><Description>{Description}</Description></ingv:AlternateNetwork>'
                #print(fragment)
                #xml_outfile.write(fragment)
            else:
                fragment+=f'<ingv:AlternateNetwork type="{type}" code="{code}" startDate="{startDate}"><Description>{Description}</Description></ingv:AlternateNetwork>'
                #print(fragment)
                #xml_outfile.write(fragment)

    fragment+='</ingv:AlternateNetworks>'
    #print(fragment)
    if fragment == '<ingv:AlternateNetworks></ingv:AlternateNetworks>':
    #if fragment == '<ingv:AlternateNetworks xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd"></ingv:AlternateNetworks>':
        fragment=""
        print(f'Station {station} has not AlternateNetworks \n')

    else:
        print(f'Station {station} has got AlternateNetworks, inserting:\n{fragment}')
        #replacement = r'\1><PIPPO>'
        replacement=f"\\1>{fragment}"
        #result = re.sub(pattern, replacement, stationdata)
        result = re.sub(pattern, replacement, stationdata)
        #debug print(result)
        xml_station=open(station_filename,'w')
        xml_station.write(result)
        xml_station.close()


def add_virtual_networks_indata(stationdata: str, station, dictionary,network_filename='AlternateNetwork.xml'):
    """

    :rtype: object string containing an StationXML after adding AlternateNetwork info if needed
    :type stationdata: object string containing an StationXML
    """

    pattern= r'(<Station.*?)>'

    #guarda nel dictionary e se la stazione fa parte della lista aggiungi lo snippet della rete corrispondente
    #print(dictionary)
    networks= corresponding_keys(station,dictionary)
    #print(networks)

    #use the AlternateNetwork file
    alternate_network_xml = open(network_filename, 'r')
    networkdata = alternate_network_xml.read()
    #print(data)
    root = ET.fromstring(networkdata)
    replacement=""
    fragment='<ingv:AlternateNetworks>'
    #fragment='<ingv:AlternateNetworks xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">'
    #print(fragment)
    for child in root.iter('*'):
        code=""
        #print(child.tag)
        if child.tag == '{https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd}AlternateNetwork' and child.attrib.get('code') in networks:
            type=child.attrib.get('type')
            code=child.attrib.get('code')
            startDate=child.attrib.get('startDate')
            endDate=child.attrib.get('endDate')
            Description=child.findtext('Description')
            #print(Description)
            #description=child.attrib.get('description')
            if endDate != None:
                fragment+=f'<ingv:AlternateNetwork type="{type}" code="{code}" startDate="{startDate}" endDate="{endDate}"><Description>{Description}</Description></ingv:AlternateNetwork>'
                #print(fragment)
                #xml_outfile.write(fragment)
            else:
                fragment+=f'<ingv:AlternateNetwork type="{type}" code="{code}" startDate="{startDate}"><Description>{Description}</Description></ingv:AlternateNetwork>'
                #print(fragment)
                #xml_outfile.write(fragment)

    fragment+='</ingv:AlternateNetworks>'
    #print(fragment)
    if fragment == '<ingv:AlternateNetworks></ingv:AlternateNetworks>':
    #if fragment == '<ingv:AlternateNetworks xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd"></ingv:AlternateNetworks>':
        fragment=""
        print(f'Station {station} has not AlternateNetworks \n')
        #will return unchanged
        result = stationdata
    else:
        print(f'Station {station} has got AlternateNetworks, inserting:\n{fragment}')
        #replacement = r'\1><PIPPO>'
        replacement=f"\\1>{fragment}"
        #result = re.sub(pattern, replacement, stationdata)
        result = re.sub(pattern, replacement, stationdata.decode('utf-8')).encode('utf-8')
        #debug print(result)
    return result

def build_alternate_network_file(url='http://jabba.int.ingv.it:10005/ingvws/virtualnetwork/1/codes',filename='AlternateNetwork.xml'):
    r = requests.get(url)
    print('Original response\n')
    print(r.content)
    print('\n')
    xml_outfile = open(filename, "w")
    root = ET.fromstring(r.content)
    #fragment='<?xml version="1.0"" ?>'
    fragment='<ingv:AlternateNetworks  xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">'
    #xml_outfile.write(fragment)
    for child in root.iter('*'):
        if child.tag != 'virtualNetworks':
            #print("tag "+child.tag)
            if child.tag == 'virtualNetwork':
                type='VIRTUAL'
                code=child.attrib.get('code')
                startDate=child.attrib.get('startDate')
                endDate=child.attrib.get('endDate')

            if child.tag == 'Description':
                Description=child.text
            #print(child.tag, child.attrib)
                if endDate != None:
                    fragment+=f'<ingv:AlternateNetwork type="{type}" code="{code}" startDate="{startDate}" endDate="{endDate}"><Description>{Description}</Description></ingv:AlternateNetwork>'
                    #print(fragment)
                    #xml_outfile.write(fragment)
                else:
                    fragment+=f'<ingv:AlternateNetwork type="{type}" code="{code}" startDate="{startDate}"><Description>{Description}</Description></ingv:AlternateNetwork>'
                    #print(fragment)
                    #xml_outfile.write(fragment)
    fragment+='</ingv:AlternateNetworks>'
    xml_outfile.write(fragment)
    xml_outfile.close()

def build_alternate_network_lists(filename='AlternateNetwork.xml'):
    alternate_network_xml = open(filename, 'r')
    data = alternate_network_xml.read()
    #debug
    #print(data)
    root = ET.fromstring(data)
    networks={}
    for child in root.iter('*'):
        #print("building dictionary: " + child.tag)
        if child.tag == '{https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd}AlternateNetwork' :
            code=child.attrib.get('code')
            #startDate=child.attrib.get('startDate')
            #endDate=child.attrib.get('endDate')
            #description=child.attrib.get('description')
            #debug print ( f'rete: {code} startDate: {startDate} endDate: {endDate} description: {description}')
            query=f'http://jabba.int.ingv.it:10005/fdsnws/station/1/query?level=station&net={code}&format=xml&nodata=404'
            #debug print(query)
            stationxml = requests.get(query)
            s= ET.fromstring(stationxml.content)
            #debug print (s)
            stationlist=[]
            for element in s.iter():
                if element.tag == "{http://www.fdsn.org/xml/station/1}Station":
                    #print("%s - %s" % (element.tag, element.text))
                    stationcode=element.attrib.get('code')
                    #debug print(stationcode)
                    stationlist.append(stationcode)
            #for child in s:
            #    print(child.tag)
            #for child in s.iter('*'):
            #    if child.tag == 'Network':
            #        stationcode=child.attrib.get('code')
            #        stationlist.append(stationcode)
            #        print(stationlist)

            networks[code]=stationlist
    print(networks)
    return networks


def main(argv):
    default_outfile="AlternateNetwork.xml"
    default_url="http://webservices.ingv.it/ingvws/virtualnetwork/1/codes"
    try:
        opts, args = getopt.getopt(argv,"hs:f:",["sourceurl=","file="])
    except getopt.GetoptError:
        print('getAlternateNetworks.py -h [-s <sourceurl>] [--sourceurl=<sourceurl>] [-f <outputfile> --file=<outputfile>]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('getAlternateNetworks.py -h -s <source> -f <outputfile>')
            print('Example: getAlternateNetworks.py -s "http://webservices.ingv.it/ingvws/virtualnetwork/1/codes" -f AlternateNetwork.xml')
            sys.exit()
        elif opt in ("-s", "--sourceurl"):
            default_url = arg
        elif opt in ("-f", "--file"):
            default_outfile = arg

    build_alternate_network_file(url=default_url, filename=default_outfile)




if __name__ == "__main__":
   main(sys.argv[1:])
