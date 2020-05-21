xquery version "3.1";

declare default element namespace "http://www.fdsn.org/xml/station/1" ;
declare namespace ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";
declare namespace functx = "http://www.functx.com";

declare namespace request="http://exist-db.org/xquery/request";
declare namespace output = "http://www.w3.org/2010/xslt-xquery-serialization";
declare option output:method "xml";
declare option output:media-type "text/xml";
(:TODO uncomment after debug:)
declare option output:indent "yes";

(:    TODO: selected number channels in AIO va preso non il totale ma il totale per la network in cui si sta scrivendo :)

(: Functions declarations  :)

declare function functx:stationcount($netcode as xs:string) as item()
{
    for $item in collection("/db/apps/fdsn-station/Station/")
        let $network:= $item//Network[@code=$netcode]
        let $station:= $network/Station
        where $network/@code=$netcode
        group by $netcode
    return count($station)
};


(:declare function functx:channelcount($station as item()) as item():)
(:{:)
(:    count($station/Channel):)
(:};:)

declare function functx:sanitize ($input as xs:string) as xs:string
{
  let $output:=translate( $input, "|", "-")    
  return $output  
};

declare function functx:network_pattern_translate ($input as xs:string) as xs:string
{
   
   let $tokens := tokenize(functx:sanitize($input), "[,\s]+")
(: split input by commas in tokens, check lenght of every token two chars, chars can be alphanum and ? or * :)
(:  return a pattern for regex, for exact match include the pattern as in ^pattern$ :)

   return "("||string-join( 
   for $token in $tokens
   return 
        if (string-length($token)=2) 
        then
            let $pattern:= translate( $token, "*", ".*")
            let $pattern:= translate( $pattern, "?", ".")
                (: * -> 0 or more characters, ? exactly one character :)
                return "^"||$pattern||"$"
        else if (string-length($token)=1) then
                let $pattern:= translate( $token, "*", ".*")
            return $pattern
        else if (string-length($token)=0) then
                let $pattern:= ""
            return $pattern
        else 
            let $pattern:="NEVERMATCH"
            return $pattern
            
    , "|") || ")"       
};

declare function functx:station_pattern_translate ($input as xs:string) as xs:string
{
   let $tokens := tokenize(functx:sanitize($input), "[,\s]+")
(: split input by commas in tokens, check lenght of every token 3-5 chars, chars can be alphanum and ? or * :)
   return "("||string-join( 
   for $token in $tokens
   return 
        if (string-length($token)<6 ) 
        then
            let $pattern:= translate( $token, "*", ".*")
            let $pattern:= translate( $pattern, "?", ".")
            (: * -> 0 or more characters, ? exactly one character :)                
                return
                $pattern    
        else
            let $pattern:="NEVERMATCH"
            return $pattern
    , "|") || ")"        
};

declare function functx:channel_pattern_translate($input as item()*) as xs:string
{
(:   let $tokens := tokenize(functx:sanitize($input), ","):)

    let $input_string:= string-join($input,",")
    let $tokens := tokenize($input_string,",")
(:    let $tokens := tokenize($input, ",")    :)
(:    let $tokens :=$input:)
(: split input by commas in tokens, check lenght of every token 3-5 chars, chars can be alphanum and ? or * :)
   return 
    "("||string-join( 
   for $token in $tokens
   return 
        if (string-length($token)<4 ) 
        then
            let $pattern:= translate( $token, "*", ".*")
            let $pattern:= translate( $pattern, "?", ".")
                (: every character will remain the same, only * and ? become . ():)
            return
                     $pattern
        else
            let $pattern:="NEVERMATCH"
            return $pattern
    , "|") || ")"    
};

declare function functx:channel_exists() as xs:boolean
{
    
let $minlatitude := xs:decimal(request:get-parameter("minlatitude","-90.0"))
let $maxlatitude := xs:decimal(request:get-parameter("maxlatitude", "90.0"))
let $minlongitude := xs:decimal(request:get-parameter("minlongitude","-180.0"))
let $maxlongitude := xs:decimal(request:get-parameter("maxlongitude", "180.0"))   
let $startbefore := xs:dateTime(request:get-parameter("startbefore", "6000-01-01T01:01:01"))
let $startafter := xs:dateTime(request:get-parameter("startafter", "1800-01-01T01:01:01"))
let $endbefore := xs:dateTime(request:get-parameter("endbefore", "6000-01-01T01:01:01"))   
let $endafter := xs:dateTime(request:get-parameter("endafter", "1800-01-01T01:01:01"))
let $network_param := request:get-parameter("network", "*")
let $station_param := request:get-parameter("station", "*")
let $channel_param := request:get-parameter("channel", "*")

return 

not(empty(
for $item in collection("/db/apps/fdsn-station/Station/")

    let $Latitude:= $item/FDSNStationXML/Network/Station/Latitude
    let $Longitude:= $item/FDSNStationXML/Network/Station/Longitude
    let $CreationDate:= $item/FDSNStationXML/Network/Station/CreationDate
    let $TerminationDate:= $item/FDSNStationXML/Network/Station/TerminationDate 
    let $pattern:=functx:channel_pattern_translate($channel_param)
where 
    $Latitude  > $minlatitude 
    and $Latitude  < $maxlatitude 
    and $Longitude > $minlongitude 
    and $Longitude < $maxlongitude 
    and $CreationDate < $startbefore
    and $CreationDate > $startafter  
    for $network in $item//Network  
        let $networkcode := $network/@code
        let $stationcode:=$network/Station/@code
        let $selchannelcode:=$network/Station/Channel/@code
    where
        matches($networkcode, functx:network_pattern_translate($network_param) ) 
        and matches($stationcode, functx:station_pattern_translate($station_param) )
        and matches ($selchannelcode, $pattern)        

        return $selchannelcode 
    ))
};

declare function functx:check_parameters_limits() as xs:boolean? 
{

let $minlatitude := xs:decimal(request:get-parameter("minlatitude","-90.0"))
let $maxlatitude := xs:decimal(request:get-parameter("maxlatitude", "90"))
let $minlongitude := xs:decimal(request:get-parameter("minlongitude","-180"))
let $maxlongitude := xs:decimal(request:get-parameter("maxlongitude", "180"))   
let $startbefore := xs:dateTime(request:get-parameter("startbefore", "6000-01-01T01:01:01"))
let $startafter := xs:dateTime(request:get-parameter("startafter", "1800-01-01T01:01:01"))
let $endbefore := xs:dateTime(request:get-parameter("endbefore", "6000-01-01T01:01:01"))   
let $endafter := xs:dateTime(request:get-parameter("endafter", "1800-01-01T01:01:01"))
let $network_param := request:get-parameter("network", "")
let $station_param := request:get-parameter("station", "")
let $outputlevel := request:get-parameter("level", "network")

(:let $attr_name:=request:attribute-names():)

return if (
           ($minlatitude>90.0 or $maxlatitude > 90.0 or $minlatitude<-90.0 or $maxlatitude <-90.0
           or $minlatitude > $maxlatitude 
           or $minlongitude>180.0 or $maxlongitude > 180.0 or $minlongitude<-180.0 or $maxlongitude <-180.0
           or $minlongitude > $maxlongitude 
           or $startbefore < $startafter
           or $endbefore < $endafter
           or not(matches($outputlevel,"network|station|channel|response"))
           )) then false() else true()
} ;


if (functx:check_parameters_limits() and functx:channel_exists()) then 
(:if (functx:check_parameters_limits() ) then     :)
<FDSNStationXML xmlns="http://www.fdsn.org/xml/station/1" xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" schemaVersion="1.0" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.0.xsd">
  <TEST>{matches("HHZ",functx:channel_pattern_translate(request:get-parameter("channel", "")))}</TEST> 
  <TEST>c_p_t: {functx:channel_pattern_translate(request:get-parameter("channel", ""))}</TEST>   
  <TEST>channel exists {functx:channel_exists()}</TEST> 
  <TEST>tokenize example {tokenize("HHZ",",")}</TEST>
  <TEST>maxlatitude {xs:decimal(request:get-parameter("minlatitude", "90.0")) < xs:decimal(request:get-parameter("maxlatitude", "90.0"))}</TEST>
  <TEST>min max longitude {xs:decimal(request:get-parameter("minlongitude", "90.0")) < xs:decimal(request:get-parameter("maxlongitude", "90.0"))}</TEST>
  <Source>eXistDB</Source>
  <Sender>INGV-ONT</Sender>
  <Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.0</Module>
  <ModuleURI>"{request:get-uri()}?{request:get-query-string()}"</ModuleURI>
  <Created>{current-dateTime()}</Created>
{
let $minlatitude := xs:decimal(request:get-parameter("minlatitude","-90.0"))
let $maxlatitude := xs:decimal(request:get-parameter("maxlatitude", "90.0"))
let $minlongitude := xs:decimal(request:get-parameter("minlongitude","-180.0"))
let $maxlongitude := xs:decimal(request:get-parameter("maxlongitude", "180.0"))   
let $startbefore := xs:dateTime(request:get-parameter("startbefore", "6000-01-01T01:01:01"))
let $startafter := xs:dateTime(request:get-parameter("startafter", "1800-01-01T01:01:01"))
let $endbefore := xs:dateTime(request:get-parameter("endbefore", "6000-01-01T01:01:01"))   
let $endafter := xs:dateTime(request:get-parameter("endafter", "1800-01-01T01:01:01"))
let $network_param := request:get-parameter("network", "*")
let $station_param := request:get-parameter("station", "*")
let $channel_param := request:get-parameter("channel", "*")
let $outputlevel := request:get-parameter("level", "network")
let $network_pattern:=functx:network_pattern_translate($network_param)
let $station_pattern:=functx:station_pattern_translate($station_param)
let $channel_pattern:=functx:channel_pattern_translate($channel_param)    
    
for $item in collection("/db/apps/fdsn-station/Station/")

let $Latitude:= $item/FDSNStationXML/Network/Station/Latitude
let $Longitude:= $item/FDSNStationXML/Network/Station/Longitude
let $CreationDate:= $item/FDSNStationXML/Network/Station/CreationDate
let $TerminationDate:= $item/FDSNStationXML/Network/Station/TerminationDate 

where $Latitude  > $minlatitude and  
      $Latitude  < $maxlatitude and 
      $Longitude > $minlongitude and 
      $Longitude < $maxlongitude and 
      $CreationDate < $startbefore and 
      $CreationDate > $startafter  
    
for $network in $item//Network  
    let $networkcode := $network/@code
    let $stationcode:=$network/Station/@code
    let $station:=$network/Station
    let $channelcode:=$network/Station/Channel/@code
    let $startDate := $network/@startDate
    let $endDate := $network/@endDate
    let $restrictedStatus:=$network/@restrictedStatus
    let $Description := $network/Description
    let $ingv_identifier := $network/ingv:Identifier
    
    where
        matches($networkcode,  $network_pattern ) 
        and matches($stationcode,  $station_pattern )
        and matches ($channelcode,  $channel_pattern) 
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
        <TotalNumberStations> {functx:stationcount($networkcode)} </TotalNumberStations>
        <SelectedNumberStations> {count($network/Station)} </SelectedNumberStations>
        {
        for $station in $network/Station
            let $stationcode:=$station/@code
            let $stationstartDate := $station/@startDate
            let $stationendDate := $station/@endDate
            let $stationrestrictedStatus := $station/@restrictedStatus
            let $channelcode:=$station/Channel/@code
            let $Latitude:=  xs:decimal($station/Latitude)
            let $Longitude:= xs:decimal($station/Longitude) 
            let $CreationDate:= $station/CreationDate
            let $TerminationDate:= $station/TerminationDate 
            let $networkcode:=$network/@code
            let $pattern:=functx:channel_pattern_translate($channel_param)
        where 
            $Latitude  > $minlatitude and  
            $Latitude  < $maxlatitude and 
            $Longitude > $minlongitude and 
            $Longitude < $maxlongitude and 
            $CreationDate < $startbefore and 
            $CreationDate > $startafter  and
            (matches ($channelcode,  $pattern ))
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
                let $pattern:=functx:channel_pattern_translate($channel_param)
                where matches ($selchannelcode,  $pattern )
                return $selchannelcode)
            }
            </SelectedNumberChannels>
            {
                for $channel in $station/Channel
                let $selchannelcode:=$channel/@code
                let $pattern:=functx:channel_pattern_translate($channel_param)
                where matches ($selchannelcode,  $pattern )
                return $channel
            }
            </Station>
}
</Network>
}   
</FDSNStationXML>
else
    <ERROR/>

    
