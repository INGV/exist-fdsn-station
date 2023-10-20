xquery version "3.1";

import module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil"  at "util.xql";
declare default element namespace "http://www.fdsn.org/xml/station/1";
declare namespace ingv = "https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";
declare option exist:serialize "method=xhtml media-type=text/html indent=yes";


let $cached:=cache:clear()
let $netcache:=stationutil:netcache_create()
let $log:=util:log("info","cache cleaned")


return
<div xmlns="http://www.w3.org/1999/xhtml" data-template="templates:surround" data-template-with="templates/page.html" data-template-at="content">
        <div class="col-md-9">
            <h1 data-template="config:app-title">Manage data</h1>
            <div class="row">
                <div class="col-md-6">
                    <h1>Cache cleaned</h1>
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
<!--Cache.xql-->
</div>
