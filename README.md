##SalesforceConnnector:
---------------------------
Salesforce to python connector. Allows REST exports and BULK inserts

requires simple_salesforce 
  ```
  (https://pypi.python.org/pypi/simple-salesforce)
  (https://github.com/heroku/simple-salesforce)
  ```

#Limitations:
  Uses full login credentials. 
  
#Usage:
  From same directory: 
  ```
  from OhioSyncExample import SalesforceFrom
  sf = SalesforceFrom(user, pwd, token)
  sf = SalesforceTo(user, pwd, token, instance)
  ```


##BulkConnector
Salesforce to python uses BULK API for export and pushes

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
###Usage
    First login:
    	```
        from BulkConnector import SalesforceConnector
        sfdc = SalesforceConnector(username = username, 
                password = password, 
                security_token = security_token)
        //subsequent login information saved in credentials, a file specified by the user in BulkConnector.py
        
    Subsequent login:
    	
        sfdc = SalesforceConnector()
        

    Example actions:
        
        data = sfdc.query(queryString = "select Id,LastName from Contact Limit 5", sObject = "Contact",contentType='CSV')
        sfdc.update('Account', data, contentType = 'CSV')
        
    ```
