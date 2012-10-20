#!/usr/bin/python
#
# main.py
# Copyright (C) 2012 Luca Gasperini <luca.gasperini@gmail.com>
# 
# Sagi is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Sagi is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

from gi.repository import Gtk, GdkPixbuf, Gdk
import os, sys
from gi.repository import GObject as gobject

gobject.set_prgname("sagi")

###Test for threads


#Aria Object
import aria as Aria



#Comment the first line and uncomment the second before installing
#or making the tarball (alternatively, use project variables)
UI_FILE = "src/sagi.ui"
#UI_FILE = "/usr/local/share/sagi/ui/sagi.ui"


class GUI:
    """Contains all the methods to manage the gui"""
    
    def refresh_list(self):
        """this handles the timer and get the list of items that are passed to refresh single"""
        self.aria.start_thread ()
        self.all_info= self.aria.all_info
        self.item_list=self.all_info["item_list"]


        gid_list = []
        self.treeview_list = []
        self.liststoreDownloads.foreach(self.get_list_of_treeview, None) 

        """Add to the GUI newdownloads if any and create a list of gid known by aria"""
        for item in self.item_list:
            gid_list.append(item.gid)
            if not item.gid in self.treeview_list:
                self.liststoreDownloads.append([item.gid,item.path,item.size,item.progress,item.speed,item.estimated,item.connections])

        """Remove from GUI downloads that are not in aria2 anymore"""
        self.liststoreDownloads.foreach(self.remove_from_treeview,gid_list)

        """Refresh single items of the treeview"""
        self.liststoreDownloads.foreach(self.refresh_single,self.item_list)

        """Set Cells function, one for all and one specific for progress bar"""
        list=self.get_columns_titles()
        self.treeviewDownloads.get_column(list.index("Progress")).set_cell_data_func(self.cellrendererprogressPB, self.set_cell_progress,self.item_list)

        """Update Label of Total Download Speed"""
        global_stats=self.all_info["global_stats"]
        if global_stats:
            self.labelDownSpeed.set_text("D: "+self.aria.convert_bytes (global_stats['downloadSpeed']))
        else:
            self.labelDownSpeed.set_text("")
        if self.item_list:
            number_active=0
            number_waiting=0
            number_complete=0
            for item in self.item_list:
                if item.status=="active":
                    number_active += 1
                elif item.status=="waiting":
                    number_waiting +=1
                elif item.status=="complete":
                   number_complete +=1
            tooltip_text = "Downloading %s at %s\nWaiting: %s\nCompleted:%s" % (number_active, self.aria.convert_bytes (global_stats['downloadSpeed']), number_waiting,number_complete)
            self.statusicon.set_tooltip_text(tooltip_text)

        

        return True	

    def remove_from_treeview(self,model, path, iter,gid_list):
        """Removes from GUI downloads that are not in aria2 anymore"""
        id=model.get_value(iter,0)
        if not id in gid_list:
            self.liststoreDownloads.remove(iter)

    def get_list_of_treeview(self,model, path, iter, Data=None):
        """Get all files present in treeview"""
        id=model.get_value(iter,0)
        self.treeview_list.append(id) 
        
    def refresh_single(self,model, path, iter, item_list):
        """Refresh single items of the treeview"""
        id=model.get_value(iter,0)
        for item in item_list:
            if item.gid == id:
                list = [item.gid,item.path,item.size,item.progress,item.speed, item.estimated, item.connections]

                    
        for value in list:
            self.liststoreDownloads.set_value(iter, list.index(value),value)
    
    def get_columns_titles(self):
        """ get column titles in order"""
        column_titles_list=[]
        for column in self.treeviewDownloads.get_columns():
            column_titles_list.append(column.get_title())
        return column_titles_list
    
    def set_cell_progress(self,column, cell_renderer, model, iter, item_list):
        """This function change the color and text of progress bar base on download status"""
        id=model.get_value(iter,0)
        dict={}
        for item in self.item_list:
            dict[item.gid] =item.status
        if dict[id]=='paused':
            cell_renderer.set_property('text', "Paused")
            #cell_renderer.set_property('cell-background', "grey")
        elif dict[id]=='complete':
            cell_renderer.set_property('text', "Complete")
            #cell_renderer.set_property('cell-background', "green")
            
        elif dict[id]=='removed':
            cell_renderer.set_property('text', "Removed")
            #cell_renderer.set_property('cell-background', "red")
        elif dict[id]=='error':
            cell_renderer.set_property('text', "Error")
            cell_renderer.set_property('cell-background', "red")
        elif dict[id]=='waiting':
            cell_renderer.set_property('text', "Waiting")
            #cell_renderer.set_property('cell-background', "grey")
        else:
            cell_renderer.set_property('text', None)
            #cell_renderer.set_property('cell-background', None)
            
    

    #
    #   GUI signals
    #
    
    def on_tbStart_clicked(self, widget, data=None):
        treeviewSelection=self.treeviewDownloads.get_selection()
        treeviewSelection.selected_foreach(self.aria.start,self.treeview_list)

    def on_tbStop_clicked(self, widget, data=None):
        treeviewSelection=self.treeviewDownloads.get_selection()
        treeviewSelection.selected_foreach(self.aria.pause,self.treeview_list)

    def on_tbRemoveAll_clicked(self, widget, data=None):
        self.aria.remove_all()
    
    def on_tbRemove_clicked(self, widget, data=None):
        treeviewSelection=self.treeviewDownloads.get_selection()
        treeviewSelection.selected_foreach(self.aria.remove,self.item_list)

    def on_tbAdd_clicked(self, widget, data=None):
        self.dialogAdd.run()
        
    def on_spinbuttonDownSpeed_value_changed(self, widget, data=None):
        self.aria.change_DownSpeed(self.spinbuttonDownSpeed.get_value())
        pass

    def on_statusicon_query_tooltip(self, widget, data=None):
        print "tooltip"

    def on_statusicon_activate(self, widget, data=None):
        visible = self.window.get_property("visible")
        if visible:
           self.window.hide()
        else:
           self.window.show()
        
    def __init__(self):
        #
        #   GTK BUilder Stuff
        #
        self.builder = Gtk.Builder()
        self.builder.add_from_file(UI_FILE)
        self.builder.connect_signals(self)
        #
        #   Get GTK Objects
        #
        self.window = self.builder.get_object('mainWindow')
        self.dialogAdd = self.builder.get_object('dialogAdd')
        self.liststoreDownloads = self.builder.get_object("liststoreDownloads")
        self.treeviewDownloads = self.builder.get_object("treeviewDownloads")
        self.cellrendererprogressPB = self.builder.get_object("cellrendererPB")
        self.labelDownSpeed = self.builder.get_object("labelDownSpeed")
        self.spinbuttonDownSpeed = self.builder.get_object("spinbuttonDownSpeed")
        self.statusicon = self.builder.get_object("statusicon")
        self.window.show_all()
        #
        #   Initiation of Aria Object
        #
        self.aria = Aria.Aria()



        self.spinbuttonDownSpeed.set_value(int(self.aria.downloadSpeed))
        #
        #   Timer to refresh the gui, it calls refresh_list
        #
        maintimer = gobject.timeout_add(1000, self.refresh_list)
        #gobject.idle_add(self.refresh_list)
	
    def on_mainWindow_destroy(self, widget, data=None):
        Gtk.main_quit()
        
    def on_addWindow_destroy(self, widget, data=None):
        Gtk.main_quit()

def main():
    app = GUI()
    Gtk.main()
		
if __name__ == "__main__":
    sys.exit(main())
