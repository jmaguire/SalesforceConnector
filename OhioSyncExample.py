## OpenGov and Wade Wegner

from simple_salesforce import Salesforce
import csv
import time
import requests
import xml.etree.ElementTree as ET
from lxml import etree

## Get Data with REST API
class SalesforceFrom:
    
    def __init__(self, user, pwd, token):
        self.username = user
        self.password = pwd
        self.token = token
        self.sf = Salesforce(password = pwd, username = user, security_token = token)
    

    ## Preform SOQL query
    # obj : Account, Opportunity etc
    # fields: fields to query
    # SOQL query: Like '%hello' and Type != "Customer"
    def query(self, obj, fields, condition):
        result = ''
        try:
            query = "Select " + ", ".join(fields) + " From " + obj + " " + condition
            result = self.sf.query_all(query)
            if result['totalSize'] == 0:
                raise ValueError("No results returned")
        except:
            raise ValueError("Query encountered an unknown error")
            
        return result

    ## Takes a result from SalesforceImporter.query and writes to a list with 
    ## the first row being the field names
    def buildList(self, result):
        if result['totalSize'] == 0:
            raise ValueError("No data in records")
        
        ## Get records, field names and init output list 
        records = result['records']    
        fields = records[0].keys()
        print fields
        fields.remove('attributes')
        output = []
        output.append(fields)
        for record in records:
            output.append([record[field] for field in fields])
        print output[:10]
        return output
    
    ## writes list of lists to csv
    def writeToCSV(self, data, filename):
        with open(filename, 'wb') as f:
            csv.writer(f).writerows(data)

    ## preform query and write result to csv
    def queryToFile(self, obj, fields, condition, filename):
        result = self.query(obj, fields, condition)
        output = self.buildList(result)
        self.writeToCSV(output, filename)

## Post data with BULK API
class SalesforceTo:    
    
    def __init__(self, user, pwd, token, instance):
        self.username = user
        self.password = pwd + token
        self.instance = instance
        #self.token = token
    

    def login(self):
        request = u"""<?xml version="1.0" encoding="utf-8" ?> \
            <env:Envelope xmlns:xsd="http://www.w3.org/2001/XMLSchema" \
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" \
                xmlns:env="http://schemas.xmlsoap.org/soap/envelope/"> \
                <env:Body> \
                    <n1:login xmlns:n1="urn:partner.soap.sforce.com"> \
                        <n1:username>""" + self.username + """</n1:username> \
                        <n1:password>""" + self.password + """</n1:password> \
                    </n1:login> \
                </env:Body> \
            </env:Envelope>"""

        encoded_request = request.encode('utf-8')
        url = 'https://login.salesforce.com/services/Soap/u/30.0'
        headers = {'Content-Type': 'text/xml; charset=UTF-8', 'SOAPAction': 'login'}
        response = requests.post(url=url, headers=headers, data=encoded_request, verify=True)

        return unicode(response.text)


    def createJob(self, sessionId, operation, object, contentType):
        request = \
            u"""<?xml version="1.0" encoding="UTF-8"?> \
            <jobInfo xmlns="http://www.force.com/2009/06/asyncapi/dataload"> \
            <operation>"""  + operation + """</operation> \
            <object>""" + object + """</object> \
            <contentType>""" + contentType + """</contentType> \
            </jobInfo>"""

        encoded_request = request.encode('utf-8')
        url = 'https://' + self.instance + '.salesforce.com/services/async/30.0/job'
        headers = {'X-SFDC-Session': sessionId, 'Content-Type': 'application/xml; charset=UTF-8'}
        response = requests.post(url=url, headers=headers, data=encoded_request, verify=True)

        return unicode(response.text)


    def addBatch(self, sessionId, jobId, objects):
        request = u"""<?xml version="1.0" encoding="UTF-8"?> \
            <sObjects xmlns="http://www.force.com/2009/06/asyncapi/dataload"> \
            """ + objects + """ \
            </sObjects>"""

        encoded_request = request.encode('utf-8')
        url = 'https://' + self.instance + '.salesforce.com/services/async/30.0/job/' + jobId + '/batch'
        headers = {'X-SFDC-Session': sessionId, 'Content-Type': 'application/xml; charset=UTF-8'}
        response = requests.post(url=url, headers=headers, data=encoded_request, verify=True)
        
        return unicode(response.text)


    def closeJob(self, sessionId, jobId):
        request = \
            u"""<?xml version="1.0" encoding="UTF-8"?> \
            <jobInfo xmlns="http://www.force.com/2009/06/asyncapi/dataload"> \
            <state>Closed</state> \
            </jobInfo>"""

        encoded_request = request.encode('utf-8')
        url = 'https://' + self.instance \
            + '.salesforce.com/services/async/30.0/job/' + jobId
        headers = {'X-SFDC-Session': sessionId, 'Content-Type': 'application/xml; charset=UTF-8'}
        response = requests.post(url=url, headers=headers, data=encoded_request, verify=True)

        return unicode(response.text)



    ## Data is a list of dictionaries where each row cooresponds to an object
    ## with keys being the object's fields and values being the object's field value
    ## Example row: {'Id' : '001d000001kca1F', 'Ohio_Implementation__c' : 'Site Build'}
    def createObjectXml(self, data):
        objectXml = ""
        for row in data:
            root = etree.Element('sObject')
            for field, value in row.iteritems():
                child = etree.Element(field)
                child.text = value
                root.append(child)
            objectXml += etree.tostring(root)

        print objectXml
        return objectXml

    def update(self, sObject, data):
    
        ## login
        loginXmlResponse = self.login()
        loginXmlRoot = ET.fromstring(loginXmlResponse)
        sessionId = loginXmlRoot[0][0][0][4].text
        print sessionId

        ## create job
        jobXmlResponse = self.createJob(sessionId, "update", sObject, "XML")
        jobXmlRoot = ET.fromstring(jobXmlResponse)
        jobId = jobXmlRoot[0].text
        print jobId

        ## add batch
        data = [{'Id' : '001d000001kca1F', 'Ohio_Implementation__c' : 'Site Build'}, \
                {'Id' : '001d000001es2fP', 'Ohio_Implementation__c' : 'Site Build'}]
        objectXml = self.createObjectXml(data)
        print self.addBatch( sessionId, jobId, objectXml)

        ## close job
        print self.closeJob( sessionId, jobId)
    
        
            
            
        
if __name__ == '__main__':
    

    ### Export
    ##----------------
    ## user details
    user = ''
    password = ''
    token = ''
    instance = ''

    ##example data. needs to be row dict format
    data = [{'Id' : '001d000001kca1F', 'Ohio_Implementation__c' : 'Site Build'}, \
        {'Id' : '001d000001es2fP', 'Ohio_Implementation__c' : 'Site Build'}]

    sfdc = SalesforceTo(user, password, token, instance)
    sfdc.update("Account", data)
    ##----------------
    
    
    ### Import
    ##----------------
    ## login
    ##sfdc = SalesforceConnector(user, password, token)
    
    ## field
    fields = [u'Id', u'Ohio_Implementation__c', u'Ohio_Implementation_Details__c', u'Ohio_Salesforce_ID__c']
    ## object
    obj = 'Account'
    ## conditions
    conditions = "Where BillingState = 'Ohio'"
    ## filename
    filename = "OpenGov_Accounts_" + time.strftime("%c") + "_.csv"

    ##result = sfdc.query(obj, fields, conditions)
    ##output = sfdc.buildList(result)
    ##sfdc.writeToCSV(output,filename)

    sfdc = SalesforceFrom(user, password, token)
    sfdc.queryToFile(obj, fields, conditions, filename)
    ##----------------
    


