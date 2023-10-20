xquery version "3.1";
(:
    A simple XQuery for an XQueryTrigger that
    logs all trigger events for which it is executed
    in the file /db/triggers-log.xml
:)
module namespace trigger="http://exist-db.org/xquery/trigger";
declare namespace xmldb="http://exist-db.org/xquery/xmldb";


declare default element namespace "http://www.fdsn.org/xml/station/1" ;
declare namespace ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";
import module  namespace functx = "http://www.functx.com";


import module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil"  at "util.xql";
(:declare default element namespace "https://raw.githubusercontent.com/FDSN/StationXML/master" ;:)
(:declare default element namespace "https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" ;:)
declare namespace station="http://www.fdsn.org/xml/station/1" ;

declare namespace request="http://exist-db.org/xquery/request";
declare namespace output = "http://www.w3.org/2010/xslt-xquery-serialization";
declare namespace local = "http://local";
declare option output:method "xml";
declare option output:media-type "text/xml";
(:TODO uncomment after debug:)
declare option output:indent "no";
declare option output:omit-xml-declaration "no";


declare function trigger:before-create-collection($uri as xs:anyURI) {
    local:log-event("before", "create", "collection", $uri)
};
declare function trigger:after-create-collection($uri as xs:anyURI) {
    let $log:=local:log-event("after", "create", "collection", $uri)
    return local:allnetworkstationchannel()
};
declare function trigger:before-copy-collection($uri as xs:anyURI, $new-uri as
xs:anyURI) {
    local:log-event("before", "copy", "collection", concat("from: ", $uri, " to:
", $new-uri))
};
declare function trigger:after-copy-collection($new-uri as xs:anyURI, $uri as xs:anyURI) {
    local:log-event("after", "copy", "collection", concat("from: ", $uri, " to:
", $new-uri))
};
declare function trigger:before-move-collection($uri as xs:anyURI, $new-uri as
xs:anyURI) {
    local:log-event("before", "move", "collection", concat("from: ", $uri, " to:
", $new-uri))
};
declare function trigger:after-move-collection($new-uri as xs:anyURI, $uri as xs:anyURI) {
    local:log-event("after", "move", "collection", concat("from: ", $uri, " to:
", $new-uri))
};
declare function trigger:before-delete-collection($uri as xs:anyURI) {
    local:log-event("before", "delete", "collection", $uri)
};
declare function trigger:after-delete-collection($uri as xs:anyURI) {
    let $log:=local:log-event("after", "delete", "collection", $uri)
    return local:allnetworkstationchannel()
};
declare function trigger:before-create-document($uri as xs:anyURI) {
    local:log-event("before", "create", "document", $uri)
};
declare function trigger:after-create-document($uri as xs:anyURI) {
    let $log:=local:log-event("after", "create", "document", $uri)
    return local:allnetworkstationchannel()
};
declare function trigger:before-update-document($uri as xs:anyURI) {
    local:log-event("before", "update", "document", $uri)
};
declare function trigger:after-update-document($uri as xs:anyURI) {
    local:log-event("after", "update", "document", $uri)
};
declare function trigger:before-copy-document($uri as xs:anyURI, $new-uri as xs:anyURI) {
    local:log-event("before", "copy", "document", concat("from: ", $uri, " to: "
, $new-uri))
};
declare function trigger:after-copy-document($new-uri as xs:anyURI, $uri as xs:anyURI) {
    local:log-event("after", "copy", "document", concat("from: ", $uri, " to: ",
$new-uri))
};
declare function trigger:before-move-document($uri as xs:anyURI, $new-uri as xs:anyURI) {
    local:log-event("before", "move", "document", concat("from: ", $uri, " to: "
, $new-uri))
};
declare function trigger:after-move-document($new-uri as xs:anyURI, $uri as xs:anyURI) {
    local:log-event("after", "move", "document", concat("from: ", $uri, " to: ",
$new-uri))
};
declare function trigger:before-delete-document($uri as xs:anyURI) {
    local:log-event("before", "delete", "document", $uri)
};
declare function trigger:after-delete-document($uri as xs:anyURI) {
    let $log:=local:log-event("after", "delete", "document", $uri)
    return local:allnetworkstationchannel()
};

declare function local:log-event($type as xs:string, $event as xs:string, $object-type as xs:string, $uri as xs:string) {
    let $log-collection := "/db"
    let $log := "triggers-log.xml"
    let $log-uri := concat($log-collection, "/", $log)
    return
        (
        (: create the log file if it does not exist :)
        if (not(doc-available($log-uri))) then
            xmldb:store($log-collection, $log, <triggers/>)
        else ()
        ,
        (: log the trigger details to the log file :)
        update insert <trigger event="{string-join(($type, $event, $object-type
), "-")}" uri="{$uri}" timestamp="{current-dateTime()}"/> into doc($log-uri
)/triggers
        )
};





declare function local:allnetworkstationchannel() {

(:let $xml:=for $all in collection("/db/apps/fdsn-station/Station/"):)
(:Buono, manca il nome statzione e la divisione in reti:)
(:let $xml:= for $all in collection("/db/apps/fdsn-station/Station/")//Network/Station/*[not(self::Channel)]:)
(:let $xml:= for $all in collection("/db/apps/fdsn-station/Station/")//ancestor::Channel:)
let $xml:= for $network in collection("/db/apps/fdsn-station/Station/")//Network/@*/..
(:let $xml:= for $network in collection("/db/apps/fdsn-station/Station/")//Network/Station/@*/..:)
(:let $xml:= for $network in collection("/db/apps/fdsn-station/Station/")//Station/node()[name(.)!="Channel"]/..:)

(:let $startDate:= $network/@startDate:)
      let $netcode:=$network/@code
      let $startDate:=$network/@startDate
      let $endDate:=$network/@endDate
      let $restrictedStatus:=$network/@restrictedStatus

      let $Description:=$network/Description
      let $Identifier:=$network/Identifier
(:      let $IdentifierType:=$network/Identifier/@type:)
      let $ingvIdentifier:=$network/ingv:Identifier

        let $station := $network/Station
(:        let $CreationDate := $network/Station/CreationDate:)
(:group by $netcode:)
      group by $netcode, $startDate, $endDate, $restrictedStatus, $Description,  $ingvIdentifier
      order by $netcode, $station[1]/@code[1]

       return <Network>
            {$netcode} {$startDate} {$endDate} {$restrictedStatus}
            {$Description}

            {
                functx:distinct-deep(
                if ($Identifier/text() = distinct-values(for $d in $Identifier return $d))
                then $Identifier
                else ()//Identifier)

            }

            {$ingvIdentifier}
        <TotalNumberStations> {stationutil:stationcount($netcode)} </TotalNumberStations>
        <SelectedNumberStations> {count($station/@code)} </SelectedNumberStations>
        {
(:            let $distinct_sta1:=stationutil:remove-multi($station,"Channel"):)
(:            let $distinct_sta2:=stationutil:remove-multi($distinct_sta1,"TotalNumberChannels"):)
(:            let $distinct_sta:=stationutil:remove-multi($distinct_sta2,"SelectedNumberChannels"):)
            let $distinct_sta:=stationutil:remove-multi($station,"Response")

        return fn:sort($distinct_sta,(), function($distinct_sta) {$distinct_sta/@code}) }

        </Network>


let $net:= <FDSNStationXML>{$xml}</FDSNStationXML>

(:return xmldb:store("/db/apps/fdsn-station/StationPruned/", "ALLSTATION", $net):)
return ()
(:return $xml:)

(:</Network>:)

};
