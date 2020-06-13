xquery version "3.0";
(:import module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil"  at "modules/util.xql";:)
declare variable $exist:path external;
declare variable $exist:resource external;
declare variable $exist:controller external;
declare variable $exist:prefix external;
declare variable $exist:root external;

(::)
(:declare variable $login :=:)
(:    let $tryImport :=:)
(:        try {:)
(:            contains($exist:path, "/query/"):)
(:        } catch * {:)
(:            false():)
(:        }:)
(:    return:)
(:        if ($tryImport) then:)
(:           "":)
(:        else:)
(:            stationutil:nodata_error():)
(:;:)

(:
 
POST example:
parameter1=value :)
(:parameter2=value:)
(:NET STA LOC CHA STARTTIME ENDTIME:)
(:NET STA LOC CHA STARTTIME ENDTIME:)
(:NET STA LOC CHA STARTTIME ENDTIME:)
(:(::):)
(:curl -X POST -H 'Content-Type: application/xml' --data-binary @/tmp/person-name.xml http://localhost:8080/exist/rest/db/people:)
(:curl -X POST "http://webservices.ingv.it/fdsnws/station/1/query" -H  "accept: application/xml" -H  "Content-Type: text/plain" -d "parameter1=value parameter2=value NET STA LOC CHA STARTTIME ENDTIMENET STA LOC CHA STARTTIME ENDTIMENET STA LOC CHA STARTTIME ENDTIME":)
(:(base) stefano@excuse:/tmp$ curl -X POST "http://webservices.ingv.it/fdsnws/station/1/query" -H  "accept: application/xml" -H  "Content-Type: text/plain" --data-binary @POST.txt :)
(:<?xml version="1.0" encoding="UTF-8"?>:)
(:<FDSNStationXML xmlns="http://www.fdsn.org/xml/station/1" schemaVersion="1.0" xsi:schemaLocation="http://www.fdsn.org/xml/station/1 http://www.fdsn.org/xml/station/fdsn-station-1.0.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ingv="https://raw.githubusercontent.com/FDSN/StationXML/master/fdsn-station.xsd"><Source>SeisNet-mysql</Source><Sender>INGV-CNT</Sender><Module>INGV-CNT WEB SERVICE: fdsnws-station | version: 1.1.41.1</Module><ModuleURI>http://webservices.ingv.it/fdsnws/station/1/query</ModuleURI><Created>2020-06-10T17:32:36</Created><Network code="MN" startDate="1988-01-01T00:00:00" restrictedStatus="open"><Description>Mediterranean Very Broadband Seismographic Network</Description><ingv:Identifier>N22</ingv:Identifier><TotalNumberStations>35</TotalNumberStations><SelectedNumberStations>5</SelectedNumberStations><Station code="AQU" startDate="1988-08-01T00:00:00" restrictedStatus="open"><ingv:Identifier>S7</ingv:Identifier><Latitude>42.354</Latitude><Longitude>13.405</Longitude><Elevation>710</Elevation><Site><Name>L'Aquila, Italy</Name></Site><CreationDate>1988-08-01T00:00:00</CreationDate></Station><Station code="CII" startDate="1994-10-19T00:00:00" endDate="2006-06-23T12:00:22" restrictedStatus="open"><ingv:Identifier>S218</ingv:Identifier><Latitude>41.723</Latitude><Longitude>14.305</Longitude><Elevation>910</Elevation><Site><Name>Carovilli, Italy</Name></Site><CreationDate>1994-10-19T00:00:00</CreationDate><TerminationDate>2006-06-23T12:00:22</TerminationDate></Station><Station code="PDG" startDate="2008-07-18T00:00:00" restrictedStatus="open"><ingv:Identifier>S231</ingv:Identifier><Latitude>42.4297</Latitude><Longitude>19.2608</Longitude><Elevation>40</Elevation><Site><Name>Podgorica, Montenegro</Name></Site><CreationDate>2008-07-18T00:00:00</CreationDate></Station><Station code="TIR" startDate="1994-07-13T00:00:00" restrictedStatus="open"><ingv:Identifier>S235</ingv:Identifier><Latitude>41.3472</Latitude><Longitude>19.8631</Longitude><Elevation>247</Elevation><Site><Name>Tirana, Albania</Name></Site><CreationDate>1994-07-13T00:00:00</CreationDate></Station><Station code="VTS" startDate="1996-05-10T00:00:00" restrictedStatus="open"><ingv:Identifier>S242</ingv:Identifier><Latitude>42.618</Latitude><Longitude>23.235</Longitude><Elevation>1490</Elevation><Site><Name>Vitosha, Bulgary</Name></Site><CreationDate>1996-05-10T00:00:00</CreationDate></Station></Network></FDSNStationXML>:)
(::)
(:POST.txt:)
(:minlat=40:)
(:maxlat=43:)
(:MN * * * 2000-01-01T00:00:00.0 2020-01-01T00:00:00.0:)



if ($exist:path eq '') then
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <redirect url="{request:get-uri()}/"/>
    </dispatch>
    
else if ($exist:path eq "/") then
    (: forward root path to index.xql :)
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <redirect url="index.html"/>
    </dispatch>
else if (ends-with($exist:resource, ".html")) then
    (: the html page is run through view.xql to expand templates :)
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <view>
            <forward url="{$exist:controller}/modules/view.xql"/>
        </view>
		<error-handler>
			<forward url="{$exist:controller}/error-page.html" method="get"/>
			<forward url="{$exist:controller}/modules/view.xql"/>
		</error-handler>
    </dispatch>
(: Resource paths starting with $shared are loaded from the shared-resources app :)
else if (contains($exist:path, "/$shared/")) then
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <forward url="/shared-resources/{substring-after($exist:path, '/$shared/')}">
            <set-header name="Cache-Control" value="max-age=3600, must-revalidate"/>
        </forward>
    </dispatch>
    
(: Pass to query.xql, then filter with finish.xsl :)    
(:else if (contains($exist:path, "/query/")) then:)
(:    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">:)
(:        <set-attribute name="xquery.attribute"	value="model"/>:)
(:        <forward url="{$exist:controller}/modules/query-no-filter.xql"> :)
(:            <set-header name="Cache-Control" value="max-age=3600, must-revalidate"/>:)
(:            <view>:)
(:            <forward servlet="XSLTServlet">:)
(:                <set-attribute name="xslt.input"	value="model"/>:)
(:                <set-attribute name="xslt.stylesheet" value="{concat($exist:root, $exist:controller,"/modules/finish.xslt")}"/>:)
(:            </forward>:)
(:            </view>:)
(:            <cache-control cache="yes"/>            :)
(:         </forward>:)
(:    </dispatch> :)

(:else if (contains($exist:path, "/query/")) then:)
(:		<dispatch xmlns="http://exist.sourceforge.net/NS/exist">:)
(:			<forward url="{$exist:controller}/modules/query-no-filter.xql">:)
(:				<!-- query results are passed to XSLT servlet via request attribute -->:)
(:				<set-attribute name="xquery.attribute":)
(:					value="model"/>:)
(:			</forward>:)
(:			<view>:)
(:			    <set-header Content-Type="application/xml; charset=UTF-8" name="Cache-Control" value="max-age=60, must-revalidate"/>:)
(:				<forward servlet="XSLTServlet">:)
(:					<set-attribute name="xslt.input":)
(:						value="model"/>:)
(:					<set-attribute name="xslt.stylesheet" :)
(:						 value="{concat($exist:root, $exist:controller,"/modules/finish.xslt")}"/>:)
(:					<set-header Content-Type="application/xml; charset=UTF-8" name="Cache-Control" value="max-age=60, must-revalidate"/>	 :)
(:				</forward>:)
(:			</view>:)
(:		</dispatch>:)
(:		:)
(: Old code works without pipeline TODO filter for json, txt, error cleaning output :)
  else if ( contains($exist:path, "/query/") )  then 
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <forward url="{$exist:controller}/modules/query.xql">
            <set-header name="Cache-Control" value="max-age=3600, must-revalidate"/>
        </forward>
    </dispatch> 
  else if ( 
            contains($exist:path, "/query/") 
            and (matches(request:get-parameter("level","network"),"response") or matches(request:get-parameter("level","network"),"channel"))
            and not(matches(string-join(request:get-parameter-names()) ,"station|sta|channel|cha|location|loc|minlatitude|minlat|maxlatitude|maxlat|minlongitude|minlon|maxlongitude|maxlon|starttime|start|endtime|end|startbefore|endbefore|startafter|endafter|latitude|lat|longitude|lon|maxradius|minradius|includerestricted" ))
        ) then 
        
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <forward url="{$exist:controller}/modules/query-network-shortcut.xql">
            <set-header name="Cache-Control" value="max-age=3600, must-revalidate"/>
        </forward>
    </dispatch>
  else if (contains($exist:path, "/query/") and matches(request:get-parameter("level", "network"),"network")) then
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <forward url="{$exist:controller}/modules/query-network-level.xql">
            <set-header name="Cache-Control" value="max-age=3600, must-revalidate"/>
        </forward>
    </dispatch>  
  else if (contains($exist:path, "/query/") and matches(request:get-parameter("level", "station"),"station")) then 
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <forward url="{$exist:controller}/modules/query-station-level.xql">
            <set-header name="Cache-Control" value="max-age=3600, must-revalidate"/>
        </forward>
    </dispatch>  
  else if (contains($exist:path, "/query/") and matches(request:get-parameter("level", "station"),"channel")) then 
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <forward url="{$exist:controller}/modules/query-channel-level.xql">
            <set-header name="Cache-Control" value="max-age=3600, must-revalidate"/>
        </forward>
    </dispatch>  
  else if (contains($exist:path, "/query/") and matches(request:get-parameter("level", "station"),"response")) then 
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <forward url="{$exist:controller}/modules/query-response-level.xql">
            <set-header name="Cache-Control" value="max-age=3600, must-revalidate"/>
        </forward>
    </dispatch>  
else if (ends-with($exist:path, "application.wadl")) then		
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <forward url="{$exist:controller}/Static/ingv-application.wadl">
            <set-header Content-Type="text/plain; charset=UTF-8" name="Cache-Control" value="max-age=3600, must-revalidate"/>
        </forward>
    </dispatch>    
    
else if (ends-with($exist:path, "version")) then		
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <forward url="{$exist:controller}/Static/version.xql"/>
        <set-header Content-Type="text/plain; charset=UTF-8" />
    </dispatch>
else if (contains($exist:path, "/query/") and matches(request:get-parameter("level", "test"),"test")) then		
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <forward url="{$exist:controller}/modules/test.xql">
            <set-header Content-Type="text/plain; charset=UTF-8" name="Cache-Control" value="max-age=3600, must-revalidate"/>
            <set-header name="Cache-Control" value="max-age=3600, must-revalidate"/>
        </forward>
    </dispatch>
    
    
    
(:else if (ends-with($exist:resource, "query.xql")) then:)
(:    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">:)
(:      <view>:)
(:        <forward servlet="XSLTServlet3">:)
(:          <set-attribute name="xslt.stylesheet" value="{$exist:controller}/modules/finish.xslt"/>:)
(:        </forward>:)
(:      </view>:)
(:        <cache-control cache="no"/>:)
(:    </dispatch>:)


else
    (: everything else is passed through :)
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <cache-control cache="yes"/>
    </dispatch>


