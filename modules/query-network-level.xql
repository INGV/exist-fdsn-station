xquery version "3.1";

declare default element namespace "http://www.fdsn.org/xml/station/1" ;
declare namespace ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";

import module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil"  at "util.xql";
(:import module namespace errors="http://exist-db.org/apps/fdsn-station/modules/stationutil"  at "errors.xql";:)

declare namespace request="http://exist-db.org/xquery/request";
declare namespace output = "http://www.w3.org/2010/xslt-xquery-serialization";
(:declare option output:method "xml";:)
(:declare option output:media-type "text/xml";:)
(:declare option exist:serialize "method=xml media-type=text/html";:)
(:TODO uncomment after debug:)
declare option output:indent "yes";

declare function local:main() as element() {
    
if (stationutil:check_parameters_limits()) then 
    if (stationutil:channel_exists()) then 
<FDSNStationXML xmlns="http://www.fdsn.org/xml/station/1" xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" schemaVersion="1.0" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.0.xsd">
  <TEST>{matches("HHZ",stationutil:channel_pattern_translate(request:get-parameter("channel", "")))}</TEST> 
  <TEST>c_p_t: {stationutil:channel_pattern_translate(request:get-parameter("channel", ""))}</TEST>   
  <TEST>channel exists {stationutil:channel_exists()}</TEST> 
  <TEST>tokenize example {tokenize("HHZ",",")}</TEST>
  <TEST>maxlatitude {xs:decimal(request:get-parameter("minlatitude", "90.0")) < xs:decimal(request:get-parameter("maxlatitude", "90.0"))}</TEST>
  <TEST>min max longitude {xs:decimal(stationutil:get-parameter("minlongitude"))} ++  {  xs:decimal(stationutil:get-parameter("maxlongitude"))}</TEST>
  <TEST>c_l_t: {stationutil:location_pattern_translate(request:get-parameter("location", "*"))}</TEST>    
  <TEST>c_l_t: {stationutil:channel_pattern_translate(stationutil:get-parameter("channel"))}</TEST>    
  <Source>eXistDB</Source>
  <Sender>INGV-ONT</Sender>
  <Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.0</Module>
  <ModuleURI>"{request:get-uri()}?{request:get-query-string()}"</ModuleURI>
  <Created>{current-dateTime()}</Created>
{

let $minlatitude := xs:decimal(stationutil:get-parameter("minlatitude"))
let $maxlatitude := xs:decimal(stationutil:get-parameter("maxlatitude"))
let $minlongitude := xs:decimal(stationutil:get-parameter("minlongitude"))
let $maxlongitude := xs:decimal(stationutil:get-parameter("maxlongitude"))   

let $network_param := stationutil:get-parameter("network")
let $station_param := stationutil:get-parameter("station")
let $channel_param := stationutil:get-parameter("channel")
let $location_param := stationutil:get-parameter("location")

let $network_pattern:=stationutil:network_pattern_translate($network_param)
let $station_pattern:=stationutil:station_pattern_translate($station_param)
let $channel_pattern:=stationutil:channel_pattern_translate($channel_param)    
let $location_pattern:=stationutil:location_pattern_translate($location_param)

for $item in collection("/db/apps/fdsn-station/Station/")

let $Latitude:= $item/FDSNStationXML/Network/Station/Latitude
let $Longitude:= $item/FDSNStationXML/Network/Station/Longitude

where $Latitude  > $minlatitude and  
      $Latitude  < $maxlatitude and 
      $Longitude > $minlongitude and 
      $Longitude < $maxlongitude 

for $network in $item//Network  
    let $networkcode := $network/@code
    let $station:=$network/Station
    let $stationcode:=$station/@code
    let $channel:=$station/Channel
    let $lat := $station/Latitude
    let $lon := $station/Longitude    
    let $CreationDate:= $channel/@startDate
    let $TerminationDate:= $channel/@endDate
    let $channelcode:=$channel/@code
    let $channellocationcode:=$channel/@locationCode
    let $startDate := $network/@startDate
    let $endDate := $network/@endDate
    let $restrictedStatus:=$network/@restrictedStatus
    let $Description := $network/Description
    let $ingv_identifier := $network/ingv:Identifier
    where
        stationutil:constraints_onchannel( $CreationDate, $TerminationDate ) 
        and stationutil:check_radius($lat,$lon) 
        and matches($networkcode,  $network_pattern ) 
        and matches($stationcode,  $station_pattern )
        and matches ($channelcode,  $channel_pattern) 
        and matches($channellocationcode,$location_pattern)
        group by $networkcode, $startDate, $endDate, $restrictedStatus, $Description, $ingv_identifier
        order by $networkcode
    return
        <Network>
        {$networkcode}  
        {$startDate}  
        {$endDate}
        {$restrictedStatus}
        {$Description}    
        {$ingv_identifier}
        <TotalNumberStations> {stationutil:stationcount($networkcode)} </TotalNumberStations>
        <SelectedNumberStations> {count($network/Station)} </SelectedNumberStations>
</Network>
}   
</FDSNStationXML>
else
    stationutil:nodata_error()
else 
    stationutil:badrequest_error()
};

declare function local:main_text(){
        util:declare-option("exist:serialize","method=text media-type=text/plain indent=yes")  ,    
        transform:transform(local:main(), doc("network.xsl"), ())
};    
    

if (stationutil:get-parameter("format")="xml") 
    then local:main()
    else if (stationutil:get-parameter("format")="text") then local:main_text()
    else ()
