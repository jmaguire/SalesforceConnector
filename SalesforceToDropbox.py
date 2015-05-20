from BulkConnector import SalesforceConnector
import csv
import time
import dropbox 
import pickle
import datetime
import os

#credentials = '/Users/opengov/Documents/OpenGov/credentials/dropbox'
#credentials = "../credentials/dropbox"
#credentials = '/home/ubuntu/credentials/dropbox'
credential_files = ['/home/ubuntu/credentials/dropbox','/Users/opengov/Documents/OpenGov/credentials/dropbox']

def queryOGAccountStatus():
    sfdc = SalesforceConnector()
    queryString = "Select Id, OpenGov_ID__c, Ohio_Implementation__c, Ohio_Implementation_Details__c, \
            Ohio_Salesforce_ID__c From Account Where BillingState = 'Ohio'"
    data = sfdc.query(queryString = queryString,  sObject = 'Account', contentType='CSV')
    return data

def writeToDropbox(data):    
    filename = "OpenGov_Accounts_" + str(datetime.datetime.now()) + "_.csv"
    
    try:
        print os.path.exists('/home/ubuntu/credentials/dropbox')
        credentials = [elem for elem in credential_files if os.path.exists(elem)][0]
    except:
        raise ValueError('No credentials found')
    
    creds = pickle.loads(open(credentials).read())
    token = creds['token']
    client = dropbox.client.DropboxClient(token)
    ## save locally
    with open(filename, 'wb') as csvfile:
        fieldnames = ['Id', 'OpenGov_ID__c', 'Ohio_Salesforce_ID__c', 'Ohio_Implementation__c', 'Ohio_Implementation_Details__c']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data) 
    ## save to dropbox
    with open(filename, 'r') as f:
        response = client.put_file('/' + filename, f)
        print response
        
    print 'saved', filename
data = queryOGAccountStatus()
writeToDropbox(data)
