xquery version "3.1";

module namespace errors="http://exist-db.org/apps/fdsn-station/modules/errors";

import module namespace request = "http://exist-db.org/xquery/request";
declare default element namespace "http://www.fdsn.org/xml/station/1" ;
(:declare namespace ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";:)
declare option exist:serialize "method=html5 media-type=text/html";

(: Functions declarations  :)
(: TODO remove the file:)

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