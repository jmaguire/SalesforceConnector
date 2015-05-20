##ReadMe


## Required Datasets

requires simple_salesforce
   ```
   (https://pypi.python.org/pypi/simple-salesforce)
   (https://github.com/heroku/simple-salesforce)
   ```
requires salesforce_bulk
   ```
  (https://pypi.python.org/pypi/salesforce-bulk/1.0.1)
  (https://github.com/heroku/salesforce-bulk)
   ```
requires dropbox
   
   ```
   https://pypi.python.org/pypi/dropbox
   ```

##CreateCredentials

Run this file to generate a folder called credentials that stores login credentials, bulk_settings, and dropbox.
Use the path to each credential in BulkConnector and SalesforceToDropbox

##BulkConnector
Salesforce to python uses BULK API for export and pushes

##Usage

   #Without Credentials:
      
        from BulkConnector import SalesforceConnector
        sfdc = SalesforceConnector(username = username, 
                password = password, 
                security_token = security_token)
      
   #With Credentials login (Make sure the path in the .py file has been updated)
   
        sfdc = SalesforceConnector()
      
      
   #Example actions:
    
         data = sfdc.query(queryString = "select Id,LastName from Contact Limit 5", sObject = "Contact",contentType='CSV')
        
         data = [{'Id' : '001d000001kca1F', 'Ohio_Implementation__c' : 'Site Build'}, \
            {'Id' : '001d000001es2fP', 'Ohio_Implementation__c' : 'Site Build'}]
            
         sfdc.update('Account', data, contentType = 'CSV')

##SalesforceToDropbox
   Script that queries data using BulkConnector and writes it to dropbox
