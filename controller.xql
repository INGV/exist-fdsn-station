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
  else if ( 
            contains($exist:path, "/query/") 

            and (matches(request:get-parameter("level","network"),"response") or matches(request:get-parameter("level","network"),"channel"))
            and not(matches(string-join(request:get-parameter-names()) ,"station|sta|channel|cha|location|loc|minlatitude|minlat|maxlatitude|maxlat|minlongitude|minlon|maxlongitude|maxlon|starttime|start|endtime|end|startbefore|endbefore|startafter|endafter|latitude|lat|longitude|lon|maxradius|minradius" ))
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


