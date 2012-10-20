from xdg import BaseDirectory
import os
import ConfigParser

class Config(object):
    def __init__(self):
        self._dir=os.path.join(BaseDirectory.xdg_config_home,"sagi")
        if not os.path.isdir(self._dir):
            os.mkdir(self._dir)
        self._file=os.path.join(self._dir,"sagi.conf")
 
        self._cfg = ConfigParser.RawConfigParser()
        if not os.path.isfile(self._file):
            self._cfg.add_section('Config')
            self._setHost("localhost")
            self._setPort("6800")
            self._setUsername("")
            self._setPassword("")
        else:
            self._cfg.read(self._file)
 
    def _getHost(self):
        return self._cfg.get('Config', 'Host')
 
    def _setHost(self,v):
        self._cfg.set('Config', 'Host',v)
        self._save()
        
    def _getPort(self):
        return self._cfg.get('Config', 'Port')
 
    def _setPort(self,v):
        self._cfg.set('Config', 'Port',v)
        self._save()
        
    def _getUsername(self):
        return self._cfg.get('Config', 'Username')
 
    def _setUsername(self,v):
        self._cfg.set('Config', 'Username',v)
        self._save()
        
    def _getPassword(self):
        return self._cfg.get('Config', 'Password')
 
    def _setPassword(self,v):
        self._cfg.set('Config', 'Password',v)
        self._save()
           
 
    Host=property(_getHost,_setHost)
    Port=property(_getPort,_setPort)
    Username=property(_getUsername,_setUsername)
    Password=property(_getPassword,_setPassword)
 
 
    def _save(self):
        fid=open(self._file, 'wb')
        if fid:
            self._cfg.write(fid)
            fid.close()