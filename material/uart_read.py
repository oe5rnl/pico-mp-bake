from machine import UART


c = {
        "Version":"0.5",
        "CW Speed": "100",
        "Bakentext": "OE5RNL OE5NVL",
        "On Time": "50",
        "Pre Time": "5",
        "Post Time": "5",
        "CW Off Timeout": "20",

        "ports":[    
            {"id":"0","Name":"LED",   "Mode":"b","gpio":"25","On": "01","Off":"00", "CW Off":"03","CW On":"04"},
            {"id":"1","Name":"10 GHz","Mode":"b","gpio":"16","On": "11","Off":"10", "CW Off":"13","CW On":"14"},
            {"id":"2","Name":"24 GHz","Mode":"b","gpio":"17","On": "21","Off":"20", "CW Off":"23","CW On":"24"},
            {"id":"3","Name":"74 GHz","Mode":"b","gpio":"18","On": "31","Off":"30", "CW Off":"33","CW On":"34"},
            {"id":"4","Name":"Frei",  "Mode":"s","gpio":"19","On": "41","Off":"40", "CW Off":"43","CW On":"44"},
            {"id":"5","Name":"Frei",  "Mode":"s","gpio":"20","On": "51","Off":"50", "CW Off":"53","CW On":"54"},
            {"id":"6","Name":"Frei",  "Mode":"s","gpio":"21","On": "61","Off":"60", "CW Off":"63","CW On":"64"},
            {"id":"7","Name":"Frei",  "Mode":"s","gpio":"22","On": "71","Off":"70", "CW Off":"73","CW On":"74"},
        ]
        }


f=open('config.txt', 'w')
f.write('Hallo')
f.close()


#, timeout=5000

# txt='123456'
# txt = txt[:-1]
# txt = txt[:-1]
# print(txt)

# u = UART(id=0, baudrate=9600, bits=8, parity=None, timeout=10, stop=1, rxbuf=256, txbuf=256)

# while True:
#     if u.any():
#         c = u.read()
#         if c != None:   
#             print(c)

# #while True:
# #    line = u.readline()
# #print(line)
