# FLTS QGIS Server Service
A sample QGIS Server plugin that exposes a custom service using simple query parameters to 
produces PDF documents (single or in a ZIP file if multiple) based on layouts defined in the test QGS project files. It  is meant to demonstrate the application of QGIS Server to produce layout outputs (designed in QGIS Desktop) 
by sending custom query parameters to the server. 

It should not be used in a production environment as it should incorporate appropriate mechanisms for authenticating and 
authorizing users, managing `*.qgs` project files (either in flat files or a PostgreSQL database), expose service capabilities, logging appropriate messages in the server, error handling and 
returning appropriate messages to the client.

## License
`FLTS QGIS Server Service` is free software. You can redistribute it and/or modify it under the terms of the GNU General 
Public License version 3 (GPLv3) as published by the Free Software Foundation. 

Software distributed under this 
License is distributed on an "AS IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See LICENSE 
or https://www.gnu.org/licenses/gpl-3.0.en.html for the specific language governing rights and limitations under the License.
