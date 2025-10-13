# Create an xml file containing the AlternateNetwork Elements to be placed in
# StationXML (pip install python-dateutil)
import requests
import sys
import json
import datetime
from dateutil import parser



service_url='https://www.orfeus-eu.org/eidaws/routing/1/'

class Routing:
    def __init__(self,service_url,service_name):
        self.service_url = service_url
        try:
            print(f'Checking with routing service')
            r = requests.get(service_url+'query?format=json&service='+service_name)
            self.data = r.content
            # print(r.status_code)
            self.routing = json.loads(self.data)
        except:
            print("Error loading routing resource")
    def print(self):
        print(f'From: {self.service_url}')
        # print(self.routing) all the json in output
        # print pretty by json.dumps
        # print(json.dumps(self.routing, indent=2))
        # List of dictionaries, print once a time
        for d in self.routing :
            # now we have keys: name url params
            name = d.get('name')
            url = d.get('url')
            params = d.get('params')
            print(f'name: {name}')
            print(f'url: {url}')

            # params other list of dictionaries
            # print(json.dumps(d.params))
            for p in params :
                # p is a dictionary with keys: net, sta, loc, cha, start, end, priority
                net = p.get('net', 'None')
                sta = p.get('sta', 'None')
                loc = p.get('loc', 'None')
                cha = p.get('cha', 'None')
                start = p.get('start', 'None')
                end = p.get('end', 'None')
                priority = p.get('priority', 'None')
                print(f'{net} {sta} {loc} {cha} {start} {end} {priority}')
                # print(json.dumps(p))
    def check_station(self,name,url,network,station,location,channel,start,end,priority=1):
        # check_service_name
        # if service_name =
        # check_network_station_location_channel_start_end_priority
        found = False
        #print(name, url, network, station, location, channel, start, end)
        for d in self.routing:
            # now we have keys: name url params
            service_name = d.get('name')
            service_url  = d.get('url')

            params = d.get('params')
            # print(f'name: {service_name}')
            # print(f'url: {service_url}')

            # params other list of dictionaries
            # print(json.dumps(d.params))
            for p in params:
                # p is a dictionary with keys: net, sta, loc, cha, start, end, priority
                service_net = p.get('net', '')
                service_sta = p.get('sta', '')
                service_loc = p.get('loc', '')
                service_cha = p.get('cha', '')
                service_start = p.get('start', '')
                service_end = p.get('end', '')
                service_priority = p.get('priority', '')
                #print(f"service_net: {service_net} service_sta: {service_sta} service_loc: {service_loc} service_cha: {service_cha}")
                try:
                    if ( self.match(service_net, network) and self.match(service_sta, station) and
                         self.match(service_loc, location) and self.match(service_cha, channel) and
                         self.datematch(service_start, service_end, start, end) and
                         self.match(service_priority, priority) and self.match(service_url, url)):
                        found = True
                        break
                except:
                    print(f'Error with {network} {station} {location} {channel} {start}  {end} {priority}')
                    break
            if found:
                break

        # if found:
        #     print('Found')
        # else:
        #     print('Missing')
        if not found:
            print(f'Not found: {network} {station} {location} {channel} {start} {end} {priority}')
        return found

    def match(self, service, param):
        match = False
        if service == '*':
            match = True
            # print(f'Trovato in: {service} il parametro: {param}')
        else:
            if service == param:
                match = True
            #     print(f'Trovato in: {service} il parametro: {param}')
            # else:
            #     print(f'Non trovato in: {service} il parametro: {param}')
        return match

    def datematch(self, service_start, service_end, param_start, param_end):
        # se param_start è maggiore o uguale di service_start e minore di service_end
        # e se param_end * maggiore di service_start e minore o uguale a service_end
        # allora il periodo di param è compreso in quello del servizio, quindi match è true
        # se service_end è vuoto la seconda condizione non è mai necessario esaminarla
        # print(f'datematch({service_start}, {service_end}, {param_start}, {param_end})')
        today = datetime.datetime.now()

        match = False
        left_match = False
        right_match = False
        service_start_time = None
        service_end_time = None
        param_start_time = None
        param_end_time = None

        if service_start != '':
            service_start_time = parser.parse(service_start)
        if service_end != '':
            service_end_time = parser.parse(service_end)
        if param_start != '':
            param_start_time = parser.parse(param_start)
        if param_end != '':
            param_end_time = parser.parse(param_end)


        if service_start == param_start and service_end == param_end:
           match = True
        else:
            if param_start_time >= service_start_time:
                left_match = True
                # print(f'Left match')
            if service_end_time is None:
                right_match = True
                # print(f'Right match 1')
            else:
                # print(f'Loooking for match 2')
                if param_end_time is not None and param_end_time <= service_end_time:
                    right_match = True
                    # print(f'Right match 2')
                else:
                    # print(f'Loooking for match 3')
                    #Patch for date of routing closing before channel closing but still a valid match for today (7F)
                    if param_end_time is not None and param_end_time > today and service_end_time > today:
                        right_match = True
                    if param_end_time is None and service_end_time > today:
                        right_match = True

        if left_match and right_match:
            match = True
        return match


def main(argv):
    print(datetime.datetime.now())
    R = Routing('https://www.orfeus-eu.org/eidaws/routing/1/','station')
    print(datetime.datetime.now())
    # R.print()
    # print(datetime.datetime.now())
    # R.check_station('station','https://webservices.ingv.it/fdsnws/station/1/query','Z3', 'A300A', '*', '*', '2015-10-28T09:00:00', '2019-04-10T23:59:00', 1)
    # R.check_station('station','https://webservices.ingv.it/fdsnws/station/1/query','AC','*','*','*','2002-01-01T00:00:00','',3)
    # R.check_station('station', 'https://webservices.ingv.it/fdsnws/station/1/query', 'PP', 'A300A', '*', '*', '2015-10-28T09:00:00', '2019-04-10T23:59:00', 1)
    # result = R.check_station('station', 'https://eida.bgs.ac.uk/fdsnws/station/1/query', 'GB', 'GAL1', '*', '*', '2009-02-16T00:00:00', '2009-03-29T00:00:00', 1)
    # result = R.check_station('station', 'https://eida.bgs.ac.uk/fdsnws/station/1/query', 'UR', 'AP12', '', 'HHE', '2023-12-09T00:00:00 ', '2009-03-29T00:00:00', 1)
    # result = R.check_station('station', 'https://webservices.ingv.it/fdsnws/station/1/query', 'IV', 'ACATE', '', 'HHZ', '2019-02-28T05:59:00', '', 1)
    # result = R.check_station('station', 'https://eida.ethz.ch/fdsnws/station/1/query', '9S', 'ILL12', '', 'EHE', '2018-05-14T17:00:00', '2018-05-14T17:00:01', 1)
    # result = R.check_station('station', 'https://webservices.ingv.it/fdsnws/station/1/query', '7F', 'SIB2', '*', '*', '2021-10-20T14:46:00', '', 1)
    # result = R.check_station('station', 'https://webservices.ingv.it/fdsnws/station/1/query', '5H', 'FR02', '*', '*', '2021-07-15T14:50:00', '', 1)
    # result = R.check_station('station', 'https://geofon.gfz.de/fdsnws/station/1/query', '1D', 'LIB00', '', 'DP3', '2023-09-10T16:00:00', '2036-01-01T00:00:00', 1)
    # result = R.check_station('station', 'https://eida.ethz.ch/fdsnws/station/1/query', 'Z3', 'A291A', '', 'HHZ', '2015-09-22T17:00:00', '2021-04-27T17:00:00', 1)
    # result = R.check_station('station', 'https://geofon.gfz.de/fdsnws/station/1/query', '1M', 'D34', '', 'BHZ','2006-06-21T00:00:00', '2015-12-31T00:00:00', 1)
    # result = R.check_station('station', 'https://geofon.gfz.de/fdsnws/station/1/query', 'DK', 'KULLO', '', 'HHE','2009-07-18T00:00:00', '', 1)
    result = R.check_station('station', 'https://eida.ethz.ch/fdsnws/station/1/query', 'DK', 'KULLO', '', 'HHE','2009-07-18T00:00:00', '', 1)

    print(datetime.datetime.now())
    print(f'Result: {result}')

if __name__ == "__main__":
   main(sys.argv[1:])
