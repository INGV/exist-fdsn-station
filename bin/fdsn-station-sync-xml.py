#!/usr/bin/env python
# coding: utf-8
import getopt
import pathlib
import re
import sys
from typing import Set
from urllib.parse import urlparse, ParseResult

import lxml.etree as et
import requests
from requests.auth import HTTPBasicAuth

import AlternateNetworks as AN
import config as cfg

current_content = u''

# Build a list with scnl for network, querying station webservice


def build_scnl_lists(webservice_path: str, query: str) -> list:
    """
    Build a list of scnl found on service
    :param webservice_path: webservice part of request
    :param query: query part of request
    :return: list of scnl
    """
    scnl = []
    url_request = webservice_path + query
    response = requests.get(url_request)
    if response.status_code == 200:
        root = et.fromstring(response.content)
        # print(response.content)
        for child in root.iter('*'):
            if child.tag == '{http://www.fdsn.org/xml/station/1}Network':
                net_code = child.attrib.get('code')
                net_startDate = fix_dates(child.attrib.get('startDate'))
                startend_query = ""
                if net_startDate != "None":
                    startend_query += f'&starttime={net_startDate}'
                net_endDate = fix_dates(child.attrib.get('endDate'))
                if net_endDate != "None":
                    startend_query += f'&endtime={net_endDate}'
                net_identifier = ""
                net_description = ""
                for elem in child.iter('*'):
                    if elem.tag == '{http://www.fdsn.org/xml/station/1}Description':
                        net_description = elem.text
                    if elem.tag == '{http://www.fdsn.org/xml/station/1}Identifier':
                        net_identifier = elem.text
                # print(f'identifier: {net_identifier}')
                # print(f'description: {net_description}')
                query = f'{webservice_path}level=channel&net={net_code}&format=xml&nodata=404' + startend_query
                # debug
                print(query)
                stationxml = requests.get(query)
                if stationxml.status_code == 200:
                    s = et.fromstring(stationxml.content)
                    # debug print (s)
                    station_list = []
                    for element in s.iter():
                        if element.tag == "{http://www.fdsn.org/xml/station/1}Station":
                            station_code = element.attrib.get('code')
                            station_startDate = fix_dates(element.attrib.get('startDate'))
                            station_endDate = fix_dates(element.attrib.get('endDate'))
                            for channel_child in element.iter('*'):
                                if channel_child.tag == "{http://www.fdsn.org/xml/station/1}Channel":
                                    channel_code = channel_child.attrib.get('code')
                                    channel_location = channel_child.attrib.get('location')
                                    channel_startDate = fix_dates(channel_child.attrib.get('startDate'))
                                    channel_endDate = fix_dates(channel_child.attrib.get('endDate'))
                                    station_list.append((net_code, station_code, net_startDate, net_endDate,
                                                        net_identifier, net_description, station_startDate,
                                                        station_endDate, channel_code, channel_location,
                                                        channel_startDate, channel_endDate))
                            scnl += station_list
                else:
                    print(f"station status_code {stationxml.status_code} for {query} ")

    else:
        if response.status_code == 204:
            print(f"Nodata on source")
    return scnl


# Given a path look for scnl defined in the contained xml files
def build_scnl_lists_from_files(dir_path: str, provider: str, network_code: str) -> list:
    """
    Build a list of scnl found on file system
    :param dir_path: path containing xml station files
    :param provider: provider code, match first part of filename
    :param network_code: network code to find on resource
    :return:
    """
    # construct path object
    d = pathlib.Path(dir_path)

    station_list = []

    for entry in d.iterdir():
        # check if it's an interesting file
        if entry.is_file() and entry.match(f'{provider}*.xml'):
            with open(entry, 'rb') as f:
                content = f.read()
            root = et.fromstring(content)
            for child in root.iter('*'):
                if child.tag == '{http://www.fdsn.org/xml/station/1}Network':
                    net_code = child.attrib.get('code')
                    if net_code == network_code:
                        print(entry)
                        net_startDate = fix_dates(child.attrib.get('startDate'))
                        net_endDate = fix_dates(child.attrib.get('endDate'))
                        net_identifier = ""
                        net_description = ""

                        for elem in child.iter('*'):
                            if elem.tag == '{http://www.fdsn.org/xml/station/1}Description':
                                net_description = elem.text
                                # print(f'description: {net_description}')
                                break
                        for elem in child.iter('*'):
                            if elem.tag == '{http://www.fdsn.org/xml/station/1}Identifier':
                                net_identifier = elem.text
                                # print(f'identifier: {net_identifier}')
                                break
                        # print(f'identifier: {net_identifier}')
                        # print(f'description: {net_description}')
                        for element in child.iter():
                            if element.tag == "{http://www.fdsn.org/xml/station/1}Station":
                                station_code = element.attrib.get('code')
                                station_startDate = fix_dates(element.attrib.get('startDate'))
                                station_endDate = fix_dates(element.attrib.get('endDate'))
                                for e in element.iter('*'):
                                    if e.tag == "{http://www.fdsn.org/xml/station/1}Channel":
                                        channel_code = e.attrib.get('code')
                                        channel_location = e.attrib.get('location')
                                        channel_startDate = fix_dates(e.attrib.get('startDate'))
                                        channel_endDate = fix_dates(e.attrib.get('endDate'))
                                        station_list.append((net_code, station_code, net_startDate, net_endDate,
                                                            net_identifier, net_description,
                                                            station_startDate, station_endDate, channel_code,
                                                            channel_location, channel_startDate, channel_endDate))
    scnl = station_list

    if not scnl:
        print(f"Nodata on disk for network {network_code}")
    return scnl


def build_network_lists(webservice_path: str, query: str) -> list:
    """
    Build a list with only network codes matching query
    :param webservice_path: webservice part of request
    :param query: query part of request
    :return: a list containing network codes
    """
    print(webservice_path + query)
    network_list = []
    response = requests.get(webservice_path + query)
    if response.status_code == 200:
        root = et.fromstring(response.content)
        for child in root.iter('*'):
            if child.tag == '{http://www.fdsn.org/xml/station/1}Network':
                net_code = child.attrib.get('code')
                network_list.append(net_code)
    return network_list


def build_network_lists_from_files(dir_path: str) -> list:
    """
    Build a list with only network codes of station files in dir_path
    :param dir_path: path containing xml station files
    :return: a list containing network codes
    """
    network_list = []

    # construct path object
    d = pathlib.Path(dir_path)

    # iterate directory
    for entry in d.iterdir():
        # check if it's an interesting file
        if entry.is_file() and entry.match("*.xml"):
            with open(entry, 'rb') as f:
                content = f.read()
            root = et.fromstring(content)
            for child in root.iter('*'):
                if child.tag == '{http://www.fdsn.org/xml/station/1}Network':
                    netcode = child.attrib.get('code')
                    if netcode not in network_list:
                        network_list.append(netcode)
    return network_list


def get_station_xml(webservice_path: str, provider: str, station: str, path: str, no_save: bool) -> bool:
    """
    Get station data, optionally saved on disk
    :param webservice_path: webservice part of request
    :param provider: provider code, match first part of filename to be saved
    :param station: station code
    :param path: where to save station files 
    :param no_save: optionally don't save 
    :return: true if data found on source
    """
    filename = f'{path}/{provider}{station}.xml'
    query = 'level=response&format=xml&station=' + station
    # To cope with nosave feature introduced current_content to carry station data instead of file
    response = requests.get(webservice_path + query)
    global current_content
    result: bool = False
    if response.status_code == 200:
        if response.encoding != 'utf-8':
            response.encoding = 'utf-8'
        if no_save:
            current_content = response.text.encode("utf-8")
        else:
            print(f'Saving in {filename}')
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
        result = True
    else:
        if response.status_code == 204:
            print(f"Nodata on source")
            result = False
    return result


# To cope with nosave feature introduced current_content to carry station data instead of file
def get_station_xml_from_files(dir_path: str, provider: str, station: str, path: str, no_save: bool) -> bool:
    """
    Get station data from a directory, optionally saved again on disk
    :param dir_path: path containing xml station files
    :param provider: provider code, match first part of filename to be saved
    :param station: station code
    :param path: where to optionally save station files
    :param no_save: optionally don't save
    :return: true if data found on source
    """
    filename = f'{path}/{provider}{station}.xml'
    global current_content
    # construct path object
    d = pathlib.Path(dir_path)
    result = False
    # iterate directory
    for entry in d.iterdir():
        # check if it is a file matching station
        if entry.is_file() and entry.match(f'{provider}{station}.xml'):
            with open(entry, encoding='utf-8') as f:
                content = f.read()
            if no_save:
                current_content = content.encode("utf-8")
            else:
                print(f'Saving in {filename}')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
            result = True
            break
    return result


def put_station_xml(webservice_path: str, provider: str, station: str, path: str, no_save: bool) -> bool:
    """
    Put station in webservice taking optionally from file system
    :param webservice_path: webservice part of request
    :param provider: provider code, match first part of filename
    :param station: station code
    :param path: where to optionally save station files
    :param no_save: optionally don't save
    :return: true if data put on destination
    """
    filename = f'{provider}{station}.xml'
    filepath = f'{path}/{filename}'
    print(webservice_path + " " + provider + " " + station + " " + path)
    result: bool
    global current_content
    if no_save:
        # To cope with nosave feature introduced current_content to carry station data instead of file
        r = requests.put(url=webservice_path, data=current_content,
                         headers={"Content-Type": "application/octet-stream", "filename": filename},
                         auth=HTTPBasicAuth(cfg.AdminUser, cfg.AdminPassword))
        current_content = u''
    else:
        r = requests.put(url=webservice_path, data=open(filepath, 'rb'),
                         headers={"Content-Type": "application/octet-stream", "filename": filename},
                         auth=HTTPBasicAuth(cfg.AdminUser, cfg.AdminPassword))
    if not r.status_code == 200:
        print(f"Error: {r.status_code}")
        print(r.headers)
        result = False
    else:
        result = True
    return result


def delete_station_xml(webservice_path: str, provider: str, station: str):
    """
    Delete station in webservice taking optionally from file system
    :param webservice_path: webservice entrypoint
    :param provider: provider code, match first part of filename
    :param station: station code
    :return: status code
    """
    filename = f'{provider}{station}.xml'
    r = requests.delete(url=webservice_path, headers={"filename": filename},
                        auth=HTTPBasicAuth(cfg.AdminUser, cfg.AdminPassword))
    return r.status_code


def fix_dates(date):
    """
    Get a date string without Z timezone
    :rtype: object
    :param date:
    :return: fixed date string
    """
    return re.sub("Z", "", str(date))


def print_help():
    """
    Print help
    """
    print('Usage: fdsn-station-sync-xml.py [OPTION...]')
    print(
        'Synchronize destination exist-fdsn-station with a fdsnws/station service, or with a directory containing station xml files named like PROVIDER_STATIONCODE.xml')

    print("  -s, --source\t\t\tSource uri")
    print("  -d", "--destination\t\tDestination url")
    print("  -p", "--path\t\t\tTemporary files path")
    print("  -q", "--query\t\t\tQuery to select stations to sync [level=channel]")
    print("  -P", "--provider\t\t\tprovider code, uppercase")
    print("  -f", "--force-station\t\tComma separated station list, if present sync only this stations")
    # print("  -S\t\t\t\tStationonly = True") TODO REMOVE
    print("  -v\t\t\t\tUse virtualnetworks service [INGV only]")
    # print("  -c", "--check_sensor_desc\t\t\t") TODO
    print("  -l", "--leave_unmatched\t\tLeave stations on destination even when not found on source")
    print("  -e", "--existdb-source\t\tSource with exist-fdsn-station url prefix")
    print("  -x", "--existdb-destination\tDestination with exist-fdsn-station url prefix")
    print("  -n", "--no-save\t\t\tDo not save station files in temporary files path")
    print("  -h", "--help\t\t\tprint this help")
    print(
        '\n\n  Example 1: fdsn-station-sync-xml.py -v -s https://webservices.ingv.it -d http://172.17.0.2:8080 -p /tmp -q "level=channel&network=*&format=xml&includerestricted=true"')
    print(
        '  Example 2: fdsn-station-sync-xml.py -s file:///opt/Station -d http://127.0.0.1:80  -p /tmp  -x -P INGV -l"')
    print(
        '  Example 3: fdsn-station-sync-xml.py -s https://webservices.ingv.it -d http://172.17.0.2:8080 -p /tmp --force-station="ACER,AMUR" ')


def main(argv):
    Source = 'webservices.ingv.it'
    Destination = '172.17.0.2:8080'
    Path = '/tmp'
    Query = "level=channel&network=*&format=xml&includerestricted=true"

    virtualNetworks = False
    CheckSensorDescription = False
    LeaveUnmatched = False
    ExistDBSource = False
    ExistDBDestination = False
    Provider = ""
    SourcePath = ""
    Station = ""
    OK = True
    NoSave = False
    # To cope with nosave feature introduced current_content to carry station data instead of file
    global current_content
    try:
        opts, args = getopt.getopt(argv, "s:d:p:q:P:f:cexlhnv",
                                   ["source=", "destination=", "path=", "query=", "provider=", "force-station=",
                                    "check_sensor_desc", "existdb-source", "existdb-destination", "leave_unmatched",
                                    "help", "no-save"])
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
        elif opt in ("-n", "--no-save"):
            NoSave = True
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
            print_help()
            sys.exit()
    networks = ""
    if virtualNetworks:
        AN.build_alternate_network_file(url='http://webservices.ingv.it/ingvws/virtualnetwork/1/codes',
                                        filename=f'{Path}/AlternateNetwork.xml')
        networks = AN.build_alternate_network_lists(filename=f'{Path}/AlternateNetwork.xml')


    print("provider: " + Provider)
    source_parse: ParseResult = urlparse(Source)
    SourceURL = ""
    if source_parse.scheme.startswith('http'):
        if ExistDBSource:
            SourceURL = Source + "/exist/apps/fdsn-station/fdsnws/station/1/query?"
        else:
            SourceURL = Source + "/fdsnws/station/1/query?"
        print(f'Reading from {SourceURL}')
    if source_parse.scheme == 'file':
        SourcePath = source_parse.path
        print(f'Reading from {SourcePath}')
    if ExistDBDestination:
        DestinationURL = Destination + "/exist/apps/fdsn-station/fdsnws/station/1/query?"
    else:
        DestinationURL = Destination + "/fdsnws/station/1/query?"
    print(f'Writing into {DestinationURL}')

    if Station == "":
        if SourcePath == "":
            SourceNetworks = build_network_lists(SourceURL, Query)
        else:
            SourceNetworks = build_network_lists_from_files(SourcePath)

        DestinationNetworks = build_network_lists(DestinationURL, Query)
        if not LeaveUnmatched:
            AllnetworksList = list(set(SourceNetworks + DestinationNetworks))
        else:
            setSN = set(SourceNetworks)
            setDN = set(DestinationNetworks)
            # #85 FIX: union take stations of networks missing on destination
            AllnetworksList = list(setDN.intersection(setSN).union(setSN))
        print(AllnetworksList)

        for net_code in AllnetworksList:
            print(f'Elaborating network {net_code} on source')
            if SourcePath == "":
                SourceSCNL = build_scnl_lists(SourceURL, f"level=network&network={net_code}")
            else:
                SourceSCNL = build_scnl_lists_from_files(SourcePath, Provider, net_code)
            # print(SourceSCNL)
            setSourceSCNL = set(SourceSCNL)
            if setSourceSCNL or (not LeaveUnmatched):
                print(f'Elaborating network {net_code} on destination')
                DestinationSCNL = build_scnl_lists(DestinationURL, f"level=network&network={net_code}")
                setDestinationSCNL = set(DestinationSCNL)
                # print(setDestinationSCNL)
                if setSourceSCNL == setDestinationSCNL:
                    print(f"{net_code} in sync")
                else:
                    setMissingOnDest = setSourceSCNL - setDestinationSCNL
                    missing_stationset: Set[str] = set()
                    destination_stationset: Set[str] = set()
                    for scnl in setMissingOnDest:
                        missing_stationset.add("".join(scnl[1:2]))
                    
                    setMissingOnSource = setDestinationSCNL - setSourceSCNL

                    for scnl in setMissingOnSource:
                        destination_stationset.add("".join(scnl[1:2]))

                    if len(destination_stationset) > 0 and (not LeaveUnmatched):
                        print("Some station on destination differ from source")
                        print(destination_stationset)
                        print('Removing unmatched stations from destination')
                        removed_stationset = set()
                        for station in destination_stationset:
                            print('Trying removing station ' + Provider + station + ' on destination ' + Destination)
                            response_status = delete_station_xml(DestinationURL, Provider, station)
                            if response_status == 200:
                                removed_stationset.add(station)
                            else:
                                OK = False
                                print(f'Failed removing, provider and station mismatch {response_status}')
                        for station in removed_stationset:
                            print('Attempting to revive station ' + Provider + station)
                            if SourcePath == "":
                                resp = get_station_xml(SourceURL, Provider, station, Path, NoSave)
                                OK &= resp
                            else:
                                get_station_xml_from_files(SourcePath, Provider, station, Path, NoSave)
                            if virtualNetworks:
                                if NoSave:
                                    current_content = AN.add_virtual_networks_indata(current_content, station, networks, 
                                                                                     Path+"/"+'AlternateNetwork.xml')
                                else:
                                    AN.add_virtual_networks(Path + "/" + Provider + station + '.xml', station, networks,
                                                            Path + "/" + 'AlternateNetwork.xml')
                            resp = put_station_xml(DestinationURL, Provider, station, Path, NoSave)
                            OK &= resp
                    # stations with missing channels
                    for station in missing_stationset:
                        print('Syncing station ' + Provider + station)
                        if SourcePath == "":
                            get_station_xml(SourceURL, Provider, station, Path, NoSave)
                        else:
                            get_station_xml_from_files(SourcePath, Provider, station, Path, NoSave)
                        if virtualNetworks:
                            if NoSave:
                                current_content = AN.add_virtual_networks_indata(current_content, station, networks,
                                                                                 Path + "/" + 'AlternateNetwork.xml')
                            else:
                                # adds in station file the alternate snippet
                                AN.add_virtual_networks(Path + "/" + Provider + station + '.xml', station, networks,
                                                        Path + "/" + 'AlternateNetwork.xml')
                        # time.sleep(1)
                        resp: bool = put_station_xml(DestinationURL, Provider, station, Path, NoSave)
                        OK &= resp

    else:
        print(f'Requested to upload: {Station}')
        stationlist = Station.split(',')
        missing_stationset = set(stationlist)

        for station in missing_stationset:
            read_station: bool
            print('Syncing station ' + Provider + station)
            if SourcePath == "":
                read_station = get_station_xml(SourceURL, Provider, station, Path, NoSave)
            else:
                read_station = get_station_xml_from_files(SourcePath, Provider, station, Path, NoSave)
            if virtualNetworks and read_station:
                if NoSave:
                    current_content = AN.add_virtual_networks_indata(current_content, station, networks,
                                                                     Path + "/" + 'AlternateNetwork.xml')
                else:
                    # add in station file the alternate snippet
                    AN.add_virtual_networks(Path + "/" + Provider + station + '.xml', station, networks,
                                            Path + "/" + 'AlternateNetwork.xml')
                print(f'Forcing upload of {station}')
            if read_station:
                resp: bool = put_station_xml(DestinationURL, Provider, station, Path, NoSave)
                OK &= resp
            else:
                OK = False
                print(f'An error occurred processing {station}')

    if OK:
        print('Synced')
    else:
        print('Synced, with errors')


if __name__ == "__main__":
    main(sys.argv[1:])
