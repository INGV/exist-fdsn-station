xquery version "3.1";
module namespace mgmt="http://exist-db.org/apps/fdsn-station/modules/management.xqm";
import module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil"  at "util.xql";
import module  namespace functx = "http://www.functx.com";
declare default element namespace "http://www.fdsn.org/xml/station/1" ;
declare namespace station = "http://www.fdsn.org/xml/station/1" ;
declare namespace ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";


(:~
 : Change network elements and attributes
 :
 :
 : attributes changeable
 : endDate="" alternateCode="" historicalCode="" restrictedStatus="" sourceID=""
 : elements changeable
 :  <Description>
 :  <Identifier> many
 :  <Comment> many
 :  <DataAvailability> NO
 :  <Operator> many
 : TODO add ingv namespace in netcache to manage and read
 : <FDSNStationXML xmlns="http://www.fdsn.org/xml/station/1" xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">
 : If passed a segment with @restrictedStatus=open, it means that all the station
 : implied and their channels must pass explicitly to restrictedStatus=open
 :)
declare function mgmt:bulkmodify($code, $startDate, $xml) {

    let $net_in_cache := stationutil:netcache_exists($code,$startDate)

    (: recover valid attribute and elements from xml:)
    (: If Sstartdate different from $netstartDate, then the date should change in all correspondent station files    :)
    let $netstartDate := if (exists($xml//Network/@startDate)) then stationutil:time_adjust($xml//Network/@startDate) else ()
    let $alternateCode := $xml//Network/@alternateCode
    let $netendDate := if (exists($xml//Network/@endDate)) then stationutil:time_adjust($xml//Network/@endDate) else ()
    let $historicalCode := $xml//Network/@historicalCode
    let $restrictedStatus := $xml//Network/@restrictedStatus

    let $sourceID := $xml//Network/@sourceID
    let $Description := $xml//Network/Description
    let $Identifier := $xml//Network/Identifier
    let $Comment := $xml//Network/Comment
    let $Operator := $xml//Network/Operator


    let $lookup_documents :=
    if ($net_in_cache) then (
      for $doc in collection($stationutil:station_collection)
        let $document_name := util:document-name($doc)
(:        let $log:= stationutil:debug('info', string-join($document_name))    :)
        for $sta_doc in $doc//Network[@code=$code and @startDate=$startDate]/..
            let $network := $sta_doc//Network[@code=$code and @startDate=$startDate]
            let $other_network := $sta_doc//Network[@code!=$code or @startDate!=$startDate]
(:            let $other_network_code := $other_network/@code:)
            let $source := $sta_doc//Source
            let $sender := $sta_doc//Sender
            let $module := $sta_doc//Module
            let $moduleURI := $sta_doc//ModuleURI
(:            let $created := $sta_doc//Created:)
(:            let $network_restricted_status := $network/@restrictedStatus:)
            (:add elements and attributes from $xml:)
            (:TODO propagate $restrictedStatus when is set to open:)

            let $new_network :=

                element Network {
                     attribute code {$code},
(:                     attribute startDate {$startDate},:)
                     attribute startDate {$netstartDate},
                     if (exists($alternateCode)) then attribute alternateCode {$alternateCode} else (),
                     if (exists($netendDate)) then attribute endDate {$netendDate} else (),
                     if (exists($historicalCode)) then attribute historicalCode {$historicalCode} else (),
                     $network/@restrictedStatus, (: untouched at this stage :)
                     if (exists($sourceID)) then attribute sourceID {$sourceID} else (),
                     $Description,
                     $Identifier,
                     $Comment,
                     $Operator,
                     $network//Station
                     }
            (:Policy: the network should only be open, restrictedStatus_closeable defaults to false :)
            let $propagated := if ($restrictedStatus='open' or $stationutil:settings('restrictedStatus_closeable')) then mgmt:restrictedStatus($new_network,$restrictedStatus) else $new_network
(:            let $log := util:log('info', string-join($propagated//@*)):)
            where $sta_doc//Network[@code=$code and @startDate=$startDate]
        return
            xmldb:store($stationutil:station_collection, $document_name,
            <FDSNStationXML xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.2" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.2.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd">
                {$source}
                {$sender}
                {$module}
                {$moduleURI}
                <Created>{format-dateTime(current-dateTime(), "[Y0001]-[M01]-[D01]T[H01]:[m01]:[s01].[f]")}</Created>
                {$propagated}{$other_network}
                </FDSNStationXML>
                ),
        stationutil:update_collections($code, $netstartDate)
        )
    else stationutil:nodata_error()
    (:Fix only the network required:)
(:    let $netcache := stationutil:update_collections($code, $startDate):)
 return ()
};



declare function mgmt:restrictedStatus($nodes as node()*, $restrictedStatus) {

    for $node in $nodes
    return
        typeswitch ($node)
            case element(Network)  | element(Station)  | element(Channel)  return
                element
                    { node-name ($node) }
                    { $node/@*[not( name() = 'restrictedStatus')], attribute restrictedStatus  {$restrictedStatus} , mgmt:restrictedStatus($node/node(), $restrictedStatus)}
            case text() return
                $node
            default return
                $node
};


