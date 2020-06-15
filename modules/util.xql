xquery version "3.1";

module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil";
import module namespace request = "http://exist-db.org/xquery/request";
declare default element namespace "http://www.fdsn.org/xml/station/1" ;
declare namespace ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";

(: Serialization cannot change during the same request, must be changed into the function :)
(:declare option exist:serialize "method=html5 media-type=text/html";:)
(:declare option output:method "html5";:)
(:declare option output:media-type "text/html";:)

(:BEWARE the order matters !!! :)
declare %public variable $stationutil:default_past_time as xs:string := "0001-01-01T00:00:00";
declare %public variable $stationutil:default_future_time as xs:string := "10001-01-01T00:00:00";
declare %public variable $stationutil:parameters as map() := if ( request:get-method() eq "POST")  then stationutil:alternate_parameters()  else stationutil:get_params_map(); 
(:declare %public variable $stationutil:parameters as map() := map{};:)


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
            let $pattern:= replace( $token, "\*", ".*")               
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
            let $pattern:= replace( $token, "\*", ".*")               
            let $pattern:= translate( $pattern, "?", ".")
            (: * -> 0 or more characters, ? exactly one character :)                
        return "^"||$pattern||"$"
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
            let $pattern:= replace( $token, "\*", ".*")            
            let $pattern:= translate( $pattern, "?", ".")
                (: every character will remain the same, only * and ? become . ():)
             return "^"||$pattern||"$"     
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
(:   every character will remain the same, only * and ? changes, no location can still be one character :)
            return
            if (string-length($pattern)<2) then 
                    "NEVERMATCH" 
                else 
                    "^"||$pattern||"$"  
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


declare function stationutil:constraints_onchannel(
    $CreationDate as xs:dateTime*, 
    $TerminationDate as xs:dateTime* ) as xs:boolean 
    {
    try {    
    let $string_startbefore := stationutil:get-parameter("startbefore")
    let $string_endbefore := stationutil:get-parameter("endbefore")
    let $string_startafter := stationutil:get-parameter("startafter")
    let $string_endafter := stationutil:get-parameter("endafter")
    let $string_starttime := stationutil:get-parameter("starttime")
    let $string_endtime := stationutil:get-parameter("endtime")
    let $startbefore := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("startbefore")))
    let $startafter := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("startafter")))
    let $endbefore := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("endbefore")))   
    let $endafter := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("endafter")))
    let $starttime := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("starttime")))
    let $endtime := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("endtime")))   
    return    
        (($string_starttime=$stationutil:default_past_time) or($CreationDate >= $starttime)) and 
        (($string_endtime=$stationutil:default_future_time) or  (not(empty($TerminationDate)) and ($TerminationDate <= $endtime))) and
        (($string_startbefore=$stationutil:default_future_time) or ($CreationDate < $startbefore)) and 
        (($string_startafter=$stationutil:default_past_time) or($CreationDate > $startafter))  and
        (($string_endbefore=$stationutil:default_future_time) or  (not(empty($TerminationDate)) and ($TerminationDate < $endbefore))) and
        (($string_endafter=$stationutil:default_past_time) or  (empty($TerminationDate)) or ($TerminationDate > $endafter))   
    }
    catch err:FORG0001 {false()}
};



declare function stationutil:channel_exists() as xs:boolean
{
(:try {    :)
let $minlatitude := xs:decimal(stationutil:get-parameter("minlatitude"))
let $maxlatitude := xs:decimal(stationutil:get-parameter("maxlatitude"))
let $minlongitude := xs:decimal(stationutil:get-parameter("minlongitude"))
let $maxlongitude := xs:decimal(stationutil:get-parameter("maxlongitude"))   
let $network_param := stationutil:get-parameter("network")
let $station_param := stationutil:get-parameter("station")
let $channel_param := stationutil:get-parameter("channel")
let $location_param := stationutil:get-parameter("location")
let $includerestricted := stationutil:get-parameter("includerestricted")

return 

if (not(empty(
for $item in collection("/db/apps/fdsn-station/Station/")

    let $Latitude:= $item/FDSNStationXML/Network/Station/Latitude
    let $Longitude:= $item/FDSNStationXML/Network/Station/Longitude

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
        let $networkrestrictedStatus := $network/@restrictedStatus
        let $stationrestrictedStatus := $station/@restrictedStatus        
        let $channelrestrictedStatus := $channel/@restrictedStatus    
    where
        stationutil:constraints_onchannel($CreationDate,$TerminationDate) 
        and stationutil:check_radius($lat,$lon)  
        and 
        (upper-case($includerestricted)="TRUE" or ( stationutil:check_restricted($networkrestrictedStatus)
        and stationutil:check_restricted($stationrestrictedStatus)        
        and stationutil:check_restricted($channelrestrictedStatus)))   
        and matches($networkcode, stationutil:network_pattern_translate($network_param) ) 
        and matches($stationcode, stationutil:station_pattern_translate($station_param) )
        and matches ($selchannelcode, stationutil:channel_pattern_translate($channel_param))        
        and matches ($selchannellocationcode,stationutil:location_pattern_translate($location_param))
        return $selchannelcode 
    )))
    then true()
    else false()
(:}:)
(:catch err:* {false()}    :)
};



declare function stationutil:channel_exists_test() as xs:boolean
{
(:try {    :)
let $minlatitude := xs:decimal(stationutil:get-parameter("minlatitude"))
let $maxlatitude := xs:decimal(stationutil:get-parameter("maxlatitude"))
let $minlongitude := xs:decimal(stationutil:get-parameter("minlongitude"))
let $maxlongitude := xs:decimal(stationutil:get-parameter("maxlongitude"))   
let $network_param := stationutil:get-parameter("network")
let $station_param := stationutil:get-parameter("station")
let $channel_param := stationutil:get-parameter("channel")
let $location_param := stationutil:get-parameter("location")
let $includerestricted := stationutil:get-parameter("includerestricted")

return 

    some $item in collection("/db/apps/fdsn-station/Station/")
    satisfies (
    $item/FDSNStationXML/Network/Station/Latitude > $minlatitude 
    and $item/FDSNStationXML/Network/Station/Latitude < $maxlatitude 
    and $item/FDSNStationXML/Network/Station/Longitude > $minlongitude 
    and $item/FDSNStationXML/Network/Station/Longitude < $maxlongitude 
    and 
        stationutil:constraints_onchannel($item//Network/Station/Channel/@startDate , $item//Network/Station/Channel/@endDate) 
        and stationutil:check_radius($item//Network/Station/Latitude,$item//Network/Station/Longitude)  
        and 
        (upper-case($includerestricted)="TRUE" or ( stationutil:check_restricted($item//Network/@restrictedStatus)
        and stationutil:check_restricted($item//Network/Station/@restrictedStatus)        
        and stationutil:check_restricted($item//Network/Station/Channel/@restrictedStatus)))   
        and matches($item//Network/@code, stationutil:network_pattern_translate($network_param) ) 
        and matches($item//Network/Station/@code, stationutil:station_pattern_translate($station_param) )
        and matches($item//Network/Station/Channel/@code, stationutil:channel_pattern_translate($channel_param))        
        and matches($item//Network/Station/Channel/@locationCode,stationutil:location_pattern_translate($location_param))
    )

(:}:)
(:catch err:* {false()}    :)
};


declare function stationutil:check_parameters_limits() as xs:boolean 
{

try {
(:let $stationutil:parameters  := stationutil:get_params_map():)
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
let $format := stationutil:get-parameter("format")

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
           or not( $format ="xml" or $format="text")           
           or (contains(stationutil:network_pattern_translate($network), "NEVERMATCH")) 
           or (contains(stationutil:station_pattern_translate($station), "NEVERMATCH")) 
           or (contains(stationutil:channel_pattern_translate($channel), "NEVERMATCH")) 
           or (contains(stationutil:location_pattern_translate($location), "NEVERMATCH"))
           ) then false() else true()
}
catch err:* {false()}

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
    let $latitude  := stationutil:get-parameter("latitude")
    let $longitude := stationutil:get-parameter("longitude")
    let $maxradius := stationutil:get-parameter("maxradius")
    let $minradius := stationutil:get-parameter("minradius")
    return
    if ($latitude ="0" and $longitude ="0" and $maxradius ="180" and $minradius = "0" ) then true() 
    else 
        stationutil:distance($Latitude1, $Longitude1, $latitude, $longitude) < xs:decimal($maxradius) and
        stationutil:distance($Latitude1, $Longitude1, $latitude, $longitude) > xs:decimal($minradius)
};

(: TODO open partial restricted:)
declare function stationutil:check_restricted($restrictedStatus as xs:string * ) as xs:boolean {
    let $includerestricted:=stationutil:get-parameter("includerestricted")
    return
    some $rs in $restrictedStatus
    satisfies 
    if (upper-case($includerestricted)="TRUE") then true()
    else (not($rs="restricted"))
};

declare function stationutil:nodata_error() {
(: declare output method locally to override default xml   :)
    util:declare-option("exist:serialize","method=text media-type=text/plain indent=no")  ,  
    if (matches(request:get-parameter("nodata", "204"),"404")) 
    then
        (
             response:set-status-code(404) , "Error 404 - no matching inventory found"
        )
    else if (matches(request:get-parameter("nodata", "204"),"204")) then
        response:set-status-code(204) 
    else 
        response:set-status-code(400) 
};


(: Here we map the request params in stationutil:parameters  :)
declare function stationutil:get_params_map() as map(*) {

let $startbefore := request:get-parameter("startbefore", $stationutil:default_future_time)
let $startafter := request:get-parameter("startafter", $stationutil:default_past_time)
let $endbefore := request:get-parameter("endbefore", $stationutil:default_future_time)   
let $endafter := request:get-parameter("endafter", $stationutil:default_past_time)
let $level := request:get-parameter("level", "network")
let $minradius := request:get-parameter("minradius", "0")
let $maxradius := request:get-parameter("maxradius", "180")
let $includerestricted := upper-case(xs:string(request:get-parameter("includerestricted","TRUE")))
let $format := request:get-parameter("format","xml")

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
let $starttime:=if (exists($start)) then $start else if (exists($starttime1)) then $starttime1 else $stationutil:default_past_time  
let $start:=$starttime
let $endtime:=if (exists($end)) then $end else if (exists($endtime1)) then $endtime1 else $stationutil:default_future_time
let $end:=$endtime




let $result := map {
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
"format" : $format,
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


return $result
};


declare function stationutil:alternate_parameters1() as map(*) {
try
{
    
        let $POST_DATA:= util:base64-decode(request:get-data())
        let $sequenceoflines :=stationutil:lines($POST_DATA)
(:        let $p:= util:log("error", "Before cicle " || $POST_DATA ):)
    return    
    map:merge( 

        
    for $line in $sequenceoflines
        return
         if (matches($line,"="))
            then (
                let $key_val := tokenize($line,"=")
                let $p:= util:log("error", "Matched " || $key_val[1] || "=" || $key_val[2] )
                return map:entry($key_val[1], $key_val[2]) 
            )
            else ()
 ) 
}
catch err:* {
    let $m := map {}
    return $m
    
}
};


declare function stationutil:alternate_parameters() as map(*) {
    (:let $res :=$result:)
(:let $res := map{}:)
(:let $result := map{}:)

let $map := 
map:merge( 
        let $POST_DATA:= util:base64-decode(request:get-data())
        let $sequenceoflines :=stationutil:lines($POST_DATA)
        let $p:= util:log("error", "Before cicle " || $POST_DATA )
        
    for $line in $sequenceoflines
        return
            if (matches($line,"="))
            then (
                let $key_val := tokenize($line,"=")
                let $p:= util:log("error", "Matched " || $key_val[1] || "=" || $key_val[2] )
                return map:entry($key_val[1], $key_val[2]) 
                )
            else ()
 ) 
(::)
(:for $key in map:keys($map) let $D := util:log("error", "Reading seqmap " ||$key || "=" || $map($key) )    :)

let $res := $map

(:for $key in map:keys($res) :)
(:let $D := util:log("error", "Reading result " ||$key || "=" || $res($key) )    :)
return $map
};


(: TODO do not use count() :)
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
let $minradius := xs:decimal(stationutil:get-parameter("minradius"))
let $maxradius := xs:decimal(stationutil:get-parameter("maxradius"))

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
    
let $includerestricted := xs:string(stationutil:get-parameter("includerestricted"))

return 
    if (not( upper-case($includerestricted)="TRUE" or upper-case($includerestricted)="FALSE"))
    then
"
The includerestricted parameter must be TRUE/true or FALSE/false
"
    else  ""

};

declare function stationutil:syntax_format() as xs:string{
    
let $format := xs:string(stationutil:get-parameter("format"))

return 
    if (not( $format ="xml" or $format="text"))
    then
"
The format parameter must be xml or text
"
    else  ""

};


declare function stationutil:syntax_times() as xs:string {
try 
{    
let $startbefore := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("startbefore")))
let $startafter := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("startafter")))
let $endbefore := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("endbefore")))   
let $endafter := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("endafter")))
let $starttime := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("starttime")))
let $endtime := xs:dateTime(stationutil:time_adjust(stationutil:get-parameter("endtime")))   
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
(:try {:)
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

(:}:)
(:catch err:* {"Error checking parameters"}:)
} ;


declare function stationutil:debug_parameter_error() as xs:string
{
(:try {:)
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

(:}:)
(:catch err:* {"Error checking parameters"}:)
} ;

declare function stationutil:post_error() as xs:string {

if ( request:get-method() eq "POST" ) then    
    util:base64-decode(request:get-data())
else 
    ""
 
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
stationutil:syntax_radius() ||
stationutil:syntax_includerestricted() ||
stationutil:empty_parameter_error() ||
stationutil:syntax_format() ||
(:stationutil:post_error() ||:)
stationutil:debug_parameter_error() ||
"

Usage details are available from <SERVICE DOCUMENTATION URI>

Request: " || request:get-query-string()||
"

Request Submitted: " || current-dateTime() ||  
"

Service version: 1.1.50"

(: response:set-status-code(404) , transform:transform(<Error>Error 404 - no matching inventory found</Error>, doc("error-translation.xsl"), ()) :)
              

};


declare function stationutil:get-parameter($k as xs:string) as xs:string
{
      if ( empty($stationutil:parameters($k))  ) then  "*" else  $stationutil:parameters($k) 
};

declare function stationutil:lines
  ( $arg as xs:string? )  as xs:string* {

(:   tokenize($arg, '(\r\n?|\n\r?)'):)
   tokenize($arg, '[\n\r]+', "m")
   
 } ;

(:declare function stationutil:map_post() {:)
(:    let $POST_DATA:= util:base64-decode(request:get-data()):)
(:    let $sequenceoflines :=stationutil:lines($POST_DATA):)
(:    for $line in $sequenceoflines:)
(:    return:)
(:    if (matches($line,"=")) :)
(:        then ( :)
(:            let $key_val := tokenize($line,"="):)
(:            let $stationutil:parameters := map:put($stationutil:parameters, $key_val[0], $key_val[1]):)
(:            return "":)
(:        ):)
(:        else let $NSLCSE := tokenize($line," ") :)
(:        return "":)
(:};:)


(: TODO gestire restrictedStatus :)

(:locationCode:)
 

declare function stationutil:query_network_shortcut_main() as element() {
if (stationutil:check_parameters_limits()) then 
    if (stationutil:channel_exists()) then 
<FDSNStationXML xmlns="http://www.fdsn.org/xml/station/1" xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" schemaVersion="1.0" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.0.xsd">
  <Source>eXistDB</Source>
  <Sender>INGV-ONT</Sender>
  <Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.0</Module>
  <ModuleURI>"{request:get-uri()}?{request:get-query-string()}"</ModuleURI>
  <Created>{current-dateTime()}</Created>
{

for $item in collection("/db/apps/fdsn-station/Station/")

for $network in $item//Network  

    let $network_param := stationutil:get-parameter("network")
    let $networkcode := $network/@code
    let $startDate := $network/@startDate
    let $endDate := $network/@endDate
    let $restrictedStatus:=$network/@restrictedStatus
    let $Description := $network/Description
    let $ingv_identifier := $network/ingv:Identifier
    let $network_pattern:=stationutil:network_pattern_translate($network_param)
    where
        matches($networkcode,  $network_pattern)
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
        order by $station/@code
        return
        if ( matches(stationutil:get-parameter("level"),"channel")) 
            then stationutil:remove-elements($station,"Stage")
            else $station
}
</Network>        
        

}   
</FDSNStationXML>
else
    stationutil:nodata_error()
else 
    stationutil:badrequest_error()
};



(:  :)
 
 
declare function stationutil:query_network_main()  {
    
if (stationutil:check_parameters_limits()) then 
    if (stationutil:channel_exists()) then 
<FDSNStationXML xmlns="http://www.fdsn.org/xml/station/1" xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" schemaVersion="1.0" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.0.xsd">
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
 
 
(: :)


declare function stationutil:query_station_main() as element() {
if (stationutil:check_parameters_limits()) then 
    if (stationutil:channel_exists()) then  
<FDSNStationXML xmlns="http://www.fdsn.org/xml/station/1" xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" schemaVersion="1.0" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.0.xsd">

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
(: TODO ????  and stationutil:check_radius($Latitude,$Longitude):)
(: TODO includerestricted :)
for $network in $item//Network  
    let $networkcode := $network/@code
    let $station:=$network/Station
    let $stationcode:=$network/Station/@code    
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
        stationutil:constraints_onchannel( $CreationDate, $TerminationDate ) and
        stationutil:check_radius($lat,$lon) and 
        matches($networkcode,  $network_pattern ) 
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
        {
        for $station in $network/Station
            let $stationcode:=$station/@code
            let $stationstartDate := $station/@startDate
            let $stationendDate := $station/@endDate
            let $stationrestrictedStatus := $station/@restrictedStatus
            let $channel :=$station/Channel
            let $channelcode:=$channel/@code
            let $channellocationcode:=$channel/@locationCode
            
            let $Latitude:=  $station/Latitude
            let $Longitude:= $station/Longitude 
            let $CreationDate:= $channel/@startDate
            let $TerminationDate:= $channel/@endDate 
            let $networkcode:=$network/@code
            let $pattern:=stationutil:channel_pattern_translate($channel_param)
            let $location_pattern:=stationutil:location_pattern_translate($location_param)    
        where 
            xs:decimal($Latitude)  > $minlatitude and  
            xs:decimal($Latitude)  < $maxlatitude and 
            xs:decimal($Longitude) > $minlongitude and 
            xs:decimal($Longitude) < $maxlongitude and 
            stationutil:constraints_onchannel( $CreationDate, $TerminationDate ) and          
            matches ($channelcode,  $pattern ) and
            matches($channellocationcode,$location_pattern) 
            and 
            stationutil:check_radius($Latitude,$Longitude) 
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
            </Station>
}
</Network>
}   
</FDSNStationXML>
else
    stationutil:nodata_error()
else 
    stationutil:badrequest_error()
};

(::)


(: TODO includerestricted :)
declare function stationutil:query_channel_main() as element() {
if (stationutil:check_parameters_limits()) then 
    if (stationutil:channel_exists()) then 

<FDSNStationXML xmlns="http://www.fdsn.org/xml/station/1" xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" schemaVersion="1.0" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.0.xsd">

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
    let $CreationDate:= $item/FDSNStationXML/Network/Station/Channel/@startDate
    let $TerminationDate:= $item/FDSNStationXML/Network/Station/Channel/@endDate
where   
    $Latitude  > $minlatitude and  
    $Latitude  < $maxlatitude and 
    $Longitude > $minlongitude and 
    $Longitude < $maxlongitude and
    stationutil:constraints_onchannel($CreationDate, $TerminationDate ) 
    
for $network in $item//Network  
    let $networkcode := $network/@code
    let $station:=$network/Station
    let $stationcode:=$station/@code
    let $lat := $station/Latitude
    let $lon := $station/Longitude       
    let $channel:=$station/Channel
    let $channelcode:=$channel/@code
    let $channellocationcode:=$channel/@locationCode
    let $startDate := $network/@startDate
    let $endDate := $network/@endDate
    let $restrictedStatus:=$network/@restrictedStatus
    let $Description := $network/Description
    let $ingv_identifier := $network/ingv:Identifier
    where
        stationutil:constraints_onchannel( $CreationDate, $TerminationDate ) and    
        stationutil:check_radius($lat,$lon) and            
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
            let $lat := $station/Latitude
            let $lon := $station/Longitude               
            let $CreationDate:= $channel/@startDate
            let $TerminationDate:= $channel/@endDate 
            let $networkcode:=$network/@code
            let $pattern:=stationutil:channel_pattern_translate($channel_param)
            let $location_pattern:=stationutil:location_pattern_translate($location_param)
        where 
            $Latitude  > $minlatitude and  
            $Latitude  < $maxlatitude and 
            $Longitude > $minlongitude and 
            $Longitude < $maxlongitude and 
            stationutil:constraints_onchannel( $CreationDate, $TerminationDate ) and          
            stationutil:check_radius($lat,$lon) and            
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
                    stationutil:constraints_onchannel($CreationDate, $TerminationDate ) and
                    stationutil:check_radius($lat,$lon) and            
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
                    stationutil:constraints_onchannel( $CreationDate, $TerminationDate ) and
                    stationutil:check_radius($lat,$lon) and            
                    matches ($selchannelcode,  $pattern )and
                    matches ($channellocationcode,  $location_pattern)
                return stationutil:remove-elements($channel,"Stage")
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
};    
 
(: :)
 
(: TODO includerestricted :)

declare function stationutil:query_response_main() as element() { 
if (stationutil:check_parameters_limits()) then 
    if (stationutil:channel_exists()) then 
(:if (stationutil:check_parameters_limits() ) then     :)
<FDSNStationXML xmlns="http://www.fdsn.org/xml/station/1" xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" schemaVersion="1.0" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.0.xsd">
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
let $CreationDate:= $item/FDSNStationXML/Network/Station/Channel/@startDate
let $TerminationDate:= $item/FDSNStationXML/Network/Station/Channel/@endDate

where 
    stationutil:constraints_onchannel( $CreationDate, $TerminationDate ) and
    $Latitude  > $minlatitude and  
    $Latitude  < $maxlatitude and 
    $Longitude > $minlongitude and 
    $Longitude < $maxlongitude 

for $network in $item//Network  
    let $networkcode := $network/@code
    let $stationcode:=$network/Station/@code
    let $station:=$network/Station
    let $lat := $station/Latitude
    let $lon := $station/Longitude    
    let $channel:=$station/Channel
    let $channelcode:=$channel/@code
    let $channellocationcode:=$channel/@locationCode
    let $startDate := $network/@startDate
    let $endDate := $network/@endDate
    let $restrictedStatus:=$network/@restrictedStatus
    let $Description := $network/Description
    let $ingv_identifier := $network/ingv:Identifier
    where
        stationutil:constraints_onchannel( $CreationDate, $TerminationDate ) and
        stationutil:check_radius($lat,$lon) and     
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
            let $lat := $station/Latitude
            let $lon := $station/Longitude
            let $CreationDate:= $channel/@startDate
            let $TerminationDate:= $channel/@endDate 
            let $networkcode:=$network/@code
            let $pattern:=stationutil:channel_pattern_translate($channel_param)
            let $location_pattern:=stationutil:location_pattern_translate($location_param)
        where 
            $Latitude  > $minlatitude and  
            $Latitude  < $maxlatitude and 
            $Longitude > $minlongitude and 
            $Longitude < $maxlongitude and
            stationutil:constraints_onchannel( $CreationDate, $TerminationDate ) and  
            stationutil:check_radius($lat,$lon) and
            matches ($channelcode,  $pattern ) and
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
                    stationutil:constraints_onchannel( $CreationDate, $TerminationDate ) and
                    stationutil:check_radius($lat,$lon) and    
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
                    stationutil:constraints_onchannel( $CreationDate, $TerminationDate ) and                    
                    stationutil:check_radius($lat,$lon) and
                    matches ($selchannelcode,  $pattern )and
                    matches ($channellocationcode,  $location_pattern)
                return $channel
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
}; 