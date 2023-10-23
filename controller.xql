xquery version "3.0";
import module namespace login="http://exist-db.org/xquery/login" at "resource:org/exist/xquery/modules/persistentlogin/login.xql";
import module namespace console="http://exist-db.org/xquery/console";
import module namespace templates="http://exist-db.org/xquery/templates";

declare variable $exist:path external;
declare variable $exist:resource external;
declare variable $exist:controller external;
declare variable $exist:prefix external;
declare variable $exist:root external;

console:log("controller path: " || $exist:path),
if ($exist:path eq '') then
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <redirect url="{request:get-uri()}/"/>
    </dispatch>
else if ($exist:path = "/") then(
    console:log("matched '/'" || $exist:path),
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <redirect url="index.html"/>
    </dispatch>
)


(:
    restricted.html is secured by the following rules
:)
else if (ends-with($exist:path, "restricted.html") or ends-with($exist:path,".xql")) then (
        (: login:set-user creates a authenticated session for a user :)
        login:set-user("org.exist.login", (), true()),

        (:
        the login:set-user function internally sets the following request attribute. If this is set we have a logged in
        user.
        :)
        let $user := request:get-attribute("org.exist.login.user")

        (: when the request comes in with a user request param the request was sent by a login form :)
        let $userParam := request:get-parameter("user","")

        (: in case of a logout we get a request param 'logout' :)
        let $logout := request:get-parameter("logout",())
        (:let $result := if (not($userParam != data($user))) then "true" else "false":)

        return
            (:
            when we get a logout the user is redirected to the index.html page in this example. The redirect target
            can be changed to application needs. E.g. redirecting to restricted.html here would pop up the login page
            again as the user is not logged in any more.
            :)
            if($logout = "true") then(
                (:
                When there is a logout request parameter we send the user back to the unrestricted page.
                :)
                <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
                    <redirect url="index.html"/>
                </dispatch>
            )
            else if ($user and sm:is-dba($user)) then
               (

                if (ends-with($exist:path,".xql")) then
                <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
                        <view>
                        <forward url="{$exist:controller}/modules/view.xql"/>
                        </view>
                		<error-handler>
			                <forward url="{$exist:controller}/error-page.html" method="get"/>
		                  	<forward url="{$exist:controller}/modules/view.xql"/>
                		</error-handler>
                </dispatch>

                else
                (:
                successful login. The user has authenticated and is in the 'dba' group. It's important however to keep
                the cache-control set to 'cache="no"'. Otherwise re-authentication after a logout won't be forced. The
                page will get served from cache and not hit the controller any more.
                :)
                <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
                    <cache-control cache="no"/>
                        <view>
                        <forward url="{$exist:controller}/modules/view.xql"/>
                        </view>
                		<error-handler>
			                <forward url="{$exist:controller}/error-page.html" method="get"/>
		                  	<forward url="{$exist:controller}/modules/view.xql"/>
                		</error-handler>
                </dispatch>
               )
            else if(not(string($userParam) eq string($user))) then
                (:
                if a user was send as request param 'user'
                AND it is NOT the same as $user
                a former login attempt has failed.

                Here a duplicate of the login.html is used. This is certainly not the most elegant solution. Just here
                to not complicate things further with templating etc.
                :)
                <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
                    <forward url="/fdsn-station/fail.html"/>
                        <view>
                            <forward url="{$exist:controller}/modules/view.xql"/>
                        </view>
                </dispatch>
            else
                (: if nothing of the above matched we got a login attempt. :)
                <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
                    <forward url="/fdsn-station/login.html"/>
                        <view>
                            <forward url="{$exist:controller}/modules/view.xql"/>
                        </view>
                </dispatch>
)


else





(:import module namespace stationutil="http://exist-db.org/apps/fdsn-station/modules/stationutil"  at "modules/util.xql";:)
(:declare variable $exist:path external;:)
(:declare variable $exist:resource external;:)
(:declare variable $exist:controller external;:)
(:declare variable $exist:prefix external;:)
(:declare variable $exist:root external;:)



if ($exist:path eq '') then (
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <redirect url="{request:get-uri()}/"/>
    </dispatch>
)
else if ($exist:path eq "/") then (
    (: forward root path to index.xql :)
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <redirect url="index.html"/>
    </dispatch>
)
else if (ends-with($exist:resource, ".html")) then (
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
)
(: Resource paths starting with $shared are loaded from the shared-resources app :)
else if (contains($exist:path, "/$shared/")) then (
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <forward url="/shared-resources/{substring-after($exist:path, '/$shared/')}">
            <set-header name="Cache-Control" value="max-age=3600, must-revalidate"/>
        </forward>
    </dispatch>
)
  else if ( $exist:path = "/fdsnws/station/1/query")  then (
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <forward url="{$exist:controller}/modules/query.xql">
            <set-header name="Cache-Control" value="max-age=60, must-revalidate"/>
            <!--<set-header name="PATH" value="query.xql"/>-->
        </forward>
    </dispatch>
)
else if ($exist:path = "/fdsnws/station/1/application.wadl") then (
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <forward url="{$exist:controller}/Static/application-wadl.xml">
            <set-header name="Content-Type"  value="application/xml; charset=UTF-8" />
            <set-header name="Cache-Control" value="max-age=3600, must-revalidate"/>
        </forward>
    </dispatch>
)
else if ($exist:path = "/fdsnws/station/1/swagger.json") then (
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <forward url="{$exist:controller}/Static/application-Swagger20.json">
            <set-header name="Content-Type"  value="application/json; charset=UTF-8" />
            <set-header name="Cache-Control" value="max-age=3600, must-revalidate"/>
        </forward>
    </dispatch>
)
else if ($exist:path = "/fdsnws/station/1/version") then (
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <forward url="{$exist:controller}/modules/version.xql">
        <set-header name="Content-Type"  value="text/plain; charset=UTF-8" />
        <set-header name="Cache-Control" value="max-age=3600, must-revalidate" />
<!-- Passed to version.xql took by request:getparam-->
<!--        <add-parameter name="exist_path" value="{$exist:path}"/>-->
<!-- Passed in response -->
<!--        <set-header name="Exist-path" value="{$exist:path}"/>-->
        </forward>
    </dispatch>
)
else if ( $exist:path = "/virtualnetwork/1/codes" )  then (
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <forward url="{$exist:controller}/modules/virtualnetwork.xql">
            <set-header name="Cache-Control" value="max-age=300, must-revalidate"/>
            <!--<set-header name="Exist-path"    value="{$exist:path}"/>-->
        </forward>
    </dispatch>
)
else if ( $exist:path = "/fdsnws/station/1/test" )  then (
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <forward url="{$exist:controller}/modules/test.xql">
            <!--<set-header name="Cache-Control" value="max-age=60, must-revalidate"/>-->
            <!--<set-header name="Exist-path"    value="{$exist:path}"/>-->
        </forward>
    </dispatch>
)
else if ( $exist:path = "/fdsnws/station/1/" )  then (
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <set-header name="Content-Type"  value="text/html; charset=UTF-8" />
        <!--<forward url="{$exist:controller}/static/doc_index.html" method="get"/>-->
        <forward url="{$exist:controller}/modules/document_index.xql" method="get"/>
    </dispatch>
)
else if (ends-with($exist:resource, ".xml") ) then (
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
<!--        <view> TODO REMOVE view_xml.xql-->
            <!-- pass the results through view_xml.xql to display xml resources in browser-->
<!--            <forward url="{$exist:controller}/modules/view_xml.xql">
            <set-header name="Content-Type"  value="application/xml; charset=UTF-8" />
            <set-attribute name="$exist:prefix" value="{$exist:prefix}"/>
            <set-attribute name="$exist:controller" value="{$exist:controller}"/>
            </forward>
        </view> -->
        <error-handler>
            <forward url="{$exist:controller}/error-page.html" method="get"/>
            <forward url="{$exist:controller}/modules/view.xql">
                <set-header name="XML-PASS" value="valore"/>
            </forward>
        </error-handler>
  </dispatch>
)
else if (ends-with($exist:resource, ".css"))  then (
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <set-header name="Content-Type"  value="text/css; charset=UTF-8" />
        <!--<forward url="{$exist:controller}/static/doc_index.html" method="get"/>-->
    </dispatch>
)
(: everything else is error :)
else

    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
		<forward url="{$exist:controller}/modules/errors.xql" method="get">
		</forward>
    </dispatch>



(:Nel blocco forward :)
(:            <set-header name="Exist-path" value="{$exist:path}"/>:)
(:            <set-header name="Exist-resource" value="{$exist:resource}"/>:)
(:            <set-header name="Exist-root" value="{$exist:root}"/>:)
(:            <set-header name="Exist-prefix" value="{$exist:prefix}"/>:)
(:            <set-header name="Exist-controller" value="{$exist:controller}"/>:)
(:Exist-controller: /fdsn-station:)
(:Exist-path: /fdsnws/station/1/query:)
(:Exist-prefix: /apps:)
(:Exist-resource: query:)
(:Exist-root: xmldb:exist:///db/apps:)
(:         <forward url="{$exist:controller}/modules/view.xql">:)
(:            <set-header name="Cache-Control" value="max-age=60, must-revalidate"/>:)
(:            <set-header name="Exist-path"    value="{$exist:path}"/>:)
(:        </forward>:)
