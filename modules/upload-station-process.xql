xquery version "3.1";
let $store-collection :="/db/apps/fdsn-station/Station/"
let $store-resource :=""
let $field-name:="FileUpload"

let $stored-file as xs:string? := xmldb:store($store-collection, $store-resource, request:get-uploaded-file-data($field-name), 'application/octet-stream')
return $stored-file
    