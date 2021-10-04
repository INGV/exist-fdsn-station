#!/usr/bin/env python
# coding: utf-8


import requests
import pytest
import conftest
import difflib
#import xml.etree.ElementTree as ET
#from io import StringIO
import lxml.etree as ET
from xmldiff import main, formatting

############################################# DATA FOR TEST #############################################


### Contains query string, expected response code
testdataxml = [
        ("level=network&net=MN&station=AQ*&format=xml&nodata=404",200,'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.1" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.1.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.1</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?level=network&amp;net=MN&amp;station=AQ*&amp;format=xml&amp;nodata=404</ModuleURI><Created>2021-02-14T17:11:37.475Z</Created><Network code="MN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Mediterranean Very Broadband Seismographic Network</Description><Identifier type="DOI">10.13127/SD/fBBBtDtd6q</Identifier><ingv:Identifier>N22</ingv:Identifier><TotalNumberStations>2</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations></Network></FDSNStationXML>',"Selection in the future"),
        ("level=station&nodata=404",200,'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.1" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.1.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.2</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?level=station&amp;nodata=404</ModuleURI><Created>2021-09-05T17:47:58.083+02:00</Created><Network code="IV" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Italian Seismic Network</Description><Identifier type="DOI">10.13127/SD/X0FXnH7QfY</Identifier><ingv:Identifier>N1</ingv:Identifier><TotalNumberStations>7</TotalNumberStations><SelectedNumberStations>7</SelectedNumberStations><Station code="ACATE" startDate="2019-02-28T05:59:00" restrictedStatus="open"><ingv:Identifier>S7381</ingv:Identifier><Latitude>37.02398</Latitude><Longitude>14.50064</Longitude><Elevation>210</Elevation><Site><Name>ACATE</Name></Site><CreationDate>2019-02-28T05:59:00</CreationDate></Station><Station code="ACER" startDate="2007-07-05T12:00:00" restrictedStatus="open"><ingv:Identifier>S1</ingv:Identifier><Latitude>40.7867</Latitude><Longitude>15.9427</Longitude><Elevation>690</Elevation><Site><Name>Acerenza</Name></Site><CreationDate>2007-07-05T12:00:00</CreationDate></Station><Station code="AQT1" startDate="2011-07-22T00:00:00" endDate="2016-09-01T09:50:00" restrictedStatus="open"><ingv:Identifier>S578</ingv:Identifier><Latitude>42.77383</Latitude><Longitude>13.2935</Longitude><Elevation>770</Elevation><Site><Name>Arquata del Tronto</Name></Site><CreationDate>2011-07-22T00:00:00</CreationDate><TerminationDate>2016-09-01T23:59:00</TerminationDate></Station><Station code="AQU" startDate="2003-03-01T00:00:00" endDate="2008-10-15T00:00:00" restrictedStatus="open"><ingv:Identifier>S7</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Site><Name>L\'Aquila, Italy</Name></Site><CreationDate>1988-08-01T00:00:00</CreationDate></Station><Station code="ARVD" startDate="2003-03-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S9</ingv:Identifier><Latitude>43.49807</Latitude><Longitude>12.94153</Longitude><Elevation>461</Elevation><Site><Name>ARCEVIA 2</Name></Site><CreationDate>2003-03-01T00:00:00</CreationDate></Station><Station code="IMTC" startDate="1988-01-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S3001</ingv:Identifier><Latitude>40.7209</Latitude><Longitude>13.8758</Longitude><Elevation>59</Elevation><Site><Name>Ischia - Monte Corvo</Name></Site><CreationDate>1988-01-01T00:00:00</CreationDate></Station><Station code="VBKN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S3031</ingv:Identifier><Latitude>40.83</Latitude><Longitude>14.4299</Longitude><Elevation>951</Elevation><Site><Name>Vesuvio - Bunker Nord</Name></Site><CreationDate>1988-01-01T00:00:00</CreationDate></Station></Network><Network code="IX" startDate="2005-01-01T00:00:00" restrictedStatus="open"><Description>Irpinia Seismic Network, Italy</Description><ingv:Identifier>N41</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="AND3" startDate="2013-12-17T00:00:00" restrictedStatus="open"><ingv:Identifier>S6221</ingv:Identifier><Latitude>40.9298</Latitude><Longitude>15.3331</Longitude><Elevation>905</Elevation><Site><Name>Station Andretta, Italy</Name></Site><CreationDate>2013-12-17T00:00:00</CreationDate></Station></Network><Network code="MN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Mediterranean Very Broadband Seismographic Network</Description><Identifier type="DOI">10.13127/SD/fBBBtDtd6q</Identifier><ingv:Identifier>N22</ingv:Identifier><TotalNumberStations>2</TotalNumberStations><SelectedNumberStations>2</SelectedNumberStations><Station code="AQU" startDate="1988-08-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S7</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Site><Name>L\'Aquila, Italy</Name></Site><CreationDate>1988-08-01T00:00:00</CreationDate></Station><Station code="ARPR" startDate="2014-01-23T00:00:00" restrictedStatus="open"><ingv:Identifier>S2151</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Site><Name>Arapgir, Turkey</Name></Site><CreationDate>2014-01-23T00:00:00</CreationDate></Station></Network><Network code="NI" startDate="2002-01-01T00:00:00" restrictedStatus="open"><Description>North-East Italy Broadband Network</Description><ingv:Identifier>N13</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="ACOM" startDate="2005-02-01T12:00:00" endDate="2015-12-31T23:59:59" restrictedStatus="open"><ingv:Identifier>S3451</ingv:Identifier><Latitude>46.548</Latitude><Longitude>13.5137</Longitude><Elevation>1788</Elevation><Site><Name>Acomizza</Name></Site><CreationDate>2005-02-01T12:00:00</CreationDate></Station></Network><Network code="OX" startDate="2016-01-01T00:00:00" restrictedStatus="open"><Description>North-East Italy Seismic Network</Description><ingv:Identifier>N111</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="ACOM" startDate="2016-01-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S3451</ingv:Identifier><Latitude>46.548</Latitude><Longitude>13.5137</Longitude><Elevation>1788</Elevation><Site><Name>Acomizza</Name></Site><CreationDate>2005-02-01T12:00:00</CreationDate></Station></Network><Network code="SI" startDate="2006-01-01T00:00:00" restrictedStatus="open"><Description>Sudtirol Network, Italy</Description><Identifier type="citation">Pintore et al. Multiple Identifier</Identifier><Identifier type="DOI">https://doi.org/10.7914/SN/3T_2020</Identifier><ingv:Identifier>N18</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="ABSI" startDate="2006-11-21T14:16:45" restrictedStatus="open"><ingv:Identifier>S122</ingv:Identifier><Latitude>46.7285</Latitude><Longitude>11.3205</Longitude><Elevation>1801</Elevation><Site><Name>Aberstuckl (Sarntal)</Name></Site><CreationDate>2006-11-21T14:16:45</CreationDate></Station></Network><Network code="Z3" startDate="2015-01-01T00:00:00" endDate="2022-12-31T00:00:00" restrictedStatus="closed"><Description>AlpArray Seismic Network (AASN) temporary component</Description><Identifier type="DOI">10.12686/alparray/z3_2015</Identifier><ingv:Identifier>N81</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="A319A" startDate="2015-12-11T12:06:34" endDate="2019-04-10T23:59:00" restrictedStatus="closed"><ingv:Identifier>S3331</ingv:Identifier><Latitude>43.476425</Latitude><Longitude>10.578689</Longitude><Elevation>343</Elevation><Site><Name>Santa Luce (PI)</Name></Site><CreationDate>2015-12-11T12:06:34</CreationDate><TerminationDate>2019-04-11T23:59:00</TerminationDate></Station></Network></FDSNStationXML>',"query_core_full_data"),
        ("level=station&net=MN&format=xml&nodata=404",200,'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.1" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.1.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.1</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?level=station&amp;net=MN&amp;format=xml&amp;nodata=404</ModuleURI><Created>2021-02-14T15:17:35.305Z</Created><Network code="MN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Mediterranean Very Broadband Seismographic Network</Description><Identifier type="DOI">10.13127/SD/fBBBtDtd6q</Identifier><ingv:Identifier>N22</ingv:Identifier><TotalNumberStations>2</TotalNumberStations><SelectedNumberStations>2</SelectedNumberStations><Station code="AQU" startDate="1988-08-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S7</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Site><Name>L\'Aquila, Italy</Name></Site><CreationDate>1988-08-01T00:00:00</CreationDate></Station><Station code="ARPR" startDate="2014-01-23T00:00:00" restrictedStatus="open"><ingv:Identifier>S2151</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Site><Name>Arapgir, Turkey</Name></Site><CreationDate>2014-01-23T00:00:00</CreationDate></Station></Network></FDSNStationXML>',"All stations in MedNet"),
        ("level=station&format=xml&starttime=2021-02-05T09:16:49&endtime=2021-02-05T09:22:09&cha=EH*&nodata=404",200,'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.1" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.1.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.1</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?level=station&amp;format=xml&amp;starttime=2021-02-05T09:16:49&amp;endtime=2021-02-05T09:22:09&amp;cha=EH*&amp;nodata=404</ModuleURI><Created>2021-02-14T14:49:01.534Z</Created><Network code="IV" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Italian Seismic Network</Description><Identifier type="DOI">10.13127/SD/X0FXnH7QfY</Identifier><ingv:Identifier>N1</ingv:Identifier><TotalNumberStations>7</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="ACATE" startDate="2019-02-28T05:59:00" restrictedStatus="open"><ingv:Identifier>S7381</ingv:Identifier><Latitude>37.02398</Latitude><Longitude>14.50064</Longitude><Elevation>210</Elevation><Site><Name>ACATE</Name></Site><CreationDate>2019-02-28T05:59:00</CreationDate></Station></Network></FDSNStationXML>',""),

        ("level=channel&net=MN&format=xml&nodata=404",200,'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.1" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.1.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.1</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?level=channel&amp;net=MN&amp;format=xml&amp;nodata=404</ModuleURI><Created>2021-02-14T15:24:55.099Z</Created><Network code="MN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Mediterranean Very Broadband Seismographic Network</Description><Identifier type="DOI">10.13127/SD/fBBBtDtd6q</Identifier><ingv:Identifier>N22</ingv:Identifier><TotalNumberStations>2</TotalNumberStations><SelectedNumberStations>2</SelectedNumberStations><Station code="AQU" startDate="1988-08-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S7</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Site><Name>L\'Aquila, Italy</Name></Site><CreationDate>1988-08-01T00:00:00</CreationDate><TotalNumberChannels>151</TotalNumberChannels><SelectedNumberChannels>151</SelectedNumberChannels><Channel code="BHE" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2469</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-5250000000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHE" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2481</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-1046640000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHE" startDate="1995-08-28T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2493</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1047020000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHE" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2509</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1075730000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHE" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2521</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-1063680000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHE" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2533</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1063680000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHE" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2545</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>983662000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHE" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2557</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>592092000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHE" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2572</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780269000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHE" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13221</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780000000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHE" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82391</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2470</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-5250000000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2482</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-1055040000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="1995-08-28T00:00:00" endDate="1996-09-05T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2494</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1049580000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="1996-09-06T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2505</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1059600000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2510</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1091140000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2522</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-1092770000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2534</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1092770000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2546</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1014990000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2558</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>600347000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2573</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>778823000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13181</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780000000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82311</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2471</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-5250000000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2483</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-1054200000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="1995-08-28T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2495</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1062530000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2511</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1044970000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2523</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-1069590000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2535</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1069590000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2547</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1001740000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2559</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>598652000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2574</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>778718000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13261</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780000000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82351</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHE" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2560</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>592092000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHE" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2575</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780269000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHE" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13231</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780000000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHE" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82401</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHN" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2561</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>600347000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHN" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2576</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>778823000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHN" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13191</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780000000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHN" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82321</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2562</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>598652000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2577</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>778718000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13271</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780000000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82361</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HLE" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2587</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>KINEMETRICS EPISENSOR</Description></Sensor><Response><InstrumentSensitivity><Value>534331</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S**2</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HLE" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13311</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>KINEMETRICS EPISENSOR</Description></Sensor><Response><InstrumentSensitivity><Value>530244</Value><Frequency>0.2</Frequency><InputUnits><Name>M/S**2</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HLN" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2588</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>KINEMETRICS EPISENSOR</Description></Sensor><Response><InstrumentSensitivity><Value>537500</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S**2</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HLN" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13301</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>KINEMETRICS EPISENSOR</Description></Sensor><Response><InstrumentSensitivity><Value>530244</Value><Frequency>0.2</Frequency><InputUnits><Name>M/S**2</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HLZ" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2589</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>KINEMETRICS EPISENSOR</Description></Sensor><Response><InstrumentSensitivity><Value>537691</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S**2</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HLZ" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13321</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>KINEMETRICS EPISENSOR</Description></Sensor><Response><InstrumentSensitivity><Value>530244</Value><Frequency>0.2</Frequency><InputUnits><Name>M/S**2</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HNE" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82451</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP</Description></Sensor><Response><InstrumentSensitivity><Value>427693</Value><Frequency>0.2</Frequency><InputUnits><Name>M/S**2</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HNN" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82431</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP</Description></Sensor><Response><InstrumentSensitivity><Value>427693</Value><Frequency>0.2</Frequency><InputUnits><Name>M/S**2</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HNZ" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82441</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP</Description></Sensor><Response><InstrumentSensitivity><Value>427693</Value><Frequency>0.2</Frequency><InputUnits><Name>M/S**2</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2472</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-21000000000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2484</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-4186560000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="1995-08-28T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2496</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1047020000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2512</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1075730000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2524</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-1063680000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2536</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1063680000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2548</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>983662000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2563</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>592092000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2578</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780269000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13241</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780000000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82411</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2473</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-21000000000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2485</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-4220160000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="1995-08-28T00:00:00" endDate="1996-09-05T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2497</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1049580000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="1996-09-06T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2506</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1059600000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2513</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1091140000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2525</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-1092770000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2537</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1092770000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2549</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1014990000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2564</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>600347000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2579</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>778823000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13201</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780000000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82331</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2474</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-21000000000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2486</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-4216800000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="1995-08-28T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2498</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1062530000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2514</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1044970000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2526</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-1069590000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2538</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1069590000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2550</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1001740000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2565</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>598652000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2580</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>778718000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13281</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780000000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82371</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHE" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2475</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-84000000000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHE" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2487</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-16746200000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHE" startDate="1995-08-28T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2499</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4188090000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHE" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2515</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4302930000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHE" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2527</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-4254720000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHE" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2539</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4254720000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHE" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2551</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>3934650000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHE" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2566</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>2368370000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHE" startDate="2008-02-19T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2581</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>3121070000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHN" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2476</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-84000000000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHN" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2488</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-16880600000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHN" startDate="1995-08-28T00:00:00" endDate="1996-09-05T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2500</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4198310000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHN" startDate="1996-09-06T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2507</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4238420000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHN" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2516</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4364570000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHN" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2528</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-4371080000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHN" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2540</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4371080000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHN" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2552</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4059940000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHN" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2567</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>2401390000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHN" startDate="2008-02-19T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2582</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>3115290000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHZ" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2477</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-84000000000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHZ" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2489</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-16867200000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHZ" startDate="1995-08-28T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2501</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4250120000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHZ" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2517</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4179890000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHZ" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2529</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-4278370000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHZ" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2541</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4278370000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHZ" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2553</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4006970000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHZ" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2568</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>2394610000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHZ" startDate="2008-02-19T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2583</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>3114870000</Value><Frequency>0.003</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2478</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-84000000000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2490</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-16746200000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="1995-08-28T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2502</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4188090000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2518</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4302930000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2530</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-4254720000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2542</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4254720000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2554</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>3934650000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2569</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>2368370000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2584</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>3121070000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13251</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>3120000000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82421</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2479</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-84000000000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2491</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-16880600000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="1995-08-28T00:00:00" endDate="1996-09-05T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2503</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4198310000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="1996-09-06T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2508</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4238420000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2519</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4364570000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2531</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-4371080000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2543</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4371080000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2555</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4059940000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2570</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>2401390000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2585</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>3115290000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13211</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>3120000000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82341</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2480</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-84000000000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2492</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-16867200000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="1995-08-28T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2504</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4250120000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2520</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4179890000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2532</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-4278370000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2544</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4278370000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2556</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4006970000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2571</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>2394610000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2586</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>3114870000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13291</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>3120000000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82381</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel></Station><Station code="ARPR" startDate="2014-01-23T00:00:00" restrictedStatus="open"><ingv:Identifier>S2151</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Site><Name>Arapgir, Turkey</Name></Site><CreationDate>2014-01-23T00:00:00</CreationDate><TotalNumberChannels>9</TotalNumberChannels><SelectedNumberChannels>9</SelectedNumberChannels><Channel code="BHE" startDate="2014-01-23T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C27341</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Depth>0</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-3G</Description></Sensor><Response><InstrumentSensitivity><Value>2516580000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="2014-01-23T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C27351</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-3G</Description></Sensor><Response><InstrumentSensitivity><Value>2516580000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="2014-01-23T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C27361</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-3G</Description></Sensor><Response><InstrumentSensitivity><Value>2516580000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="2014-01-23T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C27401</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Depth>0</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-3G</Description></Sensor><Response><InstrumentSensitivity><Value>2516580000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="2014-01-23T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C27411</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-3G</Description></Sensor><Response><InstrumentSensitivity><Value>2516580000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="2014-01-23T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C27421</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-3G</Description></Sensor><Response><InstrumentSensitivity><Value>2516580000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="2014-01-23T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C27521</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Depth>0</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-3G</Description></Sensor><Response><InstrumentSensitivity><Value>10066300000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="2014-01-23T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C27531</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-3G</Description></Sensor><Response><InstrumentSensitivity><Value>10066300000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="2014-01-23T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C27541</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-3G</Description></Sensor><Response><InstrumentSensitivity><Value>10066300000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel></Station></Network></FDSNStationXML>',""),



        ("level=channel&net=MN,IV&format=xml&nodata=404&station=AQU,ACER&channel=HHZ,EHZ",200,'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.1" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.1.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.1</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?level=channel&amp;net=MN,IV&amp;format=xml&amp;nodata=404&amp;station=AQU,ACER&amp;channel=HHZ,EHZ</ModuleURI><Created>2021-02-14T15:28:37.803Z</Created><Network code="IV" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Italian Seismic Network</Description><Identifier type="DOI">10.13127/SD/X0FXnH7QfY</Identifier><ingv:Identifier>N1</ingv:Identifier><TotalNumberStations>7</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="ACER" startDate="2007-07-05T12:00:00" restrictedStatus="open"><ingv:Identifier>S1</ingv:Identifier><Latitude>40.7867</Latitude><Longitude>15.9427</Longitude><Elevation>690</Elevation><Site><Name>Acerenza</Name></Site><CreationDate>2007-07-05T12:00:00</CreationDate><TotalNumberChannels>33</TotalNumberChannels><SelectedNumberChannels>2</SelectedNumberChannels><Channel code="HHZ" startDate="2007-07-05T12:00:00" endDate="2014-05-08T11:42:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C6</ingv:Identifier><Latitude>40.7867</Latitude><Longitude>15.9427</Longitude><Elevation>690</Elevation><Depth>1</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>1500000000</Value><Frequency>0.2</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2014-05-08T11:42:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C27281</ingv:Identifier><Latitude>40.7867</Latitude><Longitude>15.9427</Longitude><Elevation>690</Elevation><Depth>1</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>1179650000</Value><Frequency>0.2</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel></Station></Network><Network code="MN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Mediterranean Very Broadband Seismographic Network</Description><Identifier type="DOI">10.13127/SD/fBBBtDtd6q</Identifier><ingv:Identifier>N22</ingv:Identifier><TotalNumberStations>2</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="AQU" startDate="1988-08-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S7</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Site><Name>L\'Aquila, Italy</Name></Site><CreationDate>1988-08-01T00:00:00</CreationDate><TotalNumberChannels>151</TotalNumberChannels><SelectedNumberChannels>4</SelectedNumberChannels><Channel code="HHZ" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2562</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>598652000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2577</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>778718000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13271</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780000000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82361</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>M/S</Name></InputUnits><OutputUnits><Name>COUNTS</Name></OutputUnits></InstrumentSensitivity></Response></Channel></Station></Network></FDSNStationXML>',""),



("level=station&net=MN,IV&format=xml&nodata=404&station=AQU,ACER&channel=HHZ,EHZ",200,'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.1" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.1.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.1</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?level=station&amp;net=MN,IV&amp;format=xml&amp;nodata=404&amp;station=AQU,ACER&amp;channel=HHZ,EHZ</ModuleURI><Created>2021-02-14T15:36:22.336Z</Created><Network code="IV" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Italian Seismic Network</Description><Identifier type="DOI">10.13127/SD/X0FXnH7QfY</Identifier><ingv:Identifier>N1</ingv:Identifier><TotalNumberStations>7</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="ACER" startDate="2007-07-05T12:00:00" restrictedStatus="open"><ingv:Identifier>S1</ingv:Identifier><Latitude>40.7867</Latitude><Longitude>15.9427</Longitude><Elevation>690</Elevation><Site><Name>Acerenza</Name></Site><CreationDate>2007-07-05T12:00:00</CreationDate></Station></Network><Network code="MN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Mediterranean Very Broadband Seismographic Network</Description><Identifier type="DOI">10.13127/SD/fBBBtDtd6q</Identifier><ingv:Identifier>N22</ingv:Identifier><TotalNumberStations>2</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="AQU" startDate="1988-08-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S7</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Site><Name>L\'Aquila, Italy</Name></Site><CreationDate>1988-08-01T00:00:00</CreationDate></Station></Network></FDSNStationXML>',""),
]


### Contains query string, expected response code, expected content
testdatatxt = [

(
"level=station&net=MN&format=text&nodata=404",200,"\
#Network | Station | Latitude | Longitude | Elevation | SiteName | StartTime | EndTime\n\
MN|AQU|42.354|13.405|710|L'Aquila, Italy|1988-08-01T00:00:00|\n\
MN|ARPR|39.09289|38.33557|1537|Arapgir, Turkey|2014-01-23T00:00:00|\n",""),

(
"level=network&net=MN&format=text&nodata=404",200,"\
#Network | Description | StartTime | EndTime | TotalStations\n\
MN|Mediterranean Very Broadband Seismographic Network|1988-01-01T00:00:00||2\n",""),

(
"level=network&net=IV&format=text&nodata=404",200,"\
#Network | Description | StartTime | EndTime | TotalStations\n\
IV|Italian Seismic Network|1988-01-01T00:00:00||7\n",""),

(
"level=channel&net=MN&format=text&nodata=404",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-5250000000|0.02|M/S|20|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-1046640000|0.02|M/S|20|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1047020000|0.02|M/S|20|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1075730000|0.02|M/S|20|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-1063680000|0.02|M/S|20|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1063680000|0.02|M/S|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|983662000|0.02|M/S|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|M/S|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|M/S|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780000000|0.02|M/S|20|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||BHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|20|2019-03-01T00:00:00|\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-5250000000|0.02|M/S|20|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-1055040000|0.02|M/S|20|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1049580000|0.02|M/S|20|1995-08-28T00:00:00|1996-09-05T23:59:59\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1059600000|0.02|M/S|20|1996-09-06T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1091140000|0.02|M/S|20|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-1092770000|0.02|M/S|20|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1092770000|0.02|M/S|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1014990000|0.02|M/S|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|M/S|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|M/S|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|780000000|0.02|M/S|20|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||BHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|20|2019-03-01T00:00:00|\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-5250000000|0.02|M/S|20|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-1054200000|0.02|M/S|20|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1062530000|0.02|M/S|20|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1044970000|0.02|M/S|20|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-1069590000|0.02|M/S|20|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1069590000|0.02|M/S|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1001740000|0.02|M/S|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|M/S|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|M/S|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|780000000|0.02|M/S|20|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||BHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|M/S|20|2019-03-01T00:00:00|\n\
MN|AQU||HHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|M/S|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|M/S|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780000000|0.02|M/S|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|100|2019-03-01T00:00:00|\n\
MN|AQU||HHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|M/S|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|M/S|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|780000000|0.02|M/S|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|100|2019-03-01T00:00:00|\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|M/S|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|M/S|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|780000000|0.02|M/S|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|M/S|100|2019-03-01T00:00:00|\n\
MN|AQU||HLE|42.354|13.405|710|15|90|0|KINEMETRICS EPISENSOR|534331|0.02|M/S**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLE|42.354|13.405|710|15|90|0|KINEMETRICS EPISENSOR|530244|0.2|M/S**2|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HLN|42.354|13.405|710|15|0|0|KINEMETRICS EPISENSOR|537500|0.02|M/S**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLN|42.354|13.405|710|15|0|0|KINEMETRICS EPISENSOR|530244|0.2|M/S**2|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HLZ|42.354|13.405|710|15|0|-90|KINEMETRICS EPISENSOR|537691|0.02|M/S**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLZ|42.354|13.405|710|15|0|-90|KINEMETRICS EPISENSOR|530244|0.2|M/S**2|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HNE|42.354|13.405|710|0|90|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|M/S**2|100|2019-03-01T00:00:00|\n\
MN|AQU||HNN|42.354|13.405|710|0|0|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|M/S**2|100|2019-03-01T00:00:00|\n\
MN|AQU||HNZ|42.354|13.405|710|0|0|-90|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|M/S**2|100|2019-03-01T00:00:00|\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-21000000000|0.02|M/S|1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-4186560000|0.02|M/S|1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1047020000|0.02|M/S|1|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1075730000|0.02|M/S|1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-1063680000|0.02|M/S|1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1063680000|0.02|M/S|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|983662000|0.02|M/S|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|M/S|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|M/S|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780000000|0.02|M/S|1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||LHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-21000000000|0.02|M/S|1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-4220160000|0.02|M/S|1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1049580000|0.02|M/S|1|1995-08-28T00:00:00|1996-09-05T23:59:59\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1059600000|0.02|M/S|1|1996-09-06T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1091140000|0.02|M/S|1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-1092770000|0.02|M/S|1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1092770000|0.02|M/S|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1014990000|0.02|M/S|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|M/S|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|M/S|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|780000000|0.02|M/S|1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||LHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-21000000000|0.02|M/S|1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-4216800000|0.02|M/S|1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1062530000|0.02|M/S|1|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1044970000|0.02|M/S|1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-1069590000|0.02|M/S|1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1069590000|0.02|M/S|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1001740000|0.02|M/S|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|M/S|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|M/S|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|780000000|0.02|M/S|1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||LHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-84000000000|0.003|M/S|0.01|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-16746200000|0.003|M/S|0.01|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4188090000|0.003|M/S|0.01|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4302930000|0.003|M/S|0.01|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-4254720000|0.003|M/S|0.01|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4254720000|0.003|M/S|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|3934650000|0.003|M/S|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|2368370000|0.003|M/S|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3121070000|0.003|M/S|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-84000000000|0.003|M/S|0.01|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-16880600000|0.003|M/S|0.01|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4198310000|0.003|M/S|0.01|1995-08-28T00:00:00|1996-09-05T23:59:59\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4238420000|0.003|M/S|0.01|1996-09-06T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4364570000|0.003|M/S|0.01|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-4371080000|0.003|M/S|0.01|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4371080000|0.003|M/S|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4059940000|0.003|M/S|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|2401390000|0.003|M/S|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3115290000|0.003|M/S|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-84000000000|0.003|M/S|0.01|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-16867200000|0.003|M/S|0.01|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4250120000|0.003|M/S|0.01|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4179890000|0.003|M/S|0.01|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-4278370000|0.003|M/S|0.01|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4278370000|0.003|M/S|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4006970000|0.003|M/S|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|2394610000|0.003|M/S|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.003|M/S|0.01|2008-02-19T00:00:00|\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-84000000000|0.02|M/S|0.1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-16746200000|0.02|M/S|0.1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4188090000|0.02|M/S|0.1|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4302930000|0.02|M/S|0.1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-4254720000|0.02|M/S|0.1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4254720000|0.02|M/S|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|3934650000|0.02|M/S|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|2368370000|0.02|M/S|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3121070000|0.02|M/S|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3120000000|0.02|M/S|0.1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||VHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-84000000000|0.02|M/S|0.1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-16880600000|0.02|M/S|0.1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4198310000|0.02|M/S|0.1|1995-08-28T00:00:00|1996-09-05T23:59:59\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4238420000|0.02|M/S|0.1|1996-09-06T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4364570000|0.02|M/S|0.1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-4371080000|0.02|M/S|0.1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4371080000|0.02|M/S|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4059940000|0.02|M/S|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|2401390000|0.02|M/S|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3115290000|0.02|M/S|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3120000000|0.02|M/S|0.1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||VHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-84000000000|0.02|M/S|0.1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-16867200000|0.02|M/S|0.1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4250120000|0.02|M/S|0.1|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4179890000|0.02|M/S|0.1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-4278370000|0.02|M/S|0.1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4278370000|0.02|M/S|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4006970000|0.02|M/S|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|2394610000|0.02|M/S|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.02|M/S|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3120000000|0.02|M/S|0.1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||VHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|ARPR||BHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|2516580000|0.02|M/S|20|2014-01-23T00:00:00|\n\
MN|ARPR||BHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|2516580000|0.02|M/S|20|2014-01-23T00:00:00|\n\
MN|ARPR||BHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|2516580000|0.02|M/S|20|2014-01-23T00:00:00|\n\
MN|ARPR||LHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|2516580000|0.02|M/S|1|2014-01-23T00:00:00|\n\
MN|ARPR||LHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|2516580000|0.02|M/S|1|2014-01-23T00:00:00|\n\
MN|ARPR||LHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|2516580000|0.02|M/S|1|2014-01-23T00:00:00|\n\
MN|ARPR||VHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|10066300000|0.02|M/S|0.1|2014-01-23T00:00:00|\n\
MN|ARPR||VHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|10066300000|0.02|M/S|0.1|2014-01-23T00:00:00|\n\
MN|ARPR||VHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|10066300000|0.02|M/S|0.1|2014-01-23T00:00:00|\n"
,""),

(
"level=channel&starttime=2000-01-01T00:00:00.0&endtime=2020-01-02&net=MN&format=text&nodata=404",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1063680000|0.02|M/S|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|983662000|0.02|M/S|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|M/S|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|M/S|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780000000|0.02|M/S|20|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||BHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|20|2019-03-01T00:00:00|\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1092770000|0.02|M/S|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1014990000|0.02|M/S|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|M/S|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|M/S|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|780000000|0.02|M/S|20|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||BHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|20|2019-03-01T00:00:00|\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1069590000|0.02|M/S|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1001740000|0.02|M/S|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|M/S|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|M/S|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|780000000|0.02|M/S|20|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||BHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|M/S|20|2019-03-01T00:00:00|\n\
MN|AQU||HHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|M/S|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|M/S|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780000000|0.02|M/S|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|100|2019-03-01T00:00:00|\n\
MN|AQU||HHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|M/S|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|M/S|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|780000000|0.02|M/S|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|100|2019-03-01T00:00:00|\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|M/S|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|M/S|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|780000000|0.02|M/S|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|M/S|100|2019-03-01T00:00:00|\n\
MN|AQU||HLE|42.354|13.405|710|15|90|0|KINEMETRICS EPISENSOR|534331|0.02|M/S**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLE|42.354|13.405|710|15|90|0|KINEMETRICS EPISENSOR|530244|0.2|M/S**2|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HLN|42.354|13.405|710|15|0|0|KINEMETRICS EPISENSOR|537500|0.02|M/S**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLN|42.354|13.405|710|15|0|0|KINEMETRICS EPISENSOR|530244|0.2|M/S**2|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HLZ|42.354|13.405|710|15|0|-90|KINEMETRICS EPISENSOR|537691|0.02|M/S**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLZ|42.354|13.405|710|15|0|-90|KINEMETRICS EPISENSOR|530244|0.2|M/S**2|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HNE|42.354|13.405|710|0|90|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|M/S**2|100|2019-03-01T00:00:00|\n\
MN|AQU||HNN|42.354|13.405|710|0|0|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|M/S**2|100|2019-03-01T00:00:00|\n\
MN|AQU||HNZ|42.354|13.405|710|0|0|-90|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|M/S**2|100|2019-03-01T00:00:00|\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1063680000|0.02|M/S|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|983662000|0.02|M/S|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|M/S|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|M/S|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780000000|0.02|M/S|1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||LHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1092770000|0.02|M/S|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1014990000|0.02|M/S|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|M/S|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|M/S|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|780000000|0.02|M/S|1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||LHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1069590000|0.02|M/S|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1001740000|0.02|M/S|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|M/S|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|M/S|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|780000000|0.02|M/S|1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||LHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4254720000|0.003|M/S|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|3934650000|0.003|M/S|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|2368370000|0.003|M/S|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3121070000|0.003|M/S|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4371080000|0.003|M/S|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4059940000|0.003|M/S|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|2401390000|0.003|M/S|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3115290000|0.003|M/S|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4278370000|0.003|M/S|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4006970000|0.003|M/S|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|2394610000|0.003|M/S|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.003|M/S|0.01|2008-02-19T00:00:00|\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4254720000|0.02|M/S|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|3934650000|0.02|M/S|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|2368370000|0.02|M/S|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3121070000|0.02|M/S|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3120000000|0.02|M/S|0.1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||VHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4371080000|0.02|M/S|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4059940000|0.02|M/S|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|2401390000|0.02|M/S|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3115290000|0.02|M/S|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3120000000|0.02|M/S|0.1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||VHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4278370000|0.02|M/S|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4006970000|0.02|M/S|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|2394610000|0.02|M/S|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.02|M/S|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3120000000|0.02|M/S|0.1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||VHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|ARPR||BHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|2516580000|0.02|M/S|20|2014-01-23T00:00:00|\n\
MN|ARPR||BHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|2516580000|0.02|M/S|20|2014-01-23T00:00:00|\n\
MN|ARPR||BHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|2516580000|0.02|M/S|20|2014-01-23T00:00:00|\n\
MN|ARPR||LHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|2516580000|0.02|M/S|1|2014-01-23T00:00:00|\n\
MN|ARPR||LHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|2516580000|0.02|M/S|1|2014-01-23T00:00:00|\n\
MN|ARPR||LHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|2516580000|0.02|M/S|1|2014-01-23T00:00:00|\n\
MN|ARPR||VHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|10066300000|0.02|M/S|0.1|2014-01-23T00:00:00|\n\
MN|ARPR||VHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|10066300000|0.02|M/S|0.1|2014-01-23T00:00:00|\n\
MN|ARPR||VHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|10066300000|0.02|M/S|0.1|2014-01-23T00:00:00|\n\
",""),

(
"level=channel&starttime=2000-01-01T00:00:00.0&endtime=2010-01-02&net=MN&format=text&minlat=41.0&maxlat=43.0&nodata=404",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1063680000|0.02|M/S|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|983662000|0.02|M/S|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|M/S|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|M/S|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1092770000|0.02|M/S|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1014990000|0.02|M/S|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|M/S|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|M/S|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1069590000|0.02|M/S|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1001740000|0.02|M/S|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|M/S|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|M/S|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|M/S|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|M/S|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|M/S|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|M/S|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|M/S|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|M/S|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLE|42.354|13.405|710|15|90|0|KINEMETRICS EPISENSOR|534331|0.02|M/S**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLN|42.354|13.405|710|15|0|0|KINEMETRICS EPISENSOR|537500|0.02|M/S**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLZ|42.354|13.405|710|15|0|-90|KINEMETRICS EPISENSOR|537691|0.02|M/S**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1063680000|0.02|M/S|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|983662000|0.02|M/S|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|M/S|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|M/S|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1092770000|0.02|M/S|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1014990000|0.02|M/S|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|M/S|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|M/S|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1069590000|0.02|M/S|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1001740000|0.02|M/S|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|M/S|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|M/S|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4254720000|0.003|M/S|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|3934650000|0.003|M/S|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|2368370000|0.003|M/S|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3121070000|0.003|M/S|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4371080000|0.003|M/S|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4059940000|0.003|M/S|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|2401390000|0.003|M/S|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3115290000|0.003|M/S|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4278370000|0.003|M/S|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4006970000|0.003|M/S|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|2394610000|0.003|M/S|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.003|M/S|0.01|2008-02-19T00:00:00|\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4254720000|0.02|M/S|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|3934650000|0.02|M/S|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|2368370000|0.02|M/S|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3121070000|0.02|M/S|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4371080000|0.02|M/S|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4059940000|0.02|M/S|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|2401390000|0.02|M/S|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3115290000|0.02|M/S|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4278370000|0.02|M/S|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4006970000|0.02|M/S|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|2394610000|0.02|M/S|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.02|M/S|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
",""),


(
"level=channel&net=MN&format=text&nodata=404&minlat=41&maxlatitude=45",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-5250000000|0.02|M/S|20|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-1046640000|0.02|M/S|20|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1047020000|0.02|M/S|20|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1075730000|0.02|M/S|20|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-1063680000|0.02|M/S|20|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1063680000|0.02|M/S|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|983662000|0.02|M/S|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|M/S|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|M/S|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780000000|0.02|M/S|20|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||BHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|20|2019-03-01T00:00:00|\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-5250000000|0.02|M/S|20|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-1055040000|0.02|M/S|20|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1049580000|0.02|M/S|20|1995-08-28T00:00:00|1996-09-05T23:59:59\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1059600000|0.02|M/S|20|1996-09-06T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1091140000|0.02|M/S|20|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-1092770000|0.02|M/S|20|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1092770000|0.02|M/S|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1014990000|0.02|M/S|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|M/S|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|M/S|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|780000000|0.02|M/S|20|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||BHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|20|2019-03-01T00:00:00|\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-5250000000|0.02|M/S|20|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-1054200000|0.02|M/S|20|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1062530000|0.02|M/S|20|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1044970000|0.02|M/S|20|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-1069590000|0.02|M/S|20|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1069590000|0.02|M/S|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1001740000|0.02|M/S|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|M/S|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|M/S|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|780000000|0.02|M/S|20|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||BHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|M/S|20|2019-03-01T00:00:00|\n\
MN|AQU||HHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|M/S|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|M/S|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780000000|0.02|M/S|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|100|2019-03-01T00:00:00|\n\
MN|AQU||HHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|M/S|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|M/S|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|780000000|0.02|M/S|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|100|2019-03-01T00:00:00|\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|M/S|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|M/S|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|780000000|0.02|M/S|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|M/S|100|2019-03-01T00:00:00|\n\
MN|AQU||HLE|42.354|13.405|710|15|90|0|KINEMETRICS EPISENSOR|534331|0.02|M/S**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLE|42.354|13.405|710|15|90|0|KINEMETRICS EPISENSOR|530244|0.2|M/S**2|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HLN|42.354|13.405|710|15|0|0|KINEMETRICS EPISENSOR|537500|0.02|M/S**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLN|42.354|13.405|710|15|0|0|KINEMETRICS EPISENSOR|530244|0.2|M/S**2|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HLZ|42.354|13.405|710|15|0|-90|KINEMETRICS EPISENSOR|537691|0.02|M/S**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLZ|42.354|13.405|710|15|0|-90|KINEMETRICS EPISENSOR|530244|0.2|M/S**2|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HNE|42.354|13.405|710|0|90|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|M/S**2|100|2019-03-01T00:00:00|\n\
MN|AQU||HNN|42.354|13.405|710|0|0|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|M/S**2|100|2019-03-01T00:00:00|\n\
MN|AQU||HNZ|42.354|13.405|710|0|0|-90|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|M/S**2|100|2019-03-01T00:00:00|\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-21000000000|0.02|M/S|1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-4186560000|0.02|M/S|1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1047020000|0.02|M/S|1|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1075730000|0.02|M/S|1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-1063680000|0.02|M/S|1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1063680000|0.02|M/S|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|983662000|0.02|M/S|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|M/S|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|M/S|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780000000|0.02|M/S|1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||LHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-21000000000|0.02|M/S|1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-4220160000|0.02|M/S|1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1049580000|0.02|M/S|1|1995-08-28T00:00:00|1996-09-05T23:59:59\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1059600000|0.02|M/S|1|1996-09-06T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1091140000|0.02|M/S|1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-1092770000|0.02|M/S|1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1092770000|0.02|M/S|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1014990000|0.02|M/S|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|M/S|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|M/S|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|780000000|0.02|M/S|1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||LHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-21000000000|0.02|M/S|1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-4216800000|0.02|M/S|1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1062530000|0.02|M/S|1|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1044970000|0.02|M/S|1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-1069590000|0.02|M/S|1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1069590000|0.02|M/S|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1001740000|0.02|M/S|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|M/S|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|M/S|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|780000000|0.02|M/S|1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||LHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-84000000000|0.003|M/S|0.01|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-16746200000|0.003|M/S|0.01|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4188090000|0.003|M/S|0.01|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4302930000|0.003|M/S|0.01|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-4254720000|0.003|M/S|0.01|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4254720000|0.003|M/S|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|3934650000|0.003|M/S|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|2368370000|0.003|M/S|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3121070000|0.003|M/S|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-84000000000|0.003|M/S|0.01|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-16880600000|0.003|M/S|0.01|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4198310000|0.003|M/S|0.01|1995-08-28T00:00:00|1996-09-05T23:59:59\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4238420000|0.003|M/S|0.01|1996-09-06T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4364570000|0.003|M/S|0.01|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-4371080000|0.003|M/S|0.01|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4371080000|0.003|M/S|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4059940000|0.003|M/S|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|2401390000|0.003|M/S|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3115290000|0.003|M/S|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-84000000000|0.003|M/S|0.01|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-16867200000|0.003|M/S|0.01|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4250120000|0.003|M/S|0.01|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4179890000|0.003|M/S|0.01|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-4278370000|0.003|M/S|0.01|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4278370000|0.003|M/S|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4006970000|0.003|M/S|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|2394610000|0.003|M/S|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.003|M/S|0.01|2008-02-19T00:00:00|\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-84000000000|0.02|M/S|0.1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-16746200000|0.02|M/S|0.1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4188090000|0.02|M/S|0.1|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4302930000|0.02|M/S|0.1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-4254720000|0.02|M/S|0.1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4254720000|0.02|M/S|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|3934650000|0.02|M/S|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|2368370000|0.02|M/S|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3121070000|0.02|M/S|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3120000000|0.02|M/S|0.1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||VHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-84000000000|0.02|M/S|0.1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-16880600000|0.02|M/S|0.1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4198310000|0.02|M/S|0.1|1995-08-28T00:00:00|1996-09-05T23:59:59\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4238420000|0.02|M/S|0.1|1996-09-06T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4364570000|0.02|M/S|0.1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-4371080000|0.02|M/S|0.1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4371080000|0.02|M/S|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4059940000|0.02|M/S|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|2401390000|0.02|M/S|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3115290000|0.02|M/S|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3120000000|0.02|M/S|0.1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||VHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-84000000000|0.02|M/S|0.1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-16867200000|0.02|M/S|0.1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4250120000|0.02|M/S|0.1|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4179890000|0.02|M/S|0.1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-4278370000|0.02|M/S|0.1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4278370000|0.02|M/S|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4006970000|0.02|M/S|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|2394610000|0.02|M/S|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.02|M/S|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3120000000|0.02|M/S|0.1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||VHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
",""),

(
"level=channel&net=MN&startafter=1999-05-01&endbefore=2002-06-05T00:00:00.0&format=text&nodata=404&maxlatitude=45&minlat=42",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-1063680000|0.02|M/S|20|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1063680000|0.02|M/S|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-1092770000|0.02|M/S|20|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1092770000|0.02|M/S|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-1069590000|0.02|M/S|20|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1069590000|0.02|M/S|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-1063680000|0.02|M/S|1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1063680000|0.02|M/S|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-1092770000|0.02|M/S|1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1092770000|0.02|M/S|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-1069590000|0.02|M/S|1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1069590000|0.02|M/S|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-4254720000|0.003|M/S|0.01|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4254720000|0.003|M/S|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-4371080000|0.003|M/S|0.01|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4371080000|0.003|M/S|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-4278370000|0.003|M/S|0.01|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4278370000|0.003|M/S|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-4254720000|0.02|M/S|0.1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4254720000|0.02|M/S|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-4371080000|0.02|M/S|0.1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4371080000|0.02|M/S|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-4278370000|0.02|M/S|0.1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4278370000|0.02|M/S|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
",""),

("level=channel&net=MN&startbefore=1999-05-01&endafter=2002-06-05T00:00:00.0&format=text&maxlatitude=45&minlat=42",204,"",""),

(
"sta=AQU&level=channel&starttime=2021-01-01T00:00:00.0&endtime=2021-01-02&net=MN&nodata=404&format=text",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
MN|AQU||BHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|20|2019-03-01T00:00:00|\n\
MN|AQU||BHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|20|2019-03-01T00:00:00|\n\
MN|AQU||BHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|M/S|20|2019-03-01T00:00:00|\n\
MN|AQU||HHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|100|2019-03-01T00:00:00|\n\
MN|AQU||HHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|100|2019-03-01T00:00:00|\n\
MN|AQU||HHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|M/S|100|2019-03-01T00:00:00|\n\
MN|AQU||HNE|42.354|13.405|710|0|90|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|M/S**2|100|2019-03-01T00:00:00|\n\
MN|AQU||HNN|42.354|13.405|710|0|0|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|M/S**2|100|2019-03-01T00:00:00|\n\
MN|AQU||HNZ|42.354|13.405|710|0|0|-90|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|M/S**2|100|2019-03-01T00:00:00|\n\
MN|AQU||LHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||LHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||LHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3121070000|0.003|M/S|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3115290000|0.003|M/S|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.003|M/S|0.01|2008-02-19T00:00:00|\n\
MN|AQU||VHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||VHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||VHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
",""),

(
"level=station&includerestricted=true&format=text",200,"\
#Network | Station | Latitude | Longitude | Elevation | SiteName | StartTime | EndTime\n\
IV|ACATE|37.02398|14.50064|210|ACATE|2019-02-28T05:59:00|\n\
IV|ACER|40.7867|15.9427|690|Acerenza|2007-07-05T12:00:00|\n\
IV|AQT1|42.77383|13.2935|770|Arquata del Tronto|2011-07-22T00:00:00|2016-09-01T09:50:00\n\
IV|AQU|42.354|13.405|710|L'Aquila, Italy|2003-03-01T00:00:00|2008-10-15T00:00:00\n\
IV|ARVD|43.49807|12.94153|461|ARCEVIA 2|2003-03-01T00:00:00|\n\
IV|IMTC|40.7209|13.8758|59|Ischia - Monte Corvo|1988-01-01T00:00:00|\n\
IV|VBKN|40.83|14.4299|951|Vesuvio - Bunker Nord|1988-01-01T00:00:00|\n\
IX|AND3|40.9298|15.3331|905|Station Andretta, Italy|2013-12-17T00:00:00|\n\
MN|AQU|42.354|13.405|710|L'Aquila, Italy|1988-08-01T00:00:00|\n\
MN|ARPR|39.09289|38.33557|1537|Arapgir, Turkey|2014-01-23T00:00:00|\n\
NI|ACOM|46.548|13.5137|1788|Acomizza|2005-02-01T12:00:00|2015-12-31T23:59:59\n\
OX|ACOM|46.548|13.5137|1788|Acomizza|2016-01-01T00:00:00|\n\
SI|ABSI|46.7285|11.3205|1801|Aberstuckl (Sarntal)|2006-11-21T14:16:45|\n\
Z3|A319A|43.476425|10.578689|343|Santa Luce (PI)|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
","Include restricted"),

(
"level=station&includerestricted=false&format=text",200,"\
#Network | Station | Latitude | Longitude | Elevation | SiteName | StartTime | EndTime\n\
IV|ACATE|37.02398|14.50064|210|ACATE|2019-02-28T05:59:00|\n\
IV|ACER|40.7867|15.9427|690|Acerenza|2007-07-05T12:00:00|\n\
IV|AQT1|42.77383|13.2935|770|Arquata del Tronto|2011-07-22T00:00:00|2016-09-01T09:50:00\n\
IV|AQU|42.354|13.405|710|L'Aquila, Italy|2003-03-01T00:00:00|2008-10-15T00:00:00\n\
IV|ARVD|43.49807|12.94153|461|ARCEVIA 2|2003-03-01T00:00:00|\n\
IV|IMTC|40.7209|13.8758|59|Ischia - Monte Corvo|1988-01-01T00:00:00|\n\
IV|VBKN|40.83|14.4299|951|Vesuvio - Bunker Nord|1988-01-01T00:00:00|\n\
IX|AND3|40.9298|15.3331|905|Station Andretta, Italy|2013-12-17T00:00:00|\n\
MN|AQU|42.354|13.405|710|L'Aquila, Italy|1988-08-01T00:00:00|\n\
MN|ARPR|39.09289|38.33557|1537|Arapgir, Turkey|2014-01-23T00:00:00|\n\
NI|ACOM|46.548|13.5137|1788|Acomizza|2005-02-01T12:00:00|2015-12-31T23:59:59\n\
OX|ACOM|46.548|13.5137|1788|Acomizza|2016-01-01T00:00:00|\n\
SI|ABSI|46.7285|11.3205|1801|Aberstuckl (Sarntal)|2006-11-21T14:16:45|\n\
","No restricted, no Z3"),


(
"starttime=2021-01-06T15%3A55%3A02.658787&endtime=2021-02-05T15%3A55%3A02.658787&level=channel&includerestricted=false&format=text",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
IV|ACATE||EHE|37.02398|14.50064|210|0|90|0|LENNARTZ LE3D-5S|503316000|1|M/S|100|2019-02-28T05:59:00|\n\
IV|ACATE||EHN|37.02398|14.50064|210|0|0|0|LENNARTZ LE3D-5S|503316000|1|M/S|100|2019-02-28T05:59:00|\n\
IV|ACATE||EHZ|37.02398|14.50064|210|0|0|-90|LENNARTZ LE3D-5S|503316000|1|M/S|100|2019-02-28T05:59:00|\n\
IV|ACATE||HNE|37.02398|14.50064|210|0|90|0|NANOMETRICS TITAN|320770|1|M/S**2|200|2019-02-28T05:59:00|\n\
IV|ACATE||HNN|37.02398|14.50064|210|0|0|0|NANOMETRICS TITAN|320770|1|M/S**2|200|2019-02-28T05:59:00|\n\
IV|ACATE||HNZ|37.02398|14.50064|210|0|0|-90|NANOMETRICS TITAN|320770|1|M/S**2|200|2019-02-28T05:59:00|\n\
IV|ACER||BHE|40.7867|15.9427|690|1|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2014-05-08T11:42:00|\n\
IV|ACER||BHN|40.7867|15.9427|690|1|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2014-05-08T11:42:00|\n\
IV|ACER||BHZ|40.7867|15.9427|690|1|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2014-05-08T11:42:00|\n\
IV|ACER||HHE|40.7867|15.9427|690|1|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2014-05-08T11:42:00|\n\
IV|ACER||HHN|40.7867|15.9427|690|1|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2014-05-08T11:42:00|\n\
IV|ACER||HHZ|40.7867|15.9427|690|1|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2014-05-08T11:42:00|\n\
IV|ACER||HNE|40.7867|15.9427|690|1|90|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|320770|0.2|M/S**2|100|2014-05-08T11:42:00|\n\
IV|ACER||HNN|40.7867|15.9427|690|1|0|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|320770|0.2|M/S**2|100|2014-05-08T11:42:00|\n\
IV|ACER||HNZ|40.7867|15.9427|690|1|0|-90|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|320770|0.2|M/S**2|100|2014-05-08T11:42:00|\n\
IV|ACER||LHE|40.7867|15.9427|690|1|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2014-05-08T11:42:00|\n\
IV|ACER||LHN|40.7867|15.9427|690|1|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2014-05-08T11:42:00|\n\
IV|ACER||LHZ|40.7867|15.9427|690|1|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2014-05-08T11:42:00|\n\
IV|ACER||VHE|40.7867|15.9427|690|1|90|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2014-05-08T11:42:00|\n\
IV|ACER||VHN|40.7867|15.9427|690|1|0|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2014-05-08T11:42:00|\n\
IV|ACER||VHZ|40.7867|15.9427|690|1|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2014-05-08T11:42:00|\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2009-03-14T10:40:00|\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2009-03-14T10:40:00|\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2009-03-14T10:40:00|\n\
IV|ARVD||HHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2009-03-14T10:40:00|\n\
IV|ARVD||HHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2009-03-14T10:40:00|\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2009-03-14T10:40:00|\n\
IV|ARVD||LHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2009-03-14T10:40:00|\n\
IV|ARVD||LHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2009-03-14T10:40:00|\n\
IV|ARVD||LHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2009-03-14T10:40:00|\n\
IV|ARVD||VHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2009-03-14T10:40:00|\n\
IV|ARVD||VHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2009-03-14T10:40:00|\n\
IV|ARVD||VHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2009-03-14T10:40:00|\n\
IV|IMTC||HHE|40.7209|13.8758|59|0|90|0|GURALP CMG-40T-60S|243822000|1|M/S|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHN|40.7209|13.8758|59|0|0|0|GURALP CMG-40T-60S|243822000|1|M/S|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHZ|40.7209|13.8758|59|0|0|-90|GURALP CMG-40T-60S|243822000|1|M/S|100|1988-01-01T00:00:00|\n\
IV|VBKN||HHE|40.83|14.4299|951|0|90|0|GURALP CMG-40T-60S|243822000|1|M/S|100|1988-01-01T00:00:00|\n\
IV|VBKN||HHN|40.83|14.4299|951|0|0|0|GURALP CMG-40T-60S|243822000|1|M/S|100|1988-01-01T00:00:00|\n\
IV|VBKN||HHZ|40.83|14.4299|951|0|0|-90|GURALP CMG-40T-60S|243822000|1|M/S|100|1988-01-01T00:00:00|\n\
IX|AND3|01|HNE|40.9298|15.3331|905|0|90|0|GURALP CMG-5T|949627|0.1|M/S**2|125|2013-12-17T00:00:00|\n\
IX|AND3|01|HNN|40.9298|15.3331|905|0|0|0|GURALP CMG-5T|949627|0.1|M/S**2|125|2013-12-17T00:00:00|\n\
IX|AND3|01|HNZ|40.9298|15.3331|905|0|0|-90|GURALP CMG-5T|949627|0.1|M/S**2|125|2013-12-17T00:00:00|\n\
IX|AND3|02|HHE|40.9298|15.3331|905|0|90|0|GEOTECH KS-2000EDU|3731340000|0.1|M/S|125|2013-12-17T00:00:00|\n\
IX|AND3|02|HHN|40.9298|15.3331|905|0|0|0|GEOTECH KS-2000EDU|3731340000|0.1|M/S|125|2013-12-17T00:00:00|\n\
IX|AND3|02|HHZ|40.9298|15.3331|905|0|0|-90|GEOTECH KS-2000EDU|3731340000|0.1|M/S|125|2013-12-17T00:00:00|\n\
MN|AQU||BHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|20|2019-03-01T00:00:00|\n\
MN|AQU||BHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|20|2019-03-01T00:00:00|\n\
MN|AQU||BHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|M/S|20|2019-03-01T00:00:00|\n\
MN|AQU||HHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|100|2019-03-01T00:00:00|\n\
MN|AQU||HHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|100|2019-03-01T00:00:00|\n\
MN|AQU||HHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|M/S|100|2019-03-01T00:00:00|\n\
MN|AQU||HNE|42.354|13.405|710|0|90|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|M/S**2|100|2019-03-01T00:00:00|\n\
MN|AQU||HNN|42.354|13.405|710|0|0|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|M/S**2|100|2019-03-01T00:00:00|\n\
MN|AQU||HNZ|42.354|13.405|710|0|0|-90|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|M/S**2|100|2019-03-01T00:00:00|\n\
MN|AQU||LHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||LHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||LHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3121070000|0.003|M/S|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3115290000|0.003|M/S|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.003|M/S|0.01|2008-02-19T00:00:00|\n\
MN|AQU||VHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||VHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|AQU||VHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|M/S|1|2019-03-01T00:00:00|\n\
MN|ARPR||BHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|2516580000|0.02|M/S|20|2014-01-23T00:00:00|\n\
MN|ARPR||BHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|2516580000|0.02|M/S|20|2014-01-23T00:00:00|\n\
MN|ARPR||BHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|2516580000|0.02|M/S|20|2014-01-23T00:00:00|\n\
MN|ARPR||LHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|2516580000|0.02|M/S|1|2014-01-23T00:00:00|\n\
MN|ARPR||LHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|2516580000|0.02|M/S|1|2014-01-23T00:00:00|\n\
MN|ARPR||LHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|2516580000|0.02|M/S|1|2014-01-23T00:00:00|\n\
MN|ARPR||VHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|10066300000|0.02|M/S|0.1|2014-01-23T00:00:00|\n\
MN|ARPR||VHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|10066300000|0.02|M/S|0.1|2014-01-23T00:00:00|\n\
MN|ARPR||VHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|10066300000|0.02|M/S|0.1|2014-01-23T00:00:00|\n\
OX|ACOM||HHE|46.548|13.5137|1788|0|90|0|NANOMETRICS TRILLIUM-40S|650175000|0.2|M/S|100|2016-01-01T00:00:00|\n\
OX|ACOM||HHN|46.548|13.5137|1788|0|0|0|NANOMETRICS TRILLIUM-40S|650175000|0.2|M/S|100|2016-01-01T00:00:00|\n\
OX|ACOM||HHZ|46.548|13.5137|1788|0|0|-90|NANOMETRICS TRILLIUM-40S|650175000|0.2|M/S|100|2016-01-01T00:00:00|\n\
OX|ACOM||HNE|46.5479|13.5149|1715|0|90|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427894|0.07|M/S**2|100|2016-01-01T00:00:00|\n\
OX|ACOM||HNN|46.5479|13.5149|1715|0|0|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427894|0.07|M/S**2|100|2016-01-01T00:00:00|\n\
OX|ACOM||HNZ|46.5479|13.5149|1715|0|0|-90|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427894|0.07|M/S**2|100|2016-01-01T00:00:00|\n\
SI|ABSI||BHE|46.7285|11.3205|1801|0|90|0|STRECKEISEN STS-2-120S|627604000|0.4|M/S|20|2006-11-21T14:16:45|\n\
SI|ABSI||BHN|46.7285|11.3205|1801|0|0|0|STRECKEISEN STS-2-120S|627604000|0.4|M/S|20|2006-11-21T14:16:45|\n\
SI|ABSI||BHZ|46.7285|11.3205|1801|0|0|-90|STRECKEISEN STS-2-120S|627604000|0.4|M/S|20|2006-11-21T14:16:45|\n\
SI|ABSI||HHE|46.7285|11.3205|1801|0|90|0|STRECKEISEN STS-2-120S|627604000|0.4|M/S|100|2006-11-21T14:16:45|\n\
SI|ABSI||HHN|46.7285|11.3205|1801|0|0|0|STRECKEISEN STS-2-120S|627604000|0.4|M/S|100|2006-11-21T14:16:45|\n\
SI|ABSI||HHZ|46.7285|11.3205|1801|0|0|-90|STRECKEISEN STS-2-120S|627604000|0.4|M/S|100|2006-11-21T14:16:45|\n\
SI|ABSI||LHE|46.7285|11.3205|1801|0|90|0|STRECKEISEN STS-2-120S|627604000|0.4|M/S|1|2006-11-21T14:16:45|\n\
SI|ABSI||LHN|46.7285|11.3205|1801|0|0|0|STRECKEISEN STS-2-120S|627604000|0.4|M/S|1|2006-11-21T14:16:45|\n\
SI|ABSI||LHZ|46.7285|11.3205|1801|0|0|-90|STRECKEISEN STS-2-120S|627604000|0.4|M/S|1|2006-11-21T14:16:45|\n\
SI|ABSI||VHE|46.7285|11.3205|1801|0|90|0|STRECKEISEN STS-2-120S|2510420000|0.4|M/S|0.1|2006-11-21T14:16:45|\n\
SI|ABSI||VHN|46.7285|11.3205|1801|0|0|0|STRECKEISEN STS-2-120S|2510420000|0.4|M/S|0.1|2006-11-21T14:16:45|\n\
SI|ABSI||VHZ|46.7285|11.3205|1801|0|0|-90|STRECKEISEN STS-2-120S|2510420000|0.4|M/S|0.1|2006-11-21T14:16:45|\n\
","Selection in the future"),


(
"starttime=2004-01-06T15%3A55%3A02.658787&endtime=2010-02-05T15%3A55%3A02.658787&level=channel&format=text&cha=*Z",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
IV|ACER||BHZ|40.7867|15.9427|690|1|0|-90|NANOMETRICS TRILLIUM-40S|1500000000|0.2|M/S|20|2007-07-05T12:00:00|2014-05-08T11:42:00\n\
IV|ACER||HHZ|40.7867|15.9427|690|1|0|-90|NANOMETRICS TRILLIUM-40S|1500000000|0.2|M/S|100|2007-07-05T12:00:00|2014-05-08T11:42:00\n\
IV|ACER||HNZ|40.7867|15.9427|690|0|0|-90|KINEMETRICS EPISENSOR|407880|0.2|M/S**2|200|2007-07-05T12:00:00|2011-06-24T00:00:00\n\
IV|ACER||LHZ|40.7867|15.9427|690|1|0|-90|NANOMETRICS TRILLIUM-40S|1485900000|0.2|M/S|1|2007-07-05T12:00:00|2014-05-08T11:42:00\n\
IV|ACER||VHZ|40.7867|15.9427|690|1|0|-90|NANOMETRICS TRILLIUM-40S|3165200000|0.02|M/S|0.1|2007-07-05T12:00:00|2014-05-08T11:42:00\n\
IV|AQU||SHZ|42.35388|13.40193|729|0|0|-90|GEOTECH S-13|582216000|0.2|M/S|50|2003-03-01T00:00:00|2008-10-15T00:00:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2009-03-14T10:40:00|\n\
IV|ARVD||EHZ|43.49807|12.94153|461|0|0|-90|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHZ|43.49807|12.94153|461|0|0|-90|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2009-03-14T10:40:00|\n\
IV|ARVD||LHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2009-03-14T10:40:00|\n\
IV|ARVD||VHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2009-03-14T10:40:00|\n\
IV|IMTC||HHZ|40.7209|13.8758|59|0|0|-90|GURALP CMG-40T-60S|243822000|1|M/S|100|1988-01-01T00:00:00|\n\
IV|VBKN||HHZ|40.83|14.4299|951|0|0|-90|GURALP CMG-40T-60S|243822000|1|M/S|100|1988-01-01T00:00:00|\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|M/S|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|M/S|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|M/S|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|M/S|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLZ|42.354|13.405|710|15|0|-90|KINEMETRICS EPISENSOR|537691|0.02|M/S**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|M/S|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|M/S|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|2394610000|0.003|M/S|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.003|M/S|0.01|2008-02-19T00:00:00|\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|2394610000|0.02|M/S|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.02|M/S|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
NI|ACOM||BHZ|46.548|13.5137|1788|0|0|-90|STRECKEISEN STS-2-120S|626646000|5|M/S|20|2005-02-01T12:00:00|2008-10-20T16:00:01\n\
NI|ACOM||BHZ|46.548|13.5137|1788|0|0|-90|NANOMETRICS TRILLIUM-40S|629221000|0.3|M/S|20|2008-10-20T16:00:01|2008-10-20T16:00:02\n\
NI|ACOM||BHZ|46.548|13.5137|1788|0|0|-90|NANOMETRICS TRILLIUM-40S|650175000|0.2|M/S|20|2008-10-20T16:00:03|2015-12-31T23:59:59\n\
NI|ACOM||HHZ|46.548|13.5137|1788|0|0|-90|STRECKEISEN STS-2-120S|624217000|7|M/S|100|2005-02-01T12:00:00|2008-10-20T16:00:01\n\
NI|ACOM||HHZ|46.548|13.5137|1788|0|0|-90|NANOMETRICS TRILLIUM-40S|629436000|0.6|M/S|100|2008-10-20T16:00:01|2008-10-20T16:00:02\n\
NI|ACOM||HHZ|46.548|13.5137|1788|0|0|-90|NANOMETRICS TRILLIUM-40S|650175000|0.2|M/S|100|2008-10-20T16:00:03|2015-12-31T23:59:59\n\
NI|ACOM||LHZ|46.548|13.5137|1788|0|0|-90|NANOMETRICS TRILLIUM-40S|650175000|0.2|M/S|1|2008-10-20T16:00:03|2015-12-31T23:59:59\n\
NI|ACOM||VHZ|46.548|13.5137|1788|0|0|-90|NANOMETRICS TRILLIUM-40S|650175000|0.2|M/S|1|2008-10-20T16:00:03|2015-12-31T23:59:59\n\
SI|ABSI||BHZ|46.7285|11.3205|1801|0|0|-90|STRECKEISEN STS-2-120S|627604000|0.4|M/S|20|2006-11-21T14:16:45|\n\
SI|ABSI||HHZ|46.7285|11.3205|1801|0|0|-90|STRECKEISEN STS-2-120S|627604000|0.4|M/S|100|2006-11-21T14:16:45|\n\
SI|ABSI||LHZ|46.7285|11.3205|1801|0|0|-90|STRECKEISEN STS-2-120S|627604000|0.4|M/S|1|2006-11-21T14:16:45|\n\
SI|ABSI||VHZ|46.7285|11.3205|1801|0|0|-90|STRECKEISEN STS-2-120S|2510420000|0.4|M/S|0.1|2006-11-21T14:16:45|\n\
","Selection in the past"),

(
"level=station&net=*&format=text&start=2020-05-08T11:42:00&channel=EH*",200,"\
#Network | Station | Latitude | Longitude | Elevation | SiteName | StartTime | EndTime\n\
IV|ACATE|37.02398|14.50064|210|ACATE|2019-02-28T05:59:00|\n\
","0 selected channels but station selected in output"),

(
"level=channel&latitude=42&longitude=12&minradius=1.5&maxradius=2&format=text&nodata=404",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2009-03-14T10:40:00|\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2009-03-14T10:40:00|\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2009-03-14T10:40:00|\n\
IV|ARVD||EHE|43.49807|12.94153|461|0|90|0|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHE|43.49807|12.94153|461|0|90|0|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||EHN|43.49807|12.94153|461|0|0|0|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHN|43.49807|12.94153|461|0|0|0|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||EHZ|43.49807|12.94153|461|0|0|-90|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHZ|43.49807|12.94153|461|0|0|-90|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||HHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2009-03-14T10:40:00|\n\
IV|ARVD||HHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2009-03-14T10:40:00|\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2009-03-14T10:40:00|\n\
IV|ARVD||LHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2009-03-14T10:40:00|\n\
IV|ARVD||LHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2009-03-14T10:40:00|\n\
IV|ARVD||LHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2009-03-14T10:40:00|\n\
IV|ARVD||VHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2009-03-14T10:40:00|\n\
IV|ARVD||VHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2009-03-14T10:40:00|\n\
IV|ARVD||VHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2009-03-14T10:40:00|\n\
IV|IMTC||HHE|40.7209|13.8758|59|0|90|0|GURALP CMG-40T-60S|243822000|1|M/S|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHN|40.7209|13.8758|59|0|0|0|GURALP CMG-40T-60S|243822000|1|M/S|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHZ|40.7209|13.8758|59|0|0|-90|GURALP CMG-40T-60S|243822000|1|M/S|100|1988-01-01T00:00:00|\n\
Z3|A319A||HHE|43.476425|10.578689|343|1|90|0|NANOMETRICS TRILLIUM-120C|749.1|1|M/S|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
Z3|A319A||HHN|43.476425|10.578689|343|1|0|0|NANOMETRICS TRILLIUM-120C|749.1|1|M/S|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
Z3|A319A||HHZ|43.476425|10.578689|343|1|0|-90|NANOMETRICS TRILLIUM-120C|749.1|1|M/S|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
","check minradius maxradius")


,

(
"level=channel&latitude=42&longitude=12&minradiuskm=166.8&maxradiuskm=222.4&format=text&nodata=404",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2009-03-14T10:40:00|\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2009-03-14T10:40:00|\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2009-03-14T10:40:00|\n\
IV|ARVD||EHE|43.49807|12.94153|461|0|90|0|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHE|43.49807|12.94153|461|0|90|0|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||EHN|43.49807|12.94153|461|0|0|0|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHN|43.49807|12.94153|461|0|0|0|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||EHZ|43.49807|12.94153|461|0|0|-90|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHZ|43.49807|12.94153|461|0|0|-90|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||HHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2009-03-14T10:40:00|\n\
IV|ARVD||HHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2009-03-14T10:40:00|\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2009-03-14T10:40:00|\n\
IV|ARVD||LHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2009-03-14T10:40:00|\n\
IV|ARVD||LHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2009-03-14T10:40:00|\n\
IV|ARVD||LHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2009-03-14T10:40:00|\n\
IV|ARVD||VHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2009-03-14T10:40:00|\n\
IV|ARVD||VHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2009-03-14T10:40:00|\n\
IV|ARVD||VHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2009-03-14T10:40:00|\n\
IV|IMTC||HHE|40.7209|13.8758|59|0|90|0|GURALP CMG-40T-60S|243822000|1|M/S|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHN|40.7209|13.8758|59|0|0|0|GURALP CMG-40T-60S|243822000|1|M/S|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHZ|40.7209|13.8758|59|0|0|-90|GURALP CMG-40T-60S|243822000|1|M/S|100|1988-01-01T00:00:00|\n\
Z3|A319A||HHE|43.476425|10.578689|343|1|90|0|NANOMETRICS TRILLIUM-120C|749.1|1|M/S|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
Z3|A319A||HHN|43.476425|10.578689|343|1|0|0|NANOMETRICS TRILLIUM-120C|749.1|1|M/S|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
Z3|A319A||HHZ|43.476425|10.578689|343|1|0|-90|NANOMETRICS TRILLIUM-120C|749.1|1|M/S|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
","check minradiuskm maxradiuskm")



]

### Contains query string, expected response code, expected content
testdatapost = [

(
"minlat=10\n\
maxlat=62\n\
level=station\n\
format=text\n\
nodata=404\n\
* ACER * * 1920-01-01T00:00:00.0 2020-01-01T00:00:00.0",200,"\
#Network | Station | Latitude | Longitude | Elevation | SiteName | StartTime | EndTime\n\
IV|ACER|40.7867|15.9427|690|Acerenza|2007-07-05T12:00:00|\n\
",""),

(
"minlat=10\n\
maxlat=62\n\
level=station\n\
format=text\n\
nodata=404\n\
updatedafter=2000-01-01T00:00:00\n\
* * * * 1920-01-01T00:00:00.0 2020-01-01T00:00:00.0",200,"\
#Network | Station | Latitude | Longitude | Elevation | SiteName | StartTime | EndTime\n\
IV|ACATE|37.02398|14.50064|210|ACATE|2019-02-28T05:59:00|\n\
IV|ACER|40.7867|15.9427|690|Acerenza|2007-07-05T12:00:00|\n\
IV|AQT1|42.77383|13.2935|770|Arquata del Tronto|2011-07-22T00:00:00|2016-09-01T09:50:00\n\
IV|AQU|42.354|13.405|710|L'Aquila, Italy|2003-03-01T00:00:00|2008-10-15T00:00:00\n\
IV|ARVD|43.49807|12.94153|461|ARCEVIA 2|2003-03-01T00:00:00|\n\
IV|IMTC|40.7209|13.8758|59|Ischia - Monte Corvo|1988-01-01T00:00:00|\n\
IV|VBKN|40.83|14.4299|951|Vesuvio - Bunker Nord|1988-01-01T00:00:00|\n\
IX|AND3|40.9298|15.3331|905|Station Andretta, Italy|2013-12-17T00:00:00|\n\
MN|AQU|42.354|13.405|710|L'Aquila, Italy|1988-08-01T00:00:00|\n\
MN|ARPR|39.09289|38.33557|1537|Arapgir, Turkey|2014-01-23T00:00:00|\n\
NI|ACOM|46.548|13.5137|1788|Acomizza|2005-02-01T12:00:00|2015-12-31T23:59:59\n\
OX|ACOM|46.548|13.5137|1788|Acomizza|2016-01-01T00:00:00|\n\
SI|ABSI|46.7285|11.3205|1801|Aberstuckl (Sarntal)|2006-11-21T14:16:45|\n\
Z3|A319A|43.476425|10.578689|343|Santa Luce (PI)|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
",""),


(
"minlat=10\n\
maxlat=62\n\
level=station\n\
format=text\n\
nodata=404\n\
updatedafter=1900-01-01T00:00:00\n\
* ACER * * 2006-01-01T00:00:00.0 2020-01-01T00:00:00.0\n\
* ACATE * * 1988-01-01T00:00:00.0 2020-01-01T00:00:00.0\n\
* ABSI * * 1990-01-01T00:00:00.0 2005-01-01T00:00:00.0",200,"\
#Network | Station | Latitude | Longitude | Elevation | SiteName | StartTime | EndTime\n\
IV|ACATE|37.02398|14.50064|210|ACATE|2019-02-28T05:59:00|\n\
IV|ACER|40.7867|15.9427|690|Acerenza|2007-07-05T12:00:00|\n\
",""),

(
"latitude=42\n\
longitude=12\n\
level=channel\n\
format=text\n\
minradiuskm=166.8\n\
maxradiuskm=222.4\n\
nodata=404\n\
* * * * 1900-01-01T00:00:00.0 2140-01-01T00:00:00.0",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2009-03-14T10:40:00|\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2009-03-14T10:40:00|\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2009-03-14T10:40:00|\n\
IV|ARVD||EHE|43.49807|12.94153|461|0|90|0|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||EHE|43.49807|12.94153|461|0|90|0|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHN|43.49807|12.94153|461|0|0|0|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHN|43.49807|12.94153|461|0|0|0|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||EHZ|43.49807|12.94153|461|0|0|-90|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHZ|43.49807|12.94153|461|0|0|-90|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||HHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2009-03-14T10:40:00|\n\
IV|ARVD||HHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2009-03-14T10:40:00|\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2009-03-14T10:40:00|\n\
IV|ARVD||LHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2009-03-14T10:40:00|\n\
IV|ARVD||LHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2009-03-14T10:40:00|\n\
IV|ARVD||LHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2009-03-14T10:40:00|\n\
IV|ARVD||LHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2009-03-14T10:40:00|\n\
IV|ARVD||VHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2009-03-14T10:40:00|\n\
IV|ARVD||VHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2009-03-14T10:40:00|\n\
IV|ARVD||VHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|IMTC||HHE|40.7209|13.8758|59|0|90|0|GURALP CMG-40T-60S|243822000|1|M/S|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHN|40.7209|13.8758|59|0|0|0|GURALP CMG-40T-60S|243822000|1|M/S|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHZ|40.7209|13.8758|59|0|0|-90|GURALP CMG-40T-60S|243822000|1|M/S|100|1988-01-01T00:00:00|\n\
Z3|A319A||HHE|43.476425|10.578689|343|1|90|0|NANOMETRICS TRILLIUM-120C|749.1|1|M/S|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
Z3|A319A||HHN|43.476425|10.578689|343|1|0|0|NANOMETRICS TRILLIUM-120C|749.1|1|M/S|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
Z3|A319A||HHZ|43.476425|10.578689|343|1|0|-90|NANOMETRICS TRILLIUM-120C|749.1|1|M/S|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
","Check min/maxradiuskm in POST"),

(
"latitude=42\n\
longitude=12\n\
level=channel\n\
format=text\n\
minradius=1.5\n\
maxradius=2.0\n\
nodata=404\n\
* * * * 1988-01-01T00:00:00.0 2040-01-01T00:00:00.0",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2009-03-14T10:40:00|\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2009-03-14T10:40:00|\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|20|2009-03-14T10:40:00|\n\
IV|ARVD||EHE|43.49807|12.94153|461|0|90|0|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||EHE|43.49807|12.94153|461|0|90|0|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHN|43.49807|12.94153|461|0|0|0|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHN|43.49807|12.94153|461|0|0|0|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||EHZ|43.49807|12.94153|461|0|0|-90|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHZ|43.49807|12.94153|461|0|0|-90|LENNARTZ LE3D-5S|466034000|0.2|M/S|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||HHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2009-03-14T10:40:00|\n\
IV|ARVD||HHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2009-03-14T10:40:00|\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|100|2009-03-14T10:40:00|\n\
IV|ARVD||LHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2009-03-14T10:40:00|\n\
IV|ARVD||LHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2009-03-14T10:40:00|\n\
IV|ARVD||LHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2009-03-14T10:40:00|\n\
IV|ARVD||LHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|M/S|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2009-03-14T10:40:00|\n\
IV|ARVD||VHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2009-03-14T10:40:00|\n\
IV|ARVD||VHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2009-03-14T10:40:00|\n\
IV|ARVD||VHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|M/S|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|IMTC||HHE|40.7209|13.8758|59|0|90|0|GURALP CMG-40T-60S|243822000|1|M/S|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHN|40.7209|13.8758|59|0|0|0|GURALP CMG-40T-60S|243822000|1|M/S|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHZ|40.7209|13.8758|59|0|0|-90|GURALP CMG-40T-60S|243822000|1|M/S|100|1988-01-01T00:00:00|\n\
Z3|A319A||HHE|43.476425|10.578689|343|1|90|0|NANOMETRICS TRILLIUM-120C|749.1|1|M/S|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
Z3|A319A||HHN|43.476425|10.578689|343|1|0|0|NANOMETRICS TRILLIUM-120C|749.1|1|M/S|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
Z3|A319A||HHZ|43.476425|10.578689|343|1|0|-90|NANOMETRICS TRILLIUM-120C|749.1|1|M/S|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
","Check min/maxradius in POST"),
]

testdatapostxml =[
(
"minlat=15\n\
maxlat=55\n\
level=station\n\
format=xml\n\
nodata=404\n\
* * * * 2009-01-01T00:00:00.0 2010-01-01T00:00:00.0\n\
MN * * * 1988-01-01T00:00:00.0 2002-01-01T00:00:00.0\n\
* ABSI * * 1990-01-01T00:00:00.0 2005-01-01T00:00:00.0",200,'<?xml version="1.0" encoding="UTF-8"?>\n\
<FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.1" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.1.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.1</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query/?\n\
minlat=15\n\
maxlat=55\n\
level=station\n\
format=xml\n\
nodata=404\n\
* * * * 2009-01-01T00:00:00.0 2010-01-01T00:00:00.0\n\
MN * * * 1988-01-01T00:00:00.0 2002-01-01T00:00:00.0\n\
* ABSI * * 1990-01-01T00:00:00.0 2005-01-01T00:00:00.0</ModuleURI><Created>2021-02-20T08:56:56.344Z</Created><Network code="IV" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Italian Seismic Network</Description><Identifier type="DOI">10.13127/SD/X0FXnH7QfY</Identifier><ingv:Identifier>N1</ingv:Identifier><TotalNumberStations>7</TotalNumberStations><SelectedNumberStations>4</SelectedNumberStations><Station code="ACER" startDate="2007-07-05T12:00:00" restrictedStatus="open"><ingv:Identifier>S1</ingv:Identifier><Latitude>40.7867</Latitude><Longitude>15.9427</Longitude><Elevation>690</Elevation><Site><Name>Acerenza</Name></Site><CreationDate>2007-07-05T12:00:00</CreationDate></Station><Station code="ARVD" startDate="2003-03-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S9</ingv:Identifier><Latitude>43.49807</Latitude><Longitude>12.94153</Longitude><Elevation>461</Elevation><Site><Name>ARCEVIA 2</Name></Site><CreationDate>2003-03-01T00:00:00</CreationDate></Station><Station code="IMTC" startDate="1988-01-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S3001</ingv:Identifier><Latitude>40.7209</Latitude><Longitude>13.8758</Longitude><Elevation>59</Elevation><Site><Name>Ischia - Monte Corvo</Name></Site><CreationDate>1988-01-01T00:00:00</CreationDate></Station><Station code="VBKN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S3031</ingv:Identifier><Latitude>40.83</Latitude><Longitude>14.4299</Longitude><Elevation>951</Elevation><Site><Name>Vesuvio - Bunker Nord</Name></Site><CreationDate>1988-01-01T00:00:00</CreationDate></Station></Network><Network code="MN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Mediterranean Very Broadband Seismographic Network</Description><Identifier type="DOI">10.13127/SD/fBBBtDtd6q</Identifier><ingv:Identifier>N22</ingv:Identifier><TotalNumberStations>2</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="AQU" startDate="1988-08-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S7</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Site><Name>L\'Aquila, Italy</Name></Site><CreationDate>1988-08-01T00:00:00</CreationDate></Station></Network><Network code="NI" startDate="2002-01-01T00:00:00" restrictedStatus="open"><Description>North-East Italy Broadband Network</Description><ingv:Identifier>N13</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="ACOM" startDate="2005-02-01T12:00:00" endDate="2015-12-31T23:59:59" restrictedStatus="open"><ingv:Identifier>S3451</ingv:Identifier><Latitude>46.548</Latitude><Longitude>13.5137</Longitude><Elevation>1788</Elevation><Site><Name>Acomizza</Name></Site><CreationDate>2005-02-01T12:00:00</CreationDate></Station></Network><Network code="SI" startDate="2006-01-01T00:00:00" restrictedStatus="open"><Description>Sudtirol Network, Italy</Description><Identifier type="citation">Pintore et al. Multiple Identifier</Identifier><Identifier type="DOI">https://doi.org/10.7914/SN/3T_2020</Identifier><ingv:Identifier>N18</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="ABSI" startDate="2006-11-21T14:16:45" restrictedStatus="open"><ingv:Identifier>S122</ingv:Identifier><Latitude>46.7285</Latitude><Longitude>11.3205</Longitude><Elevation>1801</Elevation><Site><Name>Aberstuckl (Sarntal)</Name></Site><CreationDate>2006-11-21T14:16:45</CreationDate></Station></Network></FDSNStationXML>',"POST 2"),

]

testdataerrors =[
("level=channel&net=MN&cha=SHZ&station=AQU&format=text&maxlatitude=45&minlat=42&nodata=404",404,
"Error 404 - no matching inventory found\n\
\n\
Usage details are available from <SERVICE DOCUMENTATION URI>\n\
\n\
Request:\n\
\n\
level=channel&net=MN&cha=SHZ&station=AQU&format=text&maxlatitude=45&minlat=42&nodata=404\n\
\n\
Request Submitted:","nodata text"),

("level=channel&net=MN&cha=SHZ&station=AQU&format=xml&maxlatitude=45&minlat=42&nodata=404",404,
"Error 404 - no matching inventory found\n\
\n\
Usage details are available from <SERVICE DOCUMENTATION URI>\n\
\n\
Request:\n\
\n\
level=channel&net=MN&cha=SHZ&station=AQU&format=xml&maxlatitude=45&minlat=42&nodata=404\n\
\n\
Request Submitted:","nodata xml"),

("level=channel&net=MN&cha=SHZ&station=AQU&format=json&maxlatitude=45&minlat=42&nodata=404",404,
"Error 404 - no matching inventory found\n\
\n\
Usage details are available from <SERVICE DOCUMENTATION URI>\n\
\n\
Request:\n\
\n\
level=channel&net=MN&cha=SHZ&station=AQU&format=json&maxlatitude=45&minlat=42&nodata=404\n\
\n\
Request Submitted:","nodata xml"),
]

testdataposterrors = [
(
"minlat=10\n\
maxlat=62\n\
level=station\n\
format=text\n\
nodata=404\n\
updatedafter=2100-01-01T00:00:00\n\
* * * * 1920-01-01T00:00:00.0 2020-01-01T00:00:00.0",404,
"Error 404 - no matching inventory found\n\
\n\
Usage details are available from <SERVICE DOCUMENTATION URI>\n\
\n\
Request:\n\
\n\
","nodata on post format text "),
]

############################################# END DATA FOR TEST #############################################

#############################################################################################################

@pytest.mark.parametrize(
    "query,expected_status_code,expected_content,comment", testdataxml
)

def test_eval(query,expected_status_code,expected_content,comment,host):
    print("Requesting: "+"http://"+host+"/exist/apps/fdsn-station/fdsnws/station/1/query?" + query)
    response = requests.get( "http://"+host+"/exist/apps/fdsn-station/fdsnws/station/1/query?" + query )
    print(response.text)
    response_tree = ET.fromstring(bytes(response.text, encoding='utf-8'))

    ET.strip_elements(response_tree,'{http://www.fdsn.org/xml/station/1}Created',with_tail=True)
    ET.strip_elements(response_tree,'{http://www.fdsn.org/xml/station/1}Module',with_tail=True)
    expected_content_tree = ET.fromstring(bytes(expected_content, encoding='utf-8'))

    ET.strip_elements(expected_content_tree,'{http://www.fdsn.org/xml/station/1}Created',with_tail=True)
    ET.strip_elements(expected_content_tree,'{http://www.fdsn.org/xml/station/1}Module',with_tail=True)

    print("***Expected**")
    print(ET.tostring(expected_content_tree, encoding=None, method='c14n2'))
    print("+++Response+++")
    print(ET.tostring(response_tree, encoding=None, method='c14n2'))
    print("-----")
    print(main.diff_texts(ET.tostring(response_tree, encoding=None, method='c14n2'),ET.tostring(expected_content_tree, encoding=None, method='c14n2')))
    #print(ET.canonicalize(response_tree))
    assert response.status_code == expected_status_code
    # ONE TEST WILL FAIL    assert (main.diff_texts(ET.tostring(response_tree, encoding=None, method='c14n2'),ET.tostring(expected_content_tree, encoding=None, method='c14n2'))==[])

    #assert ET.tostring(response_tree) == ET.tostring(expected_content_tree)
    assert (ET.tostring(expected_content_tree, encoding=None, method='c14n2') == ET.tostring(response_tree, encoding=None, method='c14n2'))
    #assert  ET.canonicalize(expected_content_tree) == ET.canonicalize(response_tree) Is the same?
#    assert (ET.tostring(expected_content_tree, encoding=None, method='c14n2') == ET.tostring(response_tree, encoding=None, method='c14n2'))

#    assert (expected_content_tree.getchildren().sort() == response_tree.getchildren().sort())


#############################################################################################################


#############################################################################################################

@pytest.mark.parametrize(
    "query,expected_status_code,expected_content,comment", testdatatxt

)

def test_content(query,expected_status_code,expected_content,comment,host):
    response = requests.get( "http://"+host+"/exist/apps/fdsn-station/fdsnws/station/1/query/?" + query)
    assert (response.status_code == expected_status_code)
    assert (response.text == expected_content)

############################################################################################################



#############################################################################################################

@pytest.mark.parametrize(
    "query,expected_status_code,expected_content,comment", testdataerrors

)

def test_errors(query,expected_status_code,expected_content,comment,host):
    response = requests.get( "http://"+host+"/exist/apps/fdsn-station/fdsnws/station/1/query/?" + query)
    assert (response.status_code == expected_status_code)
#Next assert check for the same string or for the first part if differences in tail
    assert (response.text.startswith(expected_content))

############################################################################################################



#############################################################################################################

@pytest.mark.parametrize(
    "post_data,expected_status_code,expected_content,comment", testdatapost

)

def test_post(post_data,expected_status_code,expected_content,comment,host):
    response = requests.post( "http://"+host+"/exist/apps/fdsn-station/fdsnws/station/1/query/?",data=post_data, headers={"Content-Type":"application/octet-stream"} )
    assert (response.status_code == expected_status_code)
    assert (response.text == expected_content)

############################################################################################################

#############################################################################################################

@pytest.mark.parametrize(
    "post_data,expected_status_code,expected_content,comment", testdataposterrors

)

def test_post_errors(post_data,expected_status_code,expected_content,comment,host):
    response = requests.post( "http://"+host+"/exist/apps/fdsn-station/fdsnws/station/1/query/?",data=post_data, headers={"Content-Type":"application/octet-stream"} )
    assert (response.status_code == expected_status_code)
    #Next assert check for the same string or for the first part if differences in tail
    assert (response.text.startswith(expected_content))

############################################################################################################


#############################################################################################################

@pytest.mark.parametrize(
    "post_data,expected_status_code,expected_content,comment", testdatapostxml

)

def test_post_xml(post_data,expected_status_code,expected_content,comment,host):
    print("Requesting: "+"http://"+host+"/exist/apps/fdsn-station/fdsnws/station/1/query?" + post_data)
    response = requests.post( "http://"+host+"/exist/apps/fdsn-station/fdsnws/station/1/query/?",data=post_data, headers={"Content-Type":"application/octet-stream","Encoding":"utf-8"} )

    print(response.text)
    response_tree = ET.fromstring(bytes(response.text, encoding='utf-8'))

    ET.strip_elements(response_tree,'{http://www.fdsn.org/xml/station/1}Created',with_tail=True)
    ET.strip_elements(response_tree,'{http://www.fdsn.org/xml/station/1}Module',with_tail=True)
    ET.strip_elements(response_tree,'{http://www.fdsn.org/xml/station/1}ModuleURI',with_tail=True)

    expected_content_tree = ET.fromstring(bytes(expected_content, encoding='utf-8'))
    ET.strip_elements(expected_content_tree,'{http://www.fdsn.org/xml/station/1}Created',with_tail=True)
    ET.strip_elements(expected_content_tree,'{http://www.fdsn.org/xml/station/1}Module',with_tail=True)
    ET.strip_elements(expected_content_tree,'{http://www.fdsn.org/xml/station/1}ModuleURI',with_tail=True)
    print("***Expected***")
    print(ET.tostring(expected_content_tree, encoding=None, method='c14n2'))
    print("+++Response+++")
    print(ET.tostring(response_tree, encoding=None, method='c14n2'))
    print("-----")

    assert response.status_code == expected_status_code
#    assert ET.tostring(response_tree) == ET.tostring(expected_content_tree)
    assert (ET.tostring(expected_content_tree, encoding=None, method='c14n2') == ET.tostring(response_tree, encoding=None, method='c14n2'))

#############################################################################################################

#### BEWARE TEST ON MINRADIUSKM DISPLAY NO CONTROL ON TEXT SORTING. ####
#### TODO FIX SORTING AND CHANGE TEST ACCORDINLGY                   ####


## List parameters to test
##starttime=
##endtime=
##startbefore=
##startafter=
##endbefore=
##endafter=
##network=
##station=
##channel=
##location=
##minlatitude=
##maxlatitude=
##minlongitude=
##maxlongitude=

##latitude
##longitude
##minradius
##maxradius
##minradiuskm
##maxradiuskm

##level
##includerestricted
##format

##formatted

##nodata

##visibility

##authoritative



##starttime ***
##endtime ***
##startbefore
##startafter
##endbefore
##endafter
##network
##station
##channel
##location
##minlatitude ***
##maxlatitude  ***
##minlongitude
##maxlongitude
##latitude
##longitude
##minradius
##maxradius
##minradiuskm
##maxradiuskm
##level
##includerestricted
##format
##formatted
##nodata
##visibility
##authoritative
