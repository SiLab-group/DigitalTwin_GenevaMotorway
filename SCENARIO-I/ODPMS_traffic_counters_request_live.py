#    Digital Twin - Geneva Motorway (DT-GM) in SUMO
#    Author: Krešimir Kušić

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>





# README
# (I) Change the name of your SERVER in SERVER=SQLServerName (see your database), and UID=UserName (used by SQL authentication)
# (II) Find in code below <headers = {'Authorization': 'your token',> and put [your token] that you got after registered at ODPMS


import requests
import smtplib, ssl
from xml.etree import ElementTree as ET
import datetime as dt
import time
# import schedule
import pyodbc
import os
from urllib3.util.retry import Retry
from requests import Session
from requests.adapters import HTTPAdapter


# (I) Change the name of your SERVER in SERVER=SQLServerName (see your database), and UID=UserName (used by SQL authentication)
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=ServerName;DATABASE=SWISS_traffic_data;UID=UserName;TRUSTED_CONNECTION=yes')


# optional if you whant receive notification via email about road sensors status (traffic counters)
# if (YES) specifie next: your <gmail_user> and <gmail_password>, additional setup maybe required in gmail 
#(In case you have problems to connect at Google, you need to enable the “Less secure app access”. see https://myaccount.google.com/intro/security?hl=en)
def sendEmail(body):
    gmail_user = 'XXX@gmail.com'
    gmail_password = 'YYY'

    sent_from = gmail_user
    to = ['XXX@gmail.com']
    subject = 'SWISS-traffic data Error!'
    body = body

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % (sent_from, ", ".join(to), subject, body)
    # Create a secure SSL context
    context = ssl.create_default_context()
    
    try:
        smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context)
        smtp_server.ehlo()
        smtp_server.login(gmail_user, gmail_password)
        smtp_server.sendmail(sent_from, to, email_text)
        smtp_server.close()
        print ("Email sent successfully!")
    except Exception as ex:
        print ("Something went wrong….",ex)

def convert_UTC_str_to_date_time(date_time_str_input):
    date_time_str = date_time_str_input
    date_time_obj = dt.datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    return date_time_obj

def sendRequest(ID_station1, ID_station2, ID_station3, ID_station4, list_Email):

    url = "https://api.opentransportdata.swiss/TDP/Soap_Datex2/Pull"

    payload = """
    <?xml version="1.0" encoding="UTF-8"?>
    <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:tdpplv1="http://datex2.eu/wsdl/TDP/Soap_Datex2/Pull/v1" xmlns:dx223="http://datex2.eu/schema/2/2_0">
        <SOAP-ENV:Body>
            <dx223:d2LogicalModel xsi:type="dx223:D2LogicalModel" modelBaseVersion="2">
                <dx223:exchange xsi:type="dx223:Exchange">
                    <dx223:supplierIdentification xsi:type="dx223:InternationalIdentifier">
                        <dx223:country xsi:type="dx223:CountryEnum">ch</dx223:country>
                        <dx223:nationalIdentifier xsi:type="dx223:String">FEDRO</dx223:nationalIdentifier>
                    </dx223:supplierIdentification>
                </dx223:exchange>
                <dx223:payloadPublication xsi:type="dx223:GenericPublication" lang="en">
                        <dx223:publicationCreator xsi:type="dx223:InternationalIdentifier">
                            <dx223:country xsi:type="dx223:CountryEnum">ch</dx223:country>
                            <dx223:nationalIdentifier xsi:type="dx223:String">FEDRO</dx223:nationalIdentifier>
                        </dx223:publicationCreator>
                        <dx223:genericPublicationName xsi:type="dx223:String">MeasuredDataFilter</dx223:genericPublicationName>
                        <dx223:genericPublicationExtension xsi:type="dx223:_GenericPublicationExtensionType">
                            <dx223:measuredDataFilter xsi:type="dx223:MeasuredDataFilter">
                                <dx223:measurementSiteTableReference xsi:type="dx223:_MeasurementSiteTableVersionedReference" targetClass="MeasurementSiteTable" id="OTD:TrafficData" version="0"></dx223:measurementSiteTableReference>
                                <dx223:siteRequestReference xsi:type="dx223:_MeasurementSiteRecordVersionedReference" targetClass="MeasurementSiteRecord" """+ID_station1+"""/#" version="0"></dx223:siteRequestReference>
                                <dx223:measurementSiteTableReference xsi:type="dx223:_MeasurementSiteTableVersionedReference" targetClass="MeasurementSiteTable" id="OTD:TrafficData" version="0"></dx223:measurementSiteTableReference>
                                <dx223:siteRequestReference xsi:type="dx223:_MeasurementSiteRecordVersionedReference" targetClass="MeasurementSiteRecord" """+ID_station2+"""/#" version="0"></dx223:siteRequestReference>
                                <dx223:measurementSiteTableReference xsi:type="dx223:_MeasurementSiteTableVersionedReference" targetClass="MeasurementSiteTable" id="OTD:TrafficData" version="0"></dx223:measurementSiteTableReference>
                                <dx223:siteRequestReference xsi:type="dx223:_MeasurementSiteRecordVersionedReference" targetClass="MeasurementSiteRecord" """+ID_station3+"""/#" version="0"></dx223:siteRequestReference>
                                <dx223:measurementSiteTableReference xsi:type="dx223:_MeasurementSiteTableVersionedReference" targetClass="MeasurementSiteTable" id="OTD:TrafficData" version="0"></dx223:measurementSiteTableReference>
                                <dx223:siteRequestReference xsi:type="dx223:_MeasurementSiteRecordVersionedReference" targetClass="MeasurementSiteRecord" """+ID_station4+"""/#" version="0"></dx223:siteRequestReference>
                            </dx223:measuredDataFilter>
                        </dx223:genericPublicationExtension>
                </dx223:payloadPublication>
            </dx223:d2LogicalModel>
        </SOAP-ENV:Body>
    </SOAP-ENV:Envelope>
    """

# (II) put the token that you get after registering at ODPMS: headers = {'Authorization': 'your_token',
    headers = {'Authorization': 'your_token',
               'content-type': 'text/xml',
               'SOAPAction': 'http://opentransportdata.swiss/TDP/Soap_Datex2/Pull/v1/pullMeasuredData'}


    
#     response = requests.request("POST", url, headers=headers, data=payload)
    
    def retry_session(retries):
        
        session = Session()
        retries = Retry(total=retries,
                    backoff_factor=.1,
                    status_forcelist=[500, 502, 503, 504],
                    allowed_methods=frozenset(['GET', 'POST']))

        session.mount('https://', HTTPAdapter(max_retries=retries))
        session.mount('http://', HTTPAdapter(max_retries=retries))
        
        return session

    
    # {backoff factor} * (2 ** ({number of total retries} - 1))
    # 1 second the successive sleeps will be 0.5, 1, 2, 4, 8, 16, 32, 64, 128, 256.
    session = retry_session(retries=9)

    try:
        response = session.post(url=url, data=payload, headers=headers)
        if len(list_Email) != 0:
            sendEmail(list_Email)
            list_Email = []
        
#         response = requests.post(url=url, data=payload, headers=headers)
#     response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        t1 = dt.datetime.now()
        to_list = ("Http Error", t1.strftime("%d-%b-%Y (%H:%M:%S.%f)"))
        list_Email.append(to_list)
#         sendEmail("Http Error: (current time "+str(t1)+")")
        response = 'NULL'
    except requests.exceptions.ConnectionError as errc:
        t1=dt.datetime.now()
        to_list = ("Error Connecting", t1.strftime("%d-%b-%Y (%H:%M:%S.%f)"))
        list_Email.append(to_list)
#         sendEmail("Error Connecting: (current time "+str(t1)+")")        
        response = 'NULL'
    except requests.exceptions.Timeout as errt:
        t1=dt.datetime.now()
        to_list = ("Timeout Error", t1.strftime("%d-%b-%Y (%H:%M:%S.%f)"))
        list_Email.append(to_list)
#         sendEmail("Timeout Error: (current time "+str(t1)+")") 
        response = 'NULL'
    except requests.exceptions.RequestException as err:
        t1=dt.datetime.now()
        to_list = ("OOps: Something Else", t1.strftime("%d-%b-%Y (%H:%M:%S.%f)"))
        list_Email.append(to_list)
#         sendEmail("OOps: Something Else (current time "+str(t1)+")")
        response = 'NULL'
    

    return response, list_Email

def extract_data_from_xml(response_data):
    response_data = response_data
    root = ET.fromstring(response_data)
    
    attr_CH_traffic_data = []

    start_iter = 4
    end_iter = len(list(root[0][0][1]))
    
    for i in range(start_iter, end_iter):    # range (total # of detectors) to iterate in XML through children nodes 'dx223:measuredValue'
        
        inner_list_data=[]
        inner_list_attribute=[]
        
        for indx, x in enumerate(root[0][0][1][i]):

        #     print(x.tag, x.attrib, x.text)
            variable_string = ""

            if indx == 0:
                variable_string = x.attrib['id']
                inner_list_data.append(variable_string)
            elif indx ==1:
                variable_string = x.text
                inner_list_data.append(variable_string)
            else:
                variable_string = x.attrib['index']
                inner_list_data.append(variable_string)

#             print(variable_string)

            for y in x:

                for z in y:

                    for v in z:

                        for w in v:
  
                            keys_list = list(w.attrib)
                            key = keys_list[0]
                            if w.text=='0':
#                                 print(w.text)
#                                 print(w.attrib[key])      # w.attrib is dict
                                if variable_string == '1':
                                    inner_list_data.append(w.text)
                                    inner_list_data.append('2')
                                    inner_list_data.append('0.0')
                                elif variable_string == '11':
                                    inner_list_data.append(w.text)
                                    inner_list_data.append('12')
                                    inner_list_data.append('0.0')
                                else:
                                    inner_list_data.append(w.text)
                                    inner_list_data.append('22')
                                    inner_list_data.append('0.0')
                            else:
                                inner_list_data.append(w.text)
    #                         inner_list_attribute.append(w.attrib[key])
        attr_CH_traffic_data.append(inner_list_data)

    return attr_CH_traffic_data
    
    
n0=1
list_Email = []
while n0==1:
    time.sleep(1)   
    t0 = dt.datetime.now()
    
    if t0.second==25:

        current_time = t0.strftime("%H:%M:%S")
        print("Current Time =", current_time)

#       X_0224 - eastbound
#       X_0272 - northbound
#       X_0200 - southbound

        ID_station1 = '''id="CH:0272'''
        ID_station2 = '''id="CH:0224'''
        ID_station3 = '''id="CH:0200'''
        ID_station4 = '''id="CH:0068'''

        response, list_Email = sendRequest(ID_station1, ID_station2, ID_station3, ID_station4, list_Email)
        
        list_Email = list_Email
        
        if response != 'NULL':

            try:

                attr_CH_data = extract_data_from_xml(response.content)

                for i in range(len(attr_CH_data)):
                    if 'true' in attr_CH_data[i]:
                        insert_date = [None, None, None, None, None, None, None, None]
                        cursor = conn.cursor()
                        cursor.execute(query, insert_date)
                        conn.commit()
                        # optional info. via email
                        #sendEmail('SENSOR_ERROR (other sensors are working)  this not! '+str(attr_CH_data[i][0]))
                    else: 
                        DetectorID = str(attr_CH_data[i][0])
                        TimeStamp = convert_UTC_str_to_date_time(attr_CH_data[i][1])
                        CarFlow =  int(attr_CH_data[i][3])
                        CarSpeed = float(attr_CH_data[i][5])
                        TruckFlow = int(attr_CH_data[i][7])
                        TruckSpeed = float(attr_CH_data[i][9])
                        UnknownClassFlow = int(attr_CH_data[i][11])
                        UnknownClassSpeed = float(attr_CH_data[i][13])
                    # (DetectorID, TimeStampUTC, CarFlow, CurSpeed, TruckFlow, TruckSpeed, UnknownClassFlow, UnknownClassSpeed)
                        query = """insert into tblDetectors 
                        values (?, ?, ?, ?, ?, ?, ?, ?)"""
                    #     (DetectorID, TimeStamp, CarFlow, CarSpeed, TruckFlow, TruckSpeed, UnknownClassFlow, UnknownClassSpeed)
                        # # Create a cursor from the connection

                        insert_date = [DetectorID, TimeStamp, CarFlow, CarSpeed, TruckFlow, TruckSpeed, UnknownClassFlow, UnknownClassSpeed]
                        cursor = conn.cursor()
                        cursor.execute(query, insert_date)
                        conn.commit()
#                     print("Insert real data in SQL database")
                    
 
            except:
        
                t1=dt.datetime.now()
                filename = 'response_content_'+t1.strftime("%d_%b_%Y___%H_%M_%S")+'.txt'
                # response.raise_for_status() # ensure we notice bad responses
                with open(filename, 'wb') as fd:
                    fd.write(response.content)
                fd.close()
                
                query = """insert into tblDetectors 
                values (?, ?, ?, ?, ?, ?, ?, ?)"""
                #     (DetectorID, TimeStamp, CarFlow, CarSpeed, TruckFlow, TruckSpeed, UnknownClassFlow, UnknownClassSpeed)
                    # # Create a cursor from the connection

                insert_date = [None, None, None, None, None, None, None, None]
                cursor = conn.cursor()
                cursor.execute(query, insert_date)
                conn.commit()
                sendEmail('Something went wrong when iterating through XML response!')                
        else:
            
            query = """insert into tblDetectors 
            values (?, ?, ?, ?, ?, ?, ?, ?)"""
            #     (DetectorID, TimeStamp, CarFlow, CarSpeed, TruckFlow, TruckSpeed, UnknownClassFlow, UnknownClassSpeed)
                # # Create a cursor from the connection

            insert_date = [None, None, None, None, None, None, None, None]
            cursor = conn.cursor()
            cursor.execute(query, insert_date)
            conn.commit()

#============================
