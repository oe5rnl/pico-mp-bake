import json
        
        
c = {
        "version":"0.8",
        "cw_speed": "100",
        "msg": "OE5RNL OE5NVL",
        "on_time": 50,
        "pre_time": 5,
        "post_time": 5,
        "timeout_msg": 20,

        "ports":[    
            {"id":1,"mode":"b","pin":"25","on_cmd": "11","off_cmd":"10", "temp_on_cmd":"13","temp_off_cmd":"14"},
            {"id":2,"mode":"b","pin":"21","on_cmd": "21","off_cmd":"20", "temp_on_cmd":"23","temp_off_cmd":"24"},
            {"id":3,"mode":"b","pin":"22","on_cmd": "31","off_cmd":"30", "temp_on_cmd":"33","temp_off_cmd":"34"},
            {"id":4,"mode":"b","pin":"24","on_cmd": "41","off_cmd":"40", "temp_on_cmd":"43","temp_off_cmd":"44"},
            {"id":5,"mode":"s","pin":"25","on_cmd": "51","off_cmd":"50", "temp_on_cmd":"53","temp_off_cmd":"54"},
            {"id":6,"mode":"s","pin":"26","on_cmd": "61","off_cmd":"60", "temp_on_cmd":"63","temp_off_cmd":"64"},
            {"id":7,"mode":"s","pin":"27","on_cmd": "71","off_cmd":"70", "temp_on_cmd":"73","temp_off_cmd":"74"},
        ]
    }


print(c['ports'][2]['on_cmd'])
print(c['version'])

js = json.dumps(c)
print(js)

v = js[0]

a = js['ports'][0]['mode']
