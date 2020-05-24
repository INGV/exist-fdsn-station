xquery version "3.1";

module namespace errors="http://exist-db.org/apps/fdsn-station/modules/errors";

import module namespace request = "http://exist-db.org/xquery/request";
declare default element namespace "http://www.fdsn.org/xml/station/1" ;
declare namespace ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";
(:declare namespace functx = "http://www.functx.com";:)
(:declare namespace stationutil="http://exist-db.org/apps/fdsn-station/modules";:)
(:import module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil"  at "util.xql";:)

(:declare namespace request="http://exist-db.org/xquery/request";:)
(:declare namespace output = "http://www.w3.org/2010/xslt-xquery-serialization";:)
(: Serialization cannot change during the same request no way to fix using another file like in util.xql :)
declare option exist:serialize "method=html5 media-type=text/html";

(:declare option output:method "html5";:)
(:declare option output:media-type "text/html";:)


(: Functions declarations  :)


declare function errors:nodata_error() {
util:declare-option("exist:serialize","method=html media-type=text/html indent=no")  ,  
    (
    if (matches(request:get-parameter("nodata", "204"),"404")) 
    then
        (
            response:set-status-code(404) , transform:transform(<Error>Error 404 - no matching inventory found</Error>, doc("error-translation.xsl"), ())
              
        )
    else if (matches(request:get-parameter("nodata", "204"),"204")) then
        response:set-status-code(204) 
    else 
        response:set-status-code(400) 
    )    
};


(:locationCode:)