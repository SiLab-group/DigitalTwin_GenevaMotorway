#    Digital Twin of Geneva Motorway (DT-GM) in SUMO
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



import traci # Traffic Control Interface
import numpy as np
from numpy import savetxt
from scipy.spatial.distance import cosine
# from scipy.stats import qmc
from scipy.optimize import linprog
from sklearn.metrics.pairwise import cosine_similarity, cosine_distances



def TTS_Total():
    numberOfVeh = traci.vehicle.getIDCount()    
    return numberOfVeh

def getVehIDs():
    listVehIDs = traci.vehicle.getIDList()
    return listVehIDs

def routingDinamically(edgeStart, edgeStartPlusOne, routesDistribution, temp_obj_dist, perm_obj_dist, edgeStart_id, C, sim_time, vehIDs_all):

    currentVehIDs = traci.edge.getLastStepVehicleIDs(edgeStart)
    for obj1 in list(temp_obj_dist):
        if len(temp_obj_dist[0])!=0:
            for veh in list(obj1[0]):
                for vehID in list(currentVehIDs):
                    if veh == vehID:
                        for route_dist in list(obj1[1]):
                            try:
                                route_dist.index(edgeStart_id)
                            except ValueError:
                                right_router=0
                            else:
                                right_router=1
                            if right_router == True:
                                traci.vehicle.setRouteID(vehID, route_dist)
                                obj1[0].remove(veh)


    for obj1 in list(perm_obj_dist):
        if len(obj1[0])!=0:
            for veh in list(obj1[0]):
                for vehID in list(currentVehIDs):
                    if veh == vehID:
                        for route_dist in list(obj1[1]):
                            try:
                                route_dist.index(edgeStart_id)
                            except ValueError:
                                right_router=0
                            else:
                                right_router=1
                            if right_router == True:
                                traci.vehicle.setRouteID(vehID, route_dist)
                                obj1[0].remove(veh)


    if sim_time % C == 0:
        for obj1 in list(perm_obj_dist):
            if len(obj1[0])!=0:
                for veh in list(obj1[0]):
                    if veh not in vehIDs_all:
                        obj1[0].remove(veh)



    perm_obj_dist = [obj_i for obj_i in perm_obj_dist if len(obj_i[0])!=0]

    return temp_obj_dist, perm_obj_dist


def edgeVehParameters(edgeStart, edgeStartPlusOne, oldVehIDs):
# for small time step should capture only one veh on detector with the length of 5 [m]
    intersection = set(oldVehIDs).intersection(traci.edge.getLastStepVehicleIDs(edgeStartPlusOne))

    if len(list(intersection)) != 0:
        for idVeh in list(intersection):
            indexVeh = oldVehIDs.index(idVeh)
            del oldVehIDs[indexVeh]       
    
    currentVehIDs=traci.edge.getLastStepVehicleIDs(edgeStart)
    newVehIDs = []
    for vehID in currentVehIDs:
        if vehID not in oldVehIDs:
            newVehIDs.append(vehID)
    n = 0
    speed = 0
    for vehID in newVehIDs:
        speed += traci.vehicle.getSpeed(vehID)
        oldVehIDs.append(vehID)
        n = n + 1
    flow = n
        
    return flow, speed, oldVehIDs, newVehIDs



def freeVarRange(q1,q2,q3,q4,q5,q6, num_simplex_runs):
#     sampler = qmc.Sobol(d=6, scramble=False)
#     c_array = sampler.random_base2(m=8)*2
#     c_array=c_array-1
    
    X_free_range = np.zeros((6,1))
    A_con = np.array([[-1, 1, 0, 1, 1, 0], [1, -1, 0, -1, 0, 0], [1, 0, 0, 0, 0, 0], [-1, 0, 0, 0, 0, 0], [1, -1, 0, -1, -1, 0],\
                      [0, -1, 0, -1, 0, 0], [0, -1, 0, -1, -1, -1], [0, -1, -1, -1, -1, -1], [0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 0]])
    b_con = np.array([q1, 0, q5, q2-q5, q6-q1, 0, q2-q1-q5+q6, q2-q1-q3-q5+q6, q3, q4])
    
    for i in range(num_simplex_runs):
#         c = np.array([c_array[i,0], c_array[i,1], c_array[i,2],\
#                       c_array[i,3], c_array[i,4], c_array[i,5]])        
        c = np.array([np.random.uniform(-1,1), np.random.uniform(-1,1), np.random.uniform(-1,1),\
                      np.random.uniform(-1,1), np.random.uniform(-1,1), np.random.uniform(-1,1)])
#         c = np.array([np.random.randint(-30,30), np.random.randint(-30,30), np.random.randint(-30,30),\
#                       np.random.randint(-30,30), np.random.randint(-30,30), np.random.randint(-30,30)])
        res = linprog(c, A_ub=A_con, b_ub=b_con)
        res1=res
        
        if res.success == True:
        
            new_x = (np.round(res.x)).reshape(6,1)

            Xparticular=np.array([[q1],[0],[q5],[q2-q5],[q6-q1],[0],[0],[q2-q1-q5+q6],[q2-q1-q3-q5+q6],[q3],[0],[0],[q4],[0],[0],[0]])
            Xnull1=np.array([[1],[-1],[-1],[1],[-1],[1],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0]])
            Xnull2=np.array([[-1],[1],[0],[0],[1],[0],[1],[1],[1],[0],[1],[0],[0],[0],[0],[0]])
            Xnull3=np.array([[0],[0],[0],[0],[0],[0],[0],[0],[1],[-1],[0],[1],[0],[0],[0],[0]])
            Xnull4=np.array([[-1],[1],[0],[0],[1],[0],[1],[1],[1],[0],[0],[0],[-1],[1],[0],[0]])
            Xnull5=np.array([[-1],[0],[0],[0],[1],[0],[0],[1],[1],[0],[0],[0],[0],[0],[1],[0]])
            Xnull6=np.array([[0],[0],[0],[0],[0],[0],[0],[1],[1],[0],[0],[0],[0],[0],[0],[1]])

            x6 = new_x[0]
            x11 = new_x[1]
            x12 = new_x[2]
            x14 = new_x[3]
            x15 = new_x[4]
            x16 = new_x[5]
            Xcomplete = Xparticular + x6*Xnull1 + x11*Xnull2 + x12*Xnull3 + x14*Xnull4 + x15*Xnull5 + x16*Xnull6

            # for some unkonwn reason linprog sometimes return solution with negative values 
            #(even the linear program is constrained to be positivie)
            # the code below check if this is the case and just ignore that solution        
            xx=0
            for kk in Xcomplete:
                xx+=kk<0

            if xx==0:
                if i==0:
                    X_free_range[:,0]=new_x[:,0]
                else:
                    X_free_range=np.hstack((X_free_range, new_x))
            else:
                print('negative solution found first iteration')
            
    return X_free_range, res1

def restrictedfreeVarRange(q1,q2,q3,q4,q5,q6, num_simplex_runs, target_idx_x6, target_idx_x11, target_idx_x12,\
                           target_idx_x14, target_idx_x15, target_idx_x16):
#Ignore the warnings about inaccurate results from Simplex, since we ran Simplex 2x300 times with random initialization of the cost coefficients, 
#so some of the linear program formulations may be numerically difficult to solve (Numerical difficulties encountered) with this library (but those are just a few warnings among the 2x300 solutions).


#     sampler = qmc.Sobol(d=6, scramble=False)
#     c_array = sampler.random_base2(m=8)*2
#     c_array=c_array-1
    
    A_con = np.array([[-1, 1, 0, 1, 1, 0], [1, -1, 0, -1, 0, 0], [1, 0, 0, 0, 0, 0], [-1, 0, 0, 0, 0, 0], [1, -1, 0, -1, -1, 0],\
                      [0, -1, 0, -1, 0, 0], [0, -1, 0, -1, -1, -1], [0, -1, -1, -1, -1, -1], [0, 0, 1, 0, 0, 0], [0, 0, 0, 1, 0, 0]])
    b_con = np.array([q1, 0, q5, q2-q5, q6-q1, 0, q2-q1-q5+q6, q2-q1-q3-q5+q6, q3, q4])
    results = freeVarRange(q1,q2,q3,q4,q5,q6,num_simplex_runs)
    X_free_range = results[0]
    X_free_bound_feasible=np.zeros((6,1))
    
    d_x6 = (np.nanmax(X_free_range[0,:])-np.nanmin(X_free_range[0,:]))/9;
    d_x11 = (np.nanmax(X_free_range[1,:])-np.nanmin(X_free_range[1,:]))/9;
    d_x12 = (np.nanmax(X_free_range[2,:])-np.nanmin(X_free_range[2,:]))/9;
    d_x14 = (np.nanmax(X_free_range[3,:])-np.nanmin(X_free_range[3,:]))/9;
    d_x15 = (np.nanmax(X_free_range[4,:])-np.nanmin(X_free_range[4,:]))/9;
    d_x16 = (np.nanmax(X_free_range[5,:])-np.nanmin(X_free_range[5,:]))/9;    
    a0_x6 = np.nanmin(X_free_range[0,:]);
    a0_x11 = np.nanmin(X_free_range[1,:]);
    a0_x12 = np.nanmin(X_free_range[2,:]);
    a0_x14 = np.nanmin(X_free_range[3,:]);
    a0_x15 = np.nanmin(X_free_range[4,:]);
    a0_x16 = np.nanmin(X_free_range[5,:]);    
    x6_bin = [];
    x11_bin = [];
    x12_bin = [];
    x14_bin = [];
    x15_bin = [];
    x16_bin = [];    
    
    for k in range (0,10):
        x6_bin.append(a0_x6+(k)*d_x6)
        x11_bin.append(a0_x11+(k)*d_x11)
        x12_bin.append(a0_x12+(k)*d_x12)
        x14_bin.append(a0_x14+(k)*d_x14)
        x15_bin.append(a0_x15+(k)*d_x15)
        x16_bin.append(a0_x16+(k)*d_x16)        
    
    ii=0
    for i in range(num_simplex_runs):
        i_x6 = np.random.randint(0,10)
        i_x11 = np.random.randint(0,10)
        i_x12 = np.random.randint(0,10)
        i_x14 = np.random.randint(0,10)
        i_x15 = np.random.randint(0,10)
        i_x16 = np.random.randint(0,10)        
        
        x6_bounds = (np.floor(x6_bin[i_x6]), np.floor(x6_bin[i_x6] + d_x6))
        x11_bounds = (np.floor(x11_bin[i_x11]), np.floor(x11_bin[i_x11] + d_x11))
        x12_bounds = (np.floor(x12_bin[i_x12]), np.floor(x12_bin[i_x12] + d_x12))
        x14_bounds = (np.floor(x14_bin[i_x14]), np.floor(x14_bin[i_x14] + d_x14))
        x15_bounds = (np.floor(x15_bin[i_x15]), np.floor(x15_bin[i_x15] + d_x15))
        x16_bounds = (np.floor(x16_bin[i_x16]), np.floor(x16_bin[i_x16] + d_x16))        
        boun=[x6_bounds, x11_bounds, x12_bounds, x14_bounds, x15_bounds, x16_bounds];

#         c = np.array([c_array[i,0], c_array[i,1], c_array[i,2],\
#                       c_array[i,3], c_array[i,4], c_array[i,5]])        
        c = np.array([np.random.uniform(-1,1), np.random.uniform(-1,1), np.random.uniform(-1,1),\
                      np.random.uniform(-1,1), np.random.uniform(-1,1), np.random.uniform(-1,1)])
#         c = np.array([np.random.randint(-30,30), np.random.randint(-30,30), np.random.randint(-30,30),\
#                       np.random.randint(-30,30), np.random.randint(-30,30), np.random.randint(-30,30)])    
        res = linprog(c, A_ub=A_con, b_ub=b_con, bounds=boun)

        # solver summary results
        res1=results[1] # result from linprog 'feasible range'
        res2=res # result from this
        
        if res.success == True:
            new_x = (np.round(res.x)).reshape(6,1)

            Xparticular=np.array([[q1],[0],[q5],[q2-q5],[q6-q1],[0],[0],[q2-q1-q5+q6],[q2-q1-q3-q5+q6],[q3],[0],[0],[q4],[0],[0],[0]])
            Xnull1=np.array([[1],[-1],[-1],[1],[-1],[1],[0],[0],[0],[0],[0],[0],[0],[0],[0],[0]])
            Xnull2=np.array([[-1],[1],[0],[0],[1],[0],[1],[1],[1],[0],[1],[0],[0],[0],[0],[0]])
            Xnull3=np.array([[0],[0],[0],[0],[0],[0],[0],[0],[1],[-1],[0],[1],[0],[0],[0],[0]])
            Xnull4=np.array([[-1],[1],[0],[0],[1],[0],[1],[1],[1],[0],[0],[0],[-1],[1],[0],[0]])
            Xnull5=np.array([[-1],[0],[0],[0],[1],[0],[0],[1],[1],[0],[0],[0],[0],[0],[1],[0]])
            Xnull6=np.array([[0],[0],[0],[0],[0],[0],[0],[1],[1],[0],[0],[0],[0],[0],[0],[1]])

            x6 = new_x[0]
            x11 = new_x[1]
            x12 = new_x[2]
            x14 = new_x[3]
            x15 = new_x[4]
            x16 = new_x[5]            
            Xcomplete = Xparticular + x6*Xnull1 + x11*Xnull2 + x12*Xnull3 + x14*Xnull4 + x15*Xnull5 + x16*Xnull6

            # for some unkonwn reason linprog sometimes return solution with negative values 
            #(even the linprogram is constrained to be positivie)
            # the code below check if this is the case and just ignore that solution
            xx=0
            for kk in Xcomplete:
                xx+=kk<0


            if xx==0:
                if ii == 0:
                    X_free_bound_feasible[:,0]=new_x[:,0];
                    ii = 1
                else:
                    X_free_bound_feasible=np.hstack((X_free_bound_feasible, new_x))
            else:
                print('negative solution generated second iteration')

    x6_bin=np.floor(x6_bin)
    x11_bin=np.floor(x11_bin)
    x12_bin=np.floor(x12_bin)
    x14_bin=np.floor(x14_bin)
    x15_bin=np.floor(x15_bin)
    x16_bin=np.floor(x16_bin)    

    target_x6=x6_bin[target_idx_x6]
    target_x11=x11_bin[target_idx_x11]
    target_x12=x12_bin[target_idx_x12]
    target_x14=x14_bin[target_idx_x14]
    target_x15=x15_bin[target_idx_x15]
    target_x16=x16_bin[target_idx_x16]    
    

#    cos_simi_array = cosine_similarity(X_free_bound_feasible.transpose(), [[target_x6, target_x11, target_x12,\
#                                                                            target_x14, target_x15, target_x16]])
    
#====================================== Waighted cosine
#     cos_simi = []
#     print('X free shape: ', X_free_bound_feasible.shape[1])
#     for vec in range(X_free_bound_feasible.shape[1]):
#         Xfb = X_free_bound_feasible[:,vec]
#         cos_simi.append(1 - cosine(Xfb.transpose(), [target_x6, target_x11, target_x12,\
#                                                                             target_x14, target_x15, target_x16], [2,1,1,2,1,1]))
#     cos_simi_array = np.array(cos_simi)
#============================================    
#    cos_simi_max_indx = cos_simi_array.argmax()
#    cos_sim_max_value = cos_simi_array.max()
#    closest_feasible_X_free = X_free_bound_feasible[:, cos_simi_max_indx]
#=========================================================

#====== RELATIVE error  -> Produces more accurate results (Currently used in DT-GM)
    target_vec = np.array([[target_x6], [target_x11], [target_x12], [target_x14], [target_x15], [target_x16]])
    norm_target = np.linalg.norm(target_vec, axis=0)
    norm_diff_target_feasible_array = np.linalg.norm(X_free_bound_feasible - target_vec, axis=0)
    relative_error = norm_diff_target_feasible_array/norm_target

    relative_error_indx = relative_error.argmin()
    relative_error_min_value = relative_error.min()
    closest_feasible_X_free_relative_error = X_free_bound_feasible[:, relative_error_indx]
    
    
    return closest_feasible_X_free_relative_error, target_x6, target_x11, target_x12, target_x14, target_x15, target_x16



#=========== Functions Save/Load simulation state
def saveState(run):
    traci.simulation.saveState('my_save_state_DT_GM_live24h_'+str(run)+'.xml')
    
def loadState(run):
    traci.load(["--start", "1", "--quit-on-end", "1", "--load-state", "my_save_state_DT_GM_live24h_"+str(run)+".xml"])
