#    Digital Twin - Geneva Motorway (DT-GM) in SUMO
#    Author: Krešimir Kušić

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>



import os, sys
import xml.etree.ElementTree as ET
import traci
import traci.constants as tc
import shlex, subprocess
import random
import numpy as np
import matplotlib.pyplot as plt
import itertools
from numpy import savetxt
import matplotlib.pyplot as plt
from xml.dom import minidom as mini
import time
import math
import datetime as dt
import pandas as pd
import functions_DT_GE_live24h as fn
import pyodbc

#======= SUMO environment and path to the model and associated files
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
#     print(tools)
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

sumoBinary = "C:/Program Files (x86)/Eclipse/Sumo/bin/sumo-gui" #sumo-gui.exe

root = "C:/Users/kkusic/Desktop/DT-GM/SCENARIO-I/"
path_data = root+"Results/"

sumoCmd = [sumoBinary, "-c",\
           root+"DT_GM_live24h.sumocfg", "--seed", str(28815),\
                "--start", "1", "--quit-on-end", "1"]



#=============== Run simulation    
hours = 24
run = 0
num_simplex_runs = 300
res_time = 1

TTS = 0

# for routers
C = 2400 # sec to wait and than remove old vehicles from 'perm_obj_dist' list (routing control)
oldVehIDs_E_NS6 = []
oldVehIDs_ES_N6 = []
oldVehIDs_N_ES148 = []
oldVehIDs_N_ES158 = []
oldVehIDs_EN_S1 = []
oldVehIDs_S_NE12 = []
vehIDs_all = []


perm_r_dist1 = [[[],[],[0]]]
perm_r_dist2 = [[[],[],[0]]]
perm_r_dist3 = [[[],[],[0]]]
perm_r_dist4 = [[[],[],[0]]]
perm_r_dist5 = [[[],[],[0]]]
perm_r_dist6 = [[[],[],[0]]]
# temp_obj_dist = []

X_0224_01 = [0,0,0,0]
X_0224_02 = [0,0,0,0]
X_0224_01_old = [0,0,0,0]
X_0224_02_old = [0,0,0,0]
X_0224_03 = [0,0,0,0]
X_0224_04 = [0,0,0,0]
X_0224_03_old = [0,0,0,0]
X_0224_04_old = [0,0,0,0]


X_0200_01 = [0,0,0,0]
X_0200_02 = [0,0,0,0]
X_0200_03 = [0,0,0,0]
X_0200_01_old = [0,0,0,0]
X_0200_02_old = [0,0,0,0]
X_0200_03_old = [0,0,0,0]
X_0200_04 = [0,0,0,0]
X_0200_05 = [0,0,0,0]
X_0200_06 = [0,0,0,0]
X_0200_04_old = [0,0,0,0]
X_0200_05_old = [0,0,0,0]
X_0200_06_old = [0,0,0,0]


X_0272_03 = [0,0,0,0]
X_0272_04 = [0,0,0,0]
X_0272_03_old = [0,0,0,0]
X_0272_04_old = [0,0,0,0]
X_0272_01 = [0,0,0,0]
X_0272_02 = [0,0,0,0]
X_0272_01_old = [0,0,0,0]
X_0272_02_old = [0,0,0,0]

oldVehIDs_E_in = []
oldVehIDs_N_in = []
oldVehIDs_S_in = []
oldVehIDs_on_ramp_x12_N = []
oldVehIDs_on_ramp_x11_S = []
oldVehIDs_on_ramp_x15_E = []
oldVehIDs_on_ramp_x16_N = []
oldVehIDs_off_ramp_x13_S = []
oldVehIDs_off_ramp_x9_N = []
oldVehIDs_out_E = []
oldVehIDs_out_N = []
oldVehIDs_out_S = []


save_data_time = ''

step_length=0.25  # sim. step length tested for one of this values (0.1, 0.2, 0.25, 0.5). Must be equal to step length specified in .sumocfg file 


# Change the name of your SERVER in SERVER=KKUSIC-L\SQLEXPRESS (see your database), and UID=FPZ\kkusic (used by SQL authentication)
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=KKUSIC-L\SQLEXPRESS;DATABASE=SWISS_traffic_data;UID=FPZ\kkusic;TRUSTED_CONNECTION=yes')
time.sleep(0.1)

#The data from the last minute is always published 20 seconds after a full minute in UTC 0.
t_target=20
if dt.datetime.now().second>15:
    time.sleep((60-dt.datetime.now().second)+t_target)
elif dt.datetime.now().second<25:
    time.sleep(t_target-dt.datetime.now().second)

traci.start(sumoCmd)

t_target=25
time.sleep(t_target-dt.datetime.now().second)

period_check_sim_speed = 10 #[s] periodically check the simulation speed execution each X seconds to see if we need to adjust the speed to synchronized simulation time 
                            #with actual traffic data timestamp from traffic counters (by time.sleep(X))
sql_key = 1
#start_time_correction = 0
#delta_time_correction = 0
time_sleep = step_length    # it should be equal to simulation step length

while(run<hours):

    #traci.start(sumoCmd)
    
    
    error_flow_E = error_flow_N = error_flow_S = 0

    controlFile = np.zeros((1,25))
    # ==== FLOW IN
    # main sections
    flow_E_min_in = 0
    speedSum_E_min_in = 0 
    flow_N_min_in = 0
    speedSum_N_min_in = 0 
    flow_S_min_in = 0
    speedSum_S_min_in = 0
    # entry ramps
    flow_on_ramp_x12_N = 0
    flow_on_ramp_x12_N_min = 0
    speedSum_on_ramp_x12_N = 0
    flow_on_ramp_x11_S = 0
    flow_on_ramp_x11_S_min = 0
    speedSum_on_ramp_x11_S = 0
    flow_on_ramp_x15_E = 0
    flow_on_ramp_x15_E_min = 0
    speedSum_on_ramp_x15_E = 0
    flow_on_ramp_x16_N = 0
    flow_on_ramp_x16_N_min = 0
    speedSum_on_ramp_x16_N = 0

    # ==== FLOW OUT
    # main sections
    flow_E_min = 0
    speedSum_E_min = 0 
    flow_N_min = 0
    speedSum_N_min = 0
    flow_S_min = 0
    speedSum_S_min = 0 
    # exit ramps
    flow_off_ramp_x13_S = 0
    flow_off_ramp_x13_S_min = 0
    speedSum_off_ramp_x13_S = 0
    flow_off_ramp_x9_N = 0
    flow_off_ramp_x9_N_min = 0
    speedSum_off_ramp_x9_N = 0


    step = 0

    while(step <= hours*3600*(1/step_length)):    # since step_length is shortened to 0.25 (default 1 sec)
        traci.simulationStep()
        
        if step%(res_time*(1/step_length))==0:

            #=======================
            # FLOW IN (measurements from SUMO)
            flow_E_in, speed_E_in, oldVehIDs_E_in, newVehIDs_E_in =\
            fn.edgeVehParameters('E_NS5', 'E_NS6', oldVehIDs_E_in)
            flow_E_min_in = flow_E_min_in + flow_E_in
            speedSum_E_min_in = speedSum_E_min_in + speed_E_in

            flow_N_in, speed_N_in, oldVehIDs_N_in, newVehIDs_N_in =\
            fn.edgeVehParameters('N_ES148', 'N_ES149', oldVehIDs_N_in)
            flow_N_min_in = flow_N_min_in + flow_N_in
            speedSum_N_min_in = speedSum_N_min_in + speed_N_in

            flow_S_in, speed_S_in, oldVehIDs_S_in, newVehIDs_S_in =\
            fn.edgeVehParameters('S_NE12', 'S_NE13', oldVehIDs_S_in)
            flow_S_min_in = flow_S_min_in + flow_S_in
            speedSum_S_min_in = speedSum_S_min_in + speed_S_in
            
            # on_ramp_x12_N
            flow_on_ramp_x12_N, speed_on_ramp_x12_N, oldVehIDs_on_ramp_x12_N, newVehIDs_on_ramp_x12_N =\
            fn.edgeVehParameters('ES_N56_onramp1.90', 'ES_N57_onramp1', oldVehIDs_on_ramp_x12_N)
            flow_on_ramp_x12_N_min = flow_on_ramp_x12_N_min + flow_on_ramp_x12_N
            speedSum_on_ramp_x12_N = speedSum_on_ramp_x12_N + speed_on_ramp_x12_N
            
            # on_ramp_x11_S
            flow_on_ramp_x11_S, speed_on_ramp_x11_S, oldVehIDs_on_ramp_x11_S, newVehIDs_on_ramp_x11_S =\
            fn.edgeVehParameters('N_ES152_onramp1.89', 'N_ES152_onramp1.762', oldVehIDs_on_ramp_x11_S)
            flow_on_ramp_x11_S_min = flow_on_ramp_x11_S_min + flow_on_ramp_x11_S
            speedSum_on_ramp_x11_S = speedSum_on_ramp_x11_S + speed_on_ramp_x11_S
            
            # on_ramp_x15_E
            flow_on_ramp_x15_E, speed_on_ramp_x15_E, oldVehIDs_on_ramp_x15_E, newVehIDs_on_ramp_x15_E =\
            fn.edgeVehParameters('E11.196', 'E7', oldVehIDs_on_ramp_x15_E)
            flow_on_ramp_x15_E_min = flow_on_ramp_x15_E_min + flow_on_ramp_x15_E
            speedSum_on_ramp_x15_E = speedSum_on_ramp_x15_E + speed_on_ramp_x15_E
            
            # on_ramp_x16_N
            flow_on_ramp_x16_N, speed_on_ramp_x16_N, oldVehIDs_on_ramp_x16_N, newVehIDs_on_ramp_x16_N =\
            fn.edgeVehParameters('E10.25', 'E10.138', oldVehIDs_on_ramp_x16_N)
            flow_on_ramp_x16_N_min = flow_on_ramp_x16_N_min + flow_on_ramp_x16_N
            speedSum_on_ramp_x16_N = speedSum_on_ramp_x16_N + speed_on_ramp_x16_N

            #================================
            # FLOW OUT (measurements from SUMO)
            flow_E, speed_E, oldVehIDs_out_E, newVehIDs_out_E =\
            fn.edgeVehParameters('SN_E5', 'SN_E6', oldVehIDs_out_E)
            flow_E_min = flow_E_min + flow_E
            speedSum_E_min = speedSum_E_min + speed_E

            flow_N, speed_N, oldVehIDs_out_N, newVehIDs_out_N =\
            fn.edgeVehParameters('ES_N17', 'ES_N18', oldVehIDs_out_N)
            flow_N_min = flow_N_min + flow_N
            speedSum_N_min = speedSum_N_min + speed_N

            flow_S, speed_S, oldVehIDs_out_S, newVehIDs_out_S =\
            fn.edgeVehParameters('EN_S2', 'EN_S3', oldVehIDs_out_S)
            flow_S_min = flow_S_min + flow_S
            speedSum_S_min = speedSum_S_min + speed_S
            
            flow_off_ramp_x13_S, speed_off_ramp_x13_S, oldVehIDs_off_ramp_x13_S, newVehIDs_off_ramp_x13_S =\
            fn.edgeVehParameters('N_ES151_offramp1', 'N_ES151_offramp1.431', oldVehIDs_off_ramp_x13_S)
            flow_off_ramp_x13_S_min = flow_off_ramp_x13_S_min + flow_off_ramp_x13_S
            speedSum_off_ramp_x13_S = speedSum_off_ramp_x13_S + speed_off_ramp_x13_S
            
            flow_off_ramp_x9_N, speed_off_ramp_x9_N, oldVehIDs_off_ramp_x9_N, newVehIDs_off_ramp_x9_N =\
            fn.edgeVehParameters('ES_N11_offramp1', 'ES_N11_offramp1.206', oldVehIDs_off_ramp_x9_N)
            flow_off_ramp_x9_N_min = flow_off_ramp_x9_N_min + flow_off_ramp_x9_N
            speedSum_off_ramp_x9_N = speedSum_off_ramp_x9_N + speed_off_ramp_x9_N

        #===== Specify query for SQL
        if sql_key == 1 and dt.datetime.now().second==25:
            sql_key = 0 # since sim. 4 steps = 1 [s], so to prevent multiple executions during 25 [s] (one is enough)

            current_utc = dt.datetime.utcnow()
            current_time = (current_utc-dt.timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M')
            current_time_sec = (current_utc-dt.timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
            if step == 0:
                t0 = time.time()
                t_corr_iter = 1
            # Inputs    
            select_record_ID_0224_01 ="""SELECT CarFlow, CarSpeed, TruckFlow, TruckSpeed FROM tblDetectors WHERE TimeStampUTC = '"""+current_time+"""' and DetectorID = 'CH:0224.01'"""
            select_record_ID_0224_02 ="""SELECT CarFlow, CarSpeed, TruckFlow, TruckSpeed FROM tblDetectors WHERE TimeStampUTC = '"""+current_time+"""' and DetectorID = 'CH:0224.02'"""
            # Outputs
            select_record_ID_0224_03 ="""SELECT CarFlow, CarSpeed, TruckFlow, TruckSpeed FROM tblDetectors WHERE TimeStampUTC = '"""+current_time+"""' and DetectorID = 'CH:0224.03'"""
            select_record_ID_0224_04 ="""SELECT CarFlow, CarSpeed, TruckFlow, TruckSpeed FROM tblDetectors WHERE TimeStampUTC = '"""+current_time+"""' and DetectorID = 'CH:0224.04'"""            

            # Inputs
            select_record_ID_0200_01 ="""SELECT CarFlow, CarSpeed, TruckFlow, TruckSpeed FROM tblDetectors WHERE TimeStampUTC = '"""+current_time+"""' and DetectorID = 'CH:0200.01'"""
            select_record_ID_0200_02 ="""SELECT CarFlow, CarSpeed, TruckFlow, TruckSpeed FROM tblDetectors WHERE TimeStampUTC = '"""+current_time+"""' and DetectorID = 'CH:0200.02'"""
            select_record_ID_0200_03 ="""SELECT CarFlow, CarSpeed, TruckFlow, TruckSpeed FROM tblDetectors WHERE TimeStampUTC = '"""+current_time+"""' and DetectorID = 'CH:0200.03'"""    
            # Outputs
            select_record_ID_0200_04 ="""SELECT CarFlow, CarSpeed, TruckFlow, TruckSpeed FROM tblDetectors WHERE TimeStampUTC = '"""+current_time+"""' and DetectorID = 'CH:0200.04'"""
            select_record_ID_0200_05 ="""SELECT CarFlow, CarSpeed, TruckFlow, TruckSpeed FROM tblDetectors WHERE TimeStampUTC = '"""+current_time+"""' and DetectorID = 'CH:0200.05'"""
            select_record_ID_0200_06 ="""SELECT CarFlow, CarSpeed, TruckFlow, TruckSpeed FROM tblDetectors WHERE TimeStampUTC = '"""+current_time+"""' and DetectorID = 'CH:0200.06'"""    

            # Inputs
            select_record_ID_0272_03 ="""SELECT CarFlow, CarSpeed, TruckFlow, TruckSpeed FROM tblDetectors WHERE TimeStampUTC = '"""+current_time+"""' and DetectorID = 'CH:0272.03'"""
            select_record_ID_0272_04 ="""SELECT CarFlow, CarSpeed, TruckFlow, TruckSpeed FROM tblDetectors WHERE TimeStampUTC = '"""+current_time+"""' and DetectorID = 'CH:0272.04'"""

            # Outputs
            select_record_ID_0272_01 ="""SELECT CarFlow, CarSpeed, TruckFlow, TruckSpeed FROM tblDetectors WHERE TimeStampUTC = '"""+current_time+"""' and DetectorID = 'CH:0272.01'"""
            select_record_ID_0272_02 ="""SELECT CarFlow, CarSpeed, TruckFlow, TruckSpeed FROM tblDetectors WHERE TimeStampUTC = '"""+current_time+"""' and DetectorID = 'CH:0272.02'"""            
        elif sql_key == 0 and dt.datetime.now().second >= 26:
            sql_key = 1        

#=== CHECKPOINT (simple) of simulation speed execution in order to speed up or slow down to not miss the right time slot of requesting the new data
# in sequential (minute-by-minute) during the 25 [s] of each minute
        if step%(period_check_sim_speed*(1/step_length))==0 and step>0:
            t_control = t0 + period_check_sim_speed*(t_corr_iter)        
            #print('t_control',t_control)
            time_now = time.time()
            #print('time_now',time_now)
            delta_time_corr = time_now - t_control 
            time_sleep = (period_check_sim_speed - delta_time_corr)/(period_check_sim_speed/step_length)
            if time_sleep<0:
                time_sleep = 0            
            t_corr_iter+=1
	
#=== CHECKPOINT End                
            
        if step%(60*(1/step_length))==0:
            
            # store locally (in pandas dataframe) simulation data recorded during the last minute 
            if step>0:
                q1=X_0224_03[0]+X_0224_03[2]+X_0224_04[0]+X_0224_04[2]
                q3=X_0272_01[0]+X_0272_01[2]+X_0272_02[0]+X_0272_02[2]
                q5=X_0200_04[0]+X_0200_04[2]+X_0200_05[0]+X_0200_05[2]+X_0200_06[0]+X_0200_06[2]
                q2=X_0224_01[0]+X_0224_01[2]+X_0224_02[0]+X_0224_02[2]
                #===== ok here are detectors named in reversed order (q4 - North in) 'same for q3 (North-out)'
                q4=X_0272_03[0]+X_0272_03[2]+X_0272_04[0]+X_0272_04[2]
                #=====
                q6=X_0200_01[0]+X_0200_01[2]+X_0200_02[0]+X_0200_02[2]+X_0200_03[0]+X_0200_03[2]



                v = [X_0224_01[1],X_0224_01[3],X_0224_02[1],X_0224_02[3]]
                x =0.001 + sum(x > 0 for x in v)
                v_E_ref_in = (X_0224_01[1]+X_0224_01[3]+X_0224_02[1]+X_0224_02[3])/x

                v = [X_0272_03[1], X_0272_03[3], X_0272_04[1], X_0272_04[3]]
                x =0.001 + sum(x > 0 for x in v)
                v_N_ref_in = (X_0272_03[1]+X_0272_03[3]+X_0272_04[1]+X_0272_04[3])/x

                v = [X_0200_01[1], X_0200_01[3], X_0200_02[1], X_0200_02[3], X_0200_03[1], X_0200_03[3]]
                x =0.001 + sum(x > 0 for x in v)
                v_S_ref_in = (X_0200_01[1]+X_0200_01[3]+X_0200_02[1]+X_0200_02[3]+X_0200_03[1]+X_0200_03[3])/x

                v = [X_0224_03[1], X_0224_03[3], X_0224_04[1], X_0224_04[3]]
                x =0.001 + sum(x > 0 for x in v)
                v_E_ref = (X_0224_03[1]+X_0224_03[3]+X_0224_04[1]+X_0224_04[3])/x

                v = [X_0272_01[1], X_0272_01[3], X_0272_02[1], X_0272_02[3]]
                x =0.001 + sum(x > 0 for x in v)
                v_N_ref = (X_0272_01[1]+X_0272_01[3]+X_0272_02[1]+X_0272_02[3])/x

                v = [X_0200_04[1], X_0200_04[3], X_0200_05[1], X_0200_05[3], X_0200_06[1], X_0200_06[3]]
                x =0.001 + sum(x > 0 for x in v)
                v_S_ref = (X_0200_04[1]+X_0200_04[3]+X_0200_05[1]+X_0200_05[3]+X_0200_06[1]+X_0200_06[3])/x

                controlFile = np.vstack([controlFile,[q2, flow_E_min_in*60,\
                                                      q4, flow_N_min_in*60,\
                                                      q6, flow_S_min_in*60,\
                                                      q1, flow_E_min*60,\
                                                      q3, flow_N_min*60,\
                                                      q5, flow_S_min*60,\
                                                      round(TTS),\
                                                      x12, flow_on_ramp_x12_N_min*60,\
                                                      x11, flow_on_ramp_x11_S_min*60,\
                                                      x15, flow_on_ramp_x15_E_min*60,\
                                                      x16, flow_on_ramp_x16_N_min*60,\
                                                      Xcomplete[12][0], flow_off_ramp_x13_S_min*60,\
                                                      Xcomplete[8][0], flow_off_ramp_x9_N_min*60]])

                
                flow_E_min_in = 0
                speedSum_E_min_in = 0
                flow_N_min_in = 0
                speedSum_N_min_in = 0
                flow_S_min_in = 0
                speedSum_S_min_in = 0
                flow_E_min = 0
                speedSum_E_min = 0
                flow_N_min = 0
                speedSum_N_min = 0
                flow_S_min = 0
                speedSum_S_min = 0
                
                flow_on_ramp_x12_N_min = 0
                speedSum_on_ramp_x12_N = 0
                flow_on_ramp_x11_S_min = 0
                speedSum_on_ramp_x11_S = 0
                flow_on_ramp_x15_E_min = 0
                speedSum_on_ramp_x15_E = 0
                flow_on_ramp_x16_N_min = 0
                speedSum_on_ramp_x16_N = 0                
                flow_off_ramp_x13_S_min = 0
                speedSum_off_ramp_x13_S = 0
                flow_off_ramp_x9_N_min = 0
                speedSum_off_ramp_x9_N = 0
                

#============ pull actual traffic data from SQL database (real-time: Traffic Counters (FEDRO) <-> ODPMS data platform <-> Python <-> SQL <-> Python <-> TraCI <-> SUMO)
#   X_0224 - eastbound
#   X_0272 - northbound
#   X_0200 - southbound
            
            cursor = conn.cursor()
            cursor.execute(select_record_ID_0224_01)
            for row in cursor:
                #print(row)
                X_0224_01[0]=row[0]
                X_0224_01[1]=row[1]
                X_0224_01[2]=row[2]
                X_0224_01[3]=row[3]
            X_0224_01_old=X_0224_01

            cursor = conn.cursor()
            cursor.execute(select_record_ID_0224_02)              
            for row in cursor:
                #print(row)
                X_0224_02[0]=row[0]
                X_0224_02[1]=row[1]
                X_0224_02[2]=row[2]
                X_0224_02[3]=row[3]
            X_0224_02_old=X_0224_02

            cursor = conn.cursor()
            cursor.execute(select_record_ID_0224_03)
            for row in cursor:
                #print(row)
                X_0224_03[0]=row[0]
                X_0224_03[1]=row[1]
                X_0224_03[2]=row[2]
                X_0224_03[3]=row[3]
            X_0224_03_old=X_0224_03

            cursor = conn.cursor()
            cursor.execute(select_record_ID_0224_04)              
            for row in cursor:
                #print(row)
                X_0224_04[0]=row[0]
                X_0224_04[1]=row[1]
                X_0224_04[2]=row[2]
                X_0224_04[3]=row[3]
            X_0224_04_old=X_0224_04


#==========================================================
            cursor = conn.cursor()
            cursor.execute(select_record_ID_0200_01)
            for row in cursor:
                #print(row)
                X_0200_01[0]=row[0] # Flow cars
                X_0200_01[1]=row[1] # Speed cars
                X_0200_01[2]=row[2] # Flow trucks
                X_0200_01[3]=row[3] # Speed Trucks
            X_0200_01_old=X_0200_01

            cursor = conn.cursor()
            cursor.execute(select_record_ID_0200_02)              
            for row in cursor:
                #print(row)
                X_0200_02[0]=row[0]
                X_0200_02[1]=row[1]
                X_0200_02[2]=row[2]
                X_0200_02[3]=row[3]
            X_0200_02_old=X_0200_02

            cursor = conn.cursor()
            cursor.execute(select_record_ID_0200_03)              
            for row in cursor:
                #print(row)
                X_0200_03[0]=row[0]
                X_0200_03[1]=row[1]
                X_0200_03[2]=row[2]
                X_0200_03[3]=row[3]
            X_0200_03_old=X_0200_03

            cursor = conn.cursor()
            cursor.execute(select_record_ID_0200_04)
            for row in cursor:
                #print(row)
                X_0200_04[0]=row[0] # Flow cars
                X_0200_04[1]=row[1] # Speed cars
                X_0200_04[2]=row[2] # Flow trucks
                X_0200_04[3]=row[3] # Speed Trucks
            X_0200_04_old=X_0200_04

            cursor = conn.cursor()
            cursor.execute(select_record_ID_0200_05)              
            for row in cursor:
                #print(row)
                X_0200_05[0]=row[0]
                X_0200_05[1]=row[1]
                X_0200_05[2]=row[2]
                X_0200_05[3]=row[3]
            X_0200_05_old=X_0200_05

            cursor = conn.cursor()
            cursor.execute(select_record_ID_0200_06)              
            for row in cursor:
                #print(row)
                X_0200_06[0]=row[0]
                X_0200_06[1]=row[1]
                X_0200_06[2]=row[2]
                X_0200_06[3]=row[3]
            X_0200_06_old=X_0200_06

#====================================================================================
            cursor = conn.cursor()
            cursor.execute(select_record_ID_0272_03)
            for row in cursor:
                #print(row)
                X_0272_03[0]=row[0]
                X_0272_03[1]=row[1]
                X_0272_03[2]=row[2]
                X_0272_03[3]=row[3]
            X_0272_03_old=X_0272_03

            cursor = conn.cursor()
            cursor.execute(select_record_ID_0272_04)
            for row in cursor:
                #print(row)
                X_0272_04[0]=row[0]
                X_0272_04[1]=row[1]
                X_0272_04[2]=row[2]
                X_0272_04[3]=row[3]
            X_0272_04_old=X_0272_04

            cursor = conn.cursor()
            cursor.execute(select_record_ID_0272_01)
            for row in cursor:
                #print(row)
                X_0272_01[0]=row[0]
                X_0272_01[1]=row[1]
                X_0272_01[2]=row[2]
                X_0272_01[3]=row[3]
            X_0272_01_old=X_0272_01

            cursor = conn.cursor()
            cursor.execute(select_record_ID_0272_02)
            for row in cursor:
                #print(row)
                X_0272_02[0]=row[0]
                X_0272_02[1]=row[1]
                X_0272_02[2]=row[2]
                X_0272_02[3]=row[3]
            X_0272_02_old=X_0272_02

#===============================


            q1=X_0224_03[0]+X_0224_03[2]+X_0224_04[0]+X_0224_04[2]
            q3=X_0272_01[0]+X_0272_01[2]+X_0272_02[0]+X_0272_02[2]
            q5=X_0200_04[0]+X_0200_04[2]+X_0200_05[0]+X_0200_05[2]+X_0200_06[0]+X_0200_06[2]

            q2=X_0224_01[0]+X_0224_01[2]+X_0224_02[0]+X_0224_02[2]
            q4=X_0272_03[0]+X_0272_03[2]+X_0272_04[0]+X_0272_04[2]
            q6=X_0200_01[0]+X_0200_01[2]+X_0200_02[0]+X_0200_02[2]+X_0200_03[0]+X_0200_03[2]


		
# Level of traffic intensities (desired values) for free variables in the flow model. This module is currently developing in order to be self-adjustable.				
            if run == 6 or run == 7:# represents hours of the day
                target_idx_x6 = 9 # traffic intensity (1-10 levels), based on it Simplex will produce a feasible solution that satisfies (Xcomplete) all flows in the network
                target_idx_x11 = 0
                target_idx_x12 = 1 
                target_idx_x14 = 6 
                target_idx_x15 = 2 
                target_idx_x16 = 0
            elif run == 8 or run == 9:
                target_idx_x6 = 9 
                target_idx_x11 = 0
                target_idx_x12 = 1 
                target_idx_x14 = 3 
                target_idx_x15 = 2 
                target_idx_x16 = 0 
            elif run == 10 or run == 11:
                target_idx_x6 = 9 
                target_idx_x11 = 1
                target_idx_x12 = 1 
                target_idx_x14 = 4 
                target_idx_x15 = 1 
                target_idx_x16 = 0                  
            elif run == 12 or run == 13 or run == 14 or run == 15:
                target_idx_x6 = 5   
                target_idx_x11 = 0
                target_idx_x12 = 0
                target_idx_x14 = 9
                target_idx_x15 = 0
                target_idx_x16 = 0
            elif run == 16 or run == 17:  
                target_idx_x6 = 6     
                target_idx_x11 = 0
                target_idx_x12 = 2 
                target_idx_x14 = 7 
                target_idx_x15 = 0 
                target_idx_x16 = 2 
            elif run == 18 or run == 19: 
                target_idx_x6 = 7  
                target_idx_x11 = 1
                target_idx_x12 = 1
                target_idx_x14 = 7  
                target_idx_x15 = 0
                target_idx_x16 = 1  
            elif run == 20 or run == 21: 
                target_idx_x6 = 6  
                target_idx_x11 = 1
                target_idx_x12 = 1
                target_idx_x14 = 6  
                target_idx_x15 = 0
                target_idx_x16 = 1  
            else:
                target_idx_x6 = 6  
                target_idx_x11 = 0
                target_idx_x12 = 0
                target_idx_x14 = 6  
                target_idx_x15 = 0
                target_idx_x16 = 1	

#============ Simplex: Solving constraint on flow model formulated as LP (searching for positive results) using Simplex
#Ignore the warnings about inaccurate results from Simplex, since we ran Simplex 2x300 times with random initialization of the cost coefficients, 
#so some of the linear program formulations may be numerically difficult to solve (Numerical difficulties encountered) with this library (but those are just a few warnings among the 2x300 solutions).
# Final simulation results may very due to random initialization!!!!
            #start_time = time.time()   
            while True:

                closest_feasible_X_free_relative_error, target_x6, target_x11, target_x12,\
                                        target_x14, target_x15, target_x16=\
                fn.restrictedfreeVarRange(q1,q2,q3,q4,q5,q6, num_simplex_runs, target_idx_x6, target_idx_x11,\
                                       target_idx_x12, target_idx_x14, target_idx_x15, target_idx_x16)


                Xparticular=np.array([[q1],[0],[q5],[q2-q5],[q6-q1],[0],[0],[q2-q1-q5+q6],[q2-q1-q3-q5+q6],\
                                      [q3],[0],[0],[q4],[0],[0],[0]])
                Xnull1=np.array([[1],[-1],[-1],[1],[-1],[1],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0]])
                Xnull2=np.array([[-1],[1],[0],[0],[1],[0],[1],[1],[1],[0],[1],[0],[0],[0],[0],[0]])
                Xnull3=np.array([[0],[0],[0],[0],[0],[0],[0],[0],[1],[-1],[0],[1],[0],[0],[0],[0]])
                Xnull4=np.array([[-1],[1],[0],[0],[1],[0],[1],[1],[1],[0],[0],[0],[-1],[1],[0],[0]])
                Xnull5=np.array([[-1],[0],[0],[0],[1],[0],[0],[1],[1],[0],[0],[0],[0],[0],[1],[0]])
                Xnull6=np.array([[0],[0],[0],[0],[0],[0],[0],[1],[1],[0],[0],[0],[0],[0],[0],[1]])

                x6 = closest_feasible_X_free_relative_error[0]
                x11 = closest_feasible_X_free_relative_error[1]
                x12 = closest_feasible_X_free_relative_error[2]
                x14 = closest_feasible_X_free_relative_error[3]
                x15 = closest_feasible_X_free_relative_error[4]
                x16 = closest_feasible_X_free_relative_error[5]
                Xcomplete = Xparticular + x6*Xnull1 + x11*Xnull2 + x12*Xnull3 + x14*Xnull4 + x15*Xnull5 + x16*Xnull6
                #print('Xcomplete', Xcomplete)
                
                if np.all(Xcomplete >= 0):
                    break
            #print("--- %s seconds ---" % (time.time() - start_time))
#============= End Simplex

            TTS += (traci.vehicle.getIDCount())*(60/3600)

#============= Checking synchronization of actual traffic data timestamp and time of simulation - to start to simulate new flows for the new time slot in right time, new minute flows calibration            
            print('select_min: {} sim_time: {}'.format(current_time_sec, traci.simulation.getTime()))    
            
# Generate (calibrate) traffic flows    
#================= cali E_NS5
            v_cali_E_NS5_car=[X_0224_01[1]/3.6, X_0224_02[1]/3.6]
            x =0.001 + sum(x > 0 for x in v_cali_E_NS5_car)
            traci.calibrator.setFlow("caliCar1_E_NS5_0", step*step_length, (step*step_length)+60, X_0224_01[0]+\
                                    X_0224_02[0], (X_0224_01[1]/3.6 + X_0224_02[1]/3.6)/x,\
                                     'vtype_car1', 'route_cali_E_NS5',\
                                     departLane="free", departSpeed='max')

            v_cali_E_NS5_truck=[X_0224_01[3]/3.6, X_0224_02[3]/3.6]
            x =0.001 + sum(x > 0 for x in v_cali_E_NS5_truck)
            traci.calibrator.setFlow("caliTruck1_E_NS5_0", step*step_length, (step*step_length)+60, X_0224_01[2]+\
                                     X_0224_02[2], (X_0224_01[3]/3.6 + X_0224_02[3]/3.6)/x, 'vtype_truck1', 'route_cali_E_NS5',\
                                     departLane="free", departSpeed='max')

#================ cali S_NE11  newKK route_cali_S_NE  - route distribution before the border
            v_cali_S_NE11_car=[X_0200_01[1]/3.6, X_0200_02[1]/3.6, X_0200_03[1]/3.6]
            x =0.001 + sum(x > 0 for x in v_cali_S_NE11_car)
            traci.calibrator.setFlow("caliCar1_S_NE11_0", step*step_length, (step*step_length)+60, X_0200_01[0]+\
                                     X_0200_02[0]+X_0200_03[0], (X_0200_01[1]/3.6 + X_0200_02[1]/3.6 + X_0200_03[1]/3.6)/x,\
                                     'vtype_car1', 'route_cali_S_NE11',\
                                     departLane="free", departSpeed='max')

            v_cali_S_NE11_truck=[X_0200_01[3]/3.6, X_0200_02[3]/3.6, X_0200_03[3]/3.6]
            x =0.001 + sum(x > 0 for x in v_cali_S_NE11_truck)
            traci.calibrator.setFlow("caliTruck1_S_NE11_0", step*step_length, (step*step_length)+60, X_0200_01[2]+\
                                     X_0200_02[2]+X_0200_03[2], (X_0200_01[3]/3.6 + X_0200_02[3]/3.6 + X_0200_03[3]/3.6)/x,\
                                     'vtype_truck1', 'route_cali_S_NE11',\
                                     departLane="free", departSpeed='max')



#================= cali N_ES147
            v_cali_N_ES147_car=[X_0272_03[1]/3.6, X_0272_04[1]/3.6]
            x =0.001 + sum(x > 0 for x in v_cali_N_ES147_car)
            traci.calibrator.setFlow("caliCar1_N_ES147_0", step*step_length, (step*step_length)+60, X_0272_03[0]+\
                                     X_0272_04[0], (X_0272_03[1]/3.6 + X_0272_04[1]/3.6)/x,\
                                     'vtype_car1', 'route_cali_N_ES147',\
                                     departLane="free", departSpeed='max')


            v_cali_N_ES147_truck=[X_0272_03[3]/3.6, X_0272_04[3]/3.6]
            x =0.001 + sum(x > 0 for x in v_cali_N_ES147_truck)
            traci.calibrator.setFlow("caliTruck1_N_ES147_0", step*step_length, (step*step_length)+60, X_0272_03[2]+\
                                     X_0272_04[2], (X_0272_03[3]/3.6 + X_0272_04[3]/3.6)/x,\
                                     'vtype_truck1', 'route_cali_N_ES147',\
                                     departLane="free", departSpeed='max')


#                 departPos="free"
# ================ cali caliCar1_N_ES_onRamp1 (N_ES153)"
            traci.calibrator.setFlow("caliCar1_N_ES_onRamp1", step*step_length, (step*step_length)+60,\
                                     x11,\
                                     22.22, 'vtype_car1', 'route_cali_N_ES152_onRamp1',\
                                     departLane="free", departSpeed='max')

            traci.calibrator.setFlow("caliTruck1_N_ES_onRamp1", step*step_length, (step*step_length)+60,\
                                     0,\
                                     22.22, 'vtype_truck1', 'route_cali_N_ES152_onRamp1',\
                                     departLane="free", departSpeed='max')


#================ cali onRamp1 ES_N
            traci.calibrator.setFlow("caliCar1_ES_N_onRamp1", step*step_length, (step*step_length)+60,\
                                     x12,\
                                     22.22, 'vtype_car1', 'route_cali_ES_N56_onRamp1',\
                                     departLane="free", departSpeed='max')

            traci.calibrator.setFlow("caliTruck1_ES_N_onRamp1", step*step_length, (step*step_length)+60,\
                                     0,\
                                     22.22, 'vtype_truck1', 'route_cali_ES_N56_onRamp1',\
                                     departLane="free", departSpeed='max')   
        
        
#================ cali onRamp x15_E
            traci.calibrator.setFlow("caliCar1_x15_E_onRamp", step*step_length, (step*step_length)+60,\
                                     x15,\
                                     22.22, 'vtype_car1', 'route_cali_x15_E_onRamp',\
                                     departLane="free", departSpeed='max')

            traci.calibrator.setFlow("caliTruck1_x15_E_onRamp", step*step_length, (step*step_length)+60,\
                                     0,\
                                     22.22, 'vtype_truck1', 'route_cali_x15_E_onRamp',\
                                     departLane="free", departSpeed='max') 
        
        
#================ cali onRamp x16_N
            traci.calibrator.setFlow("caliCar1_x16_N_onRamp", step*step_length, (step*step_length)+60,\
                                     x16,\
                                     22.22, 'vtype_car1', 'route_cali_x16_N_onRamp',\
                                     departLane="free", departSpeed='max')

            traci.calibrator.setFlow("caliTruck1_x16_N_onRamp", step*step_length, (step*step_length)+60,\
                                     0,\
                                     22.22, 'vtype_truck1', 'route_cali_x16_N_onRamp',\
                                     departLane="free", departSpeed='max')         


#================ Route distributions             
            if q2 != 0:
                Px4 = (np.round(10*(Xcomplete[3])/q2))*10
                #print(Px4, Xcomplete[3], q2)
                Px3 = (100 - Px4)
            else:
                Px4=50
                Px3 = (100 - Px4)

            if Xcomplete[7] !=0:
                Px10 = (np.round(10*(Xcomplete[9])/Xcomplete[7]))*10
                #print(Px10, Xcomplete[9], Xcomplete[7])
                Px9 = (100 - Px10)
            else:
                Px10=50
                Px9 = (100 - Px10)

            if q4 != 0:
                Px13 = (np.round(10*(Xcomplete[12])/q4))*10
                #print(Px13, Xcomplete[12], q4)
                Px14 = (100 - Px13)
            else:
                Px13=50
                Px14 = (100 - Px13)

            if Xcomplete[6] != 0:
                Px2 = (np.round(10*(Xcomplete[1])/Xcomplete[6]))*10
                #print(Px2, Xcomplete[1], Xcomplete[6])
                Px6 = (100 - Px2)
            else:
                Px2=50
                Px6 = (100 - Px2)

            if q6 !=0:
                Px5 = (np.round(10*(Xcomplete[4])/q6))*10
                #print(Px5, Xcomplete[4], q6)
                Px1 = (100 - Px5)
            else:
                Px5=50
                Px1 = (100 - Px5)       

            edgeStart1="E_NS"
            r_dist1="routedist_E_NS_"+str(int(Px4))+"_"+str(int(Px3))
            edgeStart2="ES_N_Router"
            r_dist2="routedist_ES_N_Router123toRouter3_"+str(int(Px10))+"_"+str(int(Px9))
            edgeStart3="N_S_Router"              
            r_dist3="routedist_N_S_Router3toRouter123_"+str(int(Px14))+"_"+str(int(Px13))
            edgeStart4="N_SE"
            r_dist4="routedist_N_SE_"+str(int(Px2))+"_"+str(int(Px6))
            edgeStart5="EN_S" 
            r_dist5="routedist_equal_EN_S_border"
            edgeStart6="S_NE"
            r_dist6="routedist_S_NE_"+str(int(Px5))+"_"+str(int(Px1))
			
#================ Route distributions End			

#========== This block eventually adds routing flags to vehicles, once routed through the network, flags, and vehicles are removed from this check 
        if step%(res_time*(1/step_length))==0:
    
            if step%(60*(1/step_length))==0:
                sim_time = round(traci.simulation.getTime())
                if step==0:
                
                    temp_r_dist1 = []
                    temp_r_dist2 = []
                    temp_r_dist3 = []
                    temp_r_dist4 = []
                    temp_r_dist5 = []
                    temp_r_dist6 = []
                    
                    current_routes_dist = [r_dist1, r_dist2, r_dist3, r_dist4, r_dist5, r_dist6]
                    
                    temp_r_dist1.append([newVehIDs_E_in + newVehIDs_N_in + newVehIDs_S_in + newVehIDs_on_ramp_x12_N +\
                                     newVehIDs_on_ramp_x11_S + newVehIDs_on_ramp_x15_E + newVehIDs_on_ramp_x16_N,\
                                         [r_dist1], [sim_time]])
                    temp_r_dist2.append([newVehIDs_E_in + newVehIDs_N_in + newVehIDs_S_in + newVehIDs_on_ramp_x12_N +\
                                     newVehIDs_on_ramp_x11_S + newVehIDs_on_ramp_x15_E + newVehIDs_on_ramp_x16_N,\
                                         [r_dist2], [sim_time]])
                    temp_r_dist3.append([newVehIDs_E_in + newVehIDs_N_in + newVehIDs_S_in + newVehIDs_on_ramp_x12_N +\
                                     newVehIDs_on_ramp_x11_S + newVehIDs_on_ramp_x15_E + newVehIDs_on_ramp_x16_N,\
                                         [r_dist3], [sim_time]])
                    temp_r_dist4.append([newVehIDs_E_in + newVehIDs_N_in + newVehIDs_S_in + newVehIDs_on_ramp_x12_N +\
                                     newVehIDs_on_ramp_x11_S + newVehIDs_on_ramp_x15_E + newVehIDs_on_ramp_x16_N,\
                                         [r_dist4], [sim_time]])
                    temp_r_dist5.append([newVehIDs_E_in + newVehIDs_N_in + newVehIDs_S_in + newVehIDs_on_ramp_x12_N +\
                                     newVehIDs_on_ramp_x11_S + newVehIDs_on_ramp_x15_E + newVehIDs_on_ramp_x16_N,\
                                         [r_dist5], [sim_time]])
                    temp_r_dist6.append([newVehIDs_E_in + newVehIDs_N_in + newVehIDs_S_in + newVehIDs_on_ramp_x12_N +\
                                     newVehIDs_on_ramp_x11_S + newVehIDs_on_ramp_x15_E + newVehIDs_on_ramp_x16_N,\
                                         [r_dist6], [sim_time]])
                else:
                    if len(temp_r_dist1[0][0]) != 0:
                        perm_r_dist1.append(temp_r_dist1[0])
                    temp_r_dist1 = []
                    current_routes_dist = [r_dist1, r_dist2, r_dist3, r_dist4, r_dist5, r_dist6]
                    temp_r_dist1.append([newVehIDs_E_in + newVehIDs_N_in + newVehIDs_S_in + newVehIDs_on_ramp_x12_N +\
                                     newVehIDs_on_ramp_x11_S + newVehIDs_on_ramp_x15_E + newVehIDs_on_ramp_x16_N,\
                                         [r_dist1], [sim_time]])
                    
                    if len(temp_r_dist2[0][0]) != 0:
                        perm_r_dist2.append(temp_r_dist2[0])
                    temp_r_dist2 = []
                    current_routes_dist = [r_dist1, r_dist2, r_dist3, r_dist4, r_dist5, r_dist6]
                    temp_r_dist2.append([newVehIDs_E_in + newVehIDs_N_in + newVehIDs_S_in + newVehIDs_on_ramp_x12_N +\
                                     newVehIDs_on_ramp_x11_S + newVehIDs_on_ramp_x15_E + newVehIDs_on_ramp_x16_N,\
                                         [r_dist2], [sim_time]])
                    
                    if len(temp_r_dist3[0][0]) != 0:
                        perm_r_dist3.append(temp_r_dist3[0])
                    temp_r_dist3 = []
                    current_routes_dist = [r_dist1, r_dist2, r_dist3, r_dist4, r_dist5, r_dist6]
                    temp_r_dist3.append([newVehIDs_E_in + newVehIDs_N_in + newVehIDs_S_in + newVehIDs_on_ramp_x12_N +\
                                     newVehIDs_on_ramp_x11_S + newVehIDs_on_ramp_x15_E + newVehIDs_on_ramp_x16_N,\
                                         [r_dist3], [sim_time]])
                    
                    if len(temp_r_dist4[0][0]) != 0:
                        perm_r_dist4.append(temp_r_dist4[0])
                    temp_r_dist4 = []
                    current_routes_dist = [r_dist1, r_dist2, r_dist3, r_dist4, r_dist5, r_dist6]
                    temp_r_dist4.append([newVehIDs_E_in + newVehIDs_N_in + newVehIDs_S_in + newVehIDs_on_ramp_x12_N +\
                                     newVehIDs_on_ramp_x11_S + newVehIDs_on_ramp_x15_E + newVehIDs_on_ramp_x16_N,\
                                         [r_dist4], [sim_time]])
                    
                    if len(temp_r_dist5[0][0]) != 0:
                        perm_r_dist5.append(temp_r_dist5[0])
                    temp_r_dist5 = []
                    current_routes_dist = [r_dist1, r_dist2, r_dist3, r_dist4, r_dist5, r_dist6]
                    temp_r_dist5.append([newVehIDs_E_in + newVehIDs_N_in + newVehIDs_S_in + newVehIDs_on_ramp_x12_N +\
                                     newVehIDs_on_ramp_x11_S + newVehIDs_on_ramp_x15_E + newVehIDs_on_ramp_x16_N,\
                                         [r_dist5], [sim_time]])
                    
                    if len(temp_r_dist6[0][0]) != 0:
                        perm_r_dist6.append(temp_r_dist6[0])
                    temp_r_dist6 = []
                    current_routes_dist = [r_dist1, r_dist2, r_dist3, r_dist4, r_dist5, r_dist6]
                    temp_r_dist6.append([newVehIDs_E_in + newVehIDs_N_in + newVehIDs_S_in + newVehIDs_on_ramp_x12_N +\
                                     newVehIDs_on_ramp_x11_S + newVehIDs_on_ramp_x15_E + newVehIDs_on_ramp_x16_N,\
                                         [r_dist6], [sim_time]])
                    
                
        
            for v_id in newVehIDs_E_in:
                temp_r_dist1[0][0].append(v_id)
                temp_r_dist2[0][0].append(v_id)
                temp_r_dist3[0][0].append(v_id)
                temp_r_dist4[0][0].append(v_id)
                temp_r_dist5[0][0].append(v_id)
                temp_r_dist6[0][0].append(v_id)
            for v_id in newVehIDs_N_in:
                temp_r_dist1[0][0].append(v_id)
                temp_r_dist2[0][0].append(v_id)
                temp_r_dist3[0][0].append(v_id)
                temp_r_dist4[0][0].append(v_id)
                temp_r_dist5[0][0].append(v_id)
                temp_r_dist6[0][0].append(v_id)
            for v_id in newVehIDs_S_in:
                temp_r_dist1[0][0].append(v_id)
                temp_r_dist2[0][0].append(v_id)
                temp_r_dist3[0][0].append(v_id)
                temp_r_dist4[0][0].append(v_id)
                temp_r_dist5[0][0].append(v_id)
                temp_r_dist6[0][0].append(v_id)
            for v_id in newVehIDs_on_ramp_x12_N:
                temp_r_dist1[0][0].append(v_id)
                temp_r_dist2[0][0].append(v_id)
                temp_r_dist3[0][0].append(v_id)
                temp_r_dist4[0][0].append(v_id)
                temp_r_dist5[0][0].append(v_id)
                temp_r_dist6[0][0].append(v_id)
            for v_id in newVehIDs_on_ramp_x11_S:
                temp_r_dist1[0][0].append(v_id)
                temp_r_dist2[0][0].append(v_id)
                temp_r_dist3[0][0].append(v_id)
                temp_r_dist4[0][0].append(v_id)
                temp_r_dist5[0][0].append(v_id)
                temp_r_dist6[0][0].append(v_id)
            for v_id in newVehIDs_on_ramp_x15_E:
                temp_r_dist1[0][0].append(v_id)
                temp_r_dist2[0][0].append(v_id)
                temp_r_dist3[0][0].append(v_id)
                temp_r_dist4[0][0].append(v_id)
                temp_r_dist5[0][0].append(v_id)
                temp_r_dist6[0][0].append(v_id)            
            for v_id in newVehIDs_on_ramp_x16_N:
                temp_r_dist1[0][0].append(v_id)
                temp_r_dist2[0][0].append(v_id)
                temp_r_dist3[0][0].append(v_id)
                temp_r_dist4[0][0].append(v_id)
                temp_r_dist5[0][0].append(v_id)
                temp_r_dist6[0][0].append(v_id)

#========== adds routing flags End            
            
# routeDinamically  (DFC mechanism)
            if step>0:
                if sim_time % C == 0:
                    vehIDs_all = traci.vehicle.getIDList()
    # ========== assign routes to veh coming from east (E) in direction north-south (NS) "Router1"
    #(given the probability dist. model)
    #             r_dist1="routedist_E_NS_"+str(int(Px4))+"_"+str(int(Px3))
                temp_r_dist1, perm_r_dist1 = fn.routingDinamically("E_NS5", "E_NS6", r_dist1,\
                                                                     temp_r_dist1,\
                                                                     perm_r_dist1,\
                                                                     edgeStart1, C, sim_time, vehIDs_all)

    #=========== assign routes to veh coming from east (E) and south (S) in direction north (N) "Router123"
                # to off ramp1 (direction north)
                #(given the probability dist. model)
    #             r_dist2="routedist_ES_N_Router123toRouter3_"+str(int(Px10))+"_"+str(int(Px9))
                temp_r_dist2, perm_r_dist2 = fn.routingDinamically("ES_N6", "ES_N7", r_dist2,\
                                                                     temp_r_dist2,\
                                                                     perm_r_dist2,\
                                                                     edgeStart2, C, sim_time, vehIDs_all)

    #=========== assign routes to veh coming from north (N) in direction Ramp1 and "Router123"
                #(given the probability dist. model)
    #             r_dist3="routedist_N_S_Router3toRouter123_"+str(int(Px14))+"_"+str(int(Px13))
                temp_r_dist3, perm_r_dist3 = fn.routingDinamically("N_ES148", "N_ES149", r_dist3,\
                                                                     temp_r_dist3,\
                                                                     perm_r_dist3,\
                                                                     edgeStart3, C, sim_time, vehIDs_all)

    #=========== assign routes to veh coming from north (N) in direction south (S) and east (E)"
                #(given the probability dist. model)
    #             r_dist4="routedist_N_SE_"+str(int(Px2))+"_"+str(int(Px6))
                temp_r_dist4, perm_r_dist4 = fn.routingDinamically("N_ES158", "N_ES159", r_dist4,\
                                                                     temp_r_dist4,\
                                                                     perm_r_dist4,\
                                                                     edgeStart4, C, sim_time, vehIDs_all)

    #=========== border flows handlers:
                # assign routes to veh coming to the border (direction France) "Router2"
                # equal probability distribution)
    #             r_dist5="routedist_equal_EN_S_border"
                temp_r_dist5, perm_r_dist5 = fn.routingDinamically("EN_S1", "EN_S1.136", r_dist5,\
                                                                     temp_r_dist5,\
                                                                     perm_r_dist5,\
                                                                     edgeStart5, C, sim_time, vehIDs_all)
    #             fn.changeVehTargetEdge("EN_S1", "EN_S1.136", oldVehIDs_EN_S1, "EN_S12")

                # assign routes to veh from the flow coming out from the border (direction Geneve) "Router2"
                #(given the probability dist. model)
    #             r_dist6="routedist_S_NE_"+str(int(Px5))+"_"+str(int(Px1))
                temp_r_dist6, perm_r_dist6 = fn.routingDinamically("S_NE12", "S_NE13", r_dist6,\
                                                                     temp_r_dist6,\
                                                                     perm_r_dist6,\
                                                                     edgeStart6, C, sim_time, vehIDs_all)
                
                vehIDs_all = []
#============ END dinamicRouting

#======== SIM SPEED: slow down or speed up dynamically simulation speed execution (concerning current processing speed)      
        time.sleep(time_sleep)        
        #time.sleep(0.25) 
#======== SIM SPEED End		
    

#========= Write results
        if step%(3600*(1/step_length))==0 and step>0:
            df=pd.DataFrame({'f_E_in_ref': controlFile[1:,0], 'f_E_in': controlFile[1:,1],\
                             'f_N_in_ref': controlFile[1:,2], 'f_N_in': controlFile[1:,3],\
                             'f_S_in_ref': controlFile[1:,4], 'f_S_in': controlFile[1:,5],\
                             'f_E_out_ref': controlFile[1:,6], 'f_E_out': controlFile[1:,7],\
                             'f_N_out_ref': controlFile[1:,8], 'f_N_out': controlFile[1:,9],\
                             'f_S_out_ref': controlFile[1:,10], 'f_S_out': controlFile[1:,11],\
                             'TTS': controlFile[1:,12],\
                             'f_on_ramp_x12_N_ref': controlFile[1:,13], 'f_on_ramp_x12_N': controlFile[1:,14],\
                             'f_on_ramp_x11_S_ref': controlFile[1:,15], 'f_on_ramp_x11_S': controlFile[1:,16],\
                             'f_on_ramp_x15_E_ref': controlFile[1:,17], 'f_on_ramp_x15_E': controlFile[1:,18],\
                             'f_on_ramp_x16_N_ref': controlFile[1:,19], 'f_on_ramp_x16_N': controlFile[1:,20],\
                             'f_off_ramp_x13_S_ref': controlFile[1:,21], 'f_off_ramp_x13_S': controlFile[1:,22],\
                             'f_off_ramp_x9_N_ref': controlFile[1:,23], 'f_off_ramp_x9_N': controlFile[1:,24]})
            
            #saveState(run)  # one can save simulation state e.g., each hour (simulation can be thus reloaded and simulated from this point in time)
            TTS=0
            save_data_time = (dt.datetime.now() - dt.timedelta(minutes=59)).strftime('%Y-%m-%d-%H-%M')
            df.to_excel(path_data+"cF"+save_data_time+".xlsx", index = False)
            controlFile = np.zeros((1,25))
            run+=1

        step += 1 
    traci.close()    
