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



declare function local:main_text(){
        util:declare-option("exist:serialize","method=text media-type=text/plain indent=yes") ,
        transform:transform(stationutil:query_channel_main(), doc("channel.xsl"), ())
};    

(:  TODO check request and create params accordingly choose functions to match POST syntax  :)
    
try {
if (stationutil:get-parameter("format")="xml")  then 
    if (stationutil:get-parameter("level")="response")
        then ( 
            if ( matches(string-join(request:get-parameter-names()) ,"station|sta|channel|cha|location|loc|minlatitude|minlat|maxlatitude|maxlat|minlongitude|minlon|maxlongitude|maxlon|starttime|start|endtime|end|startbefore|endbefore|startafter|endafter|latitude|lat|longitude|lon|maxradius|minradius|includerestricted" )) 
            then  stationutil:query_response_main()
            else stationutil:query_network_shortcut_main()
            )
        else if (stationutil:get-parameter("level")="channel") 
            then  ( 
            if ( matches(string-join(request:get-parameter-names()) ,"station|sta|channel|cha|location|loc|minlatitude|minlat|maxlatitude|maxlat|minlongitude|minlon|maxlongitude|maxlon|starttime|start|endtime|end|startbefore|endbefore|startafter|endafter|latitude|lat|longitude|lon|maxradius|minradius|includerestricted" )) 
            then stationutil:query_channel_main()
            else stationutil:query_network_shortcut_main()
            )
            else if (stationutil:get-parameter("level")="station") 
                then stationutil:query_station_main()
                else if (stationutil:get-parameter("level")="network") 
                    then stationutil:query_network_main()
                    else ()
else if (stationutil:get-parameter("format")="text") then (        
    let $dummy := util:declare-option("exist:serialize","method=text media-type=text/plain indent=yes") 
    return
    if (stationutil:get-parameter("level")="response")
        then ( 
            if ( matches(string-join(request:get-parameter-names()) ,"station|sta|channel|cha|location|loc|minlatitude|minlat|maxlatitude|maxlat|minlongitude|minlon|maxlongitude|maxlon|starttime|start|endtime|end|startbefore|endbefore|startafter|endafter|latitude|lat|longitude|lon|maxradius|minradius|includerestricted" )) 
            then ( transform:transform(stationutil:query_response_main(), doc("response.xsl"), ())  )
            else ( transform:transform(stationutil:query_network_shortcut_main(), doc("response.xsl"), ()))
            )
        else if (stationutil:get-parameter("level")="channel") 
            then  ( 
            if ( matches(string-join(request:get-parameter-names()) ,"station|sta|channel|cha|location|loc|minlatitude|minlat|maxlatitude|maxlat|minlongitude|minlon|maxlongitude|maxlon|starttime|start|endtime|end|startbefore|endbefore|startafter|endafter|latitude|lat|longitude|lon|maxradius|minradius|includerestricted" )) 
            then ( transform:transform(stationutil:query_channel_main(), doc("channel.xsl"), ()) )
            else ( transform:transform(stationutil:query_network_shortcut_main(), doc("channel.xsl"), ()) )
            )    
            else if (stationutil:get-parameter("level")="station") 
                then ( transform:transform( stationutil:query_station_main(), doc("station.xsl"), ()) )
                else if (stationutil:get-parameter("level")="network") 
                    then (transform:transform(stationutil:query_network_main(), doc("network.xsl"), ()) )
                    else ()
)
    else ()

}
catch err:* {"Error checking parameters"}

