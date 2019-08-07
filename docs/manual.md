
  
    
# Oneroster manual and reference    
    
	
** **WORK IN ROGRESS - MORE COMING SOON. FOR NOW, REFERENCE [Quick Start](https://github.com/vossenv/oneroster-python/blob/master/README.md "Quick Start")** **
    
For **Clever:**     
```yaml   
     access_token: 'TEST_TOKEN'   
     host: 'https://api.clever.com/v2.1/'      
     page_size: 10000    
     max_users: 0   
     match_on: 'name'   
     key_identifier: 'id'   
```       
For **Classlink:**    
    
```yaml   
     client_id: 'api client id here'   
     client_secret: 'api client secret here'   
     host: 'https://example-ca-v2.oneroster.com/ims/oneroster/v1p1/'      
     page_size: 10000    
     max_users: 0   
     match_on: 'name'   
     key_identifier: 'sourcedId'   
```    

        
### Using multiple matchers  
You can use an array to specify which fields to match against.  This is helpful when you want to select one group based on ID, and another based on name.  In Classlink, schools and classes have different name fields: name and title, so you can use this feature to fetch from both at once.  All you need to do is change the match_on field to be a list, like so:  
  

### Using multiple matchers
You can use an array to specify which fields to match against.  This is helpful when you want to select one group based on ID, and another based on name.  In Classlink, schools and classes have different name fields: name and title, so you can use this feature to fetch from both at once.  All you need to do is change the match_on field to be a list.


## Table of parameters and descriptions

|Field                    |Type                                    |Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |Example                                                                                          |
|-------------------------|----------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
|**Connection**|++++++++++++|+++++++++++++++++++++++++++++++++++++++++++++++++++++||                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |clever                                                                                           |
|client_id                |required if no access_token (no default)|Client ID from SIS dashboard                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |5d8a7b5eff61ga25bc6e                                                                             |
|client_secret            |required if no access_token (no default)|Client Secret from SIS dashboard                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |c6d2c6745c12ae785f7f1a58a307a04cf0a4                                                             |
|host                     |required (no default)                   |Endpoint for organization's OneRoster implementation                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |Clever: https://api.clever.com/v2.1/ Classlink: https://example.oneroster.com/ims/oneroster/v1p1/|
|access_token             |optional (no default)                   |Allows to bypass API authentication for Clever.  Mainly useful for testing (use 'TEST_TOKEN') or to avoid putting credentials into the file.                                                                                                                                                                                                                                                                                                                                                                                                                           |TEST_TOKEN                                                                                       |
|page_size                |optional (default: 1000)                | api call page size.  Adjusting this will adjust the frequency of API calls made to the server                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |3000                                                                                             |
|max_users           |optional (default: 0)                   |API calls will cutoff after this many users.  Set to 0 for unlimited.  Useful when doing test runs to avoid pulling very large user counts.                                                                                                                                                                                                                                                                                                                                                                                                                            |0, 10, 50, 4000, etc…                                                                            |
|match_on          |required (default: name)                |Attribute corresponding to the group name in user-sync-config.yml.  UST will match the desired value to this field (e.g., name, sourcedId, etc…).  For clever, "name" will suffice for schools, courses and sections.  For classlink, you can user "title" for classes/courses, and "name" for schools.                                                                                                                                                                                                                                                                                                                                                                                                                       |title, name, SIS_ID, sourceId, subject                                                           |
|key_identifier           |required (default: sourcedId)           | unique key used throughout One-Roster (sourcedId or id commonly used).  This may not be an arbitrary value, since it is used in the URL of the API calls.  It must exist and be the base ID for your platform.                                                                                                                                                                                                                                                                                                                                                        |sourcedId, id                                                                                    |
           |                                        |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |                                                                                                 |


