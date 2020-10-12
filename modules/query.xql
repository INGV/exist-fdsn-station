xquery version "3.1";

declare default element namespace "http://www.fdsn.org/xml/station/1" ;
declare namespace ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";
import module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil"  at "util.xql";

declare namespace request="http://exist-db.org/xquery/request";
declare namespace output = "http://www.w3.org/2010/xslt-xquery-serialization";
declare option output:method "xml";
declare option output:media-type "text/xml";
(:TODO uncomment after debug:)
declare option output:indent "no";


if ( request:get-method() eq "POST" or request:get-method() eq "GET") then 
     stationutil:run()
 else
     
     let $content := request:get-data()
     let $decoded := util:base64-decode($content)
(: TODO: verify permissions, verify the xml, extract station name, store the file,  try versioningtrigger pag 428 Siegel...   :)
     
     return
         
(: Next line store the file in station as is !!!!!       :)
        xmldb:store("/db/apps/fdsn-station/Station/", "ACER.XML", $content)
        
(: 
 This line for testing purposes
 time curl -X PUT "http://127.0.0.1:8080/exist/apps/fdsn-station/query/?level=response&net=*&format=xml&nodata=404" -H  "accept: application/xml" -H  "Content-Type: text/plain" -H  "accept: application/xml" -H  "Content-Type: text/xml" --data-binary @ACER.xml -o output.xml
:)
    