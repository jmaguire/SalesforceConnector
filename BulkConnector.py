#from simple_salesforce.login import SalesforceLogin
from SalesforceLogin import SalesforceLogin
from simple_salesforce.util import date_to_iso8601, SalesforceError
from salesforce_bulk import SalesforceBulk
import getpass
import pickle
import os
from time import sleep
from salesforce_bulk import CsvDictsAdapter


##List path to credentials
credential_files = ['/home/ubuntu/credentials/bulk_settings','/Users/opengov/Documents/OpenGov/credentials/bulk_settings']

class SalesforceConnector:
    def __init__(self, **kwargs):
        self.sf_version = kwargs.get('version', '29.0')
        self.sandbox = kwargs.get('sandbox', False)
        self.proxies = kwargs.get('proxies')
        self.domain = kwargs.get('domain', None)

        try:
            credentials = [elem for elem in credential_files if os.path.exists(elem)][0]    
        except:
            raise ValueError('No credentials found')
        #Load Credentials from file
        if os.path.exists(credentials):
            creds = pickle.loads(open(credentials).read())
            username = creds['username']
            password = creds['password']
            security_token = creds['security_token']
            self.session_id, self.sf_instance = SalesforceLogin(
                username=username,
                password=password,
                security_token=security_token,
                sandbox=self.sandbox,
                sf_version=self.sf_version,
                proxies=self.proxies,
                domain = self.domain)
            print 'read credentials'
        ##Read credentials from arguments
        elif 'username' in kwargs and 'password' in kwargs and 'security_token' in kwargs:
            self.auth_type = "password"
            username = kwargs['username']
            password = kwargs['password']
            security_token = kwargs['security_token']
            self.session_id, self.sf_instance = SalesforceLogin(
                username=username,
                password=password,
                security_token=security_token,
                sandbox=self.sandbox,
                sf_version=self.sf_version,
                proxies=self.proxies,
                domain = self.domain)
            self.saveLogin(username, password, security_token)
        else:
            raise TypeError(
                'You must provide login information or an instance and token'
            )
        print self.sf_instance     
        self.bulk = SalesforceBulk(sessionId= self.session_id, host = self.sf_instance)

    def saveLogin(self, username, password, security_token):
        with open(credentials, "w") as f:
            f.write(pickle.dumps(
                    dict(password = password, 
                    username = username, 
                    security_token = security_token)))

    ##Returns csv dict
    # Each row is a dictionary of column_header:row_value
    def query(self, sObject, queryString, contentType):
        job_id = self.bulk.create_query_job(sObject, contentType = contentType)
        batch_id = self.bulk.query(job_id, queryString)
        self.bulk.wait_for_batch(job_id, batch_id, timeout=120)
        self.bulk.close_job(job_id)
        print 'job closed'
        result_id = self.bulk.get_batch_result_ids(batch_id,job_id)[0]
        result = [row for row in self.bulk.get_batch_results(batch_id = batch_id, result_id = result_id, job_id=job_id,
                          parse_csv=True)]
        csv_dict = [dict(zip(result[0],row)) for row in result[1:]]
        return csv_dict
    
    def update(self, sObject, data, contentType):
        job_id = self.bulk.create_update_job(sObject, contentType='CSV')
        csv_iter = CsvDictsAdapter(iter(data))
        batch_id = self.bulk.post_bulk_batch(job_id, csv_iter)
        self.bulk.wait_for_batch(job_id, batch_id, timeout=120)
        self.bulk.close_job(job_id)
        print 'done'
        return



if __name__ == '__main__':
    '''
    username = raw_input("Username: ")
    password = getpass.getpass()
    security_token = raw_input("Token: ")

    sfdc = SalesforceConnector(username = username, 
                password = password, 
                security_token = security_token)
    '''
    sfdc = SalesforceConnector()
    print sfdc.query(queryString = "select Id, Name from Account Limit 5", sObject = "Account",contentType='CSV')

    ##data = [{'Id' : '001d000001kca1F', 'Ohio_Implementation__c' : 'Site Build'}, \
    ##    {'Id' : '001d000001es2fP', 'Ohio_Implementation__c' : 'Site Build'}]
    ##sfdc.update('Account', data, contentType = 'CSV')
    
