import lxml
import os.path
import re
import string
import time
import random
import tornado.auth
import smtplib
import torndb
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import unicodedata
from tornado.options import define, options
import yajl as json
from spoj_api import *
import config 

define("port", default=8885, help="run on the given port", type=int)
define("mysql_host", default="127.0.0.1:3306", help="database host")
define("mysql_database", default="news_articles_portal", help="database name")
define("mysql_user", default="root", help="database user")
define("mysql_password", default="warrior_within", help="database password")


class spoj_application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            static_path=os.path.join(os.path.dirname(__file__), "html/"),
            cookie_secret="11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            login_url="/auth/login",
            autoescape=None,
        )
        static_path = dict(path=settings['static_path'], default_filename='index.html')
           
        handlers = [                    
           
            (r"/main", mainPage),
            (r"/uploadCode", uploadCode),
            (r"/viewStatus", viewStatus),            
            (r"/html/(.*)", tornado.web.StaticFileHandler,static_path)               
        ]
        tornado.web.Application.__init__(self, handlers, **settings)
        
        # Have one global connection to the blog DB across all handlers
#         self.db = tornado.database.Connection(
#             host=options.mysql_host, database=options.mysql_database,
#             user=options.mysql_user, password=options.mysql_password)

class mainPage(tornado.web.RequestHandler):
    def prepare(self):
        pass
    def get(self):
        self.post()
    def post(self):
        self.render("./html/mainPage.html")
class viewStatus(tornado.web.RequestHandler):
    def prepare(self):
        pass 
    def get(self):
        self.post()
    def post(self):
        id=self.get_argument("id",None)
        spoj = SpojApi()    
        spoj.login( config.userName, config.password)

        table="<table><tr><th>key</th><th>value</th></tr>"
        result=spoj.get_sub_results(id)
        for i in result.keys():
            table+="<tr><td>"+i+"</td><td>"+result[i]+"</td></tr>"
        table+="</table>"        
        self.finish(table)
        
        

class uploadCode(tornado.web.RequestHandler):
    def prepare(self):
        pass
    def get(self):
        self.post()
    def post(self):
        source=self.get_argument("source",None)
        problem=self.get_argument("problemCode",None)
        lang=self.get_argument("lang",None)
        if(not source or not problem or not lang):
            self.finish("Error submit code")
            return

        spoj = SpojApi()    
        spoj.login( config.userName, config.password)

        id=spoj.submit(problem, source, lang)
        if(id>0):
            self.finish("Code Successfully uploaded with <a href='./viewStatus?id="+str(id)+"'>"+str(id)+"</a>")
            return
        
        self.finish("Error submit code")

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(spoj_application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
            