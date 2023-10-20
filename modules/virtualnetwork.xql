xquery version "3.1";


declare namespace ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";
import module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil"  at "util.xql";
(:declare default element namespace "https://raw.githubusercontent.com/FDSN/StationXML/master" ;:)
declare default element namespace "https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" ;
(:declare namespace station="http://www.fdsn.org/xml/station/1" ;:)

declare namespace request="http://exist-db.org/xquery/request";
declare namespace output = "http://www.w3.org/2010/xslt-xquery-serialization";
declare namespace local = "http://local";
declare option output:method "xml";
declare option output:media-type "text/xml";
(:TODO uncomment after debug:)
declare option output:indent "no";
declare option output:omit-xml-declaration "no";



declare function local:alternatenetwork() {

let $xml:=for $alternate_network in collection($stationutil:station_collection)//AlternateNetwork

group by $alternate_network
order by $alternate_network/@code

return $alternate_network[1]

return <ingv:AlternateNetworks>{$xml}</ingv:AlternateNetworks>


};


declare function local:badrequest_error() {
    (: declare output method locally to override default xml   :)
    util:declare-option("exist:serialize","method=text media-type=text/plain indent=no")  ,
     response:set-status-code(400) ,
     "Error 400: Bad request

Syntax Error in Request

"
};

if ( request:get-method() eq "GET") then
     local:alternatenetwork()
 else
     local:badrequest_error()
