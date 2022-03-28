import sys
import tkinter as tk
from threading import Thread
import numpy as np
from misc import console_out, Benchmark
import time
import pyqtgraph as pg
from datetime import datetime
from NI_DAQ import AOport
from NI_DAQ import AOport2
from labjack import ljm
from MACEEXCELLOG import create_excel_mace, save_macelog_excel, last_shot


class GUI:
    def __init__(self, root, _IO):
        self.root = root
        self.root.configure(background='white')
        self.root.title("Arc Chamber Experiment Control")
        #self.root.minsize(400,400)
        self.T0 = time.time()
        self.benchmark = Benchmark()

        self.mainframe=tk.Frame(self.root, width=1600, height=1350)
        self.mainframe.pack(side=tk.TOP)
        self.maincanvas=tk.Canvas(self.mainframe, background='white', bg='white')#,scrollregion=(0,0,1350,2000))
        #self.vsb = tk.Scrollbar(self.mainframe, orient=tk.VERTICAL)
        #self.vsb.pack(side=tk.RIGHT, fill=tk.Y)
        #self.vsb.config(command=self.maincanvas.yview)
        self.maincanvas.config(width=1600, height=1350)
        #self.maincanvas.config(yscrollcommand=self.vsb.set)
        self.maincanvas.pack(side=tk.BOTTOM,expand=True, fill=tk.BOTH)
    
        
        self.time_text = tk.StringVar()
        self.time_label = tk.Label(self.maincanvas, textvariable = self.time_text, font = ("Courier", 20))
        self.time_label.pack(side=tk.TOP, fill=tk.X)
        #self.shot_number = tk.StringVar()              #Display from file
        #self.nshot_label = tk.Label(self.root, textvariable = self.shot_number, font = ("Courier", 20))
        #self.nshot_label.pack(side=tk.TOP, fill=tk.X)

        #MAKING THE SHOT BUTTONS
        self.info_frame = tk.Frame(self.mainframe, width=1600, height=1350)
        self.shot_buttons = tk.LabelFrame(self.maincanvas, background='white')
        self.shot_buttons.pack(side=tk.TOP, pady=10)

        self.simple_shot = tk.LabelFrame(self.shot_buttons, text="Simple shot", font=("Verdana", 12), background='white')
        self.simple_shot.pack(side=tk.LEFT, pady=10, padx = 15)

        self.per_shot = tk.LabelFrame(self.shot_buttons, text="Periodic shot", font=("Verdana", 12), background='white')
        self.per_shot.pack(side=tk.LEFT, pady=10, padx = 15)
        
        self.act_shot = tk.LabelFrame(self.shot_buttons, text="Active Shot", font=("Verdana", 12), background='white')
        self.act_shot.pack(side=tk.LEFT, pady=10, padx = 15)
        
        self.info_group = tk.LabelFrame(self.maincanvas, text="Live parameters", font=("Verdana", 12), background='white')
        self.info_group.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        self.varname_text = tk.StringVar()
        self.varname_label = tk.Label(self.info_group, textvariable=self.varname_text, font=("Courier", 12), bg='white', anchor=tk.NE, justify=tk.LEFT)

        self.value_text = tk.StringVar()
        self.value_label = tk.Label(self.info_group, textvariable=self.value_text, font=("Courier", 12), bg='white', anchor=tk.NE, justify=tk.LEFT)
                
        self.input_canvas = tk.Canvas(self.maincanvas, background='white', bg='white')

            
        def readValue(box, text1):#, nrow):
            value = tk.DoubleVar(box)
            label = tk.Label(box, text = text1, font=("Verdana", 12), bg='white')
            entry = tk.Entry(box, width = 5, textvariable = value, font=("Courier", 12), bg='white')
            entry.pack(side = tk.BOTTOM)
            label.pack(side = tk.BOTTOM)          
            return value
            
        def reset_values():
            try:
                self.topinput.destroy()
            except:
                pass
            try:
                self.input_frame.destroy()
            except:
                pass
            try:
                self.comment_frame.destroy()
            except:
                pass
            try:
                self.check_box.destroy()
            except:
                pass
            
        def add_comment():
            try:
                self.comment_frame.destroy()
            except:
                pass
            self.comment_frame = tk.Frame(self.input_frame, background='white')
            self.comment_frame.pack(side = tk.BOTTOM, pady = 10)
            commentlabel = tk.Label(self.input_frame, text = "SHOT Comment", font=("Verdana", 12), bg='white')
            self.comment = tk.StringVar(self.comment_frame)
            entry = tk.Entry(self.comment_frame, width = 30, textvariable = self.comment, font=("Courier", 12), bg='white')
            entry.pack(side = tk.BOTTOM)
            commentlabel.pack(side = tk.BOTTOM)

        def callback1():
            t = Thread(target = self.run_shot)
            console_out("Single Shot ON")
            t.start()
        
        def callback2():
            t = Thread(target = self.run_per_shot)
            console_out("Periodic Shot ON")
            t.start()
        

        def callback3():
            t = Thread(target = self.run_act_shot)
            console_out("Active Shot ON")
            t.start()

        def stopshot():
            t = Thread(target = self.stop)
            console_out("STOP SHOT")
            t.start()
  
        def set_values1():
            reset_values()
            self.topinput=tk.Toplevel()
            self.topinput.title("Input Control Values")
            self.topinput.lift(self.root)
            self.input_frame = tk.LabelFrame(self.topinput, text="Simple shot values", font=("Verdana", 12), background='white')
            self.input_frame.pack (side = tk.TOP)
            self.shottype = "Simple Shot"
            self.stop_button1 = tk.Button(self.input_frame, text="Stop shot!", font=("Verdana", 12), command=stopshot, bg = 'white')
            self.stop_button1.pack(side=tk.BOTTOM, pady=5)
            self.run_buttoninput = tk.Button(self.input_frame, text="Shot", font=("Verdana", 14), command=callback1, bg = 'white')
            self.run_buttoninput.pack(side=tk.BOTTOM, pady=5)
            add_comment()
            self.A = readValue(self.input_frame, "Shot duration (s): ")
            self.B = readValue(self.input_frame, "Stabilization time (s): ")
            self.C = readValue(self.input_frame, "Varc final (V): ")
            self.D = readValue(self.input_frame, "Varc initial (V): ")
            self.E = readValue(self.input_frame, "Ifil final (A): ") 
            self.F = readValue(self.input_frame, "Ifil initial (A): ")
            self.Q = readValue(self.input_frame, "Gas Pressure final (mTorr): ")
            self.P = readValue(self.input_frame, "Gas Pressure initial (mTorr): ")
            #self.G = readValue(self.input_frame, "Number of steps: ")
            



        def set_values2():
            reset_values()
            self.topinput=tk.Toplevel()
            self.topinput.title("Input Control Values")
            self.topinput.lift(self.root)
            self.input_frame = tk.LabelFrame(self.topinput, text="Periodic shot values", font=("Verdana", 12), background='white')
            self.input_frame.pack (side = tk.TOP)
            
            #self.check_box = tk.Frame(self.input_frame, background='white')
            #self.check_box.pack (side = tk.TOP)
            

            
            self.shottype = "Periodic Shot"
            self.stop_button2 = tk.Button(self.input_frame, text="Stop shot!", font=("Verdana", 12), command=stopshot, bg = 'white')
            self.stop_button2.pack(side=tk.BOTTOM, pady=5)
            self.run_buttoninput2 = tk.Button(self.input_frame, text="Shot", font=("Verdana", 14), command=callback2, bg = 'white')
            self.run_buttoninput2.pack(side=tk.BOTTOM, pady=5)
            add_comment()
            self.A = readValue(self.input_frame, "Shot duration (s): ")
            self.B = readValue(self.input_frame, "Stabilization time (s): ")
            self.C = readValue(self.input_frame, "Varc final (V): ")
            self.D = readValue(self.input_frame, "Varc initial (V): ")
            self.E = readValue(self.input_frame, "Ifil final (A): ") 
            self.F = readValue(self.input_frame, "Ifil initial (A): ")
            self.G = readValue(self.input_frame, "Period (s): ")
            self.K = readValue(self.input_frame, "Pulse width (s): ")

            self.curr = tk.IntVar()
            chk1 = tk.Checkbutton(self.input_frame, background='white', text = "Periodic Fil Curr", variable = self.curr)
            chk1.pack(side = tk.BOTTOM)
            self.volt = tk.IntVar()
            chk2 = tk.Checkbutton(self.input_frame, background='white', text = "Periodic Arc Vol", variable = self.volt)
            chk2.pack(side = tk.BOTTOM)
                
        def set_values3():
            reset_values()
            self.topinput=tk.Toplevel()
            self.topinput.title("Input Control Values")
            self.topinput.lift(self.root)
            self.input_frame = tk.LabelFrame(self.topinput, text="Active shot values", font=("Verdana", 12), background='white')
            self.input_frame.pack (side = tk.TOP)
            self.shottype = "Active Shot"
            self.stop_button3 = tk.Button(self.input_frame, text="Stop shot!", font=("Verdana", 12), command=stopshot, bg = 'white')
            self.stop_button3.pack(side=tk.BOTTOM, pady=5)
            self.run_buttoninput3 = tk.Button(self.input_frame, text="Shot", font=("Verdana", 14), command=callback3, bg = 'white')
            self.run_buttoninput3.pack(side=tk.BOTTOM, pady=5)
            add_comment()
            self.A = readValue(self.input_frame, "Shot duration (s): ")
            self.B = readValue(self.input_frame, "Stabilization time (s): ")
            self.H = readValue(self.input_frame, "Varc maximum (V): ")
            self.D = readValue(self.input_frame, "Varc initial (V): ")
            self.I = readValue(self.input_frame, "Ifil maximum (A): ") 
            self.F = readValue(self.input_frame, "Ifil initial (A): ")
            self.J = readValue(self.input_frame, "Iprobe (mA): ")              
                       
                    
        #self.reset_button = tk.Button(self.root, text="Reset Entries", font=("Verdana", 14), command=reset_values, bg = 'white')
        #self.comments = tk.Button(self.maincanvas, text="Add SHOT Comment", font=("Verdana", 14), command=add_comment, bg = 'white')

        #SHOTBUTTONS
        self.run_button = tk.Button(self.simple_shot, text="Shot", font=("Verdana", 14), command=callback1, bg = 'white')
        self.setval_button = tk.Button(self.simple_shot, text="Set values", font=("Verdana", 14), command=set_values1, bg = 'white')

        self.run_button2 = tk.Button(self.per_shot, text="Shot", font=("Verdana", 14), command=callback2, bg = 'white')
        self.setval_button2 = tk.Button(self.per_shot, text="Set values", font=("Verdana", 14), command=set_values2, bg = 'white')

        self.run_button3 = tk.Button(self.act_shot, text="Shot", font=("Verdana", 14), command=callback3, bg = 'white')
        self.setval_button3 = tk.Button(self.act_shot, text="Set values", font=("Verdana", 14), command=set_values3, bg = 'white')
        
        #MAKING THE MACE CONTROL (INPUT) SECTION
        def analyze_spectrum():
            self._temp = self._IO.spectroscopy.fit(self._IO.spectra[0])
        self._IO = _IO

        self.spectrum_button = tk.Button(self.input_canvas, text="Spectrum", font=("Verdana", 12), command=analyze_spectrum, bg = 'white')
        self.shutdown_button = tk.Button(self.input_canvas, text="Exit", font=("Verdana", 12), command=None, bg = 'white')
        self.stop_button = tk.Button(self.input_canvas, text="Stop", font=("Verdana", 12), command=None, bg = 'white')

        #THIS IS OPENVALVE PRESSURE
        def change_openvalve_pressure(a, b, c):
            try:
                int(self.openvalve_pressure_value.get())
            except:
                return
            self._IO.openvalve_pressurebase = int(self.openvalve_pressure_value.get())
            
        self.openvalve_pressure_label = tk.LabelFrame(self.input_canvas, text="Open Valve Pressure (mTorr)", font=("Verdana", 10), background='white')
        self.openvalve_pressure_value = tk.StringVar()        
        self.openvalve_pressure_value.set(_IO.openvalve_pressurebase)
        self.openvalve_pressure_value.trace_add("write", change_openvalve_pressure)
        self.openvalve_pressure_spinbox = tk.Spinbox(self.openvalve_pressure_label, from_=0, to=50, font=("Verdana", 14), textvariable=self.openvalve_pressure_value, width=3)

        def set_MFC(_open, openvalve_pressure):
            p = AOport('/Dev3/ao0')
            p_close = AOport2('Dev3/ao1')
            if(_open):
                console_out("Opening mass flow controller valve")
                p.write(openvalve_pressure/10-0.2)
                p_close.write(1)
            else:
                console_out("Closing mass flow controller valve")
                p.write(0)
                p_close.write(0)
            p.close()
            p_close.close()
        
        self.open_button = tk.Button(self.input_canvas, text="Open valve", font=("Verdana", 12), command=lambda:set_MFC(True, self._IO.openvalve_pressurebase), bg = 'white')
        self.close_button = tk.Button(self.input_canvas, text="Close valve", font=("Verdana", 12), command=lambda:set_MFC(False, self._IO.openvalve_pressurebase), bg = 'white')

        def change_overcurrent(a, b, c):
            try:
                int(self.overcurrent_value.get())
            except:
                return
            self._IO.I_max = int(self.overcurrent_value.get())

        self.overcurrent_label = tk.LabelFrame(self.input_canvas, text="Arc OC (A)", font=("Verdana", 10), background='white')
        self.overcurrent_value = tk.StringVar()        
        self.overcurrent_value.set(_IO.I_max)
        self.overcurrent_value.trace_add("write", change_overcurrent)
        self.overcurrent_spinbox = tk.Spinbox(self.overcurrent_label, from_=0, to=30, font=("Verdana", 14), textvariable=self.overcurrent_value, width=3)
        
        
        
        #here goes
        def change_overpressure(a, b, c):
            try:
                int(self.overpressure_value.get())
            except:
                return
            self._IO.P_max = int(self.overpressure_value.get())

        self.overpressure_label = tk.LabelFrame(self.input_canvas, text="P (kTorr)", font=("Verdana", 10), background='white')
        self.overpressure_value = tk.StringVar()        
        self.overpressure_value.set(_IO.P_max)
        self.overpressure_value.trace_add("write", change_overpressure)
        self.overpressure_spinbox = tk.Spinbox(self.overpressure_label, from_=0, to=30, font=("Verdana", 14), textvariable=self.overpressure_value, width=3)


        
        
        #MAKING THE MACE LOG WINDOW:

        def mace_log_line(box, text1):
            log_line = tk.StringVar(box)
            label = tk.Label(box, text = text1, font=("Verdana", 12), bg='white')
            entry = tk.Entry(box, width = 30, textvariable = log_line, font=("Courier", 12), bg='white')
            entry.insert(0,0)
            entry.pack(side = tk.BOTTOM)
            label.pack(side = tk.BOTTOM)
            return log_line
            

        def mace_log_save():
            macetext={'DATETIME': datetime.now().strftime('%m-%d-%Y_%H%M'), 'SHOTNUMBER': self.maceshotmanual.get(),'PRES': self.maceintpres.get(),'MACECOMMENT': self.macecomment.get(),'PORT1':self.diagport1.get(),'PORT2':self.diagport2.get(),'PORT3':self.diagport3.get(),'PORT4':self.diagport4.get(),'PORT5':self.diagport5.get(),'OTHER1':self.diagothers1.get(),'OTHER2':self.diagothers2.get(),'OTHER3':self.diagothers3.get(),'CONTROL':self.controlcodechange.get(),'ANALYZE':self.analyzecodechange.get()}
            if macetext['SHOTNUMBER']=='0':
                macetext['SHOTNUMBER']=last_shot()
            save_macelog_excel(macetext)
            console_out("MACE LOG Saved")
            self.topmace.destroy()
            
        def mace_log_open():
            try:
                self.topmace.destroy()
            except:
                pass
            self.topmace=tk.Toplevel()
            self.topmace.title("MACE Logging")
            self.topmace.lift(self.root)
            self.mace_frame = tk.LabelFrame(self.topmace, text="LOG MACE Alternations", font=("Verdana", 12), background='white')
            self.mace_frame.pack (side = tk.TOP)
            self.mace_frame_general=tk.LabelFrame(self.mace_frame, text="General Log", font=("Verdana",12), background='white')
            self.mace_frame_diag=tk.LabelFrame(self.mace_frame, text="Diagnostic Ports", font=("Verdana",12), background='white')
            self.mace_frame_other=tk.LabelFrame(self.mace_frame, text="Other Diagnostics", font=("Verdana",12), background='white')
            self.mace_frame_codelog=tk.LabelFrame(self.mace_frame, text="Code", font=("Verdana",12), background='white')
            self.mace_frame_general.pack(side=tk.TOP,pady=10)
            self.mace_frame_diag.pack(side=tk.TOP, pady=15)
            self.mace_frame_other.pack(side=tk.TOP, pady=15)
            self.mace_frame_codelog.pack(side=tk.TOP, pady=15)

            self.maceshotmanual=mace_log_line(self.mace_frame_general,"Applies for SHOT: ")
            self.macecomment=mace_log_line(self.mace_frame_general,"MACE comment: ")
            self.maceintpres = readValue(self.mace_frame_general, "Initial Pressure (10^(-6) Torr): ")
            
            self.diagothers3=mace_log_line(self.mace_frame_other,"Other Diagnostic 3: ")
            self.diagothers2=mace_log_line(self.mace_frame_other,"Other Diagnostic 2: ")
            self.diagothers1=mace_log_line(self.mace_frame_other,"Other Diagnostic 1: ")
            
            self.diagport5=mace_log_line(self.mace_frame_diag,"Diagnostic Port 5: ")
            self.diagport4=mace_log_line(self.mace_frame_diag,"Diagnostic Port 4: ")
            self.diagport3=mace_log_line(self.mace_frame_diag,"Diagnostic Port 3: ")
            self.diagport2=mace_log_line(self.mace_frame_diag,"Diagnostic Port 2: ")
            self.diagport1=mace_log_line(self.mace_frame_diag,"Diagnostic Port 1: ")
            
            self.analyzecodechange=mace_log_line(self.mace_frame_codelog,"Analyze Code Alternation: ")
            self.controlcodechange=mace_log_line(self.mace_frame_codelog,"Control Code Alternation: ")
            
            self.macelogsave=tk.Button(self.mace_frame, text="SAVE", font=("Verdana", 12), command=mace_log_save, bg='white')
            self.macelogsave.pack(side=tk.BOTTOM,pady=10)
            
        self.macelog = tk.Button(self.maincanvas, text="Open MACE LOG", font=("Verdana", 12),command=mace_log_open, bg ='white')

        #MAKING THE GUI INFOWINDOW INTERFACE
        self.run_button.pack(side=tk.TOP, pady=5)
        self.setval_button.pack(side=tk.TOP, pady=5)
        self.run_button2.pack(side=tk.TOP, pady=5)
        self.setval_button2.pack(side=tk.TOP, pady=5)
        self.run_button3.pack(side=tk.TOP, pady=5)
        self.setval_button3.pack(side=tk.TOP, pady=5)
        #self.comments.pack(side=tk.TOP, pady=10)
        self.macelog.pack(side=tk.TOP, pady=10)
        self.stop_button.pack(side=tk.RIGHT, padx=5)
        self.input_canvas.pack(side=tk.BOTTOM, fill=tk.X)
        self.spectrum_button.pack(side=tk.LEFT, padx=5)
        self.shutdown_button.pack(side=tk.LEFT, padx=5)
        
        self.openvalve_pressure_label.pack(side=tk.LEFT, padx=5)
        self.openvalve_pressure_spinbox.pack()
        
        self.overcurrent_label.pack(side=tk.LEFT, padx=5)
        self.overcurrent_spinbox.pack()
        ## here goes again
        self.overpressure_label.pack(side=tk.LEFT, padx=5)
        self.overpressure_spinbox.pack()        
        
        self.open_button.pack(side=tk.BOTTOM, padx=5, pady=5)
        self.close_button.pack(side=tk.BOTTOM, padx=5, pady=5)
        
        self.varname_label.pack(side=tk.LEFT, fill=tk.Y)
        self.value_label.pack(side=tk.RIGHT, fill=tk.Y)
        

        pg.setConfigOption('antialias', False)   #Enabling it causes lines to be drawn with smooth edges at the cost of reduced performance.
        #pg.setConfigOption('background', '#FFFAF0')   #Background configuration, color Floral white
        pg.setConfigOption('foreground', '#FEFEFA')   #Color for text, lines, axes, etc. Baby powder

        #MAKING THE MACE LOG WINDOW:
        def mace_log_open():
            try:
                self.topmace.destroy()
            except:
                pass
            self.topmace=tk.Toplevel()
            self.topmace.title("MACE Logging")
            self.topmace.lift(self.root)
            self.mace_frame = tk.LabelFrame(self.topinput, text="LOG MACE Alternations", font=("Verdana", 12), background='white')
            self.mace_frame.pack (side = tk.TOP)
            self.maceintpres = readValue(self.mace_frame, "Initial Pressure (10^(-6) Torr): ")

            



        
        #MAKING THE GRAPH WINDOW INTERFACE
        self.graphwindow = pg.GraphicsWindow(title="Arc Chamber Experiment Data View")
        #self.graphwindow.resize(1500, 900)
        
        self.plots = [self.graphwindow.addPlot(row=0, col=0),
                      self.graphwindow.addPlot(row=0, col=1),
                      self.graphwindow.addPlot(row=0, col=2),
                      self.graphwindow.addPlot(row=0, col=3),
                      self.graphwindow.addPlot(row=1, col=0),
                      self.graphwindow.addPlot(row=1, col=1),
                      self.graphwindow.addPlot(row=1, col=2),
                      self.graphwindow.addPlot(row=1, col=3),]
                      
        self.plotitems = [[plot.plot(pen=pg.mkPen('#79C257', width=2)),plot.plot(pen=pg.mkPen('#BF94E4', width=2))] for plot in self.plots]  #data line width and color
        
        self.data = [[np.array([]).reshape(0,2),np.array([]).reshape(0,2)] for plotitem in self.plotitems]      
        [[plotitem[0].setData(data[0]),plotitem[0].setData(data[1])] for [plotitem, data] in zip(self.plotitems, self.data)]      


        self.p2 = pg.ViewBox()      #Box that allows internal scaling/panning of children by mouse drag
        self.plots[2].showAxis('right')         #Filament graph
        self.plots[2].scene().addItem(self.p2)
        self.plots[2].getAxis('right').linkToView(self.p2)
        self.p2.setXLink(self.plots[2])
        def updateViews():
            self.p2.setGeometry(self.plots[2].vb.sceneBoundingRect())
            self.p2.linkedViewChanged(self.plots[2].vb, self.p2.XAxis)
       
        updateViews()
        self.plots[2].vb.sigResized.connect(updateViews)
        self.newdata1 = np.array([]).reshape(0,2)
        self.newitem1 = pg.PlotCurveItem(pen=pg.mkPen('#FEF65B', width=2)) #filament voltage, dodie yellow
        self.p2.addItem(self.newitem1)

        self.p1 = self.plots[3]         #Arc graph
        self.p3 = pg.ViewBox()
        self.p1.showAxis('right')
        self.p1.scene().addItem(self.p3)
        self.p1.getAxis('right').linkToView(self.p3)
        self.p3.setXLink(self.p1)
        def updateViews2():
            self.p3.setGeometry(self.p1.vb.sceneBoundingRect())
            self.p3.linkedViewChanged(self.p1.vb, self.p3.XAxis)
        updateViews2()
        self.p1.vb.sigResized.connect(updateViews2)
        self.newdata2 = np.array([]).reshape(0,2)
        self.newitem2 = pg.PlotCurveItem(pen=pg.mkPen('#FEF65B', width=2))  #arc current, dodie yellow
        self.p3.addItem(self.newitem2)
        
        """
        self.p2 = pg.ViewBox()      #Box that allows internal scaling/panning of children by mouse drag
        self.plots[3].showAxis('right')         #Filament graph
        self.plots[3].scene().addItem(self.p2)
        self.plots[3].getAxis('right').linkToView(self.p2)
        self.p2.setXLink(self.plots[3])
        def updateViews():
            self.p2.setGeometry(self.plots[3].vb.sceneBoundingRect())
            self.p2.linkedViewChanged(self.plots[3].vb, self.p2.XAxis)
       
        updateViews()
        self.plots[3].vb.sigResized.connect(updateViews)
        self.newdata1 = np.array([]).reshape(0,2)
        self.newitem1 = pg.PlotCurveItem(pen=pg.mkPen('#FEF65B', width=2)) #filament voltage, dodie yellow
        self.p2.addItem(self.newitem1)

        self.p1 = self.plots[4]                 #Arc graph
        self.p3 = pg.ViewBox()
        self.p1.showAxis('right')
        self.p1.scene().addItem(self.p3)
        self.p1.getAxis('right').linkToView(self.p3)
        self.p3.setXLink(self.p1)
        def updateViews2():
            self.p3.setGeometry(self.p1.vb.sceneBoundingRect())
            self.p3.linkedViewChanged(self.p1.vb, self.p3.XAxis)
        updateViews2()
        self.p1.vb.sigResized.connect(updateViews2)
        self.newdata2 = np.array([]).reshape(0,2)
        self.newitem2 = pg.PlotCurveItem(pen=pg.mkPen('#FEF65B', width=2))  #arc current, dodie yellow
        self.p3.addItem(self.newitem2)
        """
        
    def set_on_close(self, func):
        self.shutdown_button.configure(command=func)

    def stop_operation(self, func):
        self.stop_button.configure(command=func)
        
    def update(self):
        self.benchmark.mark()
        sys._clear_type_cache()
        """
        if self.benchmark.FPS < 6:
            ljm.eStreamStop(self.device)
            ljm.eStreamStart(self.device, self.stream_length, len(self.names), [ljm.nameToAddress(name)[0] for name in self.names], self.stream_length*self.stream_rate)  
        """        
 
        self.time_text.set(datetime.now().strftime('%H:%M:%S'))
        #self.shot_name.set()                   #Read from file
        tmem = 400
        
        self.update_plot(0, 0, self._IO.T-self.T0, self._IO.pressure, tmem, logarithmic=True)
        #self.update_plot(0, 0, self._IO.T-self.T0, self._IO.currshunt, tmem)
        self.plotitems[0][0].setPen('#00FFFF')          #Cyan
        self.plots[0].setLabel('bottom', text="Runtime (s)")
        self.plots[0].setLabel('left', text="Pressure (Torr)")
        #self.plots[0].setLabel('left', text="Current (mA)")
        
        #self.update_plot(1, 0, self._IO.T - self.T0, self._IO.ThTR1, tmem)#, ylim=[10,150])      # Type R (Blue)
        #self.update_plot(1, 1, self._IO.T - self.T0, self._IO.ThTE2, tmem)#, ylim=[10,150])      # Type E (Violet)
        #self.plots[1].setLabel('bottom', text="Runtime (s)")
        #self.plots[1].setLabel('left', text="Temperature (\u00b0 C)")

        self.update_plot(2, 0, self._IO.T-self.T0, self._IO.FIL_CUR_SETP, tmem, ylim=[0,120])
        self.plotitems[2][0].setPen('#CC00CC', style=pg.QtCore.Qt.DashLine)                 #Magenta  #Fil_cur_setp dotline
        self.update_plot(2, 1, self._IO.T-self.T0, self._IO.FIL_CUR, tmem)
        self.update_extra1( self._IO.T-self.T0, self._IO.FIL_VOL, tmem, ylim=[0,10])
        self.plotitems[2][1].setPen('#00FFFF')                                              #Cyan
        self.plots[2].setLabel('bottom', text="Runtime (s)")
        self.plots[2].setLabel('left', text="Filament current", units="A")
        self.plots[2].getAxis('right').setLabel("Filament voltage (V)", color='#FEF65B')    #Dodie Yellow
     
        self.update_plot(3, 0, self._IO.T-self.T0, self._IO.ARC_VOL_SETP, tmem, ylim=[0,160])
        self.plotitems[3][0].setPen('#CC00CC', style=pg.QtCore.Qt.DashLine)                 #Magenta     #Arc_vol_setp dotline
        self.update_plot(3, 1, self._IO.T-self.T0, self._IO.ARC_VOL, tmem)
        self.update_extra2( self._IO.T-self.T0, self._IO.ARC_CUR, tmem, ylim=[0,25])
        self.plotitems[3][1].setPen('#00FFFF')                                              #Cyan
        self.plots[3].setLabel('bottom', text="Runtime (s)")
        self.plots[3].setLabel('left', text="Arc voltage", units="V")
        self.plots[3].getAxis('right').setLabel("Arc current (A)", color='#FEF65B')         #Dodie Yellow

        if(self._IO.SPEC_OK):
            self.set_plot(4, 0, self._IO.spectra[0][:,0], self._IO.spectra[0][:,1], ylim=[0.0,65000], xlim =[300,1200])
            if(len(self._IO.spectra) > 1):
                self.set_plot(4, 1, self._IO.spectra[1][:,0], self._IO.spectra[1][:,1])
        self.plotitems[4][0].setPen('#5DADEC')      #Blue jeans
        self.plotitems[4][1].setPen('#F88379')      #Coral pink
        self.plots[4].setLabel('bottom', text="Wavelength (nm)", style = "bold")
        self.plots[4].setLabel('left', text="Intensity")   


        self.update_plot(5, 0, self._IO.T-self.T0, self._IO.currshunt, tmem)
        self.plotitems[5][0].setPen('#00FFFF')          #Cyan
        self.plots[5].setLabel('bottom', text="Runtime (s)")
        self.plots[5].setLabel('left', text="Current (mA)")


        trace = self._IO.probe.get_trace()

        #self.set_plot(6, 0, np.arange(len(trace[:,1])), trace[:,1])
        self.set_plot(6, 0, trace[:,3], trace[:,1])
        self.plotitems[6][0].setPen('#00FFFF')          #Cyan
        self.plots[6].setLabel('bottom', text="Biased")
        self.plots[6].setLabel('left', text="Current signal", units="A")

        traceb = self._IO.breakdown.get_trace()

        #self.set_plot(5, 0, trace[:,3], trace[:,1])
        self.set_plot(7, 0, traceb[:,3], traceb[:,1])#, xlim = [-200,0])
        #self.plotitems[5][0].setPen('#FFBCD9', width=2,symbol="o-")     #Cotton candy
        self.plotitems[7][0].setPen('#8FBC8F', width=2,symbol="o-")     #Dark sea green
        self.plots[7].setLabel('bottom', text="Breakdown Voltage (V)")
        self.plots[7].setLabel('left', text="Current signal", units="A")


        varname_text = ""
        value_text = ""
        values = ()

        varname_text += "GUI FPS"
        value_text += "%.1f"
        values = values + (self.benchmark.FPS,)

        varname_text += "\nLABJACK AQ FPS"
        value_text += "\n%.1f"
        values = values + (self._IO.aq_bench.FPS,)
        
        varname_text += "\nSPEC AQ FPS"
        value_text += "\n%.1f"
        values = values + (self._IO.spec_aq_bench.FPS,)
        
        varname_text += "\nNI-DAQ AQ FPS"
        value_text += "\n%.1f"
        values = values + (self._IO.langmuir_aq_bench.FPS,)
        
        varname_text += "\n"
        value_text += "\n"
        
        varname_text += "\nPressure"
        value_text += "\n%.2e Torr "
        values = values + (self._IO.pressure,)
        
        if(self._IO.pressure > self._IO.P_max*1.0e-2):
            print(self._IO.pressure,"  max  ",self._IO.P_max*1.0e-2)
            
            p = AOport('/Dev3/ao0')
            p_close = AOport2('Dev3/ao1')
            console_out("Closing mass flow controller valve")
            p.write(0)
            p_close.write(0)
            p.close()
            p_close.close()
    
        """
        varname_text += "\nI_fil setp"
        value_text += "\n%.3f A"
        values = values + (self._IO.FIL_CUR_SETP,)
        """
        varname_text += "\nI_fil"
        value_text += "\n%.3f A"
        values = values + (self._IO.FIL_CUR,)
        
        varname_text += "\nV_fil"
        value_text += "\n%.3f V"
        values = values + (self._IO.FIL_VOL,)
        """
        varname_text += "\nV_arc setp"
        value_text += "\n%.3f V"
        values = values + (self._IO.ARC_VOL_SETP,)
        """
        varname_text += "\nV_arc"
        value_text += "\n%.3f V"
        values = values + (self._IO.ARC_VOL,)
        
        varname_text += "\nI_arc"
        value_text += "\n%.3f A"
        values = values + (self._IO.ARC_CUR,)
        
        varname_text += "\nT_fil"
        value_text += "\n%0.f K"
        values = values + (self._IO.T_FIL,)
        
        self.varname_text.set(varname_text)
        self.value_text.set(value_text % values)
        
    def set_update_func(self, update_func):
        animation.FuncAnimation(self.f, update_func, interval=200)._start()

    def update_extra1(self, x, y, memory, logarithmic=False, ylim=[0,0], xlabel=""):          
        self.newdata1 = np.append(self.newdata1, [[x, y]], axis=0)    
        self.newitem1.setData(self.newdata1[:,0], self.newdata1[:,1])   
        if(not ylim==[0,0]):
            self.p2.setYRange(ylim[0], ylim[1], padding=0.05) 

    def update_extra2(self, x, y, memory, logarithmic=False, ylim=[0,0], xlabel=""):          
        self.newdata2 = np.append(self.newdata2, [[x, y]], axis=0)    
        self.newitem2.setData(self.newdata2[:,0], self.newdata2[:,1])
        if(not ylim==[0,0]):
            self.p3.setYRange(ylim[0], ylim[1], padding=0.05) 

    def update_plot(self, i, n, x, y, memory, logarithmic=False, ylim=[0,0], xlabel=""):        
        self.data[i][n] = np.append(self.data[i][n], [[x, y]], axis=0)
        if(len(self.data[i][n][:,0]) > memory):
            self.data[i][n] = self.data[i][n][1:len(self.data[i][n][:,0])-1,:]
        self.plotitems[i][n].setData(self.data[i][n])
        if(logarithmic):
            self.plots[i].setLogMode(y=True)
            self.plots[i].setYRange(np.floor(np.min(np.log10(self.data[i][n][:,1]))),np.ceil(np.max(np.log10(self.data[i][n][:,1]))), padding=0)
        elif(not ylim==[0,0]):
            self.plots[i].setYRange(ylim[0], ylim[1], padding=0.05)        

    def set_plot(self, i, n, xdata, ydata, logarithmic=False, ylim=[0,0], xlim =[0,0]):
        self.plotitems[i][n].setData(np.rot90(np.array([xdata, ydata])))
        if(logarithmic):
            self.plots[i].setLogMode(y=True)
            self.plots[i].setYRange(np.floor(np.min(np.log10(self.data[i][n][:,1]))),np.ceil(np.max(np.log10(self.data[i][n][:,1]))), padding=0)
        elif(not ylim==[0,0]):
            self.plots[i].setYRange(ylim[0], ylim[1], padding=0.05)
            
        if (not xlim==[0,0]):
            self.plots[i].setXRange(xlim[0], xlim[1], padding=0.05)    
            
    def close(self):
        self.graphwindow.close()

