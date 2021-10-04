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


(:else if (ends-with($exist:path, "restricted.html")) then ( :)
(:    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">:)
(:        <view>:)
(:            <forward url="{$exist:controller}/modules/view.xql"/>:)
(:        </view>:)
(:		<error-handler>:)
(:			<forward url="{$exist:controller}/error-page.html" method="get"/>:)
(:			<forward url="{$exist:controller}/modules/view.xql"/>:)
(:		</error-handler>:)
(:    </dispatch>:)
(:) :)


(:
    restricted.html is secured by the following rules
:)
else if (ends-with($exist:path, "restricted.html")) then (
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
            else if(not(string($userParam) eq string($user))) then
                (:
                if a user was send as request param 'user'
                AND it is NOT the same as $user
                a former login attempt has failed.

                Here a duplicate of the login.html is used. This is certainly not the most elegant solution. Just here
                to not complicate things further with templating etc.
                :)
                <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
                    <forward url="fail.html"/>
                        <view>
                            <forward url="{$exist:controller}/modules/view.xql"/>
                        </view>                    
                </dispatch>
            else
                (: if nothing of the above matched we got a login attempt. :)
                <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
                    <forward url="login.html"/>
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
    
  else if ( contains($exist:path, "/query") )  then 
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <forward url="{$exist:controller}/modules/query.xql">
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

else 
    (: everything else is passed through :)
    <dispatch xmlns="http://exist.sourceforge.net/NS/exist">
        <cache-control cache="yes"/>
    </dispatch>



