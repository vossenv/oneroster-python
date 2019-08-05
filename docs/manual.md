---
layout: default  
lang: en  
nav_link: Command Parameters  
nav_level: 2  

nav_order: 80  
---  


# Oneroster and Student Information Systems  (SIS)

---

[Previous Section](deployment_best_practices.md)  

---

## What is Oneroster?
Oneroster is not actually an application, but a specification.  Oneroster simplifies the management of rostering for education by standardizing the format for REST and CSV data handling.  This makes it easier for service applications (such as Adobe) to integrate with SIS (student information systems) platforms  that comply with the standard.  It is in a school's best interest to choose Oneroster standardized platforms, because it greatly simplifies the process of maintaining a synchronous state between their rostering breakdown and the products their users need access to.  An in-depth description of the standard can be found on the Oneroster homepage (IMS Globlal):

[https://www.imsglobal.org/activity/onerosterlis](https://www.imsglobal.org/activity/onerosterlis "https://www.imsglobal.org/activity/onerosterlis")

According to IMS, the big picture features of the standard include the following:

- Provision key roster related data including student, course and related enrollment information between various platforms such as a student information system (SIS) and a learning management system (LMS).
- Flexible implementation options to align with an institution’s needs and capabilities, supporting simple spreadsheet-style (CSV) exchanges as well as system-to-system exchanges using REST API’s
- Improves data exchange among multiple systems with roster and gradebook information, thus eliminating problems before they happen
- Transmit scored results between applications, such as student scores from the LMS back to the SIS.

The Oneroster API is open source by definition, which means that all information regarding endpoints and data models is freely available in the actual specification.  The specification provides detailed guidance as to API structure.  Since all the major SIS players adopt the standard and provide similar access to it, the Oneroster connector enables flexibility to do rostering based provisioning - a highly desirable feature!  Adobe works with a great deal of educational organizations.  Most, if not all of these organizations already leverage SIS that include the Oneroster API/CSV implementation.  Some examples of these SIS are:

- Classlink
- Clever
- Kivuto
- Infinite Campus
- Powerschool

## Connector Configuration


You MUST enter either 'clever' or 'classlink' for the platform type, though additional platforms may be supported in the future.  The client ID and secret should come from your SIS dashboard (see the prerequisites section above).  These keys enable UST to connect to your Oneroster instance.  The hostname can be set as noted above for clever, or as your classlink URL for classlink.  This may look like:  `https://example-ca-v2.oneroster.com/ims/oneroster/v1p1/` or similar.	The page size and max user count can be ignored and set to default (see the comment above if you want to use them).  Likewise, the access token field can also be ignored.  This  field is only valid for clever. 
## **To use clever you must have a district token or use TEST_TOKEN for testing.**

3. In the schema section, you can configure the default settings for your API.  The two which should be considered carefully are the match groups and key identifier settings.  If these are not set according to your platform (classlink vs clever) and group name conventions, you will not be able to sync users. The other options are filters that determine what kind of data can be fetched.  The default group and user filters will be explained in the next section as they apply directly to the group mapping configuration.  

	Lastly, the all_users_filter (as indicated in the comments above) is only applicable when the --users all command is specified on the command line or in place of --users mapped in the user-sync-config.yml.  This filter determines exactly which user types are pulled in by --users all.  You can set it to students, teachers, or users (both).  This setting does not affect the group filters.  

	To help make the configuration clearer, please look at the examples below.  These show how one can configure the connector for both cases of clever and classlink.  In the clever example, an access token (TEST_TOKEN) is shown.  Using this token will allow to access the Clever sandbox data for testing purposes.  You should replace this or comment it out,  using the client_id and client_secret to access your real API.

	For **Clever:** 

    ```yaml
    connection:
        platform: 'clever'
        access_token: 'TEST_TOKEN'
        host: 'https://api.clever.com/v2.1/'    
        
        page_size: 3000
        max_user_count: 0
    
    schema:
        match_groups_by: 'name'
        key_identifier: 'id'
        all_users_filter: 'users'
        default_group_filter: 'sections'
        default_user_filter: 'students'
    ```
    
    For **Classlink:**

    ```yaml
    connection:
        platform: 'classlink'
        client_id: 'api client id here'
        client_secret: 'api client secret here'
        host: 'https://example-ca-v2.oneroster.com/ims/oneroster/v1p1/'
    
        page_size: 3000
        max_user_count: 0
    
    schema:
        match_groups_by: 'title'
        key_identifier: 'sourcedId'
        all_users_filter: 'users'
        default_group_filter: 'classes'
        default_user_filter: 'students'
    ```

In this way we provide maximum flexibility with the options for standard simple group mappings.

### The group matching definition
In the above discussion, we did leave out a key piece of information - we have implicitly assumed that all of our target objects have a "name" filed that we can match (like "Class 003...").  But, what if we need to match on a unique identifier instead (like SIS_ID, id, sourced id) or on some other custom field (course number, etc).  Why should we be forced to use the name?  Answer: we are not!  The field named "match_groups_by" in connector-oneroster.yml allows you to specify exactly what you want to match with your group name.  This can be set to any available field on the target object (according to the api schema).  In the default configuration, it is set to "name" for clever and "title" for classlink.  This could just as easily be "sourcedId" or some other field.  Assuming for the moment that we have set "match_groups_by" to **sourcedId**, we could write our groups query as follows (assuming that "5cfb063268d44802ad7b2fb8" is the sourcedId for the section of interest)

For the above case, the connector will return all students in the class whose 'SIS_ID' is '89571'.  The pattern shows that 'match_groups_by' should be set according to how you wish to identify a group in user-sync-config.yml, in the groups section.  The default for this field is 'name', which is the a good choice for Clever, since most objects have a 'name'.  For Classlink, you might consider setting this to 'title' for classes or courses, and 'name' for schools.

### Using multiple matchers
You can use an array to specify which fields to match against.  This is helpful when you want to select one group based on ID, and another based on name.  In Classlink, schools and classes have different name fields: name and title, so you can use this feature to fetch from both at once.  All you need to do is change the match_groups_by field to be a list, like so:


# Reference

## Errors and definitions
Compiled errors from testing..?

## Table of parameters and descriptions

|Field                    |Type                                    |Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |Example                                                                                          |
|-------------------------|----------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
|**Connection**|++++++++++++|+++++++++++++++++++++++++++++++++++++++++++++++++++++||
|platform                 |required (no default)                   |specifies which platform to use.  Can ONLY be one of: [classlink, clever]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |clever                                                                                           |
|client_id                |required if no access_token (no default)|Client ID from SIS dashboard                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |5d8a7b5eff61ga25bc6e                                                                             |
|client_secret            |required if no access_token (no default)|Client Secret from SIS dashboard                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |c6d2c6745c12ae785f7f1a58a307a04cf0a4                                                             |
|host                     |required (no default)                   |Endpoint for organization's OneRoster implementation                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |Clever: https://api.clever.com/v2.1/ Classlink: https://example.oneroster.com/ims/oneroster/v1p1/|
|access_token             |optional (no default)                   |Allows to bypass API authentication for Clever.  Mainly useful for testing (use 'TEST_TOKEN') or to avoid putting credentials into the file.                                                                                                                                                                                                                                                                                                                                                                                                                           |TEST_TOKEN                                                                                       |
|page_size                |optional (default: 1000)                | api call page size.  Adjusting this will adjust the frequency of API calls made to the server                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |3000                                                                                             |
|max_user_count           |optional (default: 0)                   |API calls will cutoff after this many users.  Set to 0 for unlimited.  Useful when doing test runs to avoid pulling very large user counts.                                                                                                                                                                                                                                                                                                                                                                                                                            |0, 10, 50, 4000, etc…                                                                            |
|match_groups_by          |required (default: name)                |Attribute corresponding to the group name in user-sync-config.yml.  UST will match the desired value to this field (e.g., name, sourcedId, etc…).  For clever, "name" will suffice for schools, courses and sections.  For classlink, you can user "title" for classes/courses, and "name" for schools.                                                                                                                                                                                                                                                                                                                                                                                                                       |title, name, SIS_ID, sourceId, subject                                                           |
|key_identifier           |required (default: sourcedId)           | unique key used throughout One-Roster (sourcedId or id commonly used).  This may not be an arbitrary value, since it is used in the URL of the API calls.  It must exist and be the base ID for your platform.                                                                                                                                                                                                                                                                                                                                                        |sourcedId, id                                                                                    |
           |                                        |                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |                                                                                                 |


