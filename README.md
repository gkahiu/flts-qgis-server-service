# FLTS QGIS Server Service
A sample QGIS Server plugin that exposes a custom service using simple query parameters to 
produces PDF documents (single or in a ZIP file if multiple) based on layouts defined in the test QGS project files. It  is meant to demonstrate the application of QGIS Server to produce layout outputs (designed in QGIS Desktop) 
by sending custom query parameters to the server. 

It should not be used in a production environment as it should incorporate appropriate mechanisms for authenticating and 
authorizing users, managing `*.qgs` project files (either in flat files or a PostgreSQL database), expose service capabilities, logging appropriate messages in the server, error handling and 
returning appropriate messages to the client.

## Parameters
Parameters for the **FLTS** service include:

| Parameter | Required | Description |
|------------|---------|--------------|
| REQUEST | Yes | Specific name of the request e.g. *GetStarterCert, GetCapabilities* |
| VERSION | No | Version of the FLTS service |
| TEMPLATE_ID | Yes | Unique identifier of the QGIS project file (see supported test TEMPLATE_IDs [here](https://github.com/gkahiu/flts-qgis-server-service/blob/main/flts_service/core/handlers.py#L81) and [here](https://github.com/gkahiu/flts-qgis-server-service/blob/main/flts_service/core/handlers.py#L88)) |
| QUERY | No | `0` to return only one document in PDF matching the first record found or `1` to return all documents in ZIP format |


## Examples
* To get the capabilities supported by the FLTS service:
`http://localhost:8090/cgi-bin/qgis_mapserv.fcgi.exe?SERVICE=FLTS&REQUEST=GetCapabilities`


* To process one document and return it as a PDF file:
`http://localhost:8090/cgi-bin/qgis_mapserv.fcgi.exe?SERVICE=FLTS&REQUEST=GetStarterCert&TEMPLATE_ID=86AB5327&QUERY=0`


* To process multiple documents and return the package as a ZIP file
`http://localhost:8090/cgi-bin/qgis_mapserv.fcgi.exe?SERVICE=FLTS&REQUEST=GetStarterCert&TEMPLATE_ID=86AB5327&QUERY=1`


## License
`FLTS QGIS Server Service` is free software. You can redistribute it and/or modify it under the terms of the GNU General 
Public License version 3 (GPLv3) as published by the Free Software Foundation. 

Software distributed under this 
License is distributed on an "AS IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See LICENSE 
or https://www.gnu.org/licenses/gpl-3.0.en.html for the specific language governing rights and limitations under the License.
