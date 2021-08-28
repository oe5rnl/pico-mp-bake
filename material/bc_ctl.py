# pip install windows-curses
# pip installpyserial ?

import json
import serial
import time
import curses

# pip install pyserial

def send():
   
    c = {
            "version":"0.10",
            "cw_speed": "100",
            "msg": "OE5RNL OE5NVL",
            "on_time": 50,
            "pre_time": 2,
            "post_time": 2,
            "timeout_msg": 40,

            "ports":[    
                {"id":0,"mode":"b","gpio":25,"on_cmd": "01","off_cmd":"00", "morse_off_cmd":"03","morse_on_cmd":"04"},
                {"id":1,"mode":"b","gpio":16,"on_cmd": "11","off_cmd":"10", "morse_off_cmd":"13","morse_on_cmd":"14"},
                {"id":2,"mode":"b","gpio":17,"on_cmd": "21","off_cmd":"20", "morse_off_cmd":"23","morse_on_cmd":"24"},
                {"id":3,"mode":"b","gpio":18,"on_cmd": "31","off_cmd":"30", "morse_off_cmd":"33","morse_on_cmd":"34"},
                {"id":4,"mode":"s","gpio":19,"on_cmd": "41","off_cmd":"40", "morse_off_cmd":"43","morse_on_cmd":"44"},
                {"id":5,"mode":"s","gpio":20,"on_cmd": "51","off_cmd":"50", "morse_off_cmd":"53","morse_on_cmd":"54"},
                {"id":6,"mode":"s","gpio":21,"on_cmd": "61","off_cmd":"60", "morse_off_cmd":"63","morse_on_cmd":"64"},
                {"id":7,"mode":"s","gpio":22,"on_cmd": "71","off_cmd":"70", "morse_off_cmd":"73","morse_on_cmd":"74"},
            ]
        }



    # print(c["ports"][0])
    # print(c["ports"][0]["pin"])
    # print(c["version"])
    # print(c["cw_speed"])

    #y = json.dumps(c, indent=2)
    y = json.dumps(c)
    print(y)

    s = serial.Serial("COM5", 9600, timeout = None)
    s.close()
    s.open()
    s.write(chr(2).encode("utf8")) # STX
    for c in y:
        s.write(c.encode("utf8"))
        time.sleep(0.05)
    s.write(chr(3).encode("utf8")) # ETX
    s.close()

    #port.write(y.encode("utf8"))

    # s = serial.Serial("COM5", 9600, timeout = None)
    # s.close()
    # s.open()
    # s.write("*VVV#".encode("UTF8"))
    # time.sleep(0.1)
    # bytesToRead = s.inWaiting()
    # for a in range(1,10):
    #     print(s.read(bytesToRead))
    #     time.sleep(0.1)
    # s.close()

    #z = json.loads(y)
    #print(z)


def main():
    send()

if __name__ == '__main__':
    main()


# print(c["ports"]["a"])
#     
# 
# 
# 
# 
# 
# 
# # a Python object (dict):
# x = {
#   "name": "John",
#   "age": 30,
#   "city": "New York"
# }
# 
# # convert into JSON:
# y = json.dumps(x)
# 
# # the result is a JSON string:
# print(y)
# 
# 
# 
# x =  '{ "name":"John", "age":30, "city":"New York"}'
# 
# # parse x:
# y = json.loads(x)
# 
# # the result is a Python dictionary:
# print(y["age"])
# 
# 
# # 
# # 
# # #c= '{ "stuff": {"onetype": [{"id":1,"name":"John Doe"},{"id":2,"name":"Don Joeh"}],"othertype": {"id":2,"company":"ACME"}} }'
# # 
# # c = '{"country abbreviation": "US","places": [    {        "place name": "Belmont",        "longitude": "-71.4594",        "post code": "02178",        "latitude": "42.4464"    },    {        "place name": "Belmont",        "longitude": "-71.2044",        "post code": "02478",        "latitude": "42.4128"    }],"country": "United States","place name": "Belmont","state": "Massachusetts","state abbreviation": "MA"}'
# # 
# # 
# # # ,
# # # "otherstuff": {
# # #         "thing": [[1,42],[2,2]]
# # #      }
# # 
# # 
# # data = json.loads(c)
# # print(data['places']['latitude'])
# # 
# 
# # 
# # c = {
# #     "ports"[    
# #             {"id":1,"mode":"b","pin":"25","on-cmd": "11","off_cmd":"10", "temp_on_cmd":"13","temp_off_cmd":"14"},
# #             {"id":2,"mode":"s","pin":"21","on-cmd": "21","off_cmd":"20", "temp_on_cmd":"23","temp_off_cmd":"24"},
# #             {"id":3,"mode":"s","pin":"22","on-cmd": "31","off_cmd":"30", "temp_on_cmd":"33","temp_off_cmd":"34"},
# #             {"id":4,"mode":"s","pin":"24","on-cmd": "41","off_cmd":"40", "temp_on_cmd":"43","temp_off_cmd":"44"},
# #             {"id":5,"mode":"s","pin":"25","on-cmd": "51","off_cmd":"50", "temp_on_cmd":"53","temp_off_cmd":"54"},
# #             {"id":6,"mode":"s","pin":"26","on-cmd": "61","off_cmd":"60", "temp_on_cmd":"63","temp_off_cmd":"64"},
# #             {"id":7,"mode":"s","pin":"27","on-cmd": "71","off_cmd":"70", "temp_on_cmd":"73","temp_off_cmd":"74"},
# # ]
# #     }
# # 
# # print(c["id"])
# # 
# # #obj.stuff.onetype[0].id
# # #obj.stuff.othertype.id
# # #obj.otherstuff.thing[0][1]  //thing is a nested array or a 2-by-2 matrix.
# # #                            //I'm not sure whether you intended to do that.