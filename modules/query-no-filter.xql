xquery version "3.1";
import module namespace util = "http://exist-db.org/xquery/util";

declare default element namespace "http://www.fdsn.org/xml/station/1" ;
declare namespace ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd";

declare namespace request="http://exist-db.org/xquery/request";

(: Channel timespan :)
declare variable $starttime :='2012-02-04T02:22:33';
declare variable $endtime :='2022-02-04T02:22:33';

(: Station timespan :)
declare variable $startbefore :='2012-02-04T02:22:33';
declare variable $startafter :='2012-02-04T02:22:33';
declare variable $endbefore :='2022-02-04T02:22:33';
declare variable $endafter :='2022-02-04T02:22:33';

declare variable $network := 'IV';
declare variable $station := 'ACER';
declare variable $location := '--';
declare variable $channel := 'HHZ';

(:  declare variable $minlatitude := -90; :)
(:  declare variable $maxlatitude :=  90; :)
declare variable $minlongitude := -180;
declare variable $maxlongitude := 180;

declare variable $latitude :=  90;
declare variable $longitude := -180;
declare variable $minradius := 1;
declare variable $maxradius := 1;
declare variable $minradiuskm := 1;
declare variable $maxradiuskm := 1;

declare variable $level:='station';
declare variable $includerestricted:= 'false';
declare variable $format := 'xml';
declare variable $formatted:= 'false';
declare variable $nodata:= '204';
declare variable $visibility:= 'only';
declare variable $authoritative:= 'only';

declare variable $test:='test';
(: test ingv extension namespace :)

(: echo a list of all the URL parameters  :)
(:  let $parameters :=  request:get-parameter-names() :)


<FDSNStationXML xmlns="http://www.fdsn.org/xml/station/1" xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" schemaVersion="1.0" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.0.xsd">
  <Source>eXistDB</Source>
  <Sender>INGV-ONT</Sender>
  <Module>INGV-ONT WEB SERVICE: fdsnws-station | version: 1.1.50.0</Module>
  <ModuleURI>"{request:get-uri()}?{request:get-query-string()}"</ModuleURI>
  <Created>{current-dateTime()}</Created>
{
let $minlatitude := number(request:get-parameter("minlatitude","-90.0"))
let $maxlatitude := number(request:get-parameter("maxlatitude", "90.0"))
let $minlongitude := number(request:get-parameter("minlongtitude","-180.0"))
let $maxlongitude := number(request:get-parameter("maxlongitude", "180.0"))   
let $startbefore := xs:dateTime(request:get-parameter("startbefore", "6000-01-01T01:01:01"))
let $startafter := xs:dateTime(request:get-parameter("startafter", "1800-01-01T01:01:01"))
let $endbefore := xs:dateTime(request:get-parameter("endbefore", "6000-01-01T01:01:01"))   
let $endafter := xs:dateTime(request:get-parameter("endafter", "1800-01-01T01:01:01"))


for $item in collection("/db/apps/fdsn-station/Station/")

let $Latitude:= $item/FDSNStationXML/Network/Station/Latitude
let $Longitude:= $item/FDSNStationXML/Network/Station/Longitude
let $CreationDate:= $item/FDSNStationXML/Network/Station/CreationDate
let $TerminationDate:= $item/FDSNStationXML/Network/Station/TerminationDate 

 
where $Latitude  > $minlatitude and  
      $Latitude  < $maxlatitude and 
      $Longitude > $minlongitude and 
      $Longitude < $maxlongitude and 
      $CreationDate < $startbefore and 
      $CreationDate > $startafter  
    return $item/FDSNStationXML/Network       
(:    return for $net in $item/FDSNStationXML/Network:)
(:               group by $key := $net/@code:)
(:               order by $key:)
(:               return $net:)
(:    return (transform:transform($item/FDSNStationXML/Network, doc("finish.xsl"), ())):)

}   

</FDSNStationXML>

