xquery version "3.1";

module namespace app="http://fdsn-station/templates";
declare default element namespace "http://www.fdsn.org/xml/station/1" ;
import module namespace templates="http://exist-db.org/xquery/templates" ;
import module namespace config="http://fdsn-station/config" at "config.xqm";
import module namespace console="http://exist-db.org/xquery/console";

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


    console:log("Entered show-station-list function"),

<table class="tableSection">
    <thead>
        <tr>
            <th><span class="text">Network</span>

            </th>
            <th><span class="text">Station</span>

            </th>
            <th><span class="test">XML</span>

            </th>
            
        </tr>
    </thead>
    <tbody>
{
for $network in collection("/db/apps/fdsn-station/Station/")//Network
(:       let $uri := base-uri($station):)
    let $networkcode := $network/@code
    for $station in $network/Station
        let $stationcode:=$station/@code
        let $uri := replace(base-uri($station),'db','exist')
        let $station_basename:= util:unescape-uri(replace(base-uri($station), '.+/(.+)$', '$1'),'UTF-8')
    group by $network
    order by $stationcode
    return
<tr>    
    <td> {string($networkcode)}  </td>
    <td> {string($stationcode)}  </td>
    <td> <a href= "{string($uri)}"> "{$station_basename}" </a> </td>
</tr>

}
</tbody>
</table>
};


declare function app:search($node as node(), $model as map(*)) {
    <div>
    <h3>Search using index:</h3>
        <form class="form" id="search" method="POST" action="modules/search.xql">
            <input type="text" name="searchphrase" size="40"/>
            <input type="submit" value="Search!"/>
        </form>
    </div>
};

(:        name="{util:unescape-uri(replace($uri, ".+/(.+)$","$1"), "UTF-8")}"> :)
(:        { :)
(:            $resource//Station/text() :)
(:        } :)
(:        </div> :)
