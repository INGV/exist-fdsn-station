xquery version "3.1";

declare default element namespace "http://www.fdsn.org/xml/station/1" ;
declare namespace ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";
declare namespace request="http://exist-db.org/xquery/request";
declare namespace output = "http://www.w3.org/2010/xslt-xquery-serialization";
declare option output:method "xml";
declare option output:media-type "text/xml";
declare option output:indent "no";
declare option output:omit-xml-declaration "no";

import module namespace login="http://exist-db.org/xquery/login" at "resource:org/exist/xquery/modules/persistentlogin/login.xql";
import module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil"  at "util.xql";
import module namespace mgmt="http://exist-db.org/apps/fdsn-station/modules/management.xqm" at "management.xqm";


let $code:=request:get-parameter('code', '')
(:$startDate is the startDate in past files, it could be different from new StartDate found in passed Network File:)
(: Converting passed date, forces T00:00:00 if absent :)
let $converted := stationutil:time_adjust(request:get-parameter('startDate', ''))
let $time := xs:time(xs:dateTime($converted)) (: 6 ciphres :)
(:let $ftime:= format-time($time, "T[H01]:[m01]:[s01].[f000001,6-6]"):)
let $date := xs:date(xs:dateTime($converted))
(: 6 ciphres :)
(:let $fdate:= format-date($date, "[Y,4]-[M,2]-[D,2]"):)
let $datetime := dateTime($date,$time)

(:let $log := util:log('info',"Converted: " || $converted || " date: " || $date || " time: " || $time || " datetime: "|| $datetime  || " fdate: " || $fdate || " ftime " || $ftime):)
(:(xs:datetime has only three ciphers :)
(:Se ci sono più di tre cifre decimali nel parametro passato, conviene confrontare come stringa:)
(:let $input:=format-dateTime(dateTime($date,$time), "[Y,4]-[M,2]-[D,2]T[H01]:[m01]:[s01].[f1,6]"):)
(:let $input:= xs:dateTime(stationutil:time_adjust(request:get-parameter('startDate', ''))):)
(:let $log := util:log('info',"Datetime: " || $input):)
(:let $startDate:=fn:adjust-dateTime-to-timezone($datetime,()):)

let $startDate:=fn:adjust-dateTime-to-timezone($datetime,())
(:let $startDate:=fn:adjust-dateTime-to-timezone(xs:dateTime(request:get-parameter('startDate', '')),()):)
let $log:=util:log('info',"Startdate:" || $startDate)
(::)
(:let $log:=util:log("info", " net: " || $code  || " date: " || $startDate):)
let $content := request:get-data()
(:let $log:= util:log("info","Content: " ||$content):)
let $decoded := util:base64-decode($content)
let $log:= stationutil:debug("info", "Decoded: " || $decoded)
(:let $xml := '':)
let $xml := fn:parse-xml($decoded)
let $netcode := $xml//Network/@code
let $netstartDate := $xml//Network/@startDate
let $netrestrictedStatus := $xml//Network/@restrictedStatus

return
try {
    let $user:=sm:id()
(:    let $log:=if ($user!="guestguest") then util:log("info", "User: " || $user || " net: " || $code  || " startDate: " || $startDate) else ():)
    return
    (
        if ($user!="fdsndba")
        then
            stationutil:authorization_error()
        else
(:            if ( request:get-method() eq "PUT" and $netcode=$code and $netstartDate=$startDate and ( $netrestrictedStatus='open' or $netrestrictedStatus = 'closed' )):)
            if ( request:get-method() eq "PUT" and $netcode=$code and ( $netrestrictedStatus='open' or $netrestrictedStatus = 'closed' ))
            then mgmt:bulkmodify($code, $startDate, $xml) (: check on startDate made only in bulkmodify :)
            else stationutil:other_error()
    )

    }
catch err:* {
     let $error := stationutil:internal_error($err:code || " " || $err:description )
     return $error || "
" || $err:code || " " || $err:description
}
