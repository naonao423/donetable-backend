import requests
import json
import ics
import os
from ics import Calendar,timeline
import datetime,arrow
cwd = os.getcwd()
URL_default = ["http://p67-caldav.icloud.com/published/2/MTAyMTE2MzQ2ODgxMDIxMVdCYe666XhA45SX9t4LkLyQm3HMpDRp5T6mmc3VcFJlYZp6tm__xN1ou14tpdFQRLqMq66DfexcuvA6bjS-0SY","http://p67-caldav.icloud.com/published/2/MTAyMTE2MzQ2ODgxMDIxMVdCYe666XhA45SX9t4LkLxk0TwWcPb6pTjAwXcy6qe6iX4G-56UqoaDer6nQiVa56BGA76QVXBzVWAzoh90XRk"]
now = arrow.now("Asia/Tokyo")
localnow = now.to("Asia/Tokyo")
yesterday = now.shift(days=-24)
localyes = yesterday.to("Asia/Tokyo")
tomorrow = now.shift(days=+20)
localtom = tomorrow.to("Asia/Tokyo")




class Get_cal:
    def __init__(self,ics_url=URL_default,days=0):
        self.a = 0        
        self.url = ics_url
    
    def test(self):
        return {"test3":"test4"}

    def request_ics_file(self):
        if type(self.url) == list:
            output_dic = []
            for url in self.url:

                s = requests.Session()
                try:
                    responce = s.get(url)
                except:
                    try:
                        responce = s.get(url)
                    except:
                        print("接続できませんでした")
                ical = responce.text
#                print(type(ical))
                def Listtostring(s):  

                    # initialize an empty string 
                    str1 = ""  
                    
                    # traverse in the string   
                    for ele in s:  
                        str1 += ele +"\n"   
                    
                    # return string   
                    return str1 
                icallist = ical.splitlines()
                icallist.insert(3,"PRODID:-//hacksw/handcal//NONSGML\n")
    #            print(icallist)
                ical2 = Listtostring(icallist)
                #print(ical2)
                #with open("test.ics") as f:
                #    content = f.read()
                #    print(type(content)
                c = Calendar(ical2)
                t2 = c.timeline
                #.included(start=yesterday,stop=tomorrow)
#                print(list(t2))
                out = {"file":str(type(t2))}
#                print(out,type(out))
                output_dic.extend(list(t2))
#                print(type(output_dic),output_dic)
            return output_dic

        else:
            s = requests.Session()
            try:
                responce = s.get(self.url)
            except:
                try:
                    responce = s.get(self.url)
                except:
                    print("接続できませんでした")
            ical = responce.text
#            print(type(ical))
            def Listtostring(s):  

                # initialize an empty string 
                str1 = ""  
                
                # traverse in the string   
                for ele in s:  
                    str1 += ele +"\n"   
                
                # return string   
                return str1 
            icallist = ical.splitlines()
            icallist.insert(3,"PRODID:-//hacksw/handcal//NONSGML\n")
#            print(icallist)
            ical2 = Listtostring(icallist)
            #print(ical2)
            #with open("test.ics") as f:
            #    content = f.read()
            #    print(type(content)
            c = Calendar(ical2)
            t2 = c.timeline
            #.included(start=yesterday,stop=tomorrow)
#            print(list(t2))
            out = {"file":str(type(t2))}
#            print(out,type(out))
            return list(t2)               



    #おそらく最初からこんな木構造にする必要はないと思われる
    def assign_to_dics(self):
        sublist=["Nap","Programing","English","Study","Meditation","Stretch","英単語","Reading"]
        #既存のデータの読み込み
        #with open("data.json") as f:
        #    try:
        #        dic = json.load(f)
        #    except:
        #        print("assign読み込めませんでした")
        #データがcalendarツリーを持っているかを確認。

        #selfのdaysとbackday,file_open_dataとfile_open_searchdaysを呼び出す。
        
        output_dic = []
        dataset = self.request_ics_file()
        #print(dataset)
        for part in dataset:
            if part.name =="Programming":
                name = "Programing"
            else:
                name = part.name
#            print(name)
            dic = {"uid":str(part.uid),"sub":str(part.name),"begin_time":str(part.begin),"duration":str(part.duration)}
            output_dic.append(dic)
        #json_file = json.dumps(output_dic,indent=4)
        #with open ("data.json","w") as file:
        #    json.dump(output_dic,file,indent=4)
        #json.dumpsメソッドの返り値の型はstr型になるのでdict型で残すならそのまま返す
        #return json.dumps(output_dic,indent=4) 
        return output_dic

if __name__ == "__main__":
    #print(get_duriation().request_ics_file())
    print(Get_cal().assign_to_dics())
