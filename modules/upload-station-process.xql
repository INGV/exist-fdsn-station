xquery version "3.1";
(: Manage upload :)
let $store-collection :="/db/apps/fdsn-station/Station/"

let $field-name:="FileUpload"
let $store-resource :=request:get-uploaded-file-name($field-name)

let $stored-file as xs:string? := xmldb:store($store-collection, $store-resource, request:get-uploaded-file-data($field-name), 'application/octet-stream')
return $stored-file
    