xquery version "3.1";

declare default element namespace "http://www.fdsn.org/xml/station/1" ;
declare namespace ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";
import module  namespace functx = "http://www.functx.com";
declare namespace f="http://exist-db.org/xquery/test";



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



(:~ Remove recursively elements with given $remove-names and its children
 :
 : @param $input element tree
 : @param $remove-names name of elements to remove
 : :)
declare function local:remove-multi($in as element()*, $remove-names as xs:string*) as element()* {
    for $input in $in return
   element {node-name($input) }
      {$input/@*,
       for $child in $input/node()[not(name(.)=$remove-names)]
(:       for $child in $input/node()[name(.)!=$remove-names]:)
          return
             if ($child instance of element())
                then stationutil:remove-elements($child, $remove-names)
                else $child
      }
};

declare function local:test0() {

let $xml:=for $alternate_network in collection("/db/apps/fdsn-station/Station/")//AlternateNetwork

group by $alternate_network
order by $alternate_network/@code

return $alternate_network[1]

return <ingv:AlternateNetworks>{$xml}</ingv:AlternateNetworks>


};


(:/root/* except /root/terminate:)
declare function local:test1() {

(:let $xml:=for $all in collection("/db/apps/fdsn-station/Station/"):)
(:Buono, manca il nome statzione e la divisione in reti:)
(:let $xml:= for $all in collection("/db/apps/fdsn-station/Station/")//Network/Station/*[not(self::Channel)]:)
(:let $xml:= for $all in collection("/db/apps/fdsn-station/Station/")//Network/Station/ancestor-or-self::Channel/@*:)
(:let $xml:= for $all in collection("/db/apps/fdsn-station/Station/")//Network/*[count(*)=0]:)

let $xml:= for $all in collection("/db/apps/fdsn-station/Station/")//*[not(descendant::Channel) and not(ancestor-or-self::Channel)]
(:OKlet $xml:= for $all in collection("/db/apps/fdsn-station/Station/")//Network/@*:)

(:let $xml:= for $all in collection("/db/apps/fdsn-station/Station/")//Station/node()[name(.)!="Channel"]/..:)
let $acode:= $all/@code
let $startDate:= $all/@startDate
(:group by $acode:)
(:order by $acode:)
 group by $acode, $startDate
return $all
(:return ($acode,$startDate):)

(:let $ll:=$xml/@*:)
(:return:)
(:<Network>:)

for $a in $xml

return <Station>{$a}</Station>
(:return $xml:)

(:</Network>:)

};



declare function local:allnetworkstation() {

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
        <TotalNumberStations> {stationutil:stationcount($netcode,$startDate,$endDate,$restrictedStatus)} </TotalNumberStations>
        <SelectedNumberStations> {count($station/@code)} </SelectedNumberStations>
        {
(:            let $distinct_sta1:=stationutil:remove-multi($station,"Channel"):)
(:            let $distinct_sta2:=stationutil:remove-multi($distinct_sta1,"TotalNumberChannels"):)
(:            let $distinct_sta:=stationutil:remove-multi($distinct_sta2,"SelectedNumberChannels"):)
            let $distinct_sta:=stationutil:remove-multi($station,("Channel","TotalNumberChannels","SelectedNumberChannels"))

        return fn:sort($distinct_sta,(), function($distinct_sta) {$distinct_sta/@code}) }

        </Network>


return <FDSNStationXML>{$xml}</FDSNStationXML>
(:return $xml:)

(:</Network>:)

};

declare function local:allnetworkstationchannel() {

(:let $xml:=for $all in collection("/db/apps/fdsn-station/Station/"):)
(:Buono, manca il nome statzione e la divisione in reti:)
(:let $xml:= for $all in collection("/db/apps/fdsn-station/Station/")//Network/Station/*[not(self::Channel)]:)
(:let $xml:= for $all in collection("/db/apps/fdsn-station/Station/")//ancestor::Channel:)
(:let $xml:= for $network in collection("/db/apps/fdsn-station/Station/")//Network/@*/..:)
let $xml:= for $network in collection("/db/apps/fdsn-station/StationPruned/")//Network/@*/..
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
        <TotalNumberStations> {stationutil:stationcount($netcode,$startDate,$endDate,$restrictedStatus)} </TotalNumberStations>
        <SelectedNumberStations> {count($station/@code)} </SelectedNumberStations>
        {
(:            let $distinct_sta1:=stationutil:remove-multi($station,"Channel"):)
(:            let $distinct_sta2:=stationutil:remove-multi($distinct_sta1,"TotalNumberChannels"):)
(:            let $distinct_sta:=stationutil:remove-multi($distinct_sta2,"SelectedNumberChannels"):)
            let $distinct_sta:=stationutil:remove-multi($station,"Response")
            for $s in $station
            let $id:= util:node-id($s/@code)
            let $log := util:log("info", "Id of " || $s/@code || " " || $id)

        return fn:sort($distinct_sta,(), function($distinct_sta) {$distinct_sta/@code}) }

        </Network>


return <FDSNStationXML>{$xml}</FDSNStationXML>
(:return $xml:)

(:</Network>:)

};

(:"/db/apps/fdsn-station/Station/":)
declare function local:prune($source_c as xs:string,  $dest_c as  xs:string, $station_name as xs:string){
(:    try {:)
(:(:    Take a resource ,create a  pruned version and place it in destination:):)
(:    let $document:= doc($source_c||$station_name):)
(:    for $network in $document:)
(:    let $pruned :=stationutil:remove-multi($network,"Response"):)
(:    return:)
(:    xmldb:store($dest_c, $station_name, $pruned):)
(:    }:)
(:    catch err:* {()}:)
(:    :)

        try {
(:    Take a resource ,create a  pruned version and place it in destination:)
    let $document:= doc($source_c||$station_name)
    let $log := util:log("info", "pruning " || $station_name || " First pass")
(:    for $network in xmldb:xcollection("/db/apps/fdsn-station/Station/"||$station_name):)

    let $pruned :=stationutil:remove-multi($document//FDSNStationXML,"Stage")
    let $log := util:log("info", "pruning " || $station_name )
    return
    xmldb:store($dest_c, $station_name, $pruned)
    }
    catch err:* {()}



};


declare function local:prune-all(){

    let $station_names:= xmldb:get-child-resources("/db/apps/fdsn-station/Station/")
    return
    <B>
        {
    for $station_name in $station_names
    let $pruned:= local:prune("/db/apps/fdsn-station/Station/",  "/db/apps/fdsn-station/StationPruned/", $station_name)
    return <A>{$station_name}</A>
        }
    </B>
} ;





declare function local:CacheCreate() {



let $xml:=
    for $network in collection("/db/apps/fdsn-station/Station/")//Network/@*/..

        let $netcode:=$network/@code
        let $startDate:=$network/@startDate
        let $endDate:=$network/@endDate
        let $restrictedStatus:=$network/@restrictedStatus
        let $Description:=$network/Description
        let $ingvIdentifier:=$network/ingv:Identifier

        let $station := $network/Station
    group by $netcode, $startDate, $endDate, $restrictedStatus, $Description,  $ingvIdentifier
    order by $netcode, $station[1]/@code[1]

    return
        <Network>
        {$netcode} {$startDate} {$endDate} {$restrictedStatus} {$Description}
        <TotalNumberStations> {count($station)} </TotalNumberStations>
        </Network>

let $netfile:= <FDSNStationXML>{$xml}</FDSNStationXML>
let $store:=xmldb:store( "/db/apps/fdsn-station/NetCache","net.xml",$netfile )
 return $netfile

(:let $xml:= :)
(:    for $network in collection("/db/apps/fdsn-station/Station/")//Network/@*/..:)
(::)
(:        let $netcode:=$network/@code:)
(:        let $startDate:=$network/@startDate:)
(:        let $endDate:=$network/@endDate:)
(:        let $restrictedStatus:=$network/@restrictedStatus:)
(:        let $Description:=$network/Description:)
(:        let $ingvIdentifier:=$network/ingv:Identifier:)
(::)
(:        let $station := $network/Station:)
(:    group by $netcode, $startDate, $endDate, $restrictedStatus, $Description,  $ingvIdentifier:)
(:    order by $netcode, $station[1]/@code[1]:)
(::)
(:    return :)
(:        <Network>:)
(:        {$netcode} {$startDate} {$endDate} {$restrictedStatus} {$Description}:)
(:        <TotalNumberStations> {stationutil:stationcount($netcode)} </TotalNumberStations>:)
(:        </Network>:)
(::)
(:    return xmldb:store( "/db/apps/fdsn-station/NetCache","net.xml",<FDSNStationXML>{$xml}</FDSNStationXML> ):)

};


declare function local:CacheCount($net as xs:string) as item() {

    let $document:= doc("/db/apps/fdsn-station/NetCache/net.xml")
(:    return $document:)

    for $n in $document//Network
    let $netcode:=$n/@code
    let $totalnumberstations:=$n/TotalNumberStations
    where $netcode=$net
    return <a>{$totalnumberstations/text()}</a>

};

declare function local:badrequest_error() {
    (: declare output method locally to override default xml   :)
    util:declare-option("exist:serialize","method=text media-type=text/plain indent=no")  ,
     response:set-status-code(400) ,
     "Error 400: Bad request

Syntax Error in Request

"
};



(::)
(:declare function local:netcache_update($station as item()) as item()* {:)
(:    :)
(:(:    let $document:=doc("/db/apps/fdsn-station/Station/AQU.xml"):):)
(:    let $document:=$station:)
(:    let $nets:=( :)
(:        for $n in $document//Network:)
(:        let $netcode:= $n/@code:)
(:        let $log:=util:log("INFO", "netcache create " || $netcode):)
(:        return $netcode) :)
(:    let $xml:= doc("/db/apps/fdsn-station/NetCache/net.xml"):)
(:    let $netfile := :)
(:    (for $network in $xml//Network:)
(:    let $netcode:=$network/@code:)
(:    let $startDate:=$network/@startDate:)
(:    let $endDate:=$network/@endDate:)
(:    let $restrictedStatus:=$network/@restrictedStatus:)
(:    let $Description:=$network/Description:)
(:    let $ingvIdentifier:=$network/ingv:Identifier:)
(:    (: Only for networks of the station passed update the number   :):)
(:    let $tns:=if ($netcode=$nets) then $network/TotalNumberStations/text()+1 else $network/TotalNumberStations/text():)
(::)
(:    return <Network>{$netcode} {$startDate} {$endDate} {$restrictedStatus} {$Description} <TotalNumberStations> {$tns} </TotalNumberStations></Network>:)
(:    )    :)
(:    :)
(::)
(::)
(:    let $netfile:=<FDSNStationXML>{$netfile}</FDSNStationXML>:)
(:    return $netfile:)
(:(:    let $store:=xmldb:store( "/db/apps/fdsn-station/NetCache","net.xml",$netfile ):):)
(:};:)

declare function local:netcache_update($station as item(), $sign as xs:double) as xs:string {

(:    let $document:=doc("/db/apps/fdsn-station/Station/AQU.xml"):)
    let $document:=$station
    let $nets:=(
        for $n in $document//Network
            let $netcode:= $n/@code
            let $log:=util:log("INFO", "netcache update " || $netcode)
        return $netcode)
    let $xml:= doc("/db/apps/fdsn-station/NetCache/net.xml")
    let $netfile := (
        for $network in $xml//Network
            let $netcode:=$network/@code
            let $startDate:=$network/@startDate
            let $endDate:=$network/@endDate
            let $restrictedStatus:=$network/@restrictedStatus
            let $Description:=$network/Description
            let $ingvIdentifier:=$network/ingv:Identifier
            (: Only for networks of the station passed update the number   :)
            (:TODO manage case with $tns=0:)
            let $tns:=if ($netcode=$nets) then $network/TotalNumberStations/text()+$sign else $network/TotalNumberStations/text()

            return if ($tns>0) then
                <Network>
                    {$netcode} {$startDate} {$endDate} {$restrictedStatus} {$Description}
                    <TotalNumberStations> {$tns} </TotalNumberStations>
            </Network>
            else ()
    )


    let $netfile:=<FDSNStationXML>{$netfile}</FDSNStationXML>

    let $store:=xmldb:store( "/db/apps/fdsn-station/NetCache","net.xml",$netfile )

    return $netfile
(:    let $store:=xmldb:store( "/db/apps/fdsn-station/NetCache","net.xml",$netfile ):)
};


declare function local:netcache_exists($netcode as xs:string) {
  let $docavailable:=doc-available("/db/apps/fdsn-station/NetCache/net.xml")
  let $xml:= if ( $docavailable ) then doc("/db/apps/fdsn-station/NetCache/net.xml") else ()
  let $netfile := if ($xml=())
    then ()
    else
    (
        for $network in $xml//Network[@code=$netcode]
            let $netcode:=$network/@code
        return $network
    )

  return exists($netfile)
(:  return $netfile:)

};


declare function local:netcache_parse($pattern as xs:string * ) as item ()* {
  let $docavailable:=doc-available("/db/apps/fdsn-station/NetCache/net.xml")
  let $xml:= if ( $docavailable ) then doc("/db/apps/fdsn-station/NetCache/net.xml") else ()
(:  let $netfile := if ($xml=()) :)
(:    then () :)
(:    else :)
(:    ( :)
(:        for $network in $xml//Network[@code=$pattern]:)
(:(:        for $network in $xml//Network[matches(@code,$pattern)]:):)
(:            let $netcode:=$network/@code:)
(:        return $network:)
(:    ):)
(:    :)
(:  return <a>{$netfile}</a>:)
(:  return $netfile:)
  let $netseq:=


if ($xml=())
    then ()
    else
    (
(:        for $network in $xml//Network[@code=$pattern]:)
        for $network in $xml//Network[matches(@code,$pattern)]
            let $netcode:=$network/@code
        return $netcode
    )


  let $netfile:=distinct-values($netseq)

(:  return <a>{$netfile}</a>:)
  return $netfile

};



declare function local:netcache_find ($sequence as item ()* )  {
  let $docavailable:=doc-available("/db/apps/fdsn-station/NetCache/net.xml")
  let $xml:= if ( $docavailable ) then doc("/db/apps/fdsn-station/NetCache/net.xml") else ()
  let $netfile := if ($xml=())
    then ()
    else
    (
        for $network in $xml//Network[@code=$sequence]
(:        for $network in $xml//Network[matches(@code,$pattern)]:)
            let $netcode:=$network/@code
        return $network
    )

  return <a>{$netfile}</a>
(:  return $netfile:)


};


(:Mancano gli elementi dell'anchestor per network e station:)
declare function local:build_station(){
    let $xml :=
    for $match in collection("/db/apps/fdsn-station/Station/")
    //Station[@code="ELFMC"]
(:    //Channel[@code="HHZ"]:)
(:    //Station[matches (@code, "^AQU$")]:)
(:    //Channel:)
    /Channel[matches (@code, ".*")]
    let $networkcode:=$match/../../@code
    let $startDate:=$match/../../@startDate
    let $endDate:=$match/../../@endDate
    let $stationcode:=$match/../@code
    let $restrictedStatus:=$match/../@restrictedStatus
    group by $networkcode, $startDate, $endDate, $restrictedStatus, $stationcode
    order by $networkcode, $startDate, $endDate, $stationcode

return

    <Network>{$match/../../@*}
        {$match/../*[name()!="Station"][name()!="TotalNumberStations"][name()!="SelectedNumberStations"][name()!="Channel"]}
        <TotalNumberStations> {stationutil:stationcount($networkcode,$startDate, $endDate, $restrictedStatus)} </TotalNumberStations>
        <SelectedNumberStations>{count($stationcode)}</SelectedNumberStations>
        <Station>{$match/../@*}
        {$match/../*[name() != "SelectedNumberChannels" and name() !="Channel"]}

        <SelectedNumberChannels>{count($match)}</SelectedNumberChannels>
        {
            for $cha in $match
            let $chacode := $cha/@code
            let $startDate:=$cha/@startDate
            let $endDate:=$cha/@endDate
            order by $chacode, $startDate,$endDate
            return $cha

        }
        </Station>
    </Network>


    return <FDSNStationXML> {$xml} </FDSNStationXML>
};



(:1ms response level:)
declare function local:build_full_station(){

        <FDSNStationXML>

    {

(:    for $match in collection("/db/apps/fdsn-station/Station/"):)
    for $match in collection("/db/apps/fdsn-station/StationPruned/")
    //Station[@code="ACER"]
(:    //Channel[@code="HHZ"]:)
(:    //Station[matches (@code, ".*")]:)
(:    //Station[matches (@code, "^AQU$")]:)
(:    /Channel:)
(:    //Channel[matches (@code, ".*")]:)
    let $networkcode:=$match/../@code
    let $startDate:=$match/../@startDate
    let $endDate:=$match/../@endDate
    let $stationcode:=$match/@code
    let $restrictedStatus:=$match/../@restrictedStatus
(:  con $stationcode OK solo con una stazione   :)
(:    group by $networkcode, $startDate, $endDate, $restrictedStatus, $stationcode :)
    group by $networkcode, $startDate, $endDate, $restrictedStatus , $stationcode
    order by $networkcode, $startDate, $endDate, $stationcode
(:    , $stationcode:)

return

    <Network>{$match/../@*}{$match/../*[name()!="Station"][name()!="TotalNumberStations"][name()!="SelectedNumberStations"]}
        <TotalNumberStations> {stationutil:stationcount($networkcode,$startDate, $endDate, $restrictedStatus)} </TotalNumberStations>
        <SelectedNumberStations>{count($stationcode)}</SelectedNumberStations>

            {$match}

    </Network>
    }
</FDSNStationXML>

(:    return <FDSNStationXML> {$xml} </FDSNStationXML>:)
};



(:FIXME:)
declare function local:build_full_network(){
         <FDSNStationXML>

    {
(:    for $match in collection("/db/apps/fdsn-station/Station/"):)
    for $match in collection("/db/apps/fdsn-station/StationPruned/")
(:    //Station[@code="ACER"]:)
(:    //Channel[@code="HHZ"]:)
    //Station
(:    //Station[matches (@code, ".*")]:)
(:    //Station[matches (@code, "^AQU$")]:)
(:    /Channel:)
(:    //Channel[matches (@code, ".*")]:)
    let $network := $match/..
    let $networkcode:=$match/../@code
    let $startDate:=$match/../@startDate
    let $endDate:=$match/../@endDate
    let $stationcode:=$match/@code
    let $restrictedStatus:=$match/../@restrictedStatus
(:  con $stationcode OK solo con una stazione   :)
(:    group by $networkcode, $startDate, $endDate, $restrictedStatus, $stationcode :)
    group by $networkcode, $startDate, $endDate, $restrictedStatus
    order by $networkcode, $startDate, $endDate

return

    <Network>{$network[1]/@*}
    {$network[1]/*[name()!="Station"][name()!="TotalNumberStations"][name()!="SelectedNumberStations"]}

        <TotalNumberStations> {stationutil:stationcount($networkcode,$startDate, $endDate, $restrictedStatus)} </TotalNumberStations>
        <SelectedNumberStations>{count($stationcode)}</SelectedNumberStations>

            {
                for $station in $match
                let $stacode := $station/@code
                order by $stacode
                return $station

            }

    </Network>
    }
</FDSNStationXML>

(:    return <FDSNStationXML> {$xml} </FDSNStationXML>:)
};



(:Manage full network, loose speed:)
declare function local:query_core_channel_response_shortcut($NSLCSE as map()*){

    let $dlog := stationutil:debug("info", "query_core_channel_response_shortcut_new" )
    let $level := $NSLCSE("level")
    let $since:= xs:dateTime($NSLCSE("updatedafter"))
    let $collection := if ($level="response") then "/db/apps/fdsn-station/Station/" else "/db/apps/fdsn-station/StationPruned/"
    for $match in collection($collection)
(:    //Station[@code="ACER"]:)
(:    //Channel[@code="HHZ"]:)
    //Station
(:    //Station[matches (@code, ".*")]:)
(:    //Station[matches (@code, "^AQU$")]:)
(:    /Channel:)
(:    //Channel[matches (@code, ".*")]:)
    let $network := $match/..
    let $networkcode:=$match/../@code
    let $startDate:=$match/../@startDate
    let $endDate:=$match/../@endDate
    let $stationcode:=$match/@code
    let $restrictedStatus:=$match/../@restrictedStatus
(:  con $stationcode OK solo con una stazione   :)
(:    group by $networkcode, $startDate, $endDate, $restrictedStatus, $stationcode :)
    group by $networkcode, $startDate, $endDate, $restrictedStatus
    order by $networkcode, $startDate, $endDate

return

    <Network>{$network[1]/@*}
    {$network[1]/*[name()!="Station"][name()!="TotalNumberStations"][name()!="SelectedNumberStations"]}

        <TotalNumberStations> {stationutil:stationcount($networkcode,$startDate, $endDate, $restrictedStatus)} </TotalNumberStations>
        <SelectedNumberStations>{count($stationcode)}</SelectedNumberStations>

            {
                for $station in $match
                let $stacode := $station/@code
                order by $stacode
                return $station

            }

    </Network>


};

(:{distinct-values($network/*[name()!="Station"][name()!="TotalNumberStations"][name()!="SelectedNumberStations"])} :)

(:    <Network>{$match/../@*} :)
(:        <TotalNumberStations> {stationutil:stationcount($networkcode,$startDate, $endDate, $restrictedStatus)} </TotalNumberStations>:)
(:        <SelectedNumberStations>{stationutil:stationcount($networkcode,$startDate, $endDate, $restrictedStatus)}</SelectedNumberStations>:)
(:        <Station>{$match}:)
(:        </Station>:)
(:    </Network>:)

(:{$match/../*[not(name() = ("SelectedNumberChannels" , "Channel"))]}:)
(:{$match/../*[not(name() = "SelectedNumberChannels")][not(name() = "Channel")]}:)
(:{$match/../*[name() = ("Latitude" , "Longitude")]}:)
(:  {$match}:)

if ( request:get-method() eq "GET") then
(:    local:netcache_parse(("MN","IV")):)

(:let $sequence:=local:netcache_parse(".*"):)
(:return local:netcache_find($sequence):)

(:    local:build_full_station():)
(:    local:build_station():)

    <executed>Cleared cache {cache:clear()}</executed>

(:    local:build_full_network():)

 (:     local:allnetworkstationchannel():)
(:     local:allnetworkstation():)
(:     local:CacheCreate():)
(:     stationutil:netcache_create():)

(:     local:CacheCount("IV"):)
(:     local:prune-all():)
(:     stationutil:prune("/db/apps/fdsn-station/Station/",  "/db/apps/fdsn-station/StationPruned/", "A319A.xml"):)

(:    local:netcache_update(doc("/db/apps/fdsn-station/Station/AND3.xml"),1):)
(:    local:netcache_exists("CA"):)

 else
     local:badrequest_error()
