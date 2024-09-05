(: 	This is the main controller for the web application. It is called from the
	XQueryURLRewrite filter configured in web.xml. :)
xquery version "3.1";

(:~ -------------------------------------------------------
    This is controlled by web.xml, for errors of the server
    while made for a specific error: example version/a=1&b=2s,
    it may work for others but message could be misleading
    ------------------------------------------------------- :)

declare namespace c="http://exist-db.org/xquery/controller";
declare namespace expath="http://expath.org/ns/pkg";

import module namespace request="http://exist-db.org/xquery/request";
import module namespace xdb = "http://exist-db.org/xquery/xmldb";
import module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil"  at "xmldb:exist:///db/apps/fdsn-station/modules/util.xql";

(:
declare variable $local:data-pkg-collection :=
    let $descriptor :=
        collection(repo:get-root())//expath:package[@name = "http://fdsn-station"]
    return
        util:collection-name($descriptor)
;
:)

(: Query data provided by data-pkg :)
(:collection($local:data-pkg-collection)//foo:)


(:
declare function local:get-fdsn-station() {
	let $path := collection(repo:get-root())//expath:package[@name = "http://fdsn-station"]
    return
        if ($path) then
            substring-after(util:collection-name($path), repo:get-root())
        else
            ()
};

declare function local:get-path() {
	let $path := collection(repo:get-root())//expath:package[@name = "http://fdsn-station"]
    return
        $path
};
:)

(:
let $log := util:log("info" , "Package collection" || $local:data-pkg-collection)
let $log := util:log("info", repo:get-root())
let $log := util:log("info", local:get-fdsn-station())
let $log := util:log("info", "PATH: " || local:get-path())
:)

let $set_error :=  response:set-status-code(400)
(:let $URI := request:get-uri():)

let $set_text_type:= util:declare-option("exist:serialize","method=text media-type=text/plain indent=no")
let $version:=stationutil:version()
return
"Error 400: Bad request

Syntax Error in Request

Usage details are available from /fdsnws/station/1/

Request:

failure parsing request

Request Submitted: " || current-dateTime() ||
"

Service version: " || $version
