This project implements a seismic stations xml database compliant with the FDSN Station xml format [fdsn-station](https://www.fdsn.org/xml/station/fdsn-station-1.1.xsd)
and the corresponding FDSN webservice [fdsnws-station](https://www.fdsn.org/webservices/) .

**Install**
From the project directory invoke ``ant`` to build the package file ``fdsn-station-0.1.xar`` into the ``build`` directory.
Install the package into your [eXist-db](http://exist-db.org/exist/apps/homepage/index.html) using the package manager.
 
eXist-db can be installed simply as a docker:

```
sudo docker pull existdb/existdb:release
sudo docker run -it -d -p 8080:8080 -p 8443:8443 --name exist existdb/existdb:latest
```

Alternatively fdsn-station and eXist-db can be built and deployed in one shot:

```
sudo docker build --rm . -t exist-fdsn-station
sudo docker run --name exist-fdsn-station -it exist-fdsn-station
``` 

You can also use the provided compose.yaml

```
mkdir data
docker compose up -d
```

Your database content is on data directory.

**Use the API to add stations.**

Here is an example using curl, passing through the nginx proxy server:
```
curl -X PUT "http://127.0.01:80/fdsnws/station/1/query?" -H  "accept: application/xml"  -H "Content-Type: application/octet-stream" -H "filename: INGV_ABSI.xml"  --data-binary @Station/INGV_ABSI.xml -o output.xml -i -v -fdsn:password
```
and another example using curl but directly to the eXist-db host:

```
curl -X PUT "http://172.17.0.2:8080/exist/apps/fdsn-station/fdsnws/station/1/query?" -H  "accept: application/xml"  -H "Content-Type: application/octet-stream" -H "Expect:" -H "filename: INGV_ABSI.xml"  --data-binary @Station/INGV_ABSI.xml -o output.xml -i -v -fdsn:password
```
Adjust IP addresses if needed.

Query the webservice version as for the FDSN Station standard, assuming 172.17.0.2:8080 the docker network:port exposed:

```
wget "http://172.17.0.2:8080/exist/apps/fdsn-station/fdsnws/station/1/version -O version.text" 

```
Try this examples with the stations provided, or adapt to your stations set.

```
wget "http://172.17.0.2:8080/exist/apps/fdsn-station/fdsnws/station/1/query?level=station&format=text&lat=42.1&lon=12.5&maxradius=2.5&minradius=0.001&includerestricted=false" -O some-stations-norestricted.txt 
```

**Web interface**
GUI interface is accessible: http://127.0.0.1/exist/apps/dashboard/index.html

Security: default admin password is empty, fdsn default password is fdsn.
Change it using eXist-db ide.


Need more help? 

User Manual is coming.

[![DOI](https://zenodo.org/badge/317600375.svg)](https://zenodo.org/badge/latestdoi/317600375)
