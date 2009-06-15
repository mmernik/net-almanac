#some JSON strings for testing

bad_json_strings = ('aaaa', #not a JSON strong
                    '[{"pk": 1, "model": "event.event", "fields": {"iface": "Ethernet0", "name": "experiment", "tags": "lbnl, experiment", "url": "http://www.lbl.gov", "end_datetime": "2009-06-03 15:01:01", "begin_datetime": "2009-06-01 12:21:15", "router": "router1", "descrip": "a physics experiment"}}]', #description spelled wrong
                    '[{"pk": 1, "model": "event.event", "fields": {"iface": "Ethernet0", "name": "experiment", "tags": "lbnl, experiment", "url": "http://www.lbl.gov", "end_datetime": "2009-06-03 15:01:01", "begin_datetime": "2009-06-01 12:21:15", "router": "router1"}}]', #missing description field
                    '[{"pk": 1, "model": "event.event", "fields": {"iface": "Ethernet0", "name": "experiment", "tags": "lbnl, experiment", "url": "http://www.lbl.gov", "end_datetime": "2009-06-03 15:01:01", "begin_datetime": "no datetime", "router": "router1", "description": "a physics experiment"}}]', #bad date
                    '[{"pk": 1, "model": "events.event", "fields": {"iface": "Ethernet0", "name": "experiment", "tags": "lbnl, experiment", "url": "http://www.lbl.gov", "end_datetime": "2009-06-03 15:01:01", "begin_datetime": "2009-06-01 12:21:15", "router": "router1", "description": "a physics experiment"}}]', #wrong model
                    '[{"pk": 2, "model": "event.event", "fields": {"iface": "Ethernet0", "name": "experiment", "tags": "lbnl, experiment", "url": "http://www.lbl.gov", "end_datetime": "2009-06-03 15:01:01", "begin_datetime": "2009-06-01 12:21:15", "router": "router1", "description": "a physics experiment"}}]', #wrong pk
                    '[{"pk": 1, "model": "event.event", "fields": {"iface": "Ethernet0", "name": "experiment", "tags": "lbnl, experiment", "url": "http://www.lbl.gov", "end_datetime": "2009-06-03 15:01:01", "begin_datetime": "2009-06-01 12:21:15", "router": "router1", "description": ""}}]', #empty description
                    '[{"pk": 1, "model": "event.event", "fields": {"iface": "Ethernet0", "name": "experiment", "tags": "lbnl, experiment", "url": "http://www.lbl.gov", "end_datetime": "2009-06-03 15:01:01", "begin_datetime": "2009-06-01 12:21:15", "router": "router1", "description": "a physics experiment", "owner": "andy"}}]', #extra field
                    
                    )

NEW_DESCRIPTION = 'a laser experiment'

good_json_string = '[{"pk": 1, "model": "event.event", "fields": {"iface": "Ethernet0", "name": "experiment", "tags": "lbnl, experiment", "url": "http://www.lbl.gov", "end_datetime": "2009-06-05 15:01:03", "begin_datetime": "2009-06-01 12:21:15", "router": "router1", "description": "' + NEW_DESCRIPTION + '"}}]' #edits end_datetime and description

bad_create_string = good_json_string #bad pk, it's already in use.

good_create_string = '[{"pk": 10, "model": "event.event", "fields": {"iface": "Ethernet0", "name": "gragragra", "tags": "hi, hir a a", "url": "http://www.lbl.gov", "end_datetime": "2009-06-02 12:21:15", "begin_datetime": "2008-06-11 12:21:15", "router": "router1", "description": " a"}}]'


json_headers = {'accept':'application/json'}