# -*- coding:utf-8 -*-

#import sys,os
import wx
import GUI as ui
import multiprocessing
import UartProcess
import re
import serial

SUBMENU   = 0
MENUITEM  = 1
CHECKITEM = 2
SEPARATOR = 3
RADIOITEM = 4

MenuDefs = (
('&Operation', (
    (MENUITEM,  wx.NewId(), '&Open Port',         'Open the Port' ,     'self.OnOpenPort'  ),
    (MENUITEM,  wx.NewId(), '&Close Port',        'Close the Port',     'self.OnClosePort' ),
    (SEPARATOR,),
    (MENUITEM,  wx.NewId(), '&Exit MyTerm',       'Exit this tool',     'self.OnExitApp'   ),
)),
('&Display', (
    (CHECKITEM, wx.NewId(), 'Always on top',      'always on most top',  'self.OnAlwayOnTop'     ),
    (CHECKITEM, wx.NewId(), 'Local echo',         'echo what you typed', 'self.OnShowStatusBar'  ),
    (MENUITEM,  wx.NewId(), 'Show S&etting Bar',  'Show Setting Bar',    'self.OnShowSettingBar' ),
    (SUBMENU, 'Rx display as', (
        (RADIOITEM, wx.NewId(), 'ASCII', '', 'self.OnRxAsciiMode' ),
        (RADIOITEM, wx.NewId(), 'HEX',   '', 'self.OnRxHexMode'   ),
    )),
    (SUBMENU, 'Tx display as', (
        (RADIOITEM, wx.NewId(), 'ASCII', '', 'self.OnTxAsciiMode' ),
        (RADIOITEM, wx.NewId(), 'HEX',   '', 'self.OnTxHexMode'   ),
    )),
#     (CHECKITEM, wx.NewId(), 'S&tatus Bar',        'Show Status Bar',    'self.OnShowStatusBar'  ),
)),
('&Help', (
    (MENUITEM,  wx.NewId(), '&About',             'About  MyTerm',      'self.OnAbout' ),
))
)

regex_matchPort = re.compile('(?P<port>\d+)')

class MyApp(wx.App):
    def OnInit(self):
        self.frame = ui.MyFrame(None, wx.ID_ANY, "")
        
        self.frame.SplitterWindow.SetSashSize(0)
        self.frame.SplitterWindow.SetSashPosition(160, True)
        
        self.frame.chiocePort.AppendItems(('COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8'))
        self.frame.chiocePort.Select(0)
        # initial variables

        self.serialport = serial.Serial()
#         print self.GetPort()
#         print self.GetBaudRate()
#         print self.GetDataBits()
#         print self.GetParity()
#         print self.GetStopBits()
#         print self.GetHandShake()
        
        # Make a menu
        menuBar = wx.MenuBar()
        for m in MenuDefs:
            menu = wx.Menu()
            for k in m[1]:
                self.MakeMenu(menu, k)
            menuBar.Append(menu, m[0])

        self.frame.SetMenuBar(menuBar)
        
        self.frame.btnHideBar.Bind(wx.EVT_BUTTON, self.OnHideSettingBar)
        self.frame.Bind(wx.EVT_WINDOW_DESTROY, self.Cleanup)
 
        self.SetTopWindow(self.frame)
        self.frame.Show()
        
        self.processCommunicate = multiprocessing.Process(name = 'Uart_Communicate',
                                    target = UartProcess.UartCommunicate, 
                                    args = (None, None))
        
#         self.processCommunicate.start()
        
        return True

    def GetPort(self):
        r = regex_matchPort.search(self.frame.chiocePort.GetLabelText())
        if r:
            return int(r.group('port')) - 1
        return

    def GetBaudRate(self):
        return int(self.frame.cmbBaudRate.GetLabelText())

    def GetDataBits(self):
        s = self.frame.choiceDataBits.GetLabelText()
        if s == '5': 
            return serial.FIVEBITS
        elif s == '6': 
            return serial.SIXBITS
        elif s == '7': 
            return serial.SEVENBITS
        elif s == '8': 
            return serial.EIGHTBITS
    
    def GetParity(self):
        s = self.frame.choiceParity.GetLabelText()
        if s == 'None': 
            return serial.PARITY_NONE
        elif s == 'Even': 
            return serial.PARITY_EVEN
        elif s == 'Odd': 
            return serial.PARITY_ODD
        elif s == 'Mark': 
            return serial.PARITY_MARK
        elif s == 'Space': 
            return serial.PARITY_SPACE
        
    def GetStopBits(self):
        s = self.frame.choiceStopBits.GetLabelText()
        if s == '1': 
            return serial.STOPBITS_ONE
        elif s == '1.5': 
            return serial.STOPBITS_ONE_POINT_FIVE
        elif s == '2': 
            return serial.STOPBITS_TWO
            
    def MakeMenu(self, menu, args = ()):
#         print args
        if args[0] == 1:
            menu.Append(args[1], args[2], args[3])
            eval('self.frame.Bind(wx.EVT_MENU,' + args[4] + ', id = args[1])')
        elif args[0] == CHECKITEM:
            menu.AppendCheckItem(args[1], args[2], args[3])
            eval('self.frame.Bind(wx.EVT_MENU,' + args[4] + ', id = args[1])')
        elif args[0] == SEPARATOR:
            menu.AppendSeparator()
        elif args[0] == RADIOITEM:
            menu.AppendRadioItem(args[1], args[2], args[3])
            eval('self.frame.Bind(wx.EVT_MENU,' + args[4] + ', id = args[1])')
        elif args[0] == SUBMENU:
            submenu = wx.Menu() 
            for i in args[2:][0]:
                self.MakeMenu(submenu, i)
            menu.AppendSubMenu(submenu, args[1])
            
    def OnOpenPort(self, evt = None):
        self.serialport.port     = self.GetPort()
        self.serialport.baudrate = self.GetBaudRate()
        self.serialport.bytesize = self.GetDataBits()
        self.serialport.stopbits = self.GetStopBits()
        self.serialport.parity   = self.GetParity()
        self.serialport.rtscts   = self.frame.chkboxrtscts.IsChecked()
        self.serialport.xonxoff  = self.frame.chkboxxonxoff.IsChecked()
        try:
            self.serialport.open()
        except serial.SerialException, e:
            dlg = wx.MessageDialog(None, str(e), "Serial Port Error", wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        else:
#             self.StartThread()
            self.SetTitle("Serial Terminal on %s [%s, %s%s%s%s%s]" % (
                self.serial.portstr,
                self.serial.baudrate,
                self.serial.bytesize,
                self.serial.parity,
                self.serial.stopbits,
                self.serial.rtscts and ' RTS/CTS' or '',
                self.serial.xonxoff and ' Xon/Xoff' or '',
                )
            )
    
    def OnClosePort(self, evt = None):
        if self.serialport.isOpen():
            self.serialport.close()
    
    def OnHideSettingBar(self, evt = None):
        self.frame.SplitterWindow.SetSashPosition(1, True)
        
    def OnShowSettingBar(self, evt = None):
        self.frame.SplitterWindow.SetSashPosition(160, True)
    
    def OnShowStatusBar(self, evt = None):
        pass
    
    def OnRxAsciiMode(self, evt = None):
        
        pass
    
    def OnRxHexMode(self, evt = None):
        
        pass
        
    def OnTxAsciiMode(self, evt = None):
        
        pass
    
    def OnTxHexMode(self, evt = None):
        
        pass

    def OnAlwayOnTop(self, evt = None):
        if evt.Selection == 1:
            style = self.frame.GetWindowStyle()
            # stay on top
            self.frame.SetWindowStyle( style | wx.STAY_ON_TOP )
        else:
            style = self.frame.GetWindowStyle()
            # normal behaviour again
            self.frame.SetWindowStyle( style & ~wx.STAY_ON_TOP )
    
    def OnAbout(self, evt = None):
        pass
    
    def OnExitApp(self, evt = None):
        self.frame.Close(True)
    
    def Cleanup(self, evt = None):
        if self.processCommunicate.is_alive():
            self.processCommunicate.terminate()
        self.OnClosePort()


if __name__ == '__main__':
    app = MyApp(0)
    app.MainLoop()