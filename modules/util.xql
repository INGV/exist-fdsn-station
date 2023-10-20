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

declare %public variable $stationutil:data_collection as xs:string := "/db/apps/fdsn-station-data";
declare %public variable $stationutil:netcache_collection as xs:string := $stationutil:data_collection||"/NetCache/";
declare %public variable $stationutil:station_collection as xs:string := $stationutil:data_collection||"/Station/";
declare %public variable $stationutil:station_pruned_collection as xs:string := $stationutil:data_collection||"/StationPruned/";

(:Reading from JSON file declares the map :)
(: declare %public variable $stationutil:settings := map {:)
(:    "enable_log": true(),                               :)
(:    "enable_debug": false(),                            :)
(:    "enable_query_log": false(),                        :)
(:    "post_limit_rows": 1000,                            :)
(:    "translate_units": true(),                          :)
(:    "remove_tz": true()                                 :)
(: };                                                     :)
declare %public variable $stationutil:settings := json-doc("/db/apps/fdsn-station/config/settings.json");

(:~ Default values, from fdsn standard or for convenience :)
declare %public variable $stationutil:defaults as map()* := map {
    "nodata"             : "204",
    "level"              : "station",
    "latitude"           : "0",
    "longitude"          : "0",
    "minradius"          : "0",
    "maxradius"          : "180",
    "minradiuskm"        : "0",
    "maxradiuskm"        : "20037.5",
    "includerestricted"  : "true",
    "format"             : "xml",
    "minlatitude"        : -90.0,
    "maxlatitude"        :  90.0,
    "minlongitude"       : -180,
    "maxlongitude"       :  180,
    "startbefore"        : "10001-01-01T00:00:00",
    "startafter"         : "0001-01-01T00:00:00",
    "endbefore"          : "10001-01-01T00:00:00",
    "endafter"           : "0001-01-01T00:00:00",
    "starttime"          : "0001-01-01T00:00:00",
    "endtime"            : "10001-01-01T00:00:00",
    "updatedafter"       : "0001-01-01T00:00:00",
    "includeavailability": "false",
    "matchtimeseries"    : "false",
    "past_time"          : "0001-01-01T00:00:00",
    "future_time"        : "10001-01-01T00:00:00",
    "asofdate"           : "10001-01-01T00:00:00",
    "past_time_as_datetime"   :  xs:dateTime("0001-01-01T00:00:00"),
    "future_time_as_datetime" :  xs:dateTime("10001-01-01T00:00:00"),
    "network_sequence" : ()
};


(:Common constans  :)
declare %public variable $stationutil:postdata as xs:string* := if (request:get-method() eq "POST") then stationutil:setpostdata() else "";
declare %public variable $stationutil:parameters as map() := if (request:get-method() eq "POST")  then stationutil:set_parameters_row_from_POST()  else stationutil:set_parameters_row_from_GET();
declare %public variable $stationutil:parameters_table as map()* := if (request:get-method() eq "POST")  then stationutil:set_parameters_table_from_POST()  else stationutil:set_parameters_row_from_GET();
declare %public variable $stationutil:unknown_parameters as xs:string* := if (request:get-method() eq "POST")  then stationutil:unknown_parameter_from_POST()  else stationutil:unknown_parameter_from_GET();

(:POST-specific constants :)
declare %public variable $stationutil:alternate_networks as xs:string:=if (request:get-method() eq "POST")  then stationutil:set_alternate_network_POST()  else ();
declare %public variable $stationutil:networks_pattern as xs:string:=if (request:get-method() eq "POST")  then stationutil:set_network_pattern_POST()  else ();
declare %public variable $stationutil:stations_pattern as xs:string:=if (request:get-method() eq "POST")  then stationutil:set_station_pattern_POST()  else ();
declare %public variable $stationutil:channels_pattern as xs:string:=if (request:get-method() eq "POST")  then stationutil:set_channel_pattern_POST()  else ();
declare %public variable $stationutil:starttimes as xs:dateTime* :=if (request:get-method() eq "POST")  then stationutil:set_starttime_POST()  else ();
declare %public variable $stationutil:endtimes as xs:dateTime* :=if (request:get-method() eq "POST")  then stationutil:set_endtime_POST()  else ();

(: Functions declarations  :)

(:~ @return the current module version:)
declare function stationutil:version() as xs:string
{
    "1.1.55"
};

(:~ Output debug messages :)
declare function stationutil:debug($level as xs:string, $messages as xs:string*)
{
    if ($stationutil:settings("enable_debug")) then
        for $i in $messages
        let $logline := util:log($level, $i)
        return ()
    else
        for $i in $messages
        let $logline := ""
        return ()
};

(:~ Output log messages:)
declare function stationutil:log($level as xs:string, $messages as xs:string*)
{
    if ($stationutil:settings("enable_log")) then
        for $i in $messages
        let $logline := util:log($level, $i)
        return ()
    else
        ()
};

(:~ @return the list of forwarded-host or the remote-addr if not available
 :
 : :)
declare function stationutil:get_caller() as xs:string
{
    if (request:get-header("X-Forwarded-For")) then request:get-header("X-Forwarded-For") else request:get-remote-addr()
};

(:~ @return the total number of stations of the network with code @param, use cached info in NetCache collection
 : @param $net the net code
 : @param $startDate
 :
 : :)
declare function stationutil:stationcount($net as xs:string *, $startDate as xs:dateTime *, $endDate as xs:dateTime *, $restrictedStatus as xs:string *) as item()*
{
  collection($stationutil:netcache_collection)//Network[@code=$net][@startDate=$startDate][empty(@restrictedstatus) or @restrictedStatus=$restrictedStatus][empty(@endDate) or @endDate=$endDate]/TotalNumberStations/text()
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
   try {
   let $tokens := tokenize(stationutil:sanitize($input), "[,\s]+")
(: split input by commas in tokens, check lenght of every token max two chars, chars can be alphanum and ? or * :)
(:  return a pattern for regex, for exact match include the pattern as in ^pattern$ :)
(: IF there is more than a token and one matches "_" ignore "_"   TODO if only a token
 : IF there is no token without "_" network #
 : IF there is mixed tokens concatenate only the regular ones
 :
 : :)

   let $count_regularnet:= sum(
       for $token in $tokens return
           if (fn:starts-with($token,"_")) then
               let $ret:=0
               return $ret
           else
               let $ret:=1
               return $ret
         )


(:   let $log := util:log("info", "regular network parameter count: " ||  $count_regularnet ):)

   return
if (not(empty($tokens))) then
       if ($count_regularnet>0) then

        "("||
        string-join(
            for $token in $tokens
            return
                if (fn:starts-with($token,"_")) then (: Manage AlternateNetwork code :)
                    let $pattern := ()
                    return $pattern
                else if (string-length($token)<=2)
                then
                    let $pattern:= replace( $token, "\*", ".*")
                    let $pattern:= "^"||translate( $pattern, "?", ".")||"$"
                    return $pattern
                else if (string-length($token)=1 and $token="*" ) then
                    let $pattern:= ".*"
                    return "^"||$pattern||"$"

                else
                    let $pattern:="#"
                    return $pattern
        , "|")
        || ")"
        else
            let $pattern:="VIRTUAL"
            return $pattern
    else "#"
   }
 catch err:* {
     let $dummy := util:log("error", "network pattern" ||  $input )
     return "#"}


};


(:~
 : Translate the network parameter in sequence of netcodes
 :
 : @param $input the network code parameter
 :
 :)
declare function stationutil:network_pattern_to_sequence ($input as xs:string) as item() *
{
(:TODO use stationutil:network_pattern_translate:)
   let $pattern :=
   try {
   stationutil:network_pattern_translate($input)
   }
 catch err:* {util:log("error", "network pattern to sequence" ||  $input )}

  let $docavailable:=doc-available($stationutil:netcache_collection||"/net.xml")


  let $netseq:=
    if ($docavailable)
        then
        (
            let $values:=distinct-values(collection($stationutil:netcache_collection)//Network[matches(@code,$pattern)]/@code)
            return
                if (empty($values)) then "#"
                else $values
        )
        else ()


  return $netseq

};

(:~
 : Translate the alternate network parameter in xql pattern for matches function
 :
 : @param $input the alternate network code parameter
 :
 :)
declare function stationutil:alternate_network_pattern_translate ($input as xs:string) as xs:string
{
   try {
   let $tokens := tokenize(stationutil:sanitize($input), "[,\s]+")

(: split input by commas in tokens, check lenght of every token two chars, chars can be alphanum and ? or * :)
(:  return a pattern for regex, for exact match include the pattern as in ^pattern$ :)
(:  return FSDN when is a regular FSDN two characters network  :)

   return

       "("||string-join(
   for $token in $tokens

   return
        if (fn:starts-with($token,"_")) then (: Manage AlternateNetwork code :)
                let $pattern := "^"||$token||"$"
                return $pattern
        else
              let $pattern:= "FSDN"
              return $pattern


    , "|") || ")"
   }
 catch err:* {"#"}

};




(: Modified the function to use range:matches in path expressions
 : Do not use range:matches in where clause:)
declare function stationutil:station_pattern_translate($input as xs:string)
as xs:string
{
    (: let $tokens := tokenize(stationutil:sanitize($input), "[,\s]+") :) (: split input by commas in tokens, check
                                                                           : lenght of every token 3-5 chars, chars can
                                                                           : be alphanum and ? or * :)
    let $input_string:= string-join($input, ",")
    let $tokens := tokenize($input_string, ",")
    return
        if (not(empty($tokens))) then
            "(" || string-join(for $token in $tokens
                               return
                                   if (string-length($token) < 6) then
                                       let $pattern := replace($token, "\*", ".*")
                                       let $pattern := translate($pattern, "?", ".?")
                                       (: * -> 0 or more characters, ? exactly one character :) return $pattern
                                   else
                                       let $pattern := "#"
                                       return $pattern
                               ,
                               "|") || ")"
        else
            "#"
};





(:~ Translate the channel parameter in xql pattern for matches function
 :
 : @param $input the channel code parameter
 :
 :)
declare function stationutil:channel_pattern_translate($input as item ()*)
as xs:string
{

    let $input_string := string-join($input, ",")
    let $tokens := tokenize($input_string, ",")

    (: split input by commas in tokens, check lenght of every token 3-5 chars, chars can be alphanum and ? or * :)
        return
        if (not(empty($tokens))) then
            "(" || string-join(for $token in $tokens
                               return
                                   if (string-length($token) < 4 and string-length($token) > 0) then
                                       let $pattern := replace($token, "\*", ".*")
                                       let $pattern := translate($pattern, "?", ".")
                                       (: every character will remain the same, only * and ? become . () :)
                                       return "^" || $pattern || "$"
                                   else
                                       let $pattern := "#"
                                       return $pattern
                               ,
                               "|") || ")"
        else
            "#"
};




(:~ Translate the location parameter in xql pattern for matches function
 :
 : @param $input the location code parameter
 :
 :)
declare function stationutil:location_pattern_translate($input as item ()*)
as xs:string
{
    let $input_string := string-join($input, ",")
    let $tokens := tokenize($input_string, ",")
    (: split input by commas in tokens, check lenght of every token 3-5 chars, chars can be alphanum and ? or * :)
        return
        if (not(empty($tokens))) then
            "(" || string-join(for $token in $tokens
                               return (: ".*" :)
                                   if (string-length($token) < 3) then
                                       let $pattern := replace($token, "\*", ".*")
                                       let $pattern := translate($pattern, "?", ".")
                                       let $pattern := if ($pattern = "") then "^$" else $pattern
                                       let $pattern := if ($pattern = "--") then "^$" else $pattern
                                       (: every character will remain the same, only * and ? changes, no location can
                                        : still be one character :)
                                        return
                                           if (string-length($pattern) < 2) then
                                               "#"
                                           else
                                               "^" || $pattern || "$"
                                   else
                                       let $pattern := "#"
                                       return $pattern
                               ,
                               "|") || ")"
        else
            "#"
};






(:~
 :  Adjust datetime strings to fdsn standard format YYYY-MM-DDThh:mm:ss.d if possible
 :)
declare function stationutil:time_adjust( $mydatetime as xs:string ) as xs:string {


    if ((matches($mydatetime,"..-..-..T..:..:..*"))) then
        $mydatetime
    else
        if (matches($mydatetime,"..-..-..")) then
            $mydatetime||"T"||"00:00:00.0"
        else
            ""
};



declare function stationutil:constraints_onchannel(
    $parameters as map()*,
    $CreationDate as xs:dateTime*,
    $TerminationDate as xs:dateTime* ) as xs:boolean
    {
    try {

    let $ctd:=count($CreationDate)
    let $ttd:=count($TerminationDate)
    let $add:=$ctd - $ttd

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
(:    let $d:=util:log("info", "constraints_onchannel " ):)
    let $ctd:=count($CreationDate)
    let $ttd:=count($TerminationDate)
    let $add:=$ctd - $ttd

    let $tdd := (
        for $t in $TerminationDate
        return $t ,
        for $n in 1 to $add return $stationutil:defaults("future_time_as_datetime")
        )

    let $cdd:=(
        for $c allowing empty in $CreationDate
        order by $c
        return if (empty($c)) then xs:dateTime("2099-12-31T00:00:00") else $c
        )

    let $creation := for $c allowing empty in $cdd return <cd c="{$c}"/>
    let $termination := for $t allowing empty in $tdd return <td t="{$t}"/>

(:Create a temporary xml to facilitate results and efficiency   :)

    let $streams:= for-each-pair($creation, $termination, function($c, $t) {<row>{$c} {$t}</row>})

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
(:    let $log:= if ($td>=$start ) then util:log("info", "Examining: " || $cd || " " || $start || "  " || $td ) else util:log("info", "Examining: " || $cd || " " || $td || " " || $start ):)

    where

 (

        (($start<=$td) and ($end>=$cd)  and ($cd<$td))

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

            range:matches($s, $NSLCSE("station_pattern"))
     and    ($n = $NSLCSE("network_sequence"))
     and    matches($c, $NSLCSE("channel_pattern"))
     and    matches($l, $NSLCSE("location_pattern"))

(:    }:)
(:    catch err:* {false()}:)
};



(:~ Validate request parameters
 : @param $parameters map to be validated:)
declare function stationutil:validate_request( $parameters as map()*) as xs:boolean
{

try {

not(
some $NSLCSE in $parameters
satisfies
 (
(:          not(stationutil:empty_parameter_check()) :)

           ($NSLCSE("level")="response" and $NSLCSE("format") ="text")
           or ($NSLCSE("level")!="station" and $NSLCSE("format") ="geojson")
           or xs:decimal($NSLCSE("minlatitude")) > 90.0
           or xs:decimal($NSLCSE("maxlatitude")) > 90.0
           or xs:decimal($NSLCSE("minlatitude")) <-90.0
           or xs:decimal($NSLCSE("maxlatitude")) <-90.0
(:           or xs:decimal($NSLCSE("minlatitude")) > xs:decimal($NSLCSE("maxlatitude")):)
           or xs:decimal($NSLCSE("minlongitude")) > 180.0
           or xs:decimal($NSLCSE("maxlongitude")) > 180.0
           or xs:decimal($NSLCSE("minlongitude")) <-180.0
           or xs:decimal($NSLCSE("maxlongitude")) <-180.0
(:           or xs:decimal($NSLCSE("minlongitude")) > xs:decimal($NSLCSE("maxlongitude")):)
           or xs:decimal($NSLCSE("latitude"))  >  90.0 or xs:decimal($NSLCSE("latitude"))  <  -90.0
           or xs:decimal($NSLCSE("longitude")) > 180.0 or xs:decimal($NSLCSE("longitude")) < -180.0
           or xs:decimal($NSLCSE("minradius")) <0 or xs:decimal($NSLCSE("minradius")) >= xs:decimal($NSLCSE("maxradius"))
           or xs:decimal($NSLCSE("maxradius")) <0 or xs:decimal($NSLCSE("maxradius")) > 180.0
           or $NSLCSE("startbefore") < $NSLCSE("startafter")
           or $NSLCSE("endbefore") < $NSLCSE("endafter")
           or $NSLCSE("starttime") > $NSLCSE("endtime")
           or not(matches($NSLCSE("level"),"network|station|channel|response"))
           or not(xs:string($NSLCSE("includerestricted"))="true" or xs:string($NSLCSE("includerestricted"))="false") (:TODO options:)
           or not( $NSLCSE("format") ="xml" or $NSLCSE("format")="text" or $NSLCSE("format")="json" or $NSLCSE("format")="geojson" )
           or not(xs:string($NSLCSE("includeavailability"))="false")
           or not(xs:string($NSLCSE("matchtimeseries"))="false")
           or (contains(stationutil:network_pattern_translate($NSLCSE("network")), "#"))
           or (contains(stationutil:station_pattern_translate($NSLCSE("station")), "#"))
           or (contains(stationutil:channel_pattern_translate($NSLCSE("channel")), "#"))
           or (contains(stationutil:location_pattern_translate($NSLCSE("location")), "#"))
           or (contains(stationutil:alternate_network_pattern_translate($NSLCSE("alternate_network")), "#"))
           or (empty($NSLCSE("asofdate")) )
           or (empty($NSLCSE("updatedafter")) )
           or (empty($NSLCSE("startbefore")) )
           or (empty($NSLCSE("endbefore")) )
           or (empty($NSLCSE("startafter")) )
           or (empty($NSLCSE("startbefore")) )
           or (empty($NSLCSE("starttime")) )
           or (empty($NSLCSE("endtime")) )
           )

)
and stationutil:get-parameter($stationutil:parameters_table[1], "post_size_correct") ="true"

}
catch err:* {false()}

} ;

(:~ Validate request parameters TODO use for different xml_producer algorithm:)
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

(:~ Remove recursively elements with given $remove-names and its children, works on sequences
 :
 : @param $input element tree
 : @param $remove-names name of elements to remove
 : :)
declare function stationutil:remove-multi($in as element()*, $remove-names as xs:string*) as element()* {
    for $input in $in
    return
        element { node-name($input) } {
            $input/@*,
            for $child in $input/node()[not(name(.) = $remove-names)]
            (: for $child in $input/node()[name(.)!=$remove-names] Fails :) return
                if ($child instance of element()) then
                    stationutil:remove-elements($child, $remove-names)
                else
                    $child
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
declare function stationutil:distance($Latitude1 as xs:string*, $Longitude1 as xs:string*, $Latitude2 as xs:string*,
                                      $Longitude2 as xs:string*)
as xs:decimal
{
    (: In radians :)
    (: BEWARE multiple station periods give multiple coordinates TODO better management  :)
    let $lat1 := xs:decimal($Latitude1[1]) * (math:pi() div 180.0)
    let $lon1 := xs:decimal($Longitude1[1]) * (math:pi() div 180.0)
    let $lat2 := xs:decimal($Latitude2[1]) * (math:pi() div 180.0)
    let $lon2 := xs:decimal($Longitude2[1]) * (math:pi() div 180.0)
    (: Distance in km R*fi , d = 6371 * arccos[ (sin(lat1) * sin(lat2)) + cos(lat1) * cos(lat2) * cos(long2 – long1) ]
    Spherical Law of Cosines, TODO change with
     : :) let $d :=
        180.0 div math:pi() * math:acos(math:sin($lat1) * math:sin($lat2) + math:cos($lat1) * math:cos($lat2) *
                                            math:cos($lon2 - $lon1))
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
    empty($restrictedStatus)
    or
    (
        some $rs in $restrictedStatus, $NSLCSE in $parameter
        satisfies
        ($rs="open" or $rs="partial") or $NSLCSE("includerestricted")="true"
    )
};



(:~ Map the request params in stationutil:parameters  :)
declare function stationutil:set_parameters_row_from_GET() as map()* {
(:TODO same treatment to time params in POST:)
(:try {:)


let $nodata := request:get-parameter("nodata", $stationutil:defaults("nodata"))

let $startbefore_s := request:get-parameter("startbefore", $stationutil:defaults("startbefore"))
let $startbefore := try {xs:dateTime(stationutil:time_adjust($startbefore_s))}
                    catch err:* {()}

let $startafter_s := request:get-parameter("startafter", $stationutil:defaults("startafter"))
let $startafter := try {xs:dateTime(stationutil:time_adjust($startafter_s))}
                    catch err:* {()}

let $endbefore_s := request:get-parameter("endbefore", $stationutil:defaults("endbefore"))
let $endbefore   := try { xs:dateTime(stationutil:time_adjust($endbefore_s))}
                    catch err:* { () }

let $endafter_s  := request:get-parameter("endafter", $stationutil:defaults("endafter"))
let $endafter    := try { xs:dateTime(stationutil:time_adjust($endafter_s))}
                    catch err:* { () }

let $updatedafter_s := request:get-parameter("updatedafter", $stationutil:defaults("updatedafter"))
let $updatedafter:= try { xs:dateTime(stationutil:time_adjust($updatedafter_s))}
                    catch err:* { () }
let $asofdate_s  :=  request:get-parameter("asofdate", $stationutil:defaults("asofdate"))
let $asofdate    :=  try {xs:dateTime(stationutil:time_adjust($asofdate_s))}
                     catch err:* { () }



let $level := request:get-parameter("level", $stationutil:defaults("level"))

(: No readings if no parameters:)
let $minradius := request:get-parameter("minradius", ())
let $maxradius := request:get-parameter("maxradius", ())

(: No readings if no parameters:)
let $minradiuskm := request:get-parameter("minradiuskm", ())
let $maxradiuskm := request:get-parameter("maxradiuskm", ())

let $includerestricted := lower-case(xs:string(request:get-parameter("includerestricted",$stationutil:defaults("includerestricted"))))
let $matchtimeseries := lower-case(xs:string(request:get-parameter("matchtimeseries",$stationutil:defaults("matchtimeseries"))))
let $includeavailability := lower-case(xs:string(request:get-parameter("includeavailability",$stationutil:defaults("includeavailability"))))
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
let $alternate_network := $network
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
let $starttime:= try {if (exists($start)) then xs:dateTime(stationutil:time_adjust($start)) else if (exists($starttime1)) then xs:dateTime(stationutil:time_adjust($starttime1)) else xs:dateTime($stationutil:defaults("starttime"))} catch err:* {()}
let $start:=$starttime
let $endtime:=try {if (exists($end)) then xs:dateTime(stationutil:time_adjust($end)) else if (exists($endtime1)) then xs:dateTime(stationutil:time_adjust($endtime1)) else xs:dateTime($stationutil:defaults("endtime"))} catch err:* {()}
let $end:=$endtime

(: 4 parametri di comodo per evitare le chiamate alle pattern_translate nella query traduco i pattern qui :)

(:BEWARE CALL ORDER IMPORTANT FOR CORRECT WORK:)
let $network_pattern := stationutil:network_pattern_translate($network) (:TODO AlternateNetwork:)
(:let $log:= util:log("info", "Assigning network pattern " || $network_pattern):)
let $alternate_network_pattern := stationutil:alternate_network_pattern_translate($network)

let $network_sequence := stationutil:network_pattern_to_sequence($network)

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
"matchtimeseries" : $matchtimeseries,
"includeavailability" : $includeavailability,
"asofdate" : $asofdate,
"maxlongitude" : xs:decimal($maxlongitude),
"maxlon" : xs:decimal($maxlon),
"minlongitude" : xs:decimal($minlongitude),
"minlon" : xs:decimal($minlon),
"maxlatitude" : xs:decimal($maxlatitude),
"maxlat" : xs:decimal($maxlat),
"minlatitude" : xs:decimal($minlatitude),
"minlat" : xs:decimal($minlat),
"nodata" :$nodata,
"network_pattern" :$network_pattern,
"station_pattern" :$station_pattern,
"channel_pattern" :$channel_pattern,
"location_pattern" :$location_pattern,

"alternate_network" : $alternate_network,
"alternate_network_pattern" :$alternate_network_pattern,
"network_sequence" : $network_sequence,
"post_size_correct" : "true"
}

(:let $p:= util:log("info", "GET nscl: " || $result("network_pattern") || " " || $result("station_pattern") || " "  || $result("channel_pattern") || " " || $result("location_pattern") || " " || $result("starttime") || " " || $result("endtime") || " " ) :)
return $result
(:}:)
(:catch err:FORG0001 {:)
(:    let $result := map {}:)
(:    return $result:)
(:}:)
(:DEBUG:)
(:let $p:= util:log("info", "GET nscl: " || $result("network_pattern") || " " || $result("station_pattern") || " "  || $result("channel_pattern") || " " || $result("location_pattern") || " " || $result("starttime") || " " || $result("endtime") || " " ) :)
(:DEBUG:)

};

(:
 : @FIXME request:get-data() cannot be called twice
 : @return post data from the request
 :
 :)
declare function stationutil:setpostdata() as xs:string* {

    let $content-type := request:get-header("Content-Type")
    let $ret :=
        if ($content-type = "application/x-www-form-urlencoded") then
            (: application/x-www-form-urlencoded in ObsPy Client try to catch:)
            let $parameters := request:get-parameter-names()
(:            let $l := for $p in $parameters return util:log("info", $p || "--" || request:get-parameter($p, "None")):)
            let $ret := "level=" || request:get-parameter("level", "None")
            let $log := stationutil:debug("info", "Received" || $ret)
            return $ret
        (:   Works with pytest requests    :)
        else if ($content-type = "application/octet-stream") then
            util:base64-decode(request:get-data())
        else
            (:Works when no header is set:
             i.e when removed specifying in location section of default.conf
             nginx proxy_set_header       Content-Type "";:)
            request:get-data()
    (: let $l:=(for $i in $ret return util:log("info", $i)) :)
    let $log := if ($stationutil:settings("enable_query_log")) then util:log("info", "Received
" || string-join($ret)) else ()
    return $ret
};

declare function stationutil:getpostdata() as xs:string {
 string-join($stationutil:postdata)
};


declare function stationutil:sequenceoflines() as xs:string* {
let $sequenceoflines :=stationutil:lines($stationutil:postdata)
return $sequenceoflines
};

declare function stationutil:set_parameters_table_from_POST() as map()* {
(:try:)
(:{:)

let $sequenceoflines :=stationutil:lines($stationutil:postdata)

(: A sequence of maps :)

let $sequence :=
    for $line in $sequenceoflines
        return
         if (matches($line,"=") or $line="" )
            then ()
            else (
                let $key_val := tokenize($line,"\s+")
(: apply pattern translate and add related entries :)
                return map:merge((
                    map:entry("net", $key_val[1]), map:entry("network", $key_val[1]), map:entry("network_pattern",stationutil:network_pattern_translate($key_val[1])),
                    map:entry("sta", $key_val[2]), map:entry("station", $key_val[2]),
(:                    map:entry("station_pattern",stationutil:station_pattern_translate($key_val[2])),:)
                    map:entry("loc", $key_val[3]), map:entry("location", $key_val[3]), map:entry("location_pattern",stationutil:location_pattern_translate($key_val[3])),
                    map:entry("cha", $key_val[4]) , map:entry("channel", $key_val[4]), map:entry("channel_pattern",stationutil:channel_pattern_translate($key_val[4])),
                    map:entry("start", xs:dateTime(stationutil:time_adjust($key_val[5]))), map:entry("starttime", xs:dateTime(stationutil:time_adjust($key_val[5]))),
                    map:entry("end", xs:dateTime(stationutil:time_adjust($key_val[6]))), map:entry( "endtime", xs:dateTime(stationutil:time_adjust($key_val[6]))),
                    map:entry("alternate_network", $key_val[1]), map:entry("alternate_network_pattern",stationutil:alternate_network_pattern_translate($key_val[1]))
                    ) )
            )

let $post_size_correct:= if (count($sequence) < $stationutil:settings("post_limit_rows")) then "true" else "false"

(:Optimization phase, filter and reorder the POST lines, reducing size:)
let $reordered:=(
    for $i in $sequence
        let $net:=$i("net")
        let $network:=$i("network")
        let $network_pattern:=$i("network_pattern")
        let $sta:=$i("sta")
        let $station:=$i("station")
        let $station_pattern:=$i("station_pattern")
        let $cha:=$i("cha")
        let $channel:=$i("channel")
        let $channel_pattern:=$i("channel_pattern")
        let $loc := $i("loc")
        let $location := $i("location")
        let $location_pattern := $i("location_pattern")
        let $start:=$i("start")
        let $starttime :=$i("starttime")
        let $end := $i("end")
        let $endtime := $i("endtime")
        let $alternate_network := $i("alternate_network")
        let $alternate_network_pattern := $i("alternate_network_pattern")


(: grouping to form new station pattern sequence, compressing more lines in one):)
        group by $starttime, $start, $endtime, $end, $channel_pattern,$channel,$cha, $location_pattern, $location, $network_pattern, $network, $net, $alternate_network_pattern,$alternate_network
        order by $network_pattern, $starttime , $endtime, $location_pattern, $channel_pattern
    return

            map:merge((
                    map:entry("net", $net), map:entry("network", $network), map:entry("network_pattern",$network_pattern),
                    map:entry("sta", string-join($station,",")), map:entry("station", string-join($station,",")), map:entry("station_pattern",stationutil:station_pattern_translate(string-join($station,","))),
                    map:entry("loc", $loc), map:entry("location", $location), map:entry("location_pattern",$location_pattern),
                    map:entry("cha", $cha) , map:entry("channel", $channel), map:entry("channel_pattern",$channel_pattern),
                    map:entry("start", $start), map:entry("starttime", $starttime),
                    map:entry("end", $end), map:entry( "endtime", $endtime),
                    map:entry("alternate_network", $alternate_network), map:entry("alternate_network_pattern",$alternate_network_pattern),
                    map:entry("post_size_correct", $post_size_correct),
                    $stationutil:parameters
                    ) )
    )



return $reordered
(:}:)
(:catch err:* {:)
(:    let $m := map {}:)
(:    let $p:= util:log("error", "POST parsing"):)
(:    return $m:)
(::)
(:}:)
};





declare function stationutil:set_alternate_network_POST() as xs:string {

let $sequenceoflines :=stationutil:lines($stationutil:postdata)

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
                    map:entry("alternate_network", $key_val[1]), map:entry("alternate_network_pattern",stationutil:alternate_network_pattern_translate($key_val[1])),
                    $stationutil:parameters ) )
            )

let $alternate_network_pattern_real :=
    "("||string-join(distinct-values(
    for $entry in $NSLCSE
        return $entry("alternate_network_pattern")
    )
    ,"|")||")"


return $alternate_network_pattern_real

};

declare function stationutil:set_network_pattern_POST() as xs:string {

let $pattern_real :=
    "("||string-join(distinct-values(
    for $entry in $stationutil:parameters_table
        return $entry("network_pattern")
    )
    ,"|")||")"

return $pattern_real

};


declare function stationutil:set_station_pattern_POST() as xs:string {

let $pattern_real :=
    "("||string-join(distinct-values(
    for $entry in $stationutil:parameters_table
        return $entry("station_pattern")
    )
    ,"|")||")"

return $pattern_real

};

declare function stationutil:set_channel_pattern_POST() as xs:string {

let $pattern_real :=
    "("||string-join(distinct-values(
    for $entry in $stationutil:parameters_table
        return $entry("channel_pattern")
    )
    ,"|")||")"

return $pattern_real

};

declare function stationutil:set_starttime_POST() as xs:dateTime* {

let $times :=

    for $entry in $stationutil:parameters_table
        return xs:dateTime($entry("starttime"))


return $times

};

declare function stationutil:set_endtime_POST() as xs:dateTime* {

let $times :=

    for $entry in $stationutil:parameters_table
        return xs:dateTime($entry("endtime"))

return $times

};




(:TODO same treatment to time params in POST:)
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
"asofdate"          : xs:dateTime($stationutil:defaults("asofdate")),
"level"             : $stationutil:defaults("level"),
"includerestricted" : $stationutil:defaults("includerestricted"),
"format"            : $stationutil:defaults("format"),
"matchtimeseries"   : $stationutil:defaults("matchtimeseries"),
"includeavailability" : $stationutil:defaults("includeavailability")
}


let $sequenceoflines :=stationutil:lines($stationutil:postdata)

let $params :=
    map:merge(

    for $line in $sequenceoflines
        return
         if (matches($line,"="))
            then (
                let $key_val := tokenize($line,"=")
(:                let $p:= util:log("info", "Matched " || $key_val[1] || "=" || lower-case($key_val[2]) ):)
                return if ($key_val[1]="includerestricted" or $key_val[1]="matchtimeseries" or $key_val[1]="includeavailability" ) then map:entry($key_val[1], lower-case($key_val[2])) else map:entry($key_val[1], $key_val[2])
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

let $result := map:put($result,"minlatitude", xs:decimal($minlatitude))
let $result := map:put($result,"minlat", xs:decimal($minlat))
let $result := map:put($result,"minlongitude", xs:decimal($minlongitude))
let $result := map:put($result,"minlon", xs:decimal($minlon))
let $result := map:put($result,"maxlatitude", xs:decimal($maxlatitude))
let $result := map:put($result,"maxlat", xs:decimal($maxlat))
let $result := map:put($result,"maxlongitude", xs:decimal($maxlongitude))
let $result := map:put($result,"maxlon", xs:decimal($maxlon))

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
            case "network" return contains(stationutil:network_pattern_translate($value), "#")
            case "station" return contains(stationutil:station_pattern_translate($value), "#")
            case "channel" return contains(stationutil:channel_pattern_translate($value), "#")
            case "location" return contains(stationutil:location_pattern_translate($value), "#")
            default return false()
        )
    return $value
    )


return

string-join(
for $u in $unmatched

return

"
Check " ||  $nscl || " parameter, found '" || $u || "'" ||
"
"
)
}
catch err:* {
"
Syntax error in some parameter
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


declare function stationutil:syntax_time($parameters as map()*, $name as xs:string) as xs:string {
try
{
string-join(
for $p in $parameters

let $t := xs:dateTime(stationutil:time_adjust($p($name)))
(:let $t := $p($name):)

return ""
)
}
catch err:* {
"
Check " || $name || " parameter

Valid syntax: YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS, YYY-MM-DDTHH:MM:SS.ssssss
"
}

};


declare function stationutil:syntax_times($parameters as map()*) as xs:string {

let $a:=    stationutil:syntax_time($parameters,"startbefore")
         || stationutil:syntax_time($parameters,"endbefore")
         || stationutil:syntax_time($parameters,"startafter")
         || stationutil:syntax_time($parameters,"endafter")
         || stationutil:syntax_time($parameters,"asofdate")
         || stationutil:syntax_time($parameters,"starttime")
         || stationutil:syntax_time($parameters,"endtime")
         || stationutil:syntax_time($parameters,"updatedafter")

return $a

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
    if (not( $includerestricted="true" or $includerestricted="false"))
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
    if (not( $format ="xml" or $format="text" or $format="json" or $format="geojson" ))
    then
"
The format parameter must be xml, text json or geojson
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
        if (($level="response" and $format = "text") or ($level!="station" and $format = "geojson"))
        then
"Unsupported combination of level and format
"
else ""


};


declare function stationutil:syntax_includeavailability($parameters as map()*) as xs:string{
string-join(
for $p in $parameters

let $includeavailability := xs:string($p("includeavailability"))

return
    if (not( $includeavailability="false"))
    then
"
Filtering based on available time series not supported.
"
    else  ""
)


};


declare function stationutil:syntax_matchtimeseries($parameters as map()*) as xs:string{
string-join(
for $p in $parameters

let $matchtimeseries := xs:string($p("matchtimeseries"))

return
    if (not( $matchtimeseries="false"))
    then
"
Including of availability information not supported.
"
    else  ""
)


};


declare function stationutil:internal_error( $exception as xs:string) {

    response:set-status-code(500),
    let $log := stationutil:log("error", "Internal error for request " || request:get-query-string())
    let $log := stationutil:log("error", "Exception " || $exception)
    let $o:=util:declare-option("exist:serialize","method=text media-type=text/plain indent=no")
    return
        "Error 500: Internal Server Error"

};


declare function stationutil:empty_parameter_error($parameters as map()*) as xs:string
{
try {

string-join(
for $p in $parameters

return string-join(
for $key in map:keys($p)

return if ( empty($p($key)) )
           then
"
Parameter " || $key || " can not be empty
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

    if (stationutil:get-parameter($stationutil:parameters_table[1], "nodata") eq "404")
    then
        (
            (:return xml error tag to be translated :)
            if ( (stationutil:get-parameter($stationutil:parameters_table[1], "format") eq "text")  or
            ( (stationutil:get-parameter($stationutil:parameters_table[1], "format") eq "json")  or  (stationutil:get-parameter($stationutil:parameters_table[1], "format") eq "geojson") )) then (
                response:set-status-code(404) ,
              <xml><ERROR>{"Error 404 - no matching inventory found" || stationutil:global_error_text(404)}</ERROR></xml>
            )
            else
                (
             response:set-status-code(404) , "Error 404 - no matching inventory found" || stationutil:global_error_text(404)
        )
        )
    else if (stationutil:get-parameter($stationutil:parameters_table[1], "nodata")  eq "204") then
        response:set-status-code(204)
    else
        response:set-status-code(400)

};


declare function stationutil:request_error($parameters as map()*) {


if (stationutil:get-parameter($parameters[1], "post_size_correct")="false")
then
    let $r:=response:set-status-code(413)
    let $o:=util:declare-option("exist:serialize","method=text media-type=text/plain indent=no")
    return
"Error 413: Request Entity too large

Try splitting your request in half"

else stationutil:badrequest_error($parameters)

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
stationutil:syntax_includeavailability($p) ||
stationutil:syntax_matchtimeseries($p) ||
stationutil:empty_parameter_error($p) ||
stationutil:syntax_format($p) ||
stationutil:syntax_level($p) ||
stationutil:unknown_parameter_error()

(:||:)
(:stationutil:debug_parameter_error($p) :)
||
stationutil:global_error_text(400)



};

declare function stationutil:other_error() {
    (: declare output method locally to override default xml   :)
    util:declare-option("exist:serialize","method=text media-type=text/plain indent=no")  ,
     response:set-status-code(400) ,
     "Error 400: Bad request

Syntax Error in Request"
||
stationutil:global_error_text(400)
};

declare function stationutil:global_error_text($errorcode as xs:integer) as xs:string {

let $querystring:= request:get-query-string()
let $method := request:get-method()
let $path:= request:get-effective-uri()
let $log:=stationutil:log("info", "Error " || $errorcode || " for query:" || $querystring || " method: " || $method  || " path: " || $path)
let $realquerystring := if ($querystring) then "?" || $querystring else ""

return

"

Usage details are available from /fdsnws/station/1/

Request:

"

|| fn:substring-after( request:get-uri(), "/exist/apps/fdsn-station" )|| $realquerystring
||
(: request:get-url() || request:get-query-string() ||:)
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
      map:keys( $stationutil:parameters )
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
(:   let $log:=util:log("info", "lines " || $arg):)

(:   return :)
       tokenize($arg, '[\n\r]+', "m")

 } ;



declare function stationutil:run() {


if ( stationutil:validate_request($stationutil:parameters_table) and empty($stationutil:unknown_parameters)  )

then
    switch (stationutil:get-parameter($stationutil:parameters_table[1], "format"))
    case "xml"
    return
        let $dummy := util:declare-option("exist:serialize","method=xml media-type=text/xml indent=no")
        return
            stationutil:xml-producer()
    case "text"
    return
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
    case "json"
    return
            let $dummy := util:declare-option("exist:serialize","method=json media-type=application/json indent=yes")

            let $xml := stationutil:xml-producer()
            return
                if ($xml//ERROR) then
                     $xml//ERROR/text()
                else
                <root>{$xml}</root>

    case "geojson"
    return
        let $dummy := util:declare-option("exist:serialize","method=text media-type=application/json indent=yes")
        let $xml := stationutil:xml-producer()
        return
        if ($xml//ERROR) then
             $xml//ERROR/text()
        else
            transform:transform($xml, doc("station-geojson.xsl"), ())

    default return ()

else
        stationutil:request_error($stationutil:parameters_table)


};

(: Stations selected without conditions other than net and station code or output format  :)
declare function stationutil:use_shortcut($includerestricted as xs:string) as xs:boolean {
(:    let $log := util:log("info", "use_shortcut(" ||$includerestricted||")"):)
    let $param_list := request:get-parameter-names()
(:    let $alternate_network  := stationutil:get-parameter($stationutil:parameters_table[1], "alternate_network_pattern" ):)
    let $err_param_list := sum(for $param in $param_list
    return

      if (matches($param ,"^channel$|^cha$|^location$|^loc$|^minlatitude$|^minlat$|^maxlatitude$|^maxlat$|^minlongitude$|^minlon$|^maxlongitude$|^maxlon$|^starttime$|^start$|^endtime$|^end$|^startbefore$|^endbefore$|^startafter$|^endafter$|^latitude$|^lat$|^longitude$|^lon$|^maxradius$|^minradius$|^maxradiuskm$|^minradiuskm$|^updatedafter$" ))
      then 1
      else 0
      )


return  $err_param_list <1 and $stationutil:parameters_table("includerestricted")="true"
(:and  ($alternate_network = ('(^.*$)')):)

};

declare function stationutil:use_no_restricted_radius() as xs:boolean {
(:    let $log := util:log("info", "use_no_restricted_radius")    :)
    let $includerestricted:=$stationutil:parameters_table("includerestricted")
    let $param_list := request:get-parameter-names()
(:    let $alternate_network  := stationutil:get-parameter($stationutil:parameters_table[1], "alternate_network_pattern" ):)
    let $err_param_list := sum(for $param in $param_list
    return

      if (matches($param ,"^latitude$|^lat$|^longitude$|^lon$|^maxradius$|^minradius$|^maxradiuskm$|^minradiuskm$" ))
      then 1
      else 0
      )

return  $err_param_list <1 and $includerestricted="true"
(:and  ($alternate_network = ('(^.*$)')):)

};

declare function stationutil:use_no_radius() as xs:boolean {
(:    let $log := util:log("info", "use_no_restricted_radius")    :)
    let $param_list := request:get-parameter-names()
(:    let $alternate_network  := stationutil:get-parameter($stationutil:parameters_table[1], "alternate_network_pattern" ):)
    let $err_param_list := sum(for $param in $param_list
    return

      if (matches($param ,"^latitude$|^lat$|^longitude$|^lon$|^maxradius$|^minradius$|^maxradiuskm$|^minradiuskm$" ))
      then 1
      else 0
      )

return  $err_param_list <1
(:and  ($alternate_network = ('(^.*$)')):)

};


declare function stationutil:full_data_requested() as xs:boolean {

    (: Is all data requested ? :)
(:    let $log := util:log("info", "full_data_requested"):)
    let $param_list := request:get-parameter-names()
    let $err_param_list := sum(for $param in $param_list
    return
      if (matches($param ,"^minlatitude$|^minlat$|^maxlatitude$|^maxlat$|^minlongitude$|^minlon$|^maxlongitude$|^maxlon$|^starttime$|^start$|^endtime$|^end$|^startbefore$|^endbefore$|^startafter$|^endafter$|^latitude$|^lat$|^longitude$|^lon$|^maxradius$|^minradius$|^maxradiuskm$|^minradiuskm$|^includerestricted$|^updatedafter$" ))
      then 1
      else 0
    )

    let $network  := stationutil:get-parameter($stationutil:parameters_table[1], "network_pattern" )
    let $station  := stationutil:get-parameter($stationutil:parameters_table[1], "station_pattern")
    let $channel  := stationutil:get-parameter($stationutil:parameters_table[1], "channel_pattern")
    let $location := stationutil:get-parameter($stationutil:parameters_table[1], "location_pattern")
    let $alternate_network  := stationutil:get-parameter($stationutil:parameters_table[1], "alternate_network_pattern" )


(:    return  $err_param_list <1 and ($network = ('(^.*$)')) and ($station = ('(^.*$)'))  and ($channel = ('(^.*$)'))  and  ($location = ('(^.*$)'))  and  ($alternate_network = '(FSDN)'):)
(:PATCHED TODO change pattern and use ranges for other than station:)
    return  $err_param_list <1 and ($network = ('(^.*$)')) and ($station = ('(.*)'))  and ($channel = ('(^.*$)'))  and  ($location = ('(^.*$)'))  and  ($alternate_network = '(FSDN)')
};


(:Select case asked virtual network :)
declare function stationutil:virtual_network_requested() as xs:boolean {

    let $r :=     sum(
    for $params in  $stationutil:parameters_table
     let $alternate_network_pattern  := stationutil:get-parameter($params, "alternate_network_pattern" )
(:     let $log := util:log("info", "virtual_network_requested - Alternate Network pattern: " || $alternate_network_pattern):)

    return
        if (matches($alternate_network_pattern ,"_")) then
(:            let $log := util:log("info", "virtual_network_requested - Alternate Network pattern: " || $alternate_network_pattern || " matched"):)
            let $r:= 1
            return $r
        else
(:            let $log := util:log("info", "virtual_network_requested - Alternate Network pattern: " || $alternate_network_pattern || " not empty"):)
            let $r:=0
            return $r
            )

    return ($r != 0)
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
    return
    not(contains($station,'.') or contains($station,'|'))

};


declare function stationutil:one_full_station() as xs:boolean {

    let $param_list := request:get-parameter-names()
    let $err_param_list := sum(for $param in $param_list
    return

     if (matches($param ,"^channel$|^cha$|^location$|^loc$|^minlatitude$|^minlat$|^maxlatitude$|^maxlat$|^minlongitude$|^minlon$|^maxlongitude$|^maxlon$|^starttime$|^start$|^endtime$|^end$|^startbefore$|^endbefore$|^startafter$|^endafter$|^updatedafter$|^latitude$|^lat$|^longitude$|^lon$|^maxradius$|^minradius$|^maxradiuskm$|^minradiuskm$|^includerestricted$|^updatedafter$" ))
    then 1
    else 0
      )


    let $station := stationutil:get-parameter($stationutil:parameters_table[1], "station_pattern")

    return
    not(contains($station,'.') or contains($station,'|')) and $err_param_list<1
(:    or contains($sta,'*')) :)

};


declare function stationutil:unknown_parameter_from_GET() as xs:string* {
    let $param_list := request:get-parameter-names()

    let $err_param_list := for $param in $param_list
    return
        (
            if (matches($param,"^network$|^net$|^station$|^sta$|^channel$|^cha$|^location$|^loc$|^minlatitude$|^minlat$|^maxlatitude$|^maxlat$|^minlongitude$|^minlon$|^maxlongitude$|^maxlon$|^starttime$|^start$|^endtime$|^end$|^startbefore$|^endbefore$|^startafter$|^endafter$|^updatedafter$|^latitude$|^lat$|^longitude$|^lon$|^maxradius$|^minradius$|^maxradiuskm$|^minradiuskm$|^includerestricted$|^nodata$|^level$|^format$|^asofdate$|^matchtimeseries$|^includeavailability$"))
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
            if (matches($param,"^network$|^net$|^station$|^sta$|^channel$|^cha$|^location$|^loc$|^minlatitude$|^minlat$|^maxlatitude$|^maxlat$|^minlongitude$|^minlon$|^maxlongitude$|^maxlon$|^starttime$|^start$|^endtime$|^end$|^startbefore$|^endbefore$|^startafter$|^endafter$|^updatedafter$|^latitude$|^lat$|^longitude$|^lon$|^maxradius$|^minradius$|^maxradiuskm$|^minradiuskm$|^includerestricted$|^nodata$|^level$|^format$|^asofdate$|^matchtimeseries$|^includeavailability$"))
            then ()
            else $param
        )
    return
       $err_param_list
}
;



(:~
 : @return the Station XML or an error :)
declare function stationutil:xml-producer() {
(:let $dummy := util:declare-option("exist:serialize","method=xml media-type=text/xml indent=no"):)
let $content :=
    switch (stationutil:get-parameter($stationutil:parameters_table[1], "level"))
    case "network" return
        if (request:get-method()="POST")
        then
(:the query_core_POST specialized for skipping virtual_networks checks :)
            if ( stationutil:virtual_network_requested()) then
                stationutil:query_core_virtual_network_POST($stationutil:parameters_table,"network")
            else
                stationutil:query_core_POST($stationutil:parameters_table,"network")
        else
            if ( stationutil:virtual_network_requested()) then
                stationutil:query_core_virtual_network($stationutil:parameters_table,"network") (:TODO :)
            else
            if ( stationutil:no_wild_station() ) then
                stationutil:query_core_fixed_station($stationutil:parameters_table,"network")
            else
            if ( stationutil:full_data_requested() ) then
                stationutil:query_all_network()
            else
(: if no radius requested:)
            if (stationutil:use_no_radius()) then
                stationutil:query_noradius_level_network($stationutil:parameters_table,"network")
            else
                stationutil:query_core($stationutil:parameters_table,"network")
    case "station" return
        if (request:get-method()="POST")
        then
            if ( stationutil:virtual_network_requested()) then
                stationutil:query_core_virtual_network_POST($stationutil:parameters_table,"station")
            else
            stationutil:query_core_POST($stationutil:parameters_table,"station")
        else
            if ( stationutil:virtual_network_requested()) then
                stationutil:query_core_virtual_network($stationutil:parameters_table,"station")
            else
            if ( stationutil:no_wild_station() ) then
                stationutil:query_core_fixed_station($stationutil:parameters_table,"station")
            else
            if ( stationutil:full_data_requested() ) then
                stationutil:query_core_full_data($stationutil:parameters_table,"station")
            else
            if (stationutil:use_no_restricted_radius()) then
                stationutil:query_noradius_includerestricted_level_station($stationutil:parameters_table,"station")
            else
(:  includerestricted=false      :)
            if (stationutil:use_no_radius()) then
                stationutil:query_noradius_level_station($stationutil:parameters_table,"station")
            else
                stationutil:query_core($stationutil:parameters_table,"station")
    case "channel" return
        if (request:get-method()="POST")
        then
            if ( stationutil:virtual_network_requested()) then
                stationutil:query_core_virtual_network_POST($stationutil:parameters_table,"channel")
            else
                stationutil:query_core_POST($stationutil:parameters_table,"channel")
        else
            if ( stationutil:virtual_network_requested()) then
                stationutil:query_core_virtual_network($stationutil:parameters_table,"channel")
            else
            if ( stationutil:one_full_station() ) then
                stationutil:query_core_single_station($stationutil:parameters_table)
            else
            if ( stationutil:no_wild_station() ) then
                stationutil:query_core_fixed_station($stationutil:parameters_table,"channel")
            else
            if (stationutil:use_shortcut($stationutil:parameters_table("includerestricted"))) then
                stationutil:query_core_channel_shortcut($stationutil:parameters_table)
            else
            if (stationutil:use_no_restricted_radius()) then
                stationutil:query_noradius_includerestricted_level_channel_response($stationutil:parameters_table,"channel")
            else
            if (stationutil:use_no_radius()) then
                stationutil:query_noradius_level_channel_response($stationutil:parameters_table,"channel")
            else
                stationutil:query_core($stationutil:parameters_table,"channel")

    case "response" return
        if (request:get-method()="POST")
        then
            if ( stationutil:virtual_network_requested()) then
                stationutil:query_core_virtual_network_POST($stationutil:parameters_table,"response")
            else
                stationutil:query_core_POST($stationutil:parameters_table,"response")
        else
            if ( stationutil:virtual_network_requested()) then
                stationutil:query_core_virtual_network($stationutil:parameters_table,"response")
            else
            if ( stationutil:one_full_station() ) then
                stationutil:query_core_single_station($stationutil:parameters_table)
            else
            if ( stationutil:no_wild_station() ) then
                stationutil:query_core_fixed_station($stationutil:parameters_table,"response")
            else
            if (stationutil:use_shortcut($stationutil:parameters_table("includerestricted"))) then
                stationutil:query_core_channel_shortcut($stationutil:parameters_table)
            else
            if (stationutil:use_no_restricted_radius()) then
                stationutil:query_noradius_includerestricted_level_channel_response($stationutil:parameters_table,"response")
            else
            if (stationutil:use_no_radius()) then
                stationutil:query_noradius_level_channel_response($stationutil:parameters_table,"response")
            else
                stationutil:query_core($stationutil:parameters_table,"response")
    default return ()

return
if (not(empty($content))) then
<FDSNStationXML xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">
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
<Created>{adjust-dateTime-to-timezone(current-dateTime(),())}</Created>
{$content}
</FDSNStationXML>
else
    stationutil:nodata_error()
};


declare function stationutil:if-empty
  ( $arg as item()* ,
    $value as item() )  as item()* {

(:  let $log := for $a allowing empty in $arg return util:log("info", "empty list: " || $a ):)
  for $a allowing empty in $arg
  return
  if (string($a) != '')
  then data($a)
  else $value
 } ;





(:QUERIES SECTION START:)

declare function stationutil:query_core_fixed_station($NSLCSE as map()*, $level as xs:string){
(:DEBUG:)
(:try{:)

(: Supponiamo di eseguire codice diverso a seconda del livello, per network e station è sufficiente trovare tutte le network e station a cui appartiene
 : la stazione nominata, per channel e response si usa il codice completo di questa funzione
 : :)

let $dlog := stationutil:debug("info", "query_core_fixed_station")

(:Prepare the output, discarding it only when sure no channels meet criteria avoid to check before, then create output:)
(:let $xml := :)

(:    DONE updatedafter ( :)
    let $since:= xs:dateTime($NSLCSE("updatedafter"))

(: let $collection := if ($level="response" or $level="channel") then $stationutil:station_collection else $stationutil:station_pruned_collection:)
 let $collection := if ($level="response") then $stationutil:station_collection else $stationutil:station_pruned_collection
    for $network in xmldb:find-last-modified-since(collection($collection)//Network/Station[@code=$NSLCSE("station")]/.. ,$since) , $condition in $NSLCSE
(:    for $network in collection($stationutil:station_collection)//Network/Station[@code=$NSLCSE("station")]/..:)

(:    let $condition := $NSLCSE  :)
    let $minlatitude := $condition("minlatitude")
    let $maxlatitude := $condition("maxlatitude")
    let $minlongitude := $condition("minlongitude")
    let $maxlongitude := $condition("maxlongitude")


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
    let $startDate := $network/@startDate
    let $endDate := $network/@endDate
    let $sourceID:=$network/@sourceID
    let $restrictedStatus:=$network/@restrictedStatus
    let $alternateCode:=$network/@alternateCode
    let $historicalCode:=$network/@historicalCode
    let $stationrestrictedStatus:=$network/Station/@restrictedStatus
    let $channelrestrictedStatus:=$network//Channel/@restrictedStatus
    let $Description := $network/Description
    let $Identifier := $network/Identifier
    let $firstidentifier := $Identifier[1]
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
                    ($networkcode = $NSLCSE("network_sequence")) and
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
            ($networkcode = $NSLCSE("network_sequence")) and
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
    where
        $Latitude  > $minlatitude and
        $Latitude  < $maxlatitude and
        $Longitude > $minlongitude and
        $Longitude < $maxlongitude and
        matches($stationcode, $NSLCSE("station_pattern")) and
        ($networkcode = $NSLCSE("network_sequence")) and
        matches($channelcode, $NSLCSE("channel_pattern")) and
        matches($locationcode, $NSLCSE("location_pattern")) and
(:        stationutil:check_radius($condition, $lat,$lon) and TODO FIXME :)
        stationutil:check_restricted($condition,$restrictedStatus) and
        stationutil:check_restricted($condition,$stationrestrictedStatus) and
        stationutil:check_restricted($condition,$channelrestrictedStatus) and
        stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate )
        and
        (count($stations)>0)
        group by $networkcode, $alternateCode, $sourceID, $historicalCode, $startDate, $endDate, $restrictedStatus, $Description, $network_ingv_identifier, $firstidentifier
(:        , $Identifier:)
        order by $networkcode, $startDate, $endDate
    return

        <Network>
        {$networkcode}
        {$startDate}
        {$endDate}
        {$sourceID}{$restrictedStatus} {$alternateCode} {$historicalCode}
        {$Description}
        {functx:distinct-deep($Identifier)}
        {$network_ingv_identifier}
        <TotalNumberStations> {stationutil:stationcount($networkcode,$startDate, $endDate, $restrictedStatus)} </TotalNumberStations>
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
                    ($networkcode = $NSLCSE("network_sequence")) and
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
            ($networkcode = $NSLCSE("network_sequence")) and
            matches($channelcode, $NSLCSE("channel_pattern")) and
            matches($locationcode, $NSLCSE("location_pattern")) and
            stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and
            stationutil:check_radius($condition, $lat,$lon) and
            stationutil:check_restricted($condition,$stationrestrictedStatus)
(:            and ($channelcount>0):)
            and (count ($selected_channels)>0)
        group by $stationcode, $stationstartDate, $stationendDate, $stationrestrictedStatus
        order by $stationcode, $stationstartDate
        return

                <Station>
                {$stationcode}
                {$stationstartDate}
                {$stationendDate}
                {$stationrestrictedStatus}
                {$station/ingv:AlternateNetworks}
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




declare function stationutil:query_core_full_data($NSLCSE as map()*, $level as xs:string){
(:DEBUG:)
(:try{:)

let $dlog := stationutil:debug("info", "query_core_full_data" )

(:    DONE updatedafter ( :)
    let $since:= xs:dateTime($NSLCSE("updatedafter"))
    for $network in collection($stationutil:station_pruned_collection)//Network , $condition in $NSLCSE

    let $CreationDate:= $network//Channel/@startDate
(:    let $TerminationDate:= $network//Channel/@endDate:)
    let $TerminationDate:= if (empty($network//Channel/@endDate)) then $stationutil:defaults("future_time_as_datetime")  else $network//Channel/@endDate

    let $networkcode := $network/@code
    let $station:=$network//Station
    let $stationcode:=$station/@code
    let $lat := $station/Latitude
    let $lon := $station/Longitude

    let $channel:=$station/Channel
    let $startDate := $network/@startDate
    let $endDate := $network/@endDate
    let $sourceID:=$network/@sourceID
    let $restrictedStatus:=$network/@restrictedStatus
    let $alternateCode:=$network/@alternateCode
    let $historicalCode:=$network/@historicalCode
    let $stationrestrictedStatus:=$network/Station/@restrictedStatus
(:    let $channelrestrictedStatus:=$network//Channel/@restrictedStatus:)
    let $Description := $network/Description
    let $Identifier := $network/Identifier
    let $firstidentifier := $Identifier[1]
    let $Identifier_type:=$Identifier/@type
    let $network_ingv_identifier := $network/ingv:Identifier

(:FIX ODC TEST
 : il problema del group by per i campi che sono sequenze di elementi uguali se non si raggruppa
 : ma che per raggruppare devo conoscere e inserire nella clausola:)
        group by $networkcode, $alternateCode, $sourceID, $historicalCode, $startDate, $endDate, $restrictedStatus, $network_ingv_identifier, $Description, $firstidentifier
        order by $networkcode, $startDate, $endDate
    return

        <Network>
        {$networkcode}
        {$startDate}
        {$endDate}
        {$sourceID} {$restrictedStatus} {$alternateCode} {$historicalCode}
        {$Description}
        {functx:distinct-deep($Identifier)}
        {functx:distinct-deep($network_ingv_identifier)}
        {functx:distinct-deep($network/*[(name() != "Station") and (name() != "TotalNumberStations") and (name() != "SelectedNumberStations") and (name() != "Description") and (name() !="Identifier") and (name() != "ingv:Identifier") ])}

        <TotalNumberStations> {stationutil:stationcount($networkcode,$startDate,$endDate,$restrictedStatus )} </TotalNumberStations>
        <SelectedNumberStations> {count($station)} </SelectedNumberStations>
        {
            if ($level!="network") then
                for $station in $network/Station
            let $stationcode:=$station/@code
            let $stationstartDate := $station/@startDate
            let $stationendDate := $station/@endDate
            let $stationrestrictedStatus := $station/@restrictedStatus

        group by $stationcode, $stationstartDate, $stationendDate, $stationrestrictedStatus
        order by $stationcode, $stationstartDate
        return

                <Station>
                {$stationcode}
                {$stationstartDate}
                {$stationendDate}
                {$stationrestrictedStatus}
                {$station/ingv:AlternateNetworks}
                {$station/ingv:Identifier}
                {$station/Latitude}
                {$station/Longitude}
                {$station/Elevation}
                {$station/Site}
                {$station/CreationDate}
                {$station/TerminationDate}

                </Station>


            else
                ()
        }
        </Network>


(:}:)
(:    catch err:* {()}:)

};


(:TODO a livello network se la rete non è restricted anche se contenesse stazioni restricted, non interessa il livello station o inferiore
 : modifico  questa
 : da modificare ai livelli inferiori per non arrivare alla core se solo includerestricted=false:)
declare function stationutil:query_noradius_level_network($NSLCSE as map()*, $level as xs:string){
(:DEBUG:)
(:try{:)

    let $dlog := stationutil:debug("info", "query_noradius_level_network" )
    let $since:= xs:dateTime($NSLCSE("updatedafter"))
(:    let $dlog := util:log("info", "Collection:" || $stationutil:station_pruned_collection ):)

(: don't pass introducing [matches(ingv:AlternateNetworks/AlternateNetwork/@code,$NSLCSE("alternate_network_pattern"))]:)

        for $network in xmldb:find-last-modified-since(collection($stationutil:station_pruned_collection)
            //Network
            [ @code= $NSLCSE("network_sequence")]
            [Station[range:matches(@code, $NSLCSE("station_pattern"))]]
(:            [Station[matches(@code, $NSLCSE("station_pattern"))]]:)
            [stationutil:check_restricted($NSLCSE,@restrictedStatus)]
            /Station
(:            [@code= $NSLCSE("network_sequence")]:)
(:            /Station[matches(@code, $NSLCSE("station_pattern"))]:)
(:            [Latitude > xs:decimal($NSLCSE("minlatitude")) and Latitude < xs:decimal($NSLCSE("maxlatitude"))]:)
(:            [Longitude > xs:decimal($NSLCSE("minlongitude")) and Longitude < xs:decimal($NSLCSE("maxlongitude"))]:)
            [Latitude > $NSLCSE("minlatitude") and Latitude < $NSLCSE("maxlatitude")]
            [Longitude > $NSLCSE("minlongitude") and Longitude < $NSLCSE("maxlongitude")]


            [stationutil:check_restricted($NSLCSE,@restrictedStatus)]
            /Channel[matches(@code, $NSLCSE("channel_pattern"))]
            [matches(@locationCode, $NSLCSE("location_pattern"))]
            [(empty(@endDate)) or @endDate >= $NSLCSE("starttime")]
            [@startDate <= $NSLCSE("endtime") and @startDate < $NSLCSE("startbefore") and @startDate > $NSLCSE("startafter")]
            [ ($NSLCSE("endbefore") = $stationutil:defaults("future_time_as_datetime")) or @endDate < $NSLCSE("endbefore")]
            [(empty(@endDate)) or @endDate > $NSLCSE("endafter")]
            [stationutil:check_restricted($NSLCSE,@restrictedStatus)]
            /../.. ,$since) ,
            $condition in $NSLCSE
(:      let $dlog := if ($stationutil:enable_log) then util:log("info", " text" || $network/@code ) else ():)

      let $networkcode:=$network/@code
      let $startDate:=$network/@startDate
      let $endDate:=$network/@endDate
      let $sourceID:=$network/@sourceID
      let $restrictedStatus:=$network/@restrictedStatus
      let $alternateCode:=$network/@alternateCode
      let $historicalCode:=$network/@historicalCode
      let $Description:=$network/Description
      let $Identifier:=$network/Identifier
      let $firstidentifier:=$Identifier[1]
      let $IdentifierType:=$network/Identifier/@type
      let $ingvIdentifier:=$network/ingv:Identifier
      let $station:= $network/Station/@code

      group by $networkcode, $alternateCode, $sourceID, $historicalCode, $startDate, $endDate, $restrictedStatus, $Description,  $ingvIdentifier, $firstidentifier
      order by $networkcode, $startDate, $endDate

       return <Network>
            {$networkcode} {$startDate} {$endDate} {$sourceID} {$alternateCode} {$restrictedStatus} {$historicalCode}
            {$Description}

            {
                functx:distinct-deep(
                if ($Identifier/text() = distinct-values(for $d in $Identifier return $d))
                then $Identifier
                else ()//Identifier)

            }

        {$ingvIdentifier}
        <TotalNumberStations> {stationutil:stationcount($networkcode,$startDate,$endDate,$restrictedStatus)} </TotalNumberStations>
        <SelectedNumberStations> {count($station)} </SelectedNumberStations>
        </Network>

};



(:~ Works on station level when all but includerestricted=false and radius parameter are requested
 :
 : @param $NSLCSE
 : @param $level the response level
 : :)
declare function stationutil:query_noradius_includerestricted_level_station($NSLCSE as map()*, $level as xs:string){

    let $dlog := stationutil:debug("info", "query_noradius_includerestricted_level_station" )
    let $since:= xs:dateTime($NSLCSE("updatedafter"))

    for $network in xmldb:find-last-modified-since(collection($stationutil:station_pruned_collection)
        //Network
        [ @code= $NSLCSE("network_sequence")]
        [Station[range:matches(@code, $NSLCSE("station_pattern"))]]
(:        [Station[matches(@code, $NSLCSE("station_pattern"))]]:)
        /Station
(:        [Latitude > xs:decimal($NSLCSE("minlatitude")) and Latitude < xs:decimal($NSLCSE("maxlatitude"))]:)
(:        [Longitude > xs:decimal($NSLCSE("minlongitude")) and Longitude < xs:decimal($NSLCSE("maxlongitude"))]:)
        [Latitude > $NSLCSE("minlatitude") and Latitude < $NSLCSE("maxlatitude")]
        [Longitude > $NSLCSE("minlongitude") and Longitude < $NSLCSE("maxlongitude")]

        [Channel[matches(@code, $NSLCSE("channel_pattern"))]]
        /Channel[matches(@code, $NSLCSE("channel_pattern"))]
        [matches(@locationCode, $NSLCSE("location_pattern"))]
        [if (empty(@endDate)) then true() else @endDate >= $NSLCSE("starttime")]
        [@startDate <= $NSLCSE("endtime") and @startDate < $NSLCSE("startbefore") and @startDate > $NSLCSE("startafter")]
        [($NSLCSE("endbefore") = $stationutil:defaults("future_time_as_datetime")) or @endDate < $NSLCSE("endbefore")]
        [empty(@endDate) or @endDate > $NSLCSE("endafter") ]

        /../.. , $since)


        let $networkcode:=$network/@code
        let $startDate:=$network/@startDate
        let $endDate:=$network/@endDate
        let $sourceID:=$network/@sourceID
        let $restrictedStatus:=$network/@restrictedStatus
        let $alternateCode:=$network/@alternateCode
        let $historicalCode:=$network/@historicalCode
        let $Description:=$network/Description
        let $Identifier:=$network/Identifier
        let $firstidentifier:=$Identifier[1]
        let $IdentifierType:=$network/Identifier/@type
        let $ingvIdentifier:=$network/ingv:Identifier

        let $station := $network/Station

        group by $networkcode, $alternateCode, $sourceID, $historicalCode, $startDate, $endDate, $restrictedStatus, $Description,  $ingvIdentifier, $firstidentifier

        order by $networkcode ,$startDate, $endDate
        (:      return <Network> {$network/@code} </Network>):)
        (:      return distinct-values($network/@code)):)
        return <Network>
        {$networkcode} {$startDate} {$endDate} {$sourceID} {$restrictedStatus} {$alternateCode} {$historicalCode} {$Description}

        {
            functx:distinct-deep(
            if ($Identifier/text() = distinct-values(for $d in $Identifier return $d))
            then $Identifier
            else ()//Identifier)
        }

        {$ingvIdentifier}
        <TotalNumberStations> {stationutil:stationcount($networkcode,$startDate,$endDate, $restrictedStatus )} </TotalNumberStations>
        <SelectedNumberStations> {count($station/@code)} </SelectedNumberStations>
        {

        for $n in $network

        let $netcode:=$n/@code
        let $S:= $n/Station
        group by $netcode

        return
            for $station in $S
            let $stationcode:=$station/@code
            let $stationstartDate := $station/@startDate
            let $stationendDate := $station/@endDate
            let $stationrestrictedStatus := $station/@restrictedStatus

        group by $stationcode, $stationstartDate, $stationendDate
        order by $stationcode, $stationstartDate
        return
                <Station>
                {$stationcode}
                {$stationstartDate}
                {$stationendDate}
                {$stationrestrictedStatus}
                {$station/ingv:AlternateNetworks}
                {$station/ingv:Identifier}
                {$station/Latitude}
                {$station/Longitude}
                {$station/Elevation}
                {$station/Site}
                {$station/CreationDate}
                {$station/TerminationDate}
                </Station>
        }

        </Network>

};





(:~ Works on station level when all but radius parameter are requested
 :
 : @param $NSLCSE
 : @param $level the response level
 : :)
declare function stationutil:query_noradius_level_station($NSLCSE as map()*, $level as xs:string){

    let $dlog := stationutil:debug("info", "query_noradius_level_station" )
    let $since:= xs:dateTime($NSLCSE("updatedafter"))

    for $network in xmldb:find-last-modified-since(collection($stationutil:station_pruned_collection)
        //Network
        [ @code= $NSLCSE("network_sequence")]
        [Station[range:matches(@code, $NSLCSE("station_pattern"))]]
(:        [Station[matches(@code, $NSLCSE("station_pattern"))]]:)
        [stationutil:check_restricted($NSLCSE,@restrictedStatus)]
        /Station
(:        [Latitude > xs:decimal($NSLCSE("minlatitude")) and Latitude < xs:decimal($NSLCSE("maxlatitude"))]:)
(:        [Longitude > xs:decimal($NSLCSE("minlongitude")) and Longitude < xs:decimal($NSLCSE("maxlongitude"))]:)
        [Latitude > $NSLCSE("minlatitude") and Latitude < $NSLCSE("maxlatitude")]
        [Longitude > $NSLCSE("minlongitude") and Longitude < $NSLCSE("maxlongitude")]
        [Channel[matches(@code, $NSLCSE("channel_pattern"))]]
        [stationutil:check_restricted($NSLCSE,@restrictedStatus)]
        /Channel[matches(@code, $NSLCSE("channel_pattern"))]
        [matches(@locationCode, $NSLCSE("location_pattern"))]
        [if (empty(@endDate)) then true() else @endDate >= $NSLCSE("starttime")]
        [@startDate <= $NSLCSE("endtime") and @startDate < $NSLCSE("startbefore") and @startDate > $NSLCSE("startafter")]
        [($NSLCSE("endbefore") = $stationutil:defaults("future_time_as_datetime")) or @endDate < $NSLCSE("endbefore")]
        [empty(@endDate) or @endDate > $NSLCSE("endafter") ]

        /../.. , $since)


        let $networkcode:=$network/@code
        let $startDate:=$network/@startDate
        let $endDate:=$network/@endDate
        let $sourceID:=$network/@sourceID
        let $restrictedStatus:=$network/@restrictedStatus
        let $alternateCode:=$network/@alternateCode
        let $historicalCode:=$network/@historicalCode
        let $Description:=$network/Description
        let $Identifier:=$network/Identifier
        let $firstidentifier:=$Identifier[1]
        let $IdentifierType:=$network/Identifier/@type
        let $ingvIdentifier:=$network/ingv:Identifier

        let $station := $network/Station

        group by $networkcode, $alternateCode, $sourceID, $historicalCode, $startDate, $endDate, $restrictedStatus, $Description,  $ingvIdentifier, $firstidentifier

        order by $networkcode ,$startDate, $endDate
        (:      return <Network> {$network/@code} </Network>):)
        (:      return distinct-values($network/@code)):)
        return <Network>
        {$networkcode} {$startDate} {$endDate} {$sourceID} {$restrictedStatus} {$alternateCode} {$historicalCode} {$Description}

        {
            functx:distinct-deep(
            if ($Identifier/text() = distinct-values(for $d in $Identifier return $d))
            then $Identifier
            else ()//Identifier)
        }

        {$ingvIdentifier}
        <TotalNumberStations> {stationutil:stationcount($networkcode,$startDate,$endDate, $restrictedStatus )} </TotalNumberStations>
        <SelectedNumberStations> {count($station/@code)} </SelectedNumberStations>
        {

        for $n in $network

        let $netcode:=$n/@code
        let $S:= $n/Station
        group by $netcode

        return
            for $station in $S
            let $stationcode:=$station/@code
            let $stationstartDate := $station/@startDate
            let $stationendDate := $station/@endDate
            let $stationrestrictedStatus := $station/@restrictedStatus
        where
            stationutil:check_restricted($NSLCSE,$stationrestrictedStatus)
        group by $stationcode, $stationstartDate, $stationendDate
        order by $stationcode, $stationstartDate
        return
                <Station>
                {$stationcode}
                {$stationstartDate}
                {$stationendDate}
                {$stationrestrictedStatus}
                {$station/ingv:AlternateNetworks}
                {$station/ingv:Identifier}
                {$station/Latitude}
                {$station/Longitude}
                {$station/Elevation}
                {$station/Site}
                {$station/CreationDate}
                {$station/TerminationDate}
                </Station>
        }

        </Network>

};

(:~ Works on channel and response level when all but includerestricted=false and radius parameter are requested
 :
 : @param $NSLCSE
 : @param $level the response level
 : :)
(:TODO verify latitude and longitude match at the correct level:)
declare function stationutil:query_noradius_includerestricted_level_channel_response($NSLCSE as map()*, $level as xs:string){

    let $dlog := stationutil:debug("info", "query_noradius_includerestricted_level_channel_response" )
    let $since:= xs:dateTime($NSLCSE("updatedafter"))
    let $collection := if ($level="response") then $stationutil:station_collection else $stationutil:station_pruned_collection

    for $network in xmldb:find-last-modified-since(collection($collection)
        //Network
        [@code= $NSLCSE("network_sequence")]
        [Station[range:matches(@code, $NSLCSE("station_pattern"))]]
(:        [Station[matches(@code, $NSLCSE("station_pattern"))]]:)
        /Station
        [range:matches(@code, $NSLCSE("station_pattern"))]
        [Channel[@startDate <= $NSLCSE("endtime") and @startDate < $NSLCSE("startbefore") and @startDate > $NSLCSE("startafter")]]
        [Channel[($NSLCSE("endbefore") = $stationutil:defaults("future_time_as_datetime")) or @endDate < $NSLCSE("endbefore")]]
        [Channel[empty(@endDate) or @endDate >= $NSLCSE("starttime")]]
        [Channel[empty(@endDate) or @endDate > $NSLCSE("endafter")]]
        [Channel[matches(@code, $NSLCSE("channel_pattern"))]]
        /Channel
        [matches(@code, $NSLCSE("channel_pattern"))]
        [matches(@locationCode, $NSLCSE("location_pattern"))]
        [@startDate <= $NSLCSE("endtime") and @startDate < $NSLCSE("startbefore") and @startDate > $NSLCSE("startafter")]
        [($NSLCSE("endbefore") = $stationutil:defaults("future_time_as_datetime")) or @endDate < $NSLCSE("endbefore")]
        [empty(@endDate) or @endDate >= $NSLCSE("starttime")]
        [empty(@endDate) or @endDate > $NSLCSE("endafter")]
        [Latitude > $NSLCSE("minlatitude") and Latitude < $NSLCSE("maxlatitude")]
        [Longitude > $NSLCSE("minlongitude") and Longitude < $NSLCSE("maxlongitude")]
        /../.. , $since)


        let $networkcode:=$network/@code
        let $startDate:=$network/@startDate
        let $endDate:=$network/@endDate
        let $sourceID:=$network/@sourceID
        let $restrictedStatus:=$network/@restrictedStatus
        let $alternateCode:=$network/@alternateCode
        let $historicalCode:=$network/@historicalCode
        let $Description:=$network/Description
        let $Identifier:=$network/Identifier
        let $firstidentifier:=$Identifier[1]

        let $IdentifierType:=$network/Identifier/@type
        let $ingvIdentifier:=$network/ingv:Identifier

        let $station := $network/Station
        let $CreationDate := $network/Station/CreationDate
        let $stationcode:=$station/@code

        let $stationstartDate := $station/@startDate
        let $stationendDate := $station/@endDate
        let $stationrestrictedStatus := $station/@restrictedStatus

        group by $networkcode, $alternateCode, $sourceID, $historicalCode, $startDate, $endDate, $restrictedStatus, $Description,  $ingvIdentifier, $firstidentifier
        order by $networkcode, $startDate, $endDate

        return <Network>
        {$networkcode} {$startDate} {$endDate} {$sourceID} {$restrictedStatus} {$alternateCode} {$historicalCode} {$Description}

        {
            functx:distinct-deep(
            if ($Identifier/text() = distinct-values(for $d in $Identifier return $d))
            then $Identifier
            else ()//Identifier)

        }

        {$ingvIdentifier}
        <TotalNumberStations> {stationutil:stationcount($networkcode,$startDate,$endDate,$restrictedStatus)} </TotalNumberStations>
        <SelectedNumberStations> {count($station/@code)} </SelectedNumberStations>
        {

        for $n in $network
        let $netcode:=$n/@code
        let $S:= $n/Station

        for $station in $S
            let $stationcode:=$station/@code
            let $stationstartDate := $station/@startDate
            let $stationendDate := $station/@endDate
            let $stationrestrictedStatus := $station/@restrictedStatus

(:            let $dlog := util:log("info", "query_noradius_channel " || $netcode) :)
            let $latitude:=$station/@Latitude
            let $longitude:=$station/@Longitude
            let $channels:=$station/Channel
            let $selected_channels:=for $channel in $channels
                let $chacode:=$channel/@code
(:                let $logs:= for $p in $chacode return util:log("INFO","Channel " || $p)  :)
                let $locationcode:=$channel/@locationCode
                let $channelstartDate:=$channel/@startDate
                let $channelendDate:=(if (empty($channel/@endDate)) then $stationutil:defaults("future_time_as_datetime")  else $channel/@endDate )
                let $channelrestrictedStatus := $channel/@restrictedStatus
                where

                    matches($chacode, $NSLCSE("channel_pattern")) and
                    matches($locationcode, $NSLCSE("location_pattern"))
                    and ($channelendDate >= $NSLCSE("starttime")) (:Esclude i chiusi prima di starttime:)
                    and $channelstartDate <= $NSLCSE("endtime")   (:Esclude gli aperti dopo endtime:)
                    and $channelstartDate < $NSLCSE("startbefore")
                    and $channelstartDate > $NSLCSE("startafter")
                    and ( if ( $NSLCSE("endbefore") = $stationutil:defaults("future_time_as_datetime")) then true() else ($channelendDate < $NSLCSE("endbefore")))
                    and (($channelendDate > $NSLCSE("endafter"))  or  ($channelendDate=$stationutil:defaults("future_time")))
                    and stationutil:check_restricted($NSLCSE,$channelrestrictedStatus)

                return
                    $channel
        where
            stationutil:check_restricted($NSLCSE,$stationrestrictedStatus)
        group by $stationcode, $stationstartDate, $stationendDate
        order by $stationcode, $stationstartDate, $stationendDate
        return
                <Station>
                {$stationcode}
                {$stationstartDate}
                {$stationendDate}
                {$stationrestrictedStatus}
                {$station/ingv:AlternateNetworks}
                {$station/ingv:Identifier}
                {$station/Latitude}
                {$station/Longitude}
                {$station/Elevation}
                {$station/Site}
                {$station/CreationDate}
                {$station/TerminationDate}
                <TotalNumberChannels>
                    {count($station/Channel)}
                    </TotalNumberChannels>
                    <SelectedNumberChannels>
                    {count ($selected_channels)}
                    </SelectedNumberChannels>
                {$selected_channels}
                </Station>
        }

        </Network>

};


(:~ Works on channel and response level when includerestricted=false and radius parameter are requested
 :
 : @param $NSLCSE
 : @param $level the response level
 : :)
declare function stationutil:query_noradius_level_channel_response($NSLCSE as map()*, $level as xs:string){

    let $dlog := stationutil:debug("info", "query_noradius_level_channel_response" )
    let $since:= xs:dateTime($NSLCSE("updatedafter"))
    let $collection := if ($level="response") then $stationutil:station_collection else $stationutil:station_pruned_collection

    for $network in xmldb:find-last-modified-since(collection($collection)
        //Network
        [@code= $NSLCSE("network_sequence")]
        [Station[range:matches(@code, $NSLCSE("station_pattern"))]]
(:        [Station[matches(@code, $NSLCSE("station_pattern"))]]:)
        [stationutil:check_restricted($NSLCSE,@restrictedStatus)]
        /Station
        [range:matches(@code, $NSLCSE("station_pattern"))]
(:        [Latitude > xs:decimal($NSLCSE("minlatitude")) and Latitude < xs:decimal($NSLCSE("maxlatitude"))]:)
(:        [Longitude > xs:decimal($NSLCSE("minlongitude")) and Longitude < xs:decimal($NSLCSE("maxlongitude"))]:)
        [Latitude > $NSLCSE("minlatitude") and Latitude < $NSLCSE("maxlatitude")]
        [Longitude > $NSLCSE("minlongitude") and Longitude < $NSLCSE("maxlongitude")]
        [stationutil:check_restricted($NSLCSE,@restrictedStatus)]
        [Channel[matches(@code, $NSLCSE("channel_pattern"))]]
        [Channel[@startDate <= $NSLCSE("endtime") and @startDate < $NSLCSE("startbefore") and @startDate > $NSLCSE("startafter")]]
        [Channel[($NSLCSE("endbefore") = $stationutil:defaults("future_time_as_datetime")) or @endDate < $NSLCSE("endbefore")]]
        [Channel[empty(@endDate) or @endDate >= $NSLCSE("starttime")]]
        [Channel[empty(@endDate) or @endDate > $NSLCSE("endafter")]]
        /Channel
        [stationutil:check_restricted($NSLCSE,@restrictedStatus)]
        [matches(@code, $NSLCSE("channel_pattern"))]
        [matches(@locationCode, $NSLCSE("location_pattern"))]
        [@startDate <= $NSLCSE("endtime") and @startDate < $NSLCSE("startbefore") and @startDate > $NSLCSE("startafter")]
        [($NSLCSE("endbefore") = $stationutil:defaults("future_time_as_datetime")) or @endDate < $NSLCSE("endbefore")]
        [empty(@endDate) or @endDate >= $NSLCSE("starttime")]
        [empty(@endDate) or @endDate > $NSLCSE("endafter")]

        /../.. , $since)


        let $networkcode:=$network/@code
        let $startDate:=$network/@startDate
        let $endDate:=$network/@endDate
        let $sourceID:=$network/@sourceID
        let $restrictedStatus:=$network/@restrictedStatus
        let $alternateCode:=$network/@alternateCode
        let $historicalCode:=$network/@historicalCode
        let $Description:=$network/Description
        let $Identifier:=$network/Identifier
        let $firstidentifier:=$Identifier[1]
        let $IdentifierType:=$network/Identifier/@type
        let $ingvIdentifier:=$network/ingv:Identifier

        let $station := $network/Station
        let $CreationDate := $network/Station/CreationDate
        let $stationcode:=$station/@code

        let $stationstartDate := $station/@startDate
        let $stationendDate := $station/@endDate
        let $stationrestrictedStatus := $station/@restrictedStatus

        group by $networkcode, $alternateCode, $sourceID, $historicalCode, $startDate, $endDate, $restrictedStatus, $Description,  $ingvIdentifier, $firstidentifier
        order by $networkcode, $startDate, $endDate

        return <Network>
        {$networkcode} {$startDate} {$endDate} {$sourceID} {$restrictedStatus} {$alternateCode} {$historicalCode} {$Description}

        {
            functx:distinct-deep(
            if ($Identifier/text() = distinct-values(for $d in $Identifier return $d))
            then $Identifier
            else ()//Identifier)

        }

        {$ingvIdentifier}
        <TotalNumberStations> {stationutil:stationcount($networkcode,$startDate,$endDate,$restrictedStatus)} </TotalNumberStations>
        <SelectedNumberStations> {count($station/@code)} </SelectedNumberStations>
        {

        for $n in $network
        let $netcode:=$n/@code
        let $S:= $n/Station

        for $station in $S
            let $stationcode:=$station/@code
            let $stationstartDate := $station/@startDate
            let $stationendDate := $station/@endDate
            let $stationrestrictedStatus := $station/@restrictedStatus

(:            let $dlog := util:log("info", "query_noradius_channel " || $netcode) :)
            let $latitude:=$station/@Latitude
            let $longitude:=$station/@Longitude
            let $channels:=$station/Channel

            let $selected_channels:=for $channel in $channels
                let $chacode:=$channel/@code
(:                let $logs:= for $p in $chacode return util:log("INFO","Channel " || $p)  :)
                let $locationcode:=$channel/@locationCode
                let $channelstartDate:=$channel/@startDate
                let $channelendDate:=(if (empty($channel/@endDate)) then $stationutil:defaults("future_time_as_datetime")  else $channel/@endDate )
                where

                    matches($chacode, $NSLCSE("channel_pattern")) and
                    matches($locationcode, $NSLCSE("location_pattern"))
                    and ($channelendDate >= $NSLCSE("starttime")) (:Esclude i chiusi prima di starttime:)
                    and $channelstartDate <= $NSLCSE("endtime")   (:Esclude gli aperti dopo endtime:)
                    and $channelstartDate < $NSLCSE("startbefore")
                    and $channelstartDate > $NSLCSE("startafter")
                    and ( if ( $NSLCSE("endbefore") = $stationutil:defaults("future_time_as_datetime")) then true() else ($channelendDate < $NSLCSE("endbefore")))
                    and (($channelendDate > $NSLCSE("endafter"))  or  ($channelendDate=$stationutil:defaults("future_time")))

                return
                    $channel
        group by $stationcode, $stationstartDate, $stationendDate
        order by $stationcode, $stationstartDate, $stationendDate
        return
                <Station>
                {$stationcode}
                {$stationstartDate}
                {$stationendDate}
                {$stationrestrictedStatus}
                {$station/ingv:AlternateNetworks}
                {$station/ingv:Identifier}
                {$station/Latitude}
                {$station/Longitude}
                {$station/Elevation}
                {$station/Site}
                {$station/CreationDate}
                {$station/TerminationDate}
                <TotalNumberChannels>
                    {count($station/Channel)}
                    </TotalNumberChannels>
                    <SelectedNumberChannels>
                    {count ($selected_channels)}
                    </SelectedNumberChannels>
                {$selected_channels}
                </Station>
        }

        </Network>

};






declare function stationutil:query_core($NSLCSE as map()*, $level as xs:string){
(:DEBUG:)
(:try{:)

    let $dlog := stationutil:debug("info", "query_core" )

(:Prepare the output, discarding it only when sure no channels meet criteria avoid to check before, then create output:)
(:let $xml := :)

(:    DONE updatedafter ( :)
    let $since:= xs:dateTime($NSLCSE("updatedafter"))

    let $upper:= min( ((xs:decimal($NSLCSE("latitude")) + xs:decimal($NSLCSE("maxradius")) + xs:decimal(0.25)), xs:decimal($NSLCSE("maxlatitude")) ))
    let $lower:= max((xs:decimal($NSLCSE("latitude")) - xs:decimal($NSLCSE("maxradius")) - xs:decimal(0.25), xs:decimal($NSLCSE("minlatitude"))))
    let $left := max((xs:decimal($NSLCSE("longitude")) - xs:decimal($NSLCSE("maxradius")) - xs:decimal(0.25),xs:decimal($NSLCSE("minlongitude"))))
    let $right:= min((xs:decimal($NSLCSE("longitude")) + xs:decimal($NSLCSE("maxradius")) + xs:decimal(0.25),xs:decimal($NSLCSE("maxlongitude"))))

    let $collection := if ($level="response") then $stationutil:station_collection else $stationutil:station_pruned_collection

(: TODO approximate checkradius with a box limited search :)
(:    for $network in xmldb:find-last-modified-since(collection($collection)//Network[matches(@code, $NSLCSE("network_pattern"))]/Station[matches(@code, $NSLCSE("station_pattern"))]:)
    for $network in xmldb:find-last-modified-since(collection($collection)
        //Network
        [@code= $NSLCSE("network_sequence")]
        [Station[range:matches(@code, $NSLCSE("station_pattern"))]]
(:        [Station[range:matches(@code, "@|#")]]:)
(:        [Station[matches(@code, $NSLCSE("station_pattern"))]]:)
        [stationutil:check_restricted($NSLCSE,@restrictedStatus)]
        /Station
(:        /Station[matches(@code, $NSLCSE("station_pattern"))]:)
        [stationutil:check_radius($NSLCSE, Latitude, Longitude)]
        [Latitude  > $lower and Latitude  < $upper]
        [Longitude > $left  and Longitude < $right]
        [stationutil:check_restricted($NSLCSE,@restrictedStatus)]
        /Channel
        [stationutil:constraints_onchannel( $NSLCSE, @startDate, @endDate ) ]
        [matches(@code, $NSLCSE("channel_pattern"))]
        [matches(@locationCode, $NSLCSE("location_pattern"))]
        [@startDate <= $NSLCSE("endtime")]
        [(empty(@endDate)) or @endDate >= $NSLCSE("starttime")]
        [@startDate < $NSLCSE("startbefore") and @startDate > $NSLCSE("startafter")]
        [stationutil:check_restricted($NSLCSE,@restrictedStatus)]
        [Latitude  > $lower and Latitude  < $upper]
        [Longitude > $left  and Longitude < $right]

        /../.. ,$since) , $condition in $NSLCSE

    let $minlatitude := $condition("minlatitude")
    let $maxlatitude := $condition("maxlatitude")
    let $minlongitude := $condition("minlongitude")
    let $maxlongitude := $condition("maxlongitude")

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
    let $sourceID:=$network/@sourceID
    let $restrictedStatus:=$network/@restrictedStatus
    let $alternateCode:=$network/@alternateCode
    let $historicalCode:=$network/@historicalCode

    let $stationrestrictedStatus:=$network/Station/@restrictedStatus
    let $channelrestrictedStatus:=$network//Channel/@restrictedStatus
    let $Description := $network/Description
    let $Identifier := $network/Identifier
    let $firstidentifier := $Identifier[1]
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
        where

            (count ($channels)>0)
        group by $stationcode, $stationstartDate, $stationendDate, $stationrestrictedStatus

        return
                    $stationcode

        }
    )

    where

        (count($stations)>0)
        group by $networkcode, $alternateCode, $sourceID, $historicalCode, $startDate, $endDate, $restrictedStatus, $Description, $network_ingv_identifier, $firstidentifier
        order by $networkcode, $startDate, $endDate


    return

        <Network>
        {$networkcode}
        {$startDate}
        {$endDate}
        {$sourceID} {$restrictedStatus} {$alternateCode} {$historicalCode}
        {$Description}
        {functx:distinct-deep($Identifier)}
        {functx:distinct-deep($network/*[(name() != "Station") and (name() != "TotalNumberStations") and (name() != "SelectedNumberStations") and (name() != "Description") and (name() !="Identifier") and (name() != "ingv:Identifier") ])}
        {$network_ingv_identifier}
        <TotalNumberStations> {stationutil:stationcount($networkcode,$startDate,$endDate, $restrictedStatus )} </TotalNumberStations>

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
            let $lat := $station/Latitude
            let $lon := $station/Longitude
            let $CreationDate:= $channel/@startDate
            let $TerminationDate := $channel/@endDate
(:            let $log := util:log("info", "stations: "):)
            let $selected_channels:= (
                for $channel in $channels
                let $CreationDate:= $channel/@startDate
(:                let $TerminationDate:= $channel/@endDate:)
                let $TerminationDate := if (empty($channel/@endDate)) then $stationutil:defaults("future_time_as_datetime") else $channel/@endDate
(:                let $log := util:log("info", "channels: "):)
                where

                    (
                        ((($NSLCSE("endtime") >= $CreationDate)  and  ($NSLCSE("starttime") <= $TerminationDate))) and
                        (($CreationDate < $NSLCSE("startbefore"))) and
                        (($CreationDate > $NSLCSE("startafter"))) and
                        (($NSLCSE("endbefore")=$stationutil:defaults("future_time_as_datetime")) or ($TerminationDate < $NSLCSE("endbefore"))) and
                        (($NSLCSE("endafter")=$stationutil:defaults("past_time_as_datetime"))  or ($TerminationDate > $NSLCSE("endafter")))
                    )

                return

                         $channel

            )
(:            let $channelcount:=count ($selected_channels):)
        where (count ($selected_channels)>0)
        group by $stationcode, $stationstartDate, $stationendDate, $stationrestrictedStatus
        order by $stationcode, $stationstartDate
        return

                <Station>
                {$stationcode}
                {$stationstartDate}
                {$stationendDate}
                {$stationrestrictedStatus}
                {$station/ingv:AlternateNetworks}
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



declare function stationutil:query_core_virtual_network($NSLCSE as map()*, $level as xs:string){
(:DEBUG:)
(:try{:)
    let $dlog := stationutil:debug("info", "query_core_virtual_network: " || " ALT: "|| $NSLCSE("alternate_network_pattern") || " NET: " || $NSLCSE("network_pattern"))

(:Prepare the output, discarding it only when sure no channels meet criteria avoid to check before, then create output:)
(:let $xml := :)

(:    DONE updatedafter ( :)
    let $since:= xs:dateTime($NSLCSE("updatedafter"))
    let $collection := if ($level="response") then $stationutil:station_collection else $stationutil:station_pruned_collection

    for $network in xmldb:find-last-modified-since(collection($collection)
    //Network[(@code= $NSLCSE("network_sequence")) or matches(Station/ingv:AlternateNetworks/ingv:AlternateNetwork/@code,$NSLCSE("alternate_network_pattern"))]
    /Station
    [range:matches(@code, $NSLCSE("station_pattern"))]
(:    [Latitude > xs:decimal($NSLCSE("minlatitude"))]:)
(:    [Latitude < xs:decimal($NSLCSE("maxlatitude"))]:)
(:    [Longitude > xs:decimal($NSLCSE("minlongitude"))]:)
(:    [Longitude < xs:decimal($NSLCSE("maxlongitude"))]:)
    [Latitude > $NSLCSE("minlatitude") ][Latitude < $NSLCSE("maxlatitude")]
    [Longitude > $NSLCSE("minlongitude") ][Longitude < $NSLCSE("maxlongitude")]
    /Channel
    [matches(@code, $NSLCSE("channel_pattern"))]
    [matches(@locationCode, $NSLCSE("location_pattern"))]
    [@startDate <= $NSLCSE("endtime")]
    [if (empty(@endDate)) then true() else @endDate >= $NSLCSE("starttime")][@startDate < $NSLCSE("startbefore")][@startDate > $NSLCSE("startafter")]/../.. ,$since) , $condition in $NSLCSE

    let $minlatitude := $condition("minlatitude")
    let $maxlatitude := $condition("maxlatitude")
    let $minlongitude := $condition("minlongitude")
    let $maxlongitude := $condition("maxlongitude")

    let $Latitude:= $network/Station/Latitude
    let $Longitude:= $network/Station/Longitude
    let $CreationDate:= $network//Channel/@startDate
(:    let $TerminationDate:= $network//Channel/@endDate:)
    let $TerminationDate:= if (empty($network//Channel/@endDate)) then $stationutil:defaults("future_time_as_datetime")  else $network//Channel/@endDate

    let $networkcode := $network/@code
    let $startDate := $network/@startDate
    let $endDate := $network/@endDate
    let $sourceID:=$network/@sourceID
    let $restrictedStatus:=$network/@restrictedStatus
    let $alternateCode:=$network/@alternateCode
    let $historicalCode:=$network/@historicalCode

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

    let $stationrestrictedStatus:=$network/Station/@restrictedStatus
    let $channelrestrictedStatus:=$network//Channel/@restrictedStatus
    let $Description := $network/Description
    let $Identifier := $network/Identifier
    let $firstidentifier := $Identifier[1]
    let $network_ingv_identifier := $network/ingv:Identifier
    let $log:=stationutil:debug("info",$networkcode ||  " " || $startDate || " " || $endDate || " " ||  $restrictedStatus )
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
                    stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and
                    stationutil:check_radius($condition, $lat,$lon) and
                    stationutil:check_restricted($condition,$channelrestrictedStatus)
                return
                         $channel

            )
(:            let $channelcount:=count ($selected_channels):)
        where
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
        stationutil:check_radius($condition, $lat,$lon) and
        stationutil:check_restricted($condition,$restrictedStatus) and
        stationutil:check_restricted($condition,$stationrestrictedStatus) and
        stationutil:check_restricted($condition,$channelrestrictedStatus) and
        stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate )
        and
        (count($stations)>0)
        group by $networkcode, $alternateCode, $sourceID, $historicalCode, $startDate, $endDate, $restrictedStatus, $Description, $network_ingv_identifier, $firstidentifier
        order by $networkcode, $startDate, $endDate

    return

        <Network>
        {$networkcode}
        {$startDate}
        {$endDate}
        {$sourceID} {$restrictedStatus} {$alternateCode} {$historicalCode}
        {$Description}
        {functx:distinct-deep($Identifier)}
        {functx:distinct-deep($network/*[(name() != "Station") and (name() != "TotalNumberStations") and (name() != "SelectedNumberStations") and (name() != "Description") and (name() !="Identifier") and (name() != "ingv:Identifier") ])}
        {$network_ingv_identifier}
        <TotalNumberStations> {stationutil:stationcount($networkcode,$startDate,$endDate,$restrictedStatus)} </TotalNumberStations>
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
            matches($channelcode, $NSLCSE("channel_pattern")) and
            matches($locationcode, $NSLCSE("location_pattern")) and
            stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and
            stationutil:check_radius($condition, $lat,$lon) and
            stationutil:check_restricted($condition,$stationrestrictedStatus)
(:            and ($channelcount>0):)
            and (count ($selected_channels)>0)
        group by $stationcode, $stationstartDate, $stationendDate, $stationrestrictedStatus
        order by $stationcode, $stationstartDate
        return

                <Station>
                {$stationcode}
                {$stationstartDate}
                {$stationendDate}
                {$stationrestrictedStatus}
                {$station/ingv:AlternateNetworks}
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
declare function stationutil:query_core_virtual_network_POST($NSLCSE as map()*, $level as xs:string){
(:try{:)
(:DEBUG:)
    let $dlog := stationutil:debug("info", "query_core_virtual_network_POST" )

(:    DONE updatedafter is a unique parameter value:)
    let $since := $NSLCSE[1]("updatedafter")
    let $proxystart := min($stationutil:starttimes)
    let $proxyend := max($stationutil:endtimes)


    let $collection := if ($level="response") then $stationutil:station_collection else $stationutil:station_pruned_collection
(:    let $collection := if ($level="response") then $stationutil:station_collection else $stationutil:station_pruned_collection:)

    for $network in xmldb:find-last-modified-since(collection($collection)//
    Network
    [matches(@code, $stationutil:networks_pattern) or matches(Station/ingv:AlternateNetworks/ingv:AlternateNetwork/@code,$stationutil:alternate_networks)]
    /Station
    [@startDate <= $proxyend and ((empty(@endDate)) or @endDate >= $proxystart)]
    [matches(@code, $stationutil:stations_pattern)]
    /Channel
    [@startDate <= $proxyend and ((empty(@endDate)) or @endDate >= $proxystart) ]
    [matches(@code,$stationutil:channels_pattern)]
    /../..


    ,$since)
    , $condition in $NSLCSE

    let $minlatitude := $condition("minlatitude")
    let $maxlatitude := $condition("maxlatitude")
    let $minlongitude := $condition("minlongitude")
    let $maxlongitude := $condition("maxlongitude")

    let $Latitude:= $network/Station/Latitude
    let $Longitude:= $network/Station/Longitude
    let $CreationDate:= $network/Station/Channel/@startDate
    let $TerminationDate:= if ($network/Station/Channel/@endDate) then $network/Station/Channel/@endDate else $stationutil:defaults("future_time_as_datetime")
    let $networkcode := $network/@code
    let $station:=$network//Station
    let $stationcode:=$station/@code
    let $alternatenetworkcode:=
        if ($station/ingv:AlternateNetworks/ingv:AlternateNetwork/@code) then $station/ingv:AlternateNetworks/ingv:AlternateNetwork/@code else "FSDN"

    let $lat := $station/Latitude
    let $lon := $station/Longitude
    let $channel:=$station/Channel
    let $channelcode:=$channel/@code
    let $locationcode:=$channel/@locationCode
    let $startDate := $network/@startDate
    let $endDate := $network/@endDate
    let $sourceID:=$network/@sourceID
    let $restrictedStatus:=$network/@restrictedStatus
    let $alternateCode:=$network/@alternateCode
    let $historicalCode:=$network/@historicalCode
    let $stationrestrictedStatus:=$network/Station/@restrictedStatus
    let $channelrestrictedStatus:=$network//Channel/@restrictedStatus
    let $Description := $network/Description
    let $Identifier := $network/Identifier
    let $firstidentifier := $Identifier[1]
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
            let $alternatenetworkcode:=
                if ($station/ingv:AlternateNetworks/ingv:AlternateNetwork/@code) then $station/ingv:AlternateNetworks/ingv:AlternateNetwork/@code else "FSDN"
            let $selected_channels:=
                for $channel in $channels
                let $channelcode:=$channel/@code
                let $locationcode:=$channel/@locationCode
                let $channelrestrictedStatus := $channel/@restrictedStatus
                let $CreationDate:= $channel/@startDate
                let $TerminationDate:= $channel/@endDate

                where
                    (matches($networkcode, $condition("network_pattern")) or matches("VIRTUAL",$condition("network_pattern") ) ) and
                    (matches($alternatenetworkcode, $condition("alternate_network_pattern")) or matches("FSDN",$condition("alternate_network_pattern") ) ) and
                    matches($channelcode, $condition("channel_pattern")) and
                    matches($locationcode,$condition("location_pattern")) and

                    stationutil:check_radius($condition, $lat,$lon) and
                    stationutil:check_restricted($condition,$channelrestrictedStatus) and
                    stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate )
                    group by $channel
                return
                         $channel
        where
            $Latitude  > $minlatitude and
            $Latitude  < $maxlatitude and
            $Longitude > $minlongitude and
            $Longitude < $maxlongitude and
            (matches($networkcode, $condition("network_pattern")) or matches("VIRTUAL",$condition("network_pattern") ) ) and
            (matches($alternatenetworkcode, $condition("alternate_network_pattern")) or matches("FSDN",$condition("alternate_network_pattern") ) ) and
            matches($stationcode, $condition("station_pattern")) and
            matches($channelcode, $condition("channel_pattern")) and
            matches($locationcode,$condition("location_pattern")) and
(: VIRTUAL           stationutil:constraints_onchannel_patterns( $condition, $networkcode, $stationcode, $channelcode, $locationcode)  and:)

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
                {$station/ingv:AlternateNetworks}
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
                    $selected_channels
                )
                else
                    ()
                }
                </Station>
            )
    where
    (:        {functx:distinct-deep($Identifier)}        :)
        $Latitude  > $minlatitude and
        $Latitude  < $maxlatitude and
        $Longitude > $minlongitude and
        $Longitude < $maxlongitude and

        (matches($networkcode, $condition("network_pattern")) or matches("VIRTUAL",$condition("network_pattern") ) )
        and
        (matches($alternatenetworkcode, $condition("alternate_network_pattern")) or matches("FSDN",$condition("alternate_network_pattern") ) )
        and


        matches($stationcode, $condition("station_pattern")) and
        matches($channelcode, $condition("channel_pattern")) and
        matches($locationcode,$condition("location_pattern")) and
        stationutil:check_radius($condition, $lat,$lon) and
        stationutil:check_restricted($condition,$restrictedStatus) and
        stationutil:check_restricted($condition,$stationrestrictedStatus) and
        stationutil:check_restricted($condition,$channelrestrictedStatus) and
        stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and
        (count($stations)>0)
        group by $networkcode, $alternateCode, $sourceID, $historicalCode, $startDate, $endDate, $restrictedStatus, $Description, $network_ingv_identifier, $firstidentifier
(:        , $Identifier:)
        order by $networkcode, $startDate, $endDate

    return

        <Network>
        {$networkcode}
        {$startDate}
        {$endDate}
        {$sourceID} {$restrictedStatus} {$alternateCode} {$historicalCode}
        {$Description}
        {functx:distinct-deep($Identifier)}
        {$network_ingv_identifier}
        <TotalNumberStations> {stationutil:stationcount($networkcode,$startDate,$endDate, $restrictedStatus )} </TotalNumberStations>
        <SelectedNumberStations> {count(distinct-values($stations))} </SelectedNumberStations>
        {
            if ($level!="network") then
        (:  Coming from many rows there could be duplicates , removing here before output    :)
(:            let $log:=util:log("info", "Level: " || $level):)
            let $distinct_sta :=
                for $sta in $stations
                    group by $stacode := $sta//Network/@code
                return
                    functx:distinct-deep($sta)
            return
(:                fn:sort($distinct_sta,(), function($distinct_sta) {$distinct_sta/@code}):)
                $distinct_sta
(:                $stations:)
            else
                ()
        }
        </Network>

(:return     $xml:)

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
(:try{:)
(:DEBUG:)
    let $dlog := stationutil:debug("info", "query_core_POST" )

(:    DONE updatedafter is a unique parameter value:)
    let $since := $NSLCSE[1]("updatedafter")
    let $proxystart := min($stationutil:starttimes)
    let $proxyend := max($stationutil:endtimes)


    let $collection := if ($level="response") then $stationutil:station_collection else $stationutil:station_pruned_collection
(:    let $collection := if ($level="response") then $stationutil:station_collection else $stationutil:station_pruned_collection:)

    for $network in xmldb:find-last-modified-since(collection($collection)//
    Network
    [matches(@code, $stationutil:networks_pattern)]
(:    [Station[matches(@code, $stationutil:stations_pattern)]]:)
    [Station[range:matches(@code, $stationutil:stations_pattern)]]
    /Station
    [@startDate <= $proxyend and ((empty(@endDate)) or @endDate >= $proxystart)]
    /Channel
    [matches(@code,$stationutil:channels_pattern)]
    [@startDate <= $proxyend and ((empty(@endDate)) or @endDate >= $proxystart) ]

    /../..

(:    Faster using RANGE index because of matches function inefficiency for NEW RANGE:)
(:      Network:)
(:    [matches(@code, $stationutil:networks_pattern)]:)
(:    [Station [matches(@code, $stationutil:stations_pattern)]]:)
(:    [Station [Channel[matches(@code,$stationutil:channels_pattern)]]]:)
(:    [Station [@startDate <= $proxyend and ((empty(@endDate)) or @endDate >= $proxystart)]]:)
(:    [Station [Channel[@startDate <= $proxyend and ((empty(@endDate)) or @endDate >= $proxystart)]]]:)


    ,$since)
    , $condition in $NSLCSE

    let $minlatitude := $condition("minlatitude")
    let $maxlatitude := $condition("maxlatitude")
    let $minlongitude := $condition("minlongitude")
    let $maxlongitude := $condition("maxlongitude")

    let $Latitude:= $network/Station/Latitude
    let $Longitude:= $network/Station/Longitude
    let $CreationDate:= $network/Station/Channel/@startDate
(:    let $TerminationDate:= $network/Station/Channel/@endDate:)
    let $TerminationDate:= if ($network/Station/Channel/@endDate) then $network/Station/Channel/@endDate else $stationutil:defaults("future_time_as_datetime")
    let $networkcode := $network/@code
    let $station:=$network//Station
    let $stationcode:=$station/@code
(:    let $alternatenetworkcode:=$station/ingv:AlternateNetworks/AlternateNetwork/@code:)
    let $alternatenetworkcode:=
        if ($station/ingv:AlternateNetworks/ingv:AlternateNetwork/@code) then $station/ingv:AlternateNetworks/ingv:AlternateNetwork/@code else "FSDN"

    let $lat := $station/Latitude
    let $lon := $station/Longitude
    let $channel:=$station/Channel
    let $channelcode:=$channel/@code
    let $locationcode:=$channel/@locationCode
    let $startDate := $network/@startDate
    let $endDate := $network/@endDate
    let $sourceID:=$network/@sourceID
    let $restrictedStatus:=$network/@restrictedStatus
    let $alternateCode:=$network/@alternateCode
    let $historicalCode:=$network/@historicalCode

    let $stationrestrictedStatus:=$network/Station/@restrictedStatus
    let $channelrestrictedStatus:=$network//Channel/@restrictedStatus
    let $Description := $network/Description
    let $Identifier := $network/Identifier
    let $firstidentifier := $Identifier[1]
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
            let $alternatenetworkcode:=
                if ($station/ingv:AlternateNetworks/ingv:AlternateNetwork/@code) then $station/ingv:AlternateNetworks/ingv:AlternateNetwork/@code else "FSDN"
(:            let $log := util:log("info", "stations: "):)
            let $selected_channels:=
                for $channel in $channels
                let $channelcode:=$channel/@code
                let $locationcode:=$channel/@locationCode
                let $channelrestrictedStatus := $channel/@restrictedStatus
                let $CreationDate:= $channel/@startDate
                let $TerminationDate:= $channel/@endDate

                where
                    (matches($networkcode, $condition("network_pattern")) or matches("VIRTUAL",$condition("network_pattern") ) ) and
                    (matches($alternatenetworkcode, $condition("alternate_network_pattern")) or matches("FSDN",$condition("alternate_network_pattern") ) ) and
                    matches($channelcode, $condition("channel_pattern")) and
                    matches($locationcode,$condition("location_pattern")) and

                    stationutil:check_radius($condition, $lat,$lon) and
                    stationutil:check_restricted($condition,$channelrestrictedStatus) and
                    stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate )
                    group by $channel
                return
                         $channel
        where
            $Latitude  > $minlatitude and
            $Latitude  < $maxlatitude and
            $Longitude > $minlongitude and
            $Longitude < $maxlongitude and
            (matches($networkcode, $condition("network_pattern")) or matches("VIRTUAL",$condition("network_pattern") ) ) and
            (matches($alternatenetworkcode, $condition("alternate_network_pattern")) or matches("FSDN",$condition("alternate_network_pattern") ) ) and
            matches($stationcode, $condition("station_pattern")) and
            matches($channelcode, $condition("channel_pattern")) and
            matches($locationcode,$condition("location_pattern")) and
(: VIRTUAL           stationutil:constraints_onchannel_patterns( $condition, $networkcode, $stationcode, $channelcode, $locationcode)  and:)

            stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and
            stationutil:check_radius($condition, $lat,$lon) and
            stationutil:check_restricted($condition,$stationrestrictedStatus)
(:            and ($channelcount>0):)
            and (count ($selected_channels)>0)
        group by $stationcode, $stationstartDate, $stationendDate, $stationrestrictedStatus
        order by $stationcode, $stationstartDate
        return

                <Station>
                {$stationcode}
                {$stationstartDate}
                {$stationendDate}
                {$stationrestrictedStatus}
                {$station/ingv:AlternateNetworks}
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
                    $selected_channels
                )
                else
                    ()
                }
                </Station>
            )
    where
    (:        {functx:distinct-deep($Identifier)}        :)
        $Latitude  > $minlatitude and
        $Latitude  < $maxlatitude and
        $Longitude > $minlongitude and
        $Longitude < $maxlongitude and

        (matches($networkcode, $condition("network_pattern")) or matches("VIRTUAL",$condition("network_pattern") ) )
        and
        (matches($alternatenetworkcode, $condition("alternate_network_pattern")) or matches("FSDN",$condition("alternate_network_pattern") ) )
        and


        matches($stationcode, $condition("station_pattern")) and
        matches($channelcode, $condition("channel_pattern")) and
        matches($locationcode,$condition("location_pattern")) and
        stationutil:check_radius($condition, $lat,$lon) and
        stationutil:check_restricted($condition,$restrictedStatus) and
        stationutil:check_restricted($condition,$stationrestrictedStatus) and
        stationutil:check_restricted($condition,$channelrestrictedStatus) and
        stationutil:constraints_onchannel( $condition, $CreationDate, $TerminationDate ) and
        (count($stations)>0)
        group by $networkcode, $alternateCode, $sourceID, $historicalCode, $startDate, $endDate, $restrictedStatus, $Description, $network_ingv_identifier, $firstidentifier
(:        , $Identifier:)
        order by $networkcode, $startDate, $endDate

    return

        <Network>
        {$networkcode}
        {$startDate}
        {$endDate}
        {$sourceID} {$restrictedStatus} {$alternateCode} {$historicalCode}
        {$Description}
        {functx:distinct-deep($Identifier)}
        {$network_ingv_identifier}
        <TotalNumberStations> {stationutil:stationcount($networkcode,$startDate,$endDate, $restrictedStatus )} </TotalNumberStations>
        <SelectedNumberStations> {count(distinct-values($stations))} </SelectedNumberStations>
        {
            if ($level!="network") then
        (:  Coming from many rows there could be duplicates , removing here before output    :)
(:            let $log:=util:log("info", "Level: " || $level):)
            let $distinct_sta :=
                for $sta in $stations
                    group by $stacode := $sta//Network/@code
                return
                    functx:distinct-deep($sta)
            return
                (: slow and safe reordering do not rely on database order  :)
                fn:sort($distinct_sta,(), function($distinct_sta) {$distinct_sta/@code})

(:                $distinct_sta:)
(:                $stations:)
            else
                ()
        }
        </Network>

(:return     $xml:)

(:}:)
(:    catch err:* {()}:)

};




(:~
 :  @return the <network> Station XML fragment given the $NSLCSE map of query parameters, found in the current collection.
 :  Simplified to treat only the network and station parameter case, without other arguments
 :
 : @param $NSLCSE
 :)
(:  The query_core_channel_shortcut is two times fast :)
declare function stationutil:query_core_channel_response_shortcut($NSLCSE as map()*){
(:DEBUG:)
(:try{:)

    let $dlog := stationutil:debug("info", "query_core_channel_response_shortcut" )
    let $level := $NSLCSE("level")
    let $since:= xs:dateTime($NSLCSE("updatedafter"))
    let $collection := if ($level="response") then $stationutil:station_collection else $stationutil:station_pruned_collection
(:    for $network in collection($stationutil:station_collection)//Network:)
    for $network in collection($collection)
    //Network
    [ @code= $NSLCSE("network_sequence")]
    [Station[range:matches(@code, $NSLCSE("station_pattern"))]]
(:    [@code= $NSLCSE("network_sequence")]/Station[matches(@code, $NSLCSE("station_pattern"))]/..:)
(:    , $condition in $NSLCSE  :)


    let $networkcode := $network/@code
    let $station:=$network//Station
    let $stationcode:=$station/@code

    (:TODO use $startDate,  $endDate?:)
    let $startDate := $network/@startDate
    let $endDate := $network/@endDate
    let $sourceID:=$network/@sourceID
    let $restrictedStatus:=$network/@restrictedStatus
    let $alternateCode:=$network/@alternateCode
    let $historicalCode:=$network/@historicalCode
    let $stationrestrictedStatus:=$network/Station/@restrictedStatus
    let $Description := $network/Description
    let $Identifier := $network/Identifier
    let $firstidentifier := $Identifier[1]
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

(:            let $log := util:log("info", "stations: "):)
            let $selected_channels:= (
                for $channel in $channels
                where
                    matches($stationcode, $NSLCSE("station_pattern")) and
                    ($networkcode = $NSLCSE("network_sequence"))
                return
                         $channel
            )
(:            let $channelcount:=count ($selected_channels):)
        where

            matches($stationcode, $NSLCSE("station_pattern")) and
            ($networkcode = $NSLCSE("network_sequence")) and
            (count ($selected_channels)>0)
(:  FIX ODC problem with identifier in dataset FIXME          :)
(:        group by $networkcode,  $startDate, $endDate, $restrictedStatus, $Description, $network_ingv_identifier, $Identifier:)
        group by $stationcode, $stationstartDate, $stationendDate, $stationrestrictedStatus
        order by $stationcode, $stationstartDate
        return

                <Station>
                {$stationcode}
                </Station>

    )

(:  TODO replace it again                  {$channelcount} :)
    where

        matches($stationcode, $NSLCSE("station_pattern")) and
        ($networkcode = $NSLCSE("network_sequence"))
        and
        (count($stations)>0)

        group by $networkcode, $alternateCode, $sourceID, $historicalCode, $startDate, $endDate, $restrictedStatus, $Description, $network_ingv_identifier, $firstidentifier
        order by $networkcode, $startDate, $endDate
    return

        <Network>
        {$networkcode}
        {$startDate}
        {$endDate}
        {$sourceID} {$restrictedStatus} {$alternateCode} {$historicalCode}
        {$Description}
        {functx:distinct-deep($Identifier)}
        {$network_ingv_identifier}

        <TotalNumberStations> {stationutil:stationcount($networkcode,$startDate,$endDate, $restrictedStatus )} </TotalNumberStations>
        <SelectedNumberStations> {count($stations)} </SelectedNumberStations>
        {
            if ($level!="network") then

                for $station in $network/Station
                    let $stationcode:=$station/@code
                    let $stationstartDate := $station/@startDate
                    let $stationendDate := $station/@endDate
                    let $stationrestrictedStatus := $station/@restrictedStatus
                    let $channels:=$station//Channel


(:            let $log := util:log("info", "stations: "):)
                    let $selected_channels:= (
                        for $channel in $channels
                        where
                            matches($stationcode, $NSLCSE("station_pattern")) and
                            ($networkcode = $NSLCSE("network_sequence"))
                        return
                             if ($level="channel") then (
                                 stationutil:remove-elements($channel,"Stage")
                                 )
                             else
                                 $channel
                    )
        (:            let $channelcount:=count ($selected_channels):)
                where

                    matches($stationcode, $NSLCSE("station_pattern")) and
                    ($networkcode = $NSLCSE("network_sequence")) and
                    (count ($selected_channels)>0)
                group by $stationcode, $stationstartDate, $stationendDate, $stationrestrictedStatus
                order by $stationcode, $stationstartDate
                return
                <Station>
                {$stationcode}
                {$stationstartDate}
                {$stationendDate}
                {$stationrestrictedStatus}
                {$station/ingv:AlternateNetworks}
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
 :  @return the <network> Station XML fragment given the $NSLCSE map of query parameters, found in the current collection.
 :  Simplified to treat only the network and station parameter case, without other arguments
 :
 : @param $NSLCSE
 :)
declare function stationutil:query_core_channel_shortcut($NSLCSE as map()*){
(:DEBUG:)
(:try{:)

    let $dlog := stationutil:debug("info", "query_core_channel_shortcut" )
    let $level := $NSLCSE("level")
    let $since:= xs:dateTime($NSLCSE("updatedafter"))
    let $collection := if ($level="response") then $stationutil:station_collection else $stationutil:station_pruned_collection
    for $network in collection($collection)
        //Network
        [@code= $NSLCSE("network_sequence")]
        [Station[range:matches(@code, $NSLCSE("station_pattern"))]]
(:        [Station[matches(@code, $NSLCSE("station_pattern"))]]:)
(:        [@code= $NSLCSE("network_sequence")]/Station[matches(@code, $NSLCSE("station_pattern"))]/..:)

        let $networkcode := $network/@code
        let $station:=$network//Station
        let $stationcode:=$station/@code

        (:TODO use $startDate,  $endDate?:)
        let $startDate := $network/@startDate
        let $endDate := $network/@endDate
        let $sourceID:=$network/@sourceID
        let $restrictedStatus:=$network/@restrictedStatus
        let $alternateCode:=$network/@alternateCode
        let $historicalCode:=$network/@historicalCode
        let $stationrestrictedStatus:=$network/Station/@restrictedStatus
    (:    let $channelrestrictedStatus:=$network//Channel/@restrictedStatus    :)
        let $Description := $network/Description
        let $Identifier := $network/Identifier
        let $firstidentifier := $Identifier[1]
        let $network_ingv_identifier := $network/ingv:Identifier

        let $stations:=
        (
            for $station in $network/Station
                let $stationcode:=$station/@code
                let $stationstartDate := $station/@startDate
                let $stationendDate := $station/@endDate
                let $stationrestrictedStatus := $station/@restrictedStatus
                let $channels:=$station//Channel
            where

                matches($stationcode, $NSLCSE("station_pattern")) and
                ($networkcode = $NSLCSE("network_sequence")) and
                (count ($channels)>0)
    (:  FIX ODC problem with identifier in dataset FIXME          :)
    (:        group by $networkcode,  $startDate, $endDate, $restrictedStatus, $Description, $network_ingv_identifier, $Identifier:)
            group by $stationcode, $stationstartDate, $stationendDate, $stationrestrictedStatus
            order by $stationcode
            return

                    <Station>
                    {$stationcode}
                    </Station>
        )

        where

            matches($stationcode, $NSLCSE("station_pattern")) and
            ($networkcode = $NSLCSE("network_sequence"))
            and
            (count($stations)>0)
            group by $networkcode, $alternateCode, $sourceID, $historicalCode, $startDate, $endDate, $restrictedStatus, $Description, $network_ingv_identifier, $firstidentifier
            order by $networkcode, $startDate, $endDate
        return

            <Network>
            {$networkcode}
            {$startDate}
            {$endDate}
            {$sourceID} {$restrictedStatus} {$alternateCode} {$historicalCode}
            {$Description}
            {functx:distinct-deep($Identifier)}
            {$network_ingv_identifier}

            <TotalNumberStations> {stationutil:stationcount($networkcode,$startDate,$endDate, $restrictedStatus )} </TotalNumberStations>
            <SelectedNumberStations> {count($stations)} </SelectedNumberStations>
            {

             for $station in $network/Station
                let $stationcode:=$station/@code
                let $stationstartDate := $station/@startDate
                let $stationendDate := $station/@endDate
                let $stationrestrictedStatus := $station/@restrictedStatus
                let $channels:=$station//Channel
            where

                matches($stationcode, $NSLCSE("station_pattern")) and
                ($networkcode = $NSLCSE("network_sequence")) and
                (count ($channels)>0)
            group by $stationcode, $stationstartDate, $stationendDate, $stationrestrictedStatus
            order by $stationcode, $stationstartDate
            return
                    <Station>
                    {$stationcode}
                    {$stationstartDate}
                    {$stationendDate}
                    {$stationrestrictedStatus}
                    {$station/ingv:AlternateNetworks}
                    {$station/ingv:Identifier}
                    {$station/Latitude}
                    {$station/Longitude}
                    {$station/Elevation}
                    {$station/Site}
                    {$station/CreationDate}
                    {$station/TerminationDate}
                    {
                        <TotalNumberChannels>
                        {count($station/Channel)}
                        </TotalNumberChannels>,
                        <SelectedNumberChannels>
                        {count ($channels)}
                        </SelectedNumberChannels>,
                        $channels

                    }
                    </Station>

            }
            </Network>
(:}:)
(:    catch err:* {()}:)

};



declare function stationutil:query_core_single_station($NSLCSE as map()*){
(:DEBUG:)
(:try{:)

    let $dlog := stationutil:debug("info", "query_core_single_station" )
    let $level := $NSLCSE("level")
    let $since:= xs:dateTime($NSLCSE("updatedafter"))
    let $collection := if ($level="response") then $stationutil:station_collection else $stationutil:station_pruned_collection
(: match are the channels :)
    for $match in collection($collection)
(:    //Station[@code = $NSLCSE("station")]:)
(:    /Channel/.:)
    //Network[@code= $NSLCSE("network_sequence")][Station[@code = $NSLCSE("station")]]
    //Channel/.

    let $networkcode:=$match/../../@code
    let $startDate:=$match/../../@startDate
    let $endDate:=$match/../../@endDate
    let $alternateCode:=$match/../../@alternateCode
    let $sourceID:=$match/../../@sourceID
    let $historicalCode:=$match/../../@historicalCode

    let $restrictedStatus:=$match/../../@restrictedStatus

    let $stationcode:=$match/../@code

    group by $networkcode, $alternateCode, $sourceID, $historicalCode, $startDate, $endDate, $restrictedStatus, $stationcode
    order by $networkcode, $startDate, $endDate, $stationcode


return


    <Network>{$match/../../@*}
        {
        $match/../../*
        [name()!="Station"][name()!="TotalNumberStations"][name()!="SelectedNumberStations"][name()!="Channel"]
        }

        <TotalNumberStations> {stationutil:stationcount($networkcode, $startDate, $endDate, $restrictedStatus)} </TotalNumberStations>
        <SelectedNumberStations>{stationutil:stationcount($networkcode, $startDate, $endDate, $restrictedStatus)}</SelectedNumberStations>

        {
         for $code in $stationcode
         let $dlog := stationutil:debug("info", "station " || $code )
         return

            $match/..

        }

    </Network>


};




declare function stationutil:query_all_network(){
    let $dlog := stationutil:debug("info", "query_all_network" )
    return doc($stationutil:netcache_collection||"/net.xml")//Network
};


(:QUERIES SECTION END:)

(: PUT management:)

(: Take care of unit conversion for 1.2 recommendation :)
(:V/M -> V/m OK:)
(:M/S  -> m/s OK :)
(:M/S**2 -> m/s**2 OK :)
(:M -> m TODO:)
(:V:)
(:A:)
(:COUNTS -> count OK :)
(:V/V:)
(:Hz/V:)
(:V/Hz:)
(:V/(M/S) -> V/(m/s) OK :)
(:COUNTS/V -> count/V OK :)
(:V/(M/S**2)  -> V/(m/s**2) OK:)
(:Hz:)
(:UNKNOWN:)
(:RADIANS/S -> rad/s TODO :)
declare function  stationutil:units_1.2($element as element()) as element() {
   element {node-name($element)}
      {$element/@*,
          for $child in $element/node()
              return
               if ($child instance of element())
                 then
                    if ($child/name() eq "Name"  and ($child/../name() eq "InputUnits" or $child/../name() eq "OutputUnits" ))
                     then
                        (: only M/S and COUNTS fixed :)
                        element {node-name($child)} { replace(replace(replace($child/text(),"M/S","m/s"),"COUNTS","count"),"V/M","V/m") }
                     else
                     stationutil:units_1.2($child)
                 else
                         $child
      }
};

(:mimics functx:remove-attributes-deep:)
declare function stationutil:change-dates-deep
  ( $nodes as node()* ,
    $names as xs:string* )  as node()* {

   for $node in $nodes
   return if ($node instance of element())
          then  element { node-name($node)}
                {
                    (:RAN    css30:netType nor a valid attribute name           :)
                    try {
(:                    let $log:= if (matches(node-name($node), "Network")) then util:log("info", "Examining " || node-name($node)) else ():)
                    for $attribute in $node/@*

                    let $found-attribute-name := name($attribute)
                    let $found-attribute-value := string($attribute)
                    return
                       if ($found-attribute-name = $names )
                       then attribute {$found-attribute-name} { fn:adjust-dateTime-to-timezone(xs:dateTime($found-attribute-value),())}
                       else attribute {$found-attribute-name} {$found-attribute-value}
                    }
                    catch err:* {
                        $node/@*
                    }
                    ,  stationutil:change-dates-deep($node/node(), $names)

                }
          else if ($node instance of document-node())
          then stationutil:change-dates-deep($node/node(), $names)
          else $node
 } ;



declare function stationutil:put()
{
try {
    (:Explicitly passed the filename in a custom http header  :)
    let $filename := request:get-header('filename')
    let $log:=util:log("info", "Request to insert " || $filename)

    let $decoded :=
    if ($stationutil:settings("translate_units")) then
        let $content := request:get-data()
        let $decoded := util:base64-decode($content)
        (: management of changes in input for 1.2  :)
        let $xml := fn:parse-xml($decoded)
        let $modified_xml := stationutil:units_1.2($xml//FDSNStationXML)

    return
        if($stationutil:settings("remove_tz")) then
            fn:serialize(stationutil:change-dates-deep($modified_xml,("startDate","endDate")))
        else
            fn:serialize($modified_xml)


(: TODO END :)
    else
        let $content := request:get-data()
        return util:base64-decode($content)



    let $stored:= stationutil:real_put($decoded ,$filename)
    return $stored
    }
     catch err:* {
        let $log:=util:log("info", "Caught error " || $err:code || " " || $err:description)
        return ()
    }
};


declare function stationutil:delete()
{
    let $filename := request:get-header('filename')
    let $is_in_station := fn:doc-available($stationutil:station_collection||"/"||$filename)
(:    let $log := if ($is_in_station) then util:log("info", $filename ||  "available" ) else util:log("info", $filename ||  " not available" ) :)
    let $do:=(
        if ($is_in_station) then
        (
            let $remove :=  xmldb:remove($stationutil:station_collection, $filename)
            let $remove :=  xmldb:remove($stationutil:station_pruned_collection, $filename)
            let $update := stationutil:netcache_create()
            let $log := stationutil:log("info", "Deleted station " || $filename )
            return $remove
        )
(:response 404    :)
    else
        (
            stationutil:log("info","Missing station " || $filename || ", not deleted" ), stationutil:nodata_error()
        )
    )
    return ()
};


declare function stationutil:delete_selected()
{
    let $net := request:get-parameter("net", "")
    let $provider:= request:get-parameter("provider", "")
    let $pattern:= replace( $net, "\*", ".*")

    let $cycle:= for $doc in collection($stationutil:station_collection)
         let $filename :=util:document-name($doc)
         let $log:=stationutil:log("info","Filename: " || $filename)
         let $log := stationutil:log("info", "Deleted station " || $filename )
         where
         fn:matches($filename,"^"||$provider)
         and
         fn:matches($doc//Network/@code, "^" || $net || "$")
        return
            xmldb:remove($stationutil:station_collection, $filename)

    let $cycle:= for $doc in collection($stationutil:station_pruned_collection)
         let $filename :=util:document-name($doc)
         let $log:=stationutil:log("info","Filename: " || $filename)
         let $log := stationutil:log("info", "Deleted station " || $filename )
         where
         fn:matches($filename,"^"||$provider)
         and
         fn:matches($doc//Network/@code, "^" || $net || "$")
        return
            xmldb:remove($stationutil:station_pruned_collection, $filename)

    let $cache_created := stationutil:netcache_create()
    return ()
};

(:"CACHE" management:)

declare function stationutil:real_put($decoded as xs:string, $filename as xs:string){

(: create the second resource then store them together, update cache in the end :)
     let $station := fn:parse-xml($decoded)
     let $netcode := $station//Network/@code
     let $station_periods := count($station//Station/@startDate)
     let $startDate := $station//Network/@startDate
(:     let $log:=stationutil:log("info", "Found code: "|| count($netcode)):)
     let $pruned:=stationutil:remove-multi( $station//FDSNStationXML,"Stage")
     let $stored:=(
     try {
        (:Possible more than a netcode in a station file:)
        let $alreadyindb:=doc-available($stationutil:station_collection||$filename)
        let $store1:=xmldb:store($stationutil:station_collection, $filename, $decoded)
        let $store2:=xmldb:store($stationutil:station_pruned_collection, $filename, $pruned)

        let $todo :=
        (
            if (count($netcode)>1)
        then
(:            let $log:=stationutil:log("info", "More than a network, creating cache") return :)
            stationutil:netcache_create()
        else
        (
            for $net in $netcode
            let $net_in_cache := stationutil:netcache_exists($net,$station//Network[@code=$net]/@startDate)
            let $cached :=
                if ( $net_in_cache and $alreadyindb and count($netcode)=1) then
                    (: Do nothing if updating a simple station belonging to a single network :)
                    let $log:=stationutil:debug("info", "Nothing to change in cache") return
                    ()
                else
                    if ($net_in_cache and not($alreadyindb) and count($netcode)=1)
                    then
                        (:Update the current net count inserting a new simple station belonging to a single network:)
(:                        let $log:=stationutil:log("info", "Do update")  return :)
                            stationutil:netcache_update($station, $net, $station_periods)
                    else
                        (: new net create cache :)
(:                        let $log:=stationutil:log("info", "Create cache") return :)
                            stationutil:netcache_create()
        return ()
        )

        )

        let $log := stationutil:log("info", "Inserted station " || $filename )
        return ()
     }
     catch err:* {

          let $log := stationutil:log("error", "Error inserting station " || $filename )
          let $error := stationutil:internal_error($err:code || " " || $err:description )
          return ()
     }
     )
     return
         $stored
};


declare function stationutil:prune_station($station as item(), $filename as xs:string){

     let $pruned:=stationutil:remove-multi( $station//FDSNStationXML,"Stage")
     (: Get same creation time :)
     let $copied := xmldb:copy-resource($stationutil:station_collection, $filename, $stationutil:station_pruned_collection, $filename, true())
     let $creation-time := xmldb:created($stationutil:station_collection, $filename)
     let $modification-time := xmldb:last-modified($stationutil:station_collection, $filename)
     let $delay := xs:dayTimeDuration('PT0.2S')
     let $stored:=(
     try {
(:         let $touched := xmldb:touch($stationutil:station_pruned_collection, $filename, $creation-time+$delay):)
         let $store:=xmldb:store($stationutil:station_pruned_collection, $filename, $pruned)
         (:  $pruned-creation-time is the time of creation, inherited from station collection file , not used      :)
         let $pruned-creation-time := xmldb:created($stationutil:station_pruned_collection, $filename)
         (:Need a minimal delay for deleted resources? Need to touch otherwise modification time is when pruned:)
         let $touched := xmldb:touch($stationutil:station_pruned_collection, $filename, $modification-time+$delay)
(:         let $log := stationutil:debug("info", "Pruned station " || $filename || " stored in " || $store || " at " || $modification-time + $delay || " original creation time " || $creation-time || " creation time of pruned station " || $pruned-creation-time ):)

         return ()
     }
     catch err:* {
          let $log := stationutil:log("error", "Error pruning station " || $filename )
          let $log := stationutil:log("error", "Caught error " || $err:code || " " || $err:description)
          return ()
     }
     )
     return
         $stored

};


declare function stationutil:netcache_update($station as item(), $currentcode as xs:string,  $sign as xs:double) as xs:boolean {
    let $log:=stationutil:debug("INFO", "netcache update " || $currentcode)
    let $document:=$station
    (:find $nets which $station belongs (for this file put) :)
    let $nets:=(
        for $n in $document//Network
        let $netcode:= $n/@code
(:        let $log:=util:log("INFO", "netcache update " || $currentcode):)
        return $netcode)
    let $xml:= doc($stationutil:netcache_collection||"/net.xml")
    let $netfile :=
        (
(: Two FLOWR because of err:XQTY0024 :)
     for $network in $xml//Network
            let $netcode:=$network/@code
        where $currentcode!=$netcode
        return $network

        ,
    for $network in $xml//Network
            let $netcode:=$network/@code
            let $startDate:=$network/@startDate
            let $endDate:=$network/@endDate
            let $sourceID:=$network/@sourceID
            let $restrictedStatus:=$network/@restrictedStatus
            let $alternateCode:=$network/@alternateCode
            let $historicalCode:=$network/@historicalCode
            let $Description:=$network/Description
            let $Identifier := $network/Identifier
            let $firstidentifier := $Identifier[1]
            let $ingvIdentifier:=$network/ingv:Identifier
(:            let $log:=stationutil:log("info", $Description[1]):)
            (: Only for networks of the station passed updates the number  :)
            let $tn:=$network/TotalNumberStations
(:            let $tns:=xs:double(xs:double($tn/text)+$sign):)
            let $tns:=xs:double($tn+$sign)

        where $currentcode=$netcode
        group by $netcode, $alternateCode, $sourceID, $historicalCode, $startDate, $endDate, $restrictedStatus, $Description, $ingvIdentifier, $firstidentifier
        order by $netcode, $startDate, $endDate
        return <Network>{$netcode} {$startDate} {$endDate} {$sourceID} {$restrictedStatus} {$alternateCode} {$historicalCode}
        {$Description}
        {functx:distinct-deep($Identifier)} {$ingvIdentifier}
        <TotalNumberStations>{$tns}</TotalNumberStations>
        <SelectedNumberStations>{$tns}</SelectedNumberStations>
        </Network>
   )
   let $sorted-file := for $network in $netfile
                            let $netcode:=$network/@code
                            let $startDate:=$network/@startDate
                            let $endDate:=$network/@endDate
                       order by $netcode, $startDate, $endDate
     return $network
    let $netfile:=<FDSNStationXML>{$sorted-file}</FDSNStationXML>

    let $store := xmldb:store( $stationutil:netcache_collection,"net.xml",$netfile )
    return not(empty($store))

} ;

declare function stationutil:netcache_create() as xs:string {
    let $log:=stationutil:debug("INFO", "netcache create ")
    let $xml:=
        for $network in collection($stationutil:station_collection)//Network/@*/..

            let $netcode:=$network/@code
            let $startDate:=$network/@startDate
            let $endDate:=$network/@endDate
            let $sourceID:=$network/@sourceID
            let $restrictedStatus:=$network/@restrictedStatus
            let $alternateCode:=$network/@alternateCode
            let $historicalCode:=$network/@historicalCode
            let $Description:=$network/Description
            let $Identifier := $network/Identifier
            let $firstidentifier := $Identifier[1]
            let $ingvIdentifier := $network/ingv:Identifier
            let $station := $network/Station
        group by $netcode, $alternateCode, $sourceID, $historicalCode, $startDate, $endDate, $restrictedStatus, $Description, $ingvIdentifier, $firstidentifier
(:        order by $netcode, $station[1]/@code[1]:)
        order by $netcode, $startDate, $endDate

        return
            <Network>
            {$netcode} {$startDate} {$endDate} {$sourceID} {$restrictedStatus} {$alternateCode} {$historicalCode} {$Description}
            {functx:distinct-deep($Identifier)} {$ingvIdentifier}
            <TotalNumberStations> {count( $station)} </TotalNumberStations>
            <SelectedNumberStations> {count( $station)} </SelectedNumberStations>
            </Network>

    let $netfile:= <FDSNStationXML>{$xml}</FDSNStationXML>
    let $store:=xmldb:store( $stationutil:netcache_collection,"net.xml",$netfile )

    return $netfile

};


declare function stationutil:netcache_exists($netcode as xs:string*, $startDate as xs:string*) as xs:boolean{
  let $docavailable:=doc-available($stationutil:netcache_collection||"/net.xml")
  let $xml:= if ( $docavailable ) then doc($stationutil:netcache_collection||"/net.xml") else ()
  let $netfile := if ($xml=())
    then ()
    else
    (
        for $network in $xml//Network[@code=$netcode][@startDate=xs:dateTime($startDate)]
            let $code:=$network/@code
        return string-join($code)
    )

  return exists($netfile)

};


(:  for each station file in station_collection, prune the file, put it in station_pruned_collection, in the end update netcache:)
declare function stationutil:fix_collections()  {
   try {

   let $fix_document:= (
       for $doc in collection($stationutil:station_collection)
         let $filename :=util:document-name($doc)
         let $log:=util:log("info","Filename: " || $filename)
         let $fixed:=stationutil:prune_station($doc, $filename)
        return ())
    let $cache_created := stationutil:netcache_create()
    return ()
   }
    catch err:* {
          let $log := stationutil:log("error", "Pruning failed" )
          return ()
     }
};


(:  for each resource in netcache, station, station_collection,change creation time:)
declare function stationutil:touch_collections()  {
   try {

   let $fix_document:= (
       for $collection in ( $stationutil:station_collection, $stationutil:station_pruned_collection, $stationutil:netcache_collection)
       for $doc in collection($collection)
         let $filename :=util:document-name($doc)
         let $touched:=xmldb:touch($collection, $filename, fn:current-dateTime())
(:         let $log:=util:log("info","Filename: " || $filename):)
        return ())

    return ()
   }
    catch err:* {
          let $log := stationutil:log("error", "Touching failed" )
          return ()
     }
};


declare function stationutil:purge() {
(:  empties collections Station, StationPruned, NetCache  :)
 xmldb:remove($stationutil:netcache_collection),
 xmldb:remove($stationutil:station_collection),
 xmldb:remove($stationutil:station_pruned_collection),
 xmldb:create-collection($stationutil:data_collection, "Station"),
 xmldb:create-collection($stationutil:data_collection, "StationPruned"),
 xmldb:create-collection($stationutil:data_collection, "NetCache")

};

