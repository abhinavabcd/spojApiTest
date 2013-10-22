#!/usr/bin/python
import re
import sys

import urllib
import re
from lxml.html import parse, tostring, clean
from lxml.etree import strip_tags
import pprint
import StringIO
#from Levenshtein import ratio
import yajl as json
import socket
import time
import urllib2
import re 

from poster.encode import multipart_encode
from poster.streaminghttp import register_openers


register_openers()

url_loader=urllib2.build_opener(urllib2.HTTPCookieProcessor(),urllib2.ProxyHandler())
urllib2.install_opener(url_loader)

def get_data(url,post=None,headers={}):
    req=urllib2.Request(url,post,headers)
    return url_loader.open(req)

class SpojApi:
# data members
    user_=""
    pass_=""
# methods
    def __init__(self, local_file=None):      
        # let browser fool robots.txt
        pass

    def login(self, username, password):
        self.user_=username
        self.pass_=password
        data="login_user="+username+"&password="+password+"&submit=Log+In"
        get_data("https://www.spoj.com/logout", data)
    
    
    def submit(self, problem, source, lang):    
        post = urllib.urlencode({"source": source,
                                             "lang":lang,
                                             "problemcode":problem
                                             })
        data= get_data("http://www.spoj.com/submit/complete/", post).read()
        print data
        
        m = re.search(r'"newSubmissionId" value="(\d+)"/>',  data)
        if (m == None):
            return -1 
            
        submission_id = int(m.group(1))
        return submission_id
    
    def get_sub_results(self,sub_id): #GO CRAPPY SHIT ! WHO ON THE EARTH WRTE THIS
        items_per_page=20
        
        pg=get_data("http://www.spoj.pl/status/" + self.user_ + "/all")
        
        from BeautifulSoup import BeautifulSoup
        
        row_data = {}
        row_data['id'] = sub_id
        
        soup = BeautifulSoup( pg.read() )
        max_id=soup.find("input", { "id" : "max_id"}, recursive=True)['value']
        
        id_link=soup.find("a", {"sid" : str(sub_id), "title" :"View source code"}, recursive=True)
        
        row=id_link.parent.parent
            
        row_data['date'] = row.find("td", "status_sm").string.strip()
        row_data['result'] = row.find("td", "statusres").contents[0].strip()
        row_data['time'] = row.find("td", id="statustime_"+str(sub_id)).a.string.strip()
        cell_mem = row.find("td", id="statusmem_"+str(sub_id))
        if (cell_mem.a):
              row_data['mem'] = cell_mem.a.string.strip()
              stdio_link = "/files/stderr/" + str(sub_id)
              row_data['stdio'] = self.fetch_from_link( stdio_link )
        else:
              row_data['mem'] = cell_mem.string.strip()
        
                        
        cell_lang = row.find("td", "slang")
        if (cell_lang.a):
              test_link = "/files/psinfo/" + str(sub_id)
              row_data['test_info'] = self.fetch_from_link( test_link )
        
        return row_data
