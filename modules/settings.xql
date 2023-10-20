xquery version "3.1";

import module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil"  at "util.xql";
declare default element namespace "http://www.fdsn.org/xml/station/1";
declare namespace ingv = "https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";
declare option exist:serialize "method=xhtml media-type=text/html indent=yes";


(:Take parameters from GET in app.xql:)
let $enable_log      := if (request:get-parameter("enable_log","off") = "on") then true() else false()
let $enable_debug    := if (request:get-parameter("enable_debug","off") = "on") then true() else false() 
let $enable_query_log:= if (request:get-parameter("enable_query_log","off") = "on") then true() else false()

(:let $log:=util:log("info","New setting applied"):)
(:Reading from JSON file declares the map :)
(: declare %public variable $stationutil:settings := map {:)
(:    "enable_log": true(),                               :)
(:    "enable_debug": false(),                            :)
(:    "enable_query_log": false(),                        :)
(:    "post_limit_rows": 1000,                            :)
(:    "translate_units": true(),                          :)
(:    "remove_tz": true()                                 :)
(: };:)
 
let $settings := json-doc("/db/apps/fdsn-station/config/settings.json")
(:passo in xml per avere map:)

let $passed:= map {
    "enable_log": $enable_log,
    "enable_debug": $enable_debug,                            
    "enable_query_log": $enable_query_log
}

let $new_settings:=map:merge( ($settings,$passed)) 

let $f := function($k, $v) {concat('"',$k,'"', ': ', $v, ',')}
let $h := map:for-each($new_settings, $f)

let $string := string-join($h)
let $fixed := substring($string,1,string-length($string)-1)
let $json := "{"||$fixed || "}"

return 

if( empty(xmldb:store("/db/apps/fdsn-station/config", "settings.json", $json)) ) then  
    (
        let $log := util:log("error","Error applying settings") 
        return
        <div xmlns="http://www.w3.org/1999/xhtml" data-template="templates:surround" data-template-with="templates/page.html" data-template-at="content">
            <div class="col-md-9">
                <h1 data-template="config:app-title">Manage data</h1>
                <div class="row">
                    <div class="col-md-6">
                        <h1>Error applying settings</h1>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <h2>Application Info</h2>
                <div data-template="config:app-info"/>
                <div data-template="app:last_modify"/>
            </div>
            <div class="col-md-3">
                <a href="../restricted.html?logout=true">logout here</a>
            </div>
    <!--settings.xql-->
    </div>
)

else 
    (
        let $log := util:log("info","New settings applied")
        return
        <div xmlns="http://www.w3.org/1999/xhtml" data-template="templates:surround" data-template-with="templates/page.html" data-template-at="content">
                <div class="col-md-9">
                    <h1 data-template="config:app-title">Manage data</h1>
                    <div class="row">
                        <div class="col-md-6">
                            <h1>Settings saved </h1>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <h2>Application Info</h2>
                    <div data-template="config:app-info"/>
                    <div data-template="app:last_modify"/>
                </div>
                <div class="col-md-3">
                    <a href="../restricted.html?logout=true">logout here</a>
                </div>
        <!--settings.xql-->
        </div>
    )
    
