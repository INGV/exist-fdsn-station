Exist-fdsn-station offers an XML-based database for seismic stations
metadata, compliant with the standard FDSN StationXML format [FDSN,
2012] and accessible with the standard FDSN web service fdsnws/station
[FDSN, 2013]. The exist-fdsn-station software is an application
running into an eXist-db [Siegel and Retter, 2014] database, users
should consider becoming familiar also with the eXist-db software, in
particular with its Package Manager and with the eXide integrated
editor. Here are the instructions for using the software in brief, 
for a more detailed guide download the [manual](https://doi.org/10.13127/rpt/478).

**Installation**

You can install the eXist-db database
and application in the provided containerized package, following the
instructions presented here. Otherwise, if you prefer a standard
eXist-db installation, refer to the eXist-db documentation [eXist-db
Project, 2014]. In the latter case, after successfully installing
eXist-db stand-alone, follow the instructions presented below to install
Exist-fdsn-station using the package system.

**Get the source**

Whichever method you choose for installation, you will need to obtain
the source code before proceeding. To get the source code, download a
copy of the project from the github repository  or clone it
directly:
```
$ git clone https://github.com/INGV/exist-fdsn-station
```
**Test run with exist-fdsn-station**

For a quick application test, you can build the image by running the docker
command from the project directory:

```
$ docker build . -t exist-fdsn-station
```

then start the container using the image just built:

```
$ docker run -d -p 127.0.0.1:80:8080 --name  exist-fdsn-station
exist-fdsn-station
```

After a while, the eXist-db server with exist-fdsn-station installed into, will be
up and running. Access its Dashboard page at
http://127.0.0.1/exist 

In eXist-db interface, click on the "fdsn station" icon to activate the application. 
User "admin" password is empty.

You can stop and remove
container and image with the next commands:
```
$ docker stop exist-fdsn-station
$ docker rm exist-fdsn-station
$ docker image rm exist-fdsn-station
```
**Installation with docker-compose**

The recommended and persistent installation procedure is based on the
docker compose command, driven by the compose.yaml file. The
installation will store the database on disk in the "data" directory,
and you must create it manually before install. From the project
directory you can activate the build and start the service using docker
compose:
```
$ mkdir data
$ docker compose up -d

[+] Running 2/2

-   Container exist-fdsn-station      Started
-   Container fdsn-station-proxy-1    Started
```

This command starts two containers, one with the database and the
application, the second with the nginx web server front-end, you can check their running state with:

```
docker compose top
```

When your server will be up, access it at http://127.0.0.1/exist. With docker compose you can start or
stop the two services independently.

**Uninstall**

The database uses the "data" directory as a container local volume where database and application persist safely on disk. 

**Basic administrative tasks in eXist-db**

Administrator credentials are required to perform administrative tasks
in eXist-db. The administrator user is called "admin" and has a blank
default password. Typical administrative tasks are the user management
and the package installation. To access the Dashboard menu to start the
User Manager or the Package Manager you must log in. Use the User Manager application
to change the "admin" password. Installation of the exist-fdsn-station
packages automatically creates the "fdsn" user, you need to change its
default "fdsn" password too.

**The packages**

The exist-fds-station consists of two packages: fdsn-station and
fdsn-station-data. The first contains the application files, the second
contains data and index definitions. Their names follow the following
name convention:

-   fdsn-station-data-{majorversion}{minorversion}.xar
-   fdsn-station-{majorversion}{minorversion}{microversion}{build}.xar

The package files, compatible with eXist-db, are in EXPath format
[EXPath Community Group, 2021].

Installing the "ant" software is a prerequisite to build the packages.
Then you can build the packages, in the form of compressed ".xar"
files, invoking "ant" from the project directory. 
```
$ ant -f build.xml
$ ant -f fdsn-station-data/build.xml
```
**Installing using the packages**

If you installed eXist-db on your own, you need the two package files to
proceed with this kind of installation. Since distribution of binary
packages is not currently planned, you need to compile them from source,
as shown above. The installation of fdsn-station depends on the presence
of the fdsn-station-data package in the database, therefore you must
**first install fdsn-station-data**, otherwise the installation will
fail. Launch the Package Manager application from the Launcher, to
install the packages one at a time.

The fdsn-station-data package contains only the initial collection and
its index definitions. This collection will be filled with your stations
data, so when the system will be in production you should **avoid
reinstalling the fdsn-station-data package, otherwise your data will be
deleted**.

**Updates**

Updates of the package follow the same procedure for every kind of
installation. Updates of the fdsn-station package are data safe and do
not require updating the fdsn-station-data package. Future versions of
the fdsn-station package that eventually require changes to the data
collection will also require an updated fdsn-station-data package and
will fail installation otherwise.

**Station Database maintenance**

The application interface exposes some basic database maintenance
operation through the "Manage" page.

**Purge the database**

A dummy station is contained in the fdsn-station-data package, it is necessary to remove it
before starting to use the database with your data. To delete all stations, click on the "Purge" button. Beware,
**you cannot undelete after clicking**.

**Cache clean**

There is a kind of cache system implemented in the application, if you
moved or deleted some station document using the eXide application or
accessing the database collection with other clients, you probably broke
this system. Minor problems can be solved using the "Empty" button to
reset the cache. This operation is completely safe for data in the
station collection.

**Fix database**

Major problems occurring to the cache system can be fixed resetting the
whole cache system, using the "Fix" button. Typical symptoms of a
broken cache are inconsistent results of queries from the web service,
persisting after a Cache Clean attempt. If Cache Clean did not get the
expected results, you can still try to Fix the database. This operation
is safe for data, but could change data modification time of documents
used by queries with the parameter updatedafter.

**Touch database**

This function permits to update all modification time of all documents
in the database at the same time. Use it whenever you want to force all
your data to a given update time.

**Log verbosity**

To change the logs verbosity of the application you must check one or
more desired levels, then click apply. Changes are applied immediately,
starting from the next query to the service.

-   Enable log: add to the log of the application only error 400. It is
    a recommendable default.
-   Enable debug: enable logging of internal calls of the application,
    use it only when trying to debug the software.
-   Enable query: enables GET and POST query logs by the service.

**Where are my logs?**

The exist-fdsn-station logs are in the same place where eXist-db logs
go. If you are using the docker compose installation procedure you can
see all the logs using:
```$ docker compose logs```

**Where are my files?**

Only using eXide or through the application interface, you can view and download
the original StationXML browsing the fdsn-station-data collection. To
get the chosen file just click on the link in the station list present
in the home page. When the list is very long it may be useful to use the
"Search" function to find the input files using the station code as
the search key.

**Data Management**

Having removed the dummy station by trying the "Purge" of the
database, it's time to load some station.xml files to continue playing
around or to put in production your new fdsnws/station web service. The
better way to load data in a production environment is using the PUT
HTTP method, in this way data load can be fully automated.

**PUT your stations in the database**

In order to upload station files, you need a web client capable of
submitting a PUT request with a payload to the webservice. PUT is a
method subject to authorization, you need to know the "fdsn" user
credentials. You can store in the database station files coming from
different sources and, as station names are not uniquely attributed to a
provider, it is **mandatory** to use a **naming convention** for files.

The file names need to be in the format: PROVIDER_STATION.xml where
PROVIDER is a string used to identify the provider of the metadata
station file and STATION is a string equal to the seismic station code.

Here is an example of data input using curl, passing through the nginx
proxy server:
```
$ curl -X PUT "http://127.0.01:80/fdsnws/station/1/query?" -H
"accept: application/xml" -H "Content-Type: application/octet-stream" -H "filename: INGV_ABSI.xml" --data-binary @Station/INGV_ABSI.xml -o output.xml -i -v -fdsn:password
```
and another example using curl directly addressing the eXist-db host,
notice the different URL:
```
$ curl -X PUT "http://172.17.0.2:8080/exist/apps/fdsn-station/fdsnws/station/1/query?"
-H "accept: application/xml" -H "Content-Type:application/octet-stream" -H "Expect:" -H "filename:INGV_ABSI.xml" --data-binary @Station/INGV_ABSI.xml -o output.xml -i -v -fdsn:password
```
**DELETE your stations**

Usually stations are inserted and updated overwriting them, but if you
really want to delete one station, you can use the DELETE HTTP method,
passing the filename header. Example:
```
$ curl -v -H "filename: INGV_ACER.xml" -X DELETE "http://127.0.0.1:80/fdsnws/station/1/query?" -u fdsn:password
```
If you need to remove a whole network, pertaining to a given PROVIDER,
you have to use another syntax, passing on the URL the PROVIDER string
and the network code:
```
$ curl -v -X DELETE "http://127.0.0.1:80/fdsnws/station/1/query?provider=INGV&net=IV" -u
fdsn:fdsn
```
A different syntax is available for removing all the networks of the
given provider in a single request, using a wildcard to match every
network code:
```
$ curl -v -X DELETE "http://127.0.0.1:80/fdsnws/station/1/query?provider=INGV&net=*" -u fdsn:fdsn
```

For a complete reference of the extension of the API implemented in
exist-fdsn-station see Table 1.

|         |                |                  |                                                                             |
|---------|----------------|------------------|-----------------------------------------------------------------------------|
| Method  | Parameter      | Header           | Description                                                                 |
| PUT    | None requested | filename         | Add a station to the database. <br/>The filename of the stationXML passed is in the format PROVIDER_STATIONCODE.xml|
| DELETE | None requested | filename         | Delete a   station, the name of the stationXML to be removed is  passed in the format PROVIDER_STATIONCODE.xml |
| DELETE | provider       | None requested   | Provider of the  stations to be removed, as per the prefix of the station file previously inserted.|
|DELETE | net    | None requested | Select one network code to delete all stations of the network of the  given provider., '*'  to delete all stations of the given provider. |

Table 1: fdsnws/station API extension provided.

**Get responses from the web service**

Just after station loading, querying your service will start to give
some meaningful results. The entry points differ depending on the server
you interrogate, see Table 3 for reference.

|     |     |
|-----|-----|
|    container | entry point    |
|  exist-fdsn-station   |  http://INTERNAL_IP:8080/exist/apps/fdsn-station/fdsnws/station/1/query?   |
|  exist-fdsn-station-proxy-1   | http://127.0.0.1:80/fdsnws/station/1/query?    |




Table 2: entry points of the fdsnws/station service

Notice that INTERNAL_IP is the IP assigned on the docker network to the
exist-fdsn-station.

Access the service path "/fdsnws/station/1" to obtain a human-readable description of the service specification. 

**Automating database updates**

The API permits to write into the database programmatically, you can use
whatever instrument to exploit it for manage data into
exist-fdsn-station. For user convenience, in the "bin" project
directory you can find fdsn-station-sync-xml.py, a python script capable
of synchronizing your database with every fdsnws/station web service
source or with a directory full of station files. Use the "--help"
option or inspect the code to understand its use. The file
"bin/config.py" must be edited to insert the credentials needed to
authenticate the script with the exist-fdsn-station destination server.

**Performance monitoring**

The performance of the service can be monitored in real time using the
pre-installed Monex application, accessible from the eXist-db home page,
see Figure 1. The service works best when XML output is requested, while
text or other formats output requires translation, with a slight
penalty. This must be taken into consideration when creating
applications that access the service and have critical needs in terms of
response times.

**References**

eXist-db Project (2014). https://exist-db.org/exist/apps/doc/ 

EXPath Community Group, (2021). Packaging System EXPath Candidate Module
9 May 2012, available at http://expath.org/spec/pkg

FDSN - International Federation of Digital Seismograph
Networks (2012). StationXML schema 1.0, available at
https://www.fdsn.org/xml/station/fdsn-station-1.0.xsd

FDSN - International Federation of Digital Seismograph Networks (2013).
FDSN Web Service Specifications Version 1.0, available at http://www.fdsn.org/webservices/FDSN-WS-Specifications-1.0.pdf.

Siegel, E., Retter, A., (2014). eXist, O'Reilly Media, Inc. ISBN:9781449337100


[![DOI](https://zenodo.org/badge/317600375.svg)](https://zenodo.org/badge/latestdoi/317600375)