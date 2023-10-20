xquery version "3.1";


import module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil"  at "util.xql";
import module namespace request = "http://exist-db.org/xquery/request";
declare default element namespace "http://www.fdsn.org/xml/station/1" ;
(:declare namespace ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";:)
declare option exist:serialize "method=html5 media-type=text/html";


(:let $log:=util:log("info",request:get-uri()):)
(:return:)
stationutil:other_error()
