#!/usr/bin/env python3

# stolen from 
# http://indefero.soutade.fr/p/genericmonitor/source/tree/master/examples/picture.py

from topbarSetter.genericmonitor import *

class PicturePopup(GenericMonitor):

    def __init__(self):
        self.item = None
        self.setupMonitor()
        self.count = 0 
        self.time_widget = GenericMonitorTextWidget(f'Temp text', 'color:white')
        self.button_hovered = False

    def set_text(self, text):
        self.time_widget.setText(text)
        try:
            self.notify(self.group_outer)
        except:
            print("failed to update value")
        
    def create_popup(self, today_text):
        title_widget = GenericMonitorTextWidget(f"Classes:", 'color:black;font-weight:bold;') # No name here
        classes_widget = GenericMonitorTextWidget(f"{today_text}", 'color:black;') # No name here
        popup = GenericMonitorPopup([title_widget, classes_widget])
        signals = {
            'on-click':'toggle-popup',
        }
        self.time_item = GenericMonitorItem('picturepopup', [self.time_widget], signals)
        self.popup_item = GenericMonitorItem('picturepopup', [], signals, popup)
        self.group_outer = GenericMonitorGroup('PicturePopup', [self.time_item])
        self.group_popup = GenericMonitorGroup('PicturePopup', [self.popup_item])
        self.notify(self.group_outer)
        self.notify(self.group_popup)
        
    def _forMe(self, sender):
        return str(sender).endswith(self.item.getFullName())

    def onClick(self, sender):
        if not self._forMe(sender): return
        # self.notify(self.group)
        # print('Click from {}'.format(sender))