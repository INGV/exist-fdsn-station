xquery version "3.1";

import module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil"  at "util.xql";
declare default element namespace "http://www.fdsn.org/xml/station/1";
declare namespace ingv = "https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";
declare option exist:serialize "method=xhtml media-type=text/html indent=yes";


let $data-collection := $stationutil:station_collection
let $stationcode := request:get-parameter('searchphrase', "")

(:let $log := util:log("info", "Searching station: " || $stationcode):)

let $search-results :=
    for $network in collection( $data-collection)//Station[@code = $stationcode]/..
    let $station := $network//Station
    let $uri := replace(base-uri($station), 'db', 'exist')
    (: let $station_basename:= util:unescape-uri(replace(base-uri($station), '.+/(.+)$', '$1'),'UTF-8') :)
    (: let $log := util:log("info", "Found uri: " || $uri):)
    let $code := $station/@code
    where $code = $stationcode
    return $uri
let $count := count($search-results)

return
<div xmlns="http://www.w3.org/1999/xhtml" data-template="templates:surround" data-template-with="templates/page.html"
    data-template-at="content">
        <div class="col-md-9">
            <h1 data-template="config:app-title">Stations Search Results</h1>
        <div class="row">
            <div class="col-md-3">
                    <div data-template="app:search"/>
            </div>
        </div>
            <div class="row">
                <div class="col-md-6">
                    <p>Station Search Results </p>
                    <p>
                        <b>Search results for:</b>&quot;{ $stationcode }&quot;
                    </p>
                    <p><b>Terms Found: </b>{ $count }</p>
                    <ol>
    {
        for $term in $search-results
        let $id := $term
        order by upper-case($id)
        return
                            <li>
                               <a href= "{ $term }">"{ replace($term, '.+/(.+)$', '$1') }"</a>
                            </li>
    }

                    </ol>
                    <a href="../restricted.html">Home</a>
                </div>
            </div>


        </div>
         <div class="row">
       <div class="col-md-3">
            <h2>Application Info</h2>
            <div data-template="config:app-info"/>
        </div>

         </div>
</div>
