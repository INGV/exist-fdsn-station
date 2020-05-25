xquery version "3.1";

declare default element namespace "http://www.fdsn.org/xml/station/1" ;
declare namespace ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";
import module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil"  at "util.xql";

declare namespace request="http://exist-db.org/xquery/request";
declare namespace output = "http://www.w3.org/2010/xslt-xquery-serialization";
declare option output:method "xml";
declare option output:media-type "text/xml";
(:TODO uncomment after debug:)
declare option output:indent "no";

(:    TODO: selected number channels in AIO va preso non il totale ma il totale per la network in cui si sta scrivendo :)

(: Functions declarations  :)
declare function local:remove-elements($input as element(), $remove-names as xs:string*) as element() {
   element {node-name($input) }
      {$input/@*,
       for $child in $input/node()[not(name(.)=$remove-names)]
          return
             if ($child instance of element())
                then local:remove-elements($child, $remove-names)
                else $child
      }
};


if (stationutil:check_parameters_limits()) then 
    if (stationutil:channel_exists()) then 
(:if (stationutil:check_parameters_limits() ) then     :)
<FDSNStationXML xmlns="http://www.fdsn.org/xml/station/1" xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" schemaVersion="1.0" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.0.xsd">
  <TEST>{matches("HHZ",stationutil:channel_pattern_translate(request:get-parameter("channel", "")))}</TEST> 
  <TEST>c_p_t: {stationutil:channel_pattern_translate(request:get-parameter("channel", ""))}</TEST>   
  <TEST>channel exists {stationutil:channel_exists()}</TEST> 
  <TEST>tokenize example {tokenize("HHZ",",")}</TEST>
  <TEST>maxlatitude {xs:decimal(request:get-parameter("minlatitude", "90.0")) < xs:decimal(request:get-parameter("maxlatitude", "90.0"))}</TEST>
  <TEST>min max longitude {xs:decimal(request:get-parameter("minlongitude", "90.0")) < xs:decimal(request:get-parameter("maxlongitude", "90.0"))}</TEST>
  <Source>eXistDB</Source>
  <Sender>INGV-ONT</Sender>
  <Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.0</Module>
  <ModuleURI>"{request:get-uri()}?{request:get-query-string()}"</ModuleURI>
  <Created>{current-dateTime()}</Created>
{
(:  any level file must match the default level :)
let $outputlevel := request:get-parameter("level", "channel")

let $minlatitude := xs:decimal(request:get-parameter("minlatitude","-90.0"))
let $maxlatitude := xs:decimal(request:get-parameter("maxlatitude", "90.0"))
let $minlongitude := xs:decimal(request:get-parameter("minlongitude","-180.0"))
let $maxlongitude := xs:decimal(request:get-parameter("maxlongitude", "180.0"))   
(:I valori di default non hanno senso, se non sono passati i parametri bisogna saltare il check :)
let $missing_startbefore := request:get-parameter("startbefore", "yes")
let $missing_startafter := request:get-parameter("startafter", "yes")
let $missing_endbefore := request:get-parameter("endbefore", "yes")
let $missing_endafter := request:get-parameter("endafter", "yes")  
let $startbefore := xs:dateTime(request:get-parameter("startbefore", "6000-01-01T01:01:01"))
let $startafter := xs:dateTime(request:get-parameter("startafter", "1800-01-01T01:01:01"))
let $endbefore := xs:dateTime(request:get-parameter("endbefore", "6000-01-01T01:01:01"))   
let $endafter := xs:dateTime(request:get-parameter("endafter", "1800-01-01T01:01:01"))
let $network_param := request:get-parameter("network", "*")
let $station_param := request:get-parameter("station", "*")
let $channel_param := request:get-parameter("channel", "*")
let $location_param := request:get-parameter("location", "*")    

let $network_pattern:=stationutil:network_pattern_translate($network_param)
let $station_pattern:=stationutil:station_pattern_translate($station_param)
let $channel_pattern:=stationutil:channel_pattern_translate($channel_param)    
let $location_pattern:=stationutil:location_pattern_translate($location_param)

for $item in collection("/db/apps/fdsn-station/Station/")
    let $Latitude:= $item/FDSNStationXML/Network/Station/Latitude
    let $Longitude:= $item/FDSNStationXML/Network/Station/Longitude
    let $CreationDate:= $item/FDSNStationXML/Network/Station/Channel/@startDate
    let $TerminationDate:= $item/FDSNStationXML/Network/Station/Channel/@endDate
where   
    $Latitude  > $minlatitude and  
    $Latitude  < $maxlatitude and 
    $Longitude > $minlongitude and 
    $Longitude < $maxlongitude and
    stationutil:parameter_constraint_onchannel(
                $missing_startbefore, $missing_startafter, $missing_endbefore, $missing_endafter,
                $startbefore, $startafter, $endbefore, $endafter, 
                $CreationDate, $TerminationDate ) 
    
for $network in $item//Network  
    let $networkcode := $network/@code
    let $stationcode:=$network/Station/@code
    let $station:=$network/Station
    let $channel:=$station/Channel
    let $channelcode:=$channel/@code
    let $channellocationcode:=$channel/@locationCode
    let $startDate := $network/@startDate
    let $endDate := $network/@endDate
    let $restrictedStatus:=$network/@restrictedStatus
    let $Description := $network/Description
    let $ingv_identifier := $network/ingv:Identifier
    where
        stationutil:parameter_constraint_onchannel(
                $missing_startbefore, $missing_startafter, $missing_endbefore, $missing_endafter,
                $startbefore, $startafter, $endbefore, $endafter, 
                $CreationDate, $TerminationDate ) and    
        matches($networkcode,  $network_pattern ) 
        and matches($stationcode,  $station_pattern )
        and matches ($channelcode,  $channel_pattern)
        and matches ($channellocationcode, $location_pattern)
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
        {
        for $station in $network/Station
            let $stationcode:=$station/@code
            let $stationstartDate := $station/@startDate
            let $stationendDate := $station/@endDate
            let $stationrestrictedStatus := $station/@restrictedStatus
            let $channel:=$station/Channel
            let $channelcode:=$channel/@code
            let $channellocationcode := $channel/@locationCode
            let $Latitude:=  xs:decimal($station/Latitude)
            let $Longitude:= xs:decimal($station/Longitude) 
            let $CreationDate:= $channel/@startDate
            let $TerminationDate:= $channel/@endDate 
            let $networkcode:=$network/@code
            let $pattern:=stationutil:channel_pattern_translate($channel_param)
            let $location_pattern:=stationutil:location_pattern_translate($location_param)
            let $missing_startbefore := request:get-parameter("startbefore", "yes")
            let $missing_startafter := request:get-parameter("startafter", "yes")
            let $missing_endbefore := request:get-parameter("endbefore", "yes")
            let $missing_endafter := request:get-parameter("endafter", "yes")  
        where 
            $Latitude  > $minlatitude and  
            $Latitude  < $maxlatitude and 
            $Longitude > $minlongitude and 
            $Longitude < $maxlongitude and 
            stationutil:parameter_constraint_onchannel(
                $missing_startbefore, $missing_startafter, $missing_endbefore, $missing_endafter,
                $startbefore, $startafter, $endbefore, $endafter, 
                $CreationDate, $TerminationDate ) and          
            
            matches ($channelcode,  $pattern) and
            matches ($channellocationcode,  $location_pattern)
            order by $station/@code
        return
            <Station>
            {$stationcode}  
            {$stationstartDate}  
            {$stationendDate}   
            {$stationrestrictedStatus}
            {$station/ingv:Identifier}
            {$station/Latitude}
            {$station/Longitude}
            {$station/Elevation}
            {$station/Site}
            {$station/CreationDate}
            <TotalNumberChannels>{count($station/Channel)}</TotalNumberChannels>
            <SelectedNumberChannels>
            {
                count (for $channel in $station/Channel
                let $selchannelcode:=$channel/@code
                let $channellocationcode:=$channel/@locationCode
                let $pattern:=stationutil:channel_pattern_translate($channel_param)
                let $location_pattern:=stationutil:location_pattern_translate($location_param)
                let $CreationDate:= $channel/@startDate
                let $TerminationDate:= $channel/@endDate                                  
                where 
                    stationutil:parameter_constraint_onchannel(
                        $missing_startbefore, $missing_startafter, $missing_endbefore, $missing_endafter,
                        $startbefore, $startafter, $endbefore, $endafter, 
                        $CreationDate, $TerminationDate ) and
                    matches ($selchannelcode,  $pattern ) and
                    matches ($channellocationcode,  $location_pattern)
                return $selchannelcode)
            }
            </SelectedNumberChannels>
            {
                for $channel in $station/Channel
                let $selchannelcode:=$channel/@code
                let $channellocationcode:=$channel/@locationCode
                let $pattern:=stationutil:channel_pattern_translate($channel_param)
                let $location_pattern:=stationutil:location_pattern_translate($location_param)  
                let $CreationDate:= $channel/@startDate
                let $TerminationDate:= $channel/@endDate                  
                where
                    stationutil:parameter_constraint_onchannel(
                        $missing_startbefore, $missing_startafter, $missing_endbefore, $missing_endafter,
                        $startbefore, $startafter, $endbefore, $endafter, 
                        $CreationDate, $TerminationDate ) and
                    matches ($selchannelcode,  $pattern )and
                    matches ($channellocationcode,  $location_pattern)
                return local:remove-elements($channel,"Stage")
            }
            </Station>
}
</Network>
}   
</FDSNStationXML>
else
    stationutil:nodata_error()
else 
    stationutil:badrequest_error()
    
