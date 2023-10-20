xquery version "3.1";

declare default element namespace "http://www.fdsn.org/xml/station/1" ;
declare namespace ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";
declare namespace request="http://exist-db.org/xquery/request";
declare namespace output = "http://www.w3.org/2010/xslt-xquery-serialization";
declare option output:method "xml";
declare option output:media-type "text/xml";
(:TODO uncomment after debug:)
declare option output:indent "no";
declare option output:omit-xml-declaration "no";

import module namespace login="http://exist-db.org/xquery/login" at "resource:org/exist/xquery/modules/persistentlogin/login.xql";
import module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil"  at "util.xql";
(:import module namespace config = "http://exist-db.org/xquery/apps/config" at "modules/config.xqm";:)



let $log:= if ($stationutil:settings("enable_query_log")) then util:log("info",  stationutil:get_caller() || " [" || request:get-method() || "] "  || request:get-query-string() || " [START]") else ()


return
try {
    let $user:=sm:id()
    let $log:=if ($user!="guestguest") then util:log("info", "User: " || $user  ) else ()
    return
    (
    if ( request:get-method() eq "POST" or request:get-method() eq "GET") then
        stationutil:run() 
     else
        if ( request:get-method() eq "PUT") then
            if ($user="fdsndba") then stationutil:put() else stationutil:other_error()
        else
            if ( request:get-method() eq "DELETE" and (request:get-parameter("net","None") = "None")) then
             if ($user="fdsndba") then stationutil:delete() else stationutil:other_error()
            else 
                if ( $user="fdsndba" and request:get-method() eq "DELETE" and (request:get-parameter("net","None") != "None")) then
                    stationutil:delete_selected()
                else  stationutil:other_error()
    ,if ($stationutil:settings("enable_query_log")) then util:log("info",  stationutil:get_caller() || " [" || request:get-method() || "] " || request:get-query-string() || " [END]" ) else ()
    )           
                
    }
catch err:* {
     let $error := stationutil:internal_error($err:code || " " || $err:description )
     return $error || "
" || $err:code || " " || $err:description
}

(: TODO:  verify the xml,  try versioningtrigger :)


(:
 This lines for testing purposes:

  Use a header to get control on filename:

 EXAMPLE TO PUT:
 curl -X PUT "http://172.17.0.2:8080/exist/apps/fdsn-station/fdsnws/station/1/query?" -H  "accept: application/xml"  -H "Content-Type: application/octet-stream" -H "Expect:" -H "filename: INGV_ABSI.xml"  --data-binary @Station/INGV_ABSI.xml -o output.xml -i -v -uadmin:

 EXAMPLE TO DELETE:
 curl -v  -H "Content-Type: text/plain"  -H "accept: application/xml" -H "filename: GIZZ.xml" -o output.xml -X DELETE "http://172.17.0.2:8080/exist/apps/fdsn-station/query/?"

 EXAMPLE TO POST:
 curl -X POST "http://172.17.0.2:8080/exist/apps/fdsn-station/fdsnws/station/1/query" -H  "Content-Type: application/octet-stream" --data-binary @test-post-request.txt -o error.txt -H  "accept: application/xml" --trace-ascii /dev/stdout

:)


