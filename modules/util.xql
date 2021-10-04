xquery version "3.1";

module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil";
import module namespace request = "http://exist-db.org/xquery/request";
import module namespace util = "http://exist-db.org/xquery/util";

declare default element namespace "http://www.fdsn.org/xml/station/1" ;
declare namespace ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";
import module  namespace functx = "http://www.functx.com";


(: Serialization cannot change during the same request, must be changed into the function :)
(:declare option exist:serialize "method=html5 media-type=text/html";:)
(:declare option output:method "html5";:)
(:declare option output:media-type "text/html";:)
(:declare option exist:serialize "method=xhtml media-type=application/xhtml+html indent=no";:)
(:BEWARE the order matters !!! :)
(:TODO update date limits with javascript limits:)
(:USATA PER POSTER:)




(:~ Default values, from fdsn standard or for convenience :)
declare %public variable $stationutil:defaults as map()* := map {
    "nodata"            : "204",
    "level"             : "station",
    "latitude"          : "0",
    "longitude"         : "0",
    "minradius"         : "0",
    "maxradius"         : "180",
    "minradiuskm"       : "0",
    "maxradiuskm"       : "20037.5",
    "includerestricted" : "TRUE",
    "format"            : "xml",
    "minlatitude"       : "-90",
    "maxlatitude"       : "90",
    "minlongitude"      : "-180",
    "maxlongitude"      : "180",
    "startbefore"       : "10001-01-01T00:00:00",
    "startafter"        : "0001-01-01T00:00:00",
    "endbefore"         : "10001-01-01T00:00:00",
    "endafter"          : "0001-01-01T00:00:00",
    "starttime"         : "0001-01-01T00:00:00",
    "endtime"           : "10001-01-01T00:00:00",
    "updatedafter"      : "0001-01-01T00:00:00",
    "past_time"         : "0001-01-01T00:00:00",
    "future_time"       : "10001-01-01T00:00:00",
    "past_time_as_datetime"   :  xs:dateTime("0001-01-01T00:00:00"),
    "future_time_as_datetime" :  xs:dateTime("10001-01-01T00:00:00")
};


declare %public variable $stationutil:postdata as xs:string* := if (request:get-method() eq "POST") then stationutil:setpostdata() else "";

declare %public variable $stationutil:parameters as map() := if (request:get-method() eq "POST")  then stationutil:set_parameters_row_from_POST()  else stationutil:set_parameters_row_from_GET(); 

declare %public variable $stationutil:parameters_table as map()* := if (request:get-method() eq "POST")  then stationutil:set_parameters_table()  else stationutil:set_parameters_row_from_GET(); 

declare %public variable $stationutil:unknown_parameters as xs:string* := if (request:get-method() eq "POST")  then stationutil:unknown_parameter_from_POST()  else stationutil:unknown_parameter_from_GET(); 

(: Functions declarations  :)

(:~ @return the current module version:)
declare function stationutil:version() as xs:string
{
    "1.1.50.2"
};

(:~ Count the total number of stations of the network with code netcode :)
declare function stationutil:stationcount($netcode as xs:string) as item()
{
(:    count( collection("/db/apps/fdsn-station/Station/")//Network[@code=$netcode]/Station):)
    count(distinct-values( collection("/db/apps/fdsn-station/Station/")//Network[@code=$netcode]/Station/@code) )
};


declare function stationutil:sanitize ($input as xs:string) as xs:string
{
  let $output:=translate( $input, "|", "-")    
  return $output  
};

(:~ 
 : Translate the network parameter in xql pattern for matches function
 :  
 : @param $input the network code parameter
 : 
 :)
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
        else if (string-length($token)=1 and $token="*" ) then
(:                let $pattern:= translate( $token, "*", ".*"):)
                  let $pattern:= ".*"                
                
(:      ATTENZIONE      return $pattern:)
            return "^"||$pattern||"$"
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


(:~ Translate the station parameter in xql pattern for matches function
 :  
 : @param $input the station code parameter
 : 
 :)
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

(:~ Translate the channel parameter in xql pattern for matches function
 :  
 : @param $input the channel code parameter
 : 
 :)
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

(:~ Translate the location parameter in xql pattern for matches function
 :  
 : @param $input the location code parameter
 : 
 :)
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



(:~
 :  Adjust datetime strings to fdsn standard format YYYY-MM-DDThh:mm:ss.d if possible
 :)
declare function stationutil:time_adjust( $mydatetime as xs:string ) as xs:string {
    
    if (not(matches($mydatetime,".*T.*"))) then $mydatetime||"T"||"00:00:00.0"
    else $mydatetime
    
};



declare function stationutil:constraints_onchannel(
    $parameters as map()*,
    $CreationDate as xs:dateTime*, 
    $TerminationDate as xs:dateTime* ) as xs:boolean 
    {
    try {  
(:DEBUG:)
(:    let $p:=( :)
(:        for $p in $parameters, $c in $CreationDate:)
(:        let $dummy := util:log("info", "starttime" || $p("starttime") || "CreationDate" || $c ):)
(:        let $dummy2 := if ( $p("starttime") < $c ) then util:log("info", "starttime" || $p("starttime") || " < CreationDate" || $c ) else util:log("info", "starttime" || $p("starttime") || " >= CreationDate" || $c ):)
(:        let $dummy2 := if ( $p("endtime") < $c ) then util:log("info", "endtime" || $p("endtime") || " < TerminationDate" || $c ) else util:log("info", "endtime" || $p("endtime") || " >= TerminationDate" || $c ):)
(:        return $p:)
(:        ):)
(:    let $q:=( :)
(:        for $p in $parameters, $c in $TerminationDate:)
(:        let $dummy := util:log("info", "starttime" || $p("starttime") || "TerminationDate" || $c ):)
(:        let $dummy2 := if (empty($c)) then util:log("info", "TerminationDate empty") else util:log("info", "TerminationDate " || $c ):)
(:        let $dummy3 := if ( $p("starttime") <= $c ) then util:log("info", "starttime" || $p("starttime") || " <= TerminationDate" || $c ) else util:log("info", "starttime" || $p("starttime") || " > TerminationDate" || $c ):)
(:        return $p:)
(:        ):)
(:    return:)
(:DEBUG:)
    let $ctd:=count($CreationDate)
    let $ttd:=count($TerminationDate)
    let $add:=$ctd - $ttd
(:    let $add:=3:)
    let $TerminationDate := (
        for $t in $TerminationDate 
        return $t , 
        for $n in 1 to $add return $stationutil:defaults("future_time_as_datetime")
        )
    return
        
    some $NSLCSE in $parameters
    satisfies    
        (
(:  
 : satisfies is true if at least a $NSLCSE matches 
 :)
 
         (: 
         : If TD (= empty) doesn't match only when endtime < CD 
         : If TD exists matches when endtime greater than CD AND starttime less than TD  (total or partial overlap)
         :)
 
        (
 
            ( ($NSLCSE("endtime") >= $CreationDate)  and  ($NSLCSE("starttime") <= $TerminationDate))
            
        ) and
(:  TODO check if remove default is possible: the two block pass  the same tests:)
        (($CreationDate < $NSLCSE("startbefore"))) and
        (($CreationDate > $NSLCSE("startafter"))) and
        (($NSLCSE("endbefore")=$stationutil:defaults("future_time_as_datetime")) or ($TerminationDate < $NSLCSE("endbefore")) ) and
        (($NSLCSE("endafter")=$stationutil:defaults("past_time_as_datetime"))  or ($TerminationDate > $NSLCSE("endafter")))  

        )        
    }
    catch err:FORG0001 {false()}
};



declare function stationutil:constraints_onchannel_TEST(
    $parameters as map()*,
    $CreationDate as xs:dateTime*, 
    $TerminationDate as xs:dateTime* ) as xs:boolean*
    {
(:    try {  :)
    let $d:=util:log("info", "constraints_onchannel " )
    let $ctd:=count($CreationDate)
    let $ttd:=count($TerminationDate)
    let $add:=$ctd - $ttd
(:    let $add:=3:)
    let $tdd := (
        for $t in $TerminationDate 
        return $t , 
        for $n in 1 to $add return $stationutil:defaults("future_time_as_datetime")
        )
    
    let $d:=util:log("info", "t Num: " || count($tdd) )   
    
    let $d:=for $t allowing empty in $tdd return util:log("info", "t:  " || $t )     
        
    let $cdd:=(
        for $c allowing empty in $CreationDate 
        order by $c  
        return if (empty($c)) then xs:dateTime("2099-12-31T00:00:00") else $c
        )   
    let $d:=util:log("info", "c Num: " || count($cdd) )      
    let $d:=for $c allowing empty in $cdd return util:log("info", "c:  " || $c ) 
    
    
    let $creation := for $c allowing empty in $cdd return <cd c="{$c}"/>
    
(:    let $d:=for $c in $creation:)
(:        return util:log("info", "in tr: CD " || $c):)
        
    let $termination := for $t allowing empty in $tdd return <td t="{$t}"/>
    
(:Create a temporary xml to facilitate results and efficiency   :)


(:    let $stream:= for-each-pair($creation, $termination, function($c, $t) { <row>{ "ct=", $c, " td=" ,$t}</row>}):)
    let $streams:= for-each-pair($creation, $termination, function($c, $t) {<row>{$c} {$t}</row>})
    
(:    let $d:=:)
(:        for $s in $streams//@c:)
(:        return util:log("info", "in streams//@c: " || $s ):)
(:    let $d:=:)
(:        for $s in $streams//@t:)
(:        return util:log("info", "in streams//@t: " || $s ):)
    let $d:=
        for $s allowing empty in $streams
        let $c:=$s//@c
        let $t:=$s//@t        
        return util:log("info", "in streams " || $c || " " || $t )     
    
    let $v:=exists(     
    for $p allowing empty in $parameters , $s allowing empty in $streams
    let $start:=$p("starttime")
    let $end:=$p("endtime")
    let $startbefore:=$p("startbefore")
    let $startafter:=$p("startafter")
    let $endafter:=$p("endafter")
    let $endbefore:=$p("endbefore")
    let $cd := $s//@c
    let $td := $s//@t
    let $dummy:= if ($td>=$start ) then util:log("info", "Examining: " || $cd || " " || $start || "  " || $td ) else util:log("info", "Examining: " || $cd || " " || $td || " " || $start )
    
    where
(:    some $td in $tdd, $cd in $cdd:)
(:    satisfies :)
(:    let $dummy2 := if (empty($t)) then util:log("info", "TerminationDate empty" || " CreationDate " || $c) else util:log("info", "TerminationDate " || $t ):)
(:    let $t2 := if (empty($t)) then $stationutil:defaults("future_time_as_datetime") else  $t :)
(:    let $t2 := if (empty($t)) then $p("future_time_as_datetime") else  $t :)

(:    let $d:=if ($t>=$start) then util:log("info", "in loop: TerminationDate " || $t  || " >= " || $start ) else util:log("info", "in loop: TerminationDate " || $t || " < " || $start ) :)
(:    let $d:= for $cc in $c, $tt in $t:)
(:        let $xx:=util:log("info", "st: " || $start  || " et: " || $end || " cd: " || $cc || " td: " || $tt ):)
(:        return :)
(:            1=1:)

(:  :)
(:    where :)
    
    
(:    some $p in $parameters :)
(:return :)
(:    some $p in $parameters, $t in $td, $c in $cd:)
(:    satisfies :)
(:  (  :)

 (

(: TODO check conditions:)
        
(: This does not work :)   
 
(:        (($start<$td) and ($start>$cd) and ($cd<$td)):)
(:        or:)
        (($start<=$td) and ($end>=$cd)  and ($cd<$td))
        

(:        and:)
(:        (xs:dateTime("2014-05-08T11:41:00") > $td):)
    
 )  
 
        and
        ( 
        ($cd < $startbefore)
        and
        ($cd > $startafter)
        and
        ($td < $endbefore)
        and
        ($td > $endafter)

        )
    return $cd
    )

    return $v
(:    }:)
(:    catch err:FORG0001 {false()}:)

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
(:    try {    :)
    some $NSLCSE in $parameters , $n in $networkcode, $s in $stationcode, $c in $channelcode, $l in $locationcode
    satisfies    
            
            matches($s, $NSLCSE("station_pattern"))
     and    matches($n, $NSLCSE("network_pattern")) 
     and    matches($c, $NSLCSE("channel_pattern")) 
     and    matches($l, $NSLCSE("location_pattern")) 
    
(:    let $m := :)
(:    exists(   :)
(:        :)
(:    for $NSLCSE in $parameters, $n in $networkcode, $s in $stationcode, $c in $channelcode, $l in $locationcode:)
(:    where:)
(:            matches($s, $NSLCSE("station_pattern")):)
(:     and    matches($n, $NSLCSE("network_pattern")) :)
(:     and    matches($c, $NSLCSE("channel_pattern")) :)
(:     and    matches($l, $NSLCSE("location_pattern")) :)
(:     return $NSLCSE:)
(:    )    :)
(:    :)
(:    return $m:)
        
(:    }:)
(:    catch err:* {false()}:)
};


(:~ Validate request parameters:)
declare function stationutil:validate_request( $parameters as map()*) as xs:boolean 
{

try {

not( 
some $NSLCSE in $parameters 
satisfies
 ( 
(:          not(stationutil:empty_parameter_check()) :)
 
           ($NSLCSE("level")="response" and $NSLCSE("format") ="text")
           or xs:decimal($NSLCSE("minlatitude")) > 90.0 
           or xs:decimal($NSLCSE("maxlatitude")) > 90.0 
           or xs:decimal($NSLCSE("minlatitude")) <-90.0 
           or xs:decimal($NSLCSE("maxlatitude")) <-90.0
           or xs:decimal($NSLCSE("minlatitude")) > xs:decimal($NSLCSE("maxlatitude")) 
           or xs:decimal($NSLCSE("minlongitude")) > 180.0 
           or xs:decimal($NSLCSE("maxlongitude")) > 180.0 
           or xs:decimal($NSLCSE("minlongitude")) <-180.0 
           or xs:decimal($NSLCSE("maxlongitude")) <-180.0
           or xs:decimal($NSLCSE("minlongitude")) > xs:decimal($NSLCSE("maxlongitude")) 
           or xs:decimal($NSLCSE("latitude"))  >  90.0 or xs:decimal($NSLCSE("latitude"))  <  -90.0 
           or xs:decimal($NSLCSE("longitude")) > 180.0 or xs:decimal($NSLCSE("longitude")) < -180.0
           or xs:decimal($NSLCSE("minradius")) <0 or xs:decimal($NSLCSE("minradius")) >= xs:decimal($NSLCSE("maxradius"))
           or xs:decimal($NSLCSE("maxradius")) <0 or xs:decimal($NSLCSE("maxradius")) > 180.0 
           or $NSLCSE("startbefore") < $NSLCSE("startafter")
           or $NSLCSE("endbefore") < $NSLCSE("endafter")
           or $NSLCSE("starttime") > $NSLCSE("endtime")
           or not(matches($NSLCSE("level"),"network|station|channel|response"))
           or not(xs:string($NSLCSE("includerestricted"))="TRUE" or xs:string($NSLCSE("includerestricted"))="FALSE")
           or not( $NSLCSE("format") ="xml" or $NSLCSE("format")="text" or $NSLCSE("format")="json" )           
           or (contains(stationutil:network_pattern_translate($NSLCSE("network")), "NEVERMATCH")) 
           or (contains(stationutil:station_pattern_translate($NSLCSE("station")), "NEVERMATCH")) 
           or (contains(stationutil:channel_pattern_translate($NSLCSE("channel")), "NEVERMATCH")) 
           or (contains(stationutil:location_pattern_translate($NSLCSE("location")), "NEVERMATCH"))
           ) 
)           

}
catch err:* {false()}

} ;

(:~ Validate request parameters:)
declare function stationutil:classify_request( $parameters as map()*) as xs:boolean 
{
(: Classify request to select optimized queries :)
(: Alphabetic-only, geographic-only, Time constrained only , mixed combo of the three:)
(:  AO - GO - TO - AG - AT - GT - AGT :)
(: AO simple path expression, only need translation from syntax of the service and xquery :)
(: GO path expression only for bounding box  not for radius(km)? :)
(: TO path expression on StartTime EndTime StartBefore EndBefore :)
(: AG maybe can be combined path expr. :)
(: AT maybe can be combined path expr. :)
(: GT maybe can be combined path expr. :)
(: AGT need to choose best index to exploit :)

try {
    true()
}
catch err:* {false()}

};


(:~ Remove recursively elements with given $remove-names and its children
 : 
 : @param $input element tree
 : @param $remove-names name of elements to remove
 : :)
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



(:~ 
 : @param $Latitude1 Latitude of Point 1
 : @param $Longitude1 Longitude of Point 1 
 : @param $Latitude2 Latitude of Point 2
 : @param $Longitude2 Longitude of Point 2
 : @return the distance in degrees between Point 1 with coordinates ($Latitude1,$Longitude1) 
 : and Point 2 with coordinates ($Latitude2,$Longitude2)  
 : :)
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
    (
        $NSLCSE("latitude")  = $stationutil:defaults("latitude")  and 
        $NSLCSE("longitude") = $stationutil:defaults("longitude") and 
        $NSLCSE("maxradius") = $stationutil:defaults("maxradius") and 
        $NSLCSE("minradius") = $stationutil:defaults("minradius") 
    ) 
    or 
    (
        stationutil:distance($Latitude1, $Longitude1, $NSLCSE("latitude"), $NSLCSE("longitude")) < xs:decimal($NSLCSE("maxradius")) and
        stationutil:distance($Latitude1, $Longitude1, $NSLCSE("latitude"), $NSLCSE("longitude")) > xs:decimal($NSLCSE("minradius"))      
    ) 
};


(: TODO manage correctly open, partial, closed in station.xml match a channel station network if includerestricted=true or is open:)
declare function stationutil:check_restricted($parameter as map()*, $restrictedStatus as xs:string * ) as xs:boolean {
    some $rs in $restrictedStatus, $NSLCSE in $parameter
    satisfies 
    ($rs="open" or $rs="partial") or $NSLCSE("includerestricted")="TRUE"
};



(:~ Map the request params in stationutil:parameters  :)
declare function stationutil:set_parameters_row_from_GET() as map()* {

let $nodata := request:get-parameter("nodata", $stationutil:defaults("nodata"))
let $startbefore := xs:dateTime(stationutil:time_adjust(request:get-parameter("startbefore", $stationutil:defaults("startbefore"))))
let $startafter  := xs:dateTime(stationutil:time_adjust(request:get-parameter("startafter", $stationutil:defaults("startafter"))))
let $endbefore   := xs:dateTime(stationutil:time_adjust(request:get-parameter("endbefore", $stationutil:defaults("endbefore"))))   
let $endafter    := xs:dateTime(stationutil:time_adjust(request:get-parameter("endafter", $stationutil:defaults("endafter"))))
let $updatedafter    := xs:dateTime(stationutil:time_adjust(request:get-parameter("updatedafter", $stationutil:defaults("updatedafter"))))

let $level := request:get-parameter("level", $stationutil:defaults("level"))
(:let $minradius := request:get-parameter("minradius", $stationutil:defaults("minradius")):)
(:let $maxradius := request:get-parameter("maxradius", $stationutil:defaults("maxradius")):)

(: No readings if no parameters:)
let $minradius := request:get-parameter("minradius", ())
let $maxradius := request:get-parameter("maxradius", ())

(: No readings if no parameters:)
let $minradiuskm := request:get-parameter("minradiuskm", ())
let $maxradiuskm := request:get-parameter("maxradiuskm", ())

let $includerestricted := upper-case(xs:string(request:get-parameter("includerestricted",$stationutil:defaults("includerestricted"))))
let $format := request:get-parameter("format",$stationutil:defaults("format"))

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
let $latitude:=if (exists($lat)) then $lat else if (exists($latitude1)) then $latitude1 else $stationutil:defaults("latitude")  
let $lat:=$latitude
let $longitude:=if (exists($lon)) then $lon else if (exists($longitude1)) then $longitude1 else$stationutil:defaults("longitude")  
let $lon:=$longitude
(:Se abbiamo minradiuskm allora calcolare minradius con la proporzione e sostituire il valore in minradius con quello calcolato:)
let $minradius := if (exists($minradius)) then $minradius else if (exists($minradiuskm)) then xs:decimal($minradiuskm) * 180.0 div xs:decimal($stationutil:defaults("maxradiuskm")) else $stationutil:defaults("minradius")
let $maxradius := if (exists($maxradius)) then $maxradius else if (exists($maxradiuskm)) then xs:decimal($maxradiuskm) * 180.0 div xs:decimal($stationutil:defaults("maxradiuskm")) else $stationutil:defaults("maxradius")
let $minlatitude:=if (exists($minlat)) then $minlat else if (exists($minlatitude1)) then $minlatitude1 else $stationutil:defaults("minlatitude")
let $minlat:=$minlatitude
let $maxlatitude:=if (exists($maxlat)) then $maxlat else if (exists($maxlatitude1)) then $maxlatitude1 else $stationutil:defaults("maxlatitude")
let $maxlat:=$maxlatitude
let $minlongitude:=if (exists($minlon)) then $minlon else if (exists($minlongitude1)) then $minlongitude1 else $stationutil:defaults("minlongitude")
let $minlon:=$minlongitude
let $maxlongitude:=if (exists($maxlon)) then $maxlon else if (exists($maxlongitude1)) then $maxlongitude1 else $stationutil:defaults("maxlongitude")  
let $maxlon:=$maxlongitude
let $starttime:=if (exists($start)) then xs:dateTime(stationutil:time_adjust($start)) else if (exists($starttime1)) then xs:dateTime(stationutil:time_adjust($starttime1)) else xs:dateTime($stationutil:defaults("starttime"))  
let $start:=$starttime
let $endtime:=if (exists($end)) then xs:dateTime(stationutil:time_adjust($end)) else if (exists($endtime1)) then xs:dateTime(stationutil:time_adjust($endtime1)) else xs:dateTime($stationutil:defaults("endtime"))
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
"updatedafter" : $updatedafter,
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

(:DEBUG:)
(:let $p:= util:log("info", "GET nscl: " || $result("network_pattern") || " " || $result("station_pattern") || " "  || $result("channel_pattern") || " " || $result("location_pattern") || " " || $result("starttime") || " " || $result("endtime") || " " ) :)
(:DEBUG:)
return $result
};

(: 
 : @FIXME request:get-data() cannot be called twice 
 : 
 :)
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
(:let $p:= util:log("info", "POST: " || $stationutil:postdata):)

(: A sequence of maps :)
let $NSLCSE :=
    for $line in $sequenceoflines
        return
         if (matches($line,"=") or $line="" )
            then ()
            else (
                let $key_val := tokenize($line,"\s+")

(: apply pattern translate and add related entries :)
                return map:merge((
                    map:entry("net", $key_val[1]), map:entry("network", $key_val[1]), map:entry("network_pattern",stationutil:network_pattern_translate($key_val[1])),
                    map:entry("sta", $key_val[2]), map:entry("station", $key_val[2]), map:entry("station_pattern",stationutil:station_pattern_translate($key_val[2])),
                    map:entry("loc", $key_val[3]), map:entry("location", $key_val[3]), map:entry("location_pattern",stationutil:location_pattern_translate($key_val[3])),
                    map:entry("cha", $key_val[4]) , map:entry("channel", $key_val[4]), map:entry("channel_pattern",stationutil:channel_pattern_translate($key_val[4])),
                    map:entry("start", xs:dateTime(stationutil:time_adjust($key_val[5]))), map:entry("starttime", xs:dateTime(stationutil:time_adjust($key_val[5]))), 
                    map:entry("end", xs:dateTime(stationutil:time_adjust($key_val[6]))), map:entry( "endtime", xs:dateTime(stationutil:time_adjust($key_val[6]))), 
                    $stationutil:parameters) ) 
            )
(:NET STA LOC CHA STARTTIME ENDTIME più tutti gli altri parametri ripetuti:)
(:DEBUG:)
(:for $i in $NSLCSE:)
(:let $p:= util:log("info", "POST: " || $i("network_pattern") || " " || $i("station_pattern") || " "  || $i("channel_pattern") || " " || $i("location_pattern") || " "|| $i("starttime") || " " || $i("endtime") || " ") :)
 
return $NSLCSE
    
};

(:~ Map parameters from POST request:)
declare function stationutil:set_parameters_row_from_POST() as map(*) {
try
{
(: SET defaults for 10 non alias parameters :)

let $params_default := map {
"nodata"            : $stationutil:defaults("nodata"),    
"startbefore"       : xs:dateTime($stationutil:defaults("startbefore")),
"startafter"        : xs:dateTime( $stationutil:defaults("startafter")),
"endbefore"         : xs:dateTime($stationutil:defaults("endbefore")),
"endafter"          : xs:dateTime($stationutil:defaults("endafter")),
"updatedafter"      : xs:dateTime($stationutil:defaults("updatedafter")),
"level"             : $stationutil:defaults("level"),
"includerestricted" : $stationutil:defaults("includerestricted"),
"format"            : $stationutil:defaults("format")
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
(: "nodata" , "startbefore" ,"startafter" , "endbefore" , "endafter" , "level" , "minradius", "maxradius", "includerestricted", "format", "updatedafter :)
let $result := map:merge(($params_default, $params)) 


(: Manage 6 parameters with alias, preferred short version:)

let $latitude:=if (exists($result("lat"))) then $result("lat") else if (exists($result("latitude"))) then $result("latitude") else $stationutil:defaults("latitude")  
let $lat:=$latitude

let $longitude:=if (exists($result("lon"))) then $result("lon") else if (exists($result("longitude"))) then $result("longitude") else $stationutil:defaults("longitude")  
let $lon:=$longitude

let $minlatitude:=if (exists($result("minlat"))) then $result("minlat") else if (exists($result("minlatitude"))) then $result("minlatitude") else $stationutil:defaults("minlatitude")
let $minlat:=$minlatitude

let $maxlatitude:=if (exists($result("maxlat"))) then $result("maxlat") else if (exists($result("maxlatitude"))) then $result("maxlatitude") else $stationutil:defaults("maxlatitude")
let $maxlat:=$maxlatitude

let $minlongitude:=if (exists($result("minlon"))) then $result("minlon") else if (exists($result("minlongitude"))) then $result("minlongitude") else $stationutil:defaults("minlongitude")  
let $minlon:=$minlongitude

let $maxlongitude:=if (exists($result("maxlon"))) then $result("maxlon") else if (exists($result("maxlongitude"))) then $result("maxlongitude") else $stationutil:defaults("maxlongitude") 
let $maxlon:=$maxlongitude

(:Se abbiamo minradiuskm allora calcolare minradius con la proporzione e sostituire il valore in minradius con quello calcolato:)
let $minradius := if (exists($result("minradius"))) then $result("minradius") else if (exists($result("minradiuskm"))) then xs:decimal($result("minradiuskm")) * 180.0 div xs:decimal($stationutil:defaults("maxradiuskm")) else $stationutil:defaults("minradius")

let $maxradius := if (exists($result("maxradius"))) then $result("maxradius") else if (exists($result("maxradiuskm"))) then xs:decimal($result("maxradiuskm")) * 180.0 div xs:decimal($stationutil:defaults("maxradiuskm")) else $stationutil:defaults("maxradius")


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
let $result := map:put($result,"minradius",$minradius)
let $result := map:put($result,"maxradius",$maxradius)

 
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
};


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
let $updatedafter := xs:dateTime(stationutil:time_adjust($p("updatedafter")))
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
Check radius related parameters
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
    if (not( $format ="xml" or $format="text" or $format="json"))
    then
"
The format parameter must be xml, text or json
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
Unsupported level " || $level || "
"
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



declare function stationutil:unknown_parameter_error() as xs:string
{
try {

let $r:= string-join(
    for $p in $stationutil:unknown_parameters     
    return 
    "Unknown parameter " || $p || "
"
)


return $r   
}
catch err:* {"Error checking parameters in unknown_parameter_error"}
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
(:catch err:* {"Error checking parameters"} :)
};

(:TODO MANAGE ERRORS in XSLT
 :TODO complete error message in text and json:)
(:~ @return the error message text or xml accordingly with format and nodata parameters :)
declare function stationutil:nodata_error() {
    
    (: declare output method locally to override default xml   :)
    util:declare-option("exist:serialize","method=text media-type=text/plain indent=no")  , 
    
(:    if (request:get-parameter("nodata", "204") eq "404") :)
    if (stationutil:get-parameter($stationutil:parameters_table[1], "nodata") eq "404") 
    then
        (
            (:return xml error tag to be translated :)
(:            if ( (request:get-parameter("format","xml") eq "text")  or (request:get-parameter("format","xml") eq "json")   ) then ( :)
            if ( (stationutil:get-parameter($stationutil:parameters_table[1], "format") eq "text")  or 
            (stationutil:get-parameter($stationutil:parameters_table[1], "format") eq "json")   ) then (    
                response:set-status-code(404) , 
              <xml><ERROR>{"Error 404 - no matching inventory found" || stationutil:global_error_text()}</ERROR></xml>
            )
            else
                (
             response:set-status-code(404) , "Error 404 - no matching inventory found" || stationutil:global_error_text()
        )
        )
(:    else if (request:get-parameter("nodata", "204") eq "204") then:)
    else if (stationutil:get-parameter($stationutil:parameters_table[1], "nodata")  eq "204") then        
        response:set-status-code(204) 
    else 
        response:set-status-code(400) 

};


(:
 : @return The error message
 : Return only first error found? :)
declare function stationutil:badrequest_error($p as map()*) {
    (: declare output method locally to override default xml   :)
    util:declare-option("exist:serialize","method=text media-type=text/plain indent=no")  ,  
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
stationutil:empty_parameter_error($p) ||
stationutil:syntax_format($p) ||
stationutil:syntax_level($p) ||
stationutil:unknown_parameter_error()

(:||:)
(:stationutil:debug_parameter_error($parameters) :)
||
stationutil:global_error_text() 

(: response:set-status-code(404) , transform:transform(<Error>Error 404 - no matching inventory found</Error>, doc("error-translation.xsl"), ()) :)


};


declare function stationutil:global_error_text() as xs:string {

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

Service version: " || stationutil:version() 
    
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

(:~ Return the parameters names 
 : 
 : 
 :)
 
declare function stationutil:get-parameter-names() as xs:string*
{
      map:keys($stationutil:parameters) 
};


(:~ Return the parameters names 
 : 
 : @param $m query parameters map
 : @return parameters 
 :)
  
declare function stationutil:get-parameter-names($m as map()) as xs:string*
{
      map:keys($m) 
};



declare function stationutil:lines
  ( $arg as xs:string? )  as xs:string* {

   tokenize($arg, '[\n\r]+', "m")
   
 } ;


(:~
 : @TODO FIX treat level response in switch returning badrequest_error 
 : 
 :)

declare function stationutil:run() {

if (stationutil:validate_request($stationutil:parameters_table) and empty( $stationutil:unknown_parameters))
then 
if (stationutil:get-parameter($stationutil:parameters_table[1], "format") = "xml") 
    then 
    let $dummy := util:declare-option("exist:serialize","method=xml media-type=text/xml indent=no")
    return
        stationutil:xml-producer()
    else
    (
     if (stationutil:get-parameter($stationutil:parameters_table[1], "format") = "text")   then 
        let $dummy := util:declare-option("exist:serialize","method=text media-type=text/plain indent=no")
        let $xml := stationutil:xml-producer()
        return
            if ($xml//ERROR) then
                 $xml//ERROR/text() 
            else                  
                switch (stationutil:get-parameter($stationutil:parameters_table[1], "level"))
                    case "network" return transform:transform($xml, doc("network.xsl"), ()) 
                    case "station" return transform:transform($xml, doc("station.xsl"), ())
                    case "channel" return transform:transform($xml, doc("channel.xsl"), ())
                default return ()
    else
        let $dummy := util:declare-option("exist:serialize","method=json media-type=application/json indent=yes")
        
        let $xml := stationutil:xml-producer()
        return 
            if ($xml//ERROR) then
                 $xml//ERROR/text() 
            else      
            <root>{$xml}</root>
             
    )
else 
    stationutil:badrequest_error($stationutil:parameters_table)    

};

(: TODO apply to POST also :)
declare function stationutil:use_shortcut() as xs:boolean {
  
    let $param_list := request:get-parameter-names()
    let $err_param_list := sum(for $param in $param_list
    return
               
      if (matches($param ,"^channel$|^cha$|^location$|^loc$|^minlatitude$|^minlat$|^maxlatitude$|^maxlat$|^minlongitude$|^minlon$|^maxlongitude$|^maxlon$|^starttime$|^start$|^endtime$|^end$|^startbefore$|^endbefore$|^startafter$|^endafter$|^latitude$|^lat$|^longitude$|^lon$|^maxradius$|^minradius$|^maxradiuskm$|^minradiuskm$|^includerestricted$" )) 
      then 1
      else 0
      )  
        
        
return  $err_param_list <1
    
};

(:TODO launch function for a full request :)
declare function stationutil:full_data_requested() as xs:boolean {

    (: Is all data requested ? :)
(:    let $log := util:log("info", "full_data_requested"):)
    let $param_list := request:get-parameter-names()
    let $err_param_list := sum(for $param in $param_list
    return
      if (matches($param ,"^minlatitude$|^minlat$|^maxlatitude$|^maxlat$|^minlongitude$|^minlon$|^maxlongitude$|^maxlon$|^starttime$|^start$|^endtime$|^end$|^startbefore$|^endbefore$|^startafter$|^endafter$|^latitude$|^lat$|^longitude$|^lon$|^maxradius$|^minradius$|^maxradiuskm$|^minradiuskm$|^includerestricted$" )) 
      then 1
      else 0
    )
    
    let $network  := stationutil:get-parameter($stationutil:parameters_table[1], "network_pattern" )
    let $station  := stationutil:get-parameter($stationutil:parameters_table[1], "station_pattern")
    let $channel  := stationutil:get-parameter($stationutil:parameters_table[1], "channel_pattern")
    let $location := stationutil:get-parameter($stationutil:parameters_table[1], "location_pattern")
(:    let $log := util:log("info", "network_pattern " || $network  || '(^.*$)'):)
(:    let $log := util:log("info", "station_pattern " || $station  ):)
(:    let $log := util:log("info", "channel_pattern " || $channel  ):)
(:    let $log := util:log("info", "location_pattern " || $location  ):)
    return  $err_param_list <1 and ($network = ('(^.*$)')) and ($station = ('(^.*$)'))  and ($channel = ('(^.*$)'))  and  ($location = ('(^.*$)')) 
};


(:Select case no channel constraints :)
declare function stationutil:use_no_channel_constraint() as xs:boolean {
  
    let $param_list := request:get-parameter-names()
    let $err_param_list := sum(for $param in $param_list
    return
               
      if (matches($param ,"^channel$|^cha$|^location$|^loc$|^starttime$|^start$|^endtime$|^end$|^startbefore$|^endbefore$|^startafter$|^endafter$|^maxradius$|^minradius$|^maxradiuskm$|^minradiuskm$|^includerestricted$" )) 
      then 1
      else 0
      )  
        
        
return  $err_param_list <1
    
};

(: Only one station code :)
declare function stationutil:no_wild_station() as xs:boolean {
  
    let $station := stationutil:get-parameter($stationutil:parameters_table[1], "station_pattern")
(:    let $sta := stationutil:get-parameter($stationutil:parameters_table[1], "sta"):)
    let $log := util:log("info", "station " || $station  )
    return
    not(contains($station,'.') or contains($station,'|'))
(:    or contains($sta,'*')) :)
 
}; 

declare function stationutil:unknown_parameter_from_GET() as xs:string* {
    let $param_list := request:get-parameter-names()
    
    let $err_param_list := for $param in $param_list
    return
        ( 
            if (matches($param,"^network$|^net$|^station$|^sta$|^channel$|^cha$|^location$|^loc$|^minlatitude$|^minlat$|^maxlatitude$|^maxlat$|^minlongitude$|^minlon$|^maxlongitude$|^maxlon$|^starttime$|^start$|^endtime$|^end$|^startbefore$|^endbefore$|^startafter$|^endafter$|^updatedafter$|^latitude$|^lat$|^longitude$|^lon$|^maxradius$|^minradius$|^maxradiuskm$|^minradiuskm$|^includerestricted$|^nodata$|^level$|^format$")) 
            then ()
            else $param 
        )
    return
       $err_param_list
}
;

declare function stationutil:unknown_parameter_from_POST() as xs:string* {
    let $param_list := stationutil:get-parameter-names()
    
    let $err_param_list := for $param in $param_list
    return
        ( 
            if (matches($param,"^network$|^net$|^station$|^sta$|^channel$|^cha$|^location$|^loc$|^minlatitude$|^minlat$|^maxlatitude$|^maxlat$|^minlongitude$|^minlon$|^maxlongitude$|^maxlon$|^starttime$|^start$|^endtime$|^end$|^startbefore$|^endbefore$|^startafter$|^endafter$|^updatedafter$|^latitude$|^lat$|^longitude$|^lon$|^maxradius$|^minradius$|^maxradiuskm$|^minradiuskm$|^includerestricted$|^nodata$|^level$|^format$")) 
            then ()
            else $param 
        )
    return
       $err_param_list
}
;

(: TODO  :)
(: POST  locationCode -- :)
(: TODO :)

(:~
 : @return the Station XML or an error :)
declare function stationutil:xml-producer() {
(:let $dummy := util:declare-option("exist:serialize","method=xml media-type=text/xml indent=no"):)
let $content :=
    switch (stationutil:get-parameter($stationutil:parameters_table[1], "level"))
    case "network" return 
        if (request:get-method()="POST") 
        then
            stationutil:query_core_POST($stationutil:parameters_table,"network")
        else
            if ( stationutil:no_wild_station() ) then
                stationutil:query_core_fixed_station($stationutil:parameters_table,"network")
            else            
            if ( stationutil:full_data_requested() ) then
                stationutil:query_core_full_data($stationutil:parameters_table,"network")
            else    
(:     TODO EXPLOIT           stationutil:query_core_level_network_station($stationutil:parameters_table,"network") :)
                stationutil:query_core($stationutil:parameters_table,"network")
    case "station" return 
        if (request:get-method()="POST") 
        then
            stationutil:query_core_POST($stationutil:parameters_table,"station")
        else
            if ( stationutil:no_wild_station() ) then
                stationutil:query_core_fixed_station($stationutil:parameters_table,"station")
            else            
            if ( stationutil:full_data_requested() ) then
                stationutil:query_core_full_data($stationutil:parameters_table,"station")
            else    
(: FIXME            if ( stationutil:use_no_channel_constraint() ) then:)
(:                stationutil:query_core_level_station_no_channel_constraint($stationutil:parameters_table,"station"):)
(:            else        :)
(:                stationutil:query_core_level_network_station($stationutil:parameters_table,"station"):)
                stationutil:query_core($stationutil:parameters_table,"station")
    case "channel" return 
        if (request:get-method()="POST") 
            then
                stationutil:query_core_POST($stationutil:parameters_table,"channel")
            else
                if ( stationutil:no_wild_station() ) then
                    stationutil:query_core_fixed_station($stationutil:parameters_table,"channel")
                else                            
                if (stationutil:use_shortcut()) then 
                    stationutil:query_core_channel_response_shortcut($stationutil:parameters_table)
                else                
                    stationutil:query_core($stationutil:parameters_table,"channel")
                    
    case "response" return 
        if (request:get-method()="POST") 
            then
                stationutil:query_core_POST($stationutil:parameters_table,"response")
            else
                if ( stationutil:no_wild_station() ) then
                    stationutil:query_core_fixed_station($stationutil:parameters_table,"response")
                else            
                if (stationutil:use_shortcut()) then 
                    stationutil:query_core_channel_response_shortcut($stationutil:parameters_table)
                else                
                    stationutil:query_core($stationutil:parameters_table,"response")
    default return ()

return
if (not(empty($content))) then
<FDSNStationXML xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.1" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.1.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">
<Source>eXistDB</Source>
<Sender>INGV-ONT</Sender>
<Module>INGV-ONT WEB SERVICE: fdsnws-station | version: {stationutil:version()}</Module>
{
            if (request:get-method()="POST") 
            then
                <ModuleURI>"{request:get-uri()}? 
{stationutil:getpostdata()}"</ModuleURI>
            else 
                <ModuleURI>{request:get-uri()}?{request:get-query-string() }</ModuleURI>
(: Modificato per togliere i doppi apici per json        <ModuleURI>{request:get-uri()}?{request:get-query-string() }</ModuleURI>:)
}
<Created>{current-dateTime()}</Created>
{$content}
</FDSNStationXML>
else
    stationutil:nodata_error()
};


declare function stationutil:if-empty
  ( $arg as item()* ,
    $value as item() )  as item()* {
  
  let $log := for $a allowing empty in $arg return util:log("info", "empty list: " || $a )
  for $a allowing empty in $arg 
  return
  if (string($a) != '')
  then data($a)
  else $value
 } ;

(:~ 
 : @return the <network> Station XML fragment given the $NSLCSE map of query parameters, found in the current collection.
 : Works only for GET, speedup avoiding constraints_onchannel_patterns
 : 
 :)


declare function stationutil:query_core_level_station_no_channel_constraint($NSLCSE as map()*, $level as xs:string){
(:declare function stationutil:query_cores($NSLCSE as map()*, $level as xs:string){    :)
(:DEBUG:)
(:try{:)
let $dummy := util:log("info", "query_core_level_station_no_channel_constraint" )


(:let $d:=if (stationutil:check_channels($NSLCSE)) then util:log("info", "Channels ok " ) else util:log("info", "No channels"  ):)
(:return:)
(:( :)
(:if (stationutil:check_channels($NSLCSE)) then :)
(:DEBUG:)
(:Prepare the output, discarding it only when sure no channels meet criteria avoid to check before, then create output:)
(:let $xml := :)

(:    DONE updatedafter ( :)
    let $since:= xs:dateTime($NSLCSE("updatedafter"))
    for $network in xmldb:find-last-modified-since(collection("/db/apps/fdsn-station/Station/")//Network ,$since) , $condition in $NSLCSE  
(:    for $network in collection("/db/apps/fdsn-station/Station/")//Network:)
(:    , $condition in $NSLCSE  :)
(:    let $condition := $NSLCSE:)
    let $minlatitude := xs:decimal($condition("minlatitude"))
    let $maxlatitude := xs:decimal($condition("maxlatitude"))
    let $minlongitude := xs:decimal($condition("minlongitude"))
    let $maxlongitude := xs:decimal($condition("maxlongitude"))

    let $Latitude:= $network/Station/Latitude
    let $Longitude:= $network/Station/Longitude
(:    let $CreationDate:= $network//Channel/@startDate:)
(:    let $TerminationDate:= if (empty($network//Channel/@endDate)) then $stationutil:defaults("future_time_as_datetime")  else $network//Channel/@endDate:)
    
    let $networkcode := $network/@code
    let $station:=$network//Station
    let $stationcode:=$station/@code
    let $lat := $station/Latitude
    let $lon := $station/Longitude    
    let $channel:=$station/Channel
(:    let $channelcode:=$channel/@code:)
(:    let $locationcode:=$channel/@locationCode:)
(:    let $CreationDate:= $channel/@startDate:)
(:    let $TerminationDate:= $channel/@endDate   :)
    (:TODO use $startDate,  $endDate?:)
    let $startDate := $network/@startDate
    let $endDate := $network/@endDate
    let $restrictedStatus:=$network/@restrictedStatus
(:    let $stationrestrictedStatus:=$network/Station/@restrictedStatus    :)
(:    let $channelrestrictedStatus:=$network//Channel/@restrictedStatus    :)
    let $Description := $network/Description
    let $identifier := $network/Identifier
    let $network_ingv_identifier := $network/ingv:Identifier

    where
        $Latitude  > $minlatitude and  
        $Latitude  < $maxlatitude and 
        $Longitude > $minlongitude and 
        $Longitude < $maxlongitude and
        matches($stationcode, $NSLCSE("station_pattern")) and
        matches($networkcode, $NSLCSE("network_pattern")) 
        group by $networkcode, $startDate, $endDate, $restrictedStatus, $Description, $network_ingv_identifier
(:        , $identifier:)
        order by $networkcode
    return
        
        <Network>
        {$networkcode}
        {$startDate} 
        {$endDate}
        {$restrictedStatus}
        {$Description}    
        {functx:distinct-deep($identifier)}
        {$network_ingv_identifier}
        <TotalNumberStations> {stationutil:stationcount($networkcode)} </TotalNumberStations>
        <SelectedNumberStations> {count($station)} </SelectedNumberStations>
        
        {    
(:        if ($level="station") then:)
(:  Sort before output, do not care of order of stations before (was hard to get it right)    :)
(:                fn:sort($stations,(), function($Station) {$Station/@code}):)
(:                for $s in $stations:)
(:                order by $s/@code:)
(:                return $s :)
(:TODO                $stations:)

        for $station in $network/Station
            let $stationcode:=$station/@code
            let $Latitude:=  xs:decimal($station/Latitude)
            let $Longitude:= xs:decimal($station/Longitude) 
            let $lat := $station/Latitude
            let $lon := $station/Longitude
         where 
            $Latitude  > $minlatitude and  
            $Latitude  < $maxlatitude and 
            $Longitude > $minlongitude and 
            $Longitude < $maxlongitude and
            matches($stationcode, $NSLCSE("station_pattern")) and
            matches($networkcode, $NSLCSE("network_pattern")) 
        group by $stationcode
        order by $stationcode
 
(:        for $sta in $station:)
        return
(:                stationutil:remove-elements(stationutil:remove-elements(stationutil:remove-elements($station ,"Channel"),"TotalNumberChannels"),"SelectedNumberChannels"):)
 stationutil:remove-elements($station ,"Channel")
(:        else ():)
        
        }
        </Network>

    
(:}:)
(:    catch err:* {()}:)
    
}; 


declare function stationutil:query_core_fixed_station_ok($NSLCSE as map()*, $level as xs:string){
(:DEBUG:)
(:try{:)
 
(: Supponiamo di eseguire codice diverso a seconda del livello, per network e station è sufficiente trovare tutte le network e station a cui appartiene
 : la stazione nominata, per channel e response si usa il codice completo di questa funzione
 : :)
 
let $dummy := util:log("info", "query_core_fixed_station_ok" )


(:let $d:=if (stationutil:check_channels($NSLCSE)) then util:log("info", "Channels ok " ) else util:log("info", "No channels"  ):)
(:return:)
(:( :)
(:if (stationutil:check_channels($NSLCSE)) then :)
(:DEBUG:)
(:Prepare the output, discarding it only when sure no channels meet criteria avoid to check before, then create output:)
(:let $xml := :)

(:    DONE updatedafter ( :)
    let $since:= xs:dateTime($NSLCSE("updatedafter"))
(:    TODO RIMETTERE A POSTO:)
    for $network in xmldb:find-last-modified-since(collection("/db/apps/fdsn-station/Station/")//Network/Station[@code=$NSLCSE("station")]/.. ,$since) , $condition in $NSLCSE  
(:    for $network in collection("/db/apps/fdsn-station/Station/")//Network/Station[@code=$NSLCSE("station")]/..:)
    
(:    let $condition := $NSLCSE  :)
    let $minlatitude := xs:decimal($condition("minlatitude"))
    let $maxlatitude := xs:decimal($condition("maxlatitude"))
    let $minlongitude := xs:decimal($condition("minlongitude"))
    let $maxlongitude := xs:decimal($condition("maxlongitude"))

    let $Latitude:= $network/Station/Latitude
    let $Longitude:= $network/Station/Longitude
    let $CreationDate:= $network//Channel/@startDate
(:    let $TerminationDate:= $network//Channel/@endDate:)
    let $TerminationDate:= if (empty($network//Channel/@endDate)) then $stationutil:defaults("future_time_as_datetime")  else $network//Channel/@endDate
    
    let $networkcode := $network/@code
    let $station:=$network//Station
    let $stationcode:=$station/@code
    let $lat := $station/Latitude
    let $lon := $station/Longitude    
    let $channel:=$station/Channel
    let $channelcode:=$channel/@code
    let $locationcode:=$channel/@locationCode
    let $CreationDate:= $channel/@startDate
    let $TerminationDate:= $channel/@endDate   
    (:TODO use $startDate,  $endDate?:)
    let $startDate := $network/@startDate
    let $endDate := $network/@endDate
    let $restrictedStatus:=$network/@restrictedStatus
    let $stationrestrictedStatus:=$network/Station/@restrictedStatus    
    let $channelrestrictedStatus:=$network//Channel/@restrictedStatus    
    let $Description := $network/Description
    let $identifier := $network/Identifier
    let $network_ingv_identifier := $network/ingv:Identifier
(:    let $log := util:log("info", "networks: "):)
    let $stations:=
    (
(:        for $station in $network/Station[@code=$NSLCSE("station")]:)
        for $station in $network/Station
            let $stationcode:=$station/@code
            let $stationstartDate := $station/@startDate
            let $stationendDate := $station/@endDate
            let $stationrestrictedStatus := $station/@restrictedStatus
            let $channels:=$station//Channel
            let $channelcode:=$channel/@code
            let $locationcode := $channel/@locationCode          
            let $Latitude:=  xs:decimal($station/Latitude)
            let $Longitude:= xs:decimal($station/Longitude) 
            let $lat := $station/Latitude
            let $lon := $station/Longitude
            let $CreationDate:= $channel/@startDate
            let $TerminationDate := $channel/@endDate
(:            let $log := util:log("info", "stations: "):)
            let $selected_channels:= (
                for $channel in $channels
                let $channelcode:=$channel/@code
                let $locationcode:=$channel/@locationCode
                let $channelrestrictedStatus := $channel/@restrictedStatus                                           
                let $CreationDate:= $channel/@startDate
                let $TerminationDate:= $channel/@endDate
(:                let $log := util:log("info", "channels: "):)
                where
(:                    matches($stationcode, $NSLCSE("station_pattern")) and:)
                    matches($networkcode, $NSLCSE("network_pattern")) and
                    matches($channelcode, $NSLCSE("channel_pattern")) and
                    matches($locationcode, $NSLCSE("location_pattern")) and
                    stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and            
                    stationutil:check_radius($condition, $lat,$lon) and                    
                    stationutil:check_restricted($condition,$channelrestrictedStatus) 
                return 
                         $channel 

            )
(:            let $channelcount:=count ($selected_channels):)
        where 
            $Latitude  > $minlatitude and  
            $Latitude  < $maxlatitude and 
            $Longitude > $minlongitude and 
            $Longitude < $maxlongitude and
(:            matches($stationcode, $NSLCSE("station_pattern")) and:)
            matches($networkcode, $NSLCSE("network_pattern")) and
            matches($channelcode, $NSLCSE("channel_pattern")) and
            matches($locationcode, $NSLCSE("location_pattern")) and
            stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and              
            stationutil:check_radius($condition, $lat,$lon) and
            stationutil:check_restricted($condition,$stationrestrictedStatus)
(:            and ($channelcount>0):)
            and (count ($selected_channels)>0)
        group by $stationcode, $stationstartDate, $stationendDate, $stationrestrictedStatus
        order by $stationcode
        return 
                <Station>
                {$stationcode}  
                </Station>
            
    )
(:  TODO replace it again                  {$channelcount} :)
    where
        $Latitude  > $minlatitude and  
        $Latitude  < $maxlatitude and 
        $Longitude > $minlongitude and 
        $Longitude < $maxlongitude and
(:        matches($stationcode, $NSLCSE("station_pattern")) and:)
        matches($networkcode, $NSLCSE("network_pattern")) and
        matches($channelcode, $NSLCSE("channel_pattern")) and
        matches($locationcode, $NSLCSE("location_pattern")) and     
(:        stationutil:check_radius($condition, $lat,$lon) and TODO FIXME :)
        stationutil:check_restricted($condition,$restrictedStatus) and          
        stationutil:check_restricted($condition,$stationrestrictedStatus) and  
        stationutil:check_restricted($condition,$channelrestrictedStatus) and
        stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) 
        and 
        (count($stations)>0)
        group by $networkcode,  $startDate, $endDate, $restrictedStatus, $Description, $network_ingv_identifier
(:        , $identifier:)
        order by $networkcode
    return
        
        <Network>
        {$networkcode}
        {$startDate} 
        {$endDate}
        {$restrictedStatus}
        {$Description}    
        {$identifier}
        
        {$network_ingv_identifier}
        <TotalNumberStations> {stationutil:stationcount($networkcode)} </TotalNumberStations>
        <SelectedNumberStations> {count($stations)} </SelectedNumberStations>
        {    
            if ($level!="network") then
(:  Sort before output, do not care of order of stations before (was hard to get it right)    :)
(:                fn:sort($stations,(), function($Station) {$Station/@code}):)
(:                for $s in $stations:)
(:                order by $s/@code:)
(:                return $s :)
(:TODO                $stations:)
                        for $station in $network/Station[@code=$NSLCSE("station")]
            let $stationcode:=$station/@code
            let $stationstartDate := $station/@startDate
            let $stationendDate := $station/@endDate
            let $stationrestrictedStatus := $station/@restrictedStatus
            let $channels:=$station//Channel
            let $channelcode:=$channel/@code
            let $locationcode := $channel/@locationCode          
            let $Latitude:=  xs:decimal($station/Latitude)
            let $Longitude:= xs:decimal($station/Longitude) 
            let $lat := $station/Latitude
            let $lon := $station/Longitude
            let $CreationDate:= $channel/@startDate
            let $TerminationDate := $channel/@endDate
(:            let $log := util:log("info", "stations: "):)
            let $selected_channels:= (
                for $channel in $channels
                let $channelcode:=$channel/@code
                let $locationcode:=$channel/@locationCode
                let $channelrestrictedStatus := $channel/@restrictedStatus                                           
                let $CreationDate:= $channel/@startDate
                let $TerminationDate:= $channel/@endDate
(:                let $log := util:log("info", "channels: "):)
                where
(:                    matches($stationcode, $NSLCSE("station_pattern")) and:)
                    matches($networkcode, $NSLCSE("network_pattern")) and
                    matches($channelcode, $NSLCSE("channel_pattern")) and
                    matches($locationcode, $NSLCSE("location_pattern")) and
                    stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and            
                    stationutil:check_radius($condition, $lat,$lon) and                    
                    stationutil:check_restricted($condition,$channelrestrictedStatus) 
                return 
                     if ($level="channel") then ( 
                         stationutil:remove-elements($channel,"Stage")
                         )
                     else
                         $channel 

            )
(:            let $channelcount:=count ($selected_channels):)
        where 
            $Latitude  > $minlatitude and  
            $Latitude  < $maxlatitude and 
            $Longitude > $minlongitude and 
            $Longitude < $maxlongitude and
(:            matches($stationcode, $NSLCSE("station_pattern")) and:)
            matches($networkcode, $NSLCSE("network_pattern")) and
            matches($channelcode, $NSLCSE("channel_pattern")) and
            matches($locationcode, $NSLCSE("location_pattern")) and
            stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and              
            stationutil:check_radius($condition, $lat,$lon) and
            stationutil:check_restricted($condition,$stationrestrictedStatus)
(:            and ($channelcount>0):)
            and (count ($selected_channels)>0)
        group by $stationcode, $stationstartDate, $stationendDate, $stationrestrictedStatus
        order by $stationcode
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
                {$station/TerminationDate}
                {    
                if ($level="response" or $level="channel") then
                    (
                    <TotalNumberChannels>
                    {count($station/Channel)}
                    </TotalNumberChannels>,
                    <SelectedNumberChannels>
                    {count ($selected_channels)}
                    </SelectedNumberChannels>,
                    $selected_channels
                    )
                else 
                    ()
                }
                </Station>
                
                
            else    
                ()
        }
        </Network>

    
(:}:)
(:    catch err:* {()}:)
    
}; 


declare function stationutil:query_core_fixed_station($NSLCSE as map()*, $level as xs:string){
(:DEBUG:)
(:try{:)
 
(: Supponiamo di eseguire codice diverso a seconda del livello, per network e station è sufficiente trovare tutte le network e station a cui appartiene
 : la stazione nominata, per channel e response si usa il codice completo di questa funzione
 : :)
 
let $dummy := util:log("info", "query_core_fixed_station" )


(:let $d:=if (stationutil:check_channels($NSLCSE)) then util:log("info", "Channels ok " ) else util:log("info", "No channels"  ):)
(:return:)
(:( :)
(:if (stationutil:check_channels($NSLCSE)) then :)
(:DEBUG:)
(:Prepare the output, discarding it only when sure no channels meet criteria avoid to check before, then create output:)
(:let $xml := :)



(:    DONE updatedafter ( :)
    let $since:= xs:dateTime($NSLCSE("updatedafter"))
(:    TODO RIMETTERE A POSTO:)
    for $network in xmldb:find-last-modified-since(collection("/db/apps/fdsn-station/Station/")//Network/Station[@code=$NSLCSE("station")]/.. ,$since) , $condition in $NSLCSE  
(:    for $network in collection("/db/apps/fdsn-station/Station/")//Network/Station[@code=$NSLCSE("station")]/..:)
    
(:    let $condition := $NSLCSE  :)
    let $minlatitude := xs:decimal($condition("minlatitude"))
    let $maxlatitude := xs:decimal($condition("maxlatitude"))
    let $minlongitude := xs:decimal($condition("minlongitude"))
    let $maxlongitude := xs:decimal($condition("maxlongitude"))

    let $Latitude:= $network/Station/Latitude
    let $Longitude:= $network/Station/Longitude
    let $CreationDate:= $network//Channel/@startDate
(:    let $TerminationDate:= $network//Channel/@endDate:)
    let $TerminationDate:= if (empty($network//Channel/@endDate)) then $stationutil:defaults("future_time_as_datetime")  else $network//Channel/@endDate
    
    let $networkcode := $network/@code
    let $station:=$network//Station
    let $stationcode:=$station/@code
    let $lat := $station/Latitude
    let $lon := $station/Longitude    
    let $channel:=$station/Channel
    let $channelcode:=$channel/@code
    let $locationcode:=$channel/@locationCode
    let $CreationDate:= $channel/@startDate
    let $TerminationDate:= $channel/@endDate   
    (:TODO use $startDate,  $endDate?:)
    let $startDate := $network/@startDate
    let $endDate := $network/@endDate
    let $restrictedStatus:=$network/@restrictedStatus
    let $stationrestrictedStatus:=$network/Station/@restrictedStatus    
    let $channelrestrictedStatus:=$network//Channel/@restrictedStatus    
    let $Description := $network/Description
    let $identifier := $network/Identifier
    let $network_ingv_identifier := $network/ingv:Identifier
(:    let $log := util:log("info", "networks: "):)
    let $stations:=
    (
(:        for $station in $network/Station[@code=$NSLCSE("station")]:)
        for $station in $network/Station
            let $stationcode:=$station/@code
            let $stationstartDate := $station/@startDate
            let $stationendDate := $station/@endDate
            let $stationrestrictedStatus := $station/@restrictedStatus
            let $channels:=$station//Channel
            let $channelcode:=$channel/@code
            let $locationcode := $channel/@locationCode          
            let $Latitude:=  xs:decimal($station/Latitude)
            let $Longitude:= xs:decimal($station/Longitude) 
            let $lat := $station/Latitude
            let $lon := $station/Longitude
            let $CreationDate:= $channel/@startDate
            let $TerminationDate := $channel/@endDate
(:            let $log := util:log("info", "stations: "):)
            let $selected_channels:= (
                for $channel in $channels
                let $channelcode:=$channel/@code
                let $locationcode:=$channel/@locationCode
                let $channelrestrictedStatus := $channel/@restrictedStatus                                           
                let $CreationDate:= $channel/@startDate
                let $TerminationDate:= $channel/@endDate
(:                let $log := util:log("info", "channels: "):)
                where
                    matches($stationcode, $NSLCSE("station_pattern")) and
                    matches($networkcode, $NSLCSE("network_pattern")) and
                    matches($channelcode, $NSLCSE("channel_pattern")) and
                    matches($locationcode, $NSLCSE("location_pattern")) and
                    stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and            
                    stationutil:check_radius($condition, $lat,$lon) and                    
                    stationutil:check_restricted($condition,$channelrestrictedStatus) 
                return 
                         $channel 

            )
(:            let $channelcount:=count ($selected_channels):)
        where 
            $Latitude  > $minlatitude and  
            $Latitude  < $maxlatitude and 
            $Longitude > $minlongitude and 
            $Longitude < $maxlongitude and
            matches($stationcode, $NSLCSE("station_pattern")) and
            matches($networkcode, $NSLCSE("network_pattern")) and
            matches($channelcode, $NSLCSE("channel_pattern")) and
            matches($locationcode, $NSLCSE("location_pattern")) and
            stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and              
            stationutil:check_radius($condition, $lat,$lon) and
            stationutil:check_restricted($condition,$stationrestrictedStatus)
(:            and ($channelcount>0):)
            and (count ($selected_channels)>0)
        group by $stationcode, $stationstartDate, $stationendDate, $stationrestrictedStatus
        order by $stationcode
        return 
                <Station>
                {$stationcode}  
                </Station>
            
    )
(:  TODO replace it again                  {$channelcount} :)
    where
        $Latitude  > $minlatitude and  
        $Latitude  < $maxlatitude and 
        $Longitude > $minlongitude and 
        $Longitude < $maxlongitude and
        matches($stationcode, $NSLCSE("station_pattern")) and
        matches($networkcode, $NSLCSE("network_pattern")) and
        matches($channelcode, $NSLCSE("channel_pattern")) and
        matches($locationcode, $NSLCSE("location_pattern")) and     
(:        stationutil:check_radius($condition, $lat,$lon) and TODO FIXME :)
        stationutil:check_restricted($condition,$restrictedStatus) and          
        stationutil:check_restricted($condition,$stationrestrictedStatus) and  
        stationutil:check_restricted($condition,$channelrestrictedStatus) and
        stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) 
        and 
        (count($stations)>0)
        group by $networkcode,  $startDate, $endDate, $restrictedStatus, $Description, $network_ingv_identifier
(:        , $identifier:)
        order by $networkcode
    return
        
        <Network>
        {$networkcode}
        {$startDate} 
        {$endDate}
        {$restrictedStatus}
        {$Description}    
        {functx:distinct-deep($identifier)}
        {$network_ingv_identifier}
        <TotalNumberStations> {stationutil:stationcount($networkcode)} </TotalNumberStations>
        <SelectedNumberStations> {count($stations)} </SelectedNumberStations>
        {    
            if ($level!="network") then
(:  Sort before output, do not care of order of stations before (was hard to get it right)    :)
(:                fn:sort($stations,(), function($Station) {$Station/@code}):)
(:                for $s in $stations:)
(:                order by $s/@code:)
(:                return $s :)
(:TODO                $stations:)
            for $station in $network/Station
            let $stationcode:=$station/@code
            let $stationstartDate := $station/@startDate
            let $stationendDate := $station/@endDate
            let $stationrestrictedStatus := $station/@restrictedStatus
            let $channels:=$station//Channel
            let $channelcode:=$channel/@code
            let $locationcode := $channel/@locationCode          
            let $Latitude:=  xs:decimal($station/Latitude)
            let $Longitude:= xs:decimal($station/Longitude) 
            let $lat := $station/Latitude
            let $lon := $station/Longitude
            let $CreationDate:= $channel/@startDate
            let $TerminationDate := $channel/@endDate
(:            let $log := util:log("info", "stations: "):)
            let $selected_channels:= (
                for $channel in $channels
                let $channelcode:=$channel/@code
                let $locationcode:=$channel/@locationCode
                let $channelrestrictedStatus := $channel/@restrictedStatus                                           
                let $CreationDate:= $channel/@startDate
                let $TerminationDate:= $channel/@endDate
(:                let $log := util:log("info", "channels: "):)
                where
                    matches($stationcode, $NSLCSE("station_pattern")) and
                    matches($networkcode, $NSLCSE("network_pattern")) and
                    matches($channelcode, $NSLCSE("channel_pattern")) and
                    matches($locationcode, $NSLCSE("location_pattern")) and
                    stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and            
                    stationutil:check_radius($condition, $lat,$lon) and                    
                    stationutil:check_restricted($condition,$channelrestrictedStatus) 
                return 
                     if ($level="channel") then ( 
                         stationutil:remove-elements($channel,"Stage")
                         )
                     else
                         $channel 

            )
(:            let $channelcount:=count ($selected_channels):)
        where 
            $Latitude  > $minlatitude and  
            $Latitude  < $maxlatitude and 
            $Longitude > $minlongitude and 
            $Longitude < $maxlongitude and
(:            matches($stationcode, $NSLCSE("station_pattern")) and:)
            matches($networkcode, $NSLCSE("network_pattern")) and
            matches($channelcode, $NSLCSE("channel_pattern")) and
            matches($locationcode, $NSLCSE("location_pattern")) and
            stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and              
            stationutil:check_radius($condition, $lat,$lon) and
            stationutil:check_restricted($condition,$stationrestrictedStatus)
(:            and ($channelcount>0):)
            and (count ($selected_channels)>0)
        group by $stationcode, $stationstartDate, $stationendDate, $stationrestrictedStatus
        order by $stationcode
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
                {$station/TerminationDate}
                {    
                if ($level="response" or $level="channel") then
                    (
                    <TotalNumberChannels>
                    {count($station/Channel)}
                    </TotalNumberChannels>,
                    <SelectedNumberChannels>
                    {count ($selected_channels)}
                    </SelectedNumberChannels>,
                    $selected_channels
                    )
                else 
                    ()
                }
                </Station>
                
                
            else    
                ()
        }
        </Network>

    
(:}:)
(:    catch err:* {()}:)
    
}; 



(:TODO all channels requested but only bounding box and time constraint 
 : 
 : declare function stationutil:query_core_all_where_when($NSLCSE as map()*, $level as xs:string){
 : 
 : :)

declare function stationutil:query_core_full_data($NSLCSE as map()*, $level as xs:string){
(:DEBUG:)
(:try{:)
let $dummy := util:log("info", "query_core_full_data" )


(:    DONE updatedafter ( :)
    let $since:= xs:dateTime($NSLCSE("updatedafter"))
(:    TODO RIMETTERE A POSTO:)
(:    for $network in xmldb:find-last-modified-since(collection("/db/apps/fdsn-station/Station/")//Network ,$since) , $condition in $NSLCSE  :)
    for $network in collection("/db/apps/fdsn-station/Station/")//Network 

    let $CreationDate:= $network//Channel/@startDate
(:    let $TerminationDate:= $network//Channel/@endDate:)
    let $TerminationDate:= if (empty($network//Channel/@endDate)) then $stationutil:defaults("future_time_as_datetime")  else $network//Channel/@endDate
    
    let $networkcode := $network/@code
    let $station:=$network//Station
    let $stationcode:=$station/@code
    let $lat := $station/Latitude
    let $lon := $station/Longitude    
    let $channel:=$station/Channel
    let $channelcode:=$channel/@code
    let $locationcode:=$channel/@locationCode
    let $CreationDate:= $channel/@startDate
    let $TerminationDate:= $channel/@endDate   
    (:TODO use $startDate,  $endDate?:)
    let $startDate := $network/@startDate
    let $endDate := $network/@endDate
    let $restrictedStatus:=$network/@restrictedStatus
    let $stationrestrictedStatus:=$network/Station/@restrictedStatus    
    let $channelrestrictedStatus:=$network//Channel/@restrictedStatus    
    let $Description := $network/Description
    let $identifier := $network/Identifier
    let $identifier_type:=$identifier/@type
    let $network_ingv_identifier := $network/ingv:Identifier
(:    let $log := util:log("info", "networks: "):)
(:    let $stations:= :)
(:    ( :)
(:        for $station in $network/Station:)
(:            let $stationcode:=$station/@code:)
(:            let $stationstartDate := $station/@startDate:)
(:            let $stationendDate := $station/@endDate:)
(:            let $stationrestrictedStatus := $station/@restrictedStatus:)
(:            let $channels:=$station//Channel:)
(:            let $channelcode:=$channel/@code:)
(:            let $locationcode := $channel/@locationCode          :)
(:            let $Latitude:=  xs:decimal($station/Latitude):)
(:            let $Longitude:= xs:decimal($station/Longitude) :)
(:            let $lat := $station/Latitude:)
(:            let $lon := $station/Longitude:)
(:            let $CreationDate:= $channel/@startDate:)
(:            let $TerminationDate := $channel/@endDate:)
(:(:            let $log := util:log("info", "stations: "):):)
(:            let $selected_channels:= ( :)
(:                for $channel in $channels:)
(:                let $channelcode:=$channel/@code:)
(:                let $locationcode:=$channel/@locationCode:)
(:                let $channelrestrictedStatus := $channel/@restrictedStatus                                           :)
(:                let $CreationDate:= $channel/@startDate:)
(:                let $TerminationDate:= $channel/@endDate:)
(:(:                let $log := util:log("info", "channels: "):):)
(::)
(:                return :)
(:                         $channel :)
(::)
(:            ):)
(:(:            let $channelcount:=count ($selected_channels):):)
(::)
(:        group by $stationcode, $stationstartDate, $stationendDate, $stationrestrictedStatus:)
(:        order by $stationcode:)
(:        return :)
(:                <Station>:)
(:                {$stationcode}  :)
(:                </Station>:)
(:            :)
(:    ):)
(:  TODO replace it again                  {$channelcount} :)
(:FIX ODC TEST 
 : il problema del group by per i campi che sono sequenze di elementi uguali se non si raggruppa
 : ma che per raggruppare devo conoscere e inserire nella clausola:)
        group by $networkcode ,  $startDate, $endDate,$restrictedStatus , $network_ingv_identifier, $Description
(:         $restrictedStatus, $Description, $network_ingv_identifier:)
(:        , $identifier:)
(:        , $identifier_type:)
(:        group by $networkcode,  $startDate, $endDate, $restrictedStatus, $Description, $identifier:)
(:        group by $networkcode,  $startDate, $endDate, $restrictedStatus, $Description:)
(:        <Identifier>{distinct-values($identifier)}</Identifier>:)
(:        {$identifier}:)
(:        {$network_ingv_identifier} :)
(:        {$Description}    :)
(:{$network/*[not(name() = ("Station", "TotalNumberStations", "SelectedNumberStations", "Description")) ]}   :)
(:        {$network_ingv_identifier} :)
        order by $networkcode
    return
        
        <Network>
        {$networkcode}
        {$startDate} 
        {$endDate}
        {$restrictedStatus}
        {$Description}
        {functx:distinct-deep($identifier)}
        {$network_ingv_identifier}
        {functx:distinct-deep($network/*[not(name() = ("Identifier","Station", "TotalNumberStations", "SelectedNumberStations", "Description", "ingv:Identifier")) ])}
        <TotalNumberStations> {stationutil:stationcount($networkcode)} </TotalNumberStations>
        <SelectedNumberStations> {count($station)} </SelectedNumberStations>
        {    
            if ($level!="network") then
(:  Sort before output, do not care of order of stations before (was hard to get it right)    :)
(:                fn:sort($stations,(), function($Station) {$Station/@code}):)
(:                for $s in $stations:)
(:                order by $s/@code:)
(:                return $s :)
(:TODO                $stations:)
            for $station in $network/Station
            let $stationcode:=$station/@code
            let $stationstartDate := $station/@startDate
            let $stationendDate := $station/@endDate
            let $stationrestrictedStatus := $station/@restrictedStatus
            let $channels:=$station//Channel
            let $channelcode:=$channel/@code
            let $locationcode := $channel/@locationCode          
            let $Latitude:=  xs:decimal($station/Latitude)
            let $Longitude:= xs:decimal($station/Longitude) 
            let $lat := $station/Latitude
            let $lon := $station/Longitude
            let $CreationDate:= $channel/@startDate
            let $TerminationDate := $channel/@endDate
(:            let $log := util:log("info", "stations: "):)

        group by $stationcode, $stationstartDate, $stationendDate, $stationrestrictedStatus
        order by $stationcode
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
                {$station/TerminationDate}    
                {    
                if ($level="response" or $level="channel") then
                    (
                    <TotalNumberChannels>
                    {count($station/Channel)}
                    </TotalNumberChannels>,
                    <SelectedNumberChannels>
                    {count($station/Channel)}
                    </SelectedNumberChannels>,
                    $channels
                    )
                else 
                    ()
                }
                </Station>
                
                
            else    
                ()
        }
        </Network>

    
(:}:)
(:    catch err:* {()}:)
    
}; 


declare function stationutil:query_core_level_network_station($NSLCSE as map()*, $level as xs:string){
(:DEBUG:)
(:try{:)
let $dummy := util:log("info", "query_core_level_network_station" )


(:Prepare the output, discarding it only when sure no channels meet criteria avoid to check before, then create output:)
(:let $xml := :)

(:    DONE updatedafter ( :)
    let $since:= xs:dateTime($NSLCSE("updatedafter"))
(:    TODO RIMETTERE A POSTO:)
    for $network in xmldb:find-last-modified-since(collection("/db/apps/fdsn-station/Station/")//Network ,$since) 
    , $condition in $NSLCSE  
(:    for $network in collection("/db/apps/fdsn-station/Station/")//Network[@code=$NSLCSE("network")] :)
(:    let $condition := $NSLCSE  :)
    let $minlatitude := xs:decimal($condition("minlatitude"))
    let $maxlatitude := xs:decimal($condition("maxlatitude"))
    let $minlongitude := xs:decimal($condition("minlongitude"))
    let $maxlongitude := xs:decimal($condition("maxlongitude"))

    let $Latitude:= $network/Station/Latitude
    let $Longitude:= $network/Station/Longitude
    let $CreationDate:= $network//Channel/@startDate
(:    let $TerminationDate:= $network//Channel/@endDate:)
    let $TerminationDate:= if (empty($network//Channel/@endDate)) then $stationutil:defaults("future_time_as_datetime")  else $network//Channel/@endDate
    
    let $networkcode := $network/@code
    let $station:=$network//Station
    let $stationcode:=$station/@code
    let $lat := $station/Latitude
    let $lon := $station/Longitude    
    let $channel:=$station/Channel
    let $channelcode:=$channel/@code
    let $locationcode:=$channel/@locationCode
    let $CreationDate:= $channel/@startDate
    let $TerminationDate:= $channel/@endDate   
    (:TODO use $startDate,  $endDate?:)
    let $startDate := $network/@startDate
    let $endDate := $network/@endDate
    let $restrictedStatus:=$network/@restrictedStatus
    let $stationrestrictedStatus:=$network/Station/@restrictedStatus    
    let $channelrestrictedStatus:=$network//Channel/@restrictedStatus    
    let $Description := $network/Description
    let $identifier := $network/Identifier
    let $network_ingv_identifier := $network/ingv:Identifier
(:    let $log := util:log("info", "networks: "):)
    let $stations:=
    (
        unordered {
            for $station in $network/Station
            let $stationcode:=$station/@code
            let $stationstartDate := $station/@startDate
            let $stationendDate := $station/@endDate
            let $stationrestrictedStatus := $station/@restrictedStatus
            let $channels:=$station//Channel
            let $channelcode:=$channel/@code
            let $locationcode := $channel/@locationCode          
            let $Latitude:=  xs:decimal($station/Latitude)
            let $Longitude:= xs:decimal($station/Longitude) 
            let $lat := $station/Latitude
            let $lon := $station/Longitude
            let $CreationDate:= $channel/@startDate
            let $TerminationDate := $channel/@endDate
(:            let $log := util:log("info", "stations: "):)
            let $selected_channels:= (
                for $channel in $channels
                let $channelcode:=$channel/@code
                let $locationcode:=$channel/@locationCode
                let $channelrestrictedStatus := $channel/@restrictedStatus                                           
                let $CreationDate:= $channel/@startDate
                let $TerminationDate:= $channel/@endDate
(:                let $log := util:log("info", "channels: "):)
                where
                    matches($stationcode, $NSLCSE("station_pattern")) and
                    matches($networkcode, $NSLCSE("network_pattern")) and
                    matches($channelcode, $NSLCSE("channel_pattern")) and
                    matches($locationcode, $NSLCSE("location_pattern")) and
                    stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and            
                    stationutil:check_radius($condition, $lat,$lon) and                    
                    stationutil:check_restricted($condition,$channelrestrictedStatus) 
                return 
                         $channel 

            )
(:            let $channelcount:=count ($selected_channels):)
        where 
            $Latitude  > $minlatitude and  
            $Latitude  < $maxlatitude and 
            $Longitude > $minlongitude and 
            $Longitude < $maxlongitude and
            matches($stationcode, $NSLCSE("station_pattern")) and
            matches($networkcode, $NSLCSE("network_pattern")) and
            matches($channelcode, $NSLCSE("channel_pattern")) and
            matches($locationcode, $NSLCSE("location_pattern")) and
            stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and              
            stationutil:check_radius($condition, $lat,$lon) and
            stationutil:check_restricted($condition,$stationrestrictedStatus)
(:            and ($channelcount>0):)
            and (count ($selected_channels)>0)
        group by $stationcode, $stationstartDate, $stationendDate, $stationrestrictedStatus
(:        order by $stationcode:)
        return 
                
                $station 
                
        }
    )
(:  TODO replace it again                  {$channelcount} :)
    where
        $Latitude  > $minlatitude and  
        $Latitude  < $maxlatitude and 
        $Longitude > $minlongitude and 
        $Longitude < $maxlongitude and
        matches($stationcode, $NSLCSE("station_pattern")) and
        matches($networkcode, $NSLCSE("network_pattern")) and
        matches($channelcode, $NSLCSE("channel_pattern")) and
        matches($locationcode, $NSLCSE("location_pattern")) and     
(:        stationutil:check_radius($condition, $lat,$lon) and TODO FIXME :)
        stationutil:check_restricted($condition,$restrictedStatus) and          
        stationutil:check_restricted($condition,$stationrestrictedStatus) and  
        stationutil:check_restricted($condition,$channelrestrictedStatus) and
        stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) 
        and 
        (count($stations)>0)
        group by $networkcode,  $startDate, $endDate, $restrictedStatus, $Description, $network_ingv_identifier
        order by $networkcode
(:
 : 
        {$networkcode}
        {$startDate} 
        {$endDate}
        {$restrictedStatus}
        {$Description}    
        {$identifier}
        {$network_ingv_identifier}
:)

(: TODO  try to use:      {$network/@*} :)
(:      
(:        {$network/@*[not(name()=("code","startDate","endDate","restrictedStatus"))]}    
         {$network/*[not(name() = ("Station", "TotalNumberStations", "SelectedNumberStations")) ]}
{$network/*[name() = "Identifier" ]}
 :  : :)
:)
(:{$network_ingv_identifier}:)
(:{functx:distinct-deep($identifier)}:)
    return
        
        <Network>
        {$networkcode}
        {$startDate} 
        {$endDate}
        {$restrictedStatus}
        {$Description}
        {functx:distinct-deep($identifier)}
        {$network_ingv_identifier}
        {functx:distinct-deep($network/*[not(name() = ("Identifier","Station", "TotalNumberStations", "SelectedNumberStations", "Description", "ingv:Identifier")) ])}

        <TotalNumberStations> {stationutil:stationcount($networkcode)} </TotalNumberStations>
        <SelectedNumberStations> {count($stations)} </SelectedNumberStations>
        {    
(:            if ($level!="network") then:)
              
(:  Sort before output, do not care of order of stations before (was hard to get it right)    :)
(:                fn:sort($stations,(), function($Station) {$Station/@code}):)
(:                for $s in $stations:)
(:                order by $s/@code :)
(:                return $s:)
              
                
                if ($level="station") then 
                    ( 
                        functx:remove-elements-deep($stations,("Channel","TotalNumberChannels","SelectedNumberChannels"))
                    )
                else  
                    ( 
                        functx:remove-elements-deep($stations,"Station")
                )

                        
        }
        </Network>

    
(:}:)
(:    catch err:* {()}:)
    
}; 
declare function stationutil:query_core($NSLCSE as map()*, $level as xs:string){
(:DEBUG:)
(:try{:)
let $dummy := util:log("info", "query_core" )


(:let $d:=if (stationutil:check_channels($NSLCSE)) then util:log("info", "Channels ok " ) else util:log("info", "No channels"  ):)
(:return:)
(:( :)
(:if (stationutil:check_channels($NSLCSE)) then :)
(:DEBUG:)
(:Prepare the output, discarding it only when sure no channels meet criteria avoid to check before, then create output:)
(:let $xml := :)

(:    DONE updatedafter ( :)
    let $since:= xs:dateTime($NSLCSE("updatedafter"))
(:    TODO RIMETTERE A POSTO:)
(:    for $network in collection("/db/apps/fdsn-station/Station/")//Network  :)
(: TODO (($NSLCSE("endtime") >= $CreationDate)  and  ($NSLCSE("starttime") <= $TerminationDate)) in path 
        (($CreationDate < $NSLCSE("startbefore"))) and
        (($CreationDate > $NSLCSE("startafter"))) and
        (($NSLCSE("endbefore")=$stationutil:defaults("future_time_as_datetime")) or ($TerminationDate < $NSLCSE("endbefore")) ) and
        (($NSLCSE("endafter")=$stationutil:defaults("past_time_as_datetime"))  or ($TerminationDate > $NSLCSE("endafter"))) :)
(: for $network in xmldb:find-last-modified-since(collection("/db/apps/fdsn-station/Station/")//Network/Station[@code=$NSLCSE("station")]/.. ,$since) , 
 : 
xs:decimal($condition("maxlongitude")
 : :)
    for $network in xmldb:find-last-modified-since(collection("/db/apps/fdsn-station/Station/")//Network[matches(@code, $NSLCSE("network_pattern"))]/Station[matches(@code, $NSLCSE("station_pattern"))][xs:decimal(Latitude) > xs:decimal($NSLCSE("minlatitude"))][xs:decimal(Latitude) < xs:decimal($NSLCSE("maxlatitude"))][xs:decimal(Longitude) > xs:decimal($NSLCSE("minlongitude"))][xs:decimal(Longitude) < xs:decimal($NSLCSE("maxlongitude"))]/Channel[matches(@code, $NSLCSE("channel_pattern"))][matches(@locationCode, $NSLCSE("location_pattern"))][xs:dateTime(@startDate) <= $NSLCSE("endtime")][if (empty(@endDate)) then true() else xs:dateTime(@endDate) >= $NSLCSE("starttime")][xs:dateTime(@startDate) < $NSLCSE("startbefore")][xs:dateTime(@startDate) > $NSLCSE("startafter")]/../.. ,$since) , $condition in $NSLCSE
(:    OK
 : 
for $network in xmldb:find-last-modified-since(collection("/db/apps/fdsn-station/Station/")//Network[matches(@code, $NSLCSE("network_pattern"))]/Station[matches(@code, $NSLCSE("station_pattern"))]/Channel[matches(@code, $NSLCSE("channel_pattern"))][matches(@locationCode, $NSLCSE("location_pattern"))]/../.. ,$since) , $condition in $NSLCSE
 :)
    
(:    for $network in xmldb:find-last-modified-since(collection("/db/apps/fdsn-station/Station/")//Network ,$since) , $condition in $NSLCSE  :)
(:    for $network in collection("/db/apps/fdsn-station/Station/")//Network[@code=$NSLCSE("network")] :)
(:    let $condition := $NSLCSE  :)
    let $minlatitude := xs:decimal($condition("minlatitude"))
    let $maxlatitude := xs:decimal($condition("maxlatitude"))
    let $minlongitude := xs:decimal($condition("minlongitude"))
    let $maxlongitude := xs:decimal($condition("maxlongitude"))

    let $Latitude:= $network/Station/Latitude
    let $Longitude:= $network/Station/Longitude
    let $CreationDate:= $network//Channel/@startDate
(:    let $TerminationDate:= $network//Channel/@endDate:)
    let $TerminationDate:= if (empty($network//Channel/@endDate)) then $stationutil:defaults("future_time_as_datetime")  else $network//Channel/@endDate
    
    let $networkcode := $network/@code
    let $station:=$network//Station
    let $stationcode:=$station/@code
    let $lat := $station/Latitude
    let $lon := $station/Longitude    
    let $channel:=$station/Channel
    let $channelcode:=$channel/@code
    let $locationcode:=$channel/@locationCode
    let $CreationDate:= $channel/@startDate
    let $TerminationDate:= $channel/@endDate   
    (:TODO use $startDate,  $endDate?:)
    let $startDate := $network/@startDate
    let $endDate := $network/@endDate
    let $restrictedStatus:=$network/@restrictedStatus
    let $stationrestrictedStatus:=$network/Station/@restrictedStatus    
    let $channelrestrictedStatus:=$network//Channel/@restrictedStatus    
    let $Description := $network/Description
    let $identifier := $network/Identifier
    let $network_ingv_identifier := $network/ingv:Identifier
(:    let $log := util:log("info", "networks: "):)
    let $stations:=
    (
        unordered { 
        for $station in $network/Station
            let $stationcode:=$station/@code
            let $stationstartDate := $station/@startDate
            let $stationendDate := $station/@endDate
            let $stationrestrictedStatus := $station/@restrictedStatus
            let $channels:=$station//Channel
            let $channelcode:=$channel/@code
            let $locationcode := $channel/@locationCode          
            let $Latitude:=  xs:decimal($station/Latitude)
            let $Longitude:= xs:decimal($station/Longitude) 
            let $lat := $station/Latitude
            let $lon := $station/Longitude
            let $CreationDate:= $channel/@startDate
            let $TerminationDate := $channel/@endDate
(:            let $log := util:log("info", "stations: "):)
            let $selected_channels:= (
                for $channel in $channels
                let $channelcode:=$channel/@code
                let $locationcode:=$channel/@locationCode
                let $channelrestrictedStatus := $channel/@restrictedStatus                                           
                let $CreationDate:= $channel/@startDate
                let $TerminationDate:= $channel/@endDate
(:                let $log := util:log("info", "channels: "):)
                where
(:                    matches($stationcode, $NSLCSE("station_pattern")) and:)
(:                    matches($networkcode, $NSLCSE("network_pattern")) and:)
(:                    matches($channelcode, $NSLCSE("channel_pattern")) and:)
(:                    matches($locationcode, $NSLCSE("location_pattern")) and:)
                    stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and            
                    stationutil:check_radius($condition, $lat,$lon) and                    
                    stationutil:check_restricted($condition,$channelrestrictedStatus) 
                return 
                         $channel 

            )
(:            let $channelcount:=count ($selected_channels):)
        where 
(:            $Latitude  > $minlatitude and  :)
(:            $Latitude  < $maxlatitude and :)
(:            $Longitude > $minlongitude and :)
(:            $Longitude < $maxlongitude and:)
(:            matches($stationcode, $NSLCSE("station_pattern")) and:)
(:            matches($networkcode, $NSLCSE("network_pattern")) and:)
(:            matches($channelcode, $NSLCSE("channel_pattern")) and:)
(:            matches($locationcode, $NSLCSE("location_pattern")) and:)
            stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and              
            stationutil:check_radius($condition, $lat,$lon) and
            stationutil:check_restricted($condition,$stationrestrictedStatus)
(:            and ($channelcount>0):)
            and (count ($selected_channels)>0)
        group by $stationcode, $stationstartDate, $stationendDate, $stationrestrictedStatus
(:        order by $stationcode:)
        return 
                <Station>
                {$stationcode}  
                </Station>
        }    
    )
(:  TODO replace it again                  {$channelcount} :)
    where
(:        $Latitude  > $minlatitude and  :)
(:        $Latitude  < $maxlatitude and :)
(:        $Longitude > $minlongitude and :)
(:        $Longitude < $maxlongitude and:)
(:        matches($stationcode, $NSLCSE("station_pattern")) and:)
(:        matches($networkcode, $NSLCSE("network_pattern")) and:)
(:        matches($channelcode, $NSLCSE("channel_pattern")) and:)
(:        matches($locationcode, $NSLCSE("location_pattern")) and     :)
(:        stationutil:check_radius($condition, $lat,$lon) and TODO FIXME :)
        stationutil:check_restricted($condition,$restrictedStatus) and          
        stationutil:check_restricted($condition,$stationrestrictedStatus) and  
        stationutil:check_restricted($condition,$channelrestrictedStatus) and
        stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) 
        and 
        (count($stations)>0)
        group by $networkcode,  $startDate, $endDate, $restrictedStatus, $Description, $network_ingv_identifier
        order by $networkcode
(:
 : 
        {$networkcode}
        {$startDate} 
        {$endDate}
        {$restrictedStatus}
        {$Description}    
        {$identifier}
        {$network_ingv_identifier}
:)

(: TODO  try to use:      {$network/@*} :)
(:      
    {$network/@*}    
(:        {$network/@*[not(name()=("code","startDate","endDate","restrictedStatus"))]}    
         {$network/*[not(name() = ("Station", "TotalNumberStations", "SelectedNumberStations")) ]}
{$network/*[name() = "Identifier" ]}
 :  : :)
:)
(:{$network_ingv_identifier}:)
(:{functx:distinct-deep($identifier)}:)
    return
        
        <Network>
        {$networkcode}
        {$startDate} 
        {$endDate}
        {$restrictedStatus}
        {$Description}
        {functx:distinct-deep($identifier)}
        {functx:distinct-deep($network/*[not(name() = ("Identifier","Station", "TotalNumberStations", "SelectedNumberStations", "Description", "ingv:Identifier")) ])}
        {$network_ingv_identifier}
        <TotalNumberStations> {stationutil:stationcount($networkcode)} </TotalNumberStations>
        <SelectedNumberStations> {count($stations)} </SelectedNumberStations>
        {    
            if ($level!="network") then
(:  Sort before output, do not care of order of stations before (was hard to get it right)    :)
(:                fn:sort($stations,(), function($Station) {$Station/@code}):)
(:                for $s in $stations:)
(:                order by $s/@code:)
(:                return $s :)
(:TODO                $stations:)
            for $station in $network/Station
            let $stationcode:=$station/@code
            let $stationstartDate := $station/@startDate
            let $stationendDate := $station/@endDate
            let $stationrestrictedStatus := $station/@restrictedStatus
            let $channels:=$station//Channel
            let $channelcode:=$channel/@code
            let $locationcode := $channel/@locationCode          
(:            let $Latitude:=  xs:decimal($station/Latitude):)
(:            let $Longitude:= xs:decimal($station/Longitude) :)
            let $lat := $station/Latitude
            let $lon := $station/Longitude
            let $CreationDate:= $channel/@startDate
            let $TerminationDate := $channel/@endDate
(:            let $log := util:log("info", "stations: "):)
            let $selected_channels:= (
                for $channel in $channels
                let $channelcode:=$channel/@code
                let $locationcode:=$channel/@locationCode
                let $channelrestrictedStatus := $channel/@restrictedStatus                                           
                let $CreationDate:= $channel/@startDate
                let $TerminationDate:= $channel/@endDate
(:                let $log := util:log("info", "channels: "):)
                where
(:                    matches($stationcode, $NSLCSE("station_pattern")) and:)
(:                    matches($networkcode, $NSLCSE("network_pattern")) and:)
                    matches($channelcode, $NSLCSE("channel_pattern")) and
                    matches($locationcode, $NSLCSE("location_pattern")) and
                    stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and            
                    stationutil:check_radius($condition, $lat,$lon) and                    
                    stationutil:check_restricted($condition,$channelrestrictedStatus) 
                return 
                     if ($level="channel") then ( 
                         stationutil:remove-elements($channel,"Stage")
                         )
                     else
                         $channel 

            )
(:            let $channelcount:=count ($selected_channels):)
        where 
(:            $Latitude  > $minlatitude and  :)
(:            $Latitude  < $maxlatitude and :)
(:            $Longitude > $minlongitude and :)
(:            $Longitude < $maxlongitude and:)
(:            matches($stationcode, $NSLCSE("station_pattern")) and:)
(:            matches($networkcode, $NSLCSE("network_pattern")) and:)
            matches($channelcode, $NSLCSE("channel_pattern")) and
            matches($locationcode, $NSLCSE("location_pattern")) and
            stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and              
            stationutil:check_radius($condition, $lat,$lon) and
            stationutil:check_restricted($condition,$stationrestrictedStatus)
(:            and ($channelcount>0):)
            and (count ($selected_channels)>0)
        group by $stationcode, $stationstartDate, $stationendDate, $stationrestrictedStatus
        order by $stationcode
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
                {$station/TerminationDate}
                {    
                if ($level="response" or $level="channel") then
                    (
                    <TotalNumberChannels>
                    {count($station/Channel)}
                    </TotalNumberChannels>,
                    <SelectedNumberChannels>
                    {count ($selected_channels)}
                    </SelectedNumberChannels>,
                    $selected_channels
                    )
                else 
                    ()
                }
                </Station>
                
                
            else    
                ()
        }
        </Network>

    
(:}:)
(:    catch err:* {()}:)
    
}; 


(:~ 
 : @return the <network> Station XML fragment given the $NSLCSE map of query parameters, found in the current collection.
 : Works for POST
 : 
 :)
(: TODO rewrite looking at query_core:)
declare function stationutil:query_core_POST($NSLCSE as map()*, $level as xs:string){
try{    
(:DEBUG:)
let $dummy := util:log("info", "query_core_POST" )
(:DEBUG:)
(:let $xml := :)
(:    DONE updatedafter is a unique parameter value:)
    let $since := $NSLCSE[1]("updatedafter")
    for $network in (xmldb:find-last-modified-since(collection("/db/apps/fdsn-station/Station/")//Network ,$since) ), $condition in $NSLCSE  
    let $minlatitude := xs:decimal($condition("minlatitude"))
    let $maxlatitude := xs:decimal($condition("maxlatitude"))
    let $minlongitude := xs:decimal($condition("minlongitude"))
    let $maxlongitude := xs:decimal($condition("maxlongitude"))

    let $Latitude:= $network/Station/Latitude
    let $Longitude:= $network/Station/Longitude
    let $CreationDate:= $network/Station/Channel/@startDate
(:    let $TerminationDate:= $network/Station/Channel/@endDate:)
    let $TerminationDate:= if ($network/Station/Channel/@endDate) then $network/Station/Channel/@endDate else $stationutil:defaults("future_time_as_datetime") 
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
    let $identifier := $network/Identifier
    let $network_ingv_identifier := $network/ingv:Identifier

    let $stations:=(
        for $station in $network/Station
            let $stationcode:=$station/@code
            let $stationstartDate := $station/@startDate
            let $stationendDate := $station/@endDate
            let $stationrestrictedStatus := $station/@restrictedStatus
            let $channels:=$station//Channel
            let $channelcode:=$channel/@code
            let $locationcode := $channel/@locationCode          
            let $Latitude:=  xs:decimal($station/Latitude)
            let $Longitude:= xs:decimal($station/Longitude) 
            let $lat := $station/Latitude
            let $lon := $station/Longitude
            let $CreationDate:= $channel/@startDate
            let $TerminationDate := $channel/@endDate
            let $log := util:log("info", "stations: ")
            let $selected_channels:= 
                for $channel in $channels
                let $channelcode:=$channel/@code
                let $locationcode:=$channel/@locationCode
                let $channelrestrictedStatus := $channel/@restrictedStatus                                           
                let $CreationDate:= $channel/@startDate
                let $TerminationDate:= $channel/@endDate
(:                let $log := util:log("info", $networkcode || " " || $stationcode || " " || " " || $channelcode || " " || $CreationDate):)
                where
                    stationutil:constraints_onchannel_patterns( $condition, $networkcode, $stationcode, $channelcode, $locationcode)  and 
                    stationutil:check_radius($condition, $lat,$lon) and                    
                    stationutil:check_restricted($condition,$channelrestrictedStatus) and 
                    stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) 
                    group by $channel
                return 
                     if ($level="channel") then ( 
                         stationutil:remove-elements($channel,"Stage")
                         )
                     else
                         $channel 
        where 
            $Latitude  > $minlatitude and  
            $Latitude  < $maxlatitude and 
            $Longitude > $minlongitude and 
            $Longitude < $maxlongitude and
            stationutil:constraints_onchannel_patterns( $condition, $networkcode, $stationcode, $channelcode, $locationcode)  and
            stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and              
            stationutil:check_radius($condition, $lat,$lon) and
            stationutil:check_restricted($condition,$stationrestrictedStatus)
(:            and ($channelcount>0):)
            and (count ($selected_channels)>0) 
        group by $stationcode, $stationstartDate, $stationendDate, $stationrestrictedStatus
        order by $stationcode
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
                {$station/TerminationDate}
                {    
                if ($level="channel" or $level="response") 
                then
                (
                    <TotalNumberChannels>  {count($station/Channel)} </TotalNumberChannels>,
                    <SelectedNumberChannels>   {count ($selected_channels)}  </SelectedNumberChannels>,
                    $selected_channels,
                    util:log("info", "Into selected channels" )
                )    
                else 
                    ()
                }
                </Station>
            )
    where
    (:        {functx:distinct-deep($identifier)}        :)
        $Latitude  > $minlatitude and  
        $Latitude  < $maxlatitude and 
        $Longitude > $minlongitude and 
        $Longitude < $maxlongitude and
        stationutil:check_radius($condition, $lat,$lon) and 
        stationutil:check_restricted($condition,$restrictedStatus) and          
        stationutil:check_restricted($condition,$stationrestrictedStatus) and  
        stationutil:check_restricted($condition,$channelrestrictedStatus) and
        stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and
        stationutil:constraints_onchannel_patterns( $condition, $networkcode, $stationcode, $channelcode, $locationcode) 
        and 
        (count($stations)>0)
        group by $networkcode,  $startDate, $endDate, $restrictedStatus, $Description, $network_ingv_identifier
(:        , $identifier:)
        order by $networkcode
        
    return
        
        <Network>
        {$networkcode}
        {$startDate} 
        {$endDate}
        {$restrictedStatus}
        {$Description}    
        {functx:distinct-deep($identifier)}
        {$network_ingv_identifier}
        <TotalNumberStations> {stationutil:stationcount($networkcode)} </TotalNumberStations>
        <SelectedNumberStations> {count(distinct-values($stations))} </SelectedNumberStations>
        {    
            if ($level!="network") then
        (:  Coming from many rows there could be duplicates , removing here before output    :)
            let $log:=util:log("info", "Level: " || $level) 
            let $distinct_sta := 
                for $sta in $stations
                    group by $stacode := $sta//Network/@code
                return
                    functx:distinct-deep($sta) 
            return 
                fn:sort($distinct_sta,(), function($distinct_sta) {$distinct_sta/@code})
            else    
                ()
        }
        </Network>

(:return     $xml:)

}
    catch err:* {()}
    
}; 



(:~
 :  @return the <network> Station XML fragment given the $NSLCSE map of query parameters, found in the current collection.
 :  Simplified to treat only the network and station parameter case, without other arguments
 : 
 : @param $NSLCSE 
 :) 
declare function stationutil:query_core_channel_response_shortcut($NSLCSE as map()*){
(:DEBUG:)
(:try{:)
let $dummy := util:log("info", "query_core_channel_response_shortcut" )
let $level := $NSLCSE("level") 

(:let $d:=if (stationutil:check_channels($NSLCSE)) then util:log("info", "Channels ok " ) else util:log("info", "No channels"  ):)
(:return:)
(:( :)
(:if (stationutil:check_channels($NSLCSE)) then :)
(:DEBUG:)
(:Prepare the output, discarding it only when sure no channels meet criteria avoid to check before, then create output:)
(:let $xml := :)
(: fn:sort( :)
(:    TODO updatedafter ( :)
let $since:= xs:dateTime($NSLCSE("updatedafter"))
for $network in xmldb:find-last-modified-since(collection("/db/apps/fdsn-station/Station/")//Network, $since)
(:    for $network in collection("/db/apps/fdsn-station/Station/")//Network:)
(:    , $condition in $NSLCSE  :)

(:    let $minlatitude := xs:decimal($condition("minlatitude")):)
(:    let $maxlatitude := xs:decimal($condition("maxlatitude")):)
(:    let $minlongitude := xs:decimal($condition("minlongitude")):)
(:    let $maxlongitude := xs:decimal($condition("maxlongitude")):)

(:    let $Latitude:= $network/Station/Latitude:)
(:    let $Longitude:= $network/Station/Longitude:)
(:    let $CreationDate:= $network//Channel/@startDate:)
(:    let $TerminationDate:= $network//Channel/@endDate:)
(:    let $TerminationDate:= if (empty($network//Channel/@endDate)) then $stationutil:defaults("future_time_as_datetime")  else $network//Channel/@endDate:)
    
    let $networkcode := $network/@code
    let $station:=$network//Station
    let $stationcode:=$station/@code
(:    let $lat := $station/Latitude:)
(:    let $lon := $station/Longitude    :)
(:    let $channel:=$station/Channel:)
(:    let $channelcode:=$channel/@code:)
(:    let $locationcode:=$channel/@locationCode:)
(:    let $CreationDate:= $channel/@startDate:)
(:    let $TerminationDate:= $channel/@endDate   :)
    (:TODO use $startDate,  $endDate?:)
    let $startDate := $network/@startDate
    let $endDate := $network/@endDate
    let $restrictedStatus:=$network/@restrictedStatus
    let $stationrestrictedStatus:=$network/Station/@restrictedStatus    
(:    let $channelrestrictedStatus:=$network//Channel/@restrictedStatus    :)
    let $Description := $network/Description
    let $identifier := $network/Identifier
    let $network_ingv_identifier := $network/ingv:Identifier
(:    let $log := util:log("info", "networks: "):)
    let $stations:=
    (
        for $station in $network/Station
            let $stationcode:=$station/@code
            let $stationstartDate := $station/@startDate
            let $stationendDate := $station/@endDate
            let $stationrestrictedStatus := $station/@restrictedStatus
            let $channels:=$station//Channel
(:            let $channelcode:=$channel/@code:)
(:            let $locationcode := $channel/@locationCode          :)
(:            let $Latitude:=  xs:decimal($station/Latitude):)
(:            let $Longitude:= xs:decimal($station/Longitude) :)
(:            let $lat := $station/Latitude:)
(:            let $lon := $station/Longitude:)
(:            let $CreationDate:= $channel/@startDate:)
(:            let $TerminationDate := $channel/@endDate:)
            
(:            let $log := util:log("info", "stations: "):)
            let $selected_channels:= (
                for $channel in $channels
(:                let $channelcode:=$channel/@code:)
(:                let $locationcode:=$channel/@locationCode:)
(:                let $channelrestrictedStatus := $channel/@restrictedStatus                                           :)
(:                let $CreationDate:= $channel/@startDate:)
(:                let $TerminationDate:= $channel/@endDate:)
(:                let $log := util:log("info", "channels: "):)
                where
                    matches($stationcode, $NSLCSE("station_pattern")) and
                    matches($networkcode, $NSLCSE("network_pattern")) 
(:                    and:)
(:                    matches($channelcode, $NSLCSE("channel_pattern")) and:)
(:                    matches($locationcode, $NSLCSE("location_pattern")) and:)
(:                    stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and            :)
(:                    stationutil:check_radius($condition, $lat,$lon) and                    :)
(:                    stationutil:check_restricted($condition,$channelrestrictedStatus) :)
                return 
                         $channel 
            )
(:            let $channelcount:=count ($selected_channels):)
        where 
(:            $Latitude  > $minlatitude and  :)
(:            $Latitude  < $maxlatitude and :)
(:            $Longitude > $minlongitude and :)
(:            $Longitude < $maxlongitude and:)
            matches($stationcode, $NSLCSE("station_pattern")) and
            matches($networkcode, $NSLCSE("network_pattern")) 
(:            and:)
(:            matches($channelcode, $NSLCSE("channel_pattern")) and:)
(:            matches($locationcode, $NSLCSE("location_pattern")) and:)
(:            stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and              :)
(:            stationutil:check_radius($condition, $lat,$lon) and:)
(:            stationutil:check_restricted($condition,$stationrestrictedStatus):)
(:            and ($channelcount>0):)
            and (count ($selected_channels)>0)
(:  FIX ODC problem with identifier in dataset FIXME          :)
(:        group by $networkcode,  $startDate, $endDate, $restrictedStatus, $Description, $network_ingv_identifier, $identifier:)
        group by $stationcode, $stationstartDate, $stationendDate, $stationrestrictedStatus
        order by $stationcode
        return 
                
                <Station>
                {$stationcode}  
                </Station>
            
    )

(:  TODO replace it again                  {$channelcount} :)
    where
(:        $Latitude  > $minlatitude and  :)
(:        $Latitude  < $maxlatitude and :)
(:        $Longitude > $minlongitude and :)
(:        $Longitude < $maxlongitude and:)
        matches($stationcode, $NSLCSE("station_pattern")) and
        matches($networkcode, $NSLCSE("network_pattern")) 
(:        and:)
(:        matches($channelcode, $NSLCSE("channel_pattern")) and:)
(:        matches($locationcode, $NSLCSE("location_pattern")) and     :)
(:        stationutil:check_radius($condition, $lat,$lon) and :)
(:        stationutil:check_restricted($condition,$restrictedStatus) and          :)
(:        stationutil:check_restricted($condition,$stationrestrictedStatus) and  :)
(:        stationutil:check_restricted($condition,$channelrestrictedStatus) and:)
(:        stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) :)
        and 
        (count($stations)>0)
(: INVALID FIX       group by $networkcode,  $startDate, $restrictedStatus , $endDate, $Description:)
        group by $networkcode,  $startDate, $endDate, $restrictedStatus, $Description, $network_ingv_identifier
(:        , $identifier:)
(:        , $endDate, $restrictedStatus, $Description,  $identifier $ingvidentifier:)
        
        order by $networkcode
    return
        
        <Network>
        {$networkcode}
        {$startDate} 
        {$endDate}
        {$restrictedStatus}
        {$Description}    
        {functx:distinct-deep($identifier)}
        {$network_ingv_identifier}
        
        <TotalNumberStations> {stationutil:stationcount($networkcode)} </TotalNumberStations>
        <SelectedNumberStations> {count($stations)} </SelectedNumberStations>
        {    
            if ($level!="network") then
(:                fn:sort($stations,(), function($Station) {$Station/@code}):)
(:            for $s in $stations:)
(:              order by $s/@code:)
(:                return $s :)
(:  TODO          $stations:)
         for $station in $network/Station
            let $stationcode:=$station/@code
            let $stationstartDate := $station/@startDate
            let $stationendDate := $station/@endDate
            let $stationrestrictedStatus := $station/@restrictedStatus
            let $channels:=$station//Channel
            
(:            let $channelcode:=$channel/@code:)
(:            let $locationcode := $channel/@locationCode          :)
(:            let $Latitude:=  xs:decimal($station/Latitude):)
(:            let $Longitude:= xs:decimal($station/Longitude) :)
(:            let $lat := $station/Latitude:)
(:            let $lon := $station/Longitude:)
(:            let $CreationDate:= $channel/@startDate:)
(:            let $TerminationDate := $channel/@endDate:)
            
(:            let $log := util:log("info", "stations: "):)
            let $selected_channels:= (
                for $channel in $channels
(:                let $channelcode:=$channel/@code:)
(:                let $locationcode:=$channel/@locationCode:)
(:                let $channelrestrictedStatus := $channel/@restrictedStatus                                           :)
(:                let $CreationDate:= $channel/@startDate:)
(:                let $TerminationDate:= $channel/@endDate:)
(:                let $log := util:log("info", "channels: "):)
                where
                    matches($stationcode, $NSLCSE("station_pattern")) and
                    matches($networkcode, $NSLCSE("network_pattern")) 
(:                    and:)
(:                    matches($channelcode, $NSLCSE("channel_pattern")) and:)
(:                    matches($locationcode, $NSLCSE("location_pattern")) and:)
(:                    stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and            :)
(:                    stationutil:check_radius($condition, $lat,$lon) and                    :)
(:                    stationutil:check_restricted($condition,$channelrestrictedStatus) :)
                return 
                     if ($level="channel") then ( 
                         stationutil:remove-elements($channel,"Stage")
                         )
                     else
                         $channel 
            )
(:            let $channelcount:=count ($selected_channels):)
        where 
(:            $Latitude  > $minlatitude and  :)
(:            $Latitude  < $maxlatitude and :)
(:            $Longitude > $minlongitude and :)
(:            $Longitude < $maxlongitude and:)
            matches($stationcode, $NSLCSE("station_pattern")) and
            matches($networkcode, $NSLCSE("network_pattern")) 
(:            and:)
(:            matches($channelcode, $NSLCSE("channel_pattern")) and:)
(:            matches($locationcode, $NSLCSE("location_pattern")) and:)
(:            stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and              :)
(:            stationutil:check_radius($condition, $lat,$lon) and:)
(:            stationutil:check_restricted($condition,$stationrestrictedStatus):)
(:            and ($channelcount>0):)
            and (count ($selected_channels)>0)
        group by $stationcode, $stationstartDate, $stationendDate, $stationrestrictedStatus
        order by $stationcode
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
                {$station/TerminationDate}
                {    
                if ($level="response" or $level="channel") then
                    (
                    <TotalNumberChannels>
                    {count($station/Channel)}
                    </TotalNumberChannels>,
                    <SelectedNumberChannels>
                    {count ($selected_channels)}
                    </SelectedNumberChannels>,
                    $selected_channels
                    )
                else 
                    ()
                }
                </Station>
            else    
                ()
        }
        </Network>


(:}:)
(:    catch err:* {()}:)
    
}; 


