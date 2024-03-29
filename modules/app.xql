xquery version "3.1";

module namespace app="http://fdsn-station/templates";
declare default element namespace "http://www.fdsn.org/xml/station/1" ;
import module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil"  at "util.xql";
import module namespace templates="http://exist-db.org/xquery/templates" ;
import module namespace config="http://fdsn-station/config" at "config.xqm";
import module namespace console="http://exist-db.org/xquery/console";
declare namespace functx = "http://www.functx.com";
declare namespace v = "http://exist-db.org/versioning";

(:import module namespace f="http://exist-db.org/fakemodule";:)
(:Comment out if versioning module not installed:)
(:import module namespace v="http://exist-db.org/versioning";:)
(:Set to 0 to hide columns related to versioning:)


declare function functx:if-empty
  ( $arg as item()? ,
    $value as item()* )  as item()* {

  if (string($arg) != '')
  then data($arg)
  else $value
 } ;


(:~
 : This is a sample templating function. It will be called by the templating module if
 : it encounters an HTML element with an attribute: data-template="app:test" or class="app:test" (deprecated).
 : The function has to take 2 default parameters. Additional parameters are automatically mapped to
 : any matching request or function parameter.
 :
 : @param $node the HTML node with the attribute which triggered this call
 : @param $model a map containing arbitrary data - used to pass information between template calls
 :)
declare function app:test($node as node(), $model as map(*)) {
    <p>Dummy template output generated by function app:test at {current-dateTime()}. The templating
        function was triggered by the data-template attribute <code>data-template="app:test"</code>.</p>
};

(:TODO FIX the upload:)
declare function app:upload($node as node(), $model as map(*)) {
        <form enctype="multipart/form-data" method="post" action="modules/upload-station-process.xql">
            <p>Upload binary file:
            <input type="file" size="80" name="FileUpload"/>
            <br/>
            <input type="submit"/>
            </p>
        </form>
};

declare function app:login($node as node(), $model as map(*)) {
    <div>
      <form class="form" id="form" action="restricted.html" method="post">
        <input type="hidden" name="origin" value="origin" autocomplete="on"/>
        <input label="User ID" id="user" name="user" autofocus="autofocus" required="required" error="Please input your username"/>
        <input label="Password" type="password" id="password" name="password" error="Please input your password"/>
        <button type="submit" on-click="_handleSubmit">Sign me in</button>
      </form>
    </div>
};


declare function app:show-station-list($node as node(), $model as map(*)) {

(:    console:log("Entered show-station-list function"),:)
try {
let $versioning_module := fn:load-xquery-module("http://exist-db.org/versioning")
let $variables :=  $versioning_module("variables")
let $functions :=  $versioning_module("functions")
let $history := $versioning_module?functions?(xs:QName("v:history"))?1
let $revisions := $versioning_module?functions?(xs:QName("v:revisions"))?1
let $dates:=$versioning_module?functions?(xs:QName("v:dates"))?1
let $loaded:=true()

return
<table>
    <thead>
        <tr>
            <th>Network</th>
            <th>Station</th>
            <th>XML</th>
{
                for $col in ("Revisions", "Date")
                return <th>{$col}</th>
}
        <th class="scrollbarhead"></th>
        </tr>
    </thead>
    <tbody>
{

for $network in collection($stationutil:station_collection)//Network
(:       let $uri := base-uri($station):)
    let $networkcode := $network/@code
(: station[1] to cope station with more periods   :)
    for $station in $network/Station[1]
        let $stationcode:=$station/@code
        let $uri := replace(base-uri($station),'db','exist')
        let $station_basename:= util:unescape-uri(replace(base-uri($station), '.+/(.+)$', '$1'),'UTF-8')
        (:Comment out if versioning module not installed:)
        let $station_history:= parse-xml-fragment( $history(doc($stationutil:station_collection || $stationcode || ".xml")) )
        let $revisions := $revisions(doc($stationutil:station_collection || $stationcode || ".xml"))
        let $dates := $dates(doc($stationutil:station_collection || $stationcode || ".xml"))
(:                let $dates := v:dates(doc($stationutil:station_collection || $stationcode || ".xml")):)
        (:Comment out if versioning module not installed:)
    group by $network
    order by $stationcode
    return
(:Comment out revisions and dates if versioning module is missing :)
<tr>
    <td>{string($networkcode)}</td>
    <td>{string($stationcode)}</td>
    <td><a href= "{string($uri)}">"{$station_basename}"</a></td>
    <td>{functx:if-empty(max($revisions),"0")}</td>
    <td>{functx:if-empty(max($dates),"2021-01-01T00:00:00.0000")}</td>
</tr>

}
</tbody>
</table>

}
catch err:* {

(:<table class="tableSection">:)
<table>
    <thead>
        <tr>
            <th>Network</th>
            <th>Station</th>
            <th>XML</th>
            <th class="scrollbarhead"></th>
        </tr>
    </thead>
    <tbody>
{

    for $network in collection($stationutil:station_collection)//Network
    let $networkcode := $network/@code
    let $networkstartdate := $network/@startDate
    for $station in $network/Station
        let $stationcode:=$station/@code
        let $startdate:=$station/@startDate
(:        let $log := (if (fn:count($networkcode)=1) then stationutil:log("info", $networkcode[1] || " " || $stationcode[1]) else ()):)
        let $uri := replace(base-uri($station),'db','exist')
        let $station_basename:= util:unescape-uri(replace(base-uri($station), '.+/(.+)$', '$1'),'UTF-8')

    group by $networkcode, $networkstartdate, $stationcode, $startdate, $uri, $station_basename
    order by $networkcode, $station_basename

    return

<tr>
    <td>{string($networkcode)}</td>
    <td>{string($stationcode)}</td>
    <td><a href= "{string($uri)}">{$station_basename}</a></td>

</tr>

}
</tbody>
</table>
}


};


declare function app:search($node as node(), $model as map(*)) {
    <div>
    <h2>Search by station code</h2>
        <form class="form" id="search" method="POST" action="/exist/apps/fdsn-station/modules/search.xql">
            <input type="text" name="searchphrase" size="6"/>
            <input type="submit" value="Search"/>
        </form>
    </div>
};


declare function app:purge($node as node(), $model as map(*)) {
    <div>
    <h2>Purge database</h2>
    <h3>Beware all data will be erased !! </h3>
        <form class="form" id="purge" method="GET" action="/exist/apps/fdsn-station/modules/purge.xql">
            <input type="submit" value="Purge"/>
        </form>
    </div>
};

declare function app:fix($node as node(), $model as map(*)) {
    <div>
    <h2>Fix database</h2>
    <h3>Try to fix database collections, beware you are tampering updatedafter information</h3>
        <form class="form" id="fix" method="GET" action="/exist/apps/fdsn-station/modules/fix.xql">
            <input type="submit" value="Fix"/>
        </form>
    </div>
};

declare function app:cache($node as node(), $model as map(*)) {
    <div>
    <h2>Cache clean</h2>
    <h3>Empty cached application data</h3>
        <form class="form" id="cache" method="GET" action="/exist/apps/fdsn-station/modules/cache.xql">
            <input type="submit" value="Empty"/>
        </form>
    </div>
};

declare function app:touch($node as node(), $model as map(*)) {
    <div>
    <h2>Touch database</h2>
    <h3>Reset creation date to current</h3>
        <form class="form" id="cache" method="GET" action="/exist/apps/fdsn-station/modules/touch.xql">
            <input type="submit" value="Touch"/>
        </form>
    </div>
};


declare function app:settings($node as node(), $model as map(*)) {
    <div>
    <h2>Configure</h2>
    <h3>Modify configuration</h3>
    <div class="col-md-6">   
        <form class="form" id="cache" method="GET" action="/exist/apps/fdsn-station/modules/settings.xql">
                <div class="form-check">  
                {
                if ($stationutil:settings("enable_log")) then
                  <input class="form-check-input" type="checkbox" name="enable_log" id="enable_log" checked="checked">
                  <label class="form-check-label" for="enable_log">
                    Enable log
                  </label>
                 </input> 
                 else
                  <input class="form-check-input" type="checkbox" name="enable_log" id="enable_log">
                  <label class="form-check-label" for="enable_log">
                    Enable log
                  </label>
                 </input> 
                } 
                </div>
                <div class="form-check">
                {
                if ($stationutil:settings("enable_debug")) then
                  <input class="form-check-input" type="checkbox" name="enable_debug" id="enable_debug" checked="checked">
                  <label class="form-check-label" for="enable_debug">
                    Enable debug
                  </label>
                 </input> 
                 else
                     <input class="form-check-input" type="checkbox" name="enable_debug" id="enable_debug">
                  <label class="form-check-label" for="enable_debug">
                    Enable debug
                  </label>
                 </input>   
                }
                </div>
                <div class="form-check">
                {
                 if ($stationutil:settings("enable_query_log")) then
                  <input class="form-check-input" type="checkbox" name="enable_query_log" id="enable_query_log" checked="checked"  >
                  <label class="form-check-label" for="enable_query_log">
                    Enable query log
                  </label>
                 </input> 
                 else
                    <input class="form-check-input" type="checkbox" name="enable_query_log" id="enable_query_log"  >
                  <label class="form-check-label" for="enable_query_log">
                    Enable query log
                  </label>
                 </input> 
                }
             </div>
                 <input type="submit" value="Apply changes"/>
        </form>
        </div>
    </div>
};


declare function app:last_modify($node as node(), $model as map(*)) {
    <p>
        Now {current-dateTime()}
        Database last modified on {
            let $resources := xmldb:get-child-resources($stationutil:station_collection)
            return max(
                for $resource in $resources
                return xmldb:last-modified($stationutil:station_collection,$resource)
            )
        }
    </p>


};


