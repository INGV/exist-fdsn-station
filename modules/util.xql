xquery version "3.1";

module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil";
import module namespace request = "http://exist-db.org/xquery/request";
declare default element namespace "http://www.fdsn.org/xml/station/1" ;
declare namespace ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";

(: Serialization cannot change during the same request no way to fix using another file like in util.xql :)
(:declare option exist:serialize "method=html5 media-type=text/html";:)
(:declare option output:method "html5";:)
(:declare option output:media-type "text/html";:)


(: Functions declarations  :)

declare function stationutil:stationcount($netcode as xs:string) as item()
{
    for $item in collection("/db/apps/fdsn-station/Station/")
        let $network:= $item//Network[@code=$netcode]
        let $station:= $network/Station
        where $network/@code=$netcode
        group by $netcode
    return count($station)
};


declare function stationutil:sanitize ($input as xs:string) as xs:string
{
  let $output:=translate( $input, "|", "-")    
  return $output  
};

declare function stationutil:network_pattern_translate ($input as xs:string) as xs:string
{
   
   let $tokens := tokenize(stationutil:sanitize($input), "[,\s]+")
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

declare function stationutil:station_pattern_translate ($input as xs:string) as xs:string
{
(:   let $tokens := tokenize(stationutil:sanitize($input), "[,\s]+"):)
(: split input by commas in tokens, check lenght of every token 3-5 chars, chars can be alphanum and ? or * :)
    let $input_string:= string-join($input,",")
    let $tokens := tokenize($input_string,",")
 
   return "("||string-join( 
   for $token in $tokens
   return 
        if (string-length($token)<6 ) 
        then
            let $pattern:= translate( $token, "*", ".*")
            let $pattern:= translate( $pattern, "?", ".")
            (: * -> 0 or more characters, ? exactly one character :)                
             return "^"||$pattern
        else
            let $pattern:="NEVERMATCH"
            return $pattern
    , "|") || ")"        
};

declare function stationutil:channel_pattern_translate($input as item()*) as xs:string
{
(:   let $tokens := tokenize(functx:sanitize($input), ","):)

    let $input_string:= string-join($input,",")
    let $tokens := tokenize($input_string,",")

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

declare function stationutil:location_pattern_translate($input as item()*) as xs:string
{

    let $input_string:= string-join($input,",")
    let $tokens := tokenize($input_string,",")

(: split input by commas in tokens, check lenght of every token 3-5 chars, chars can be alphanum and ? or * :)
   return 
    "("||string-join( 
   for $token in $tokens
   return 
(:       ".*":)
        if (string-length($token)<3) 
        then
            let $pattern:= replace( $token, "\*", ".*")
            let $pattern:= translate( $pattern, "?", ".")
            let $pattern:= if ($pattern="") then "^$" else $pattern
            let $pattern:= if ($pattern="--") then "^$" else $pattern
(:                (: every character will remain the same, only * and ? become . ():):)
            return
                     $pattern
        else
            let $pattern:="NEVERMATCH"
            return $pattern

    , "|") || ")"    
};


(:declare function stationutil:parameter_constraint_onchannel( :)
(:    $missing_starttime as xs:string*, :)
(:    $missing_endtime as xs:string*,:)
(:    $missing_startbefore as xs:string*, :)
(:    $missing_startafter as xs:string*,:)
(:    $missing_endbefore as xs:string*,:)
(:    $missing_endafter as xs:string*,:)
(:    $starttime as xs:dateTime*,  :)
(:    $endtime as xs:dateTime*, :)
(:    $startbefore as xs:dateTime*,  :)
(:    $startafter as xs:dateTime*, :)
(:    $endbefore as xs:dateTime*, :)
(:    $endafter as xs:dateTime*, :)
(:    $CreationDate as xs:dateTime*, :)
(:    $TerminationDate as xs:dateTime* ) as xs:boolean :)
(:    {:)
(:        (($missing_starttime="yes") or($CreationDate >= $starttime)) and :)
(:        (($missing_endtime="yes") or  (not(empty($TerminationDate)) and ($TerminationDate <= $endtime))) and:)
(:        (($missing_startbefore="yes") or ($CreationDate < $startbefore)) and :)
(:        (($missing_startafter="yes") or($CreationDate > $startafter))  and:)
(:        (($missing_endbefore="yes") or  (not(empty($TerminationDate)) and ($TerminationDate < $endbefore))) and:)
(:        (($missing_endafter="yes") or  (empty($TerminationDate)) or ($TerminationDate > $endafter))   :)
(:        :)
(:};:)


(:YYYY-MM-DD:)
declare function stationutil:time_adjust( $mydatetime as xs:string ) as xs:string {
    
    if (not(matches($mydatetime,".*T.*"))) then $mydatetime||"T"||"00:00:00.0"
    else $mydatetime
    
};

declare function stationutil:constraints_onchannel(
    $CreationDate as xs:dateTime*, 
    $TerminationDate as xs:dateTime* ) as xs:boolean 
    {
    try {    
    let $missing_startbefore := request:get-parameter("startbefore", "yes")
    let $missing_endbefore := request:get-parameter("endbefore", "yes")
    let $missing_startafter := request:get-parameter("startafter", "yes")
    let $missing_endafter := request:get-parameter("endafter", "yes")
    let $missing_starttime := request:get-parameter("starttime", "yes")
    let $missing_endtime := request:get-parameter("endtime", "yes")
    let $startbefore := xs:dateTime(stationutil:time_adjust(request:get-parameter("startbefore", "6000-01-01T01:01:01")))
    let $startafter := xs:dateTime(stationutil:time_adjust(request:get-parameter("startafter", "1800-01-01T01:01:01")))
    let $endbefore := xs:dateTime(stationutil:time_adjust(request:get-parameter("endbefore", "6000-01-01T01:01:01")))   
    let $endafter := xs:dateTime(stationutil:time_adjust(request:get-parameter("endafter", "1800-01-01T01:01:01")))
    let $starttime := xs:dateTime(stationutil:time_adjust(request:get-parameter("starttime", "1800-01-01T01:01:01")))
    let $endtime := xs:dateTime(stationutil:time_adjust(request:get-parameter("endtime", "6000-01-01T01:01:01")))   
    
    return    
        (($missing_starttime="yes") or($CreationDate >= $starttime)) and 
        (($missing_endtime="yes") or  (not(empty($TerminationDate)) and ($TerminationDate <= $endtime))) and
        (($missing_startbefore="yes") or ($CreationDate < $startbefore)) and 
        (($missing_startafter="yes") or($CreationDate > $startafter))  and
        (($missing_endbefore="yes") or  (not(empty($TerminationDate)) and ($TerminationDate < $endbefore))) and
        (($missing_endafter="yes") or  (empty($TerminationDate)) or ($TerminationDate > $endafter))   
    }
    catch err:FORG0001 {false()}
};


declare function stationutil:channel_match( $channels as item()* )  as xs:boolean *
{
 
(:I valori di default non hanno senso, se non sono passati i parametri bisogna saltare il check :)
(:FUNZIONE DA rivedere:)
    for $channel in $channels
    
        let $missing_startbefore := request:get-parameter("startbefore", "yes")
        let $missing_endbefore := request:get-parameter("endbefore", "yes")
        let $missing_startafter := request:get-parameter("startafter", "yes")
        let $missing_endafter := request:get-parameter("endafter", "yes")
        let $missing_startime := request:get-parameter("starttime", "yes")
        let $missing_endtime := request:get-parameter("endtime", "yes")
        let $startbefore := xs:dateTime(stationutil:time_adjust(request:get-parameter("startbefore", "6000-01-01T01:01:01")))
        let $startafter := xs:dateTime(stationutil:time_adjust(request:get-parameter("startafter", "1800-01-01T01:01:01")))
        let $endbefore := xs:dateTime(stationutil:time_adjust(request:get-parameter("endbefore", "6000-01-01T01:01:01")))   
        let $endafter := xs:dateTime(stationutil:time_adjust(request:get-parameter("endafter", "1800-01-01T01:01:01")))
        let $starttime := xs:dateTime(stationutil:time_adjust(request:get-parameter("starttime", "1800-01-01T01:01:01")))
        let $endtime := xs:dateTime(stationutil:time_adjust(request:get-parameter("endtime", "6000-01-01T01:01:01")))   
        let $network_param := request:get-parameter("network", "*")
        let $station_param := request:get-parameter("station", "*")
        let $channel_param := request:get-parameter("channel", "*")
        let $location_param := request:get-parameter("location", "*")
        let $CreationDate:= $channel/@startDate
        let $TerminationDate:= $channel/@endDate
        let $Latitude:= $channel/Latitude
        let $Longitude:=  $channel//Longitude    
        let $pattern:=stationutil:channel_pattern_translate($channel_param)
        let $locationpattern:=stationutil:location_pattern_translate($location_param)
        let $minlatitude := xs:decimal(request:get-parameter("minlatitude","-90.0"))
        let $maxlatitude := xs:decimal(request:get-parameter("maxlatitude", "90.0"))
        let $minlongitude := xs:decimal(request:get-parameter("minlongitude","-180.0"))
        let $maxlongitude := xs:decimal(request:get-parameter("maxlongitude", "180.0"))          
       return 

            $Latitude  > $minlatitude 
            and $Latitude  < $maxlatitude 
            and $Longitude > $minlongitude 
            and $Longitude < $maxlongitude and
            (($missing_startbefore="yes") or ($CreationDate < $startbefore)) and 
            (($missing_startafter="yes") or($CreationDate > $startafter))  and
            (($missing_endbefore="yes") or  (not(empty($TerminationDate)) and ($TerminationDate < $endbefore))) and
            (($missing_endafter="yes") or  (empty($TerminationDate)) or ($TerminationDate > $endafter))
            (($missing_starttime="yes") or($CreationDate >= $starttime))  
            (($missing_endtime="yes") or  (not(empty($TerminationDate)) and ($TerminationDate <= $endtime)))
};


declare function stationutil:channel_exists() as xs:boolean
{
    
let $minlatitude := xs:decimal(request:get-parameter("minlatitude","-90.0"))
let $maxlatitude := xs:decimal(request:get-parameter("maxlatitude", "90.0"))
let $minlongitude := xs:decimal(request:get-parameter("minlongitude","-180.0"))
let $maxlongitude := xs:decimal(request:get-parameter("maxlongitude", "180.0"))   
(:I valori di default non hanno senso, se non sono passati i parametri bisogna saltare il check :)

let $network_param := request:get-parameter("network", "*")
let $station_param := request:get-parameter("station", "*")
let $channel_param := request:get-parameter("channel", "*")
let $location_param := request:get-parameter("location", "*")

return 

if (not(empty(
for $item in collection("/db/apps/fdsn-station/Station/")

    let $Latitude:= $item/FDSNStationXML/Network/Station/Latitude
    let $Longitude:= $item/FDSNStationXML/Network/Station/Longitude
(:TODO move check on channels epochs    :)
(:    let $CreationDate:= $item/FDSNStationXML/Network/Station/Channel/@startDate:)
(:    let $TerminationDate:= $item/FDSNStationXML/Network/Station/Channel/@endDate:)
(:TODO move check on channes epochs    :)    
    let $pattern:=stationutil:channel_pattern_translate($channel_param)
    let $locationpattern:=stationutil:location_pattern_translate($location_param)
where 
    $Latitude  > $minlatitude 
    and $Latitude  < $maxlatitude 
    and $Longitude > $minlongitude 
    and $Longitude < $maxlongitude 
    for $network in $item//Network  
        let $networkcode := $network/@code
        let $station :=$network/Station
        let $stationcode:=$station/@code
        let $channel:=$station/Channel
        let $CreationDate:= $channel/@startDate
        let $TerminationDate:= $channel/@endDate
        let $selchannelcode:=$channel/@code
        let $selchannellocationcode:=$channel/@locationCode
        let $CreationDate:= $channel/@startDate
        let $TerminationDate:= $channel/@endDate   
    where
        stationutil:constraints_onchannel($CreationDate,$TerminationDate) and
        matches($networkcode, stationutil:network_pattern_translate($network_param) ) 
        and matches($stationcode, stationutil:station_pattern_translate($station_param) )
        and matches ($selchannelcode, $pattern)        
        and matches ($selchannellocationcode,$locationpattern)
        return $selchannelcode 
    )))
    then true()
    else false()
};

declare function stationutil:check_parameters_limits() as xs:boolean 
{
try {
let $minlatitude := xs:decimal(request:get-parameter("minlatitude","-90.0"))
let $maxlatitude := xs:decimal(request:get-parameter("maxlatitude", "90"))
let $minlongitude := xs:decimal(request:get-parameter("minlongitude","-180"))
let $maxlongitude := xs:decimal(request:get-parameter("maxlongitude", "180"))   
let $startbefore := xs:dateTime(stationutil:time_adjust(request:get-parameter("startbefore", "6000-01-01T01:01:01")))
let $startafter := xs:dateTime(stationutil:time_adjust(request:get-parameter("startafter", "1800-01-01T01:01:01")))
let $endbefore := xs:dateTime(stationutil:time_adjust(request:get-parameter("endbefore", "6000-01-01T01:01:01")))   
let $endafter := xs:dateTime(stationutil:time_adjust(request:get-parameter("endafter", "1800-01-01T01:01:01")))
let $starttime := xs:dateTime(stationutil:time_adjust(request:get-parameter("starttime", "1800-01-01T01:01:01")))
let $endtime := xs:dateTime(stationutil:time_adjust(request:get-parameter("endtime", "6000-01-01T01:01:01")))   

let $network := request:get-parameter("network", "*")
let $station := request:get-parameter("station", "*")
let $channel := request:get-parameter("channel", "*")
let $location := request:get-parameter("location", "*")
let $outputlevel := request:get-parameter("level", "network")

return if (
           ($minlatitude>90.0 or $maxlatitude > 90.0 or $minlatitude<-90.0 or $maxlatitude <-90.0
           or $minlatitude > $maxlatitude 
           or $minlongitude>180.0 or $maxlongitude > 180.0 or $minlongitude<-180.0 or $maxlongitude <-180.0
           or $minlongitude > $maxlongitude 
           or $startbefore < $startafter
           or $endbefore < $endafter
           or $starttime > $endtime
           or not(matches($outputlevel,"network|station|channel|response"))
           or (contains(stationutil:network_pattern_translate($network), "NEVERMATCH")) 
           or (contains(stationutil:station_pattern_translate($station), "NEVERMATCH")) 
           or (contains(stationutil:channel_pattern_translate($channel), "NEVERMATCH")) 
           or (contains(stationutil:location_pattern_translate($location), "NEVERMATCH")) 
           
           )) then false() else true()
}
catch err:FORG0001 {false()}
} ;

declare function stationutil:remove-elements($input as element(), $remove-names as xs:string*) as element() {
   element {node-name($input) }
      {$input/@*,
       for $child in $input/node()[not(name(.)=$remove-names)]
          return
             if ($child instance of element())
                then stationutil:remove-elements($child, $remove-names)
                else $child
      }
};


declare function stationutil:nodata_error() {
(: declare output method locally to override default xml   :)
    util:declare-option("exist:serialize","method=text media-type=text/plain indent=no")  ,  
    if (matches(request:get-parameter("nodata", "204"),"404")) 
    then
        (
             response:set-status-code(404) , "Error 404 - no matching inventory found"
(:            response:set-status-code(404) , transform:transform(<Error>Error 404 - no matching inventory found</Error>, doc("error-translation.xsl"), ()):)
              
        )
    else if (matches(request:get-parameter("nodata", "204"),"204")) then
        response:set-status-code(204) 
    else 
        response:set-status-code(400) 
};

declare function stationutil:syntax_longitude() as xs:string{

let $minlongitude := xs:decimal(request:get-parameter("minlongitude","-180"))
let $maxlongitude := xs:decimal(request:get-parameter("maxlongitude", "180"))   
 
return 
    if ($minlongitude>180.0 or $maxlongitude > 180.0 or $minlongitude<-180.0 or $maxlongitude <-180.0) then 
" 
Must be -180 < longitude < 180
"
else ""     
  
};

declare function stationutil:syntax_latitude() as xs:string{
    
let $minlatitude := xs:decimal(request:get-parameter("minlatitude","-90.0"))
let $maxlatitude := xs:decimal(request:get-parameter("maxlatitude", "90"))

return 
    if ( $minlatitude>90.0 or $maxlatitude > 90.0 or $minlatitude<-90.0 or $maxlatitude <-90.0) 
    then
        "
Must be -90 < latitude < 90
"
    else ""

};

declare function stationutil:syntax_location() as xs:string{
    
let $location := xs:string(request:get-parameter("location","*"))

return 
if (contains(stationutil:location_pattern_translate($location), "NEVERMATCH")) 
    then
        "
Check location parameter
"
    else  ""

};

declare function stationutil:syntax_channel() as xs:string{
    
let $channel := xs:string(request:get-parameter("channel","*"))

return 
if (contains(stationutil:location_pattern_translate($channel), "NEVERMATCH")) 
    then
        "
Check channel parameter
"
    else  ""

};


declare function stationutil:syntax_station() as xs:string{
    
let $station := xs:string(request:get-parameter("station","*"))

return 
if (contains(stationutil:station_pattern_translate($station), "NEVERMATCH")) 
    then
        "
Check station parameter
"
    else  ""

};

declare function stationutil:syntax_network() as xs:string{
    
let $network := xs:string(request:get-parameter("network","*"))

return 
    if (contains(stationutil:network_pattern_translate($network), "NEVERMATCH")) 
    then
"
Check network parameter
"
    else  ""

};


declare function stationutil:syntax_times() as xs:string {
try 
{    
let $startbefore := xs:dateTime(stationutil:time_adjust(request:get-parameter("startbefore", "6000-01-01T01:01:01")))
let $startafter := xs:dateTime(stationutil:time_adjust(request:get-parameter("startafter", "1800-01-01T01:01:01")))
let $endbefore := xs:dateTime(stationutil:time_adjust(request:get-parameter("endbefore", "6000-01-01T01:01:01")))   
let $endafter := xs:dateTime(stationutil:time_adjust(request:get-parameter("endafter", "1800-01-01T01:01:01")))
let $starttime := xs:dateTime(stationutil:time_adjust(request:get-parameter("starttime", "1800-01-01T01:01:01")))
let $endtime := xs:dateTime(stationutil:time_adjust(request:get-parameter("endtime", "6000-01-01T01:01:01")))   
return ""
}
catch err:FORG0001 {
"
Check time related parameters syntax

Valid syntax: YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS, YYY-MM-DDTHH:MM:SS.ssssss
"
}

};


declare function stationutil:badrequest_error() {
(: declare output method locally to override default xml   :)
    util:declare-option("exist:serialize","method=text media-type=text/plain indent=yes")  ,  
     response:set-status-code(400) , 
     "Error 400: Bad request 
     
Syntax Error in Request

" ||
stationutil:syntax_network() ||
stationutil:syntax_station() ||
stationutil:syntax_channel() ||
stationutil:syntax_location() ||
stationutil:syntax_latitude() ||
stationutil:syntax_longitude() ||
stationutil:syntax_times() ||
"

Usage details are available from <SERVICE DOCUMENTATION URI>

Request: " || request:get-query-string()||
"

Request Submitted: " || current-dateTime() ||  
"

Service version: 1.1.50"

(:            response:set-status-code(404) , transform:transform(<Error>Error 404 - no matching inventory found</Error>, doc("error-translation.xsl"), ()):)
              

};


(:locationCode:)