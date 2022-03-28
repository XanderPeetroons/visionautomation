from misc import console_out, tick, tock, Benchmark
console_out("Importing modules")

import numpy as np
import tkinter as tk
import time
from datetime import datetime
from GUI import GUI
from IO import IO
from plotting import App
import pyqtgraph as pg
from NI_DAQ import AOport
from NI_DAQ import AOport2
import gc

import threading

#IMPORTANT MESSAGE

#CLOSE THE SHELL THAT YOU'RE NOT USING
#EVERYTHING WILL FAIL IF YOU DON'T DO IT
#DON'T FORGET
#SEARCH FOR MORE COMMENTS LIKE THIS
#SORRY

#END OF IMPORTANT MESSAGE

gc.set_threshold(5)
console_out("Initializing input/output")
_IO = IO('/dat/')
_IO.start()
_IO.I_max = 10

root = tk.Tk()
root.attributes("-topmost",True)
_GUI = GUI(root, _IO)

def FilCurr_ONOFF(counts, i0, ifinal, t):
    for i in np.arange(0, counts+1):
        if(not _IO.OC):
            curr = i0 + i*(ifinal-i0)/counts
            #print(curr,_IO.currshunt)
            iset = 'ISET ' + str(curr)
            _IO.FIL_PS.write(iset)
            time.sleep(t/counts)
        else:
            break

def FilArc_ONOFF(counts,v0,i0,vfinal,ifinal,t):
    for i in np.arange(0, counts + 1):
        if(not _IO.OC):
            vset = (v0 + i*(vfinal-v0)/counts)*(5/160)
            curr = i0 + i*(ifinal-i0)/counts
            iset = 'ISET ' + str(curr)
            _IO.FIL_PS.write(iset)
            _IO.AO_ARC.write(vset)      # writing the arc voltage
            time.sleep(t/counts)
        else:
            break
"""
def FilCurr_ONOFFtoSP(counts, i0, ifinal, t,Iprobe):
    targetI=0
    currlast=i0
    for i in np.arange(0, counts+1):
        if(not _IO.OC):
            curr = i0 + i*(ifinal-i0)/counts
            
            
            if _IO.currshunt > Iprobe and ifinal > i0:
                targetI=i
                print("first if in loop to  sp...going UP")
                curr = currlast
            if _IO.currshunt < Iprobe and ifinal < i0:
                print("2nd if in loop to  sp...going going down")
                targetI=i
                curr = currlast
            print(curr,_IO.currshunt,i," target i",targetI,"  Iprobe ",Iprobe)
            currlast=curr
            iset = 'ISET ' + str(curr)
            _IO.FIL_PS.write(iset)
            time.sleep(t/counts)
"""
def ArcVol_ONOFF(counts, v0, vfinal, t):
    for i in np.arange(0, counts + 1):
        if(not _IO.OC):
            vset = (v0 + i*(vfinal-v0)/counts)*(5/160)
            #print(vset)
            _IO.AO_ARC.write(vset) # writing the arc voltage
            time.sleep(t/counts)
        else:
            break
   


    
        
def run_shot():
    ## Starting...
    _GUI.run_button.config(state = tk.DISABLED)
    _IO.OC = False
    # TYPO
    #pressswithc=True
    #pressswitch=True
    ## Data from GUI entries
    text1 = _GUI.shottype   # Shot type
    try:
        text2 = _GUI.comment.get()  # Comments
    except:
        text2 = "No comments"
        
    T = _GUI.A.get()        # Shot duration
    Tstb = _GUI.B.get()     # Stabilization time (fil curr and gas)
    varcf = _GUI.C.get()
    varc0 = _GUI.D.get()     # Filament current setting
    ifilf = _GUI.E.get()     # Arc voltage setting
    ifil0 = _GUI.F.get()
    p0 = _GUI.P.get()
    pf = _GUI.Q.get()
    #p00 = _IO.pressure.get()
    
    if (varc0 != 0.0):
        text3 = "Ramp Voltage"
    else:
        text3 = "Constant Voltage"
        
    if (ifil0 != 0.0):
        text4 = "Ramp Current"
    else:
        text4 = "Constant Current"

    if (p0 != 0.0):
        text5 = "Ramp Pressure"
    else:
        text5 = "Constant Pressure"

    #if (ifil0 == ifilf):
    #    text4 = "Constant Current"
    #else
    #if (varc0 == varcf):
    #    text3 = "Constant Voltage"
    text = [text1, text2, text3, text4, text5]       # Saving shot and comments strings
    data = [varc0,varcf,ifil0,ifilf,0,T,0,Tstb, p0, pf]  # Saving the rest of data 

    # Preparation of ports and logs 
    p = AOport('/Dev3/ao0')     #Mass flow controller set
    p_close = AOport2('/Dev3/ao1')     #Mass flow controller 2 set
    _IO.start_log()
    t_initial=time.time()
    console_out("Logging...")
    _IO.save_spectra(back=True) #True background spectrum without fillament and gas
    console_out("Setting Fil Curr")
    _IO.FIL_PS.write('VSET 10') 
    time.sleep(2)

    # Opening valve approximation
    console_out("Opening mass flow controller valve")
    pset, mass_Flow=_IO.Press_start(p,p_close,p0,pf)
    
    # Start pressure control
    pressswitch=False
    presscontroler=threading.Thread(target=_IO.Press_control, args=(p,lambda: pressswitch,'Stable',pset,pset,mass_Flow,T), daemon=True)
    presscontroler.start()
    
    # Fill Curr ON
    if (ifil0 != 0.0):
        FilCurr_ONOFF(100, 0, ifil0, 1)
    else:    
        FilCurr_ONOFF(100, 0, ifilf, 1)

        

            
    print("Stabilization in", Tstb," seconds")
    time.sleep(Tstb) # Stabilization time

        # Start reading background spectra
    
    _IO.save_spectra(dark=True)
    console_out("Reading Background Spectra")
    #console_out("Closing mass flow controller valve")
    #p.write(0)
    # Arc Voltage ON
    console_out("Setting Arc Voltage")
    if (varc0 != 0.0):
        ArcVol_ONOFF(100, 0, varc0, 1)
    else:
        ArcVol_ONOFF(100, 0, varcf, 1)
        
    # Running shot and duration
    time.sleep(1) #To make sure that the initial voltage is reached)
    startt0= time.time()-t_initial
    _IO.start_probe()
    print("Prepare to start shot at", startt0)
    
    console_out("Start Probe")
    console_out("Running shot...")
    if (p0 != 0.0):
        pressswitch=True
        presscontroler.join()
        time.sleep(5)
        pressswitch=False
        presscontroler=threading.Thread(target=_IO.Press_control, args=(p,lambda: pressswitch,'RAMP',p0,pf,mass_Flow,T), daemon=True)
        presscontroler.start()
    if (ifil0 != 0.0):
        FilCurr_ONOFF(500, ifil0, ifilf, T)  
    elif (varc0 != 0.0):
        ArcVol_ONOFF(500, varc0, varcf, T)
    else:
        time.sleep(T)
    console_out("Finish shot ,saving data")
    #Saving data in log
    _IO.save_spectra()  
    _IO.stop_probe()
    print("Stopping the probe at", time.time()-t_initial)
    time.sleep(1) #so that the probe stops before the shot stops
    endtf=time.time()-t_initial#SIM:SET FINAL SHOT TIME
    _IO.save_time_points(startt0,endtf)
    print("Shot data finished at", endtf, ",the total shot duration was", endtf-startt0)
    console_out("Set Supplies off")
    #Fil Curr OFF
    FilCurr_ONOFF(10, ifilf, 0, 1)
    _IO.FIL_PS.write('CLR')
    
    #Arc Voltage OFF
    ArcVol_ONOFF(100, varcf, 0, 1)
    
    console_out("Stopping logging")
    _IO.stop_log()
    console_out("Closing mass flow controller valve")
    pressswitch=True
    presscontroler.join()
    p_close.write(0)
    p.write(0)
    _GUI.run_button.config(state = tk.NORMAL)
    _IO.save_setpoints(text, data)
    console_out("Done")
    
_GUI.run_shot = run_shot

def run_per_shot():
   
    # Starting... 
    _GUI.run_button2.config(state = tk.DISABLED)
    _IO.OC = False

    ## Data from GUI entries
    text1 = _GUI.shottype   # Shot type
    try:
        text2 = _GUI.comment.get()  # Comments
    except:
        text2 = "No comments"
    T = _GUI.A.get()        # Shot duration
    Tstb = _GUI.B.get()     # Stabilization time (fil curr and gas)
    varcf = _GUI.C.get()
    varc0 = _GUI.D.get()     # Filament current setting
    ifilf = _GUI.E.get()     # Arc voltage setting
    ifil0 = _GUI.F.get()
    Tper = _GUI.G.get()
    Tpw = _GUI.K.get()
    filc = _GUI.curr.get()
    volt = _GUI.volt.get()
    
    if (varc0 != 0.0):
        text3 = "Ramp Voltage"
    else:
        text3 = "Constant Voltage"
        
    if (ifil0 != 0.0):
        text4 = "Ramp Current"
    else:
        text4 = "Constant Current"
        
    text = [text1, text2, text3, text4]       # Saving shot and comments strings
    
    # Preparation of ports and logs
    p = AOport('/Dev3/ao0')     #Mass flow controller set
    p_close = AOport2('/Dev3/ao1')     #Mass flow controller 2 set
    _IO.start_log()
    console_out("Logging...")
    console_out("Starting filament current")
    _IO.FIL_PS.write('VSET 10')
    time.sleep(2)
    
    # Opening valve
    console_out("Opening mass flow controller valve")
    mass_Flow = (p0/10 - 0.2)
    mass_Step = 0.05
    p.write(mass_Flow)
                        
    _IO.mass_check_thread
    
    print("Stabilization in ", Tstb," seconds")
    time.sleep(Tstb) # Stabilization time

    # Start reading probe and background spectrum
    _IO.start_probe()
    _IO.save_spectra(dark=True)

    # Fill Curr ON
    if (ifil0 != 0.0):
        FilCurr_ONOFF(100, 0, ifil0, 1)
    else:    
        FilCurr_ONOFF(100, 0, ifilf, 1)
    
    # Arc Voltage ON
    console_out("Setting Arc Voltage")
    if (varc0 != 0.0):
        ArcVol_ONOFF(100, 0, varc0, 1)
    else:
        ArcVol_ONOFF(100, 0, varcf, 1)
   
    
    # Starting the spec shot
    console_out("Running shot..")
    t0 = time.time()

    if filc and not volt:
        di = (ifilf - ifil0)*Tpw/T
        j = 1
        vfin = varcf
        while time.time() - t0 < T:
            if(not _IO.OC):
                if  (time.time() - t0) % Tper <= Tpw:
                    if (ifil0 != 0.0):
                        ifin = ifil0 + j*di
                        i0 = ifin - di
                        #print(di, ifin, i0, Tpw)
                        FilCurr_ONOFF(100, i0, ifin, Tpw)
                        j = j + 2
                    else:
                        ifin = ifilf
                        iset = 'ISET ' + str(ifin)
                        _IO.FIL_PS.write(iset)

                else:
                    _IO.FIL_PS.write('ISET 0')
                    ifin = 0
                    
                    if (Tper-Tpw) > 15:
                        if (time.time()-t0) % Tper <= Tper - Tstb:
                            p.write(0)
                        else:
                            mass_Flow = (p0/10 - 0.2)
                            mass_Step = 0.05
                            p.write(mass_Flow)
                            
                            _IO.mass_check_thread
                    #_IO.AO_ARC.write(0)

            else:
                break
                    

                        
    elif not filc and volt:
        
        dv = (varcf -varc0)*Tpw/T                
        k = 1
        ifin = ifilf
        #first = 0
        while time.time() - t0 < T:
            if(not _IO.OC):
                if  (time.time() - t0) % Tper <= Tpw:
                    if (varc0 != 0.0):
                        vfin = varc0 + k*dv
                        v0 = vfin - dv
                        #print(dv,varc0, k, vfin, v0, Tper)
                        ArcVol_ONOFF(100, v0, vfin, Tpw)
                        k = k + 2
                    else:
                        vfin = varcf
                        _IO.AO_ARC.write(vfin*(5/160))
                        
                else:
                    vfin = 0
                    _IO.AO_ARC.write(vfin)
                    
                    if (Tper-Tpw) > 15:
                        if (time.time()-t0) % Tper <= Tper - Tstb:
                            p.write(0)
                        else:
                            mass_Flow = (p0/10 - 0.2)
                            mass_Step = 0.05
                            p.write(mass_Flow)
                            
                                
                            _IO.mass_check_thread
                    #_IO.FIL_PS.write('ISET 0')
                        
            else:
                break
                    
                
            
    elif filc and volt:
        di = (ifilf - ifil0)*Tpw/T
        dv = (varcf -varc0)*Tpw/T                
        i = 1
        while time.time() - t0 < T :
            if(not _IO.OC):
                if  (time.time() - t0) % Tper <= Tpw:
                    if (varc0 != 0.0):
                        vfin = varc0 + i*dv
                        ifin = ifil0 + i*di
                        v0 = vfin - dv
                        i0 = ifin - di
                        #print(dv,varc0, k, vfin, v0, Tper)
                        FilArc_ONOFF(100,v0,i0,vfin,ifin, Tpw)
                        i = i + 2
                    else:
                        vfin = varcf
                        _IO.AO_ARC.write(vfin*(5/160))                            
                        ifin = ifilf
                        iset = 'ISET ' + str(ifin)
                        _IO.FIL_PS.write(iset)
                    
                else:
                    vfin = 0
                    _IO.AO_ARC.write(vfin)
                    ifin = 0
                    _IO.FIL_PS.write('ISET 0')

                    if (Tper-Tpw) > 15:
                        if (time.time()-t0) % Tper <= Tper - Tstb:
                            p.write(0)
                        else:
                            mass_Flow = (p0/10 - 0.2)
                            mass_Step = 0.05
                            p.write(mass_Flow)
                            
                                
                            _IO.mass_check_thread
                    
    else:
        console_out("Select at least one option or try a simple shot")
        ifin = 0
        vfin = 0

        
    ## Only for Tijs Experiment                
    #FilCurr_ONOFF(100, ifilf, 0, 1)
    #time.sleep(280)
                     
    # Saving data in log

    
    data = [varc0,varcf,ifil0,ifilf,0,T,Tper,Tstb]
    _IO.save_setpoints(text, data)
    _IO.save_spectra()
    _IO.stop_probe()
            
    # Fil Curr OFF
    FilCurr_ONOFF(10, ifin, 0, 1) 
    _IO.FIL_PS.write('CLR')
    
    # Arc Vol OFF
    ArcVol_ONOFF(10,vfin,0,1)
    
    console_out("Stopping logging")    
    _IO.stop_log()
    console_out("Closing mass flow controller valve")
    p.write(0)
    console_out("Done")

    _GUI.run_button2.config(state = tk.NORMAL)
    
_GUI.run_per_shot = run_per_shot


def run_act_shot():
       
    ## Starting...
    _GUI.run_button3.config(state = tk.DISABLED)
    _IO.OC = False

    ## Data from GUI entries
    text1 = _GUI.shottype   # Shot type
    try:
        text2 = _GUI.comment.get()  # Comments
    except:
        text2 = "No comments"
        
    T = _GUI.A.get()        # Shot duration
    Tstb = _GUI.B.get()     # Stabilization time (fil curr and gas)
    varcmax = _GUI.H.get()
    varc0 = _GUI.D.get()    # Arc voltage setting 
    ifilmax = _GUI.I.get()    # Filament current setting
    ifil0 = _GUI.F.get()     
    iprob = _GUI.J.get()    # Prob current in mA
    
    if (varcmax != 0.0):
        text3 = "Active Voltage"
    else:
        text3 = "Constant Voltage"
    
    if (ifilmax != 0.0):
        text4 = "Active Current"
    else:
        text4 = "Constant Current"
        
    text = [text1, text2, text3, text4]       # Saving shot and comments strings  

    # Preparation of ports and logs 
    p = AOport('/Dev3/ao0')     #Mass flow controller set
    p_close = AOport2('/Dev3/ao1')     #Mass flow controller 2 set
    _IO.start_log()
    console_out("Logging...")
    console_out("Setting Fil Curr")
    _IO.FIL_PS.write('VSET 10') 
    time.sleep(2)
    # Fill Curr ON
    FilCurr_ONOFF(100, 0, ifil0, 3)

    # Opening valve
    console_out("Opening mass flow controller valve")
    mass_Flow = (p0/10 - 0.2)
    mass_Step = 0.05
    p.write(mass_Flow)
    #GONZALO: RAMP UP (DONT USE)
    #while(_IO.pressure < 0.001*p0):
        #time.sleep(1)
        #mass_Flow = mass_Flow + 5*mass_Step
        #p.write(mass_Flow)
    
    
    _IO.mass_check_thread
    print("Stabilization in", Tstb," seconds")
    time.sleep(Tstb) # Stabilization time


    # Start reading probe and background spectra
    _IO.start_probe()
    _IO.save_spectra(dark=True)

    # Arc Voltage ON
    console_out("Setting Arc Voltage")
    
    if varcmax != 0 :
        vfinal = varc0
        counts = 100
        t = 3
        i = 0
        while (_IO.currshunt < iprob and i < counts):
            if(not _IO.OC):
                i = i+1
                vset = (i*vfinal/counts)
                _IO.AO_ARC.write(vset*(5/160)) # writing the arc voltage
                time.sleep(t/counts)
            else:
                break
        
        # Running shot
        console_out("Running shot...")
        varci = vset
        varcf = vset
        time0 = time.time()
        Tol = 0.01
        
        while (time.time() - time0 < T and varcf < varcmax and not _IO.OC):
            if (iprob - _IO.currshunt < - Tol):  # mA both
                varcf = round(0.999*varci,3)            
                ArcVol_ONOFF(1, varci, varcf, 0.01)
                varci = varcf
            elif (iprob - _IO.currshunt > Tol):
                varcf = round(1.001*varci,3)
                ArcVol_ONOFF(1, varci, varcf, 0.01)
                varci = varcf
            else:
                pass

    if ifilmax != 0: 
        ArcVol_ONOFF(100,0,varc0,2)
        time.sleep(2)
        """
        i0 = ifil0
        if(not _IO.OC):
            if _IO.currshunt > iprob:
                ifinal = 0.999*ifil0
                FilCurr_ONOFF(5, i0, ifinal, 1)
                i0 = ifinal
            else:
                ifinal = 1.001*ifil0
                FilCurr_ONOFF(5, i0, ifinal, 1)
                i0 = ifinal
                
        time.sleep(5)
        # Running shot
        console_out("Running shot...")
        try:
            i0 = ifinal
            ifilf = ifinal
        except:
            i0 = ifil0
            ifilf = ifil0
        """
        i0 = ifil0
        ifilf = ifil0
        time0 = time.time()
        Tol = 0.01
        delI = 0
        dip = 0
        n = 0
        ifilp = 0
        while (time.time() - time0 < T and ifilf < ifilmax  and not _IO.OC):
            print(" Time ",time.time() - time0,ifilf," target ",_IO.currshunt, " delta curr ", dip, " Del I ", delI)
            time.sleep(0.25)
            dip = iprob - _IO.currshunt
            #delI = 0
            """
            if ( dip < - Tol or dip > Tol ):  # mA both
                delI = np.log(iprob/_IO.currshunt)*5.7      #Logaritmic increased
                #delI = np.log(iprob/_IO.currshunt)*.0762+1      #Logaritmic increased
                ifilf = round(ifilf + delI,4) #round(delI*i0,3)
                if ifilf >= ifilmax:
                    ifilf = ifilmax-1
                    #ifilf = round(0.9999*i0,4)
                    #iset = 'ISET ' + str(ifilf)
                    #_IO.FIL_PS.write(iset)
                FilCurr_ONOFFtoSP(10, i0, ifilf, 0.05,iprob)
                i0 = ifilf
                time.sleep(0.1)
            else:
                pass
            """

            
            if dip < - Tol:
                delI=-50e-3
            elif dip > Tol:
                delI=25e-3    
            else:
                ifilp += ifilf
                n += 1
                delI = 0
            ifilf = round(ifilf + delI,4)
            FilCurr_ONOFF(2, i0, ifilf, 0.01)
            i0 = ifilf
            """
            elif (iprob - _IO.currshunt > Tol):
            delI =np.log(iprob/_IO.currshunt)*.2+1
            ifilf = round(delI*ifil0,3)
            #ifilf = round(1.0001*i0,4)            
            FilCurr_ONOFF(2, i0, ifilf, 0.01)
            i0 = ifilf
            """
            
    #Saving data in log
    if varcmax != 0:
        data = [varc0,varcf,0,ifil0,iprob,T,0,Tstb]  # Saving the rest of data
    if ifilmax != 0:
        data = [0,varc0,ifil0,ifilp/n,iprob,T,0,Tstb]  # Saving the rest of data
    _IO.save_setpoints(text, data)
    _IO.save_spectra()  
    _IO.stop_probe()
    
    #Fil Curr OFF
    try:
        FilCurr_ONOFF(10, ifilf, 0, 1)
    except:
        FilCurr_ONOFF(10, ifil0, 0, 1)
    _IO.FIL_PS.write('CLR')
    
    #Arc Voltage OFF
    try:
        ArcVol_ONOFF(100, varcf, 0, 1)
    except:
        ArcVol_ONOFF(100, varc0, 0, 1)
    console_out("Stopping logging")
    _IO.stop_log()
    console_out("Closing mass flow controller valve")
    p.write(0)
    console_out("Done")
    _GUI.run_button3.config(state = tk.NORMAL)
    
_GUI.run_act_shot = run_act_shot


def background_func():
    
    _GUI.update()

    root.update_idletasks()
        
    if(_IO.IO_OK):
        root.after(10, background_func)

def on_close():
    console_out("Closing")
    
    try:    
        p = AOport('/Dev3/ao0')
        p_close = AOport2('/Dev3/ao1')     #Mass flow controller 2 set
        p_close.write(0)
        p.write(0)
    except:
        pass
    _IO.reset()
    _IO.close()
    _GUI.close()
    root.destroy()

    import sys
    sys.exit()

    
_GUI.set_on_close(on_close)


def stop():
    console_out("Supplies OFF")
    _IO.reset()
    try:
        p_close.write(0)
        p.write(0)
        console_out("Closing mass flow controller valve")
    except:
        pass
    console_out("Stopping log")
    _IO.stop_log()
    _IO.stop_probe()
    console_out("Deleting file")
    _IO.del_logs()
    console_out("Stopping shot")

_GUI.stop = stop

    
_GUI.stop_operation(stop)


_IO.reset()
while(not _IO.IO_OK):
    pass

root.protocol('WM_DELETE_WINDOW', on_close)
root.after(0, background_func)

console_out("Starting GUI")
root.mainloop()
