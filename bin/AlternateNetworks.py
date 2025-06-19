# Create an xml file containing the AlternateNetwork Elements to be placed in
# StationXML
import requests
import lxml.etree as ET
import sys, os, time
import getopt
import re
from copy import deepcopy

service_url='http://exist-dev.int.ingv.it:9080/eidaws/alternatenetworks/1/'

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
    xml_station = open(station_filename,'r')
    station_et = ET.parse(station_filename)
    xml_station.close()

    stationdata = ET.tostring(station_et)
    result = add_virtual_networks_indata(stationdata, station, dictionary, network_filename)
    if result is not None:
        station_et = ET.fromstring(result)
        with open(station_filename, 'wb') as f :
            f.write(ET.tostring(station_et,xml_declaration=True, encoding="UTF-8"))

def add_virtual_networks_indata(stationdata: str, station, dictionary,network_filename='AlternateNetwork.xml'):
    """

    :rtype: object string containing an StationXML after adding AlternateNetwork info if needed
    :type stationdata: object string containing an StationXML
    """
    station_et=ET.fromstring(stationdata)
    #guarda nel dictionary e se la stazione fa parte della lista aggiungi lo snippet della rete corrispondente
    networks= corresponding_keys(station,dictionary)
    # print("add_virtual_networks_indata: ")
    # print(networks)

    #use the AlternateNetwork file
    alternate_network_xml = open(network_filename, 'r')
    networkdata = alternate_network_xml.read()
    #print(networkdata)
    root_AN = ET.fromstring(networkdata)

    temp_alternate_networks_ET = deepcopy(alternate_networks_ET)

    # Removing all other stations, leave more than a period of same station if exists
    # print('Removing all other stations')
    for item in temp_alternate_networks_ET.iter('station') :
        #print("tag " + item.tag + ' ' + item.attrib.get('code'))
        #for item in child.findall('station') :
        if item.tag == 'station' and item.attrib.get('code') != station:
            #print('removing an item: ' + item.tag + ' ' + item.attrib.get('code'))
            (item.getparent()).remove(item)
        # if item.tag == 'station' and item.attrib.get('code') == station:
        #     print('Not removing an item: ' + item.tag + ' ' + item.attrib.get('code'))

    # print(f"Removing other alternate networks")
    # look in findall result to modify temp_alternate_networks_ET without collaterals effects, leaving in the matching AlternateNetwork
    # Remove empty networks
    for child in temp_alternate_networks_ET.findall('{https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd}AlternateNetwork'):
        if child.attrib.get('code') in networks :
            type = child.attrib.get('type')
            code = child.attrib.get('code')
            startDate = child.attrib.get('startDate')
            endDate = child.attrib.get('endDate')
            Description = child.findtext('Description')
            #print(f"Not removing {child.attrib.get('code')}")

        if not (child.attrib.get('code') in networks):
            #print(f"Removing {child.attrib.get('code')}")
            child.getparent().remove(child)

    # print(ET.tostring(temp_alternate_networks_ET))

    # print(f"Removing empty networks")
    for child in temp_alternate_networks_ET.iter('network'):
        lung =len(child.getchildren())
        if lung == 0:
            #print(f"Removing {child.attrib.get('code')}")
            child.getparent().remove(child)
        # else:
        #     None
        #     print(f"Not removing {child.attrib.get('code')}")

    if len(temp_alternate_networks_ET.getchildren()) == 0:
    # if len(root_AN.getchildren()) == 0 :
        print(f'Station {station} has not AlternateNetworks')
        result = stationdata
    else:
        first = 0
        mismatches = True
        # Build the elements to add
        # Verify all vnets, adding only the alternatenetwork belonging to the same period redefined in the station element
        for child in station_et.iter('*'):
            if child.tag == '{http://www.fdsn.org/xml/station/1}Station':

                #Station endtime verified against None
                if child.attrib.get('endDate') is None:
                    end_sta_none = True
                else:
                    end_sta_none = False

                # Create a full copy of temp_alternate_networks_ET to modify if needed
                # derived_AN=deepcopy(root_AN)
                derived_AN = deepcopy(temp_alternate_networks_ET)

                end_vnet_none = True

                for a_net_station in derived_AN.iter('*'):

                    #print(a_net_station.tag)
                    # if a_net_station.tag == '{https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd}AlternateNetwork}' :
                    if a_net_station.tag == 'station':

                        matches = False
                        if a_net_station.attrib.get('endDate') is None:
                            end_vnet_none = True
                        else:
                            end_vnet_none = False

                        # Add only the right AlternateNetwork, removing the ones matching a different station period
                        # need to add AlternateNetworks once, then the AlternateNetwork
                        # Time conditions to satisfy for a station belonging to an AlternateNetwork
                        if not ((end_sta_none and end_vnet_none) or
                                (end_sta_none and (not end_vnet_none) and (child.attrib.get('startDate') < a_net_station.attrib.get('endDate'))) or
                                ((not end_sta_none) and end_vnet_none and (child.attrib.get('endDate') > a_net_station.attrib.get('startDate'))) or
                                ((not end_sta_none) and (not end_vnet_none) and (child.attrib.get('startDate') < a_net_station.attrib.get('endDate') and child.attrib.get('endDate') > a_net_station.attrib.get('startDate')))):

                            # remove the alternatenetwork from derived_AN
                            # print("Warning: not fully tested until a station belong to two AlternateNetwork during two different periods")
                            print(f"Warning: station period starting at {child.attrib.get('startDate')}, does not match alternate network period starting at {a_net_station.attrib.get('startDate')}")
                            a_net_station.getparent().remove(a_net_station)
                            break
                        else:
                            matches = True
                            first += 1

                        alt_net_code= a_net_station.getparent().getparent().attrib.get('code')

                        #Not clear, empties the derived_AN removing all networks, should remove only the matching one, adding one AlternateNetwork per cicle, only if matches
                        #TODO clean only the AlternateNetwork to add (the matching one)
                        for item in derived_AN.iter('*'):
                            if item.tag == 'network' or item.tag == 'Supervisor':
                                item.getparent().remove(item)

                        #Add only one element AlternateNetworks in the first loop cycle
                        if first == 1:
                            ANs = ET.fromstring('<ingv:AlternateNetworks  xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd"></ingv:AlternateNetworks>')

                        # if end_sta_none and end_vnet_none:
                        #     #print(f"{child.attrib.get('code')} {child.attrib.get('startDate')} open and {alt_net_code} is open ")
                        # if end_sta_none and (not end_vnet_none) and (child.attrib.get('startDate') < a_net_station.attrib.get('endDate')) :
                        #     #print(f"{child.attrib.get('code')} {child.attrib.get('startDate')} open and {alt_net_code} is closed")
                        # if (not end_sta_none) and end_vnet_none and (child.attrib.get('endDate') > a_net_station.attrib.get('startDate')) :
                        #     #print(f"{child.attrib.get('code')} {child.attrib.get('startDate')} closed and {alt_net_code} is open")
                        # if (not end_sta_none) and (not end_vnet_none) and (child.attrib.get('startDate') < a_net_station.attrib.get('endDate') and child.attrib.get('endDate') > a_net_station.attrib.get('startDate')):
                        #     #print(f"{child.attrib.get('code')} {child.attrib.get('startDate')} closed and {alt_net_code} is closed")

                        if matches:
                            print(f"{child.attrib.get('code')} {child.attrib.get('startDate')} in {alt_net_code}")
                            if first == 1:
                                ANs.append(derived_AN.find('*'))
                                inner_element = child.find("*")
                                inner_element.addprevious(ANs)
                            else:
                                inner_element = child.find("*")
                                inner_element.append(derived_AN.find('*'))
                            mismatches = False
        if mismatches:
            print(f'Warning: station {station} time data mismatch with AltenateNetworks service data')
        # Using station_et can't avoid to mess up the namespaces
        result = ET.tostring(station_et)

        return result


def build_alternate_network_file(url=service_url, filename='AlternateNetwork.xml') :
    """
    Build an alternate network file complete of namespace and the correspondent global elementtree
    """
    r = requests.get(url)
    # print('Original response\n')
    # print(r.content)
    # print('\n')
    print(f"Reading AlternateNetwork info from: {url}")
    xml_outfile = open(filename, "w")
    root = ET.fromstring(r.content)
    #fragment='<?xml version="1.0"" ?>'
    fragment='<ingv:AlternateNetworks  xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">'
    #xml_outfile.write(fragment)
    for child in root.iter('*'):
        if child.tag != 'AlternateNetworks':
            #print("tag "+child.tag)
            if child.tag == 'AlternateNetwork':
                type='VIRTUAL'
                code=child.attrib.get('code')
                startDate=child.attrib.get('startDate')
                endDate=child.attrib.get('endDate')
                children=child.getchildren()
                #TODO loop on children to take all of them
                #
                network_fragment=""
                for elem in children:
                    network_fragment += ET.tostring(elem).decode()
                #print(network_fragment)

                if endDate != None:
                    fragment+=f'<ingv:AlternateNetwork type="{type}" code="{code}" startDate="{startDate}" endDate="{endDate}">{network_fragment}</ingv:AlternateNetwork>'
                else:
                    fragment+=f'<ingv:AlternateNetwork type="{type}" code="{code}" startDate="{startDate}">{network_fragment}</ingv:AlternateNetwork>'

                # print(fragment)

    fragment+='</ingv:AlternateNetworks>'
    xml_outfile.write(fragment)
    xml_outfile.close()
    global alternate_networks_ET
    alternate_networks_ET = ET.fromstring(fragment)

def build_alternate_network_lists(filename='AlternateNetwork.xml'):
    alternate_network_xml = open(filename, 'r')
    data = alternate_network_xml.read()
    root = ET.fromstring(data)
    networks={}
    for child in root.iter('*'):
        #print("building dictionary: " + child.tag)
        if child.tag == '{https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd}AlternateNetwork' :
            code = child.attrib.get('code')
            #debug print ( f'rete: {code} startDate: {startDate} endDate: {endDate} description: {description}')
            query=service_url+f'?code={code}'
            #debug print(query)
            stationxml = requests.get(query)
            s= ET.fromstring(stationxml.content)
            # print (stationxml.content)
            stationlist=[]
            for element in s.iter():
                if element.tag == "station":
                    #print("%s - %s" % (element.tag, element.text))
                    stationcode=element.attrib.get('code')
                    #debug print(stationcode)
                    stationlist.append(stationcode)

            networks[code]=stationlist
    # print(networks)
    return networks


def main(argv):
    default_outfile="AlternateNetwork.xml"
    default_url=service_url
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
    build_alternate_network_lists()


if __name__ == "__main__":
   main(sys.argv[1:])
