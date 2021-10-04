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
declare option output:omit-xml-declaration "no";


if ( request:get-method() eq "POST" or request:get-method() eq "GET") then 
     stationutil:run()
     
 else

     let $content := request:get-data()
     let $decoded := util:base64-decode($content)
(:Hardly get filenames:)
(:     let $filename2 := util:binary-to-string(request:get-uploaded-file-name('file')) :)
(:     let $filename1 := util:base64-decode(request:get-uploaded-file-name('filename')):)
(:Explicitly pass the filename in a custom http header           :)
(:     let $station := request:get-parameter("station", "AAA") || ".xml":)
     let $filename := request:get-header('filename')
                        
                    

     return
         
         xmldb:store("/db/apps/fdsn-station/Station/", $filename, $decoded)

     
(: TODO: verify permissions, verify the xml, extract station name, store the file,  try versioningtrigger pag 428 Siegel...   :)         
(: Next line store the file in station as is !!!!!       :)
        
     
(:        ,        xmldb:store("/db/apps/fdsn-station/Station/", $filename1, $content):)
        
(: 
 This lines for testing purposes
 
 time curl -X PUT "http://127.0.0.1:8080/exist/apps/fdsn-station/query/?level=response&net=*&format=xml&nodata=404" -H  "accept: application/xml" -H  "Content-Type: text/plain" -H  "accept: application/xml" -H  "Content-Type: text/xml" --data-binary @ACER.xml -o output.xml
 
 time curl -T "Station/CP02.xml" "http://127.0.0.1:80/exist/apps/fdsn-station/query/?level=response&net=*&format=xml&nodata=404" -H  "accept: application/xml" -H  "Content-Type: text/plain" -o output.xml
 
 Place the file
 Use a header to get control on filename:
 time curl -X PUT "http://127.0.0.1:80/exist/apps/fdsn-station/query/?level=response&net=*&format=xml&nodata=404" -H  "accept: application/xml" -H  "Content-Type: text/plain" -H  "accept: application/xml" -H  "Content-Type: text/xml" --data-binary @Station/MNS.xml  -H "file: MNS.xml" -o output.xml

 
 
:)
    

