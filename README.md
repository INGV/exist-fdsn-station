This project aims to create a database and implementing fdsn-station webservice.
The database use eXist-db NoSQL Document Database and Application Platform.


From project directory invoke ``ant`` to build the package file ``fdsn-station-0.1.xar`` into the ``build`` directory .
Install the package into your existing eXist-db using package manager.
 
eXist-db can be installed simply as a docker:

```
sudo docker pull existdb/existdb:release
sudo docker run -it -d -p 8080:8080 -p 8443:8443 --name exist existdb/existdb:latest
```


Alternatively fdsn-station and eXist-db can be buylt and deployed in one shot:


```
sudo docker build --rm . -t exist-fdsn-station
sudo docker run --name exist-fdsn-station -it exist-fdsn-station
``` 


Put all your station.xml files in the Station directory  (one file per station) before building the package. You will get your database right in eXist-db after package installation. It works even for the one shot deploy.
 

