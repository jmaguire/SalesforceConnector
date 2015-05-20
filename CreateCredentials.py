import pickle
import getpass
import os

## make folder if it doesn't exist
mypath = './credentials/'
if not os.path.isdir(mypath):
   os.makedirs(mypath)



## save login info for salesforce
username = raw_input('username: ')
password = getpass.getpass('password: ')
security_token = raw_input('token: ')

with open('credentials/bulk_settings', "w") as f:
    f.write(pickle.dumps(
            dict(password = password, 
            username = username, 
            security_token = security_token)))

dropbox_token = raw_input('dropbox token: ')
with open('credentials/dropbox', 'w') as f:
    f.write(pickle.dumps(
        dict(token = dropbox_token)))

print 'done!'
