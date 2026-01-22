xquery version "3.1";

declare default element namespace "http://www.fdsn.org/xml/station/1";
declare namespace ingv    = "https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";
declare namespace request = "http://exist-db.org/xquery/request";
declare namespace response= "http://exist-db.org/xquery/response";
declare namespace output  = "http://www.w3.org/2010/xslt-xquery-serialization";
declare namespace json    = "http://www.json.org";
declare option output:method "xml";
declare option output:media-type "text/xml";
declare option output:indent "no";
declare option output:omit-xml-declaration "no";

import module namespace login       = "http://exist-db.org/xquery/login"
  at "resource:org/exist/xquery/modules/persistentlogin/login.xql";
import module namespace stationutil = "http://exist-db.org/apps/fdsn-station/modules/stationutil"
  at "util.xql";
import module namespace mgmt        = "http://exist-db.org/apps/fdsn-station/modules/management.xqm"
  at "management.xqm";

(: ---------- AUTHORIZATION ---------- :)
declare function local:authorize($user as xs:string) as item()? {
  if ($user = "fdsndba") then () else stationutil:authorization_error()
};

(: ---------- ROUTER ENUMERATION ---------- :)
declare function local:route($endpoint as xs:string) as xs:string {
  let $e := lower-case($endpoint)
  return
    if (contains($e, "management/settings/keys")) then "settings-keys"
    else if (contains($e, "management/settings/")) then "settings-key"
    else if (contains($e, "management/settings"))  then "settings"
    else if (contains($e, "network"))              then "network"
    else if (contains($e, "database/purge"))                then "purge"
    else if (contains($e, "database/cache_clean"))          then "cache_clean"
    else if (contains($e, "database/fix"))         then "database-fix"
    else if (contains($e, "database/touch"))       then "database-touch"
    else if (contains($e, "database/change_date_format")) then "database-change-date-format"
    else ""
};
(: ---------- SETTINGS defaults/storage ---------- :)
declare function local:settings-path() as map(*) {
  map { "collection": "/db/apps/fdsn-station/config", "resource": "settings.json" }
};

declare function local:default-settings() as map(*) {
  map {
    "enable_query_log": true(),
    "enable_check_validity": true(),
    "enable_debug": false(),
    "fix_restrictedStatus": true(),
    "remove_tz": false(),
    "sender": "INGV-ONT",
    "serialize_input": false(),
    "post_limit_rows": 1000,
    "strip_zero": false(),
    "restrictedStatus_closeable": true(),
    "expose_db": true(),
    "source": "eXistDB",
    "translate_units": true(),
    "enable_log": true()
  }
};

(:TODO Evaluate removal of defaults:)
declare function local:load-settings() as map(*) {
  let $p := local:settings-path()
  let $col := $p("collection")
  let $res := $p("resource")
  return
    try {
      let $doc := json-doc(concat($col, "/", $res))
      let $log := if (exists($doc)) then  stationutil:log('info', "Settings from: " || $col || "/"  || $res) else stationutil:log('info', "Settings not found in: " || $col || "/"  || $res)
      return if (exists($doc)) then $doc
             else local:default-settings()
    } catch * { local:default-settings() }
};

declare function local:save-settings($m as map(*)) as map(*) {
  let $p := local:settings-path()
  let $col := $p("collection")
  let $res := $p("resource")
  let $log :=stationutil:log('info', "Settings from: " || $col || "/"  || $res)
  let $json := serialize($m, map{"method":"json","indent":true()})
  let $mkcol :=
    if (xmldb:collection-available($col)) then ()
    else xmldb:create-collection(replace($col, "^(/db)(.*)$", "$1"), replace($col, "^/db/?", ""))
  let $store := xmldb:store($col, $res, $json, "application/json")
  return $m
};

(: ---------- VALIDAZIONE TIPI ---------- :)
declare function local:boolean-keys() as xs:string* {
  ("enable_query_log","enable_check_validity","enable_debug","fix_restrictedStatus",
   "remove_tz","serialize_input","strip_zero","restrictedStatus_closeable",
   "expose_db","translate_units","enable_log")
};

declare function local:is-integer($n as item()) as xs:boolean {
  typeswitch($n)
    case xs:integer return true()
    case xs:double  return (not($n = xs:double('NaN')) and floor($n) = $n)
    case xs:decimal return (floor($n) = $n)
    default         return false()
};

declare function local:valid-entry($k as xs:string, $v as item()) as xs:boolean {
  if ($k = local:boolean-keys()) then
    $v instance of xs:boolean
  else
    ( $v instance of xs:string or local:is-integer($v) )
};

declare function local:validate-settings($m as map(*)) as xs:boolean {
  every $k in map:keys($m) satisfies local:valid-entry($k, $m($k))
};

(: ---------- /management/settings (GET/PUT) ---------- :)
declare function local:handle_settings() as item()* {
  let $method := request:get-method()
  return
    switch ($method)
      case "GET" return
        let $_ := util:declare-option("exist:serialize", "method=json media-type=application/json indent=yes")
        return local:load-settings()
      case "PUT" return
        let $raw := request:get-data()
        let $body := try { fn:parse-json($raw) } catch * { fn:parse-json(util:base64-decode($raw)) }
        return
          if ($body instance of map(*) and local:validate-settings($body)) then (
            local:save-settings($body),
            util:declare-option("exist:serialize", "method=json media-type=application/json indent=yes"),
            $body
          )
          else stationutil:other_error()
      default return stationutil:other_error()
};

(: ---------- /management/settings/keys (GET) ---------- :)
declare function local:handle_settings_keys() as item()* {
  let $cfg  := local:load-settings()
  let $keys := map:keys($cfg)
  let $_    := util:declare-option("exist:serialize", "method=json media-type=application/json indent=yes")
  return array { $keys }
};

(: ---------- helper: extract {key} from /management/settings/{key}[?...] ---------- :)
declare function local:extract-settings-key($endpoint as xs:string) as xs:string? {
  let $after := replace($endpoint, "^.*?/management/settings/", "")
  let $seg   := tokenize($after, "/|\?")[1]
  return $seg
};

(: ---------- /management/settings/{key} (GET/PUT/DELETE) ---------- :)
declare function local:handle_settings_key($endpoint as xs:string) as item()* {
  let $key := local:extract-settings-key($endpoint)
  return
    if (empty($key)) then stationutil:other_error()
    else
      let $method := request:get-method()
      let $cfg0 := local:load-settings()
      return
        switch ($method)
          case "GET" return
            if (map:contains($cfg0, $key)) then (
              util:declare-option("exist:serialize", "method=json media-type=application/json indent=yes"),
              $cfg0($key)
            )
            else stationutil:other_error()
          case "PUT" return
            let $raw := request:get-data()
            let $val := try { fn:parse-json($raw) } catch * { fn:parse-json(util:base64-decode($raw)) }
            return
              if (local:valid-entry($key, $val)) then (
                util:declare-option("exist:serialize", "method=json media-type=application/json indent=yes"),
                local:save-settings(map:put($cfg0, $key, $val))
(:                ,:)
(:                map:put($cfg0, $key, $val):)
              )
              else stationutil:other_error()
          default return stationutil:other_error()
};

(: ---------- NETWORK handler  ---------- :)
declare function local:handle_network() as item()* {
  let $code       := request:get-parameter('code', '')
  let $converted  := stationutil:time_adjust(request:get-parameter('startDate', ''))
(:  let $time       := xs:time(xs:dateTime($converted)):)
(:  let $date       := xs:date(xs:dateTime($converted)):)
(:  let $datetime   := dateTime($date, $time):)
(:  let $startDate0 := fn:adjust-dateTime-to-timezone($datetime, ()):)
(:  let $log0       := stationutil:debug("info", "startdate: " || $startDate0 || " - converted: " || $converted):)
  let $startDate  := $converted
  let $content    := request:get-data()
  let $decoded    := util:base64-decode($content)
  let $xml        := fn:parse-xml($decoded)
  let $netcode    := $xml//Network/@code
  let $netstart   := $xml//Network/@startDate
  let $netend     := if (exists($xml//Network/@endDate)) then stationutil:time_adjust($xml//Network/@endDate) else ()
  let $log1       := util:log("info", "startDate: " || string-join($startDate) || " endDate: " || string-join($netend))
  let $status     := $xml//Network/@restrictedStatus
  return
    try {
        if (request:get-method() eq "PUT" and $netcode = $code and ($status = "open" or $status = "closed"))
        then
          mgmt:bulkmodify($code, $startDate, $netend, $xml)
        else
          stationutil:other_error()
    }
    catch err:* {
      let $error := stationutil:internal_error($err:code || " " || $err:description)
      return $error || "
" || $err:code || " " || $err:description
    }
};


(: ---------- /management/database/purge ---------- :)
declare function local:handle_purge() {
  if (request:get-method() ne "DELETE") then
    stationutil:method-not-allowed_error("DELETE")
  else
    if (exists(stationutil:purge())) then (
        util:declare-option("exist:serialize", "method=json media-type=application/json indent=yes"),
        response:set-status-code(200)
      )
      else (
        util:declare-option("exist:serialize", "method=json media-type=application/json indent=yes"),
        response:set-status-code(204)
      )
};

(: ---------- /management/database/cache_clean ---------- :)
declare function local:handle_cache_clean() {
  if (request:get-method() ne "POST") then
    stationutil:method-not-allowed_error("POST")
  else
    if (exists(stationutil:netcache_create())) then (
(:        util:declare-option("exist:serialize", "method=json media-type=application/json indent=yes"),:)
        response:set-status-code(200),
        "Database cache clean completed."
      )
      else (
(:        util:declare-option("exist:serialize", "method=json media-type=application/json indent=yes"),  :)
        response:set-status-code(204),
        "No changes required."
      )
};

(: ---------- /management/database/fix ---------- :)
declare function local:handle_database_fix() as item()* {
  let $log:=util:log("info", "Database fix requested — may alter 'updatedafter' timestamps.")
  return
  if (request:get-method() ne "POST") then
    stationutil:method-not-allowed_error("POST")
  else (
    let $res := exists(stationutil:fix_collections())
    return
      if ($res) then (
        util:declare-option("exist:serialize", "method=json media-type=application/json indent=yes"),
        response:set-status-code(200),
        "Database fix completed."
      )
      else (
        util:declare-option("exist:serialize", "method=json media-type=application/json indent=yes"),
        response:set-status-code(204),
        "No changes required."
      )
  )
};

(: ---------- /management/database/touch ---------- :)
declare function local:handle_database_touch() as item()* {
  let $log:= util:log("info", "Database touch requested — resetting creation dates.")
  return
  if (request:get-method() ne "POST") then
    stationutil:method-not-allowed_error("POST")
  else (
(:    let $res := stationutil:touch_collections(current-dateTime()):)
    let $res := stationutil:touch_collections()
    return
      if ($res) then (
        response:set-status-code(200),
        "Creation dates reset successfully."
      )
      else (
        response:set-status-code(204),
        "No documents found to update."
      )
  )
};

(: ---------- /management/database/change_dateformat ---------- :)
declare function local:handle_database_change_date_format() as item()* {
  if (request:get-method() ne "POST") then
    stationutil:method-not-allowed_error("POST")
  else (
    let $settings := local:load-settings(),
        $tz := map:get($settings, "remove_tz"),
        $strip := map:get($settings, "strip_zero"),
        $res := stationutil:rewrite_collections_change_dates()
    return
      if ($res) then (
        response:set-status-code(200),
        concat("Date format corrected (TZ=", $tz, ", strip_zero=", $strip, ").")
      )
      else (
        response:set-status-code(204),
        "No date fields required correction."
      )
  )
};

(: ---------- MAIN ROUTER ---------- :)
let $endpoint := request:get-url()
let $user     := sm:id()
let $auth     := local:authorize($user)
return
  if (exists($auth)) then $auth
  else
    let $route := local:route($endpoint)
    let $log := stationutil:debug("info","Requested "  || $endpoint || " parameters: " || string-join(request:get-parameter-names()))
    return
      switch ($route)
        case "settings-keys"           return local:handle_settings_keys()
        case "settings"                return local:handle_settings()
        case "settings-key"            return local:handle_settings_key($endpoint)
        case "network"                 return local:handle_network()
        case "purge"                   return local:handle_purge()
        case "cache_clean"             return local:handle_cache_clean()
        case "database-fix"            return local:handle_database_fix()
        case "database-touch"          return local:handle_database_touch()
        case "database-change-date-format" return local:handle_database_change_date_format()
        default                        return ()
