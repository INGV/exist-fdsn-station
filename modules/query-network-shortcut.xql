xquery version "3.1";

declare default element namespace "http://www.fdsn.org/xml/station/1" ;
declare namespace ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";
import module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil"  at "util.xql";
(:import module namespace errors="http://exist-db.org/apps/fdsn-station/modules/errors"  at "errors.xql";:)
declare namespace output = "http://www.w3.org/2010/xslt-xquery-serialization";
declare namespace request="http://exist-db.org/xquery/request";
(:TODO uncomment after debug:)
declare option output:indent "yes";

(:declare function local:query_network_shortcut_main() as element() {:)
(:if (stationutil:check_parameters_limits()) then :)
(:    if (stationutil:channel_exists()) then :)
(:<FDSNStationXML xmlns="http://www.fdsn.org/xml/station/1" xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" schemaVersion="1.0" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.0.xsd">:)
(:  <Source>eXistDB</Source>:)
(:  <Sender>INGV-ONT</Sender>:)
(:  <Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.0</Module>:)
(:  <ModuleURI>"{request:get-uri()}?{request:get-query-string()}"</ModuleURI>:)
(:  <Created>{current-dateTime()}</Created>:)
(:{:)
(::)
(:for $item in collection("/db/apps/fdsn-station/Station/"):)
(::)
(:for $network in $item//Network  :)
(::)
(:    let $network_param := stationutil:get-parameter("network"):)
(:    let $networkcode := $network/@code:)
(:    let $startDate := $network/@startDate:)
(:    let $endDate := $network/@endDate:)
(:    let $restrictedStatus:=$network/@restrictedStatus:)
(:    let $Description := $network/Description:)
(:    let $ingv_identifier := $network/ingv:Identifier:)
(:    let $network_pattern:=stationutil:network_pattern_translate($network_param):)
(:    where:)
(:        matches($networkcode,  $network_pattern):)
(:        group by $networkcode, $startDate, $endDate, $restrictedStatus, $Description, $ingv_identifier:)
(:        order by $networkcode:)
(:    return :)
(:        <Network>:)
(:        {$networkcode}  :)
(:        {$startDate}  :)
(:        {$endDate}:)
(:        {$restrictedStatus}:)
(:        {$Description}    :)
(:        {$ingv_identifier}:)
(:        <TotalNumberStations> {stationutil:stationcount($networkcode)} </TotalNumberStations>:)
(:        <SelectedNumberStations> {count($network/Station)} </SelectedNumberStations>:)
(:        {:)
(:        for $station in $network/Station:)
(:        order by $station/@code:)
(:        return:)
(:        if ( matches(stationutil:get-parameter("level"),"channel")) :)
(:            then stationutil:remove-elements($station,"Stage"):)
(:            else $station:)
(:}:)
(:</Network>        :)
(:        :)
(::)
(:}   :)
(:</FDSNStationXML>:)
(:else:)
(:    stationutil:nodata_error():)
(:else :)
(:    stationutil:badrequest_error():)
(:};:)


declare function local:main_text(){
        util:declare-option("exist:serialize","method=text media-type=text/plain indent=yes") ,
        transform:transform(stationutil:query_network_shortcut_main(), doc("channel.xsl"), ())
};    
    

if (stationutil:get-parameter("format")="xml") 
    then stationutil:query_network_shortcut_main()
    else local:main_text()