This project implements a seismic stations xml database compliant with the FDSN Station xml format [fdsn-station](https://www.fdsn.org/xml/station/fdsn-station-1.1.xsd)
and the corresponding FDSN webservice [fdsnws-station](https://www.fdsn.org/webservices/) .


From the project directory invoke ``ant`` to build the package file ``fdsn-station-0.1.xar`` into the ``build`` directory.
Install the package into your [eXist-db](ihttp://exist-db.org/exist/apps/homepage/index.html) using the package manager.
 
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


Replace the files in the Station directory with your station.xml files (one file per station) before building the package. You will get your database right in eXist-db after package installation. It works even for the one shot deploy.
 
Query the webservice version as for the FDSN Station standard, assuming 172.17.0.2:8080 the docker network:port exposed:

```
wget "http://172.17.0.2:8080/exist/apps/fdsn-station/version -O version.text" 

```
Try this examples with the stations provided, or adapt to your stations set.

```
wget "http://172.17.0.2:8080/exist/apps/fdsn-station/query/?level=station&format=text&lat=42.1&lon=12.5&maxradius=2.5&minradius=0.001&includerestricted=false" -O some-stations-norestricted.txt 
```

