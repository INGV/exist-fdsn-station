xquery version "3.1";

module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil";
import module namespace request = "http://exist-db.org/xquery/request";
declare default element namespace "http://www.fdsn.org/xml/station/1" ;
declare namespace ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";

(: Serialization cannot change during the same request no way to fix using another file like in util.xql :)
(:declare option exist:serialize "method=html5 media-type=text/html";:)
(:declare option output:method "html5";:)
(:declare option output:media-type "text/html";:)

declare %public variable $stationutil:parameters as map() :=stationutil:get_params_map();

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
(:   try {:)
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
(:   }:)
(: catch err:* {"NEVERMATCH"} :)
    
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
            return  $pattern     
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



(:YYYY-MM-DD:)
declare function stationutil:time_adjust( $mydatetime as xs:string ) as xs:string {
    
    if (not(matches($mydatetime,".*T.*"))) then $mydatetime||"T"||"00:00:00.0"
    else $mydatetime
    
};


(: TODO get-parameter :)
declare function stationutil:constraints_onchannel(
    $CreationDate as xs:dateTime*, 
    $TerminationDate as xs:dateTime* ) as xs:boolean 
    {
    try {    
    let $missing_startbefore := request:get-parameter("startbefore", "yes")
    let $missing_endbefore := request:get-parameter("endbefore", "yes")
    let $missing_startafter := request:get-parameter("startafter", "yes")
    let $missing_endafter := request:get-parameter("endafter", "yes")
    let $missing_starttime := request:get-parameter("stationutil:get-parameter", "yes")
    let $missing_endtime := request:get-parameter("endtime", "yes")
    let $startbefore := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("startbefore")))
    let $startafter := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("startafter")))
    let $endbefore := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("endbefore")))   
    let $endafter := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("endafter")))
    let $starttime := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("starttime")))
    let $endtime := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("endtime")))   
    
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
        let $network_param := stationutil:get-parameter("network")
        let $station_param := stationutil:get-parameter("station")
        let $channel_param := stationutil:get-parameter("channel")
        let $location_param := stationutil:get-parameter("location")
        let $CreationDate:= $channel/@startDate
        let $TerminationDate:= $channel/@endDate
        let $Latitude:= $channel/Latitude
        let $Longitude:=  $channel/Longitude    
        let $pattern:=stationutil:channel_pattern_translate($channel_param)
        let $locationpattern:=stationutil:location_pattern_translate($location_param)
        let $minlatitude := xs:decimal(stationutil:get-parameter("minlatitude"))
        let $maxlatitude := xs:decimal(stationutil:get-parameter("maxlatitude"))
        let $minlongitude := xs:decimal(stationutil:get-parameter("minlongitude"))
        let $maxlongitude := xs:decimal(stationutil:get-parameter("maxlongitude"))          
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
    
let $minlatitude := xs:decimal(stationutil:get-parameter("minlatitude"))
let $maxlatitude := xs:decimal(stationutil:get-parameter("maxlatitude"))
let $minlongitude := xs:decimal(stationutil:get-parameter("minlongitude"))
let $maxlongitude := xs:decimal(stationutil:get-parameter("maxlongitude"))   
(:I valori di default non hanno senso, se non sono passati i parametri bisogna saltare il check :)

let $network_param := stationutil:get-parameter("network")
let $station_param := stationutil:get-parameter("station")
let $channel_param := stationutil:get-parameter("channel")
let $location_param := stationutil:get-parameter("location")

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
        let $lat :=  $station/Latitude
        let $lon :=  $station/Longitude
    where
        stationutil:constraints_onchannel($CreationDate,$TerminationDate) 
        and stationutil:check_radius($lat,$lon)         
        and matches($networkcode, stationutil:network_pattern_translate($network_param) ) 
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
(:try {:)
let $minlatitude := xs:decimal(stationutil:get-parameter("minlatitude"))
let $maxlatitude := xs:decimal(stationutil:get-parameter("maxlatitude"))
let $minlongitude := xs:decimal(stationutil:get-parameter("minlongitude"))
let $maxlongitude := xs:decimal(stationutil:get-parameter("maxlongitude"))   
let $startbefore := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("startbefore")))
let $startafter := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("startafter")))
let $endbefore := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("endbefore")))   
let $endafter := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("endafter")))
let $starttime := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("starttime")))
let $endtime := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("endtime")))   
let $latitude := xs:decimal(stationutil:get-parameter("latitude"))
let $longitude := xs:decimal(stationutil:get-parameter("longitude"))
let $minradius := xs:decimal(stationutil:get-parameter("minradius"))
let $maxradius := xs:decimal(stationutil:get-parameter("maxradius"))
let $includerestricted := xs:string(stationutil:get-parameter("includerestricted"))

let $network := stationutil:get-parameter("network")
let $station := stationutil:get-parameter("station")
let $channel := stationutil:get-parameter("channel")
let $location := stationutil:get-parameter("location")
let $level := stationutil:get-parameter("level")

return if (
           not(stationutil:empty_parameter_check()) 
           or $minlatitude>90.0 or $maxlatitude > 90.0 or $minlatitude<-90.0 or $maxlatitude <-90.0
           or $minlatitude > $maxlatitude 
           or $minlongitude>180.0 or $maxlongitude > 180.0 or $minlongitude<-180.0 or $maxlongitude <-180.0
           or $minlongitude > $maxlongitude 
           or $latitude  >90.0  or $latitude  <  -90.0 
           or $longitude >180.0 or $longitude < -180.0
           or $minradius <0 or $minradius >= $maxradius
           or $maxradius <0 or $maxradius > 180.0 
           or $startbefore < $startafter
           or $endbefore < $endafter
           or $starttime > $endtime
           or not(matches($level,"network|station|channel|response"))
           or not($includerestricted="TRUE" or $includerestricted="FALSE")
           or (contains(stationutil:network_pattern_translate($network), "NEVERMATCH")) 
           or (contains(stationutil:station_pattern_translate($station), "NEVERMATCH")) 
           or (contains(stationutil:channel_pattern_translate($channel), "NEVERMATCH")) 
           or (contains(stationutil:location_pattern_translate($location), "NEVERMATCH"))
           ) then false() else true()
(:}:)
(:catch err:* {false()}:)
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

declare function stationutil:distance( $Latitude1 as xs:string , $Longitude1 as xs:string , $Latitude2 as xs:string , $Longitude2 as xs:string  ) as xs:decimal {
(: In radians :)
let $lat1 := xs:decimal($Latitude1)  * ( math:pi() div 180.0 )
let $lon1 := xs:decimal($Longitude1)  * ( math:pi() div 180.0 )

let $lat2 := xs:decimal($Latitude2)  * ( math:pi() div 180.0 )
let $lon2 := xs:decimal($Longitude2)  * ( math:pi() div 180.0 )

(: Distance in km R*fi , d = 6371 * arccos[ (sin(lat1) * sin(lat2)) + cos(lat1) * cos(lat2) * cos(long2 – long1) ] :)
let $d:=  180.0 div math:pi() * math:acos(  math:sin($lat1) * math:sin($lat2)  + math:cos($lat1) * math:cos($lat2) * math:cos($lon2 - $lon1) ) 
return $d
    
};    

declare function stationutil:check_radius( $Latitude1 as xs:string, $Longitude1 as xs:string ) as xs:boolean 
{
    let $latitude  := request:get-parameter("latitude","")
    let $longitude := request:get-parameter("longitude","")
    return
    if (request:get-parameter("latitude","") ="" or 
    request:get-parameter("longitude","")     ="" or 
    request:get-parameter("maxradius","")     ="" or 
    request:get-parameter("minradius","")     = "" ) then true() 
    else 
        stationutil:distance($Latitude1, $Longitude1, $latitude, $longitude) < xs:decimal(request:get-parameter("maxradius","")) and
        stationutil:distance($Latitude1, $Longitude1, $latitude, $longitude) > xs:decimal(request:get-parameter("minradius",""))
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



declare function stationutil:get_params_map() as map(*) {
    
let $startbefore := request:get-parameter("startbefore", "6000-01-01T01:01:01")
let $startafter := request:get-parameter("startafter", "1800-01-01T01:01:01")
let $endbefore := request:get-parameter("endbefore", "6000-01-01T01:01:01")   
let $endafter := request:get-parameter("endafter", "1800-01-01T01:01:01")
let $level := request:get-parameter("level", "network")
let $minradius := request:get-parameter("minradius", "0")
let $maxradius := request:get-parameter("maxradius", "180")
let $includerestricted := xs:string(request:get-parameter("includerestricted","TRUE"))

let $minlatitude1 := request:get-parameter("minlatitude",())
let $minlat := request:get-parameter("minlat",())
let $maxlatitude1 := request:get-parameter("maxlatitude", ())
let $maxlat := request:get-parameter("maxlat", ())
let $minlongitude1 := request:get-parameter("minlongitude",())
let $minlon := request:get-parameter("minlon",())
let $maxlongitude1 := request:get-parameter("maxlon", ())
let $maxlon := request:get-parameter("maxlongitude", ())
let $starttime1 := request:get-parameter("starttime", ())
let $start := request:get-parameter("start", ())
let $endtime1 := request:get-parameter("endtime", ())   
let $end := request:get-parameter("end", ())   
let $latitude1 := request:get-parameter("latitude",())
let $lat := request:get-parameter("lat",())
let $longitude1 := request:get-parameter("longitude", ())
let $lon := request:get-parameter("lon", ())
let $network1 := request:get-parameter("network", ())
let $net := request:get-parameter("net", ())
let $station1 := request:get-parameter("station", ())
let $sta := request:get-parameter("sta", ())
let $channel1 := request:get-parameter("channel", ())
let $cha := request:get-parameter("cha", ())
let $location1 := request:get-parameter("location", ())
let $loc := request:get-parameter("loc", ())

let $network:=if (exists($net)) then $net else if (exists($network1)) then $network1 else "*"
let $net := $network
let $station:=if (exists($sta)) then $sta else if (exists($station1)) then $station1 else "*" 
let $sta:=$station
let $channel:=if (exists($cha)) then $cha else if (exists($channel1)) then $channel1 else "*" 
let $cha:=$channel
let $location:=if (exists($loc)) then $loc else if (exists($location1)) then $location1 else "*" 
let $loc:=$location
let $latitude:=if (exists($lat)) then $lat else if (exists($latitude1)) then $latitude1 else "0"  
let $lat:=$latitude
let $longitude:=if (exists($lon)) then $lon else if (exists($longitude1)) then $longitude1 else "0"  
let $lon:=$longitude
let $minlatitude:=if (exists($minlat)) then $minlat else if (exists($minlatitude1)) then $minlatitude1 else "-90.0"
let $minlat:=$minlatitude
let $maxlatitude:=if (exists($maxlat)) then $maxlat else if (exists($maxlatitude1)) then $maxlatitude1 else "90.0"
let $maxlat:=$maxlatitude
let $minlongitude:=if (exists($minlon)) then $minlon else if (exists($minlongitude1)) then $minlongitude1 else "-180.0"  
let $minlon:=$minlongitude
let $maxlongitude:=if (exists($maxlon)) then $maxlon else if (exists($maxlongitude1)) then $maxlongitude1 else "180.0"  
let $maxlon:=$maxlongitude
let $starttime:=if (exists($start)) then $start else if (exists($starttime1)) then $starttime1 else "1800-01-01T01:01:01"  
let $start:=$starttime
let $endtime:=if (exists($end)) then $end else if (exists($endtime1)) then $endtime1 else "6000-01-01T01:01:01"  
let $end:=$endtime
return map {
"level" : $level, 
"location" : $location,
"loc" : $loc,
"channel" : $channel, 
"cha" : $cha, 
"station" : $station, 
"sta" : $sta, 
"network" : $network, 
"net" : $net, 
"includerestricted" : $includerestricted, 
"maxradius" : $maxradius, 
"minradius" : $minradius,
"longitude" : $longitude, 
"lon" : $lon,
"latitude" : $latitude,
"lat" : $lat,
"endtime" : $endtime, 
"end" : $end, 
"starttime" : $starttime, 
"start" : $start, 
"endafter" : $endafter, 
"endbefore" : $endbefore, 
"startafter" : $startafter, 
"startbefore" : $startbefore, 
"maxlongitude" : $maxlongitude, 
"maxlon" : $maxlon, 
"minlongitude" :$minlongitude,
"minlon" :$minlon,
"maxlatitude" : $maxlatitude, 
"maxlat" : $maxlat, 
"minlatitude" :$minlatitude,    
"minlat" :$minlat    
}
    
};

declare function stationutil:empty_parameter_check() as xs:boolean
{
try {
let $params_map:=stationutil:get_params_map()
return if (
count(
for $key in map:keys($params_map) 
 where ($params_map($key)="")
return $key) >0
) then false()
else true()
}
catch err:* {true()}
} ;


declare function stationutil:syntax_longitude() as xs:string{
try 
{
let $minlongitude := xs:decimal(stationutil:get-parameter("minlongitude"))
let $maxlongitude := xs:decimal(stationutil:get-parameter("maxlongitude"))
let $longitude := xs:decimal(stationutil:get-parameter("longitude"))
 
return 
    if ($minlongitude>180.0 or $maxlongitude > 180.0 or $minlongitude<-180.0 or $maxlongitude <-180.0 or $longitude>180.0 or $longitude <-180.0) then 
" 
Must be -180 < longitude < 180
"
else ""     
}
     catch err:* {
"
Syntax error in longitude parameter
"        
    } 
};

declare function stationutil:syntax_latitude() as xs:string{
try 
{
let $minlatitude := xs:decimal(stationutil:get-parameter("minlatitude"))
let $maxlatitude := xs:decimal(stationutil:get-parameter("maxlatitude"))
let $latitude := xs:decimal(stationutil:get-parameter("latitude"))

return 
    if ( $minlatitude>90.0 or $maxlatitude > 90.0 or $minlatitude<-90.0 or $maxlatitude <-90.0 or $latitude> 90.0 or $latitude < -90.0) 
    then
        "
Must be -90 < latitude < 90
"
    else ""
}
    catch err:* {
"
Syntax error in latitude parameter
"        
    }
};

declare function stationutil:syntax_radius() as xs:string{
try {
let $minradius := xs:decimal(request:get-parameter("minradius","0"))
let $maxradius := xs:decimal(request:get-parameter("maxradius", "180"))

return 
    if (  ($maxradius - $minradius) <=0  or $maxradius<0 or $minradius<0  or $maxradius >180.0) 
    then
        "
Must be 0<minradius<maxradius<=180
"
    else
    ""
}
catch err:* {
"
Syntax Error in radius parameters
"
    
}
};


declare function stationutil:syntax_location() as xs:string{
try {
let $location := xs:string(stationutil:get-parameter("location"))

return 
if (contains(stationutil:location_pattern_translate($location), "NEVERMATCH")) 
    then
        "
Check location parameter
"
    else  ""
}
    catch err:* {
"
Syntax error in location parameter
"        
}

};

declare function stationutil:syntax_channel() as xs:string{
try {    
let $channel := xs:string(stationutil:get-parameter("channel"))

return 
if (contains(stationutil:channel_pattern_translate($channel), "NEVERMATCH")) 
    then
        "
Check channel parameter
"
    else  ""
}
    catch err:* {
"
Syntax error in channel parameter
"        
    }
};


declare function stationutil:syntax_station() as xs:string{
try {        
let $station := xs:string(stationutil:get-parameter("station"))

return 
if (contains(stationutil:station_pattern_translate($station), "NEVERMATCH")) 
    then
        "
Check station parameter
"
    else  ""
}
catch err:* {
"
Syntax error in station parameter
"        
    }
};

declare function stationutil:syntax_network() as xs:string{
try {            
let $network := xs:string(stationutil:get-parameter("network"))

return 
    if (contains(stationutil:network_pattern_translate($network), "NEVERMATCH")) 
    then
"
Check network parameter
"
    else  ""
}
catch err:* {
"
Syntax error in network parameter
"        
}
};

declare function stationutil:syntax_includerestricted() as xs:string{
    
let $includerestricted := xs:string(request:get-parameter("includerestricted","TRUE"))

return 
    if (not( upper-case($includerestricted)="TRUE" or upper-case($includerestricted)="FALSE"))
    then
"
The includerestricted parameter must be TRUE or FALSE
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

declare function stationutil:empty_parameter_error() as xs:string
{
try {
(:let $params_map:=stationutil:get_params_map():)
(:let $dummy :=stationutil:adiust_map_params():)
let $params_map:=$stationutil:parameters
return string-join(
for $key in map:keys($params_map) 

return if ( $params_map($key)="" ) 
           then 
"
Parameter " || $key || " cannot be empty
" 
            else ""
   
)

}
catch err:* {"Error checking parameters"}
} ;


declare function stationutil:debug_parameter_error() as xs:string
{
try {
(:let $params_map:=stationutil:get_params_map():)
(:let $dummy :=stationutil:adiust_map_params():)
let $params_map:=$stationutil:parameters
return string-join(
for $key in map:keys($params_map) 

return if ( $params_map($key)="" ) 
           then 
"
Parameter " || $key || " cannot be empty
" 
            else $key || " : " || $params_map($key) || "
            
"
   
)

}
catch err:* {"Error checking parameters"}
} ;


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
stationutil:syntax_radius() ||
stationutil:syntax_includerestricted() ||
stationutil:empty_parameter_error() ||
stationutil:debug_parameter_error() ||
"

Usage details are available from <SERVICE DOCUMENTATION URI>

Request: " || request:get-query-string()||
"

Request Submitted: " || current-dateTime() ||  
"

Service version: 1.1.50"

(:            response:set-status-code(404) , transform:transform(<Error>Error 404 - no matching inventory found</Error>, doc("error-translation.xsl"), ()):)
              

};



declare function stationutil:get-parameter($k as xs:string) as xs:string
{
    $stationutil:parameters($k)
    
};





(: TODO gestire restrictedStatus :)

(:locationCode:)