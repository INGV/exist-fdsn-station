(: 	This is the main controller for the web application. It is called from the
	XQueryURLRewrite filter configured in web.xml. :)
xquery version "3.0";

(:~ -------------------------------------------------------
    Main controller: handles all requests not matched by
    sub-controllers.
    ------------------------------------------------------- :)

declare namespace c="http://exist-db.org/xquery/controller";
declare namespace expath="http://expath.org/ns/pkg";

import module namespace request="http://exist-db.org/xquery/request";
import module namespace xdb = "http://exist-db.org/xquery/xmldb";
(: import module namespace prefix="stationutil" at "/exist/apps/fdsn-station/modules/util.xql"; :)

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






(: let $log := util:log("info", repo:get-root()) :)
(: let $log := util:log("info", local:get-fdsn-station()) :)
(: let $log := util:log("info", "PATH: " || local:get-path()) :)
let $set_error :=  response:set-status-code(400)
let $URI := request:get-uri()

let $set_text_type:= util:declare-option("exist:serialize","method=text media-type=text/plain indent=no")
return
"Error 400: Bad request

Syntax Error in Request

Usage details are available from /fdsnws/station/1/

Request:

failure parsing request

Request Submitted: " || current-dateTime() ||
"

Service version: 1.1.56
"


(: stationutil:other_error() :)
(:
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <title>Page not found</title>
        <link rel="shortcut icon" href="resources/exist_icon_16x16.ico" />
        <link rel="icon" href="resources/exist_icon_16x16.png" type="image/png" />
    </head>
    <body>
        <div id="logo">
            <img src="logo.jpg" title="eXist-db: Open Source Native XML Database" alt="Logo"/>
        </div>
        <div id="content">
            <h1>Page Not Found</h1>
            
            <p>The requested page could not be found, probably because the application is not
                installed. Please use the <a href="/exist/apps/fdsn-station/modules/error.xql">dashboard</a> to install
                missing application packages.</p>
        </div>
    </body>
</html>
:)

(: 
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <title>Page not found</title>
        <link rel="shortcut icon" href="resources/exist_icon_16x16.ico" />
        <link rel="icon" href="resources/exist_icon_16x16.png" type="image/png" />
    </head>
    <body>
        <div id="logo">
            <img src="logo.jpg" title="eXist-db: Open Source Native XML Database" alt="Logo"/>
        </div>
        <div id="content">
            <h1>Page Not Found</h1>
            
            <p>The requested page could not be found, probably because the application is not
                installed. Please use the <a href="apps/dashboard/">dashboard</a> to install
                missing application packages.</p>
        </div>
    </body>
</html>

:)
