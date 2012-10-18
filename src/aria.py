import xmlrpclib, datetime,time
from gi.repository import GObject as gobject
from gi.repository import Gtk
import threading
class AriaItem(file):
    """Object that stores all the information of each item in aria download list"""
    
    def __init__(self,file):
        self.gid = file["gid"]
        if file["files"][0]["path"]:
            self.path = file["files"][0]["path"]
        else:
            self.path = file["files"][0]["uris"][0]["uri"].rsplit("/",1)[1]
        if file["totalLength"] != "0":
            self.size = self.convert_bytes (file["totalLength"])
            self.progress = int(float(file["completedLength"])/float(file["totalLength"])*100)
        else:
            self.size = file["totalLength"]
            self.progress = 0
        self.status = file["status"]
        if file["downloadSpeed"] != "0":
            self.speed = self.convert_bytes (file["downloadSpeed"])
            self.remainingLenght = int(file["totalLength"])-int(file["completedLength"])
            self.estimated = str(datetime.timedelta(seconds = int(float(self.remainingLenght)/float(file["downloadSpeed"]))))
        else:
            self.speed = "N/A"
            self.estimated= ""
        if self.status == "active":
            self.connections = file["connections"]
        else:
            self.connections = "N/A"
            
    def convert_bytes(self,bytes):
        """Method to convert bytes"""    
        bytes = float(bytes)
        if bytes >= 1099511627776:
            terabytes = bytes / 1099511627776
            size = '%.2fT' % terabytes
        elif bytes >= 1073741824:
            gigabytes = bytes / 1073741824
            size = '%.2fG' % gigabytes
        elif bytes >= 1048576:
            megabytes = bytes / 1048576
            size = '%.2fM' % megabytes
        elif bytes >= 1024:
            kilobytes = bytes / 1024
            size = '%.2fK' % kilobytes
        else:
            size = '%.2fb' % bytes
        return size

      
        
    
    
class Aria():
    """Object that contains everything aria related that is not specific of an item"""
    
    def __init__(self):
        self.server = xmlrpclib.ServerProxy('http://casagas.dyndns.org:6801/rpc').aria2
        gobject.threads_init()
        self.all_info = {}
        self.all_info["item_list"]=[]
        self.all_info["global_stats"]=[]
    
    def rpc_ask (self):
        """Return a list of objects in all states Active,Waiting and Stopped, see docs tellActive"""
        file_list=[]        
        item_list=[]
        global_stats={}
        all_info = {}
        for file in self.server.tellActive():
           file_list.append(file)
        for file in self.server.tellWaiting(0,100):
           file_list.append(file)
        for file in self.server.tellStopped(0,100):
           file_list.append(file)
        for file in file_list:
           item = AriaItem(file)
           item_list.append (item)
        global_stats = self.server.getGlobalStat ()  

        all_info["item_list"]=item_list
        all_info["global_stats"]=global_stats
        self.all_info=all_info

    def get_all(self):
        return self.all_info     
        
    def start_thread(self):
        if threading.active_count () == 1:
            thread = threading.Thread(target=self.rpc_ask)          
            thread.start()

        
        
        

    

    #
    #   Aria commands, connected to buttons in the toolbar
    #
    def start(self, model, path, iter,treeview_list):
        self.server.unpause(model.get_value(iter,0))
        
    def pause(self, model, path, iter,treeview_list):
        self.server.pause(model.get_value(iter,0))

    def remove(self, model, path, iter,item_list):
        for item in item_list:
            if item.gid == model.get_value(iter,0):
                if item.status =="active":
                    #self.server.remove (model.get_value(iter,0))
                    self.server.removeDownloadResult (model.get_value(iter,0))
                if item.status in ["complete","error","removed"]:
                    self.server.removeDownloadResult (model.get_value(iter,0))
                self.server.remove (model.get_value(iter,0))
    
    def remove_all(self):
        self.server.purgeDownloadResult ()

    def unpause(self,gid):
        self.server.unpause(gid)
        
    def add(self,url):

        self.server.addUri(url)


        
    def convert_bytes(self,bytes):
        """Method to convert bytes"""    
        bytes = float(bytes)
        if bytes >= 1099511627776:
            terabytes = bytes / 1099511627776
            size = '%.2fT' % terabytes
        elif bytes >= 1073741824:
            gigabytes = bytes / 1073741824
            size = '%.2fG' % gigabytes
        elif bytes >= 1048576:
            megabytes = bytes / 1048576
            size = '%.2fM' % megabytes
        elif bytes >= 1024:
            kilobytes = bytes / 1024
            size = '%.2fK' % kilobytes
        else:
            size = '%.2fb' % bytes
        return size

    def change_DownSpeed(self,speed):
        pass

    




  