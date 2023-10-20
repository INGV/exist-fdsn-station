xquery version "3.1";

let $xml:=doc("/db/apps/fdsn-station/Static/ingv-application-wadl.xml")

return transform:transform($xml, doc("wadl.xsl"), ())
