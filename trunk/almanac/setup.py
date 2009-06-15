import httplib2
url = "http://localhost:8000/event/1/"
headers = {'accept':'application/json'}
body = {'data':'[{"pk": 1, "model": "event.event", "fields": {"iface": "Ethernet0", "name": "experiment", "tags": "lbnl, experiment", "url": "http://www.lbl.gov", "end_datetime": "2009-06-03 15:01:01", "begin_datetime": "2009-06-01 12:21:15", "router": "router1", "description": "a science experiment"}}]'}
json_string = '[{"pk": 1, "model": "event.event", "fields": {"iface": "Ethernet0", "name": "experiment", "tags": "lbnl, experiment", "url": "http://www.lbl.gov", "end_datetime": "2009-06-03 15:01:01", "begin_datetime": "2009-06-01 12:21:15", "router": "router1", "description": "a science experiment"}}]'


response,content = http.request(url,'PUT',headers=headers,body=json_string)