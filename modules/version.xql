xquery version "3.1";
import module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil"  at "../modules/util.xql";

declare option exist:serialize "method=text media-type=text/plain";

stationutil:version()

