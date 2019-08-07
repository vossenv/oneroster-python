# Oneroster Python Client

This library facilitates easy access to the user database from Clever or Classlink.  
The connectors provide single-method calls that will return users (students, teachers or both) from the provider of your choice,
based on class, course, or school membership without the need for paging and response handling.  Additional documentation to come.

For the time being, this library **only returns users** for differente classes, courses and schools - it was designed for this purpose as integrated into a sync process.  Additional options for fetching other data types will hopefully come down the line.

- https://developer.classlink.com/
- https://dev.clever.com/v2.1/reference
- https://www.imsglobal.org/oneroster-v11-final-specification

For details on the development of this library, visit https://github.com/vossenv/oneroster-python

Contact Danimae Vossen (vossen.dm@gmail.com) for inquiries


# Quick Start

*Note: a full version of this code can be found [here](https://github.com/vossenv/oneroster-quickstart "here")

`pip install oneroster`

Begin by installing the oneroster dependency as above (home is [here](https://pypi.org/project/oneroster/ "here")).  The constructor takes more than 3 arguments, but 3 is all you need to instantiate it.  These arguments are:

1. host name - this should come from your SIS dashboard (classlink here).  It may look different for different providers
2. client_id - also from SIS dashboard
3. client_secret - also from SIS dashboard

Import and instantiate the connector (Classlink) as shown.

```python
import oneroster
from pprint import pprint						# optional

connector = oneroster.ClasslinkConnector(
    host="https://example.oneroster.com/ims/oneroster/v1p1/",
    client_id='your_client_id',
    client_secret='your_client_secret',
)
```
For a first try, you can call **get_users**, giving a single argument: 'students'.  This will return a list of all the students in the system.
```python
user_list = connector.get_users(user_filter='students')

print(str(len(user_list)) + " students in total")
pprint(user_list[0])
```

The connector queries are made up of 3 main arguments:

 user_filter - this 'filter's the kind of user requested.  The options are: students, teachers, and users.  students and teachers work for any query, but users is only available when getting a full list (e.g.:
 /ims/oneroster/v1p1/users)

group_filter - the word 'group filter' is chosen to represent how users might be grouped.  This can be any of: classes, courses, schools.  This is equivalent of making an api call like:
/ims/oneroster/v1p1/classes/class_id/{user_filter}

group_name - the 'group name' indicates which class, course or school we want to target.  This might be the name or id of a class.  The final query with the group and user filters looks like this: /ims/oneroster/v1p1/{group_filter}/{group_name}/{user_filter}

For example:
/ims/oneroster/v1p1/classes/31763/students

The following snippets should help to illustrate this.  Consider the simple case of getting all students for classes named ELA (6A ELA):

```python
class_name = "ELA 6 (6A ELA)"
ela_users = connector.get_users(user_filter='students',
                                group_filter='classes',
                                group_name=class_name)

print(str(len(ela_users)) + " users found for ELA 6")
```

Alternatively, we can query the same class using it's sourcedId.  This second case may return less results, because an id corresponds to a specific section, whereas the classname gets all sections sharing that name.

```python
class_id = "31763"
ela_users = connector.get_users(user_filter='students',
                                group_filter='classes',
                                group_name=class_id)

print(str(len(ela_users)) + " users found for ELA 6 (1 section)")
```

We can expand the option of "match groups by" by setting the connector option.  The default is ['sourcedId', 'name', 'title'], which means that the group name you enter will be compared against these three fields for matches.  This means you can make queries using any of those 3 fields.  For example, we can query for "Classlink HS" and school with id 7 (the middle school), and both will return results.  You are free to set the match_groups_by field to any of the fields in your target object (a class, course, or school)

```python
hschool_users = connector.get_users(user_filter='students',
                                    group_filter='schools',
                                    group_name='Classlink HS')

mschool_users = connector.get_users(user_filter='students',
                                    group_filter='schools',
                                    group_name='7')

print(str(len(hschool_users)) + " high school students returned")
print(str(len(mschool_users)) + " middle school students returned")
```

You can change the matcher by setting the class level property or by passing it with get_users.  As an example, let's say we want to get the number of students with classes in room 302.  We can look at the available JSON properties from the api standard, and see that 'location' represents a room.  We can pass this expicitly in the call as shown.  Note that for the moment, only *string* type matchers are allowed.  The 'grades' field is represented by a list like ['11'] - and so it is an invalid matcher.  Extended matching functionality will come in a future release.

```python
connector.match_groups_by = ['sourcedId', 'name', 'title', 'location']
or
connector.match_groups_by = 'location'
or
r302_users = connector.get_users(user_filter='students',
                                group_filter='classes',
                                group_name='302',
                                match_on='location')

print(str(len(r302_users)) + " students with classes in room 302")

```
When run, the above  snippets result in the following output:

```
139 students in total.  First result:

{'agents': [],
 'dateLastModified': '2019-03-01T18:14:45.000Z',
 'email': 'billy.flores@classlink.k12.nj.us',
 'enabledUser': 'true',
 'familyName': 'FLORES',
 'givenName': 'BILLY',
 'grades': ['11'],
 'identifier': '17580',
 'middleName': 'DASEAN',
 'orgs': [{'href': 'https://adobe-ca-v2.oneroster.com/ims/oneroster/v1p1/orgs/2',
           'sourcedId': '2',
           'type': 'org'}],
 'password': '',
 'phone': '',
 'role': 'student',
 'sms': '',
 'sourcedId': '18125',
 'status': 'active',
 'userIds': [{'identifier': '18125', 'type': 'FED'}],
 'username': 'billy.flores'}

7 users found for ELA 6
3 users found for ELA 6 (1 section)
38 high school students returned
54 middle school students returned
13 students with classes in room 302
```