xquery version "3.1";

module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil";
import module namespace request = "http://exist-db.org/xquery/request";
import module namespace util = "http://exist-db.org/xquery/util";

declare default element namespace "http://www.fdsn.org/xml/station/1" ;
declare namespace ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";


(: Serialization cannot change during the same request, must be changed into the function :)
(:declare option exist:serialize "method=html5 media-type=text/html";:)
(:declare option output:method "html5";:)
(:declare option output:media-type "text/html";:)
(:declare option exist:serialize "method=xhtml media-type=application/xhtml+html indent=no";:)
(:BEWARE the order matters !!! :)
(:TODO update limits with javascript limits:)
declare %public variable $stationutil:default_past_time  :="0001-01-01T00:00:00";
declare %public variable $stationutil:default_future_time :="10001-01-01T00:00:00";

declare %public variable $stationutil:default_past_time_as_datetime  :=  xs:dateTime("0001-01-01T00:00:00");
declare %public variable $stationutil:default_future_time_as_datetime :=  xs:dateTime("10001-01-01T00:00:00");


declare %public variable $stationutil:default_nodata as xs:string := "204";

declare %public variable $stationutil:postdata as xs:string* := if (request:get-method() eq "POST") then stationutil:setpostdata() else "";

declare %public variable $stationutil:parameters as map() := if (request:get-method() eq "POST")  then stationutil:set_parameters_row_from_POST()  else stationutil:set_parameters_row_from_GET(); 

declare %public variable $stationutil:parameters_table as map()* := if (request:get-method() eq "POST")  then stationutil:set_parameters_table()  else stationutil:set_parameters_row_from_GET(); 


(: Functions declarations  :)

(: Count the total number of stations of the network with code netcode :)
declare function stationutil:stationcount($netcode as xs:string) as item()
{
    count( collection("/db/apps/fdsn-station/Station/")//Network[@code=$netcode]/Station)
};


declare function stationutil:sanitize ($input as xs:string) as xs:string
{
  let $output:=translate( $input, "|", "-")    
  return $output  
};

(: optimization not requested :)
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


(: optimization not requested :)
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

(: optimization not requested :)
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

(: optimization not requested :)
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



(: Adjust datetimes to fdsn standard format YYYY-MM-DD:)
declare function stationutil:time_adjust( $mydatetime as xs:string ) as xs:string {
    
    if (not(matches($mydatetime,".*T.*"))) then $mydatetime||"T"||"00:00:00.0"
    else $mydatetime
    
};


(: Use the "some" clause to check some channel meet criteria :)

declare function stationutil:constraints_onchannel(
    $parameters as map()*,
    $CreationDate as xs:dateTime*, 
    $TerminationDate as xs:dateTime* ) as xs:boolean 
    {
    try {    
    some $NSLCSE in $parameters
    satisfies    
        (($NSLCSE("starttime")=$stationutil:default_past_time_as_datetime) or($CreationDate >= $NSLCSE("starttime"))) and 
        (($NSLCSE("endtime")=$stationutil:default_future_time_as_datetime) or empty($TerminationDate) or  (not(empty($TerminationDate)) and ($TerminationDate <=  $NSLCSE("endtime")))) and
        (($NSLCSE("startbefore")=$stationutil:default_future_time_as_datetime) or ($CreationDate < $NSLCSE("startbefore"))) and 
        (($NSLCSE("startafter")=$stationutil:default_past_time_as_datetime) or($CreationDate > $NSLCSE("startafter")))  and
        (($NSLCSE("endbefore")=$stationutil:default_future_time_as_datetime) or  (not(empty($TerminationDate)) and ($TerminationDate < $NSLCSE("endbefore")))) and
        (($NSLCSE("endafter")=$stationutil:default_past_time_as_datetime) or  (empty($TerminationDate)) or ($TerminationDate > $NSLCSE("endafter")))       
    }
    catch err:FORG0001 {false()}
};


(: Introduced to avoid call to pattern translate:)
declare function stationutil:constraints_onchannel_patterns(
    $parameters as map()*,
    $networkcode as xs:string*, 
    $stationcode as xs:string*,
    $channelcode as xs:string*, 
    $locationcode as xs:string*
    ) as xs:boolean 
    {
    try {    
    some $NSLCSE in $parameters , $n in $networkcode, $s in $stationcode, $c in $channelcode, $l in $locationcode
    satisfies    
            
            matches($s, $NSLCSE("station_pattern"))
     and    matches($n, $NSLCSE("network_pattern")) 
     and    matches($c, $NSLCSE("channel_pattern")) 
     and    matches($l, $NSLCSE("location_pattern")) 
        
    }
    catch err:* {false()}
};


(: TODO or DONE? change check_radius for AQU like station: two networks, single station :)


declare function stationutil:channel_exists($parameters as map()*) as xs:boolean
{
try {    

some $item in collection("/db/apps/fdsn-station/Station/") , $condition in $parameters

satisfies 

        $item/FDSNStationXML/Network/Station/Latitude  > xs:decimal($condition("minlatitude"))
    and $item/FDSNStationXML/Network/Station/Latitude  < xs:decimal($condition("maxlatitude")) 
    and $item/FDSNStationXML/Network/Station/Longitude > xs:decimal($condition("minlongitude")) 
    and $item/FDSNStationXML/Network/Station/Longitude < xs:decimal($condition("maxlongitude")) 
    and stationutil:constraints_onchannel($condition,$item//Network/Station/Channel/@startDate,$item//Network/Station/Channel/@endDate) 
    and stationutil:check_radius($condition,$item//Network/Station/Latitude,$item//Network/Station/Longitude)  
    and stationutil:check_restricted($condition,$item//Network/@restrictedStatus)
    and stationutil:check_restricted($condition,$item//Network/Station/@restrictedStatus)        
    and stationutil:check_restricted($condition,$item//Network/Station/Channel/@restrictedStatus)   
    and matches($item//Network/@code, stationutil:network_pattern_translate($condition("network")) ) 
    and matches($item//Network/Station/@code, stationutil:station_pattern_translate($condition("station")) )
    and matches ($item//Network/Station/Channel/@code, stationutil:channel_pattern_translate($condition("channel")))        
    and matches ($item//Network/Station/Channel/@locationCode,stationutil:location_pattern_translate($condition("location")))

}
catch err:* {false()}    
};


declare function stationutil:check_parameters_limits( $parameters as map()*) as xs:boolean 
{

try {

not( 
some $NSLCSE in $parameters 
satisfies
 ( 
(:          not(stationutil:empty_parameter_check()) :)
 
           ($NSLCSE("level")="response" and $NSLCSE("format") ="text")
           or xs:decimal($NSLCSE("minlatitude"))>90.0 
           or xs:decimal($NSLCSE("maxlatitude")) > 90.0 
           or xs:decimal($NSLCSE("minlatitude"))<-90.0 
           or xs:decimal($NSLCSE("maxlatitude")) <-90.0
           or xs:decimal($NSLCSE("minlatitude")) > xs:decimal($NSLCSE("maxlatitude")) 
           or xs:decimal($NSLCSE("minlongitude"))>180.0 
           or xs:decimal($NSLCSE("maxlongitude")) > 180.0 
           or xs:decimal($NSLCSE("minlongitude"))<-180.0 
           or xs:decimal($NSLCSE("maxlongitude")) <-180.0
           or xs:decimal($NSLCSE("minlongitude")) > xs:decimal($NSLCSE("maxlongitude")) 
           or xs:decimal($NSLCSE("latitude"))  >90.0  or xs:decimal($NSLCSE("latitude"))  <  -90.0 
           or xs:decimal($NSLCSE("longitude")) >180.0 or xs:decimal($NSLCSE("longitude")) < -180.0
           or xs:decimal($NSLCSE("minradius")) <0 or xs:decimal($NSLCSE("minradius")) >= xs:decimal($NSLCSE("maxradius"))
           or xs:decimal($NSLCSE("maxradius")) <0 or xs:decimal($NSLCSE("maxradius")) > 180.0 
           or $NSLCSE("startbefore") < $NSLCSE("startafter")
           or $NSLCSE("endbefore") < $NSLCSE("endafter")
           or $NSLCSE("starttime") > $NSLCSE("endtime")
           or not(matches($NSLCSE("level"),"network|station|channel|response"))
           or not(xs:string($NSLCSE("includerestricted"))="TRUE" or xs:string($NSLCSE("includerestricted"))="FALSE")
           or not( $NSLCSE("format") ="xml" or $NSLCSE("format")="text")           
           or (contains(stationutil:network_pattern_translate($NSLCSE("network")), "NEVERMATCH")) 
           or (contains(stationutil:station_pattern_translate($NSLCSE("station")), "NEVERMATCH")) 
           or (contains(stationutil:channel_pattern_translate($NSLCSE("channel")), "NEVERMATCH")) 
           or (contains(stationutil:location_pattern_translate($NSLCSE("location")), "NEVERMATCH"))
           ) 
)           

}
catch err:* {false()}

} ;



declare function stationutil:remove-elements($input as element(), $remove-names as xs:string*) as element() {
   element {node-name($input) }
      {$input/@*,
       for $child in $input/node()[name(.)!=$remove-names]
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


(: Use "some" clause to find matches :)
declare function stationutil:check_radius( $parameter as map()*, $Latitude1 as xs:string*, $Longitude1 as xs:string* ) as xs:boolean 
{

    some $NSLCSE in $parameter
    satisfies 
    ($NSLCSE("latitude") ="0" and $NSLCSE("longitude") ="0" and $NSLCSE("maxradius") ="180" and $NSLCSE("minradius") = "0" ) or 
    (
        stationutil:distance($Latitude1, $Longitude1, $NSLCSE("latitude"), $NSLCSE("longitude")) < xs:decimal($NSLCSE("maxradius")) and
        stationutil:distance($Latitude1, $Longitude1, $NSLCSE("latitude"), $NSLCSE("longitude")) > xs:decimal($NSLCSE("minradius"))       ) 
    
};


(: TODO manage correctly open, partial, closed in station.xml match a channel station network if includerestricted=true or is open:)
declare function stationutil:check_restricted($parameter as map()*, $restrictedStatus as xs:string * ) as xs:boolean {
    some $rs in $restrictedStatus, $NSLCSE in $parameter
    satisfies 
    ($rs="open" or $rs="partial") or $NSLCSE("includerestricted")="TRUE"
};



(: Here we map the request params in stationutil:parameters  :)
declare function stationutil:set_parameters_row_from_GET() as map()* {

let $nodata := request:get-parameter("nodata", $stationutil:default_nodata)
let $startbefore := xs:dateTime(stationutil:time_adjust(request:get-parameter("startbefore", $stationutil:default_future_time)))
let $startafter := xs:dateTime(stationutil:time_adjust(request:get-parameter("startafter", $stationutil:default_past_time)))
let $endbefore := xs:dateTime(stationutil:time_adjust(request:get-parameter("endbefore", $stationutil:default_future_time)))   
let $endafter := xs:dateTime(stationutil:time_adjust(request:get-parameter("endafter", $stationutil:default_past_time)))

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
let $starttime:=if (exists($start)) then xs:dateTime(stationutil:time_adjust($start)) else if (exists($starttime1)) then xs:dateTime(stationutil:time_adjust($starttime1)) else $stationutil:default_past_time_as_datetime  
let $start:=$starttime
let $endtime:=if (exists($end)) then xs:dateTime(stationutil:time_adjust($end)) else if (exists($endtime1)) then xs:dateTime(stationutil:time_adjust($endtime1)) else $stationutil:default_future_time_as_datetime
let $end:=$endtime

(: 4 parametri di comodo per evitare le chiamate alle pattern_translate nella query traduco i pattern qui :)

let $network_pattern := stationutil:network_pattern_translate($network)
let $station_pattern := stationutil:station_pattern_translate($station)
let $channel_pattern := stationutil:channel_pattern_translate($channel)
let $location_pattern := stationutil:location_pattern_translate($location)

(: Specifica totale 25 parametri 12 alias :)
(: Gestiti 22 parametri 12 alias 
 :  3 opzionali e non definiti - matchtimeseries - updatedafter -includeavailability
 : 
 : in più i 4 di comodo
 : :)

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
"minlat" :$minlat, 
"nodata" :$nodata,
"network_pattern" :$network_pattern,
"station_pattern" :$station_pattern,
"channel_pattern" :$channel_pattern,
"location_pattern" :$location_pattern
}


let $p:= util:log("error", "GET nscl: " || $result("network_pattern") || " " || $result("station_pattern") || " "  || $result("channel_pattern") || " " || $result("location_pattern") || " ") 
 
return $result
};

(: FIXME request:get-data() cannot be called twice :)
declare function stationutil:setpostdata() as xs:string* {
util:base64-decode(request:get-data())    
};

declare function stationutil:getpostdata() as xs:string {
 string-join($stationutil:postdata)
};


declare function stationutil:sequenceoflines() as xs:string* {
let $sequenceoflines :=stationutil:lines($stationutil:postdata)
return $sequenceoflines     
};

declare function stationutil:set_parameters_table() as map()* {

(:let $p:= util:log("error", "POST: " ):)
let $sequenceoflines :=stationutil:lines($stationutil:postdata)
(:let $p:= util:log("error", "POST: " || $stationutil:postdata):)

(: A sequence of maps :)
let $NSLC :=
    for $line in $sequenceoflines
        return
         if (matches($line,"=") or $line="" )
            then ()
            else (
                let $key_val := tokenize($line,"\s+")
(:                let $p:= util:log("error", "Matched in set_parameters_table" || $key_val[1] || "," || $key_val[2] || "," || $key_val[3] || "," || $key_val[4]|| "," || $key_val[5] || "," || $key_val[6]):)
(: apply pattern translate and add related entries :)
                return map:merge((
                    map:entry("net", $key_val[1]), map:entry("network", $key_val[1]), map:entry("network_pattern",stationutil:network_pattern_translate($key_val[1])),
                    map:entry("sta", $key_val[2]), map:entry("station", $key_val[2]), map:entry("station_pattern",stationutil:station_pattern_translate($key_val[2])),
                    map:entry("loc", $key_val[3]), map:entry("location", $key_val[3]), map:entry("location_pattern",stationutil:location_pattern_translate($key_val[3])),
                    map:entry("cha", $key_val[4]) , map:entry("channel", $key_val[4]), map:entry("channel_pattern",stationutil:channel_pattern_translate($key_val[4])),
                    map:entry("start", $key_val[5]), map:entry("starttime", $key_val[5]), 
                    map:entry("end", $key_val[6]), map:entry( "endtime", $key_val[6]), 
                    $stationutil:parameters) ) 
            )
(:NET STA LOC CHA STARTTIME ENDTIME più tutti gli altri parametri ripetuti:)

for $i in $NSLC
let $p:= util:log("error", "POST: " || $i("network_pattern") || " " || $i("station_pattern") || " "  || $i("channel_pattern") || " " || $i("location_pattern") || " ") 
 
return $NSLC
    
};

(: This function read parameters from POST values:)
declare function stationutil:set_parameters_row_from_POST() as map(*) {
try
{
(: SET defaults for 10 non alias parameters :)

let $params_default := map {
"nodata" : $stationutil:default_nodata,    
"startbefore" :  $stationutil:default_future_time,
"startafter" :  $stationutil:default_past_time,
"endbefore" : $stationutil:default_future_time,
"endafter" : $stationutil:default_past_time,
"level" : "network",
"minradius" : "0",
"maxradius" : "180",
"includerestricted" : "TRUE",
"format" : "xml"
}


let $sequenceoflines :=stationutil:lines($stationutil:postdata)

let $params :=
    map:merge( 

    for $line in $sequenceoflines
        return
         if (matches($line,"="))
            then (
                let $key_val := tokenize($line,"=")
(:                let $p:= util:log("error", "Matched " || $key_val[1] || "=" || $key_val[2] ):)
                return map:entry($key_val[1], $key_val[2]) 
            )
            else ()
 ) 

(: NSLCSE net sta loc cha start end sono mappate diversamente :)
 
(: Overwrite defaults :) 
(: "nodata" , "startbefore" ,"startafter" , "endbefore" , "endafter" , "level" , "minradius", "maxradius", "includerestricted", "format":)
let $result := map:merge(($params_default, $params)) 


(: Manage 6 parameters with alias, preferred short version:)

let $latitude:=if (exists($result("lat"))) then $result("lat") else if (exists($result("latitude"))) then $result("latitude") else "0"  
let $lat:=$latitude

let $longitude:=if (exists($result("lon"))) then $result("lon") else if (exists($result("longitude"))) then $result("longitude") else "0"  
let $lon:=$longitude

let $minlatitude:=if (exists($result("minlat"))) then $result("minlat") else if (exists($result("minlatitude"))) then $result("minlatitude") else "-90.0"
let $minlat:=$minlatitude

let $maxlatitude:=if (exists($result("maxlat"))) then $result("maxlat") else if (exists($result("maxlatitude"))) then $result("maxlatitude") else "90.0"
let $maxlat:=$maxlatitude

let $minlongitude:=if (exists($result("minlon"))) then $result("minlon") else if (exists($result("minlongitude"))) then $result("minlongitude") else "-180.0"  
let $minlon:=$minlongitude

let $maxlongitude:=if (exists($result("maxlon"))) then $result("maxlon") else if (exists($result("maxlongitude"))) then $result("maxlongitude") else "180.0" let $maxlon:=$maxlongitude



(: put in map all alias parameters :)
let $result := map:put($result,"latitude",$latitude)
let $result := map:put($result,"lat",$lat)
let $result := map:put($result,"longitude",$longitude)
let $result := map:put($result,"lon",$lon)
let $result := map:put($result,"minlatitude",$minlatitude)
let $result := map:put($result,"minlat",$minlat)
let $result := map:put($result,"minlongitude",$minlongitude)
let $result := map:put($result,"minlon",$minlon)
let $result := map:put($result,"maxlatitude",$maxlatitude)
let $result := map:put($result,"maxlat",$maxlat)
let $result := map:put($result,"maxlongitude",$maxlongitude)
let $result := map:put($result,"maxlon",$maxlon)

 
 return $result
}
catch err:* {
    let $m := map {}
    return $m
    
}
};



(: TODO do not use count() :)
declare function stationutil:empty_parameter_check() as xs:boolean
{
try {
let $params_map:=stationutil:set_parameters_row_from_GET()
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


declare function stationutil:syntax_nscl($parameters as map()*, $nscl as xs:string) as xs:string{
try {     
(: USE some or any for check :)

let $unmatched := distinct-values(
    for $p in $parameters   
        let $value := $p($nscl)
    where 
        not(empty($value)) 
        and (
        switch ($nscl)
            case "network" return contains(stationutil:network_pattern_translate($value), "NEVERMATCH")
            case "station" return contains(stationutil:station_pattern_translate($value), "NEVERMATCH")
            case "channel" return contains(stationutil:channel_pattern_translate($value), "NEVERMATCH")
            case "location" return contains(stationutil:location_pattern_translate($value), "NEVERMATCH")
            default return false()
        )
    return $value
    )

(:let $c:=count($unmatched):)
    
return
    
string-join(
for $u in $unmatched

return 
    
"
Check " ||  $nscl || " parameter, found " || $u ||  
"
"
)    
}
catch err:* {
"
Syntax error in network parameter
"   
}
};



declare function stationutil:syntax_latitude($parameters as map()*) as xs:string{
try 
{
string-join(
for $p in $parameters   
    
let $minlatitude := xs:decimal($p("minlatitude"))
let $maxlatitude := xs:decimal($p("maxlatitude"))
let $latitude := xs:decimal($p("latitude"))

return 
    if ( $minlatitude>90.0 or $maxlatitude > 90.0 or $minlatitude<-90.0 or $maxlatitude <-90.0 or $latitude> 90.0 or $latitude < -90.0) 
    then
        "
Must be -90 < latitude < 90
"
    else ""
)
}
    catch err:* {
"
Syntax error in latitude parameter
"        
    }
};

declare function stationutil:syntax_longitude($parameters as map()*) as xs:string{
try 
{
string-join(
for $p in $parameters   
    
    
let $minlongitude := xs:decimal($p("minlongitude"))
let $maxlongitude := xs:decimal($p("maxlongitude"))
let $longitude := xs:decimal($p("longitude"))
 
return 
    if ($minlongitude>180.0 or $maxlongitude > 180.0 or $minlongitude<-180.0 or $maxlongitude <-180.0 or $longitude>180.0 or $longitude <-180.0) then 
" 
Must be -180 < longitude < 180
"
else ""     
)
}
     catch err:* {
"
Syntax error in longitude parameter
"        
    } 
};

(:  TODO remove , check only defaults ?   :)
declare function stationutil:syntax_times($parameters as map()*) as xs:string {
try 
{    
string-join(
for $p in $parameters   
    
let $startbefore := xs:dateTime(stationutil:time_adjust($p("startbefore")))
let $startafter := xs:dateTime(stationutil:time_adjust($p("startafter")))
let $endbefore := xs:dateTime(stationutil:time_adjust($p("endbefore")))   
let $endafter := xs:dateTime(stationutil:time_adjust($p("endafter")))
let $starttime := xs:dateTime(stationutil:time_adjust($p("starttime")))
let $endtime := xs:dateTime(stationutil:time_adjust($p("endtime")))   
return ""
)
}
catch err:* {
"
Check time related parameters syntax

Valid syntax: YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS, YYY-MM-DDTHH:MM:SS.ssssss
"
}

};

declare function stationutil:syntax_radius($parameters as map()*) as xs:string{
try {
string-join(
for $p in $parameters   

let $minradius := xs:decimal($p("minradius"))
let $maxradius := xs:decimal($p("maxradius"))

return 
    if (  ($maxradius - $minradius) <=0  or $maxradius<0 or $minradius<0  or $maxradius >180.0) 
    then
        "
Must be 0<minradius<maxradius<=180
"
    else
    ""
)
}
catch err:* {
"
Syntax Error in radius parameters
"
    
}
};

declare function stationutil:syntax_includerestricted($parameters as map()*) as xs:string{

string-join(
for $p in $parameters 

let $includerestricted := xs:string($p("includerestricted"))

return 
    if (not( upper-case($includerestricted)="TRUE" or upper-case($includerestricted)="FALSE"))
    then
"
The includerestricted parameter must be TRUE or FALSE, case insensitive
"
    else  ""
)

};

declare function stationutil:syntax_format($parameters as map()*) as xs:string{

string-join(
for $p in $parameters     
let $format := xs:string($p("format"))

return 
    if (not( $format ="xml" or $format="text"))
    then
"
The format parameter must be xml or text
"
    else  ""
)

};

declare function stationutil:syntax_level($parameters as map()*) as xs:string{
    
(:The first is sufficient :)
for $p in $parameters[1]     
let $level := xs:string($p("level"))
let $format := xs:string($p("format"))
return 
    if (not( $level ="network" or $level="station" or $level ="channel" or $level="response"))  
    then
"
Unsupported level " || $level 
    else  
        if ($level="response" and $format = "text")
        then  
"Unsupported combination of level and format
"
else ""


};

declare function stationutil:empty_parameter_error($parameters as map()*) as xs:string
{
try {
(:let $params_map:=stationutil:set_parameters_row_from_GET():)
(:let $dummy :=stationutil:adiust_map_params():)
string-join(
for $p in $parameters     

return string-join(
for $key in map:keys($p) 

return if ( empty($p($key)) ) 
           then 
"
Parameter " || $key || " cannot be empty
" 
            else ""
)   
)

}
catch err:* {"Error checking parameters in empty_parameter_error"}
} ;

declare function stationutil:debug_parameter_error($parameters as map()*) as xs:string
{
try {
(:let $params_map:=stationutil:set_parameters_row_from_GET():)
(:let $dummy :=stationutil:adiust_map_params():)

string-join( 
for $p in $parameters     
for $key in map:keys($p) 

return if ( empty($p($key)) ) 
           then 
"
Parameter " || $key || " cannot be empty
" 
            else $key || " : " || $p($key) || "
            
"
   
)


}
catch err:* {"Error checking parameters in debug_parameter_error"}
} ;


declare function stationutil:debug_parameter_error() as xs:string
{
(:try {:)
(:let $params_map:=stationutil:set_parameters_row_from_GET():)
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


(:Return only first error found?:)
declare function stationutil:badrequest_error($p as map()*) {
(: declare output method locally to override default xml   :)
    util:declare-option("exist:serialize","method=text media-type=text/plain indent=yes")  ,  
     response:set-status-code(400) , 
     "Error 400: Bad request 
     
Syntax Error in Request

" 
||

stationutil:syntax_nscl($p,"network") ||
stationutil:syntax_nscl($p,"station") ||
stationutil:syntax_nscl($p,"channel") ||
stationutil:syntax_nscl($p,"location") ||
stationutil:syntax_latitude($p) ||
stationutil:syntax_longitude($p) ||
stationutil:syntax_times($p) ||
stationutil:syntax_radius($p) ||
stationutil:syntax_includerestricted($p) ||
(:stationutil:empty_parameter_error($p) ||:)
stationutil:syntax_format($p) ||
stationutil:syntax_level($p) 
(:):)
(:stationutil:debug_parameter_error($parameters) :)
||
"

Usage details are available from <SERVICE DOCUMENTATION URI>

Request:

" 

|| request:get-query-string() || 

stationutil:getpostdata()

||
"

Request Submitted: " || current-dateTime() ||  
"

Service version: 1.1.50"

(: response:set-status-code(404) , transform:transform(<Error>Error 404 - no matching inventory found</Error>, doc("error-translation.xsl"), ()) :)


};

declare function stationutil:get-parameter($k as xs:string) as xs:string
{
      if ( empty($stationutil:parameters($k))  ) then  "" || $k  else  $stationutil:parameters($k) 
};

declare function stationutil:get-parameter($m as map(), $k as xs:string) as xs:string
{
(:      let $p:= util:log("error", "looking for " || $k || " = " || $m($k) ) :)
(:      return:)
      if ( empty($m($k))  ) then  "EMPTY" else  $m($k) 
};


declare function stationutil:get-parameter-names() as xs:string*
{
      map:keys($stationutil:parameters) 
};

declare function stationutil:get-parameter-names($m as map()) as xs:string*
{
      map:keys($m) 
};



declare function stationutil:lines
  ( $arg as xs:string? )  as xs:string* {

(:   tokenize($arg, '(\r\n?|\n\r?)'):)
   tokenize($arg, '[\n\r]+', "m")
   
 } ;



(:Possible FIX treat level response in switch returning badrequest_error :)

declare function stationutil:run() {

if (stationutil:check_parameters_limits($stationutil:parameters_table))
then 
if (stationutil:get-parameter($stationutil:parameters_table[1], "format") = "xml") 
    then 
    let $dummy := util:declare-option("exist:serialize","method=xml media-type=text/xml indent=no")
    return
        stationutil:xml-producer()
    else
    (
    let $dummy := util:declare-option("exist:serialize","method=text media-type=text/plain indent=yes")
    return
    switch (stationutil:get-parameter($stationutil:parameters_table[1], "level"))
    case "network" return transform:transform(stationutil:xml-producer(), doc("network.xsl"), ()) 
    case "station" return transform:transform(stationutil:xml-producer(), doc("station.xsl"), ())
    case "channel" return transform:transform(stationutil:xml-producer(), doc("channel.xsl"), ())
    default return ()
    )
else 
    stationutil:badrequest_error($stationutil:parameters_table)    

};

(: TODO apply to POST if possible :)
declare function stationutil:use_shortcut() as xs:boolean {
  not( matches(string-join(request:get-parameter-names()) ,"channel|cha|location|loc|minlatitude|minlat|maxlatitude|maxlat|minlongitude|minlon|maxlongitude|maxlon|starttime|start|endtime|end|startbefore|endbefore|startafter|endafter|latitude|lat|longitude|lon|maxradius|minradius|includerestricted" ))  
};
 
declare function stationutil:use_station_shortcut() as xs:boolean {
  not( matches(string-join(request:get-parameter-names()) ,"network|net|channel|cha|location|loc|minlatitude|minlat|maxlatitude|maxlat|minlongitude|minlon|maxlongitude|maxlon|starttime|start|endtime|end|startbefore|endbefore|startafter|endafter|latitude|lat|longitude|lon|maxradius|minradius|includerestricted" ))  
};


(: TODO  :)
(: POST  locationCode -- :)
(: TODO :)

 
declare function stationutil:xml-producer() {
let $dummy := util:declare-option("exist:serialize","method=xml media-type=text/xml indent=no")
let $content :=
    switch (stationutil:get-parameter($stationutil:parameters_table[1], "level"))
    case "network" return stationutil:query_core($stationutil:parameters_table,"network")
    case "station" return stationutil:query_core($stationutil:parameters_table,"station")
    case "channel" return 
        if (stationutil:use_shortcut()) then 
            stationutil:query_core_channel_response_shortcut($stationutil:parameters_table)
        else 
            stationutil:query_core($stationutil:parameters_table,"channel")
    case "response" return 
        if (stationutil:use_shortcut()) then 
            stationutil:query_core_channel_response_shortcut($stationutil:parameters_table)
        else
            stationutil:query_core($stationutil:parameters_table,"response")
    default return stationutil:query_core($stationutil:parameters_table,"network")

return
if (not(empty($content))) then
<FDSNStationXML xmlns="http://www.fdsn.org/xml/station/1" xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" schemaVersion="1.0" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.0.xsd">
<Source>eXistDB</Source>
<Sender>INGV-ONT</Sender>
<Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.0</Module>
<ModuleURI>"{request:get-uri()}?{request:get-query-string()}"</ModuleURI>
<Created>{current-dateTime()}</Created>
{$content}
</FDSNStationXML>
else
    stationutil:nodata_error()
};



(: NEW single query for all levels:)
declare function stationutil:query_core($NSLCSE as map()*, $level as xs:string){

for $network in collection("/db/apps/fdsn-station/Station/")//Network , $condition in $NSLCSE  

    let $minlatitude := xs:decimal($condition("minlatitude"))
    let $maxlatitude := xs:decimal($condition("maxlatitude"))
    let $minlongitude := xs:decimal($condition("minlongitude"))
    let $maxlongitude := xs:decimal($condition("maxlongitude"))

    let $Latitude:= $network/Station/Latitude
    let $Longitude:= $network/Station/Longitude
    let $CreationDate:= $network/Station/Channel/@startDate
    let $TerminationDate:= $network/Station/Channel/@endDate

    let $networkcode := $network/@code
    let $station:=$network//Station
    let $stationcode:=$station/@code
    let $lat := $station/Latitude
    let $lon := $station/Longitude    
    let $channel:=$station/Channel
    let $channelcode:=$channel/@code
    let $locationcode:=$channel/@locationCode
    let $startDate := $network/@startDate
    let $endDate := $network/@endDate
    let $restrictedStatus:=$network/@restrictedStatus
    let $stationrestrictedStatus:=$network/Station/@restrictedStatus    
    let $channelrestrictedStatus:=$network//Channel/@restrictedStatus    
    let $Description := $network/Description
    let $ingv_identifier := $network/ingv:Identifier

    where
        $Latitude  > $minlatitude and  
        $Latitude  < $maxlatitude and 
        $Longitude > $minlongitude and 
        $Longitude < $maxlongitude and
        stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and
        stationutil:check_radius($condition, $lat,$lon) and 
        matches($stationcode, $NSLCSE("station_pattern")) and
        matches($networkcode, $NSLCSE("network_pattern")) and
        matches($channelcode, $NSLCSE("channel_pattern")) and
        matches($locationcode, $NSLCSE("location_pattern")) and         
        stationutil:check_restricted($condition,$restrictedStatus) and          
        stationutil:check_restricted($condition,$stationrestrictedStatus) and  
        stationutil:check_restricted($condition,$channelrestrictedStatus)
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
        <SelectedNumberStations> {count($station)} </SelectedNumberStations>
        {
        if ( $level= "network") then ()
        else
        for $station in $network/Station
            let $stationcode:=$station/@code
            let $stationstartDate := $station/@startDate
            let $stationendDate := $station/@endDate
            let $stationrestrictedStatus := $station/@restrictedStatus
            let $channel:=$station//Channel
            let $channelcode:=$channel/@code
            let $locationcode := $channel/@locationCode          
            let $Latitude:=  xs:decimal($station/Latitude)
            let $Longitude:= xs:decimal($station/Longitude) 
            let $lat := $station/Latitude
            let $lon := $station/Longitude
            let $CreationDate:= $channel/@startDate
            let $TerminationDate:= $channel/@endDate 
            let $networkcode:=$network/@code

        where 
            $Latitude  > $minlatitude and  
            $Latitude  < $maxlatitude and 
            $Longitude > $minlongitude and 
            $Longitude < $maxlongitude and
            stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and  
            stationutil:check_radius($condition, $lat,$lon) and
            matches($stationcode, $NSLCSE("station_pattern")) and
            matches($networkcode, $NSLCSE("network_pattern")) and
            matches($channelcode, $NSLCSE("channel_pattern")) and
            matches($locationcode, $NSLCSE("location_pattern")) and            
            stationutil:check_restricted($condition,$stationrestrictedStatus) 

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
            {
            if ($level="station" or $level="network") then () 
            else  
            <TotalNumberChannels>{count($station/Channel)}</TotalNumberChannels>,
            if ($level="station" or $level="network") then () 
            else  
                
                let $selected_channels:= (
                for $channel in $station/Channel
                let $channelcode:=$channel/@code
                let $locationcode:=$channel/@locationCode
                let $channelrestrictedStatus := $channel/@restrictedStatus                                           
                let $CreationDate:= $channel/@startDate
                let $TerminationDate:= $channel/@endDate  
                where 
                    stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and            
                    stationutil:check_radius($condition, $lat,$lon) and
                    matches($stationcode, $NSLCSE("station_pattern")) and
                    matches($networkcode, $NSLCSE("network_pattern")) and
                    matches($channelcode, $NSLCSE("channel_pattern")) and
                    matches($locationcode, $NSLCSE("location_pattern")) and
                    stationutil:check_restricted($condition,$channelrestrictedStatus)
                return 
                    
                    if ($level="channel") then stationutil:remove-elements($channel,"Stage") else $channel 
                 
                )
                let $channelcount:=count ($selected_channels)
            return  (<SelectedNumberChannels>{$channelcount}</SelectedNumberChannels>, $selected_channels)
            }
            </Station>
}
</Network>

    
}; 
 

(: A function to call when no conditions are posed but station= :)
declare function stationutil:query_core_channel_response_shortcut($NSLCSE as map()*) { 

for $network in collection("/db/apps/fdsn-station/Station/")//Network , $condition in $NSLCSE  

    let $level:=$condition("level")
    let $networkcode := $network/@code
    let $startDate := $network/@startDate
    let $endDate := $network/@endDate
    let $restrictedStatus:=$network/@restrictedStatus
    let $Description := $network/Description
    let $ingv_identifier := $network/ingv:Identifier
    let $network_pattern:=$condition("network_pattern")
    let $station_pattern:=$condition("station_pattern")
    let $stationcode:=$network//Station/@code
    where
        matches($networkcode,  $network_pattern)
        and matches($stationcode,  $station_pattern)
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
        if  ($level = "channel") 
        then 
            for $station in $network/Station
                order by $station/@code
            return stationutil:remove-elements($station,"Stage")
        else
            for $station in $network/Station
                order by $station/@code 
            return  $station
}
</Network>       
 
}; 
 

