xquery version "3.1";

declare default element namespace "http://www.fdsn.org/xml/station/1" ;
declare namespace ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";
import module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil"  at "util.xql";

declare namespace request="http://exist-db.org/xquery/request";
declare namespace output = "http://www.w3.org/2010/xslt-xquery-serialization";
declare option output:method "xml";
declare option output:media-type "text/xml";
(:TODO uncomment after debug:)
declare option output:indent "yes";



(:declare function local:main_text(){:)
(:        util:declare-option("exist:serialize","method=text media-type=text/plain indent=yes") ,:)
(:        transform:transform(stationutil:query_channel_main(), doc("channel.xsl"), ()):)
(:};    :)

(: check request and create params accordingly choose functions to match POST syntax  :)
(: TODO change functions to adapt to POST  :)
    
(:try {:)
(:if (request:get-method() eq "GET" or request:get-method() eq "POST" )  then :)
    stationutil:run()

(:}:)
(:catch err:* {"Error checking parameters"}:)

