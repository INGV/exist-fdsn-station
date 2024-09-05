#!/usr/bin/env python
# coding: utf-8


import requests
# noinspection PyUnresolvedReferences
import pytest
import conftest
import difflib
#import xml.etree.ElementTree as ET
#from io import StringIO
import lxml.etree as ET
from xmldiff import main, formatting
from requests.auth import HTTPBasicAuth
import urllib.parse


############################################# DATA FOR TEST #############################################


### Contains query string, expected response code
testdataxml = [
("level=network&net=MN&station=AQ*&format=xml&nodata=404",200,'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.1</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?level=network&amp;net=MN&amp;station=AQ*&amp;format=xml&amp;nodata=404</ModuleURI><Created>2021-02-14T17:11:37.475Z</Created><Network code="MN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Mediterranean Very Broadband Seismographic Network</Description><Identifier type="DOI">10.13127/SD/fBBBtDtd6q</Identifier><ingv:Identifier>N22</ingv:Identifier><TotalNumberStations>2</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations></Network></FDSNStationXML>',"Network level for a double network station"),

('level=response&nodata=404&format=xml&station=AQT1',200,'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.57</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?level=response&amp;nodata=404&amp;format=xml&amp;station=AQT1</ModuleURI><Created>2023-12-19T13:33:06.582</Created><Network code="IV" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Italian Seismic Network</Description><Identifier type="DOI">10.13127/SD/X0FXnH7QfY</Identifier><ingv:Identifier>N1</ingv:Identifier><TotalNumberStations>7</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="AQT1" startDate="2011-07-22T00:00:00" endDate="2016-09-01T09:50:00" restrictedStatus="open"><ingv:Identifier>S578</ingv:Identifier><Latitude>42.77383</Latitude><Longitude>13.2935</Longitude><Elevation>770</Elevation><Site><Name>Arquata del Tronto</Name></Site><CreationDate>2011-07-22T00:00:00</CreationDate><TerminationDate>2016-09-01T23:59:00</TerminationDate><TotalNumberChannels>3</TotalNumberChannels><SelectedNumberChannels>3</SelectedNumberChannels><Channel code="EHE" startDate="2011-07-22T00:00:00" endDate="2016-09-01T09:50:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C7312</ingv:Identifier><Latitude>42.77383</Latitude><Longitude>13.2935</Longitude><Elevation>770</Elevation><Depth>1</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>LENNARTZ LE3D-1S</Description></Sensor><Response><InstrumentSensitivity><Value>503316000</Value><Frequency>10</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity><Stage number="1"><PolesZeros><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>V</Name></OutputUnits><PzTransferFunctionType>LAPLACE (RADIANS/SECOND)</PzTransferFunctionType><NormalizationFactor>1</NormalizationFactor><NormalizationFrequency>10</NormalizationFrequency><Zero number="0"><Real>0</Real><Imaginary>0</Imaginary></Zero><Zero number="1"><Real>0</Real><Imaginary>0</Imaginary></Zero><Zero number="2"><Real>0</Real><Imaginary>0</Imaginary></Zero><Pole number="0"><Real>-4.21</Real><Imaginary>-4.66</Imaginary></Pole><Pole number="1"><Real>-4.21</Real><Imaginary>4.66</Imaginary></Pole><Pole number="2"><Real>-2.105</Real><Imaginary>0</Imaginary></Pole></PolesZeros><StageGain><Value>400</Value><Frequency>10</Frequency></StageGain></Stage><Stage number="2"><Coefficients><InputUnits><Name>V</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType></Coefficients><Decimation><InputSampleRate>512000</InputSampleRate><Factor>640</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1258290</Value><Frequency>0</Frequency></StageGain></Stage><Stage number="3"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>1.32084E-5</Numerator><Numerator>4.5093E-5</Numerator><Numerator>9.07542E-5</Numerator><Numerator>0.000121148</Numerator><Numerator>8.63987E-6</Numerator><Numerator>-0.000343654</Numerator><Numerator>-0.000941793</Numerator><Numerator>-0.00159459</Numerator><Numerator>-0.00165481</Numerator><Numerator>-0.000460399</Numerator><Numerator>0.00230635</Numerator><Numerator>0.00612794</Numerator><Numerator>0.00888989</Numerator><Numerator>0.00786742</Numerator><Numerator>0.000943616</Numerator><Numerator>-0.0117493</Numerator><Numerator>-0.0256623</Numerator><Numerator>-0.0329694</Numerator><Numerator>-0.0249326</Numerator><Numerator>0.00448412</Numerator><Numerator>0.0536484</Numerator><Numerator>0.112885</Numerator><Numerator>0.166708</Numerator><Numerator>0.198566</Numerator><Numerator>0.198566</Numerator><Numerator>0.166708</Numerator><Numerator>0.112885</Numerator><Numerator>0.0536484</Numerator><Numerator>0.00448412</Numerator><Numerator>-0.00249325</Numerator><Numerator>-0.00329693</Numerator><Numerator>-0.00256623</Numerator><Numerator>-0.0117493</Numerator><Numerator>0.000943616</Numerator><Numerator>0.00786742</Numerator><Numerator>0.00888989</Numerator><Numerator>0.00612794</Numerator><Numerator>0.00230635</Numerator><Numerator>-0.000460399</Numerator><Numerator>-0.00165481</Numerator><Numerator>-0.00159459</Numerator><Numerator>-0.000941793</Numerator><Numerator>-0.000343654</Numerator><Numerator>8.63987E-6</Numerator><Numerator>0.000121148</Numerator><Numerator>9.07542E-5</Numerator><Numerator>4.5093E-5</Numerator><Numerator>1.32084E-5</Numerator></Coefficients><Decimation><InputSampleRate>800</InputSampleRate><Factor>4</Factor><Offset>0</Offset><Delay>0.029375</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>1</Frequency></StageGain></Stage><Stage number="4"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>-3.41751E-6</Numerator><Numerator>-1.78577E-5</Numerator><Numerator>-4.18766E-5</Numerator><Numerator>-4.74601E-5</Numerator><Numerator>1.63655E-6</Numerator><Numerator>8.59673E-5</Numerator><Numerator>0.000110275</Numerator><Numerator>1.4007E-5</Numerator><Numerator>-9.80008E-5</Numerator><Numerator>-4.53903E-5</Numerator><Numerator>0.00014368</Numerator><Numerator>0.000182139</Numerator><Numerator>-7.01793E-5</Numerator><Numerator>-0.000279562</Numerator><Numerator>-4.84709E-5</Numerator><Numerator>0.000373327</Numerator><Numerator>0.000285675</Numerator><Numerator>-0.000343436</Numerator><Numerator>-0.000562734</Numerator><Numerator>0.000169961</Numerator><Numerator>0.000842344</Numerator><Numerator>0.000211212</Numerator><Numerator>-0.000994496</Numerator><Numerator>-0.000768218</Numerator><Numerator>0.000911176</Numerator><Numerator>0.00143478</Numerator><Numerator>-0.000471472</Numerator><Numerator>-0.00204921</Numerator><Numerator>-0.000372798</Numerator><Numerator>0.00240641</Numerator><Numerator>0.00158943</Numerator><Numerator>-0.00226672</Numerator><Numerator>-0.00301564</Numerator><Numerator>0.00142968</Numerator><Numerator>0.00436787</Numerator><Numerator>0.000213522</Numerator><Numerator>-0.0052557</Numerator><Numerator>-0.00260751</Numerator><Numerator>0.00524704</Numerator><Numerator>0.00549468</Numerator><Numerator>-0.00394665</Numerator><Numerator>-0.00839707</Numerator><Numerator>0.00109986</Numerator><Numerator>0.0106478</Numerator><Numerator>0.00331465</Numerator><Numerator>-0.0114571</Numerator><Numerator>-0.00900784</Numerator><Numerator>0.0100127</Numerator><Numerator>0.0153433</Numerator><Numerator>-0.00558378</Numerator><Numerator>-0.0213364</Numerator><Numerator>-0.00240468</Numerator><Numerator>0.0256715</Numerator><Numerator>0.0143909</Numerator><Numerator>-0.0266601</Numerator><Numerator>-0.0309249</Numerator><Numerator>0.0219005</Numerator><Numerator>0.053611</Numerator><Numerator>-0.00660297</Numerator><Numerator>-0.0892565</Numerator><Numerator>-0.0368817</Numerator><Numerator>0.186534</Numerator><Numerator>0.403777</Numerator><Numerator>0.403777</Numerator><Numerator>0.186534</Numerator><Numerator>-0.0368817</Numerator><Numerator>-0.0892565</Numerator><Numerator>-0.00660297</Numerator><Numerator>0.053611</Numerator><Numerator>0.0219005</Numerator><Numerator>-0.0309249</Numerator><Numerator>-0.0266601</Numerator><Numerator>0.0143909</Numerator><Numerator>0.0256715</Numerator><Numerator>-0.00240468</Numerator><Numerator>-0.0213364</Numerator><Numerator>-0.00558378</Numerator><Numerator>0.0153433</Numerator><Numerator>0.0100127</Numerator><Numerator>-0.00900784</Numerator><Numerator>-0.0114571</Numerator><Numerator>0.00331465</Numerator><Numerator>0.0106478</Numerator><Numerator>0.00109986</Numerator><Numerator>-0.00839707</Numerator><Numerator>-0.00394665</Numerator><Numerator>0.00549468</Numerator><Numerator>0.00524704</Numerator><Numerator>-0.00260751</Numerator><Numerator>-0.0052557</Numerator><Numerator>0.000213522</Numerator><Numerator>0.00436787</Numerator><Numerator>0.00142968</Numerator><Numerator>-0.00301564</Numerator><Numerator>-0.00226672</Numerator><Numerator>0.00158943</Numerator><Numerator>0.00240641</Numerator><Numerator>-0.000372798</Numerator><Numerator>-0.00204921</Numerator><Numerator>-0.000471472</Numerator><Numerator>0.00143478</Numerator><Numerator>0.000911176</Numerator><Numerator>-0.000768218</Numerator><Numerator>-0.000994496</Numerator><Numerator>0.000211212</Numerator><Numerator>0.000842344</Numerator><Numerator>0.000169961</Numerator><Numerator>-0.000562734</Numerator><Numerator>-0.000343436</Numerator><Numerator>0.000285675</Numerator><Numerator>0.000373327</Numerator><Numerator>-4.84709E-5</Numerator><Numerator>-0.000279562</Numerator><Numerator>-7.01793E-5</Numerator><Numerator>0.000182139</Numerator><Numerator>0.00014368</Numerator><Numerator>-4.53903E-5</Numerator><Numerator>-9.80008E-5</Numerator><Numerator>1.4007E-5</Numerator><Numerator>0.000110275</Numerator><Numerator>8.59673E-5</Numerator><Numerator>1.63655E-6</Numerator><Numerator>-4.74601E-5</Numerator><Numerator>-4.18766E-5</Numerator><Numerator>-1.78577E-5</Numerator><Numerator>-3.41751E-6</Numerator></Coefficients><Decimation><InputSampleRate>200</InputSampleRate><Factor>2</Factor><Offset>0</Offset><Delay>0.3125</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>1</Frequency></StageGain></Stage></Response></Channel><Channel code="EHN" startDate="2011-07-22T00:00:00" endDate="2016-09-01T09:50:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C7314</ingv:Identifier><Latitude>42.77383</Latitude><Longitude>13.2935</Longitude><Elevation>770</Elevation><Depth>1</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>LENNARTZ LE3D-1S</Description></Sensor><Response><InstrumentSensitivity><Value>503316000</Value><Frequency>10</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity><Stage number="1"><PolesZeros><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>V</Name></OutputUnits><PzTransferFunctionType>LAPLACE (RADIANS/SECOND)</PzTransferFunctionType><NormalizationFactor>1</NormalizationFactor><NormalizationFrequency>10</NormalizationFrequency><Zero number="0"><Real>0</Real><Imaginary>0</Imaginary></Zero><Zero number="1"><Real>0</Real><Imaginary>0</Imaginary></Zero><Zero number="2"><Real>0</Real><Imaginary>0</Imaginary></Zero><Pole number="0"><Real>-4.21</Real><Imaginary>-4.66</Imaginary></Pole><Pole number="1"><Real>-4.21</Real><Imaginary>4.66</Imaginary></Pole><Pole number="2"><Real>-2.105</Real><Imaginary>0</Imaginary></Pole></PolesZeros><StageGain><Value>400</Value><Frequency>10</Frequency></StageGain></Stage><Stage number="2"><Coefficients><InputUnits><Name>V</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType></Coefficients><Decimation><InputSampleRate>512000</InputSampleRate><Factor>640</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1258290</Value><Frequency>0</Frequency></StageGain></Stage><Stage number="3"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>1.32084E-5</Numerator><Numerator>4.5093E-5</Numerator><Numerator>9.07542E-5</Numerator><Numerator>0.000121148</Numerator><Numerator>8.63987E-6</Numerator><Numerator>-0.000343654</Numerator><Numerator>-0.000941793</Numerator><Numerator>-0.00159459</Numerator><Numerator>-0.00165481</Numerator><Numerator>-0.000460399</Numerator><Numerator>0.00230635</Numerator><Numerator>0.00612794</Numerator><Numerator>0.00888989</Numerator><Numerator>0.00786742</Numerator><Numerator>0.000943616</Numerator><Numerator>-0.0117493</Numerator><Numerator>-0.0256623</Numerator><Numerator>-0.0329694</Numerator><Numerator>-0.0249326</Numerator><Numerator>0.00448412</Numerator><Numerator>0.0536484</Numerator><Numerator>0.112885</Numerator><Numerator>0.166708</Numerator><Numerator>0.198566</Numerator><Numerator>0.198566</Numerator><Numerator>0.166708</Numerator><Numerator>0.112885</Numerator><Numerator>0.0536484</Numerator><Numerator>0.00448412</Numerator><Numerator>-0.00249325</Numerator><Numerator>-0.00329693</Numerator><Numerator>-0.00256623</Numerator><Numerator>-0.0117493</Numerator><Numerator>0.000943616</Numerator><Numerator>0.00786742</Numerator><Numerator>0.00888989</Numerator><Numerator>0.00612794</Numerator><Numerator>0.00230635</Numerator><Numerator>-0.000460399</Numerator><Numerator>-0.00165481</Numerator><Numerator>-0.00159459</Numerator><Numerator>-0.000941793</Numerator><Numerator>-0.000343654</Numerator><Numerator>8.63987E-6</Numerator><Numerator>0.000121148</Numerator><Numerator>9.07542E-5</Numerator><Numerator>4.5093E-5</Numerator><Numerator>1.32084E-5</Numerator></Coefficients><Decimation><InputSampleRate>800</InputSampleRate><Factor>4</Factor><Offset>0</Offset><Delay>0.029375</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>1</Frequency></StageGain></Stage><Stage number="4"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>-3.41751E-6</Numerator><Numerator>-1.78577E-5</Numerator><Numerator>-4.18766E-5</Numerator><Numerator>-4.74601E-5</Numerator><Numerator>1.63655E-6</Numerator><Numerator>8.59673E-5</Numerator><Numerator>0.000110275</Numerator><Numerator>1.4007E-5</Numerator><Numerator>-9.80008E-5</Numerator><Numerator>-4.53903E-5</Numerator><Numerator>0.00014368</Numerator><Numerator>0.000182139</Numerator><Numerator>-7.01793E-5</Numerator><Numerator>-0.000279562</Numerator><Numerator>-4.84709E-5</Numerator><Numerator>0.000373327</Numerator><Numerator>0.000285675</Numerator><Numerator>-0.000343436</Numerator><Numerator>-0.000562734</Numerator><Numerator>0.000169961</Numerator><Numerator>0.000842344</Numerator><Numerator>0.000211212</Numerator><Numerator>-0.000994496</Numerator><Numerator>-0.000768218</Numerator><Numerator>0.000911176</Numerator><Numerator>0.00143478</Numerator><Numerator>-0.000471472</Numerator><Numerator>-0.00204921</Numerator><Numerator>-0.000372798</Numerator><Numerator>0.00240641</Numerator><Numerator>0.00158943</Numerator><Numerator>-0.00226672</Numerator><Numerator>-0.00301564</Numerator><Numerator>0.00142968</Numerator><Numerator>0.00436787</Numerator><Numerator>0.000213522</Numerator><Numerator>-0.0052557</Numerator><Numerator>-0.00260751</Numerator><Numerator>0.00524704</Numerator><Numerator>0.00549468</Numerator><Numerator>-0.00394665</Numerator><Numerator>-0.00839707</Numerator><Numerator>0.00109986</Numerator><Numerator>0.0106478</Numerator><Numerator>0.00331465</Numerator><Numerator>-0.0114571</Numerator><Numerator>-0.00900784</Numerator><Numerator>0.0100127</Numerator><Numerator>0.0153433</Numerator><Numerator>-0.00558378</Numerator><Numerator>-0.0213364</Numerator><Numerator>-0.00240468</Numerator><Numerator>0.0256715</Numerator><Numerator>0.0143909</Numerator><Numerator>-0.0266601</Numerator><Numerator>-0.0309249</Numerator><Numerator>0.0219005</Numerator><Numerator>0.053611</Numerator><Numerator>-0.00660297</Numerator><Numerator>-0.0892565</Numerator><Numerator>-0.0368817</Numerator><Numerator>0.186534</Numerator><Numerator>0.403777</Numerator><Numerator>0.403777</Numerator><Numerator>0.186534</Numerator><Numerator>-0.0368817</Numerator><Numerator>-0.0892565</Numerator><Numerator>-0.00660297</Numerator><Numerator>0.053611</Numerator><Numerator>0.0219005</Numerator><Numerator>-0.0309249</Numerator><Numerator>-0.0266601</Numerator><Numerator>0.0143909</Numerator><Numerator>0.0256715</Numerator><Numerator>-0.00240468</Numerator><Numerator>-0.0213364</Numerator><Numerator>-0.00558378</Numerator><Numerator>0.0153433</Numerator><Numerator>0.0100127</Numerator><Numerator>-0.00900784</Numerator><Numerator>-0.0114571</Numerator><Numerator>0.00331465</Numerator><Numerator>0.0106478</Numerator><Numerator>0.00109986</Numerator><Numerator>-0.00839707</Numerator><Numerator>-0.00394665</Numerator><Numerator>0.00549468</Numerator><Numerator>0.00524704</Numerator><Numerator>-0.00260751</Numerator><Numerator>-0.0052557</Numerator><Numerator>0.000213522</Numerator><Numerator>0.00436787</Numerator><Numerator>0.00142968</Numerator><Numerator>-0.00301564</Numerator><Numerator>-0.00226672</Numerator><Numerator>0.00158943</Numerator><Numerator>0.00240641</Numerator><Numerator>-0.000372798</Numerator><Numerator>-0.00204921</Numerator><Numerator>-0.000471472</Numerator><Numerator>0.00143478</Numerator><Numerator>0.000911176</Numerator><Numerator>-0.000768218</Numerator><Numerator>-0.000994496</Numerator><Numerator>0.000211212</Numerator><Numerator>0.000842344</Numerator><Numerator>0.000169961</Numerator><Numerator>-0.000562734</Numerator><Numerator>-0.000343436</Numerator><Numerator>0.000285675</Numerator><Numerator>0.000373327</Numerator><Numerator>-4.84709E-5</Numerator><Numerator>-0.000279562</Numerator><Numerator>-7.01793E-5</Numerator><Numerator>0.000182139</Numerator><Numerator>0.00014368</Numerator><Numerator>-4.53903E-5</Numerator><Numerator>-9.80008E-5</Numerator><Numerator>1.4007E-5</Numerator><Numerator>0.000110275</Numerator><Numerator>8.59673E-5</Numerator><Numerator>1.63655E-6</Numerator><Numerator>-4.74601E-5</Numerator><Numerator>-4.18766E-5</Numerator><Numerator>-1.78577E-5</Numerator><Numerator>-3.41751E-6</Numerator></Coefficients><Decimation><InputSampleRate>200</InputSampleRate><Factor>2</Factor><Offset>0</Offset><Delay>0.3125</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>1</Frequency></StageGain></Stage></Response></Channel><Channel code="EHZ" startDate="2011-07-22T00:00:00" endDate="2016-09-01T09:50:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C7310</ingv:Identifier><Latitude>42.77383</Latitude><Longitude>13.2935</Longitude><Elevation>770</Elevation><Depth>1</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>LENNARTZ LE3D-1S</Description></Sensor><Response><InstrumentSensitivity><Value>503316000</Value><Frequency>10</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity><Stage number="1"><PolesZeros><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>V</Name></OutputUnits><PzTransferFunctionType>LAPLACE (RADIANS/SECOND)</PzTransferFunctionType><NormalizationFactor>1</NormalizationFactor><NormalizationFrequency>10</NormalizationFrequency><Zero number="0"><Real>0</Real><Imaginary>0</Imaginary></Zero><Zero number="1"><Real>0</Real><Imaginary>0</Imaginary></Zero><Zero number="2"><Real>0</Real><Imaginary>0</Imaginary></Zero><Pole number="0"><Real>-4.21</Real><Imaginary>-4.66</Imaginary></Pole><Pole number="1"><Real>-4.21</Real><Imaginary>4.66</Imaginary></Pole><Pole number="2"><Real>-2.105</Real><Imaginary>0</Imaginary></Pole></PolesZeros><StageGain><Value>400</Value><Frequency>10</Frequency></StageGain></Stage><Stage number="2"><Coefficients><InputUnits><Name>V</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType></Coefficients><Decimation><InputSampleRate>512000</InputSampleRate><Factor>640</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1258290</Value><Frequency>0</Frequency></StageGain></Stage><Stage number="3"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>1.32084E-5</Numerator><Numerator>4.5093E-5</Numerator><Numerator>9.07542E-5</Numerator><Numerator>0.000121148</Numerator><Numerator>8.63987E-6</Numerator><Numerator>-0.000343654</Numerator><Numerator>-0.000941793</Numerator><Numerator>-0.00159459</Numerator><Numerator>-0.00165481</Numerator><Numerator>-0.000460399</Numerator><Numerator>0.00230635</Numerator><Numerator>0.00612794</Numerator><Numerator>0.00888989</Numerator><Numerator>0.00786742</Numerator><Numerator>0.000943616</Numerator><Numerator>-0.0117493</Numerator><Numerator>-0.0256623</Numerator><Numerator>-0.0329694</Numerator><Numerator>-0.0249326</Numerator><Numerator>0.00448412</Numerator><Numerator>0.0536484</Numerator><Numerator>0.112885</Numerator><Numerator>0.166708</Numerator><Numerator>0.198566</Numerator><Numerator>0.198566</Numerator><Numerator>0.166708</Numerator><Numerator>0.112885</Numerator><Numerator>0.0536484</Numerator><Numerator>0.00448412</Numerator><Numerator>-0.00249325</Numerator><Numerator>-0.00329693</Numerator><Numerator>-0.00256623</Numerator><Numerator>-0.0117493</Numerator><Numerator>0.000943616</Numerator><Numerator>0.00786742</Numerator><Numerator>0.00888989</Numerator><Numerator>0.00612794</Numerator><Numerator>0.00230635</Numerator><Numerator>-0.000460399</Numerator><Numerator>-0.00165481</Numerator><Numerator>-0.00159459</Numerator><Numerator>-0.000941793</Numerator><Numerator>-0.000343654</Numerator><Numerator>8.63987E-6</Numerator><Numerator>0.000121148</Numerator><Numerator>9.07542E-5</Numerator><Numerator>4.5093E-5</Numerator><Numerator>1.32084E-5</Numerator></Coefficients><Decimation><InputSampleRate>800</InputSampleRate><Factor>4</Factor><Offset>0</Offset><Delay>0.029375</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>1</Frequency></StageGain></Stage><Stage number="4"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>-3.41751E-6</Numerator><Numerator>-1.78577E-5</Numerator><Numerator>-4.18766E-5</Numerator><Numerator>-4.74601E-5</Numerator><Numerator>1.63655E-6</Numerator><Numerator>8.59673E-5</Numerator><Numerator>0.000110275</Numerator><Numerator>1.4007E-5</Numerator><Numerator>-9.80008E-5</Numerator><Numerator>-4.53903E-5</Numerator><Numerator>0.00014368</Numerator><Numerator>0.000182139</Numerator><Numerator>-7.01793E-5</Numerator><Numerator>-0.000279562</Numerator><Numerator>-4.84709E-5</Numerator><Numerator>0.000373327</Numerator><Numerator>0.000285675</Numerator><Numerator>-0.000343436</Numerator><Numerator>-0.000562734</Numerator><Numerator>0.000169961</Numerator><Numerator>0.000842344</Numerator><Numerator>0.000211212</Numerator><Numerator>-0.000994496</Numerator><Numerator>-0.000768218</Numerator><Numerator>0.000911176</Numerator><Numerator>0.00143478</Numerator><Numerator>-0.000471472</Numerator><Numerator>-0.00204921</Numerator><Numerator>-0.000372798</Numerator><Numerator>0.00240641</Numerator><Numerator>0.00158943</Numerator><Numerator>-0.00226672</Numerator><Numerator>-0.00301564</Numerator><Numerator>0.00142968</Numerator><Numerator>0.00436787</Numerator><Numerator>0.000213522</Numerator><Numerator>-0.0052557</Numerator><Numerator>-0.00260751</Numerator><Numerator>0.00524704</Numerator><Numerator>0.00549468</Numerator><Numerator>-0.00394665</Numerator><Numerator>-0.00839707</Numerator><Numerator>0.00109986</Numerator><Numerator>0.0106478</Numerator><Numerator>0.00331465</Numerator><Numerator>-0.0114571</Numerator><Numerator>-0.00900784</Numerator><Numerator>0.0100127</Numerator><Numerator>0.0153433</Numerator><Numerator>-0.00558378</Numerator><Numerator>-0.0213364</Numerator><Numerator>-0.00240468</Numerator><Numerator>0.0256715</Numerator><Numerator>0.0143909</Numerator><Numerator>-0.0266601</Numerator><Numerator>-0.0309249</Numerator><Numerator>0.0219005</Numerator><Numerator>0.053611</Numerator><Numerator>-0.00660297</Numerator><Numerator>-0.0892565</Numerator><Numerator>-0.0368817</Numerator><Numerator>0.186534</Numerator><Numerator>0.403777</Numerator><Numerator>0.403777</Numerator><Numerator>0.186534</Numerator><Numerator>-0.0368817</Numerator><Numerator>-0.0892565</Numerator><Numerator>-0.00660297</Numerator><Numerator>0.053611</Numerator><Numerator>0.0219005</Numerator><Numerator>-0.0309249</Numerator><Numerator>-0.0266601</Numerator><Numerator>0.0143909</Numerator><Numerator>0.0256715</Numerator><Numerator>-0.00240468</Numerator><Numerator>-0.0213364</Numerator><Numerator>-0.00558378</Numerator><Numerator>0.0153433</Numerator><Numerator>0.0100127</Numerator><Numerator>-0.00900784</Numerator><Numerator>-0.0114571</Numerator><Numerator>0.00331465</Numerator><Numerator>0.0106478</Numerator><Numerator>0.00109986</Numerator><Numerator>-0.00839707</Numerator><Numerator>-0.00394665</Numerator><Numerator>0.00549468</Numerator><Numerator>0.00524704</Numerator><Numerator>-0.00260751</Numerator><Numerator>-0.0052557</Numerator><Numerator>0.000213522</Numerator><Numerator>0.00436787</Numerator><Numerator>0.00142968</Numerator><Numerator>-0.00301564</Numerator><Numerator>-0.00226672</Numerator><Numerator>0.00158943</Numerator><Numerator>0.00240641</Numerator><Numerator>-0.000372798</Numerator><Numerator>-0.00204921</Numerator><Numerator>-0.000471472</Numerator><Numerator>0.00143478</Numerator><Numerator>0.000911176</Numerator><Numerator>-0.000768218</Numerator><Numerator>-0.000994496</Numerator><Numerator>0.000211212</Numerator><Numerator>0.000842344</Numerator><Numerator>0.000169961</Numerator><Numerator>-0.000562734</Numerator><Numerator>-0.000343436</Numerator><Numerator>0.000285675</Numerator><Numerator>0.000373327</Numerator><Numerator>-4.84709E-5</Numerator><Numerator>-0.000279562</Numerator><Numerator>-7.01793E-5</Numerator><Numerator>0.000182139</Numerator><Numerator>0.00014368</Numerator><Numerator>-4.53903E-5</Numerator><Numerator>-9.80008E-5</Numerator><Numerator>1.4007E-5</Numerator><Numerator>0.000110275</Numerator><Numerator>8.59673E-5</Numerator><Numerator>1.63655E-6</Numerator><Numerator>-4.74601E-5</Numerator><Numerator>-4.18766E-5</Numerator><Numerator>-1.78577E-5</Numerator><Numerator>-3.41751E-6</Numerator></Coefficients><Decimation><InputSampleRate>200</InputSampleRate><Factor>2</Factor><Offset>0</Offset><Delay>0.3125</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>1</Frequency></StageGain></Stage></Response></Channel></Station></Network></FDSNStationXML>','Response level single station'),

("level=network&net=*&format=xml&nodata=404",200,'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.55</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?level=network&amp;net=*&amp;format=xml&amp;nodata=404</ModuleURI><Created>2023-03-01T15:14:51.353</Created><Network xmlns:css30="http://www.brtt.com/xml/station/css30" code="IT" startDate="1970-01-01T00:00:00" endDate="2599-12-31T23:59:59" css30:netType="-" restrictedStatus="open"><Description>Italian Strong Motion Network (RAN)</Description><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations></Network><Network code="IV" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Italian Seismic Network</Description><Identifier type="DOI">10.13127/SD/X0FXnH7QfY</Identifier><ingv:Identifier>N1</ingv:Identifier><TotalNumberStations>7</TotalNumberStations><SelectedNumberStations>7</SelectedNumberStations></Network><Network code="IX" startDate="2005-01-01T00:00:00" restrictedStatus="open"><Description>Irpinia Seismic Network, Italy</Description><ingv:Identifier>N41</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations></Network><Network code="MN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Mediterranean Very Broadband Seismographic Network</Description><Identifier type="DOI">10.13127/SD/fBBBtDtd6q</Identifier><ingv:Identifier>N22</ingv:Identifier><TotalNumberStations>2</TotalNumberStations><SelectedNumberStations>2</SelectedNumberStations></Network><Network code="NI" startDate="2002-01-01T00:00:00" restrictedStatus="open"><Description>North-East Italy Broadband Network</Description><ingv:Identifier>N13</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations></Network><Network code="OX" startDate="2016-01-01T00:00:00" restrictedStatus="open"><Description>North-East Italy Seismic Network</Description><ingv:Identifier>N111</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations></Network><Network code="S" startDate="2008-07-03T00:00:00" restrictedStatus="open" alternateCode="Test alternate code" historicalCode="Test historical code"><Description>Seismology at School Program</Description><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations></Network><Network code="SI" startDate="2006-01-01T00:00:00" restrictedStatus="open"><Description>Sudtirol Network, Italy</Description><Identifier type="citation">Pintore et al. Multiple Identifier</Identifier><Identifier type="DOI">https://doi.org/10.7914/SN/3T_2020</Identifier><ingv:Identifier>N18</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations></Network><Network code="TH" startDate="1980-01-01T00:00:00" sourceID="http://test.exist.fdsn.station/xml/station/1234" restrictedStatus="partial" alternateCode="Test alternate code" historicalCode="Test historical code"><Description>Thuringia Seismic Network, Uni Jena</Description><Identifier type="DOI">10.7914/SN/TH</Identifier><TotalNumberStations>4</TotalNumberStations><SelectedNumberStations>4</SelectedNumberStations></Network><Network code="TV" startDate="2008-01-01T00:00:00" restrictedStatus="open"><Description>INGV Experiments Network</Description><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations></Network><Network code="Z3" startDate="2005-06-05T00:00:00" endDate="2007-04-30T00:00:00" restrictedStatus="open"><Description>Egelados project, RUB Bochum, Germany</Description><Identifier type="DOI">10.14470/M87550267382</Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations></Network><Network code="Z3" startDate="2015-01-01T00:00:00" endDate="2022-12-31T00:00:00" restrictedStatus="closed"><Description>AlpArray Seismic Network (AASN) temporary component</Description><Identifier type="DOI">10.12686/alparray/z3_2015</Identifier><ingv:Identifier>N81</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations></Network></FDSNStationXML>',"Network level for all networks"),



("level=station&nodata=404",200,'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns="http://www.fdsn.org/xml/station/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?level=station&amp;nodata=404</ModuleURI><Network xmlns:css30="http://www.brtt.com/xml/station/css30" code="IT" startDate="1970-01-01T00:00:00" endDate="2599-12-31T23:59:59" css30:netType="-" restrictedStatus="open"><Description>Italian Strong Motion Network (RAN)</Description><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="CMA" startDate="2007-11-13T00:00:00" endDate="2599-12-31T23:59:59.999" css30:staType="-"><Latitude>39.414900</Latitude><Longitude>16.818000</Longitude><Elevation>610.000000</Elevation><Site><Name>Campana</Name></Site><Vault>-</Vault><CreationDate>2007-11-13T00:00:00</CreationDate></Station></Network><Network code="IV" restrictedStatus="open" startDate="1988-01-01T00:00:00"><Description>Italian Seismic Network</Description><Identifier type="DOI">10.13127/SD/X0FXnH7QfY</Identifier><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">N1</ingv:Identifier><TotalNumberStations>7</TotalNumberStations><SelectedNumberStations>7</SelectedNumberStations><Station code="ACATE" restrictedStatus="open" startDate="2019-02-28T05:59:00"><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">S7381</ingv:Identifier><Latitude>37.02398</Latitude><Longitude>14.50064</Longitude><Elevation>210</Elevation><Site><Name>ACATE</Name></Site><CreationDate>2019-02-28T05:59:00</CreationDate></Station><Station code="ACER" restrictedStatus="open" startDate="2007-07-05T12:00:00"><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">S1</ingv:Identifier><Latitude>40.7867</Latitude><Longitude>15.9427</Longitude><Elevation>690</Elevation><Site><Name>Acerenza</Name></Site><CreationDate>2007-07-05T12:00:00</CreationDate></Station><Station code="AQT1" endDate="2016-09-01T09:50:00" restrictedStatus="open" startDate="2011-07-22T00:00:00"><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">S578</ingv:Identifier><Latitude>42.77383</Latitude><Longitude>13.2935</Longitude><Elevation>770</Elevation><Site><Name>Arquata del Tronto</Name></Site><CreationDate>2011-07-22T00:00:00</CreationDate><TerminationDate>2016-09-01T23:59:00</TerminationDate></Station><Station code="AQU" endDate="2008-10-15T00:00:00" restrictedStatus="open" startDate="2003-03-01T00:00:00"><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">S7</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Site><Name>L\'Aquila, Italy</Name></Site><CreationDate>1988-08-01T00:00:00</CreationDate></Station><Station code="ARVD" restrictedStatus="open" startDate="2003-03-01T00:00:00"><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">S9</ingv:Identifier><Latitude>43.49807</Latitude><Longitude>12.94153</Longitude><Elevation>461</Elevation><Site><Name>ARCEVIA 2</Name></Site><CreationDate>2003-03-01T00:00:00</CreationDate></Station><Station code="IMTC" restrictedStatus="open" startDate="1988-01-01T00:00:00"><ingv:AlternateNetworks xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd"><ingv:AlternateNetwork code="_MOST" startDate="2011-03-14T00:00:00" type="VIRTUAL"><Description>"Monitoring of Structures"</Description></ingv:AlternateNetwork></ingv:AlternateNetworks><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">S3001</ingv:Identifier><Latitude>40.7209</Latitude><Longitude>13.8758</Longitude><Elevation>59</Elevation><Site><Name>Ischia - Monte Corvo</Name></Site><CreationDate>1988-01-01T00:00:00</CreationDate></Station><Station code="VBKN" restrictedStatus="open" startDate="1988-01-01T00:00:00"><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">S3031</ingv:Identifier><Latitude>40.83</Latitude><Longitude>14.4299</Longitude><Elevation>951</Elevation><Site><Name>Vesuvio - Bunker Nord</Name></Site><CreationDate>1988-01-01T00:00:00</CreationDate></Station></Network><Network code="IX" restrictedStatus="open" startDate="2005-01-01T00:00:00"><Description>Irpinia Seismic Network, Italy</Description><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">N41</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="AND3" restrictedStatus="open" startDate="2013-12-17T00:00:00"><ingv:AlternateNetworks xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd"><ingv:AlternateNetwork code="_MOST" startDate="2011-03-14T00:00:00" type="VIRTUAL"><Description>"Monitoring of Structures"</Description></ingv:AlternateNetwork><ingv:AlternateNetwork code="_MOST-ICO" startDate="2011-03-14T00:00:00" type="VIRTUAL"><Description>"Monitoring of Structures in Central-Eastern Italy (Italia Centro Orientale)"</Description></ingv:AlternateNetwork><ingv:AlternateNetwork code="_NFOTABOO" startDate="2010-04-01T00:00:00" type="VIRTUAL"><Description>"The Altotiberina Near Fault Observatory (TABOO), Italy."</Description></ingv:AlternateNetwork></ingv:AlternateNetworks><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">S6221</ingv:Identifier><Latitude>40.9298</Latitude><Longitude>15.3331</Longitude><Elevation>905</Elevation><Site><Name>Station Andretta, Italy</Name></Site><CreationDate>2013-12-17T00:00:00</CreationDate></Station></Network><Network code="MN" restrictedStatus="open" startDate="1988-01-01T00:00:00"><Description>Mediterranean Very Broadband Seismographic Network</Description><Identifier type="DOI">10.13127/SD/fBBBtDtd6q</Identifier><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">N22</ingv:Identifier><TotalNumberStations>2</TotalNumberStations><SelectedNumberStations>2</SelectedNumberStations><Station code="AQU" restrictedStatus="open" startDate="1988-08-01T00:00:00"><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">S7</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Site><Name>L\'Aquila, Italy</Name></Site><CreationDate>1988-08-01T00:00:00</CreationDate></Station><Station code="ARPR" restrictedStatus="open" startDate="2014-01-23T00:00:00"><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">S2151</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Site><Name>Arapgir, Turkey</Name></Site><CreationDate>2014-01-23T00:00:00</CreationDate></Station></Network><Network code="NI" restrictedStatus="open" startDate="2002-01-01T00:00:00"><Description>North-East Italy Broadband Network</Description><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">N13</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="ACOM" endDate="2015-12-31T23:59:59" restrictedStatus="open" startDate="2005-02-01T12:00:00"><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">S3451</ingv:Identifier><Latitude>46.548</Latitude><Longitude>13.5137</Longitude><Elevation>1788</Elevation><Site><Name>Acomizza</Name></Site><CreationDate>2005-02-01T12:00:00</CreationDate></Station></Network><Network code="OX" restrictedStatus="open" startDate="2016-01-01T00:00:00"><Description>North-East Italy Seismic Network</Description><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">N111</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="ACOM" restrictedStatus="open" startDate="2016-01-01T00:00:00"><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">S3451</ingv:Identifier><Latitude>46.548</Latitude><Longitude>13.5137</Longitude><Elevation>1788</Elevation><Site><Name>Acomizza</Name></Site><CreationDate>2005-02-01T12:00:00</CreationDate></Station></Network><Network code="S" startDate="2008-07-03T00:00:00" restrictedStatus="open" alternateCode="Test alternate code" historicalCode="Test historical code"><Description>Seismology at School Program</Description><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="ELFMC" endDate="2015-07-01T00:01:54.843" restrictedStatus="open" startDate="2010-05-11T00:00:00"><Latitude>47.3855</Latitude><Longitude>8.5996</Longitude><Elevation>650</Elevation><Site><Name>Gockhausen, Lycee Francais de Marie Curie, ZH</Name><Country>Switzerland</Country></Site><CreationDate>2010-05-11T00:00:00</CreationDate></Station></Network><Network code="SI" restrictedStatus="open" startDate="2006-01-01T00:00:00"><Description>Sudtirol Network, Italy</Description><Identifier type="citation">Pintore et al. Multiple Identifier</Identifier><Identifier type="DOI">https://doi.org/10.7914/SN/3T_2020</Identifier><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">N18</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="ABSI" restrictedStatus="open" startDate="2006-11-21T14:16:45"><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">S122</ingv:Identifier><Latitude>46.7285</Latitude><Longitude>11.3205</Longitude><Elevation>1801</Elevation><Site><Name>Aberstuckl (Sarntal)</Name></Site><CreationDate>2006-11-21T14:16:45</CreationDate></Station></Network><Network code="TH" startDate="1980-01-01T00:00:00" sourceID="http://test.exist.fdsn.station/xml/station/1234" restrictedStatus="partial" alternateCode="Test alternate code" historicalCode="Test historical code"><Description>Thuringia Seismic Network, Uni Jena</Description><Identifier type="DOI">10.7914/SN/TH</Identifier><TotalNumberStations>4</TotalNumberStations><SelectedNumberStations>4</SelectedNumberStations><Station code="ABG1" startDate="2011-10-18T16:00:00" endDate="2012-11-22T12:00:00" restrictedStatus="open"><Latitude>50.96532</Latitude><Longitude>12.57208</Longitude><Elevation>203</Elevation><Site><Name>UJENA Station Forsthaus Leinawald, Germany</Name><Country>Germany</Country></Site><CreationDate>2011-10-18T16:00:00</CreationDate></Station><Station code="ABG1" startDate="2012-11-22T12:00:00" restrictedStatus="closed"><Latitude>50.96757</Latitude><Longitude>12.57625</Longitude><Elevation>203</Elevation><Site><Name>UJENA Station Forsthaus Leinawald, Germany</Name><Country>Germany</Country></Site><CreationDate>2012-11-22T12:00:00</CreationDate></Station><Station code="ANNA" startDate="2014-03-25T10:00:00" endDate="2017-12-04T00:00:00" restrictedStatus="open"><Latitude>50.88399</Latitude><Longitude>12.64365</Longitude><Elevation>249</Elevation><Site><Name>UJENA Station St. Anna Fundgrube, Germany</Name><Country>Germany</Country></Site><CreationDate>2014-03-25T10:00:00Z</CreationDate></Station><Station code="ANNA" startDate="2017-12-04T00:00:00" restrictedStatus="open"><Latitude>50.88902</Latitude><Longitude>12.64499</Longitude><Elevation>235</Elevation><Site><Name>UJENA Station St. Anna Fundgrube, Germany</Name><Country>Germany</Country></Site><CreationDate>2017-12-04T00:00:00Z</CreationDate></Station></Network><Network code="TV" restrictedStatus="open" startDate="2008-01-01T00:00:00"><Description>INGV Experiments Network</Description><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="AT04" endDate="2011-02-09T09:55:00" restrictedStatus="open" startDate="2010-03-31T00:00:00"><Latitude>43.254269</Latitude><Longitude>12.450467</Longitude><Elevation>595</Elevation><Site><Name>Castiglione Aldobrando</Name></Site><CreationDate>2010-03-31T00:00:00</CreationDate><TerminationDate>2011-02-09T23:00:00</TerminationDate></Station></Network><Network code="Z3" endDate="2007-04-30T00:00:00" restrictedStatus="open" startDate="2005-06-05T00:00:00"><Description>Egelados project, RUB Bochum, Germany</Description><Identifier type="DOI">10.14470/M87550267382</Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="AT04" endDate="2007-02-23T00:00:00" restrictedStatus="open" startDate="2005-11-02T00:00:00"><Latitude>37.7252</Latitude><Longitude>24.0496</Longitude><Elevation>23</Elevation><Site><Name>Station Egelados Network, Greece</Name><Country>Greece</Country></Site><CreationDate>2005-11-02T00:00:00</CreationDate></Station></Network><Network code="Z3" endDate="2022-12-31T00:00:00" restrictedStatus="closed" startDate="2015-01-01T00:00:00"><Description>AlpArray Seismic Network (AASN) temporary component</Description><Identifier type="DOI">10.12686/alparray/z3_2015</Identifier><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">N81</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="A319A" endDate="2019-04-10T23:59:00" restrictedStatus="closed" startDate="2015-12-11T12:06:34"><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">S3331</ingv:Identifier><Latitude>43.476425</Latitude><Longitude>10.578689</Longitude><Elevation>343</Elevation><Site><Name>Santa Luce (PI)</Name></Site><CreationDate>2015-12-11T12:06:34</CreationDate><TerminationDate>2019-04-11T23:59:00</TerminationDate></Station></Network></FDSNStationXML>',"All station in the database, level station"),

("level=channel&net=MN&format=xml&nodata=404",200,'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.1</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?level=channel&amp;net=MN&amp;format=xml&amp;nodata=404</ModuleURI><Created>2021-02-14T15:24:55.099Z</Created><Network code="MN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Mediterranean Very Broadband Seismographic Network</Description><Identifier type="DOI">10.13127/SD/fBBBtDtd6q</Identifier><ingv:Identifier>N22</ingv:Identifier><TotalNumberStations>2</TotalNumberStations><SelectedNumberStations>2</SelectedNumberStations><Station code="AQU" startDate="1988-08-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S7</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Site><Name>L\'Aquila, Italy</Name></Site><CreationDate>1988-08-01T00:00:00</CreationDate><TotalNumberChannels>151</TotalNumberChannels><SelectedNumberChannels>151</SelectedNumberChannels><Channel code="BHE" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2469</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-5250000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHE" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2481</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-1046640000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHE" startDate="1995-08-28T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2493</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1047020000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHE" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2509</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1075730000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHE" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2521</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-1063680000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHE" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2533</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1063680000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHE" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2545</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>983662000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHE" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2557</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>592092000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHE" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2572</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780269000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHE" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13221</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHE" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82391</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2470</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-5250000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2482</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-1055040000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="1995-08-28T00:00:00" endDate="1996-09-05T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2494</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1049580000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="1996-09-06T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2505</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1059600000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2510</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1091140000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2522</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-1092770000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2534</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1092770000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2546</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1014990000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2558</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>600347000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2573</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>778823000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13181</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82311</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2471</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-5250000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2483</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-1054200000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="1995-08-28T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2495</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1062530000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2511</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1044970000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2523</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-1069590000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2535</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1069590000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2547</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1001740000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2559</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>598652000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2574</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>778718000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13261</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82351</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHE" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2560</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>592092000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHE" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2575</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780269000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHE" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13231</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHE" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82401</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHN" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2561</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>600347000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHN" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2576</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>778823000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHN" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13191</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHN" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82321</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2562</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>598652000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2577</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>778718000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13271</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82361</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HLE" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2587</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>KINEMETRICS EPISENSOR</Description></Sensor><Response><InstrumentSensitivity><Value>534331</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s**2</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HLE" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13311</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>KINEMETRICS EPISENSOR</Description></Sensor><Response><InstrumentSensitivity><Value>530244</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s**2</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HLN" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2588</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>KINEMETRICS EPISENSOR</Description></Sensor><Response><InstrumentSensitivity><Value>537500</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s**2</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HLN" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13301</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>KINEMETRICS EPISENSOR</Description></Sensor><Response><InstrumentSensitivity><Value>530244</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s**2</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HLZ" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2589</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>KINEMETRICS EPISENSOR</Description></Sensor><Response><InstrumentSensitivity><Value>537691</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s**2</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HLZ" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13321</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>KINEMETRICS EPISENSOR</Description></Sensor><Response><InstrumentSensitivity><Value>530244</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s**2</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HNE" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82451</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP</Description></Sensor><Response><InstrumentSensitivity><Value>427693</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s**2</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HNN" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82431</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP</Description></Sensor><Response><InstrumentSensitivity><Value>427693</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s**2</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HNZ" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82441</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP</Description></Sensor><Response><InstrumentSensitivity><Value>427693</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s**2</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2472</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-21000000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2484</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-4186560000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="1995-08-28T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2496</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1047020000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2512</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1075730000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2524</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-1063680000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2536</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1063680000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2548</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>983662000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2563</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>592092000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2578</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780269000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13241</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82411</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2473</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-21000000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2485</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-4220160000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="1995-08-28T00:00:00" endDate="1996-09-05T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2497</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1049580000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="1996-09-06T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2506</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1059600000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2513</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1091140000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2525</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-1092770000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2537</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1092770000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2549</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1014990000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2564</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>600347000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2579</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>778823000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13201</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82331</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2474</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-21000000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2486</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-4216800000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="1995-08-28T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2498</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1062530000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2514</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1044970000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2526</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-1069590000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2538</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1069590000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2550</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>1001740000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2565</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>598652000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2580</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>778718000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13281</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82371</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHE" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2475</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-84000000000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHE" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2487</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-16746200000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHE" startDate="1995-08-28T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2499</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4188090000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHE" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2515</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4302930000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHE" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2527</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-4254720000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHE" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2539</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4254720000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHE" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2551</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>3934650000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHE" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2566</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>2368370000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHE" startDate="2008-02-19T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2581</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>3121070000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHN" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2476</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-84000000000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHN" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2488</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-16880600000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHN" startDate="1995-08-28T00:00:00" endDate="1996-09-05T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2500</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4198310000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHN" startDate="1996-09-06T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2507</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4238420000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHN" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2516</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4364570000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHN" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2528</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-4371080000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHN" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2540</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4371080000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHN" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2552</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4059940000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHN" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2567</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>2401390000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHN" startDate="2008-02-19T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2582</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>3115290000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHZ" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2477</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-84000000000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHZ" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2489</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-16867200000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHZ" startDate="1995-08-28T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2501</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4250120000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHZ" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2517</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4179890000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHZ" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2529</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-4278370000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHZ" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2541</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4278370000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHZ" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2553</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4006970000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHZ" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2568</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>2394610000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHZ" startDate="2008-02-19T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2583</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>3114870000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2478</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-84000000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2490</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-16746200000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="1995-08-28T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2502</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4188090000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2518</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4302930000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2530</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-4254720000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2542</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4254720000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2554</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>3934650000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2569</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>2368370000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2584</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>3121070000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13251</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>3120000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82421</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2479</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-84000000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2491</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-16880600000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="1995-08-28T00:00:00" endDate="1996-09-05T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2503</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4198310000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="1996-09-06T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2508</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4238420000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2519</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4364570000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2531</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-4371080000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2543</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4371080000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2555</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1H-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4059940000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2570</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>2401390000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2585</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>3115290000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13211</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>3120000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82341</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="1988-08-01T00:00:00" endDate="1991-07-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2480</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-84000000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="1991-08-01T00:00:00" endDate="1995-08-27T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2492</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-16867200000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="1995-08-28T00:00:00" endDate="1998-02-04T11:30:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2504</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4250120000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="1998-02-04T11:30:01" endDate="1999-06-16T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2520</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4179890000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="1999-06-16T11:00:00" endDate="1999-08-31T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2532</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>-4278370000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="1999-08-31T10:00:01" endDate="2000-09-26T10:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2544</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4278370000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="2000-09-26T10:00:01" endDate="2002-06-05T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2556</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-1V-VBB</Description></Sensor><Response><InstrumentSensitivity><Value>4006970000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2571</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>2394610000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2586</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>3114870000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13291</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>3120000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82381</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel></Station><Station code="ARPR" startDate="2014-01-23T00:00:00" restrictedStatus="open"><ingv:Identifier>S2151</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Site><Name>Arapgir, Turkey</Name></Site><CreationDate>2014-01-23T00:00:00</CreationDate><TotalNumberChannels>9</TotalNumberChannels><SelectedNumberChannels>9</SelectedNumberChannels><Channel code="BHE" startDate="2014-01-23T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C27341</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Depth>0</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-3G</Description></Sensor><Response><InstrumentSensitivity><Value>2516580000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" startDate="2014-01-23T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C27351</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-3G</Description></Sensor><Response><InstrumentSensitivity><Value>2516580000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="2014-01-23T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C27361</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-3G</Description></Sensor><Response><InstrumentSensitivity><Value>2516580000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHE" startDate="2014-01-23T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C27401</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Depth>0</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-3G</Description></Sensor><Response><InstrumentSensitivity><Value>2516580000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHN" startDate="2014-01-23T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C27411</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-3G</Description></Sensor><Response><InstrumentSensitivity><Value>2516580000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="2014-01-23T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C27421</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-3G</Description></Sensor><Response><InstrumentSensitivity><Value>2516580000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHE" startDate="2014-01-23T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C27521</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Depth>0</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-3G</Description></Sensor><Response><InstrumentSensitivity><Value>10066300000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHN" startDate="2014-01-23T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C27531</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>0.1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-3G</Description></Sensor><Response><InstrumentSensitivity><Value>10066300000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="2014-01-23T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C27541</ingv:Identifier><Latitude>39.09289</Latitude><Longitude>38.33557</Longitude><Elevation>1537</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-3G</Description></Sensor><Response><InstrumentSensitivity><Value>10066300000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel></Station></Network></FDSNStationXML>',"MN at channel level"),



("level=channel&net=MN,IV&format=xml&nodata=404&station=AQU,ACER&channel=HHZ,EHZ",200,'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.1</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?level=channel&amp;net=MN,IV&amp;format=xml&amp;nodata=404&amp;station=AQU,ACER&amp;channel=HHZ,EHZ</ModuleURI><Created>2021-02-14T15:28:37.803Z</Created><Network code="IV" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Italian Seismic Network</Description><Identifier type="DOI">10.13127/SD/X0FXnH7QfY</Identifier><ingv:Identifier>N1</ingv:Identifier><TotalNumberStations>7</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="ACER" startDate="2007-07-05T12:00:00" restrictedStatus="open"><ingv:Identifier>S1</ingv:Identifier><Latitude>40.7867</Latitude><Longitude>15.9427</Longitude><Elevation>690</Elevation><Site><Name>Acerenza</Name></Site><CreationDate>2007-07-05T12:00:00</CreationDate><TotalNumberChannels>33</TotalNumberChannels><SelectedNumberChannels>2</SelectedNumberChannels><Channel code="HHZ" startDate="2007-07-05T12:00:00" endDate="2014-05-08T11:42:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C6</ingv:Identifier><Latitude>40.7867</Latitude><Longitude>15.9427</Longitude><Elevation>690</Elevation><Depth>1</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>1500000000</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2014-05-08T11:42:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C27281</ingv:Identifier><Latitude>40.7867</Latitude><Longitude>15.9427</Longitude><Elevation>690</Elevation><Depth>1</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>1179650000</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel></Station></Network><Network code="MN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Mediterranean Very Broadband Seismographic Network</Description><Identifier type="DOI">10.13127/SD/fBBBtDtd6q</Identifier><ingv:Identifier>N22</ingv:Identifier><TotalNumberStations>2</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="AQU" startDate="1988-08-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S7</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Site><Name>L\'Aquila, Italy</Name></Site><CreationDate>1988-08-01T00:00:00</CreationDate><TotalNumberChannels>151</TotalNumberChannels><SelectedNumberChannels>4</SelectedNumberChannels><Channel code="HHZ" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2562</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>598652000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2577</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>778718000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2011-04-13T00:00:00" endDate="2017-12-31T07:56:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C13271</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>780000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82361</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel></Station></Network></FDSNStationXML>',""),

("level=station&net=MN,IV&format=xml&nodata=404&station=AQU,ACER&channel=HHZ,EHZ",200,
'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.1</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?level=station&amp;net=MN,IV&amp;format=xml&amp;nodata=404&amp;station=AQU,ACER&amp;channel=HHZ,EHZ</ModuleURI><Created>2021-02-14T15:36:22.336Z</Created><Network code="IV" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Italian Seismic Network</Description><Identifier type="DOI">10.13127/SD/X0FXnH7QfY</Identifier><ingv:Identifier>N1</ingv:Identifier><TotalNumberStations>7</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="ACER" startDate="2007-07-05T12:00:00" restrictedStatus="open"><ingv:Identifier>S1</ingv:Identifier><Latitude>40.7867</Latitude><Longitude>15.9427</Longitude><Elevation>690</Elevation><Site><Name>Acerenza</Name></Site><CreationDate>2007-07-05T12:00:00</CreationDate></Station></Network><Network code="MN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Mediterranean Very Broadband Seismographic Network</Description><Identifier type="DOI">10.13127/SD/fBBBtDtd6q</Identifier><ingv:Identifier>N22</ingv:Identifier><TotalNumberStations>2</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="AQU" startDate="1988-08-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S7</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Site><Name>L\'Aquila, Italy</Name></Site><CreationDate>1988-08-01T00:00:00</CreationDate></Station></Network></FDSNStationXML>',"Networks stations and channel for station on two networks"),

("format=xml&level=response&station=A319A",200,
'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.1</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?format=xml&amp;level=response&amp;station=A319A</ModuleURI><Created>2021-02-08T09:51:44</Created><Network code="Z3" startDate="2015-01-01T00:00:00" endDate="2022-12-31T00:00:00" restrictedStatus="closed"><Description>AlpArray Seismic Network (AASN) temporary component</Description><Identifier type="DOI">10.12686/alparray/z3_2015</Identifier><ingv:Identifier>N81</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="A319A" startDate="2015-12-11T12:06:34" endDate="2019-04-10T23:59:00" restrictedStatus="closed"><ingv:Identifier>S3331</ingv:Identifier><Latitude>43.476425</Latitude><Longitude>10.578689</Longitude><Elevation>343</Elevation><Site><Name>Santa Luce (PI)</Name></Site><CreationDate>2015-12-11T12:06:34</CreationDate><TerminationDate>2019-04-11T23:59:00</TerminationDate><TotalNumberChannels>3</TotalNumberChannels><SelectedNumberChannels>3</SelectedNumberChannels><Channel code="HHE" startDate="2015-12-11T12:06:34" endDate="2019-04-10T23:59:00" restrictedStatus="closed" locationCode=""><ingv:Identifier>C37641</ingv:Identifier><Latitude>43.476425</Latitude><Longitude>10.578689</Longitude><Elevation>343</Elevation><Depth>1</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><CalibrationUnits><Name>V</Name><Description>Volts</Description></CalibrationUnits><Sensor><Description>NANOMETRICS TRILLIUM-120C</Description></Sensor><Response><InstrumentSensitivity><Value>749.1</Value><Frequency>1</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity><Stage number="1"><PolesZeros><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>V</Name></OutputUnits><PzTransferFunctionType>LAPLACE (RADIANS/SECOND)</PzTransferFunctionType><NormalizationFactor>818400000000</NormalizationFactor><NormalizationFrequency>1</NormalizationFrequency><Zero number="0"><Real>0</Real><Imaginary>0</Imaginary></Zero><Zero number="1"><Real>0</Real><Imaginary>0</Imaginary></Zero><Zero number="2"><Real>-434.1</Real><Imaginary>0</Imaginary></Zero><Pole number="0"><Real>-371.2</Real><Imaginary>0</Imaginary></Pole><Pole number="1"><Real>-0.03691</Real><Imaginary>0.03712</Imaginary></Pole><Pole number="2"><Real>-0.03691</Real><Imaginary>-0.03712</Imaginary></Pole><Pole number="3"><Real>-373.9</Real><Imaginary>475.5</Imaginary></Pole><Pole number="4"><Real>-373.9</Real><Imaginary>-475.5</Imaginary></Pole><Pole number="5"><Real>-588.4</Real><Imaginary>1508</Imaginary></Pole><Pole number="6"><Real>-588.4</Real><Imaginary>-1508</Imaginary></Pole></PolesZeros><StageGain><Value>749.1</Value><Frequency>1</Frequency></StageGain></Stage><Stage number="2"><Coefficients><InputUnits><Name>V</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType></Coefficients><Decimation><InputSampleRate>0</InputSampleRate><Factor>1</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0</Frequency></StageGain></Stage></Response></Channel><Channel code="HHN" startDate="2015-12-11T12:06:34" endDate="2019-04-10T23:59:00" restrictedStatus="closed" locationCode=""><ingv:Identifier>C37651</ingv:Identifier><Latitude>43.476425</Latitude><Longitude>10.578689</Longitude><Elevation>343</Elevation><Depth>1</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><CalibrationUnits><Name>V</Name><Description>Volts</Description></CalibrationUnits><Sensor><Description>NANOMETRICS TRILLIUM-120C</Description></Sensor><Response><InstrumentSensitivity><Value>749.1</Value><Frequency>1</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity><Stage number="1"><PolesZeros><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>V</Name></OutputUnits><PzTransferFunctionType>LAPLACE (RADIANS/SECOND)</PzTransferFunctionType><NormalizationFactor>818400000000</NormalizationFactor><NormalizationFrequency>1</NormalizationFrequency><Zero number="0"><Real>0</Real><Imaginary>0</Imaginary></Zero><Zero number="1"><Real>0</Real><Imaginary>0</Imaginary></Zero><Zero number="2"><Real>-434.1</Real><Imaginary>0</Imaginary></Zero><Pole number="0"><Real>-371.2</Real><Imaginary>0</Imaginary></Pole><Pole number="1"><Real>-0.03691</Real><Imaginary>0.03712</Imaginary></Pole><Pole number="2"><Real>-0.03691</Real><Imaginary>-0.03712</Imaginary></Pole><Pole number="3"><Real>-373.9</Real><Imaginary>475.5</Imaginary></Pole><Pole number="4"><Real>-373.9</Real><Imaginary>-475.5</Imaginary></Pole><Pole number="5"><Real>-588.4</Real><Imaginary>1508</Imaginary></Pole><Pole number="6"><Real>-588.4</Real><Imaginary>-1508</Imaginary></Pole></PolesZeros><StageGain><Value>749.1</Value><Frequency>1</Frequency></StageGain></Stage><Stage number="2"><Coefficients><InputUnits><Name>V</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType></Coefficients><Decimation><InputSampleRate>0</InputSampleRate><Factor>1</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0</Frequency></StageGain></Stage></Response></Channel><Channel code="HHZ" startDate="2015-12-11T12:06:34" endDate="2019-04-10T23:59:00" restrictedStatus="closed" locationCode=""><ingv:Identifier>C37661</ingv:Identifier><Latitude>43.476425</Latitude><Longitude>10.578689</Longitude><Elevation>343</Elevation><Depth>1</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><CalibrationUnits><Name>V</Name><Description>Volts</Description></CalibrationUnits><Sensor><Description>NANOMETRICS TRILLIUM-120C</Description></Sensor><Response><InstrumentSensitivity><Value>749.1</Value><Frequency>1</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity><Stage number="1"><PolesZeros><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>V</Name></OutputUnits><PzTransferFunctionType>LAPLACE (RADIANS/SECOND)</PzTransferFunctionType><NormalizationFactor>818400000000</NormalizationFactor><NormalizationFrequency>1</NormalizationFrequency><Zero number="0"><Real>0</Real><Imaginary>0</Imaginary></Zero><Zero number="1"><Real>0</Real><Imaginary>0</Imaginary></Zero><Zero number="2"><Real>-434.1</Real><Imaginary>0</Imaginary></Zero><Pole number="0"><Real>-371.2</Real><Imaginary>0</Imaginary></Pole><Pole number="1"><Real>-0.03691</Real><Imaginary>0.03712</Imaginary></Pole><Pole number="2"><Real>-0.03691</Real><Imaginary>-0.03712</Imaginary></Pole><Pole number="3"><Real>-373.9</Real><Imaginary>475.5</Imaginary></Pole><Pole number="4"><Real>-373.9</Real><Imaginary>-475.5</Imaginary></Pole><Pole number="5"><Real>-588.4</Real><Imaginary>1508</Imaginary></Pole><Pole number="6"><Real>-588.4</Real><Imaginary>-1508</Imaginary></Pole></PolesZeros><StageGain><Value>749.1</Value><Frequency>1</Frequency></StageGain></Stage><Stage number="2"><Coefficients><InputUnits><Name>V</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType></Coefficients><Decimation><InputSampleRate>0</InputSampleRate><Factor>1</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0</Frequency></StageGain></Stage></Response></Channel></Station></Network></FDSNStationXML>',"Query a single station"),


("level=response&net=*&nodata=404&format=xml&channel=HHZ&starttime=1988-01-01&endtime=1988-02-01",200,
'<?xml version="1.0" encoding="UTF-8"?>\n\
<FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.52.0</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?level=response&amp;net=*&amp;nodata=404&amp;format=xml&amp;channel=HHZ&amp;starttime=1988-01-01&amp;endtime=1988-02-01</ModuleURI><Created>2022-09-13T12:36:29.739Z</Created><Network code="IV" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Italian Seismic Network</Description><Identifier type="DOI">10.13127/SD/X0FXnH7QfY</Identifier><ingv:Identifier>N1</ingv:Identifier><TotalNumberStations>7</TotalNumberStations><SelectedNumberStations>2</SelectedNumberStations><Station code="IMTC" startDate="1988-01-01T00:00:00" restrictedStatus="open"><ingv:AlternateNetworks><ingv:AlternateNetwork type="VIRTUAL" code="_MOST" startDate="2011-03-14T00:00:00"><Description>"Monitoring of Structures"</Description></ingv:AlternateNetwork></ingv:AlternateNetworks><ingv:Identifier>S3001</ingv:Identifier><Latitude>40.7209</Latitude><Longitude>13.8758</Longitude><Elevation>59</Elevation><Site><Name>Ischia - Monte Corvo</Name></Site><CreationDate>1988-01-01T00:00:00</CreationDate><TotalNumberChannels>3</TotalNumberChannels><SelectedNumberChannels>1</SelectedNumberChannels><Channel code="HHZ" startDate="1988-01-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C34861</ingv:Identifier><Latitude>40.7209</Latitude><Longitude>13.8758</Longitude><Elevation>59</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><CalibrationUnits><Name>V</Name><Description>Volts</Description></CalibrationUnits><Sensor><Description>GURALP CMG-40T-60S</Description></Sensor><Response><InstrumentSensitivity><Value>243822000</Value><Frequency>1</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity><Stage number="1"><PolesZeros><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>V</Name></OutputUnits><PzTransferFunctionType>LAPLACE (RADIANS/SECOND)</PzTransferFunctionType><NormalizationFactor>571508000</NormalizationFactor><NormalizationFrequency>1</NormalizationFrequency><Zero number="0"><Real>0</Real><Imaginary>0</Imaginary></Zero><Zero number="1"><Real>0</Real><Imaginary>0</Imaginary></Zero><Pole number="0"><Real>-0.074016</Real><Imaginary>0.074016</Imaginary></Pole><Pole number="1"><Real>-0.074016</Real><Imaginary>-0.074016</Imaginary></Pole><Pole number="2"><Real>-502.65</Real><Imaginary>0</Imaginary></Pole><Pole number="3"><Real>-1005</Real><Imaginary>0</Imaginary></Pole><Pole number="4"><Real>-1131</Real><Imaginary>0</Imaginary></Pole></PolesZeros><StageGain><Value>800</Value><Frequency>1</Frequency></StageGain></Stage><Stage number="2"><StageGain><Value>1</Value><Frequency>0.05</Frequency></StageGain></Stage><Stage number="3"><Coefficients><InputUnits><Name>V</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>1</Numerator></Coefficients><Decimation><InputSampleRate>512000</InputSampleRate><Factor>1</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>304878</Value><Frequency>0.05</Frequency></StageGain></Stage><Stage number="4"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>3.1E-5</Numerator><Numerator>0.000153</Numerator><Numerator>0.000458</Numerator><Numerator>0.001068</Numerator><Numerator>0.002136</Numerator><Numerator>0.003845</Numerator><Numerator>0.006409</Numerator><Numerator>0.010071</Numerator><Numerator>0.014954</Numerator><Numerator>0.021057</Numerator><Numerator>0.028259</Numerator><Numerator>0.036316</Numerator><Numerator>0.044861</Numerator><Numerator>0.053406</Numerator><Numerator>0.06134</Numerator><Numerator>0.067932</Numerator><Numerator>0.072632</Numerator><Numerator>0.075073</Numerator><Numerator>0.075073</Numerator><Numerator>0.072632</Numerator><Numerator>0.067932</Numerator><Numerator>0.06134</Numerator><Numerator>0.053406</Numerator><Numerator>0.044861</Numerator><Numerator>0.036316</Numerator><Numerator>0.028259</Numerator><Numerator>0.021057</Numerator><Numerator>0.014954</Numerator><Numerator>0.010071</Numerator><Numerator>0.006409</Numerator><Numerator>0.003845</Numerator><Numerator>0.002136</Numerator><Numerator>0.001068</Numerator><Numerator>0.000458</Numerator><Numerator>0.000153</Numerator><Numerator>3.1E-5</Numerator></Coefficients><Decimation><InputSampleRate>512000</InputSampleRate><Factor>8</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0.05</Frequency></StageGain></Stage><Stage number="5"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>0.03125</Numerator><Numerator>0.15625</Numerator><Numerator>0.3125</Numerator><Numerator>0.3125</Numerator><Numerator>0.15625</Numerator><Numerator>0.03125</Numerator></Coefficients><Decimation><InputSampleRate>64000</InputSampleRate><Factor>2</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0.05</Frequency></StageGain></Stage><Stage number="6"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>0.015625</Numerator><Numerator>0.09375</Numerator><Numerator>0.234375</Numerator><Numerator>0.3125</Numerator><Numerator>0.234375</Numerator><Numerator>0.09375</Numerator><Numerator>0.015625</Numerator></Coefficients><Decimation><InputSampleRate>32000</InputSampleRate><Factor>2</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0.05</Frequency></StageGain></Stage><Stage number="7"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>0.0016</Numerator><Numerator>0.0064</Numerator><Numerator>0.016</Numerator><Numerator>0.032</Numerator><Numerator>0.056</Numerator><Numerator>0.0832</Numerator><Numerator>0.1088</Numerator><Numerator>0.128</Numerator><Numerator>0.136</Numerator><Numerator>0.128</Numerator><Numerator>0.1088</Numerator><Numerator>0.0832</Numerator><Numerator>0.056</Numerator><Numerator>0.032</Numerator><Numerator>0.016</Numerator><Numerator>0.0064</Numerator><Numerator>0.0016</Numerator></Coefficients><Decimation><InputSampleRate>16000</InputSampleRate><Factor>5</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0.05</Frequency></StageGain></Stage><Stage number="8"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>0.03125</Numerator><Numerator>0.15625</Numerator><Numerator>0.3125</Numerator><Numerator>0.3125</Numerator><Numerator>0.15625</Numerator><Numerator>0.03125</Numerator></Coefficients><Decimation><InputSampleRate>3200</InputSampleRate><Factor>2</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0.05</Frequency></StageGain></Stage><Stage number="9"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>0.015625</Numerator><Numerator>0.09375</Numerator><Numerator>0.234375</Numerator><Numerator>0.3125</Numerator><Numerator>0.234375</Numerator><Numerator>0.09375</Numerator><Numerator>0.015625</Numerator></Coefficients><Decimation><InputSampleRate>1600</InputSampleRate><Factor>2</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0.05</Frequency></StageGain></Stage><Stage number="10"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>1.4E-5</Numerator><Numerator>4.9E-5</Numerator><Numerator>9.8E-5</Numerator><Numerator>0.000131</Numerator><Numerator>9.0E-6</Numerator><Numerator>-0.000372</Numerator><Numerator>-0.001018</Numerator><Numerator>-0.001724</Numerator><Numerator>-0.001789</Numerator><Numerator>-0.000498</Numerator><Numerator>0.002494</Numerator><Numerator>0.006626</Numerator><Numerator>0.009613</Numerator><Numerator>0.008507</Numerator><Numerator>0.00102</Numerator><Numerator>-0.012705</Numerator><Numerator>-0.027749</Numerator><Numerator>-0.035651</Numerator><Numerator>-0.02696</Numerator><Numerator>0.004849</Numerator><Numerator>0.058011</Numerator><Numerator>0.122065</Numerator><Numerator>0.180265</Numerator><Numerator>0.214714</Numerator><Numerator>0.214714</Numerator><Numerator>0.180265</Numerator><Numerator>0.122065</Numerator><Numerator>0.058011</Numerator><Numerator>0.004849</Numerator><Numerator>-0.02696</Numerator><Numerator>-0.035651</Numerator><Numerator>-0.027749</Numerator><Numerator>-0.012705</Numerator><Numerator>0.00102</Numerator><Numerator>0.008507</Numerator><Numerator>0.009613</Numerator><Numerator>0.006626</Numerator><Numerator>0.002494</Numerator><Numerator>-0.000498</Numerator><Numerator>-0.001789</Numerator><Numerator>-0.001724</Numerator><Numerator>-0.001018</Numerator><Numerator>-0.000372</Numerator><Numerator>9.0E-6</Numerator><Numerator>0.000131</Numerator><Numerator>9.8E-5</Numerator><Numerator>4.9E-5</Numerator><Numerator>1.4E-5</Numerator></Coefficients><Decimation><InputSampleRate>800</InputSampleRate><Factor>4</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0.05</Frequency></StageGain></Stage><Stage number="11"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>-3.0E-6</Numerator><Numerator>-1.8E-5</Numerator><Numerator>-4.2E-5</Numerator><Numerator>-4.7E-5</Numerator><Numerator>2.0E-6</Numerator><Numerator>8.6E-5</Numerator><Numerator>0.00011</Numerator><Numerator>1.4E-5</Numerator><Numerator>-9.8E-5</Numerator><Numerator>-4.5E-5</Numerator><Numerator>0.000144</Numerator><Numerator>0.000182</Numerator><Numerator>-7.0E-5</Numerator><Numerator>-0.00028</Numerator><Numerator>-4.8E-5</Numerator><Numerator>0.000373</Numerator><Numerator>0.000286</Numerator><Numerator>-0.000343</Numerator><Numerator>-0.000563</Numerator><Numerator>0.00017</Numerator><Numerator>0.000842</Numerator><Numerator>0.000211</Numerator><Numerator>-0.000994</Numerator><Numerator>-0.000768</Numerator><Numerator>0.000911</Numerator><Numerator>0.001435</Numerator><Numerator>-0.000471</Numerator><Numerator>-0.002049</Numerator><Numerator>-0.000373</Numerator><Numerator>0.002406</Numerator><Numerator>0.001589</Numerator><Numerator>-0.002267</Numerator><Numerator>-0.003016</Numerator><Numerator>0.00143</Numerator><Numerator>0.004368</Numerator><Numerator>0.000214</Numerator><Numerator>-0.005256</Numerator><Numerator>-0.002608</Numerator><Numerator>0.005247</Numerator><Numerator>0.005495</Numerator><Numerator>-0.003947</Numerator><Numerator>-0.008397</Numerator><Numerator>0.0011</Numerator><Numerator>0.010648</Numerator><Numerator>0.003315</Numerator><Numerator>-0.011457</Numerator><Numerator>-0.009008</Numerator><Numerator>0.010013</Numerator><Numerator>0.015343</Numerator><Numerator>-0.005584</Numerator><Numerator>-0.021337</Numerator><Numerator>-0.002405</Numerator><Numerator>0.025672</Numerator><Numerator>0.014391</Numerator><Numerator>-0.02666</Numerator><Numerator>-0.030925</Numerator><Numerator>0.021901</Numerator><Numerator>0.053611</Numerator><Numerator>-0.006603</Numerator><Numerator>-0.089257</Numerator><Numerator>-0.036882</Numerator><Numerator>0.186535</Numerator><Numerator>0.403778</Numerator><Numerator>0.403778</Numerator><Numerator>0.186535</Numerator><Numerator>-0.036882</Numerator><Numerator>-0.089257</Numerator><Numerator>-0.006603</Numerator><Numerator>0.053611</Numerator><Numerator>0.021901</Numerator><Numerator>-0.030925</Numerator><Numerator>-0.02666</Numerator><Numerator>0.014391</Numerator><Numerator>0.025672</Numerator><Numerator>-0.002405</Numerator><Numerator>-0.021337</Numerator><Numerator>-0.005584</Numerator><Numerator>0.015343</Numerator><Numerator>0.010013</Numerator><Numerator>-0.009008</Numerator><Numerator>-0.011457</Numerator><Numerator>0.003315</Numerator><Numerator>0.010648</Numerator><Numerator>0.0011</Numerator><Numerator>-0.008397</Numerator><Numerator>-0.003947</Numerator><Numerator>0.005495</Numerator><Numerator>0.005247</Numerator><Numerator>-0.002608</Numerator><Numerator>-0.005256</Numerator><Numerator>0.000214</Numerator><Numerator>0.004368</Numerator><Numerator>0.00143</Numerator><Numerator>-0.003016</Numerator><Numerator>-0.002267</Numerator><Numerator>0.001589</Numerator><Numerator>0.002406</Numerator><Numerator>-0.000373</Numerator><Numerator>-0.002049</Numerator><Numerator>-0.000471</Numerator><Numerator>0.001435</Numerator><Numerator>0.000911</Numerator><Numerator>-0.000768</Numerator><Numerator>-0.000994</Numerator><Numerator>0.000211</Numerator><Numerator>0.000842</Numerator><Numerator>0.00017</Numerator><Numerator>-0.000563</Numerator><Numerator>-0.000343</Numerator><Numerator>0.000286</Numerator><Numerator>0.000373</Numerator><Numerator>-4.8E-5</Numerator><Numerator>-0.00028</Numerator><Numerator>-7.0E-5</Numerator><Numerator>0.000182</Numerator><Numerator>0.000144</Numerator><Numerator>-4.5E-5</Numerator><Numerator>-9.8E-5</Numerator><Numerator>1.4E-5</Numerator><Numerator>0.00011</Numerator><Numerator>8.6E-5</Numerator><Numerator>2.0E-6</Numerator><Numerator>-4.7E-5</Numerator><Numerator>-4.2E-5</Numerator><Numerator>-1.8E-5</Numerator><Numerator>-3.0E-6</Numerator></Coefficients><Decimation><InputSampleRate>200</InputSampleRate><Factor>2</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0.05</Frequency></StageGain></Stage></Response></Channel></Station><Station code="VBKN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S3031</ingv:Identifier><Latitude>40.83</Latitude><Longitude>14.4299</Longitude><Elevation>951</Elevation><Site><Name>Vesuvio - Bunker Nord</Name></Site><CreationDate>1988-01-01T00:00:00</CreationDate><TotalNumberChannels>3</TotalNumberChannels><SelectedNumberChannels>1</SelectedNumberChannels><Channel code="HHZ" startDate="1988-01-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C34951</ingv:Identifier><Latitude>40.83</Latitude><Longitude>14.4299</Longitude><Elevation>951</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><CalibrationUnits><Name>V</Name><Description>Volts</Description></CalibrationUnits><Sensor><Description>GURALP CMG-40T-60S</Description></Sensor><Response><InstrumentSensitivity><Value>243822000</Value><Frequency>1</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity><Stage number="1"><PolesZeros><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>V</Name></OutputUnits><PzTransferFunctionType>LAPLACE (RADIANS/SECOND)</PzTransferFunctionType><NormalizationFactor>571508000</NormalizationFactor><NormalizationFrequency>1</NormalizationFrequency><Zero number="0"><Real>0</Real><Imaginary>0</Imaginary></Zero><Zero number="1"><Real>0</Real><Imaginary>0</Imaginary></Zero><Pole number="0"><Real>-0.074016</Real><Imaginary>0.074016</Imaginary></Pole><Pole number="1"><Real>-0.074016</Real><Imaginary>-0.074016</Imaginary></Pole><Pole number="2"><Real>-502.65</Real><Imaginary>0</Imaginary></Pole><Pole number="3"><Real>-1005</Real><Imaginary>0</Imaginary></Pole><Pole number="4"><Real>-1131</Real><Imaginary>0</Imaginary></Pole></PolesZeros><StageGain><Value>800</Value><Frequency>1</Frequency></StageGain></Stage><Stage number="2"><StageGain><Value>1</Value><Frequency>0.05</Frequency></StageGain></Stage><Stage number="3"><Coefficients><InputUnits><Name>V</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>1</Numerator></Coefficients><Decimation><InputSampleRate>512000</InputSampleRate><Factor>1</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>304878</Value><Frequency>0.05</Frequency></StageGain></Stage><Stage number="4"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>3.1E-5</Numerator><Numerator>0.000153</Numerator><Numerator>0.000458</Numerator><Numerator>0.001068</Numerator><Numerator>0.002136</Numerator><Numerator>0.003845</Numerator><Numerator>0.006409</Numerator><Numerator>0.010071</Numerator><Numerator>0.014954</Numerator><Numerator>0.021057</Numerator><Numerator>0.028259</Numerator><Numerator>0.036316</Numerator><Numerator>0.044861</Numerator><Numerator>0.053406</Numerator><Numerator>0.06134</Numerator><Numerator>0.067932</Numerator><Numerator>0.072632</Numerator><Numerator>0.075073</Numerator><Numerator>0.075073</Numerator><Numerator>0.072632</Numerator><Numerator>0.067932</Numerator><Numerator>0.06134</Numerator><Numerator>0.053406</Numerator><Numerator>0.044861</Numerator><Numerator>0.036316</Numerator><Numerator>0.028259</Numerator><Numerator>0.021057</Numerator><Numerator>0.014954</Numerator><Numerator>0.010071</Numerator><Numerator>0.006409</Numerator><Numerator>0.003845</Numerator><Numerator>0.002136</Numerator><Numerator>0.001068</Numerator><Numerator>0.000458</Numerator><Numerator>0.000153</Numerator><Numerator>3.1E-5</Numerator></Coefficients><Decimation><InputSampleRate>512000</InputSampleRate><Factor>8</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0.05</Frequency></StageGain></Stage><Stage number="5"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>0.03125</Numerator><Numerator>0.15625</Numerator><Numerator>0.3125</Numerator><Numerator>0.3125</Numerator><Numerator>0.15625</Numerator><Numerator>0.03125</Numerator></Coefficients><Decimation><InputSampleRate>64000</InputSampleRate><Factor>2</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0.05</Frequency></StageGain></Stage><Stage number="6"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>0.015625</Numerator><Numerator>0.09375</Numerator><Numerator>0.234375</Numerator><Numerator>0.3125</Numerator><Numerator>0.234375</Numerator><Numerator>0.09375</Numerator><Numerator>0.015625</Numerator></Coefficients><Decimation><InputSampleRate>32000</InputSampleRate><Factor>2</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0.05</Frequency></StageGain></Stage><Stage number="7"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>0.0016</Numerator><Numerator>0.0064</Numerator><Numerator>0.016</Numerator><Numerator>0.032</Numerator><Numerator>0.056</Numerator><Numerator>0.0832</Numerator><Numerator>0.1088</Numerator><Numerator>0.128</Numerator><Numerator>0.136</Numerator><Numerator>0.128</Numerator><Numerator>0.1088</Numerator><Numerator>0.0832</Numerator><Numerator>0.056</Numerator><Numerator>0.032</Numerator><Numerator>0.016</Numerator><Numerator>0.0064</Numerator><Numerator>0.0016</Numerator></Coefficients><Decimation><InputSampleRate>16000</InputSampleRate><Factor>5</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0.05</Frequency></StageGain></Stage><Stage number="8"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>0.03125</Numerator><Numerator>0.15625</Numerator><Numerator>0.3125</Numerator><Numerator>0.3125</Numerator><Numerator>0.15625</Numerator><Numerator>0.03125</Numerator></Coefficients><Decimation><InputSampleRate>3200</InputSampleRate><Factor>2</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0.05</Frequency></StageGain></Stage><Stage number="9"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>0.015625</Numerator><Numerator>0.09375</Numerator><Numerator>0.234375</Numerator><Numerator>0.3125</Numerator><Numerator>0.234375</Numerator><Numerator>0.09375</Numerator><Numerator>0.015625</Numerator></Coefficients><Decimation><InputSampleRate>1600</InputSampleRate><Factor>2</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0.05</Frequency></StageGain></Stage><Stage number="10"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>1.4E-5</Numerator><Numerator>4.9E-5</Numerator><Numerator>9.8E-5</Numerator><Numerator>0.000131</Numerator><Numerator>9.0E-6</Numerator><Numerator>-0.000372</Numerator><Numerator>-0.001018</Numerator><Numerator>-0.001724</Numerator><Numerator>-0.001789</Numerator><Numerator>-0.000498</Numerator><Numerator>0.002494</Numerator><Numerator>0.006626</Numerator><Numerator>0.009613</Numerator><Numerator>0.008507</Numerator><Numerator>0.00102</Numerator><Numerator>-0.012705</Numerator><Numerator>-0.027749</Numerator><Numerator>-0.035651</Numerator><Numerator>-0.02696</Numerator><Numerator>0.004849</Numerator><Numerator>0.058011</Numerator><Numerator>0.122065</Numerator><Numerator>0.180265</Numerator><Numerator>0.214714</Numerator><Numerator>0.214714</Numerator><Numerator>0.180265</Numerator><Numerator>0.122065</Numerator><Numerator>0.058011</Numerator><Numerator>0.004849</Numerator><Numerator>-0.02696</Numerator><Numerator>-0.035651</Numerator><Numerator>-0.027749</Numerator><Numerator>-0.012705</Numerator><Numerator>0.00102</Numerator><Numerator>0.008507</Numerator><Numerator>0.009613</Numerator><Numerator>0.006626</Numerator><Numerator>0.002494</Numerator><Numerator>-0.000498</Numerator><Numerator>-0.001789</Numerator><Numerator>-0.001724</Numerator><Numerator>-0.001018</Numerator><Numerator>-0.000372</Numerator><Numerator>9.0E-6</Numerator><Numerator>0.000131</Numerator><Numerator>9.8E-5</Numerator><Numerator>4.9E-5</Numerator><Numerator>1.4E-5</Numerator></Coefficients><Decimation><InputSampleRate>800</InputSampleRate><Factor>4</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0.05</Frequency></StageGain></Stage><Stage number="11"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>-3.0E-6</Numerator><Numerator>-1.8E-5</Numerator><Numerator>-4.2E-5</Numerator><Numerator>-4.7E-5</Numerator><Numerator>2.0E-6</Numerator><Numerator>8.6E-5</Numerator><Numerator>0.00011</Numerator><Numerator>1.4E-5</Numerator><Numerator>-9.8E-5</Numerator><Numerator>-4.5E-5</Numerator><Numerator>0.000144</Numerator><Numerator>0.000182</Numerator><Numerator>-7.0E-5</Numerator><Numerator>-0.00028</Numerator><Numerator>-4.8E-5</Numerator><Numerator>0.000373</Numerator><Numerator>0.000286</Numerator><Numerator>-0.000343</Numerator><Numerator>-0.000563</Numerator><Numerator>0.00017</Numerator><Numerator>0.000842</Numerator><Numerator>0.000211</Numerator><Numerator>-0.000994</Numerator><Numerator>-0.000768</Numerator><Numerator>0.000911</Numerator><Numerator>0.001435</Numerator><Numerator>-0.000471</Numerator><Numerator>-0.002049</Numerator><Numerator>-0.000373</Numerator><Numerator>0.002406</Numerator><Numerator>0.001589</Numerator><Numerator>-0.002267</Numerator><Numerator>-0.003016</Numerator><Numerator>0.00143</Numerator><Numerator>0.004368</Numerator><Numerator>0.000214</Numerator><Numerator>-0.005256</Numerator><Numerator>-0.002608</Numerator><Numerator>0.005247</Numerator><Numerator>0.005495</Numerator><Numerator>-0.003947</Numerator><Numerator>-0.008397</Numerator><Numerator>0.0011</Numerator><Numerator>0.010648</Numerator><Numerator>0.003315</Numerator><Numerator>-0.011457</Numerator><Numerator>-0.009008</Numerator><Numerator>0.010013</Numerator><Numerator>0.015343</Numerator><Numerator>-0.005584</Numerator><Numerator>-0.021337</Numerator><Numerator>-0.002405</Numerator><Numerator>0.025672</Numerator><Numerator>0.014391</Numerator><Numerator>-0.02666</Numerator><Numerator>-0.030925</Numerator><Numerator>0.021901</Numerator><Numerator>0.053611</Numerator><Numerator>-0.006603</Numerator><Numerator>-0.089257</Numerator><Numerator>-0.036882</Numerator><Numerator>0.186535</Numerator><Numerator>0.403778</Numerator><Numerator>0.403778</Numerator><Numerator>0.186535</Numerator><Numerator>-0.036882</Numerator><Numerator>-0.089257</Numerator><Numerator>-0.006603</Numerator><Numerator>0.053611</Numerator><Numerator>0.021901</Numerator><Numerator>-0.030925</Numerator><Numerator>-0.02666</Numerator><Numerator>0.014391</Numerator><Numerator>0.025672</Numerator><Numerator>-0.002405</Numerator><Numerator>-0.021337</Numerator><Numerator>-0.005584</Numerator><Numerator>0.015343</Numerator><Numerator>0.010013</Numerator><Numerator>-0.009008</Numerator><Numerator>-0.011457</Numerator><Numerator>0.003315</Numerator><Numerator>0.010648</Numerator><Numerator>0.0011</Numerator><Numerator>-0.008397</Numerator><Numerator>-0.003947</Numerator><Numerator>0.005495</Numerator><Numerator>0.005247</Numerator><Numerator>-0.002608</Numerator><Numerator>-0.005256</Numerator><Numerator>0.000214</Numerator><Numerator>0.004368</Numerator><Numerator>0.00143</Numerator><Numerator>-0.003016</Numerator><Numerator>-0.002267</Numerator><Numerator>0.001589</Numerator><Numerator>0.002406</Numerator><Numerator>-0.000373</Numerator><Numerator>-0.002049</Numerator><Numerator>-0.000471</Numerator><Numerator>0.001435</Numerator><Numerator>0.000911</Numerator><Numerator>-0.000768</Numerator><Numerator>-0.000994</Numerator><Numerator>0.000211</Numerator><Numerator>0.000842</Numerator><Numerator>0.00017</Numerator><Numerator>-0.000563</Numerator><Numerator>-0.000343</Numerator><Numerator>0.000286</Numerator><Numerator>0.000373</Numerator><Numerator>-4.8E-5</Numerator><Numerator>-0.00028</Numerator><Numerator>-7.0E-5</Numerator><Numerator>0.000182</Numerator><Numerator>0.000144</Numerator><Numerator>-4.5E-5</Numerator><Numerator>-9.8E-5</Numerator><Numerator>1.4E-5</Numerator><Numerator>0.00011</Numerator><Numerator>8.6E-5</Numerator><Numerator>2.0E-6</Numerator><Numerator>-4.7E-5</Numerator><Numerator>-4.2E-5</Numerator><Numerator>-1.8E-5</Numerator><Numerator>-3.0E-6</Numerator></Coefficients><Decimation><InputSampleRate>200</InputSampleRate><Factor>2</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0.05</Frequency></StageGain></Stage></Response></Channel></Station></Network></FDSNStationXML>',"Response level selecting channel codes and epoch"),

("level=network&net=_MOST&format=xml&nodata=404",200,
'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.3</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?level=network&amp;net=_MOST&amp;format=xml&amp;nodata=404</ModuleURI><Created>2022-08-11T10:01:55.13Z</Created><Network code="IV" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Italian Seismic Network</Description><Identifier type="DOI">10.13127/SD/X0FXnH7QfY</Identifier><ingv:Identifier>N1</ingv:Identifier><TotalNumberStations>7</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations></Network><Network code="IX" startDate="2005-01-01T00:00:00" restrictedStatus="open"><Description>Irpinia Seismic Network, Italy</Description><ingv:Identifier>N41</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations></Network></FDSNStationXML>'
,"AlternateNetworks only net"),

("level=station&net=_MOST&format=xml&nodata=404",200,
'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.3</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?level=station&amp;net=_MOST&amp;format=xml&amp;nodata=404</ModuleURI><Created>2022-08-11T14:18:31.022Z</Created><Network code="IV" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Italian Seismic Network</Description><Identifier type="DOI">10.13127/SD/X0FXnH7QfY</Identifier><ingv:Identifier>N1</ingv:Identifier><TotalNumberStations>7</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="IMTC" startDate="1988-01-01T00:00:00" restrictedStatus="open"><ingv:AlternateNetworks><ingv:AlternateNetwork type="VIRTUAL" code="_MOST" startDate="2011-03-14T00:00:00"><Description>"Monitoring of Structures"</Description></ingv:AlternateNetwork></ingv:AlternateNetworks><ingv:Identifier>S3001</ingv:Identifier><Latitude>40.7209</Latitude><Longitude>13.8758</Longitude><Elevation>59</Elevation><Site><Name>Ischia - Monte Corvo</Name></Site><CreationDate>1988-01-01T00:00:00</CreationDate></Station></Network><Network code="IX" startDate="2005-01-01T00:00:00" restrictedStatus="open"><Description>Irpinia Seismic Network, Italy</Description><ingv:Identifier>N41</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="AND3" startDate="2013-12-17T00:00:00" restrictedStatus="open"><ingv:AlternateNetworks><ingv:AlternateNetwork type="VIRTUAL" code="_MOST" startDate="2011-03-14T00:00:00"><Description>"Monitoring of Structures"</Description></ingv:AlternateNetwork><ingv:AlternateNetwork type="VIRTUAL" code="_MOST-ICO" startDate="2011-03-14T00:00:00"><Description>"Monitoring of Structures in Central-Eastern Italy (Italia Centro Orientale)"</Description></ingv:AlternateNetwork><ingv:AlternateNetwork type="VIRTUAL" code="_NFOTABOO" startDate="2010-04-01T00:00:00"><Description>"The Altotiberina Near Fault Observatory (TABOO), Italy."</Description></ingv:AlternateNetwork></ingv:AlternateNetworks><ingv:Identifier>S6221</ingv:Identifier><Latitude>40.9298</Latitude><Longitude>15.3331</Longitude><Elevation>905</Elevation><Site><Name>Station Andretta, Italy</Name></Site><CreationDate>2013-12-17T00:00:00</CreationDate></Station></Network></FDSNStationXML>'
,"AlternateNetworks only net, level station"),



("level=station&format=xml&network=MN,_MOST&nodata=404&startbefore=2013-03-14T00:00:00",200,
'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.3</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?level=station&amp;format=xml&amp;network=MN,_MOST&amp;nodata=404&amp;startbefore=2013-03-14T00:00:00</ModuleURI><Created>2022-08-11T12:40:12.223Z</Created><Network code="IV" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Italian Seismic Network</Description><Identifier type="DOI">10.13127/SD/X0FXnH7QfY</Identifier><ingv:Identifier>N1</ingv:Identifier><TotalNumberStations>7</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="IMTC" startDate="1988-01-01T00:00:00" restrictedStatus="open"><ingv:AlternateNetworks><ingv:AlternateNetwork type="VIRTUAL" code="_MOST" startDate="2011-03-14T00:00:00"><Description>"Monitoring of Structures"</Description></ingv:AlternateNetwork></ingv:AlternateNetworks><ingv:Identifier>S3001</ingv:Identifier><Latitude>40.7209</Latitude><Longitude>13.8758</Longitude><Elevation>59</Elevation><Site><Name>Ischia - Monte Corvo</Name></Site><CreationDate>1988-01-01T00:00:00</CreationDate></Station></Network><Network code="MN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Mediterranean Very Broadband Seismographic Network</Description><Identifier type="DOI">10.13127/SD/fBBBtDtd6q</Identifier><ingv:Identifier>N22</ingv:Identifier><TotalNumberStations>2</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="AQU" startDate="1988-08-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S7</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Site><Name>L\'Aquila, Italy</Name></Site><CreationDate>1988-08-01T00:00:00</CreationDate></Station></Network></FDSNStationXML>',"AlternateNetworks and regular network with time limit"),

("level=station&format=xml&network=_MOST,_NFOTABOO,GU&nodata=404&startafter=1987-03-14T00:00:00",200,
'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.3</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?level=station&amp;format=xml&amp;network=_MOST,_NFOTABOO,GU&amp;nodata=404&amp;startafter=1987-03-14T00:00:00</ModuleURI><Created>2022-08-11T13:19:59.649Z</Created><Network code="IV" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Italian Seismic Network</Description><Identifier type="DOI">10.13127/SD/X0FXnH7QfY</Identifier><ingv:Identifier>N1</ingv:Identifier><TotalNumberStations>7</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="IMTC" startDate="1988-01-01T00:00:00" restrictedStatus="open"><ingv:AlternateNetworks><ingv:AlternateNetwork type="VIRTUAL" code="_MOST" startDate="2011-03-14T00:00:00"><Description>"Monitoring of Structures"</Description></ingv:AlternateNetwork></ingv:AlternateNetworks><ingv:Identifier>S3001</ingv:Identifier><Latitude>40.7209</Latitude><Longitude>13.8758</Longitude><Elevation>59</Elevation><Site><Name>Ischia - Monte Corvo</Name></Site><CreationDate>1988-01-01T00:00:00</CreationDate></Station></Network><Network code="IX" startDate="2005-01-01T00:00:00" restrictedStatus="open"><Description>Irpinia Seismic Network, Italy</Description><ingv:Identifier>N41</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="AND3" startDate="2013-12-17T00:00:00" restrictedStatus="open"><ingv:AlternateNetworks><ingv:AlternateNetwork type="VIRTUAL" code="_MOST" startDate="2011-03-14T00:00:00"><Description>"Monitoring of Structures"</Description></ingv:AlternateNetwork><ingv:AlternateNetwork type="VIRTUAL" code="_MOST-ICO" startDate="2011-03-14T00:00:00"><Description>"Monitoring of Structures in Central-Eastern Italy (Italia Centro Orientale)"</Description></ingv:AlternateNetwork><ingv:AlternateNetwork type="VIRTUAL" code="_NFOTABOO" startDate="2010-04-01T00:00:00"><Description>"The Altotiberina Near Fault Observatory (TABOO), Italy."</Description></ingv:AlternateNetwork></ingv:AlternateNetworks><ingv:Identifier>S6221</ingv:Identifier><Latitude>40.9298</Latitude><Longitude>15.3331</Longitude><Elevation>905</Elevation><Site><Name>Station Andretta, Italy</Name></Site><CreationDate>2013-12-17T00:00:00</CreationDate></Station></Network></FDSNStationXML>',"Two AlternateNetworks and missing regular network  with time limit"),

("nodata=404&format=xml&level=station&lat=42&lon=12&minradius=0&maxradiuskm=130",200,
'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.51.0</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?nodata=404&amp;format=xml&amp;level=station&amp;lat=42&amp;lon=12&amp;minradius=0&amp;maxradiuskm=130</ModuleURI><Created>2022-08-29T07:07:30.304Z</Created><Network code="IV" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Italian Seismic Network</Description><Identifier type="DOI">10.13127/SD/X0FXnH7QfY</Identifier><ingv:Identifier>N1</ingv:Identifier><TotalNumberStations>7</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="AQU" startDate="2003-03-01T00:00:00" endDate="2008-10-15T00:00:00" restrictedStatus="open"><ingv:Identifier>S7</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Site><Name>L\'Aquila, Italy</Name></Site><CreationDate>1988-08-01T00:00:00</CreationDate></Station></Network><Network code="MN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Mediterranean Very Broadband Seismographic Network</Description><Identifier type="DOI">10.13127/SD/fBBBtDtd6q</Identifier><ingv:Identifier>N22</ingv:Identifier><TotalNumberStations>2</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="AQU" startDate="1988-08-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S7</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Site><Name>L\'Aquila, Italy</Name></Site><CreationDate>1988-08-01T00:00:00</CreationDate></Station></Network></FDSNStationXML>',"Radius in km at Station level"),

("starttime=2004-01-06T15%3A55%3A02.658787&endtime=2010-02-05T15%3A55%3A02.658787&level=channel&format=xml&cha=*Z",200,
'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.51.0</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?starttime=2004-01-06T15%3A55%3A02.658787&amp;endtime=2010-02-05T15%3A55%3A02.658787&amp;level=channel&amp;format=xml&amp;cha=*Z</ModuleURI><Created>2022-09-02T14:58:11.972Z</Created><Network xmlns:css30="http://www.brtt.com/xml/station/css30" code="IT" startDate="1970-01-01T00:00:00" endDate="2599-12-31T23:59:59" css30:netType="-" restrictedStatus="open"><Description>Italian Strong Motion Network (RAN)</Description><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="CMA" startDate="2007-11-13T00:00:00" endDate="2599-12-31T23:59:59.999" css30:staType="-"><Latitude>39.414900</Latitude><Longitude>16.818000</Longitude><Elevation>610.000000</Elevation><Site><Name>Campana</Name></Site><Vault>-</Vault><CreationDate>2007-11-13T00:00:00</CreationDate><SelectedNumberChannels>1</SelectedNumberChannels><Channel xmlns:css30="http://www.brtt.com/xml/station/css30" code="HGZ" locationCode="" startDate="2007-11-13T00:00:00" endDate="2599-12-31T23:59:59.999" css30:chanType="-"><Comment><Value>cfx_5086 5086</Value></Comment><Latitude>39.414900</Latitude><Longitude>16.818000</Longitude><Elevation>610.000000</Elevation><Depth>0.000000</Depth><Azimuth>0.000000</Azimuth><Dip>-90.000000</Dip><SampleRate>200</SampleRate><CalibrationUnits><Name>A</Name></CalibrationUnits><Sensor css30:responseFrequencyBand="b"><Type>A</Type><Description>CFX_US4H 200 Hz 5 Volt per 5g/Edax Datalogger</Description><InstallationDate>2007-11-13T12:00:00.00000</InstallationDate><CalibrationDate>2007-11-13T12:00:00.00000</CalibrationDate></Sensor><Response><InstrumentSensitivity><Value>0.000106955</Value><Frequency>0.03</Frequency><InputUnits><Name>nm/s**2</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel></Station></Network><Network code="IV" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Italian Seismic Network</Description><Identifier type="DOI">10.13127/SD/X0FXnH7QfY</Identifier><ingv:Identifier>N1</ingv:Identifier><TotalNumberStations>7</TotalNumberStations><SelectedNumberStations>5</SelectedNumberStations><Station code="ACER" startDate="2007-07-05T12:00:00" restrictedStatus="open"><ingv:Identifier>S1</ingv:Identifier><Latitude>40.7867</Latitude><Longitude>15.9427</Longitude><Elevation>690</Elevation><Site><Name>Acerenza</Name></Site><CreationDate>2007-07-05T12:00:00</CreationDate><TotalNumberChannels>33</TotalNumberChannels><SelectedNumberChannels>5</SelectedNumberChannels><Channel code="BHZ" startDate="2007-07-05T12:00:00" endDate="2014-05-08T11:42:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C3</ingv:Identifier><Latitude>40.7867</Latitude><Longitude>15.9427</Longitude><Elevation>690</Elevation><Depth>1</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>1500000000</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2007-07-05T12:00:00" endDate="2014-05-08T11:42:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C6</ingv:Identifier><Latitude>40.7867</Latitude><Longitude>15.9427</Longitude><Elevation>690</Elevation><Depth>1</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>1500000000</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HNZ" startDate="2007-07-05T12:00:00" endDate="2011-06-24T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C9</ingv:Identifier><Latitude>40.7867</Latitude><Longitude>15.9427</Longitude><Elevation>690</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>200</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>KINEMETRICS EPISENSOR</Description></Sensor><Response><InstrumentSensitivity><Value>407880</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s**2</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="2007-07-05T12:00:00" endDate="2014-05-08T11:42:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C12</ingv:Identifier><Latitude>40.7867</Latitude><Longitude>15.9427</Longitude><Elevation>690</Elevation><Depth>1</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>1485900000</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="2007-07-05T12:00:00" endDate="2014-05-08T11:42:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C15</ingv:Identifier><Latitude>40.7867</Latitude><Longitude>15.9427</Longitude><Elevation>690</Elevation><Depth>1</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>3165200000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel></Station><Station code="AQU" startDate="2003-03-01T00:00:00" endDate="2008-10-15T00:00:00" restrictedStatus="open"><ingv:Identifier>S7</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Site><Name>L\'Aquila, Italy</Name></Site><CreationDate>1988-08-01T00:00:00</CreationDate><TotalNumberChannels>1</TotalNumberChannels><SelectedNumberChannels>1</SelectedNumberChannels><Channel code="SHZ" startDate="2003-03-01T00:00:00" endDate="2008-10-15T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C76</ingv:Identifier><Latitude>42.35388</Latitude><Longitude>13.40193</Longitude><Elevation>729</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>50</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>GEOTECH S-13</Description></Sensor><Response><InstrumentSensitivity><Value>582216000</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel></Station><Station code="ARVD" startDate="2003-03-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S9</ingv:Identifier><Latitude>43.49807</Latitude><Longitude>12.94153</Longitude><Elevation>461</Elevation><Site><Name>ARCEVIA 2</Name></Site><CreationDate>2003-03-01T00:00:00</CreationDate><TotalNumberChannels>33</TotalNumberChannels><SelectedNumberChannels>11</SelectedNumberChannels><Channel code="BHZ" startDate="2008-02-08T12:00:00" endDate="2008-02-26T10:03:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C100</ingv:Identifier><Latitude>43.49807</Latitude><Longitude>12.94153</Longitude><Elevation>461</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>50</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>1179650000</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="2008-02-26T10:03:00" endDate="2009-03-14T10:40:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C103</ingv:Identifier><Latitude>43.49807</Latitude><Longitude>12.94153</Longitude><Elevation>461</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>1179650000</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="2009-03-14T10:40:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C115</ingv:Identifier><Latitude>43.49807</Latitude><Longitude>12.94153</Longitude><Elevation>461</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>1179650000</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="EHZ" startDate="2003-03-01T00:00:00" endDate="2005-09-30T10:33:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C94</ingv:Identifier><Latitude>43.49807</Latitude><Longitude>12.94153</Longitude><Elevation>461</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>50</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>LENNARTZ LE3D-5S</Description></Sensor><Response><InstrumentSensitivity><Value>466034000</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="EHZ" startDate="2005-09-30T10:33:00" endDate="2008-02-08T12:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C97</ingv:Identifier><Latitude>43.49807</Latitude><Longitude>12.94153</Longitude><Elevation>461</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>50</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>LENNARTZ LE3D-5S</Description></Sensor><Response><InstrumentSensitivity><Value>466034000</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2008-02-26T10:03:00" endDate="2009-03-14T10:40:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C106</ingv:Identifier><Latitude>43.49807</Latitude><Longitude>12.94153</Longitude><Elevation>461</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>1179650000</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2009-03-14T10:40:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C118</ingv:Identifier><Latitude>43.49807</Latitude><Longitude>12.94153</Longitude><Elevation>461</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>1179650000</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="2008-02-26T10:03:00" endDate="2009-03-14T10:40:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C109</ingv:Identifier><Latitude>43.49807</Latitude><Longitude>12.94153</Longitude><Elevation>461</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>1179650000</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="2009-03-14T10:40:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C121</ingv:Identifier><Latitude>43.49807</Latitude><Longitude>12.94153</Longitude><Elevation>461</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>1179650000</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="2008-02-26T10:03:00" endDate="2009-03-14T10:40:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C112</ingv:Identifier><Latitude>43.49807</Latitude><Longitude>12.94153</Longitude><Elevation>461</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>2430000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="2009-03-14T10:40:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C124</ingv:Identifier><Latitude>43.49807</Latitude><Longitude>12.94153</Longitude><Elevation>461</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>2430000000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel></Station><Station code="IMTC" startDate="1988-01-01T00:00:00" restrictedStatus="open"><ingv:AlternateNetworks><ingv:AlternateNetwork type="VIRTUAL" code="_MOST" startDate="2011-03-14T00:00:00"><Description>"Monitoring of Structures"</Description></ingv:AlternateNetwork></ingv:AlternateNetworks><ingv:Identifier>S3001</ingv:Identifier><Latitude>40.7209</Latitude><Longitude>13.8758</Longitude><Elevation>59</Elevation><Site><Name>Ischia - Monte Corvo</Name></Site><CreationDate>1988-01-01T00:00:00</CreationDate><TotalNumberChannels>3</TotalNumberChannels><SelectedNumberChannels>1</SelectedNumberChannels><Channel code="HHZ" startDate="1988-01-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C34861</ingv:Identifier><Latitude>40.7209</Latitude><Longitude>13.8758</Longitude><Elevation>59</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><CalibrationUnits><Name>V</Name><Description>Volts</Description></CalibrationUnits><Sensor><Description>GURALP CMG-40T-60S</Description></Sensor><Response><InstrumentSensitivity><Value>243822000</Value><Frequency>1</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel></Station><Station code="VBKN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S3031</ingv:Identifier><Latitude>40.83</Latitude><Longitude>14.4299</Longitude><Elevation>951</Elevation><Site><Name>Vesuvio - Bunker Nord</Name></Site><CreationDate>1988-01-01T00:00:00</CreationDate><TotalNumberChannels>3</TotalNumberChannels><SelectedNumberChannels>1</SelectedNumberChannels><Channel code="HHZ" startDate="1988-01-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C34951</ingv:Identifier><Latitude>40.83</Latitude><Longitude>14.4299</Longitude><Elevation>951</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><CalibrationUnits><Name>V</Name><Description>Volts</Description></CalibrationUnits><Sensor><Description>GURALP CMG-40T-60S</Description></Sensor><Response><InstrumentSensitivity><Value>243822000</Value><Frequency>1</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel></Station></Network><Network code="MN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Mediterranean Very Broadband Seismographic Network</Description><Identifier type="DOI">10.13127/SD/fBBBtDtd6q</Identifier><ingv:Identifier>N22</ingv:Identifier><TotalNumberStations>2</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="AQU" startDate="1988-08-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S7</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Site><Name>L\'Aquila, Italy</Name></Site><CreationDate>1988-08-01T00:00:00</CreationDate><TotalNumberChannels>151</TotalNumberChannels><SelectedNumberChannels>11</SelectedNumberChannels><Channel code="BHZ" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2559</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>598652000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2574</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>778718000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2562</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>598652000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2577</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>778718000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HLZ" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2589</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>KINEMETRICS EPISENSOR</Description></Sensor><Response><InstrumentSensitivity><Value>537691</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s**2</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2565</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>598652000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2580</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>778718000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHZ" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2568</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>2394610000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="UHZ" startDate="2008-02-19T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2583</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.01</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>3114870000</Value><Frequency>0.003</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="2002-06-05T12:00:01" endDate="2008-02-18T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C2571</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>2394610000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="2008-02-19T00:00:00" endDate="2011-04-13T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C2586</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>15</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.02</ClockDrift><CalibrationUnits><Name>A</Name><Description>Ampere</Description></CalibrationUnits><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>3114870000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel></Station></Network><Network code="NI" startDate="2002-01-01T00:00:00" restrictedStatus="open"><Description>North-East Italy Broadband Network</Description><ingv:Identifier>N13</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="ACOM" startDate="2005-02-01T12:00:00" endDate="2015-12-31T23:59:59" restrictedStatus="open"><ingv:Identifier>S3451</ingv:Identifier><Latitude>46.548</Latitude><Longitude>13.5137</Longitude><Elevation>1788</Elevation><Site><Name>Acomizza</Name></Site><CreationDate>2005-02-01T12:00:00</CreationDate><TotalNumberChannels>24</TotalNumberChannels><SelectedNumberChannels>8</SelectedNumberChannels><Channel code="BHZ" startDate="2005-02-01T12:00:00" endDate="2008-10-20T16:00:01" restrictedStatus="open" locationCode=""><ingv:Identifier>C39941</ingv:Identifier><Latitude>46.548</Latitude><Longitude>13.5137</Longitude><Elevation>1788</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>626646000</Value><Frequency>5</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="2008-10-20T16:00:01" endDate="2008-10-20T16:00:02" restrictedStatus="open" locationCode=""><ingv:Identifier>C40001</ingv:Identifier><Latitude>46.548</Latitude><Longitude>13.5137</Longitude><Elevation>1788</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>629221000</Value><Frequency>0.3</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHZ" startDate="2008-10-20T16:00:03" endDate="2015-12-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C40061</ingv:Identifier><Latitude>46.548</Latitude><Longitude>13.5137</Longitude><Elevation>1788</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>650175000</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2005-02-01T12:00:00" endDate="2008-10-20T16:00:01" restrictedStatus="open" locationCode=""><ingv:Identifier>C39971</ingv:Identifier><Latitude>46.548</Latitude><Longitude>13.5137</Longitude><Elevation>1788</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>624217000</Value><Frequency>7</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2008-10-20T16:00:01" endDate="2008-10-20T16:00:02" restrictedStatus="open" locationCode=""><ingv:Identifier>C40031</ingv:Identifier><Latitude>46.548</Latitude><Longitude>13.5137</Longitude><Elevation>1788</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>629436000</Value><Frequency>0.6</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2008-10-20T16:00:03" endDate="2015-12-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C40091</ingv:Identifier><Latitude>46.548</Latitude><Longitude>13.5137</Longitude><Elevation>1788</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>650175000</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="2008-10-20T16:00:03" endDate="2015-12-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C40121</ingv:Identifier><Latitude>46.548</Latitude><Longitude>13.5137</Longitude><Elevation>1788</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>650175000</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="2008-10-20T16:00:03" endDate="2015-12-31T23:59:59" restrictedStatus="open" locationCode=""><ingv:Identifier>C40151</ingv:Identifier><Latitude>46.548</Latitude><Longitude>13.5137</Longitude><Elevation>1788</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>NANOMETRICS TRILLIUM-40S</Description></Sensor><Response><InstrumentSensitivity><Value>650175000</Value><Frequency>0.2</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel></Station></Network><Network code="SI" startDate="2006-01-01T00:00:00" restrictedStatus="open"><Description>Sudtirol Network, Italy</Description><Identifier type="citation">Pintore et al. Multiple Identifier</Identifier><Identifier type="DOI">https://doi.org/10.7914/SN/3T_2020</Identifier><ingv:Identifier>N18</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="ABSI" startDate="2006-11-21T14:16:45" restrictedStatus="open"><ingv:Identifier>S122</ingv:Identifier><Latitude>46.7285</Latitude><Longitude>11.3205</Longitude><Elevation>1801</Elevation><Site><Name>Aberstuckl (Sarntal)</Name></Site><CreationDate>2006-11-21T14:16:45</CreationDate><TotalNumberChannels>12</TotalNumberChannels><SelectedNumberChannels>4</SelectedNumberChannels><Channel code="BHZ" startDate="2006-11-21T14:16:45" restrictedStatus="open" locationCode=""><ingv:Identifier>C1335</ingv:Identifier><Latitude>46.7285</Latitude><Longitude>11.3205</Longitude><Elevation>1801</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>20</SampleRate><ClockDrift>0.0001</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>627604000</Value><Frequency>0.4</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2006-11-21T14:16:45" restrictedStatus="open" locationCode=""><ingv:Identifier>C1338</ingv:Identifier><Latitude>46.7285</Latitude><Longitude>11.3205</Longitude><Elevation>1801</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><ClockDrift>0.0001</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>627604000</Value><Frequency>0.4</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="LHZ" startDate="2006-11-21T14:16:45" restrictedStatus="open" locationCode=""><ingv:Identifier>C1341</ingv:Identifier><Latitude>46.7285</Latitude><Longitude>11.3205</Longitude><Elevation>1801</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><ClockDrift>0.0001</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>627604000</Value><Frequency>0.4</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="VHZ" startDate="2006-11-21T14:16:45" restrictedStatus="open" locationCode=""><ingv:Identifier>C1344</ingv:Identifier><Latitude>46.7285</Latitude><Longitude>11.3205</Longitude><Elevation>1801</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>0.1</SampleRate><ClockDrift>0.0001</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>2510420000</Value><Frequency>0.4</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel></Station></Network><Network code="Z3" startDate="2005-06-05T00:00:00" endDate="2007-04-30T00:00:00" restrictedStatus="open"><Description>Egelados project, RUB Bochum, Germany</Description><Identifier type="DOI">10.14470/M87550267382</Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="AT04" startDate="2005-11-02T00:00:00" endDate="2007-02-23T00:00:00" restrictedStatus="open"><Latitude>37.7252</Latitude><Longitude>24.0496</Longitude><Elevation>23</Elevation><Site><Name>Station Egelados Network, Greece</Name><Country>Greece</Country></Site><CreationDate>2005-11-02T00:00:00</CreationDate><SelectedNumberChannels>2</SelectedNumberChannels><Channel code="LHZ" startDate="2005-11-02T00:00:00" endDate="2007-02-23T00:00:00" restrictedStatus="open" locationCode=""><Latitude>37.7252</Latitude><Longitude>24.0496</Longitude><Elevation>23</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>1</SampleRate><SampleRateRatio><NumberSamples>1</NumberSamples><NumberSeconds>1</NumberSeconds></SampleRateRatio><ClockDrift>0</ClockDrift><Sensor resourceId="Sensor/20180508113316.019358.6"><Type>BB</Type><Description>GFZ:Z32005:CMG-3ESP/60/g=2000</Description><Manufacturer>Guralp</Manufacturer><Model>CMG-3ESP/60</Model><SerialNumber>C018</SerialNumber></Sensor><DataLogger resourceId="Datalogger/20180508113316.020501.8"><Type>EarthData PS6-SC</Type><Description>GFZ:Z32005:PS6-Log/g=1000000</Description><Manufacturer>EarthData</Manufacturer><Model>PS6-SC</Model><SerialNumber>3305</SerialNumber></DataLogger><Response><InstrumentSensitivity><Value>2000000000</Value><Frequency>0.1</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="HHZ" startDate="2005-11-02T00:00:00" endDate="2007-02-23T00:00:00" restrictedStatus="open" locationCode=""><Latitude>37.7252</Latitude><Longitude>24.0496</Longitude><Elevation>23</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>-90</Dip><SampleRate>100</SampleRate><SampleRateRatio><NumberSamples>100</NumberSamples><NumberSeconds>1</NumberSeconds></SampleRateRatio><ClockDrift>0</ClockDrift><Sensor resourceId="Sensor/20180508113316.019358.6"><Type>BB</Type><Description>GFZ:Z32005:CMG-3ESP/60/g=2000</Description><Manufacturer>Guralp</Manufacturer><Model>CMG-3ESP/60</Model><SerialNumber>C018</SerialNumber></Sensor><DataLogger resourceId="Datalogger/20180508113316.020501.8"><Type>EarthData PS6-SC</Type><Description>GFZ:Z32005:PS6-Log/g=1000000</Description><Manufacturer>EarthData</Manufacturer><Model>PS6-SC</Model><SerialNumber>3305</SerialNumber></DataLogger><Response><InstrumentSensitivity><Value>2000000000</Value><Frequency>0.1</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel></Station></Network></FDSNStationXML>',"Many stations for network , Channel level TODO fix TotalnumberChannels/SelectedNumberChannels when lacking in input"),



("nodata=404&format=xml&level=network&lat=42&lon=12&minradius=0&maxradiuskm=130",200,
'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.51.0</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?nodata=404&amp;format=xml&amp;level=network&amp;lat=42&amp;lon=12&amp;minradius=0&amp;maxradiuskm=130</ModuleURI><Created>2022-08-29T06:44:18.815Z</Created><Network code="IV" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Italian Seismic Network</Description><Identifier type="DOI">10.13127/SD/X0FXnH7QfY</Identifier><ingv:Identifier>N1</ingv:Identifier><TotalNumberStations>7</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations></Network><Network code="MN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Mediterranean Very Broadband Seismographic Network</Description><Identifier type="DOI">10.13127/SD/fBBBtDtd6q</Identifier><ingv:Identifier>N22</ingv:Identifier><TotalNumberStations>2</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations></Network></FDSNStationXML>',"Radius in km at Network level"),


("format=xml&net=TH&includerestricted=false&level=station",200,
'<?xml version="1.0" encoding="UTF-8"?><FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.60</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?format=xml&amp;net=TH&amp;includerestricted=false&amp;level=station</ModuleURI><Created>2024-04-02T12:20:08.479</Created><Network code="TH" startDate="1980-01-01T00:00:00" sourceID="http://test.exist.fdsn.station/xml/station/1234" restrictedStatus="partial" alternateCode="Test alternate code" historicalCode="Test historical code"><Description>Thuringia Seismic Network, Uni Jena</Description><Identifier type="DOI">10.7914/SN/TH</Identifier><TotalNumberStations>4</TotalNumberStations><SelectedNumberStations>3</SelectedNumberStations><Station code="ABG1" startDate="2011-10-18T16:00:00" endDate="2012-11-22T12:00:00" restrictedStatus="open"><Latitude>50.96532</Latitude><Longitude>12.57208</Longitude><Elevation>203</Elevation><Site><Name>UJENA Station Forsthaus Leinawald, Germany</Name><Country>Germany</Country></Site><CreationDate>2011-10-18T16:00:00</CreationDate></Station><Station code="ANNA" startDate="2014-03-25T10:00:00" endDate="2017-12-04T00:00:00" restrictedStatus="open"><Latitude>50.88399</Latitude><Longitude>12.64365</Longitude><Elevation>249</Elevation><Site><Name>UJENA Station St. Anna Fundgrube, Germany</Name><Country>Germany</Country></Site><CreationDate>2014-03-25T10:00:00Z</CreationDate></Station><Station code="ANNA" startDate="2017-12-04T00:00:00" restrictedStatus="open"><Latitude>50.88902</Latitude><Longitude>12.64499</Longitude><Elevation>235</Elevation><Site><Name>UJENA Station St. Anna Fundgrube, Germany</Name><Country>Germany</Country></Site><CreationDate>2017-12-04T00:00:00Z</CreationDate></Station></Network></FDSNStationXML>'
,"Partially open network, returns and counts only restricted stations"),

("level=station&sta=CMA",200,
'<FDSNStationXML xmlns="http://www.fdsn.org/xml/station/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?level=station&amp;sta=CMA</ModuleURI><Network xmlns:css30="http://www.brtt.com/xml/station/css30" code="IT" startDate="1970-01-01T00:00:00" endDate="2599-12-31T23:59:59" css30:netType="-" restrictedStatus="open"><Description>Italian Strong Motion Network (RAN)</Description><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="CMA" startDate="2007-11-13T00:00:00" endDate="2599-12-31T23:59:59.999" css30:staType="-"><Latitude>39.414900</Latitude><Longitude>16.818000</Longitude><Elevation>610.000000</Elevation><Site><Name>Campana</Name></Site><Vault>-</Vault><CreationDate>2007-11-13T00:00:00</CreationDate></Station></Network></FDSNStationXML>',"Network with namespace extension"),


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
"level=channel&net=IV&station=AQU&format=text&nodata=404",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
IV|AQU||SHZ|42.35388|13.40193|729|0|0|-90|GEOTECH S-13|582216000|0.2|m/s|50|2003-03-01T00:00:00|2008-10-15T00:00:00\n","One station belong to two networks"),

(
"level=channel&net=IV&station=AQU&format=text&nodata=404&matchtimeseries=false&includeavailability=false",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
IV|AQU||SHZ|42.35388|13.40193|729|0|0|-90|GEOTECH S-13|582216000|0.2|m/s|50|2003-03-01T00:00:00|2008-10-15T00:00:00\n","matchtimeseries includeavailability ignored for default false"),

(
"level=channel&net=IV&station=AQU&format=text&nodata=404&includeavailability=false",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
IV|AQU||SHZ|42.35388|13.40193|729|0|0|-90|GEOTECH S-13|582216000|0.2|m/s|50|2003-03-01T00:00:00|2008-10-15T00:00:00\n","includeavailability ignored for default false"),

(
"level=channel&net=IV&station=AQU&format=text&nodata=404&matchtimeseries=false",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
IV|AQU||SHZ|42.35388|13.40193|729|0|0|-90|GEOTECH S-13|582216000|0.2|m/s|50|2003-03-01T00:00:00|2008-10-15T00:00:00\n","matchtimeseries ignored for default false"),

(
"level=channel&net=MN&format=text&nodata=404",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-5250000000|0.02|m/s|20|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-1046640000|0.02|m/s|20|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1047020000|0.02|m/s|20|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1075730000|0.02|m/s|20|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-1063680000|0.02|m/s|20|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1063680000|0.02|m/s|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|983662000|0.02|m/s|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|m/s|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|m/s|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780000000|0.02|m/s|20|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||BHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|20|2019-03-01T00:00:00|\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-5250000000|0.02|m/s|20|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-1055040000|0.02|m/s|20|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1049580000|0.02|m/s|20|1995-08-28T00:00:00|1996-09-05T23:59:59\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1059600000|0.02|m/s|20|1996-09-06T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1091140000|0.02|m/s|20|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-1092770000|0.02|m/s|20|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1092770000|0.02|m/s|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1014990000|0.02|m/s|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|m/s|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|m/s|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|780000000|0.02|m/s|20|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||BHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|20|2019-03-01T00:00:00|\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-5250000000|0.02|m/s|20|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-1054200000|0.02|m/s|20|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1062530000|0.02|m/s|20|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1044970000|0.02|m/s|20|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-1069590000|0.02|m/s|20|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1069590000|0.02|m/s|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1001740000|0.02|m/s|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|m/s|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|m/s|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|780000000|0.02|m/s|20|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||BHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|m/s|20|2019-03-01T00:00:00|\n\
MN|AQU||HHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|m/s|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|m/s|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780000000|0.02|m/s|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|100|2019-03-01T00:00:00|\n\
MN|AQU||HHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|m/s|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|m/s|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|780000000|0.02|m/s|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|100|2019-03-01T00:00:00|\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|m/s|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|m/s|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|780000000|0.02|m/s|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|m/s|100|2019-03-01T00:00:00|\n\
MN|AQU||HLE|42.354|13.405|710|15|90|0|KINEMETRICS EPISENSOR|534331|0.02|m/s**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLE|42.354|13.405|710|15|90|0|KINEMETRICS EPISENSOR|530244|0.2|m/s**2|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HLN|42.354|13.405|710|15|0|0|KINEMETRICS EPISENSOR|537500|0.02|m/s**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLN|42.354|13.405|710|15|0|0|KINEMETRICS EPISENSOR|530244|0.2|m/s**2|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HLZ|42.354|13.405|710|15|0|-90|KINEMETRICS EPISENSOR|537691|0.02|m/s**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLZ|42.354|13.405|710|15|0|-90|KINEMETRICS EPISENSOR|530244|0.2|m/s**2|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HNE|42.354|13.405|710|0|90|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|m/s**2|100|2019-03-01T00:00:00|\n\
MN|AQU||HNN|42.354|13.405|710|0|0|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|m/s**2|100|2019-03-01T00:00:00|\n\
MN|AQU||HNZ|42.354|13.405|710|0|0|-90|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|m/s**2|100|2019-03-01T00:00:00|\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-21000000000|0.02|m/s|1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-4186560000|0.02|m/s|1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1047020000|0.02|m/s|1|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1075730000|0.02|m/s|1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-1063680000|0.02|m/s|1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1063680000|0.02|m/s|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|983662000|0.02|m/s|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|m/s|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|m/s|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780000000|0.02|m/s|1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||LHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-21000000000|0.02|m/s|1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-4220160000|0.02|m/s|1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1049580000|0.02|m/s|1|1995-08-28T00:00:00|1996-09-05T23:59:59\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1059600000|0.02|m/s|1|1996-09-06T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1091140000|0.02|m/s|1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-1092770000|0.02|m/s|1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1092770000|0.02|m/s|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1014990000|0.02|m/s|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|m/s|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|m/s|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|780000000|0.02|m/s|1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||LHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-21000000000|0.02|m/s|1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-4216800000|0.02|m/s|1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1062530000|0.02|m/s|1|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1044970000|0.02|m/s|1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-1069590000|0.02|m/s|1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1069590000|0.02|m/s|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1001740000|0.02|m/s|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|m/s|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|m/s|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|780000000|0.02|m/s|1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||LHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-84000000000|0.003|m/s|0.01|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-16746200000|0.003|m/s|0.01|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4188090000|0.003|m/s|0.01|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4302930000|0.003|m/s|0.01|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-4254720000|0.003|m/s|0.01|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4254720000|0.003|m/s|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|3934650000|0.003|m/s|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|2368370000|0.003|m/s|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3121070000|0.003|m/s|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-84000000000|0.003|m/s|0.01|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-16880600000|0.003|m/s|0.01|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4198310000|0.003|m/s|0.01|1995-08-28T00:00:00|1996-09-05T23:59:59\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4238420000|0.003|m/s|0.01|1996-09-06T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4364570000|0.003|m/s|0.01|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-4371080000|0.003|m/s|0.01|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4371080000|0.003|m/s|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4059940000|0.003|m/s|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|2401390000|0.003|m/s|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3115290000|0.003|m/s|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-84000000000|0.003|m/s|0.01|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-16867200000|0.003|m/s|0.01|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4250120000|0.003|m/s|0.01|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4179890000|0.003|m/s|0.01|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-4278370000|0.003|m/s|0.01|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4278370000|0.003|m/s|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4006970000|0.003|m/s|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|2394610000|0.003|m/s|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.003|m/s|0.01|2008-02-19T00:00:00|\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-84000000000|0.02|m/s|0.1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-16746200000|0.02|m/s|0.1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4188090000|0.02|m/s|0.1|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4302930000|0.02|m/s|0.1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-4254720000|0.02|m/s|0.1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4254720000|0.02|m/s|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|3934650000|0.02|m/s|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|2368370000|0.02|m/s|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3121070000|0.02|m/s|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3120000000|0.02|m/s|0.1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||VHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-84000000000|0.02|m/s|0.1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-16880600000|0.02|m/s|0.1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4198310000|0.02|m/s|0.1|1995-08-28T00:00:00|1996-09-05T23:59:59\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4238420000|0.02|m/s|0.1|1996-09-06T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4364570000|0.02|m/s|0.1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-4371080000|0.02|m/s|0.1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4371080000|0.02|m/s|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4059940000|0.02|m/s|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|2401390000|0.02|m/s|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3115290000|0.02|m/s|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3120000000|0.02|m/s|0.1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||VHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-84000000000|0.02|m/s|0.1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-16867200000|0.02|m/s|0.1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4250120000|0.02|m/s|0.1|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4179890000|0.02|m/s|0.1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-4278370000|0.02|m/s|0.1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4278370000|0.02|m/s|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4006970000|0.02|m/s|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|2394610000|0.02|m/s|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.02|m/s|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3120000000|0.02|m/s|0.1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||VHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|ARPR||BHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|20|2014-01-23T00:00:00|\n\
MN|ARPR||BHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|20|2014-01-23T00:00:00|\n\
MN|ARPR||BHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|20|2014-01-23T00:00:00|\n\
MN|ARPR||LHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|1|2014-01-23T00:00:00|\n\
MN|ARPR||LHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|1|2014-01-23T00:00:00|\n\
MN|ARPR||LHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|1|2014-01-23T00:00:00|\n\
MN|ARPR||VHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|10066300000|0.02|m/s|0.1|2014-01-23T00:00:00|\n\
MN|ARPR||VHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|10066300000|0.02|m/s|0.1|2014-01-23T00:00:00|\n\
MN|ARPR||VHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|10066300000|0.02|m/s|0.1|2014-01-23T00:00:00|\n"
,""),

(
"level=channel&starttime=2000-01-01T00:00:00.0&endtime=2020-01-02&net=MN&format=text&nodata=404",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1063680000|0.02|m/s|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|983662000|0.02|m/s|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|m/s|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|m/s|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780000000|0.02|m/s|20|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||BHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|20|2019-03-01T00:00:00|\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1092770000|0.02|m/s|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1014990000|0.02|m/s|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|m/s|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|m/s|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|780000000|0.02|m/s|20|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||BHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|20|2019-03-01T00:00:00|\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1069590000|0.02|m/s|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1001740000|0.02|m/s|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|m/s|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|m/s|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|780000000|0.02|m/s|20|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||BHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|m/s|20|2019-03-01T00:00:00|\n\
MN|AQU||HHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|m/s|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|m/s|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780000000|0.02|m/s|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|100|2019-03-01T00:00:00|\n\
MN|AQU||HHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|m/s|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|m/s|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|780000000|0.02|m/s|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|100|2019-03-01T00:00:00|\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|m/s|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|m/s|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|780000000|0.02|m/s|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|m/s|100|2019-03-01T00:00:00|\n\
MN|AQU||HLE|42.354|13.405|710|15|90|0|KINEMETRICS EPISENSOR|534331|0.02|m/s**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLE|42.354|13.405|710|15|90|0|KINEMETRICS EPISENSOR|530244|0.2|m/s**2|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HLN|42.354|13.405|710|15|0|0|KINEMETRICS EPISENSOR|537500|0.02|m/s**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLN|42.354|13.405|710|15|0|0|KINEMETRICS EPISENSOR|530244|0.2|m/s**2|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HLZ|42.354|13.405|710|15|0|-90|KINEMETRICS EPISENSOR|537691|0.02|m/s**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLZ|42.354|13.405|710|15|0|-90|KINEMETRICS EPISENSOR|530244|0.2|m/s**2|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HNE|42.354|13.405|710|0|90|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|m/s**2|100|2019-03-01T00:00:00|\n\
MN|AQU||HNN|42.354|13.405|710|0|0|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|m/s**2|100|2019-03-01T00:00:00|\n\
MN|AQU||HNZ|42.354|13.405|710|0|0|-90|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|m/s**2|100|2019-03-01T00:00:00|\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1063680000|0.02|m/s|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|983662000|0.02|m/s|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|m/s|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|m/s|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780000000|0.02|m/s|1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||LHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1092770000|0.02|m/s|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1014990000|0.02|m/s|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|m/s|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|m/s|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|780000000|0.02|m/s|1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||LHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1069590000|0.02|m/s|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1001740000|0.02|m/s|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|m/s|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|m/s|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|780000000|0.02|m/s|1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||LHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4254720000|0.003|m/s|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|3934650000|0.003|m/s|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|2368370000|0.003|m/s|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3121070000|0.003|m/s|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4371080000|0.003|m/s|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4059940000|0.003|m/s|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|2401390000|0.003|m/s|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3115290000|0.003|m/s|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4278370000|0.003|m/s|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4006970000|0.003|m/s|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|2394610000|0.003|m/s|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.003|m/s|0.01|2008-02-19T00:00:00|\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4254720000|0.02|m/s|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|3934650000|0.02|m/s|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|2368370000|0.02|m/s|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3121070000|0.02|m/s|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3120000000|0.02|m/s|0.1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||VHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4371080000|0.02|m/s|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4059940000|0.02|m/s|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|2401390000|0.02|m/s|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3115290000|0.02|m/s|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3120000000|0.02|m/s|0.1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||VHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4278370000|0.02|m/s|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4006970000|0.02|m/s|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|2394610000|0.02|m/s|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.02|m/s|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3120000000|0.02|m/s|0.1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||VHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|ARPR||BHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|20|2014-01-23T00:00:00|\n\
MN|ARPR||BHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|20|2014-01-23T00:00:00|\n\
MN|ARPR||BHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|20|2014-01-23T00:00:00|\n\
MN|ARPR||LHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|1|2014-01-23T00:00:00|\n\
MN|ARPR||LHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|1|2014-01-23T00:00:00|\n\
MN|ARPR||LHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|1|2014-01-23T00:00:00|\n\
MN|ARPR||VHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|10066300000|0.02|m/s|0.1|2014-01-23T00:00:00|\n\
MN|ARPR||VHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|10066300000|0.02|m/s|0.1|2014-01-23T00:00:00|\n\
MN|ARPR||VHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|10066300000|0.02|m/s|0.1|2014-01-23T00:00:00|\n\
",""),

(
"level=channel&starttime=2000-01-01T00:00:00.0&endtime=2010-01-02&net=MN&format=text&minlat=41.0&maxlat=43.0&nodata=404",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1063680000|0.02|m/s|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|983662000|0.02|m/s|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|m/s|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|m/s|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1092770000|0.02|m/s|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1014990000|0.02|m/s|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|m/s|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|m/s|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1069590000|0.02|m/s|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1001740000|0.02|m/s|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|m/s|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|m/s|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|m/s|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|m/s|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|m/s|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|m/s|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|m/s|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|m/s|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLE|42.354|13.405|710|15|90|0|KINEMETRICS EPISENSOR|534331|0.02|m/s**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLN|42.354|13.405|710|15|0|0|KINEMETRICS EPISENSOR|537500|0.02|m/s**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLZ|42.354|13.405|710|15|0|-90|KINEMETRICS EPISENSOR|537691|0.02|m/s**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1063680000|0.02|m/s|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|983662000|0.02|m/s|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|m/s|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|m/s|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1092770000|0.02|m/s|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1014990000|0.02|m/s|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|m/s|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|m/s|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1069590000|0.02|m/s|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1001740000|0.02|m/s|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|m/s|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|m/s|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4254720000|0.003|m/s|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|3934650000|0.003|m/s|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|2368370000|0.003|m/s|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3121070000|0.003|m/s|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4371080000|0.003|m/s|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4059940000|0.003|m/s|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|2401390000|0.003|m/s|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3115290000|0.003|m/s|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4278370000|0.003|m/s|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4006970000|0.003|m/s|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|2394610000|0.003|m/s|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.003|m/s|0.01|2008-02-19T00:00:00|\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4254720000|0.02|m/s|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|3934650000|0.02|m/s|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|2368370000|0.02|m/s|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3121070000|0.02|m/s|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4371080000|0.02|m/s|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4059940000|0.02|m/s|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|2401390000|0.02|m/s|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3115290000|0.02|m/s|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4278370000|0.02|m/s|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4006970000|0.02|m/s|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|2394610000|0.02|m/s|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.02|m/s|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
",""),


(
"level=channel&net=MN&format=text&nodata=404&minlat=41&maxlatitude=45",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-5250000000|0.02|m/s|20|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-1046640000|0.02|m/s|20|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1047020000|0.02|m/s|20|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1075730000|0.02|m/s|20|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-1063680000|0.02|m/s|20|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1063680000|0.02|m/s|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|983662000|0.02|m/s|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|m/s|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|m/s|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780000000|0.02|m/s|20|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||BHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|20|2019-03-01T00:00:00|\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-5250000000|0.02|m/s|20|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-1055040000|0.02|m/s|20|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1049580000|0.02|m/s|20|1995-08-28T00:00:00|1996-09-05T23:59:59\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1059600000|0.02|m/s|20|1996-09-06T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1091140000|0.02|m/s|20|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-1092770000|0.02|m/s|20|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1092770000|0.02|m/s|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1014990000|0.02|m/s|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|m/s|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|m/s|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|780000000|0.02|m/s|20|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||BHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|20|2019-03-01T00:00:00|\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-5250000000|0.02|m/s|20|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-1054200000|0.02|m/s|20|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1062530000|0.02|m/s|20|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1044970000|0.02|m/s|20|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-1069590000|0.02|m/s|20|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1069590000|0.02|m/s|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1001740000|0.02|m/s|20|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|m/s|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|m/s|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|780000000|0.02|m/s|20|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||BHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|m/s|20|2019-03-01T00:00:00|\n\
MN|AQU||HHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|m/s|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|m/s|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780000000|0.02|m/s|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|100|2019-03-01T00:00:00|\n\
MN|AQU||HHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|m/s|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|m/s|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|780000000|0.02|m/s|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|100|2019-03-01T00:00:00|\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|m/s|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|m/s|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|780000000|0.02|m/s|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|m/s|100|2019-03-01T00:00:00|\n\
MN|AQU||HLE|42.354|13.405|710|15|90|0|KINEMETRICS EPISENSOR|534331|0.02|m/s**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLE|42.354|13.405|710|15|90|0|KINEMETRICS EPISENSOR|530244|0.2|m/s**2|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HLN|42.354|13.405|710|15|0|0|KINEMETRICS EPISENSOR|537500|0.02|m/s**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLN|42.354|13.405|710|15|0|0|KINEMETRICS EPISENSOR|530244|0.2|m/s**2|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HLZ|42.354|13.405|710|15|0|-90|KINEMETRICS EPISENSOR|537691|0.02|m/s**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLZ|42.354|13.405|710|15|0|-90|KINEMETRICS EPISENSOR|530244|0.2|m/s**2|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HNE|42.354|13.405|710|0|90|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|m/s**2|100|2019-03-01T00:00:00|\n\
MN|AQU||HNN|42.354|13.405|710|0|0|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|m/s**2|100|2019-03-01T00:00:00|\n\
MN|AQU||HNZ|42.354|13.405|710|0|0|-90|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|m/s**2|100|2019-03-01T00:00:00|\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-21000000000|0.02|m/s|1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-4186560000|0.02|m/s|1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1047020000|0.02|m/s|1|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1075730000|0.02|m/s|1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-1063680000|0.02|m/s|1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1063680000|0.02|m/s|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|983662000|0.02|m/s|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|592092000|0.02|m/s|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780269000|0.02|m/s|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|780000000|0.02|m/s|1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||LHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-21000000000|0.02|m/s|1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-4220160000|0.02|m/s|1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1049580000|0.02|m/s|1|1995-08-28T00:00:00|1996-09-05T23:59:59\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1059600000|0.02|m/s|1|1996-09-06T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1091140000|0.02|m/s|1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-1092770000|0.02|m/s|1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1092770000|0.02|m/s|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1014990000|0.02|m/s|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|600347000|0.02|m/s|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|778823000|0.02|m/s|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|780000000|0.02|m/s|1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||LHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-21000000000|0.02|m/s|1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-4216800000|0.02|m/s|1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1062530000|0.02|m/s|1|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1044970000|0.02|m/s|1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-1069590000|0.02|m/s|1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1069590000|0.02|m/s|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1001740000|0.02|m/s|1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|m/s|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|m/s|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|780000000|0.02|m/s|1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||LHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-84000000000|0.003|m/s|0.01|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-16746200000|0.003|m/s|0.01|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4188090000|0.003|m/s|0.01|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4302930000|0.003|m/s|0.01|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-4254720000|0.003|m/s|0.01|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4254720000|0.003|m/s|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|3934650000|0.003|m/s|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|2368370000|0.003|m/s|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3121070000|0.003|m/s|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-84000000000|0.003|m/s|0.01|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-16880600000|0.003|m/s|0.01|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4198310000|0.003|m/s|0.01|1995-08-28T00:00:00|1996-09-05T23:59:59\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4238420000|0.003|m/s|0.01|1996-09-06T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4364570000|0.003|m/s|0.01|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-4371080000|0.003|m/s|0.01|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4371080000|0.003|m/s|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4059940000|0.003|m/s|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|2401390000|0.003|m/s|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3115290000|0.003|m/s|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-84000000000|0.003|m/s|0.01|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-16867200000|0.003|m/s|0.01|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4250120000|0.003|m/s|0.01|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4179890000|0.003|m/s|0.01|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-4278370000|0.003|m/s|0.01|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4278370000|0.003|m/s|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4006970000|0.003|m/s|0.01|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|2394610000|0.003|m/s|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.003|m/s|0.01|2008-02-19T00:00:00|\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-84000000000|0.02|m/s|0.1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-16746200000|0.02|m/s|0.1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4188090000|0.02|m/s|0.1|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4302930000|0.02|m/s|0.1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-4254720000|0.02|m/s|0.1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4254720000|0.02|m/s|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|3934650000|0.02|m/s|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|2368370000|0.02|m/s|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3121070000|0.02|m/s|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3120000000|0.02|m/s|0.1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||VHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-84000000000|0.02|m/s|0.1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-16880600000|0.02|m/s|0.1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4198310000|0.02|m/s|0.1|1995-08-28T00:00:00|1996-09-05T23:59:59\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4238420000|0.02|m/s|0.1|1996-09-06T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4364570000|0.02|m/s|0.1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-4371080000|0.02|m/s|0.1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4371080000|0.02|m/s|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4059940000|0.02|m/s|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|2401390000|0.02|m/s|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3115290000|0.02|m/s|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3120000000|0.02|m/s|0.1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||VHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-84000000000|0.02|m/s|0.1|1988-08-01T00:00:00|1991-07-31T23:59:59\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-16867200000|0.02|m/s|0.1|1991-08-01T00:00:00|1995-08-27T23:59:59\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4250120000|0.02|m/s|0.1|1995-08-28T00:00:00|1998-02-04T11:30:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4179890000|0.02|m/s|0.1|1998-02-04T11:30:01|1999-06-16T10:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-4278370000|0.02|m/s|0.1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4278370000|0.02|m/s|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4006970000|0.02|m/s|0.1|2000-09-26T10:00:01|2002-06-05T12:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|2394610000|0.02|m/s|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.02|m/s|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3120000000|0.02|m/s|0.1|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||VHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
",""),

(
"level=channel&net=MN&startafter=1999-05-01&endbefore=2002-06-05T00:00:00.0&format=text&nodata=404&maxlatitude=45&minlat=42",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-1063680000|0.02|m/s|20|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||BHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1063680000|0.02|m/s|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-1092770000|0.02|m/s|20|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||BHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1092770000|0.02|m/s|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-1069590000|0.02|m/s|20|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1069590000|0.02|m/s|20|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-1063680000|0.02|m/s|1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||LHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|1063680000|0.02|m/s|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-1092770000|0.02|m/s|1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||LHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|1092770000|0.02|m/s|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-1069590000|0.02|m/s|1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|1069590000|0.02|m/s|1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-4254720000|0.003|m/s|0.01|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4254720000|0.003|m/s|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-4371080000|0.003|m/s|0.01|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4371080000|0.003|m/s|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-4278370000|0.003|m/s|0.01|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4278370000|0.003|m/s|0.01|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|-4254720000|0.02|m/s|0.1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||VHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-1H-VBB|4254720000|0.02|m/s|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|-4371080000|0.02|m/s|0.1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||VHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-1H-VBB|4371080000|0.02|m/s|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|-4278370000|0.02|m/s|0.1|1999-06-16T11:00:00|1999-08-31T10:00:00\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-1V-VBB|4278370000|0.02|m/s|0.1|1999-08-31T10:00:01|2000-09-26T10:00:00\n\
",""),

("level=channel&net=MN&startbefore=1999-05-01&endafter=2002-06-05T00:00:00.0&format=text&maxlatitude=45&minlat=42",204,"",""),

(
"sta=AQU&level=channel&starttime=2021-01-01T00:00:00.0&endtime=2021-01-02&net=MN&nodata=404&format=text",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
MN|AQU||BHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|20|2019-03-01T00:00:00|\n\
MN|AQU||BHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|20|2019-03-01T00:00:00|\n\
MN|AQU||BHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|m/s|20|2019-03-01T00:00:00|\n\
MN|AQU||HHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|100|2019-03-01T00:00:00|\n\
MN|AQU||HHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|100|2019-03-01T00:00:00|\n\
MN|AQU||HHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|m/s|100|2019-03-01T00:00:00|\n\
MN|AQU||HNE|42.354|13.405|710|0|90|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|m/s**2|100|2019-03-01T00:00:00|\n\
MN|AQU||HNN|42.354|13.405|710|0|0|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|m/s**2|100|2019-03-01T00:00:00|\n\
MN|AQU||HNZ|42.354|13.405|710|0|0|-90|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|m/s**2|100|2019-03-01T00:00:00|\n\
MN|AQU||LHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||LHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||LHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3121070000|0.003|m/s|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3115290000|0.003|m/s|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.003|m/s|0.01|2008-02-19T00:00:00|\n\
MN|AQU||VHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||VHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||VHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
",""),

(
"level=station&includerestricted=true&format=text",200,"\
#Network | Station | Latitude | Longitude | Elevation | SiteName | StartTime | EndTime\n\
IT|CMA|39.414900|16.818000|610.000000|Campana|2007-11-13T00:00:00|2599-12-31T23:59:59.999\n\
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
S|ELFMC|47.3855|8.5996|650|Gockhausen, Lycee Francais de Marie Curie, ZHSwitzerland|2010-05-11T00:00:00|2015-07-01T00:01:54.843\n\
SI|ABSI|46.7285|11.3205|1801|Aberstuckl (Sarntal)|2006-11-21T14:16:45|\n\
TH|ABG1|50.96532|12.57208|203|UJENA Station Forsthaus Leinawald, GermanyGermany|2011-10-18T16:00:00|2012-11-22T12:00:00\n\
TH|ABG1|50.96757|12.57625|203|UJENA Station Forsthaus Leinawald, GermanyGermany|2012-11-22T12:00:00|\n\
TH|ANNA|50.88399|12.64365|249|UJENA Station St. Anna Fundgrube, GermanyGermany|2014-03-25T10:00:00|2017-12-04T00:00:00\n\
TH|ANNA|50.88902|12.64499|235|UJENA Station St. Anna Fundgrube, GermanyGermany|2017-12-04T00:00:00|\n\
TV|AT04|43.254269|12.450467|595|Castiglione Aldobrando|2010-03-31T00:00:00|2011-02-09T09:55:00\n\
Z3|AT04|37.7252|24.0496|23|Station Egelados Network, GreeceGreece|2005-11-02T00:00:00|2007-02-23T00:00:00\n\
Z3|A319A|43.476425|10.578689|343|Santa Luce (PI)|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
","Include restricted"),

(
"level=station&includerestricted=false&format=text",200,"\
#Network | Station | Latitude | Longitude | Elevation | SiteName | StartTime | EndTime\n\
IT|CMA|39.414900|16.818000|610.000000|Campana|2007-11-13T00:00:00|2599-12-31T23:59:59.999\n\
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
S|ELFMC|47.3855|8.5996|650|Gockhausen, Lycee Francais de Marie Curie, ZHSwitzerland|2010-05-11T00:00:00|2015-07-01T00:01:54.843\n\
SI|ABSI|46.7285|11.3205|1801|Aberstuckl (Sarntal)|2006-11-21T14:16:45|\n\
TH|ABG1|50.96532|12.57208|203|UJENA Station Forsthaus Leinawald, GermanyGermany|2011-10-18T16:00:00|2012-11-22T12:00:00\n\
TH|ANNA|50.88399|12.64365|249|UJENA Station St. Anna Fundgrube, GermanyGermany|2014-03-25T10:00:00|2017-12-04T00:00:00\n\
TH|ANNA|50.88902|12.64499|235|UJENA Station St. Anna Fundgrube, GermanyGermany|2017-12-04T00:00:00|\n\
TV|AT04|43.254269|12.450467|595|Castiglione Aldobrando|2010-03-31T00:00:00|2011-02-09T09:55:00\n\
Z3|AT04|37.7252|24.0496|23|Station Egelados Network, GreeceGreece|2005-11-02T00:00:00|2007-02-23T00:00:00\n\
","No restricted, no A319A "),


(
"starttime=2021-01-06T15%3A55%3A02.658787&endtime=2021-02-05T15%3A55%3A02.658787&level=channel&includerestricted=false&format=text",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
IT|CMA||HGE|39.414900|16.818000|610.000000|0.000000|90.000000|0.000000|CFX_US4H 200 Hz 5 Volt per 5g/Edax Datalogger|0.000106955|0.03|nm/s**2|200|2007-11-13T00:00:00|2599-12-31T23:59:59.999\n\
IT|CMA||HGN|39.414900|16.818000|610.000000|0.000000|0.000000|0.000000|CFX_US4H 200 Hz 5 Volt per 5g/Edax Datalogger|0.000106955|0.03|nm/s**2|200|2007-11-13T00:00:00|2599-12-31T23:59:59.999\n\
IT|CMA||HGZ|39.414900|16.818000|610.000000|0.000000|0.000000|-90.000000|CFX_US4H 200 Hz 5 Volt per 5g/Edax Datalogger|0.000106955|0.03|nm/s**2|200|2007-11-13T00:00:00|2599-12-31T23:59:59.999\n\
IV|ACATE||EHE|37.02398|14.50064|210|0|90|0|LENNARTZ LE3D-5S|503316000|1|m/s|100|2019-02-28T05:59:00|\n\
IV|ACATE||EHN|37.02398|14.50064|210|0|0|0|LENNARTZ LE3D-5S|503316000|1|m/s|100|2019-02-28T05:59:00|\n\
IV|ACATE||EHZ|37.02398|14.50064|210|0|0|-90|LENNARTZ LE3D-5S|503316000|1|m/s|100|2019-02-28T05:59:00|\n\
IV|ACATE||HNE|37.02398|14.50064|210|0|90|0|NANOMETRICS TITAN|320770|1|m/s**2|200|2019-02-28T05:59:00|\n\
IV|ACATE||HNN|37.02398|14.50064|210|0|0|0|NANOMETRICS TITAN|320770|1|m/s**2|200|2019-02-28T05:59:00|\n\
IV|ACATE||HNZ|37.02398|14.50064|210|0|0|-90|NANOMETRICS TITAN|320770|1|m/s**2|200|2019-02-28T05:59:00|\n\
IV|ACER||BHE|40.7867|15.9427|690|1|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2014-05-08T11:42:00|\n\
IV|ACER||BHN|40.7867|15.9427|690|1|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2014-05-08T11:42:00|\n\
IV|ACER||BHZ|40.7867|15.9427|690|1|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2014-05-08T11:42:00|\n\
IV|ACER||HHE|40.7867|15.9427|690|1|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2014-05-08T11:42:00|\n\
IV|ACER||HHN|40.7867|15.9427|690|1|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2014-05-08T11:42:00|\n\
IV|ACER||HHZ|40.7867|15.9427|690|1|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2014-05-08T11:42:00|\n\
IV|ACER||HNE|40.7867|15.9427|690|1|90|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|320770|0.2|m/s**2|100|2014-05-08T11:42:00|\n\
IV|ACER||HNN|40.7867|15.9427|690|1|0|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|320770|0.2|m/s**2|100|2014-05-08T11:42:00|\n\
IV|ACER||HNZ|40.7867|15.9427|690|1|0|-90|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|320770|0.2|m/s**2|100|2014-05-08T11:42:00|\n\
IV|ACER||LHE|40.7867|15.9427|690|1|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2014-05-08T11:42:00|\n\
IV|ACER||LHN|40.7867|15.9427|690|1|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2014-05-08T11:42:00|\n\
IV|ACER||LHZ|40.7867|15.9427|690|1|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2014-05-08T11:42:00|\n\
IV|ACER||VHE|40.7867|15.9427|690|1|90|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2014-05-08T11:42:00|\n\
IV|ACER||VHN|40.7867|15.9427|690|1|0|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2014-05-08T11:42:00|\n\
IV|ACER||VHZ|40.7867|15.9427|690|1|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2014-05-08T11:42:00|\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2009-03-14T10:40:00|\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2009-03-14T10:40:00|\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2009-03-14T10:40:00|\n\
IV|ARVD||HHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2009-03-14T10:40:00|\n\
IV|ARVD||HHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2009-03-14T10:40:00|\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2009-03-14T10:40:00|\n\
IV|ARVD||LHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2009-03-14T10:40:00|\n\
IV|ARVD||LHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2009-03-14T10:40:00|\n\
IV|ARVD||LHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2009-03-14T10:40:00|\n\
IV|ARVD||VHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2009-03-14T10:40:00|\n\
IV|ARVD||VHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2009-03-14T10:40:00|\n\
IV|ARVD||VHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2009-03-14T10:40:00|\n\
IV|IMTC||HHE|40.7209|13.8758|59|0|90|0|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHN|40.7209|13.8758|59|0|0|0|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHZ|40.7209|13.8758|59|0|0|-90|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IV|VBKN||HHE|40.83|14.4299|951|0|90|0|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IV|VBKN||HHN|40.83|14.4299|951|0|0|0|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IV|VBKN||HHZ|40.83|14.4299|951|0|0|-90|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IX|AND3|01|HNE|40.9298|15.3331|905|0|90|0|GURALP CMG-5T|949627|0.1|m/s**2|125|2013-12-17T00:00:00|\n\
IX|AND3|01|HNN|40.9298|15.3331|905|0|0|0|GURALP CMG-5T|949627|0.1|m/s**2|125|2013-12-17T00:00:00|\n\
IX|AND3|01|HNZ|40.9298|15.3331|905|0|0|-90|GURALP CMG-5T|949627|0.1|m/s**2|125|2013-12-17T00:00:00|\n\
IX|AND3|02|HHE|40.9298|15.3331|905|0|90|0|GEOTECH KS-2000EDU|3731340000|0.1|m/s|125|2013-12-17T00:00:00|\n\
IX|AND3|02|HHN|40.9298|15.3331|905|0|0|0|GEOTECH KS-2000EDU|3731340000|0.1|m/s|125|2013-12-17T00:00:00|\n\
IX|AND3|02|HHZ|40.9298|15.3331|905|0|0|-90|GEOTECH KS-2000EDU|3731340000|0.1|m/s|125|2013-12-17T00:00:00|\n\
MN|AQU||BHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|20|2019-03-01T00:00:00|\n\
MN|AQU||BHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|20|2019-03-01T00:00:00|\n\
MN|AQU||BHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|m/s|20|2019-03-01T00:00:00|\n\
MN|AQU||HHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|100|2019-03-01T00:00:00|\n\
MN|AQU||HHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|100|2019-03-01T00:00:00|\n\
MN|AQU||HHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|m/s|100|2019-03-01T00:00:00|\n\
MN|AQU||HNE|42.354|13.405|710|0|90|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|m/s**2|100|2019-03-01T00:00:00|\n\
MN|AQU||HNN|42.354|13.405|710|0|0|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|m/s**2|100|2019-03-01T00:00:00|\n\
MN|AQU||HNZ|42.354|13.405|710|0|0|-90|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|m/s**2|100|2019-03-01T00:00:00|\n\
MN|AQU||LHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||LHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||LHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||UHE|42.354|13.405|710|15|90|0|STRECKEISEN STS-2-120S|3121070000|0.003|m/s|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHN|42.354|13.405|710|15|0|0|STRECKEISEN STS-2-120S|3115290000|0.003|m/s|0.01|2008-02-19T00:00:00|\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.003|m/s|0.01|2008-02-19T00:00:00|\n\
MN|AQU||VHE|42.354|13.405|710|0|90|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||VHN|42.354|13.405|710|0|0|0|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|AQU||VHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|m/s|1|2019-03-01T00:00:00|\n\
MN|ARPR||BHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|20|2014-01-23T00:00:00|\n\
MN|ARPR||BHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|20|2014-01-23T00:00:00|\n\
MN|ARPR||BHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|20|2014-01-23T00:00:00|\n\
MN|ARPR||LHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|1|2014-01-23T00:00:00|\n\
MN|ARPR||LHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|1|2014-01-23T00:00:00|\n\
MN|ARPR||LHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|1|2014-01-23T00:00:00|\n\
MN|ARPR||VHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|10066300000|0.02|m/s|0.1|2014-01-23T00:00:00|\n\
MN|ARPR||VHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|10066300000|0.02|m/s|0.1|2014-01-23T00:00:00|\n\
MN|ARPR||VHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|10066300000|0.02|m/s|0.1|2014-01-23T00:00:00|\n\
OX|ACOM||HHE|46.548|13.5137|1788|0|90|0|NANOMETRICS TRILLIUM-40S|650175000|0.2|m/s|100|2016-01-01T00:00:00|\n\
OX|ACOM||HHN|46.548|13.5137|1788|0|0|0|NANOMETRICS TRILLIUM-40S|650175000|0.2|m/s|100|2016-01-01T00:00:00|\n\
OX|ACOM||HHZ|46.548|13.5137|1788|0|0|-90|NANOMETRICS TRILLIUM-40S|650175000|0.2|m/s|100|2016-01-01T00:00:00|\n\
OX|ACOM||HNE|46.5479|13.5149|1715|0|90|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427894|0.07|m/s**2|100|2016-01-01T00:00:00|\n\
OX|ACOM||HNN|46.5479|13.5149|1715|0|0|0|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427894|0.07|m/s**2|100|2016-01-01T00:00:00|\n\
OX|ACOM||HNZ|46.5479|13.5149|1715|0|0|-90|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427894|0.07|m/s**2|100|2016-01-01T00:00:00|\n\
SI|ABSI||BHE|46.7285|11.3205|1801|0|90|0|STRECKEISEN STS-2-120S|627604000|0.4|m/s|20|2006-11-21T14:16:45|\n\
SI|ABSI||BHN|46.7285|11.3205|1801|0|0|0|STRECKEISEN STS-2-120S|627604000|0.4|m/s|20|2006-11-21T14:16:45|\n\
SI|ABSI||BHZ|46.7285|11.3205|1801|0|0|-90|STRECKEISEN STS-2-120S|627604000|0.4|m/s|20|2006-11-21T14:16:45|\n\
SI|ABSI||HHE|46.7285|11.3205|1801|0|90|0|STRECKEISEN STS-2-120S|627604000|0.4|m/s|100|2006-11-21T14:16:45|\n\
SI|ABSI||HHN|46.7285|11.3205|1801|0|0|0|STRECKEISEN STS-2-120S|627604000|0.4|m/s|100|2006-11-21T14:16:45|\n\
SI|ABSI||HHZ|46.7285|11.3205|1801|0|0|-90|STRECKEISEN STS-2-120S|627604000|0.4|m/s|100|2006-11-21T14:16:45|\n\
SI|ABSI||LHE|46.7285|11.3205|1801|0|90|0|STRECKEISEN STS-2-120S|627604000|0.4|m/s|1|2006-11-21T14:16:45|\n\
SI|ABSI||LHN|46.7285|11.3205|1801|0|0|0|STRECKEISEN STS-2-120S|627604000|0.4|m/s|1|2006-11-21T14:16:45|\n\
SI|ABSI||LHZ|46.7285|11.3205|1801|0|0|-90|STRECKEISEN STS-2-120S|627604000|0.4|m/s|1|2006-11-21T14:16:45|\n\
SI|ABSI||VHE|46.7285|11.3205|1801|0|90|0|STRECKEISEN STS-2-120S|2510420000|0.4|m/s|0.1|2006-11-21T14:16:45|\n\
SI|ABSI||VHN|46.7285|11.3205|1801|0|0|0|STRECKEISEN STS-2-120S|2510420000|0.4|m/s|0.1|2006-11-21T14:16:45|\n\
SI|ABSI||VHZ|46.7285|11.3205|1801|0|0|-90|STRECKEISEN STS-2-120S|2510420000|0.4|m/s|0.1|2006-11-21T14:16:45|\n\
TH|ANNA||HHE|50.88902|12.64499|235|0|90|0|CMG-3ESPC_60s|1968513261|1|m/s|100|2017-12-04T00:00:00|\n\
TH|ANNA||HHN|50.88902|12.64499|235|0|0|0|CMG-3ESPC_60s|1974539322|1|m/s|100|2017-12-04T00:00:00|\n\
TH|ANNA||HHZ|50.88902|12.64499|235|0|0|-90|CMG-3ESPC_60s|1976548009|1|m/s|100|2017-12-04T00:00:00|\n\
","Selection in the future"),


(
"starttime=2004-01-06T15%3A55%3A02.658787&endtime=2010-02-05T15%3A55%3A02.658787&level=channel&format=text&cha=*Z",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
IT|CMA||HGZ|39.414900|16.818000|610.000000|0.000000|0.000000|-90.000000|CFX_US4H 200 Hz 5 Volt per 5g/Edax Datalogger|0.000106955|0.03|nm/s**2|200|2007-11-13T00:00:00|2599-12-31T23:59:59.999\n\
IV|ACER||BHZ|40.7867|15.9427|690|1|0|-90|NANOMETRICS TRILLIUM-40S|1500000000|0.2|m/s|20|2007-07-05T12:00:00|2014-05-08T11:42:00\n\
IV|ACER||HHZ|40.7867|15.9427|690|1|0|-90|NANOMETRICS TRILLIUM-40S|1500000000|0.2|m/s|100|2007-07-05T12:00:00|2014-05-08T11:42:00\n\
IV|ACER||HNZ|40.7867|15.9427|690|0|0|-90|KINEMETRICS EPISENSOR|407880|0.2|m/s**2|200|2007-07-05T12:00:00|2011-06-24T00:00:00\n\
IV|ACER||LHZ|40.7867|15.9427|690|1|0|-90|NANOMETRICS TRILLIUM-40S|1485900000|0.2|m/s|1|2007-07-05T12:00:00|2014-05-08T11:42:00\n\
IV|ACER||VHZ|40.7867|15.9427|690|1|0|-90|NANOMETRICS TRILLIUM-40S|3165200000|0.02|m/s|0.1|2007-07-05T12:00:00|2014-05-08T11:42:00\n\
IV|AQU||SHZ|42.35388|13.40193|729|0|0|-90|GEOTECH S-13|582216000|0.2|m/s|50|2003-03-01T00:00:00|2008-10-15T00:00:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2009-03-14T10:40:00|\n\
IV|ARVD||EHZ|43.49807|12.94153|461|0|0|-90|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHZ|43.49807|12.94153|461|0|0|-90|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2009-03-14T10:40:00|\n\
IV|ARVD||LHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2009-03-14T10:40:00|\n\
IV|ARVD||VHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2009-03-14T10:40:00|\n\
IV|IMTC||HHZ|40.7209|13.8758|59|0|0|-90|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IV|VBKN||HHZ|40.83|14.4299|951|0|0|-90|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|m/s|20|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||BHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|m/s|20|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|m/s|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|m/s|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLZ|42.354|13.405|710|15|0|-90|KINEMETRICS EPISENSOR|537691|0.02|m/s**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|m/s|1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||LHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|m/s|1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|2394610000|0.003|m/s|0.01|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||UHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.003|m/s|0.01|2008-02-19T00:00:00|\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|2394610000|0.02|m/s|0.1|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||VHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|3114870000|0.02|m/s|0.1|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
NI|ACOM||BHZ|46.548|13.5137|1788|0|0|-90|STRECKEISEN STS-2-120S|626646000|5|m/s|20|2005-02-01T12:00:00|2008-10-20T16:00:01\n\
NI|ACOM||BHZ|46.548|13.5137|1788|0|0|-90|NANOMETRICS TRILLIUM-40S|629221000|0.3|m/s|20|2008-10-20T16:00:01|2008-10-20T16:00:02\n\
NI|ACOM||BHZ|46.548|13.5137|1788|0|0|-90|NANOMETRICS TRILLIUM-40S|650175000|0.2|m/s|20|2008-10-20T16:00:03|2015-12-31T23:59:59\n\
NI|ACOM||HHZ|46.548|13.5137|1788|0|0|-90|STRECKEISEN STS-2-120S|624217000|7|m/s|100|2005-02-01T12:00:00|2008-10-20T16:00:01\n\
NI|ACOM||HHZ|46.548|13.5137|1788|0|0|-90|NANOMETRICS TRILLIUM-40S|629436000|0.6|m/s|100|2008-10-20T16:00:01|2008-10-20T16:00:02\n\
NI|ACOM||HHZ|46.548|13.5137|1788|0|0|-90|NANOMETRICS TRILLIUM-40S|650175000|0.2|m/s|100|2008-10-20T16:00:03|2015-12-31T23:59:59\n\
NI|ACOM||LHZ|46.548|13.5137|1788|0|0|-90|NANOMETRICS TRILLIUM-40S|650175000|0.2|m/s|1|2008-10-20T16:00:03|2015-12-31T23:59:59\n\
NI|ACOM||VHZ|46.548|13.5137|1788|0|0|-90|NANOMETRICS TRILLIUM-40S|650175000|0.2|m/s|1|2008-10-20T16:00:03|2015-12-31T23:59:59\n\
SI|ABSI||BHZ|46.7285|11.3205|1801|0|0|-90|STRECKEISEN STS-2-120S|627604000|0.4|m/s|20|2006-11-21T14:16:45|\n\
SI|ABSI||HHZ|46.7285|11.3205|1801|0|0|-90|STRECKEISEN STS-2-120S|627604000|0.4|m/s|100|2006-11-21T14:16:45|\n\
SI|ABSI||LHZ|46.7285|11.3205|1801|0|0|-90|STRECKEISEN STS-2-120S|627604000|0.4|m/s|1|2006-11-21T14:16:45|\n\
SI|ABSI||VHZ|46.7285|11.3205|1801|0|0|-90|STRECKEISEN STS-2-120S|2510420000|0.4|m/s|0.1|2006-11-21T14:16:45|\n\
Z3|AT04||HHZ|37.7252|24.0496|23|0|0|-90|GFZ:Z32005:CMG-3ESP/60/g=2000|2000000000|0.1|m/s|100|2005-11-02T00:00:00|2007-02-23T00:00:00\n\
Z3|AT04||LHZ|37.7252|24.0496|23|0|0|-90|GFZ:Z32005:CMG-3ESP/60/g=2000|2000000000|0.1|m/s|1|2005-11-02T00:00:00|2007-02-23T00:00:00\n\
","Selection in the past"),

(
"level=station&net=*&format=text&start=2020-05-08T11:42:00&channel=EH*",200,"\
#Network | Station | Latitude | Longitude | Elevation | SiteName | StartTime | EndTime\n\
IV|ACATE|37.02398|14.50064|210|ACATE|2019-02-28T05:59:00|\n\
","0 selected channels but station selected in output"),

(
"level=channel&latitude=42&longitude=12&minradius=1.5&maxradius=2&format=text&nodata=404",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2009-03-14T10:40:00|\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2009-03-14T10:40:00|\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2009-03-14T10:40:00|\n\
IV|ARVD||EHE|43.49807|12.94153|461|0|90|0|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHE|43.49807|12.94153|461|0|90|0|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||EHN|43.49807|12.94153|461|0|0|0|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHN|43.49807|12.94153|461|0|0|0|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||EHZ|43.49807|12.94153|461|0|0|-90|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHZ|43.49807|12.94153|461|0|0|-90|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||HHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2009-03-14T10:40:00|\n\
IV|ARVD||HHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2009-03-14T10:40:00|\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2009-03-14T10:40:00|\n\
IV|ARVD||LHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2009-03-14T10:40:00|\n\
IV|ARVD||LHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2009-03-14T10:40:00|\n\
IV|ARVD||LHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2009-03-14T10:40:00|\n\
IV|ARVD||VHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2009-03-14T10:40:00|\n\
IV|ARVD||VHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2009-03-14T10:40:00|\n\
IV|ARVD||VHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2009-03-14T10:40:00|\n\
IV|IMTC||HHE|40.7209|13.8758|59|0|90|0|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHN|40.7209|13.8758|59|0|0|0|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHZ|40.7209|13.8758|59|0|0|-90|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
Z3|A319A||HHE|43.476425|10.578689|343|1|90|0|NANOMETRICS TRILLIUM-120C|749.1|1|m/s|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
Z3|A319A||HHN|43.476425|10.578689|343|1|0|0|NANOMETRICS TRILLIUM-120C|749.1|1|m/s|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
Z3|A319A||HHZ|43.476425|10.578689|343|1|0|-90|NANOMETRICS TRILLIUM-120C|749.1|1|m/s|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
","check minradius maxradius"),


(
"level=station&latitude=42&longitude=12&minradius=1.5&maxradius=2&format=text&nodata=404",200,"\
#Network | Station | Latitude | Longitude | Elevation | SiteName | StartTime | EndTime\n\
IV|ARVD|43.49807|12.94153|461|ARCEVIA 2|2003-03-01T00:00:00|\n\
IV|IMTC|40.7209|13.8758|59|Ischia - Monte Corvo|1988-01-01T00:00:00|\n\
Z3|A319A|43.476425|10.578689|343|Santa Luce (PI)|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
","check minradius maxradius level station"),

(
"level=network&latitude=42&longitude=12&minradius=1.5&maxradius=2&format=text&nodata=404",200,"\
#Network | Description | StartTime | EndTime | TotalStations\n\
IV|Italian Seismic Network|1988-01-01T00:00:00||7\n\
Z3|AlpArray Seismic Network (AASN) temporary component|2015-01-01T00:00:00|2022-12-31T00:00:00|1\n\
","check minradius maxradius level network"),

(
"level=channel&latitude=42&longitude=12&minradiuskm=166.8&maxradiuskm=222.4&format=text&nodata=404",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2009-03-14T10:40:00|\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2009-03-14T10:40:00|\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2009-03-14T10:40:00|\n\
IV|ARVD||EHE|43.49807|12.94153|461|0|90|0|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHE|43.49807|12.94153|461|0|90|0|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||EHN|43.49807|12.94153|461|0|0|0|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHN|43.49807|12.94153|461|0|0|0|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||EHZ|43.49807|12.94153|461|0|0|-90|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHZ|43.49807|12.94153|461|0|0|-90|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||HHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2009-03-14T10:40:00|\n\
IV|ARVD||HHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2009-03-14T10:40:00|\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2009-03-14T10:40:00|\n\
IV|ARVD||LHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2009-03-14T10:40:00|\n\
IV|ARVD||LHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2009-03-14T10:40:00|\n\
IV|ARVD||LHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2009-03-14T10:40:00|\n\
IV|ARVD||VHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2009-03-14T10:40:00|\n\
IV|ARVD||VHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2009-03-14T10:40:00|\n\
IV|ARVD||VHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2009-03-14T10:40:00|\n\
IV|IMTC||HHE|40.7209|13.8758|59|0|90|0|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHN|40.7209|13.8758|59|0|0|0|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHZ|40.7209|13.8758|59|0|0|-90|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
Z3|A319A||HHE|43.476425|10.578689|343|1|90|0|NANOMETRICS TRILLIUM-120C|749.1|1|m/s|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
Z3|A319A||HHN|43.476425|10.578689|343|1|0|0|NANOMETRICS TRILLIUM-120C|749.1|1|m/s|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
Z3|A319A||HHZ|43.476425|10.578689|343|1|0|-90|NANOMETRICS TRILLIUM-120C|749.1|1|m/s|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
","check minradiuskm maxradiuskm"),


(
"sta=ABG1&nodata=404&level=channel&format=text",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
TH|ABG1||BHE|50.96532|12.57208|203|0|90|0|CMG-3ESPC_60s|1230064236|1|m/s|20|2011-10-18T16:00:00|2012-11-22T12:00:00\n\
TH|ABG1||BHN|50.96532|12.57208|203|0|0|0|CMG-3ESPC_60s|1230064236|1|m/s|20|2011-10-18T16:00:00|2012-11-22T12:00:00\n\
TH|ABG1||BHZ|50.96532|12.57208|203|0|0|-90|CMG-3ESPC_60s|1231320686|1|m/s|20|2011-10-18T16:00:00|2012-11-22T12:00:00\n\
TH|ABG1||HHE|50.96532|12.57208|203|0|90|0|CMG-3ESPC_60s|1233092545|1|m/s|100|2011-10-18T16:00:00|2012-11-22T12:00:00\n\
TH|ABG1||HHN|50.96532|12.57208|203|0|0|0|CMG-3ESPC_60s|1233092545|1|m/s|100|2011-10-18T16:00:00|2012-11-22T12:00:00\n\
TH|ABG1||HHZ|50.96532|12.57208|203|0|0|-90|CMG-3ESPC_60s|1234352088|1|m/s|100|2011-10-18T16:00:00|2012-11-22T12:00:00\n\
TH|ABG1||LHE|50.96532|12.57208|203|0|90|0|CMG-3ESPC_60s|1232924070|0.3|m/s|1|2011-10-18T16:00:00|2012-11-22T12:00:00\n\
TH|ABG1||LHN|50.96532|12.57208|203|0|0|0|CMG-3ESPC_60s|1232924070|0.3|m/s|1|2011-10-18T16:00:00|2012-11-22T12:00:00\n\
TH|ABG1||LHZ|50.96532|12.57208|203|0|0|-90|CMG-3ESPC_60s|1234183441|0.3|m/s|1|2011-10-18T16:00:00|2012-11-22T12:00:00\n\
TH|ABG1||BHE|50.96757|12.57625|203|0|90|0|CMG-3ESPC_60s|1230064236|1|m/s|20|2012-11-22T12:00:00|\n\
TH|ABG1||BHN|50.96757|12.57625|203|0|0|0|CMG-3ESPC_60s|1230064236|1|m/s|20|2012-11-22T12:00:00|\n\
TH|ABG1||BHZ|50.96757|12.57625|203|0|0|-90|CMG-3ESPC_60s|1231320686|1|m/s|20|2012-11-22T12:00:00|\n\
TH|ABG1||HHE|50.96757|12.57625|203|0|90|0|CMG-3ESPC_60s|1233092545|1|m/s|100|2012-11-22T12:00:00|\n\
TH|ABG1||HHN|50.96757|12.57625|203|0|0|0|CMG-3ESPC_60s|1233092545|1|m/s|100|2012-11-22T12:00:00|\n\
TH|ABG1||HHZ|50.96757|12.57625|203|0|0|-90|CMG-3ESPC_60s|1234352088|1|m/s|100|2012-11-22T12:00:00|\n\
TH|ABG1||LHE|50.96757|12.57625|203|0|90|0|CMG-3ESPC_60s|1232924070|0.3|m/s|1|2012-11-22T12:00:00|\n\
TH|ABG1||LHN|50.96757|12.57625|203|0|0|0|CMG-3ESPC_60s|1232924070|0.3|m/s|1|2012-11-22T12:00:00|\n\
TH|ABG1||LHZ|50.96757|12.57625|203|0|0|-90|CMG-3ESPC_60s|1234183441|0.3|m/s|1|2012-11-22T12:00:00|\n\
","query_core_single_station check of a station with two periods"),



(
"level=channel&network=S&station=ELFMC&format=text",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
S|ELFMC||EHE|47.3855|8.5996|650|0|90|0||399981208.4|10|m/s|500|2010-05-11T00:00:00|2010-12-01T00:00:00\n\
S|ELFMC||EHE|47.3855|8.5996|650|0|90|0||404236000|5|m/s|100|2010-12-01T00:00:00|2015-07-01T00:00:00\n\
S|ELFMC||EHN|47.3855|8.5996|650|0|0|0||399981208.4|10|m/s|500|2010-05-11T00:00:00|2010-12-01T00:00:00\n\
S|ELFMC||EHN|47.3855|8.5996|650|0|0|0||404236000|5|m/s|100|2010-12-01T00:00:00|2015-07-01T00:00:00\n\
S|ELFMC||EHZ|47.3855|8.5996|650|0|0|-90||399981208.4|10|m/s|500|2010-05-11T00:00:00|2010-12-01T00:00:00\n\
S|ELFMC||EHZ|47.3855|8.5996|650|0|0|-90||404236000|5|m/s|100|2010-12-01T00:00:00|2015-07-01T00:00:00\n\
","check one character network code"),

(
"level=channel&format=text&starttime=2000-09-18T03:09:54&endtime=2023-09-18T03:18:34&cha=C??,E??,H??,S??&nodata=404&lat=43&lon=12&maxradius=0.9",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
IV|ARVD||EHE|43.49807|12.94153|461|0|90|0|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHE|43.49807|12.94153|461|0|90|0|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||EHN|43.49807|12.94153|461|0|0|0|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHN|43.49807|12.94153|461|0|0|0|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||EHZ|43.49807|12.94153|461|0|0|-90|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHZ|43.49807|12.94153|461|0|0|-90|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||HHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2009-03-14T10:40:00|\n\
IV|ARVD||HHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2009-03-14T10:40:00|\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2009-03-14T10:40:00|\n\
TV|AT04||EHE|43.254269|12.450467|595|0|90|0|LENNARTZ LE3D-5S|251652000|1|m/s|100|2010-03-31T00:00:00|2011-02-09T09:55:00\n\
TV|AT04||EHN|43.254269|12.450467|595|0|0|0|LENNARTZ LE3D-5S|251652000|1|m/s|100|2010-03-31T00:00:00|2011-02-09T09:55:00\n\
TV|AT04||EHZ|43.254269|12.450467|595|0|0|-90|LENNARTZ LE3D-5S|251652000|1|m/s|100|2010-03-31T00:00:00|2011-02-09T09:55:00\n\
TV|AT04||HNE|43.254269|12.450467|595|0|90|0|KINEMETRICS EPISENSOR|641523|0.2|m/s**2|200|2010-03-31T00:00:00|2011-02-09T09:55:00\n\
TV|AT04||HNN|43.254269|12.450467|595|0|0|0|KINEMETRICS EPISENSOR|641523|0.2|m/s**2|200|2010-03-31T00:00:00|2011-02-09T09:55:00\n\
TV|AT04||HNZ|43.254269|12.450467|595|0|0|-90|KINEMETRICS EPISENSOR|641523|0.2|m/s**2|200|2010-03-31T00:00:00|2011-02-09T09:55:00\n\
","maxradius and channel"),

(
"level=station&format=geojson&station=ACER,ACOM",200,'\
{"type":"FeatureCollection","features":[{"type":"Feature","properties":{"code":"ACER","Name":"Acerenza","network":"IV","startDate":"2007-07-05T12:00:00","endDate":null,"Latitude":40.7867,"Longitude":15.9427,"Elevation":690},"geometry":{"type":"Point","coordinates":[15.9427,40.7867]}},{"type":"Feature","properties":{"code":"ACOM","Name":"Acomizza","network":"NI","startDate":"2005-02-01T12:00:00","endDate":"2015-12-31T23:59:59","Latitude":46.548,"Longitude":13.5137,"Elevation":1788},"geometry":{"type":"Point","coordinates":[13.5137,46.548]}},{"type":"Feature","properties":{"code":"ACOM","Name":"Acomizza","network":"OX","startDate":"2016-01-01T00:00:00","endDate":null,"Latitude":46.548,"Longitude":13.5137,"Elevation":1788},"geometry":{"type":"Point","coordinates":[13.5137,46.548]}}]}',"geojson two station in three networks"),

(
"level=station&format=geojson&net=IV&nodata=404",200,'\
{"type":"FeatureCollection","features":[{"type":"Feature","properties":{"code":"ACATE","Name":"ACATE","network":"IV","startDate":"2019-02-28T05:59:00","endDate":null,"Latitude":37.02398,"Longitude":14.50064,"Elevation":210},"geometry":{"type":"Point","coordinates":[14.50064,37.02398]}},{"type":"Feature","properties":{"code":"ACER","Name":"Acerenza","network":"IV","startDate":"2007-07-05T12:00:00","endDate":null,"Latitude":40.7867,"Longitude":15.9427,"Elevation":690},"geometry":{"type":"Point","coordinates":[15.9427,40.7867]}},{"type":"Feature","properties":{"code":"AQT1","Name":"Arquata del Tronto","network":"IV","startDate":"2011-07-22T00:00:00","endDate":"2016-09-01T09:50:00","Latitude":42.77383,"Longitude":13.2935,"Elevation":770},"geometry":{"type":"Point","coordinates":[13.2935,42.77383]}},{"type":"Feature","properties":{"code":"AQU","Name":"L\'Aquila, Italy","network":"IV","startDate":"2003-03-01T00:00:00","endDate":"2008-10-15T00:00:00","Latitude":42.354,"Longitude":13.405,"Elevation":710},"geometry":{"type":"Point","coordinates":[13.405,42.354]}},{"type":"Feature","properties":{"code":"ARVD","Name":"ARCEVIA 2","network":"IV","startDate":"2003-03-01T00:00:00","endDate":null,"Latitude":43.49807,"Longitude":12.94153,"Elevation":461},"geometry":{"type":"Point","coordinates":[12.94153,43.49807]}},{"type":"Feature","properties":{"code":"IMTC","Name":"Ischia - Monte Corvo","network":"IV","startDate":"1988-01-01T00:00:00","endDate":null,"Latitude":40.7209,"Longitude":13.8758,"Elevation":59},"geometry":{"type":"Point","coordinates":[13.8758,40.7209]}},{"type":"Feature","properties":{"code":"VBKN","Name":"Vesuvio - Bunker Nord","network":"IV","startDate":"1988-01-01T00:00:00","endDate":null,"Latitude":40.83,"Longitude":14.4299,"Elevation":951},"geometry":{"type":"Point","coordinates":[14.4299,40.83]}}]}',"Multiple stations issue #102, commas among features"),

]


testdatapostobspy = [
(
"level=station\n\
minlat=10\n\
maxlat=62\n\
format=text\n\
nodata=404\n\
* ACER * * 1920-01-01T00:00:00.0 2020-01-01T00:00:00.0",200,"\
#Network | Station | Latitude | Longitude | Elevation | SiteName | StartTime | EndTime\n\
IV|ACER|40.7867|15.9427|690|Acerenza|2007-07-05T12:00:00|\n\
","POST level station 1.3", "1.3.0"),

(
"minlat=10\n\
maxlat=62\n\
level=station\n\
format=text\n\
nodata=404\n\
* ACER * * 1920-01-01T00:00:00.0 2020-01-01T00:00:00.0",200,"\
#Network | Station | Latitude | Longitude | Elevation | SiteName | StartTime | EndTime\n\
IV|ACER|40.7867|15.9427|690|Acerenza|2007-07-05T12:00:00|\n\
","POST level station 1.4", "1.4.0" ),
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
","POST level station"),

(
"minlat=10\n\
maxlat=62\n\
level=station\n\
format=text\n\
nodata=404\n\
updatedafter=2000-01-01T00:00:00\n\
* * * * 1920-01-01T00:00:00.0 2020-01-01T00:00:00.0",200,"\
#Network | Station | Latitude | Longitude | Elevation | SiteName | StartTime | EndTime\n\
IT|CMA|39.414900|16.818000|610.000000|Campana|2007-11-13T00:00:00|2599-12-31T23:59:59.999\n\
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
S|ELFMC|47.3855|8.5996|650|Gockhausen, Lycee Francais de Marie Curie, ZHSwitzerland|2010-05-11T00:00:00|2015-07-01T00:01:54.843\n\
SI|ABSI|46.7285|11.3205|1801|Aberstuckl (Sarntal)|2006-11-21T14:16:45|\n\
TH|ABG1|50.96532|12.57208|203|UJENA Station Forsthaus Leinawald, GermanyGermany|2011-10-18T16:00:00|2012-11-22T12:00:00\n\
TH|ABG1|50.96757|12.57625|203|UJENA Station Forsthaus Leinawald, GermanyGermany|2012-11-22T12:00:00|\n\
TH|ANNA|50.88399|12.64365|249|UJENA Station St. Anna Fundgrube, GermanyGermany|2014-03-25T10:00:00|2017-12-04T00:00:00\n\
TH|ANNA|50.88902|12.64499|235|UJENA Station St. Anna Fundgrube, GermanyGermany|2017-12-04T00:00:00|\n\
TV|AT04|43.254269|12.450467|595|Castiglione Aldobrando|2010-03-31T00:00:00|2011-02-09T09:55:00\n\
Z3|AT04|37.7252|24.0496|23|Station Egelados Network, GreeceGreece|2005-11-02T00:00:00|2007-02-23T00:00:00\n\
Z3|A319A|43.476425|10.578689|343|Santa Luce (PI)|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
","POST updatedafter"),


(
"minlat=10\n\
maxlat=62\n\
level=station\n\
format=text\n\
nodata=404\n\
updatedafter=1900-01-01T00:00:00\n\
includerestricted=False\n\
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
IV|ARVD||BHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2009-03-14T10:40:00|\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2009-03-14T10:40:00|\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2009-03-14T10:40:00|\n\
IV|ARVD||EHE|43.49807|12.94153|461|0|90|0|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHE|43.49807|12.94153|461|0|90|0|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||EHN|43.49807|12.94153|461|0|0|0|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHN|43.49807|12.94153|461|0|0|0|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||EHZ|43.49807|12.94153|461|0|0|-90|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHZ|43.49807|12.94153|461|0|0|-90|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||HHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2009-03-14T10:40:00|\n\
IV|ARVD||HHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2009-03-14T10:40:00|\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2009-03-14T10:40:00|\n\
IV|ARVD||LHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2009-03-14T10:40:00|\n\
IV|ARVD||LHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2009-03-14T10:40:00|\n\
IV|ARVD||LHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2009-03-14T10:40:00|\n\
IV|ARVD||VHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2009-03-14T10:40:00|\n\
IV|ARVD||VHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2009-03-14T10:40:00|\n\
IV|ARVD||VHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2009-03-14T10:40:00|\n\
IV|IMTC||HHE|40.7209|13.8758|59|0|90|0|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHN|40.7209|13.8758|59|0|0|0|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHZ|40.7209|13.8758|59|0|0|-90|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
Z3|A319A||HHE|43.476425|10.578689|343|1|90|0|NANOMETRICS TRILLIUM-120C|749.1|1|m/s|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
Z3|A319A||HHN|43.476425|10.578689|343|1|0|0|NANOMETRICS TRILLIUM-120C|749.1|1|m/s|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
Z3|A319A||HHZ|43.476425|10.578689|343|1|0|-90|NANOMETRICS TRILLIUM-120C|749.1|1|m/s|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
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
IV|ARVD||BHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2009-03-14T10:40:00|\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2009-03-14T10:40:00|\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2009-03-14T10:40:00|\n\
IV|ARVD||EHE|43.49807|12.94153|461|0|90|0|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHE|43.49807|12.94153|461|0|90|0|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||EHN|43.49807|12.94153|461|0|0|0|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHN|43.49807|12.94153|461|0|0|0|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||EHZ|43.49807|12.94153|461|0|0|-90|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2003-03-01T00:00:00|2005-09-30T10:33:00\n\
IV|ARVD||EHZ|43.49807|12.94153|461|0|0|-90|LENNARTZ LE3D-5S|466034000|0.2|m/s|50|2005-09-30T10:33:00|2008-02-08T12:00:00\n\
IV|ARVD||HHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2009-03-14T10:40:00|\n\
IV|ARVD||HHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2009-03-14T10:40:00|\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||HHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|100|2009-03-14T10:40:00|\n\
IV|ARVD||LHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2009-03-14T10:40:00|\n\
IV|ARVD||LHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2009-03-14T10:40:00|\n\
IV|ARVD||LHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||LHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|1|2009-03-14T10:40:00|\n\
IV|ARVD||VHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2009-03-14T10:40:00|\n\
IV|ARVD||VHN|43.49807|12.94153|461|0|45|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHN|43.49807|12.94153|461|0|0|0|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2009-03-14T10:40:00|\n\
IV|ARVD||VHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||VHZ|43.49807|12.94153|461|0|0|-90|NANOMETRICS TRILLIUM-40S|2430000000|0.02|m/s|0.1|2009-03-14T10:40:00|\n\
IV|IMTC||HHE|40.7209|13.8758|59|0|90|0|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHN|40.7209|13.8758|59|0|0|0|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHZ|40.7209|13.8758|59|0|0|-90|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
Z3|A319A||HHE|43.476425|10.578689|343|1|90|0|NANOMETRICS TRILLIUM-120C|749.1|1|m/s|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
Z3|A319A||HHN|43.476425|10.578689|343|1|0|0|NANOMETRICS TRILLIUM-120C|749.1|1|m/s|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
Z3|A319A||HHZ|43.476425|10.578689|343|1|0|-90|NANOMETRICS TRILLIUM-120C|749.1|1|m/s|100|2015-12-11T12:06:34|2019-04-10T23:59:00\n\
","Check min/maxradius in POST"),



(
"latitude=42\n\
longitude=12\n\
level=channel\n\
format=text\n\
minradius=1.5\n\
maxradius=2.0\n\
nodata=404\n\
_MOST * * * 1988-01-01T00:00:00.0 2040-01-01T00:00:00.0",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
IV|IMTC||HHE|40.7209|13.8758|59|0|90|0|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHN|40.7209|13.8758|59|0|0|0|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHZ|40.7209|13.8758|59|0|0|-90|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
","Check min/maxradius in POST with virtual network"),

(
"minlat=0\n\
maxlat=45\n\
level=channel\n\
format=text\n\
nodata=404\n\
MN * * H*Z 1900-01-01T00:00:00.0 2030-01-01T00:00:00.0\n\
IV * * B*E 1900-01-01T00:00:00.0 2030-01-01T00:00:00.0",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
IV|ACER||BHE|40.7867|15.9427|690|1|90|0|NANOMETRICS TRILLIUM-40S|1500000000|0.2|m/s|20|2007-07-05T12:00:00|2014-05-08T11:42:00\n\
IV|ACER||BHE|40.7867|15.9427|690|1|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2014-05-08T11:42:00|\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2009-03-14T10:40:00|\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|m/s|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|m/s|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|780000000|0.02|m/s|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|m/s|100|2019-03-01T00:00:00|\n\
MN|AQU||HLZ|42.354|13.405|710|15|0|-90|KINEMETRICS EPISENSOR|537691|0.02|m/s**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLZ|42.354|13.405|710|15|0|-90|KINEMETRICS EPISENSOR|530244|0.2|m/s**2|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HNZ|42.354|13.405|710|0|0|-90|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|m/s**2|100|2019-03-01T00:00:00|\n\
","Different networks and channel patterns"),


(
"minlat=0\n\
maxlat=45\n\
level=channel\n\
format=text\n\
nodata=404\n\
MN * * H*Z 1900-01-01T00:00:00.0 2030-01-01T00:00:00.0\n\
_NFOTABOO * * ?N? 1900-01-01T00:00:00.0 2030-01-01T00:00:00.0\n\
IV * * B*E 1900-01-01T00:00:00.0 2030-01-01T00:00:00.0",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
IV|ACER||BHE|40.7867|15.9427|690|1|90|0|NANOMETRICS TRILLIUM-40S|1500000000|0.2|m/s|20|2007-07-05T12:00:00|2014-05-08T11:42:00\n\
IV|ACER||BHE|40.7867|15.9427|690|1|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2014-05-08T11:42:00|\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|50|2008-02-08T12:00:00|2008-02-26T10:03:00\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|135|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2008-02-26T10:03:00|2009-03-14T10:40:00\n\
IV|ARVD||BHE|43.49807|12.94153|461|0|90|0|NANOMETRICS TRILLIUM-40S|1179650000|0.2|m/s|20|2009-03-14T10:40:00|\n\
IX|AND3|01|HNE|40.9298|15.3331|905|0|90|0|GURALP CMG-5T|949627|0.1|m/s**2|125|2013-12-17T00:00:00|\n\
IX|AND3|01|HNN|40.9298|15.3331|905|0|0|0|GURALP CMG-5T|949627|0.1|m/s**2|125|2013-12-17T00:00:00|\n\
IX|AND3|01|HNZ|40.9298|15.3331|905|0|0|-90|GURALP CMG-5T|949627|0.1|m/s**2|125|2013-12-17T00:00:00|\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|598652000|0.02|m/s|100|2002-06-05T12:00:01|2008-02-18T23:59:59\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|778718000|0.02|m/s|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HHZ|42.354|13.405|710|15|0|-90|STRECKEISEN STS-2-120S|780000000|0.02|m/s|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HHZ|42.354|13.405|710|0|0|-90|STRECKEISEN STS-2-120S|629145000|0.02|m/s|100|2019-03-01T00:00:00|\n\
MN|AQU||HLZ|42.354|13.405|710|15|0|-90|KINEMETRICS EPISENSOR|537691|0.02|m/s**2|100|2008-02-19T00:00:00|2011-04-13T00:00:00\n\
MN|AQU||HLZ|42.354|13.405|710|15|0|-90|KINEMETRICS EPISENSOR|530244|0.2|m/s**2|100|2011-04-13T00:00:00|2017-12-31T07:56:00\n\
MN|AQU||HNZ|42.354|13.405|710|0|0|-90|KINEMETRICS EPISENSOR-FBA-ES-T-CL-2G-FS-40-VPP|427693|0.2|m/s**2|100|2019-03-01T00:00:00|\n\
","Different networks and channel patterns virtual networks"),

(
"minlat=0\n\
maxlat=42\n\
level=channel\n\
format=text\n\
nodata=404\n\
updatedafter=1900-01-01T00:00:00\n\
MN * * * 1900-01-01T00:00:00.0 2030-01-01T00:00:00.0\n\
_MOST * * * 1900-01-01T00:00:00.0 2030-01-01T00:00:00.0\n\
_NFOTABOO * * * 1900-01-01T00:00:00.0 2030-01-01T00:00:00.0",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
IV|IMTC||HHE|40.7209|13.8758|59|0|90|0|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHN|40.7209|13.8758|59|0|0|0|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHZ|40.7209|13.8758|59|0|0|-90|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IX|AND3|01|HNE|40.9298|15.3331|905|0|90|0|GURALP CMG-5T|949627|0.1|m/s**2|125|2013-12-17T00:00:00|\n\
IX|AND3|01|HNN|40.9298|15.3331|905|0|0|0|GURALP CMG-5T|949627|0.1|m/s**2|125|2013-12-17T00:00:00|\n\
IX|AND3|01|HNZ|40.9298|15.3331|905|0|0|-90|GURALP CMG-5T|949627|0.1|m/s**2|125|2013-12-17T00:00:00|\n\
IX|AND3|02|HHE|40.9298|15.3331|905|0|90|0|GEOTECH KS-2000EDU|3731340000|0.1|m/s|125|2013-12-17T00:00:00|\n\
IX|AND3|02|HHN|40.9298|15.3331|905|0|0|0|GEOTECH KS-2000EDU|3731340000|0.1|m/s|125|2013-12-17T00:00:00|\n\
IX|AND3|02|HHZ|40.9298|15.3331|905|0|0|-90|GEOTECH KS-2000EDU|3731340000|0.1|m/s|125|2013-12-17T00:00:00|\n\
MN|ARPR||BHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|20|2014-01-23T00:00:00|\n\
MN|ARPR||BHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|20|2014-01-23T00:00:00|\n\
MN|ARPR||BHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|20|2014-01-23T00:00:00|\n\
MN|ARPR||LHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|1|2014-01-23T00:00:00|\n\
MN|ARPR||LHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|1|2014-01-23T00:00:00|\n\
MN|ARPR||LHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|1|2014-01-23T00:00:00|\n\
MN|ARPR||VHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|10066300000|0.02|m/s|0.1|2014-01-23T00:00:00|\n\
MN|ARPR||VHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|10066300000|0.02|m/s|0.1|2014-01-23T00:00:00|\n\
MN|ARPR||VHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|10066300000|0.02|m/s|0.1|2014-01-23T00:00:00|\n\
","Two virtual, one FDSN networks"),


(
"minlat=0\n\
maxlat=42\n\
level=channel\n\
format=text\n\
nodata=404\n\
updatedafter=1900-01-01T00:00:00\n\
MN * * BH* 1900-01-01T00:00:00.0 2030-01-01T00:00:00.0\n\
_MOST * * * 1900-01-01T00:00:00.0 2030-01-01T00:00:00.0\n\
_NFOTABOO * * * 1900-01-01T00:00:00.0 2030-01-01T00:00:00.0",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
IV|IMTC||HHE|40.7209|13.8758|59|0|90|0|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHN|40.7209|13.8758|59|0|0|0|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHZ|40.7209|13.8758|59|0|0|-90|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IX|AND3|01|HNE|40.9298|15.3331|905|0|90|0|GURALP CMG-5T|949627|0.1|m/s**2|125|2013-12-17T00:00:00|\n\
IX|AND3|01|HNN|40.9298|15.3331|905|0|0|0|GURALP CMG-5T|949627|0.1|m/s**2|125|2013-12-17T00:00:00|\n\
IX|AND3|01|HNZ|40.9298|15.3331|905|0|0|-90|GURALP CMG-5T|949627|0.1|m/s**2|125|2013-12-17T00:00:00|\n\
IX|AND3|02|HHE|40.9298|15.3331|905|0|90|0|GEOTECH KS-2000EDU|3731340000|0.1|m/s|125|2013-12-17T00:00:00|\n\
IX|AND3|02|HHN|40.9298|15.3331|905|0|0|0|GEOTECH KS-2000EDU|3731340000|0.1|m/s|125|2013-12-17T00:00:00|\n\
IX|AND3|02|HHZ|40.9298|15.3331|905|0|0|-90|GEOTECH KS-2000EDU|3731340000|0.1|m/s|125|2013-12-17T00:00:00|\n\
MN|ARPR||BHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|20|2014-01-23T00:00:00|\n\
MN|ARPR||BHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|20|2014-01-23T00:00:00|\n\
MN|ARPR||BHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|20|2014-01-23T00:00:00|\n\
","Two virtual, one FDSN networks, channels"),


(
"minlat=0\n\
maxlat=42\n\
level=channel\n\
format=text\n\
nodata=404\n\
updatedafter=1900-01-01T00:00:00\n\
_NFOTABOO * * * 1900-01-01T00:00:00.0 2030-01-01T00:00:00.0\n\
_MOST * * * 1900-01-01T00:00:00.0 2030-01-01T00:00:00.0\n\
MN * * * 1900-01-01T00:00:00.0 2030-01-01T00:00:00.0",200,"\
#Network | Station | location | Channel | Latitude | Longitude | Elevation | Depth | Azimuth | Dip | SensorDescription | Scale | ScaleFreq | ScaleUnits | SampleRate | StartTime | EndTime\n\
IV|IMTC||HHE|40.7209|13.8758|59|0|90|0|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHN|40.7209|13.8758|59|0|0|0|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IV|IMTC||HHZ|40.7209|13.8758|59|0|0|-90|GURALP CMG-40T-60S|243822000|1|m/s|100|1988-01-01T00:00:00|\n\
IX|AND3|01|HNE|40.9298|15.3331|905|0|90|0|GURALP CMG-5T|949627|0.1|m/s**2|125|2013-12-17T00:00:00|\n\
IX|AND3|01|HNN|40.9298|15.3331|905|0|0|0|GURALP CMG-5T|949627|0.1|m/s**2|125|2013-12-17T00:00:00|\n\
IX|AND3|01|HNZ|40.9298|15.3331|905|0|0|-90|GURALP CMG-5T|949627|0.1|m/s**2|125|2013-12-17T00:00:00|\n\
IX|AND3|02|HHE|40.9298|15.3331|905|0|90|0|GEOTECH KS-2000EDU|3731340000|0.1|m/s|125|2013-12-17T00:00:00|\n\
IX|AND3|02|HHN|40.9298|15.3331|905|0|0|0|GEOTECH KS-2000EDU|3731340000|0.1|m/s|125|2013-12-17T00:00:00|\n\
IX|AND3|02|HHZ|40.9298|15.3331|905|0|0|-90|GEOTECH KS-2000EDU|3731340000|0.1|m/s|125|2013-12-17T00:00:00|\n\
MN|ARPR||BHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|20|2014-01-23T00:00:00|\n\
MN|ARPR||BHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|20|2014-01-23T00:00:00|\n\
MN|ARPR||BHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|20|2014-01-23T00:00:00|\n\
MN|ARPR||LHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|1|2014-01-23T00:00:00|\n\
MN|ARPR||LHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|1|2014-01-23T00:00:00|\n\
MN|ARPR||LHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|2516580000|0.02|m/s|1|2014-01-23T00:00:00|\n\
MN|ARPR||VHE|39.09289|38.33557|1537|0|90|0|STRECKEISEN STS-2-3G|10066300000|0.02|m/s|0.1|2014-01-23T00:00:00|\n\
MN|ARPR||VHN|39.09289|38.33557|1537|0|0|0|STRECKEISEN STS-2-3G|10066300000|0.02|m/s|0.1|2014-01-23T00:00:00|\n\
MN|ARPR||VHZ|39.09289|38.33557|1537|0|0|-90|STRECKEISEN STS-2-3G|10066300000|0.02|m/s|0.1|2014-01-23T00:00:00|\n\
","Two virtual, one FDSN networks"),


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
<FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.1</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query/?\n\
minlat=15\n\
maxlat=55\n\
level=station\n\
format=xml\n\
nodata=404\n\
* * * * 2009-01-01T00:00:00.0 2010-01-01T00:00:00.0\n\
MN * * * 1988-01-01T00:00:00.0 2002-01-01T00:00:00.0\n\
* ABSI * * 1990-01-01T00:00:00.0 2005-01-01T00:00:00.0</ModuleURI><Created>2021-02-20T08:56:56.344Z</Created><Network xmlns:css30="http://www.brtt.com/xml/station/css30" code="IT" startDate="1970-01-01T00:00:00" endDate="2599-12-31T23:59:59" css30:netType="-" restrictedStatus="open"><Description>Italian Strong Motion Network (RAN)</Description><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="CMA" startDate="2007-11-13T00:00:00" endDate="2599-12-31T23:59:59.999" css30:staType="-"><Latitude>39.414900</Latitude><Longitude>16.818000</Longitude><Elevation>610.000000</Elevation><Site><Name>Campana</Name></Site><Vault>-</Vault><CreationDate>2007-11-13T00:00:00</CreationDate></Station></Network><Network code="IV" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Italian Seismic Network</Description><Identifier type="DOI">10.13127/SD/X0FXnH7QfY</Identifier><ingv:Identifier>N1</ingv:Identifier><TotalNumberStations>7</TotalNumberStations><SelectedNumberStations>4</SelectedNumberStations><Station code="ACER" startDate="2007-07-05T12:00:00" restrictedStatus="open"><ingv:Identifier>S1</ingv:Identifier><Latitude>40.7867</Latitude><Longitude>15.9427</Longitude><Elevation>690</Elevation><Site><Name>Acerenza</Name></Site><CreationDate>2007-07-05T12:00:00</CreationDate></Station><Station code="ARVD" startDate="2003-03-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S9</ingv:Identifier><Latitude>43.49807</Latitude><Longitude>12.94153</Longitude><Elevation>461</Elevation><Site><Name>ARCEVIA 2</Name></Site><CreationDate>2003-03-01T00:00:00</CreationDate></Station><Station code="IMTC" startDate="1988-01-01T00:00:00" restrictedStatus="open"><ingv:AlternateNetworks><ingv:AlternateNetwork type="VIRTUAL" code="_MOST" startDate="2011-03-14T00:00:00"><Description>"Monitoring of Structures"</Description></ingv:AlternateNetwork></ingv:AlternateNetworks><ingv:Identifier>S3001</ingv:Identifier><Latitude>40.7209</Latitude><Longitude>13.8758</Longitude><Elevation>59</Elevation><Site><Name>Ischia - Monte Corvo</Name></Site><CreationDate>1988-01-01T00:00:00</CreationDate></Station><Station code="VBKN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S3031</ingv:Identifier><Latitude>40.83</Latitude><Longitude>14.4299</Longitude><Elevation>951</Elevation><Site><Name>Vesuvio - Bunker Nord</Name></Site><CreationDate>1988-01-01T00:00:00</CreationDate></Station></Network><Network code="MN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Mediterranean Very Broadband Seismographic Network</Description><Identifier type="DOI">10.13127/SD/fBBBtDtd6q</Identifier><ingv:Identifier>N22</ingv:Identifier><TotalNumberStations>2</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="AQU" startDate="1988-08-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S7</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Site><Name>L\'Aquila, Italy</Name></Site><CreationDate>1988-08-01T00:00:00</CreationDate></Station></Network><Network code="NI" startDate="2002-01-01T00:00:00" restrictedStatus="open"><Description>North-East Italy Broadband Network</Description><ingv:Identifier>N13</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="ACOM" startDate="2005-02-01T12:00:00" endDate="2015-12-31T23:59:59" restrictedStatus="open"><ingv:Identifier>S3451</ingv:Identifier><Latitude>46.548</Latitude><Longitude>13.5137</Longitude><Elevation>1788</Elevation><Site><Name>Acomizza</Name></Site><CreationDate>2005-02-01T12:00:00</CreationDate></Station></Network><Network code="SI" startDate="2006-01-01T00:00:00" restrictedStatus="open"><Description>Sudtirol Network, Italy</Description><Identifier type="citation">Pintore et al. Multiple Identifier</Identifier><Identifier type="DOI">https://doi.org/10.7914/SN/3T_2020</Identifier><ingv:Identifier>N18</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="ABSI" startDate="2006-11-21T14:16:45" restrictedStatus="open"><ingv:Identifier>S122</ingv:Identifier><Latitude>46.7285</Latitude><Longitude>11.3205</Longitude><Elevation>1801</Elevation><Site><Name>Aberstuckl (Sarntal)</Name></Site><CreationDate>2006-11-21T14:16:45</CreationDate></Station></Network></FDSNStationXML>',"POST 2"),

(
"minlat=15\n\
maxlat=55\n\
level=station\n\
format=xml\n\
nodata=404\n\
_MOST * * * 1988-01-01T00:00:00.0 2030-01-01T00:00:00.0",200,'<?xml version="1.0" encoding="UTF-8"?>\n\
<FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.3</Module><ModuleURI>"/exist/apps/fdsn-station/fdsnws/station/1/query/?\n\
minlat=0\n\
maxlat=55\n\
level=station\n\
format=xml\n\
nodata=404\n\
_MOST * * * 1900-01-01T00:00:00.0 2030-01-01T00:00:00.0"</ModuleURI><Created>2022-08-11T14:18:31.022Z</Created><Network code="IV" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Italian Seismic Network</Description><Identifier type="DOI">10.13127/SD/X0FXnH7QfY</Identifier><ingv:Identifier>N1</ingv:Identifier><TotalNumberStations>7</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="IMTC" startDate="1988-01-01T00:00:00" restrictedStatus="open"><ingv:AlternateNetworks><ingv:AlternateNetwork type="VIRTUAL" code="_MOST" startDate="2011-03-14T00:00:00"><Description>"Monitoring of Structures"</Description></ingv:AlternateNetwork></ingv:AlternateNetworks><ingv:Identifier>S3001</ingv:Identifier><Latitude>40.7209</Latitude><Longitude>13.8758</Longitude><Elevation>59</Elevation><Site><Name>Ischia - Monte Corvo</Name></Site><CreationDate>1988-01-01T00:00:00</CreationDate></Station></Network><Network code="IX" startDate="2005-01-01T00:00:00" restrictedStatus="open"><Description>Irpinia Seismic Network, Italy</Description><ingv:Identifier>N41</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="AND3" startDate="2013-12-17T00:00:00" restrictedStatus="open"><ingv:AlternateNetworks><ingv:AlternateNetwork type="VIRTUAL" code="_MOST" startDate="2011-03-14T00:00:00"><Description>"Monitoring of Structures"</Description></ingv:AlternateNetwork><ingv:AlternateNetwork type="VIRTUAL" code="_MOST-ICO" startDate="2011-03-14T00:00:00"><Description>"Monitoring of Structures in Central-Eastern Italy (Italia Centro Orientale)"</Description></ingv:AlternateNetwork><ingv:AlternateNetwork type="VIRTUAL" code="_NFOTABOO" startDate="2010-04-01T00:00:00"><Description>"The Altotiberina Near Fault Observatory (TABOO), Italy."</Description></ingv:AlternateNetwork></ingv:AlternateNetworks><ingv:Identifier>S6221</ingv:Identifier><Latitude>40.9298</Latitude><Longitude>15.3331</Longitude><Elevation>905</Elevation><Site><Name>Station Andretta, Italy</Name></Site><CreationDate>2013-12-17T00:00:00</CreationDate></Station></Network></FDSNStationXML>',"POST AlternateNetworks, only one virtual"),

(
"minlat=15\n\
maxlat=55\n\
level=station\n\
format=xml\n\
nodata=404\n\
_MOST * * * 1988-01-01T00:00:00.0 2030-01-01T00:00:00.0",200,'<?xml version="1.0" encoding="UTF-8"?>\n\
<FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.3</Module><ModuleURI>"/exist/apps/fdsn-station/fdsnws/station/1/query/?\n\
minlat=0\n\
maxlat=55\n\
level=station\n\
format=xml\n\
nodata=404\n\
matchtimeseries=false\n\
includeavailability=false\n\
_MOST * * * 1900-01-01T00:00:00.0 2030-01-01T00:00:00.0"</ModuleURI><Created>2022-08-11T14:18:31.022Z</Created><Network code="IV" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Italian Seismic Network</Description><Identifier type="DOI">10.13127/SD/X0FXnH7QfY</Identifier><ingv:Identifier>N1</ingv:Identifier><TotalNumberStations>7</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="IMTC" startDate="1988-01-01T00:00:00" restrictedStatus="open"><ingv:AlternateNetworks><ingv:AlternateNetwork type="VIRTUAL" code="_MOST" startDate="2011-03-14T00:00:00"><Description>"Monitoring of Structures"</Description></ingv:AlternateNetwork></ingv:AlternateNetworks><ingv:Identifier>S3001</ingv:Identifier><Latitude>40.7209</Latitude><Longitude>13.8758</Longitude><Elevation>59</Elevation><Site><Name>Ischia - Monte Corvo</Name></Site><CreationDate>1988-01-01T00:00:00</CreationDate></Station></Network><Network code="IX" startDate="2005-01-01T00:00:00" restrictedStatus="open"><Description>Irpinia Seismic Network, Italy</Description><ingv:Identifier>N41</ingv:Identifier><TotalNumberStations>1</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="AND3" startDate="2013-12-17T00:00:00" restrictedStatus="open"><ingv:AlternateNetworks><ingv:AlternateNetwork type="VIRTUAL" code="_MOST" startDate="2011-03-14T00:00:00"><Description>"Monitoring of Structures"</Description></ingv:AlternateNetwork><ingv:AlternateNetwork type="VIRTUAL" code="_MOST-ICO" startDate="2011-03-14T00:00:00"><Description>"Monitoring of Structures in Central-Eastern Italy (Italia Centro Orientale)"</Description></ingv:AlternateNetwork><ingv:AlternateNetwork type="VIRTUAL" code="_NFOTABOO" startDate="2010-04-01T00:00:00"><Description>"The Altotiberina Near Fault Observatory (TABOO), Italy."</Description></ingv:AlternateNetwork></ingv:AlternateNetworks><ingv:Identifier>S6221</ingv:Identifier><Latitude>40.9298</Latitude><Longitude>15.3331</Longitude><Elevation>905</Elevation><Site><Name>Station Andretta, Italy</Name></Site><CreationDate>2013-12-17T00:00:00</CreationDate></Station></Network></FDSNStationXML>',"POST AlternateNetworks, only one virtual, matchtimeseries and includeavailability false"),

(
"level=channel\n\
MN AQU -- BHE 2023-01-07T01:49:38.200000 2023-01-07T02:19:38.200000\n\
MN AQU -- BHN 2023-01-07T01:49:38.200000 2023-01-07T02:19:38.200000\n\
",200,'<?xml version="1.0" encoding="UTF-8"?>\n\
<FDSNStationXML xmlns="http://www.fdsn.org/xml/station/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Network code="MN" restrictedStatus="open" startDate="1988-01-01T00:00:00"><Description>Mediterranean Very Broadband Seismographic Network</Description><Identifier type="DOI">10.13127/SD/fBBBtDtd6q</Identifier><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">N22</ingv:Identifier><TotalNumberStations>2</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="AQU" restrictedStatus="open" startDate="1988-08-01T00:00:00"><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">S7</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Site><Name>L\'Aquila, Italy</Name></Site><CreationDate>1988-08-01T00:00:00</CreationDate><TotalNumberChannels>151</TotalNumberChannels><SelectedNumberChannels>2</SelectedNumberChannels><Channel code="BHE" locationCode="" restrictedStatus="open" startDate="2019-03-01T00:00:00"><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">C82391</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel><Channel code="BHN" locationCode="" restrictedStatus="open" startDate="2019-03-01T00:00:00"><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">C82311</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity></Response></Channel></Station></Network></FDSNStationXML>',"POST same station in two lines"),

(
"level=response\n\
MN AQU -- BHE 2023-01-07T01:49:38.200000 2023-01-07T02:19:38.200000\n\
MN AQU -- BHN 2023-01-07T01:49:38.200000 2023-01-07T02:19:38.200000\n\
",200,'<?xml version="1.0" encoding="UTF-8"?>\n\
<FDSNStationXML xmlns="http://www.fdsn.org/xml/station/1" xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Network code="MN" restrictedStatus="open" startDate="1988-01-01T00:00:00"><Description>Mediterranean Very Broadband Seismographic Network</Description><Identifier type="DOI">10.13127/SD/fBBBtDtd6q</Identifier><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">N22</ingv:Identifier><TotalNumberStations>2</TotalNumberStations><SelectedNumberStations>1</SelectedNumberStations><Station code="AQU" restrictedStatus="open" startDate="1988-08-01T00:00:00"><ingv:Identifier xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">S7</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Site><Name>L\'Aquila, Italy</Name></Site><CreationDate>1988-08-01T00:00:00</CreationDate><TotalNumberChannels>151</TotalNumberChannels><SelectedNumberChannels>2</SelectedNumberChannels><Channel code="BHE" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82391</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>90</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity><Stage number="1"><PolesZeros><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>V</Name></OutputUnits><PzTransferFunctionType>LAPLACE (RADIANS/SECOND)</PzTransferFunctionType><NormalizationFactor>59680600</NormalizationFactor><NormalizationFrequency>0.02</NormalizationFrequency><Zero number="0"><Real>0</Real><Imaginary>0</Imaginary></Zero><Zero number="1"><Real>0</Real><Imaginary>0</Imaginary></Zero><Pole number="0"><Real>-0.035647</Real><Imaginary>-0.036879</Imaginary></Pole><Pole number="1"><Real>-0.035647</Real><Imaginary>0.036879</Imaginary></Pole><Pole number="2"><Real>-251.33</Real><Imaginary>0</Imaginary></Pole><Pole number="3"><Real>-131.04</Real><Imaginary>-467.29</Imaginary></Pole><Pole number="4"><Real>-131.04</Real><Imaginary>467.29</Imaginary></Pole></PolesZeros><StageGain><Value>1500</Value><Frequency>0.02</Frequency></StageGain></Stage><Stage number="2"><Coefficients><InputUnits><Name>V</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType></Coefficients><Decimation><InputSampleRate>100</InputSampleRate><Factor>1</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>419430</Value><Frequency>0</Frequency></StageGain></Stage><Stage number="3"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType></Coefficients><Decimation><InputSampleRate>100</InputSampleRate><Factor>1</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0</Frequency></StageGain></Stage><Stage number="4"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType></Coefficients><Decimation><InputSampleRate>20</InputSampleRate><Factor>1</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0</Frequency></StageGain></Stage><Stage number="5"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>-5.42954E-11</Numerator><Numerator>1.25712E-9</Numerator><Numerator>-1.06384E-8</Numerator><Numerator>-2.83336E-7</Numerator><Numerator>1.52435E-6</Numerator><Numerator>-1.25273E-6</Numerator><Numerator>6.80795E-7</Numerator><Numerator>8.14909E-7</Numerator><Numerator>-1.41985E-6</Numerator><Numerator>1.57736E-5</Numerator><Numerator>-5.568E-5</Numerator><Numerator>-0.000565037</Numerator><Numerator>0.0005027</Numerator><Numerator>-0.000451897</Numerator><Numerator>7.67719E-5</Numerator><Numerator>0.000715218</Numerator><Numerator>-0.00192052</Numerator><Numerator>0.00338213</Numerator><Numerator>-0.0047611</Numerator><Numerator>0.00556131</Numerator><Numerator>-0.0051932</Numerator><Numerator>0.00309797</Numerator><Numerator>0.00109645</Numerator><Numerator>-0.00740398</Numerator><Numerator>0.0153211</Numerator><Numerator>-0.0235259</Numerator><Numerator>0.0310842</Numerator><Numerator>-0.0385687</Numerator><Numerator>0.0361532</Numerator><Numerator>-0.0266714</Numerator><Numerator>0.00314168</Numerator><Numerator>0.0442574</Numerator><Numerator>-0.156905</Numerator><Numerator>0.724167</Numerator><Numerator>0.527652</Numerator><Numerator>-0.191755</Numerator><Numerator>0.0964923</Numerator><Numerator>-0.0447787</Numerator><Numerator>0.0117525</Numerator><Numerator>0.00860734</Numerator><Numerator>-0.0220986</Numerator><Numerator>0.0240398</Numerator><Numerator>-0.0229704</Numerator><Numerator>0.0191765</Numerator><Numerator>-0.0135815</Numerator><Numerator>0.00777805</Numerator><Numerator>-0.00280512</Numerator><Numerator>-0.000771971</Numerator><Numerator>0.00281441</Numerator><Numerator>-0.00350639</Numerator><Numerator>0.00322534</Numerator><Numerator>-0.00240627</Numerator><Numerator>0.00144175</Numerator><Numerator>-0.000608222</Numerator><Numerator>4.63258E-5</Numerator><Numerator>0.000210677</Numerator><Numerator>-0.000517759</Numerator><Numerator>7.47336E-6</Numerator><Numerator>5.41172E-6</Numerator><Numerator>-3.74403E-6</Numerator><Numerator>2.78747E-6</Numerator><Numerator>-3.37274E-7</Numerator><Numerator>-1.87594E-7</Numerator><Numerator>1.14502E-6</Numerator><Numerator>-4.2706E-7</Numerator><Numerator>3.67488E-8</Numerator><Numerator>-3.65342E-17</Numerator></Coefficients><Decimation><InputSampleRate>20</InputSampleRate><Factor>1</Factor><Offset>0</Offset><Delay>1.6305</Delay><Correction>1.6305</Correction></Decimation><StageGain><Value>1</Value><Frequency>0</Frequency></StageGain></Stage></Response></Channel><Channel code="BHN" startDate="2019-03-01T00:00:00" restrictedStatus="open" locationCode=""><ingv:Identifier>C82311</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Depth>0</Depth><Azimuth>0</Azimuth><Dip>0</Dip><SampleRate>20</SampleRate><ClockDrift>0</ClockDrift><Sensor><Description>STRECKEISEN STS-2-120S</Description></Sensor><Response><InstrumentSensitivity><Value>629145000</Value><Frequency>0.02</Frequency><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits></InstrumentSensitivity><Stage number="1"><PolesZeros><InputUnits><Name>m/s</Name></InputUnits><OutputUnits><Name>V</Name></OutputUnits><PzTransferFunctionType>LAPLACE (RADIANS/SECOND)</PzTransferFunctionType><NormalizationFactor>59680600</NormalizationFactor><NormalizationFrequency>0.02</NormalizationFrequency><Zero number="0"><Real>0</Real><Imaginary>0</Imaginary></Zero><Zero number="1"><Real>0</Real><Imaginary>0</Imaginary></Zero><Pole number="0"><Real>-0.035647</Real><Imaginary>-0.036879</Imaginary></Pole><Pole number="1"><Real>-0.035647</Real><Imaginary>0.036879</Imaginary></Pole><Pole number="2"><Real>-251.33</Real><Imaginary>0</Imaginary></Pole><Pole number="3"><Real>-131.04</Real><Imaginary>-467.29</Imaginary></Pole><Pole number="4"><Real>-131.04</Real><Imaginary>467.29</Imaginary></Pole></PolesZeros><StageGain><Value>1500</Value><Frequency>0.02</Frequency></StageGain></Stage><Stage number="2"><Coefficients><InputUnits><Name>V</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType></Coefficients><Decimation><InputSampleRate>100</InputSampleRate><Factor>1</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>419430</Value><Frequency>0</Frequency></StageGain></Stage><Stage number="3"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType></Coefficients><Decimation><InputSampleRate>100</InputSampleRate><Factor>1</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0</Frequency></StageGain></Stage><Stage number="4"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType></Coefficients><Decimation><InputSampleRate>20</InputSampleRate><Factor>1</Factor><Offset>0</Offset><Delay>0</Delay><Correction>0</Correction></Decimation><StageGain><Value>1</Value><Frequency>0</Frequency></StageGain></Stage><Stage number="5"><Coefficients><InputUnits><Name>count</Name></InputUnits><OutputUnits><Name>count</Name></OutputUnits><CfTransferFunctionType>DIGITAL</CfTransferFunctionType><Numerator>-5.42954E-11</Numerator><Numerator>1.25712E-9</Numerator><Numerator>-1.06384E-8</Numerator><Numerator>-2.83336E-7</Numerator><Numerator>1.52435E-6</Numerator><Numerator>-1.25273E-6</Numerator><Numerator>6.80795E-7</Numerator><Numerator>8.14909E-7</Numerator><Numerator>-1.41985E-6</Numerator><Numerator>1.57736E-5</Numerator><Numerator>-5.568E-5</Numerator><Numerator>-0.000565037</Numerator><Numerator>0.0005027</Numerator><Numerator>-0.000451897</Numerator><Numerator>7.67719E-5</Numerator><Numerator>0.000715218</Numerator><Numerator>-0.00192052</Numerator><Numerator>0.00338213</Numerator><Numerator>-0.0047611</Numerator><Numerator>0.00556131</Numerator><Numerator>-0.0051932</Numerator><Numerator>0.00309797</Numerator><Numerator>0.00109645</Numerator><Numerator>-0.00740398</Numerator><Numerator>0.0153211</Numerator><Numerator>-0.0235259</Numerator><Numerator>0.0310842</Numerator><Numerator>-0.0385687</Numerator><Numerator>0.0361532</Numerator><Numerator>-0.0266714</Numerator><Numerator>0.00314168</Numerator><Numerator>0.0442574</Numerator><Numerator>-0.156905</Numerator><Numerator>0.724167</Numerator><Numerator>0.527652</Numerator><Numerator>-0.191755</Numerator><Numerator>0.0964923</Numerator><Numerator>-0.0447787</Numerator><Numerator>0.0117525</Numerator><Numerator>0.00860734</Numerator><Numerator>-0.0220986</Numerator><Numerator>0.0240398</Numerator><Numerator>-0.0229704</Numerator><Numerator>0.0191765</Numerator><Numerator>-0.0135815</Numerator><Numerator>0.00777805</Numerator><Numerator>-0.00280512</Numerator><Numerator>-0.000771971</Numerator><Numerator>0.00281441</Numerator><Numerator>-0.00350639</Numerator><Numerator>0.00322534</Numerator><Numerator>-0.00240627</Numerator><Numerator>0.00144175</Numerator><Numerator>-0.000608222</Numerator><Numerator>4.63258E-5</Numerator><Numerator>0.000210677</Numerator><Numerator>-0.000517759</Numerator><Numerator>7.47336E-6</Numerator><Numerator>5.41172E-6</Numerator><Numerator>-3.74403E-6</Numerator><Numerator>2.78747E-6</Numerator><Numerator>-3.37274E-7</Numerator><Numerator>-1.87594E-7</Numerator><Numerator>1.14502E-6</Numerator><Numerator>-4.2706E-7</Numerator><Numerator>3.67488E-8</Numerator><Numerator>-3.65342E-17</Numerator></Coefficients><Decimation><InputSampleRate>20</InputSampleRate><Factor>1</Factor><Offset>0</Offset><Delay>1.6305</Delay><Correction>1.6305</Correction></Decimation><StageGain><Value>1</Value><Frequency>0</Frequency></StageGain></Stage></Response></Channel></Station></Network></FDSNStationXML>',"POST response level"),

]

testdataerrors =[
("level=channel&net=MN&cha=SHZ&station=AQU&format=text&maxlatitude=45&minlat=42&nodata=404",404,
"Error 404 - no matching inventory found\n\
\n\
Usage details are available from /fdsnws/station/1/\n\
\n\
Request:\n\
\n\
/fdsnws/station/1/query?level=channel&net=MN&cha=SHZ&station=AQU&format=text&maxlatitude=45&minlat=42&nodata=404\n\
\n\
Request Submitted:","nodata text"),

("level=channel&net=MN&cha=SHZ&station=AQU&format=xml&maxlatitude=45&minlat=42&nodata=404",404,
"Error 404 - no matching inventory found\n\
\n\
Usage details are available from /fdsnws/station/1/\n\
\n\
Request:\n\
\n\
/fdsnws/station/1/query?level=channel&net=MN&cha=SHZ&station=AQU&format=xml&maxlatitude=45&minlat=42&nodata=404\n\
\n\
Request Submitted:","nodata xml"),

("level=channel&net=MN&cha=SHZ&station=AQU&format=json&maxlatitude=45&minlat=42&nodata=404",404,
"Error 404 - no matching inventory found\n\
\n\
Usage details are available from /fdsnws/station/1/\n\
\n\
Request:\n\
\n\
/fdsnws/station/1/query?level=channel&net=MN&cha=SHZ&station=AQU&format=json&maxlatitude=45&minlat=42&nodata=404\n\
\n\
Request Submitted:","nodata xml"),

("level=channel&net=&sta=ACER&loc=??&format=json&maxlatitude=45&minlat=42&nodata=404",400,
"Error 400: Bad request\n\
\n\
Syntax Error in Request\n\
\n\
\n\
Check network parameter","empty network parameter"),

("level=channel&net=*&sta=&loc=*&format=json&maxlatitude=45&minlat=42&nodata=404",400,
"Error 400: Bad request\n\
\n\
Syntax Error in Request\n\
\n\
\n\
Check station parameter","empty station parameter"),

("level=channel&net=*&cha=&loc=??&format=json&maxlatitude=45&minlat=42&nodata=404",400,
"Error 400: Bad request\n\
\n\
Syntax Error in Request\n\
\n\
\n\
Check channel parameter","empty channelparameter"),

("level=channel&net=*&sta=ACER&loc=&format=json&maxlatitude=45&minlat=42&nodata=404",400,
"Error 400: Bad request\n\
\n\
Syntax Error in Request\n\
\n\
\n\
Check location parameter","empty location"),

("level=channel&net=*&sta=ACER&format=json&maxlatitude=45&minlat=42&nodata=404&matchtimeseries=true",400,
"Error 400: Bad request\n\
\n\
Syntax Error in Request\n\
\n\
\n\
Including of availability information not supported.\n\
\n\
\n\
Usage details are available from /fdsnws/station/1/\n\
\n\
Request:","matchtimeseries is not supported"),

("level=channel&net=*&sta=ACER&format=json&maxlatitude=45&minlat=42&nodata=404&includeavailability=true",400,
"Error 400: Bad request\n\
\n\
Syntax Error in Request\n\
\n\
\n\
Filtering based on available time series not supported.\n\
\n\
\n\
Usage details are available from /fdsnws/station/1/\n\
\n\
Request:","includeavailability is not supported"),

("format=text&nodata=404&station=ACER&station=ACATE",400,
"Error 400: Bad request\n\n\
Syntax Error in Request\n\n\
Usage details are available from /fdsnws/station/1/"
,"Multiplicity in parameter"),

("format=text&nodata=404&station=ACER&sta=ACATE",400,
"Error 400: Bad request\n\n\
Syntax Error in Request\n\n\
Usage details are available from /fdsnws/station/1/"
,"Alias abuse on station"),

("format=text&nodata=404&network=IV&net=MN",400,
"Error 400: Bad request\n\n\
Syntax Error in Request\n\n\
Usage details are available from /fdsnws/station/1/"
,"Alias abuse on network"),

("format=text&nodata=404&lat=42&longitude=12&minradius=10&minradiuskm=200",400,
"Error 400: Bad request\n\n\
Syntax Error in Request\n\n\
Usage details are available from /fdsnws/station/1/"
,"Alias abuse on minradius")


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
Usage details are available from /fdsnws/station/1/\n\
\n\
Request:\n\
\n\
","nodata on post format text "),


(
"minlat=10\n\
maxlat=62\n\
level=station\n\
format=text\n\
nodata=404\n\
updatedafter=2100-01-01T00:00:00\n\
matchtimeseries=true\n\
* * * * 1920-01-01T00:00:00.0 2020-01-01T00:00:00.0",400,
"Error 400: Bad request\n\
\n\
Syntax Error in Request\n\
\n\
\n\
Including of availability information not supported.\n\
\n\
\n\
Usage details are available from /fdsnws/station/1/\n\
\n\
Request:","Error 400 matchtimeseries not supported"),

(
"minlat=10\n\
maxlat=62\n\
maxlatitude=63\n\
level=station\n\
format=text\n\
nodata=404\n\
updatedafter=2000-01-01T00:00:00\n\
* * * * 1920-01-01T00:00:00.0 2020-01-01T00:00:00.0",400,
"Error 400: Bad request\n\n\
Syntax Error in Request","Error 400 alias abuse in POST"),

(
"lat=10\n\
lon=62\n\
maxradius=10\n\
maxradiuskm=5\n\
level=station\n\
format=text\n\
nodata=404\n\
updatedafter=2000-01-01T00:00:00\n\
* * * * 1920-01-01T00:00:00.0 2020-01-01T00:00:00.0",400,
"Error 400: Bad request\n\n\
Syntax Error in Request","Error 400 quasi-alias abuse in POST"),

(
"minlat=10\n\
minlat=62\n\
maxlatitude=63\n\
level=station\n\
format=text\n\
nodata=404\n\
updatedafter=2000-01-01T00:00:00\n\
* * * * 1920-01-01T00:00:00.0 2020-01-01T00:00:00.0",400,
"Error 400: Bad request\n\n\
Syntax Error in Request","Error 400 duplicate params in POST"),


(
"level=channel\n\
includerestricted=false\n\
nodata=404\n\
AC PHP * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
AC PUK * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
AC LSK * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
AC SRN * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU BHB * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
AC VLO * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU BLANC * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU BURY * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU CANO * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU CARD * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU CIRO * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU ENR * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU EQUI * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU GORR * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU GBOS * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU ZORR * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00",404, "\
Error 404 - no matching inventory found\n\
\n\
Usage details are available from /fdsnws/station/1/\n\
\n\
Request:\n\
\n\
","nodata on post format text "),

(
"level=channel\n\
includerestricted=false\n\
nodata=404\n\
AC BCI * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
AC KBN * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
AC PHP * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
AC PUK * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
AC LSK * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
AC SRN * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU BHB * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
AC VLO * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU BKB * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
AC VLOS * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU BLANC * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU BURY * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU CANO * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU CARD * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU CIRO * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU ENR * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU EQUI * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU GORR * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU GBOS * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU STOS * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU EQUA * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU GOR * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU GBO * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU STO * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00\n\
GU ZORR * BHZ,HHZ 2021-01-01T00:00:00 2021-12-31T00:00:00",404, "\
Error 404 - no matching inventory found\n\
\n\
Usage details are available from /fdsnws/station/1/\n\
\n\
Request:\n\
\n\
","nodata on post format text too long"),

]


testendpoints = [
("/exist/apps/fdsn-station/virtualnetwork/1/codes",200,
'<?xml version="1.0" encoding="UTF-8"?>\n\
<ingv:AlternateNetworks xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd"><ingv:AlternateNetwork type="VIRTUAL" code="_MOST" startDate="2011-03-14T00:00:00"><Description xmlns="http://www.fdsn.org/xml/station/1">"Monitoring of Structures"</Description></ingv:AlternateNetwork>\
<ingv:AlternateNetwork type="VIRTUAL" code="_MOST-ICO" startDate="2011-03-14T00:00:00"><Description xmlns="http://www.fdsn.org/xml/station/1">"Monitoring of Structures in Central-Eastern Italy (Italia Centro Orientale)"</Description></ingv:AlternateNetwork>\
<ingv:AlternateNetwork type="VIRTUAL" code="_NFOTABOO" startDate="2010-04-01T00:00:00"><Description xmlns="http://www.fdsn.org/xml/station/1">"The Altotiberina Near Fault Observatory (TABOO), Italy."</Description></ingv:AlternateNetwork></ingv:AlternateNetworks>',"list of virtualnetworks ","matches"),

("/exist/apps/fdsn-station/fdsnws/station/1/application.wadl",200,
'<application xmlns="http://wadl.dev.java.net/2009/02" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n\
  <doc title="INGV FDSNWS station Web Service Documentation" xml:lang="en">\n\
    <div>\n\
    The fdsnws/station web service returns station metadata in <a href="http://www.fdsn.org/xml/station/">FDSN StationXML</a> format or as delimited text.',
"application.wadl","startswith"),

("/exist/apps/fdsn-station/fdsnws/station/1/swagger.json",200,
'{\n\
  "openapi": "3.0.1",\n\
  "info": {\n\
    "title": "INGV FDSNWS station Web Service Documentation",',
"swagger.json","startswith"),

("/exist/rest/apps",403,
'<html>\n\
<head>\n\
<meta http-equiv="Content-Type" ',"REST interface closed","startswith"),

("/exist/apps/fdsn-station/fdsnws/station/1/query/version/a=1&b=2",400,
'Error 400: Bad request\n\
\n\
Syntax Error in Request\n\
\n\
Usage details are available from /fdsnws/station/1/\n\
\n\
Request:\n\
\n\
failure parsing request',"Intercept Jetty Error 500 parsing parameters in bad paths err:XPST0003 Invalid character (=) in entity name","startswith"),

("/exist/apps/fdsn-station/fdsnws/station/1/querry",400,
'Error 400: Bad request\n\
\n\
Syntax Error in Request\n\
\n\
Usage details are available from /fdsnws/station/1/\n\
\n\
Request:\n\
\n',"Intercept Error XPTY0004: The actual cardinality for parameter 1 does not match the cardinality","startswith"),

("/exist/apps/fdsn-station/fdsnws/station/1/",200,
'<html xmlns="http://www.w3.org/1999/xhtml" ',
"application entry point translated by xslt","startswith"),

]

#A319A.xml  ABSI.xml  ACATE.xml  ACER.xml  ACOM.xml  AND3.xml  AQT1.xml  AQU.xml  ARPR.xml  ARVD.xml  IMTC.xml  VBKN.xml
testdataio = [

(
"provider=INGV&net=*","TEST/data/Station/",200,
'',
"DELETE_MULTI" , "DELETE ALL INGV station present in DB [NetCache]"),

(
"FAKE","TEST/data/Station/",204,
'',
"DELETE_MULTI" , "DELETE ALL FAKE station present in DB [NetCache]"),

(
"INGV_A319A.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT A319A station"),

(
"provider=INGV&net=IV","TEST/data/Station/",204,
'',
"DELETE_MULTI" , "DELETE ALL INGV IV station present in DB (NONE)"),

(
"INGV_A319A.xml","TEST/data/Station/",200,
'',
"DELETE" , "DELETE A319A station present in DB [NetCache]"),


(
"INGV_A319A.xml","TEST/data/Station/",204,
'',
"DELETE" , "DELETE A319A station from empty DB [NetCache]"),

(
"INGV_A319A.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT A319A station"),


(
"INGV_A319A.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT A319A station again [NetCache]"),

(
"INGV_ABSI.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT ABSI station"),

(
"INGV_ACATE.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT ACATE station"),

(
"INGV_ACER.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT ACER station"),

(
"INGV_ACOM.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT ACOM station NI,OX networks [NetCache]" ),

(
"INGV_ACOM.xml","TEST/data/Station/",200,
'',
"DELETE" , "DELETE ACOM station NI,OX networks [NetCache]"),

(
"INGV_ACOM.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT ACOM station NI,OX networks [NetCache]"),


(
"INGV_ACOM.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT ACOM station, NI,OX networks, again. [NetCache]"),

(
"INGV_AND3.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT AND3 station"),

(
"INGV_AQT1.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT AQT1 station"),

(
"INGV_AQU.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT AQU station"),

(
"INGV_ARPR.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT ARPR station"),

(
"INGV_ARVD.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT ARVD station"),

(
"INGV_IMTC.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT IMTC station"),

(
"INGV_VBKN.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT VBKN station"),

(
"INGV_AT04.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT (INGV) AT04 station"),

(
"INGV_VBKN.xml","TEST/data/Station/",200,
'',
"DELETE" , "DELETE VBKN station. [NetCache update #78]"),

(
"INGV_ACER.xml","TEST/data/Station/",200,
'',
"DELETE" , "DELETE ACER station. [NetCache update #78]"),

(
"INGV_AQT1.xml","TEST/data/Station/",200,
'',
"DELETE" , "DELETE AQT1 station. [NetCache update #78]"),

(
"INGV_VBKN.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT VBKN station. [NetCache update #78]"),

(
"INGV_ACER.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT ACER station. [NetCache update #78]"),

(
"INGV_AQT1.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT AQT1 station. [NetCache update #78]"),



(
"GFZ_AT04.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT (GFZ) AT04 station"),

(
"ETH_ELFMC.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT (ETH) ELFMC station"),

(
"RAN_CMA.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT (RAN) CMA station"),

(
"BGR_ABG1.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT (BGR) ABG1 station"),

(
"BGR_ANNA.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT (BGR) ANNA station"),

#Place some stations with buggy net
(
"INGV_ACER.xml","TEST/data/Fake/",200,
'',
"PUT" , "PUT ACER station, fake net"),

#Stations with duplicate network
(
"INGV_IMTC.xml","TEST/data/Fake/",409,
'',
"PUT" , "PUT IMTC station, fail for conflicting network"),

(
"INGV_ARVD.xml","TEST/data/Fake/",200,
'',
"PUT" , "PUT ARVD station, fake net"),

#Overwrite buggy stations
(
"INGV_ACER.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT ACER station, fake net"),

(
"INGV_ARVD.xml","TEST/data/Station/",200,
'',
"PUT" , "PUT ARVD station, fake net"),

#Delete the buggy stations must fail
(
"provider=INGV&net=IY","TEST/data/Station/",204,
'',
"DELETE_MULTI" , "DELETE Fake station must fail "),

]



test_management = [
(
'code=IV&startDate=1988-01-01T00:00:01', 'TEST/data/Fake/INGV_NET_002.xml', 204, '',
'PUT',
"No matching network in DB"),

(
'code=MN&startDate=1988-01-01T00:00:00', 'TEST/data/Fake/INGV_NET_001.xml', 400, '',
'PUT',
"Parameters and file content mismatch"),

(
'code=IV&startDate=1988-01-01T00:00:00','TEST/data/Fake/INGV_NET_001.xml',200, '',
'PUT',
"Change elements in IV network"),

(
'format=xml&net=IV&level=network',
'',200,
'<?xml version="1.0" encoding="UTF-8"?>\n\
<FDSNStationXML xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd"><Source>eXistDB</Source><Sender>INGV-ONT</Sender><Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.60</Module><ModuleURI>/exist/apps/fdsn-station/fdsnws/station/1/query?format=xml&amp;net=IV&amp;level=network</ModuleURI><Created>2024-04-02T09:26:02.345</Created><Network code="IV" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Italian Seismic Network</Description><Identifier type="DOI">10.13127/CHANGED/X0FXnH7QfY</Identifier><Identifier type="NONE">ID_OF_NONE_TYPE</Identifier><Comment>La rete integrata</Comment><TotalNumberStations>7</TotalNumberStations><SelectedNumberStations>7</SelectedNumberStations></Network></FDSNStationXML>',
'GETXML',
"Look for changed elements in IV network"),

(
'format=text&net=Z3&includerestricted=false', 'TEST/data/Fake/INGV_NET_003.xml', 200,
'#Network | Station | Latitude | Longitude | Elevation | SiteName | StartTime | EndTime\n\
Z3|AT04|37.7252|24.0496|23|Station Egelados Network, GreeceGreece|2005-11-02T00:00:00|2007-02-23T00:00:00\n',
'GETTEXT',
"Verifying restrictedStatus for A319A"),

(
'code=Z3&startDate=2015-01-01T00:00:00', 'TEST/data/Fake/INGV_NET_003.xml', 200, '',
'PUT',
"Opening restrictedStatus previously closed"),

(
'format=text&net=Z3&includerestricted=false', 'TEST/data/Fake/INGV_NET_003.xml', 200,
'#Network | Station | Latitude | Longitude | Elevation | SiteName | StartTime | EndTime\n\
Z3|AT04|37.7252|24.0496|23|Station Egelados Network, GreeceGreece|2005-11-02T00:00:00|2007-02-23T00:00:00\n\
Z3|A319A|43.476425|10.578689|343|Santa Luce (PI)|2015-12-11T12:06:34|2019-04-10T23:59:00\n',
'GETTEXT',
"Verifying restrictedStatus previously closed"),


]

############################################# END DATA FOR TEST #############################################


#############################################################################################################

@pytest.mark.parametrize(
    "name,path,expected_status_code,expected_content,action,comment", testdataio
)

def test_io(name,path,expected_status_code,expected_content,action,comment,host):

    webservicepath="http://"+host+"/exist/apps/fdsn-station/fdsnws/station/1/query?"
    #filename="TEST/data/Station/"+ name
    filename = path + name
    #files = {'file' : (filename, open(filename, 'rb'), 'application/xml')}
    if action == 'PUT':
        print("Inserting: " + name + " in " + webservicepath)
        response = requests.put(url=webservicepath, data=open(filename, 'rb'), headers={"Content-Type": "application/octet-stream", "filename": name}, auth=HTTPBasicAuth('fdsn', 'fdsn'))
    elif action == 'DELETE':
        print("Deleting: " + name + " in " + webservicepath)
        response = requests.delete(url=webservicepath, headers={"filename" : name}, auth=HTTPBasicAuth('fdsn', 'fdsn'))
    elif action == 'DELETE_MULTI':
        print("Deleting: " + name + " in " + webservicepath)
        response = requests.delete(url=webservicepath+name, auth=HTTPBasicAuth('fdsn', 'fdsn'))

    print("***Expected**")
    print(expected_content)
    print("+++Response+++")
    print(response.text)
    print("-----")

    #print(main.diff_texts(ET.tostring(response_tree, encoding=None, method='c14n2'),ET.tostring(expected_content_tree, encoding=None, method='c14n2')))
    #print(ET.canonicalize(response_tree))
    assert response.status_code == expected_status_code

#############################################################################################################



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
    response = requests.get( "http://"+host+"/exist/apps/fdsn-station/fdsnws/station/1/query?" + query)
    assert (response.status_code == expected_status_code)
    assert (response.text == expected_content)

############################################################################################################



#############################################################################################################

@pytest.mark.parametrize(
    "query,expected_status_code,expected_content,comment", testdataerrors

)

def test_errors(query,expected_status_code,expected_content,comment,host):
    response = requests.get( "http://"+host+"/exist/apps/fdsn-station/fdsnws/station/1/query?" + query)
    assert (response.status_code == expected_status_code)
#Next assert check for the same string or for the first part if differences in tail
    assert (response.text.startswith(expected_content))

############################################################################################################

#############################################################################################################

@pytest.mark.parametrize(
    "post_data,expected_status_code,expected_content,comment,version", testdatapostobspy

)

def test_post_obspy(post_data,expected_status_code,expected_content,comment,version,host):

    if version == "1.3.0":
        resp = requests.post("http://" + host + "/exist/apps/fdsn-station/fdsnws/station/1/query?", data=post_data,
                             headers={"Content-Type" : "application/x-www-form-urlencoded", "User-Agent" : "ObsPy/1.3.0"})
    else:
        resp = requests.post("http://" + host + "/exist/apps/fdsn-station/fdsnws/station/1/query?", data=post_data,
                          headers={"Content-Type" : "text/plain", "User-Agent" : "ObsPy/1.4.0"})

    assert (resp.status_code == expected_status_code)
    assert (resp.text == expected_content)

############################################################################################################

#############################################################################################################

@pytest.mark.parametrize(
    "post_data,expected_status_code,expected_content,comment", testdatapost

)

def test_post(post_data,expected_status_code,expected_content,comment,host):
    response = requests.post( "http://"+host+"/exist/apps/fdsn-station/fdsnws/station/1/query?",data=post_data, headers={"Content-Type":"application/octet-stream"} )

    assert (response.status_code == expected_status_code)
    assert (response.text == expected_content)


############################################################################################################


#############################################################################################################

@pytest.mark.parametrize(
    "post_data,expected_status_code,expected_content,comment", testdataposterrors

)

def test_post_errors(post_data,expected_status_code,expected_content,comment,host):
    response = requests.post( "http://"+host+"/exist/apps/fdsn-station/fdsnws/station/1/query?",data=post_data, headers={"Content-Type":"application/octet-stream"} )
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
    response = requests.post( "http://"+host+"/exist/apps/fdsn-station/fdsnws/station/1/query?",data=post_data, headers={"Content-Type":"application/octet-stream","Encoding":"utf-8"} )

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



#############################################################################################################

@pytest.mark.parametrize(
    "query,expected_status_code,expected_content,comment,match", testendpoints

)

def test_endpoint(query,expected_status_code,expected_content,comment,match,host):
    response = requests.get( "http://"+host + query)

    print("***Expected***")
    print(expected_content)
    print("+++Response+++")
    print(response.text)

    assert (response.status_code == expected_status_code)
    if match=='matches':
        assert (response.text == expected_content)
    elif match=='startswith':
        assert (response.text.startswith(expected_content))

############################################################################################################



#############################################################################################################

@pytest.mark.parametrize(
    "query,path,expected_status_code,expected_content,action,comment", test_management
)

def test_management(query,path,expected_status_code,expected_content,action,comment,host):

    if action == 'PUT':
        webservicepath = "http://" + host + "/exist/apps/fdsn-station/fdsnws/station/1/management/network?" + query
        filename = path
        print("Applying: " + query + " -> " + webservicepath)
        response = requests.put(url=webservicepath, data=open(filename, 'rb'), headers={"Content-Type":"application/octet-stream"}, auth=HTTPBasicAuth('fdsn', 'fdsn'))
    if action == 'GETTEXT':
        test_content(query,expected_status_code,expected_content,comment,host)
    if action == 'GETXML':
        test_eval(query, expected_status_code, expected_content, comment, host)
    if action == 'PUT':
        assert response.status_code == expected_status_code

#############################################################################################################


#### BEWARE TEST ON MINRADIUSKM DISPLAY NO CONTROL ON TEXT SORTING. ####
#### TODO FIX SORTING AND CHANGE TEST ACCORDINLGY                   ####
