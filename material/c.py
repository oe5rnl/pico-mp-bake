import json


class Config:

    def __init__(self):

        #self.wd = Wdt(8000)
        
        self.config_file = 'config.json'

        self.c = {
                'saves': '0',
                'Version': '0.99',
                'CW Speed': '100',
                'Bakentext': 'OE5RNL',
                'On Time': '2',
                'Pre Time': '2',
                'Post Time':'2',
                'CW Off Timeout': '20',
                'ports':[    
                    {'id':'0','Name':'LED',   'Mode':'B','gpio':'25','On': '01','Off':'00','Port On':'1', 'CW Off':'03','CW On':'04'},
                    {'id':'1','Name':'10 GHZ','Mode':'B','gpio':'16','On': '11','Off':'10','Port On':'1', 'CW Off':'13','CW On':'14'},
                    {'id':'2','Name':'24 GHZ','Mode':'S','gpio':'17','On': '21','Off':'20','Port On':'1', 'CW Off':'23','CW On':'24'},
                    {'id':'3','Name':'74 GHZ','Mode':'S','gpio':'18','On': '31','Off':'30','Port On':'0', 'CW Off':'33','CW On':'34'},
                    {'id':'4','Name':'FREI',  'Mode':'S','gpio':'19','On': '41','Off':'40','Port On':'0', 'CW Off':'43','CW On':'44'},
                    {'id':'5','Name':'FREI',  'Mode':'S','gpio':'20','On': '51','Off':'50','Port On':'0', 'CW Off':'53','CW On':'54'},
                    {'id':'6','Name':'FREI',  'Mode':'S','gpio':'21','On': '61','Off':'60','Port On':'0', 'CW Off':'63','CW On':'64'},
                    {'id':'7','Name':'FREI',  'Mode':'S','gpio':'22','On': '71','Off':'70','Port On':'0', 'CW Off':'73','CW On':'74'},
                ]
                }
        
        self.load()

    def get_attr(self, a):
        return self.c[a]

    def set_attr(self,a,v):
        self.c[a] = v

    def get_port_attr(self,p,a):
        return self.c['ports'][p][a]

    def set_port_attr(self,p,a,v):
        self.c['ports'][p][a] = v

    def get_port(self,id):
        return self.c['ports'][id]

    def load(self):
        try:
            self.f = open(self.config_file,'r')
            self.txt = self.f.read()
            self.c = json.loads(self.txt)
            print('config from fs loaded')
        except: 
            print('load failed -  use default')
            self.c = self.c

    def save(self):
        print('s1')
        self.set_attr('saves',str(int(self.get_attr('saves'))+1))

        txt='daklsdjajsljkdaldjlajdlajldjasjdlajdlajdklalkdjakldjlajdlajldajlsdjaldlkakldadk'
        txt+='daklsdjajsljkdaldjlajdlajldjasjdlajdlajdklalkdjakldjlajdlajldajlsdjaldlkakldadk'

        #txt = 'Hallo'

        with open(self.config_file, 'w') as fp:
            print('s2')
            json.dump(self.c, fp)
            #fp.write(txt)
            #fp.write(str(self.c))
            print('s3')

        print(self.c)

    def get_intatt(self,a):
        return int(self.get_attr(a))*1000



def main():
    config=Config()

    #while True:
    config.save()

if __name__ == "__main__":
    main()

