import xmlrpclib, gobject, datetime

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
            self.remainingLenght = file["totalLength"]-file["completedLength"]
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
        self.object_list=[]
        self.global_stats = {}
        maintimer = gobject.timeout_add(1000, self.rpc_ask_all )

    def get_all_files(self):
        return self.object_list
        
    def get_global_stats(self):
        return self.global_stats

    
    def rpc_ask_all (self):
        """Return a list of objects in all states Active,Waiting and Stopped, see docs tellActive"""
        file_list=[]
        for file in self.server.tellActive():
            file_list.append(file)
        for file in self.server.tellWaiting(0,100):
            file_list.append(file)
        for file in self.server.tellStopped(0,100):
            file_list.append(file)
        object_list=[]
        for file in file_list:
            object = AriaItem(file)
            object_list.append (object)
        self.object_list = object_list
        self.global_stats = self.server.getGlobalStat ()
        return True
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

    #
    #   Get info from aria
    #
    def rpc_get_global_stats(self):
        return self.server.getGlobalStat ()
        
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
        
    """----------OLD-------------"""

    
    def send_command(self, model, path, iter,command,file_info_dict):
        if command=="pause":
            self.server.pause(model.get_value(iter,0))
        if command=="start":
            self.server.unpause(model.get_value(iter,0))
        if command=="remove":
            if file_info_dict[model.get_value(iter,0)]['status']=="active":
                print "active"
            
            #self.server.remove(model.get_value(iter,0))
            #self.server.removeDownloadResult (model.get_value(iter,0))
    
    def unpause(self,gid):
        self.server.unpause(gid)
    def add(self,url):
        print url
        self.server.addUri(url)
    def start(self, model, path, iter,treeview_list):
        self.server.unpause(model.get_value(iter,0))
    def pause(self, model, path, iter,file_info_dict):
        self.server.pause(model.get_value(iter,0))



    def get_file_info(self,file,list):
        """store all needed info for a file and return a dict containing all info"""
        file_info={}
        file_info['status']= file['status']
        for column in list:
            if column =="#":
                file_info['#']= str(file['gid'])
            if column =="File":
                if file['files'][0]['path']:
                    file_info['File']= file['files'][0]['path']
                else:
                    o = urlparse(file['files'][0]['uris'][0]['uri'])
                    file_info['File']= os.path.basename(o[2])
            if column =="Size":
                file_info['Size']= self.convert_bytes(file['files'][0]['length'])
            if column =="Progress":
                file_info['Progress']=self.get_progress(file)
            if column =="Speed":
                if file_info['status'] in ["waiting","error","paused","stopped","complete","removed"]:
                    file_info['Speed']=None
                else:
                    file_info['Speed']=self.convert_bytes(file['downloadSpeed'])
            if column =="Connections":
                file_info['Connections']=file['connections']
        return file_info

    def get_file_info_dict(self,sagi):
        file_info_dict={}
        for file in self.get_all_files():
            file_info=self.get_file_info(file,sagi.get_columns_titles())
            file_info_dict[file_info['#']]=file_info
        return file_info_dict
            
    def change_download_limit_single(self,gid):
        self.server.changeOption(str(gid), {'max-download-limit':'1K'})

    
    

    def get_progress(self,file):
        compl= float(file['files'][0]['completedLength'])
        total= float(file['files'][0]['length'])
        if total > 0:
            done=int((compl/total)*100)
        else:
            done=0
        return done
            


    def convert_bytes(self,bytes):
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
