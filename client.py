import numpy as np
import pandas as pd
from itertools import chain

import scipy as sp
from scipy.spatial import distance_matrix

from pyclustering.cluster.kmeans import kmeans
from pyclustering.cluster.center_initializer import kmeans_plusplus_initializer
from pyclustering.utils.metric import type_metric, distance_metric

manhattan_dist = lambda p1, p2: np.ravel(np.sum(abs(p1 - p2), axis=1)) 
metric = distance_metric(type_metric.USER_DEFINED, func=manhattan_dist)

class routePlanner():
    def __init__(self, patients, hospitals, ambulances, pop_size, num_iter):
        self.readinData(patients, hospitals, ambulances)
        
        self.__pop_size = pop_size
        self.__crossover_size = int(pop_size * 0.8)
        self.__save_size = int(pop_size * 0.2)
        self.__mutate_size = int(pop_size * 0.1)
        
        self.__num_iter = num_iter
        
        
    def readinData(self, patients_readin, hospitals_readin, ambulances):
        """Clean patient data, assign hospitals, get distance matrix"""
        self.__patients = pd.DataFrame.from_dict(patients_readin, orient='index').values
        self.__hospitals = {h:hospitals_readin[h]['ambulances_at_start'] for h in hospitals_readin}
        self.__hospital_size = {h:len(self.__hospitals[h]) for h in self.__hospitals}
        self.__ambulance_order = list(chain(*[self.__hospitals[h] for h in self.__hospitals]))
        self.clusterPatients()
        hospital_assignment = self.assignHospitals()
        hospital_array = [self.__hospital_loc[i[0]] for i in hospital_assignment]

        self.__ambulances = ambulances
        self.__dist_mat = sp.spatial.distance_matrix(np.vstack((self.__patients[:,:2], hospital_array[::-1])), np.vstack((self.__patients[:,:2], hospital_array[::-1])), 1)    
        
    def assignHospitals(self):
        """Assign hospitals to clusters"""
        clusters_sort = np.argsort(self.__clusters)
        hospital_sort = sorted(self.__hospital_size, key=lambda k: self.__hospital_size[k], reverse=True)
        return list(zip(clusters_sort, hospital_sort))

    def clusterPatients(self):
        """Assign hospital locations"""
        initial_centers = kmeans_plusplus_initializer(self.__patients[:,:2], 5).initialize()
        clusterer = kmeans(self.__patients[:,:2], initial_centers, metric=metric, ccore=True)
        clusterer.process()
        self.__hospital_loc= [np.array([ int(y) for y in x]) for x in clusterer.get_centers()]
        self.__clusters = [c for c in clusterer.get_clusters()]
        self.__num_clusters = len(self.__clusters)

    def evolve(self):
        """Run Genetic Algorithm"""
        self.initPop()
        
        for i in range(self.__num_iter):
            pop_cost = self.popCost()
            print('Max Gen: ', pop_cost.max())
            new_pop = self.selection(pop_cost, self.__crossover_size)  
            new_pop += [self.__pop[i] for i in pop_cost.argsort()[::-1][:self.__save_size]]
            self.__pop = new_pop
            self.mutate()
            
        
    def initPop(self):
        """Initiate Pop of chromosome"""
        self.__pop = [[] for x in range(self.__pop_size)]
        
        for c in range(self.__pop_size):
            
            amb = [[] for x in range(self.__num_clusters)]
            route = [[] for x in range(self.__num_clusters)]
            
            for i in range(self.__num_clusters):
                routes = self.chromsomeInit(i)
                amb[i] = [len(r) for r in routes]
                route[i] = list(chain(*routes))

            self.__pop[c] = [list(chain(*route)), np.cumsum(list(chain(*amb)))]
            
    def chromsomeInit(self, c_num):
        """Create a chromosome"""
        cluster = self.__clusters[c_num].copy()
        amb_num = self.__hospital_size[c_num]
        np.random.shuffle(cluster)

        routes = []
        last_h = [[-c_num] for x in range(amb_num)]
        last_h_pos =[1 for x in range(amb_num)]

        for j in range(amb_num):
            routes.extend([[cluster[j]]])

        for e in cluster[amb_num:]:
            max_saving, max_ind = -np.infty, -1
            for ind, route in enumerate(routes):
                savings = self.__dist_mat[last_h[ind], route[-1]] + self.__dist_mat[last_h[ind], e] - self.__dist_mat[route[-1], e] 

                if savings > max_saving:
                    max_saving = savings
                    max_ind = ind

            add_h = False    
            
            if len(routes[max_ind]) >= (last_h_pos[max_ind] + 2):
                add_h = True
            else:
                if np.random.uniform() < 0.2:
                    add_h = True

            if add_h:      
                dists = self.__dist_mat[e,-5:]
                dists = np.array([ d if d != 0 else 1 for d in dists])
                inv_probs = 1/dists
                probs = inv_probs/np.linalg.norm(inv_probs, ord=1)
                choice = np.random.choice([-1,-2,-3,-4,-5], p=probs)
                routes[max_ind].extend((e, choice))
                last_h[max_ind] = choice
                last_h_pos[max_ind] = len(routes[max_ind])
            else:
                routes[max_ind].extend([e])

        for route in routes:
            if route[-1] > 0:
                dists = self.__dist_mat[route[-1],-5:]
                dists = np.array([ d if d != 0 else 1 for d in dists])
                inv_probs = 1/dists
                probs = inv_probs/np.linalg.norm(inv_probs, ord=1)
                choice = np.random.choice([-1,-2,-3,-4,-5], p=probs)
                route.extend([choice])
        
        return routes
    
    def popCost(self):
        cost_arr = np.zeros(self.__pop_size)

        for i, p in enumerate(self.__pop):
            cost_arr[i] = self.cost(p)
        
        return cost_arr

    def cost(self, chrm):
        """GA Cost"""
        route = chrm[0]
        amb = chrm[1]
        
        #print(len(route), amb[-1])

        p_picked = np.zeros(max(route)+1)
        p_saved = np.zeros(max(route)+1)

        for amb_num in range(len(amb)):
            amb_id = self.__ambulance_order[amb_num]
            cur_loc = self.__ambulances[amb_id]['starting_hospital']

            t_counter = 0
            in_amb = 0
            p_in_amb_arr = np.zeros(4, dtype=int)

            rng = range(amb[amb_id-1], amb[amb_id]) if amb_id > 0 else range(0, amb[amb_id])
            for e in rng:
                amb_stop = route[e]
                if amb_stop > 0:
                    p = amb_stop
                    if in_amb >= 4:
                        print('Get Fucked - Ambulance Full')
                        break
                    if p_picked[p] > 0:
                        print('Already picked up - Facking Idiot')
                        continue
                    else:
                        p_in_amb_arr[in_amb] = p
                        in_amb += 1
                        p_picked[amb_stop] = 1
                        t_counter += 1
                    t_taken = self.__dist_mat[cur_loc, p]
                    t_counter += t_taken
                    cur_loc = p
                    continue 
                else:
                    hosp = amb_stop
                    t_taken = self.__dist_mat[cur_loc, hosp]
                    t_counter += t_taken
                    if in_amb > 0:
                        t_taken += 1
                    cur_loc = hosp 
                    for p in p_in_amb_arr:
                        if t_counter <= self.__patients[p,2]:
                            #print('Ambulance ' + str(amb_id) + ' saved patient ' + str(p))
                            p_saved[p] = 1
                    in_amb = 0
                    p_in_amb_arr = np.zeros(4, dtype=int)
                    
        return sum(p_saved)
    
    def selection(self, pop_cost, k):
        new_pop = [[] for x in range(k)]
        for i in range(0,k,2):
            p1, p2 = np.random.choice(np.arange(0,self.__pop_size), 2, p=pop_cost/pop_cost.sum())
            ch1, ch2 = self.crossover(self.__pop[p1], self.__pop[p2])
            new_pop[i] = ch1
            new_pop[i+1] = ch2
        return new_pop
    
    def crossover(self, chrm1, chrm2):

        p1, amb1 = chrm1
        p2, amb2 = chrm2

        i1 = np.random.randint(1, len(amb1))
        i2 = np.random.randint(1, len(amb2))

        r1 = p1[amb1[i1-1]-1:amb1[i1]]
        r2 = p2[amb2[i2-1]-1:amb2[i2]]
        
        ch1, amb1_new = self.crossoverInsert(r1, p2, amb2)
        ch2, amb2_new = self.crossoverInsert(r2, p1, amb1)
        
        if len(ch1) != amb1_new[-1]:
            print('******************************************************')
            print('p2', p2)
            print('r1', r1)
            print('amb2', amb2)
            print('ch1', ch1)
            print('amb_new', amb1_new)
        
        return [ch1, amb1_new], [ch2, amb2_new]
    
    def crossoverInsert(self, route, parent, amb):
        pr = []
        route_clean = [e for e in route if e > 0]
        for i, el in enumerate(parent):
            if el not in route_clean:
                pr.extend([el])
            else:
                for a in range(len(amb)):
                    if amb[a] >= i:
                        amb[a] -= 1
        
        for el in route_clean:
            for d in self.__dist_mat[pr, el].argsort():
                if pr[d] < 0:
                    continue
                if d < 3:
                    if (min(pr[-3+d:]) < 0)|(min(pr[d:d+3]) < 0):
                        pr.insert(d+1, el)
                        for a in range(len(amb)):
                            if amb[a] >= (d+1):
                                amb[a] += 1
                        break
                else:
                    if min(pr[d-3:d+3]) < 0:
                        pr.insert(d+1, el)
                        for a in range(len(amb)):
                            if amb[a] >= (d+1):
                                amb[a] += 1
                        break
        #print(len(pr), amb)
        return pr, amb

    def mutate(self):
        for i in range(self.__mutate_size):
            c = np.random.choice(np.arange(0,self.__pop_size))
            c1, a1 = self.__pop[c]
            r1_ind = np.random.randint(1, len(a1))
            c1[a1[r1_ind-1]-1:a1[r1_ind]] = c1[a1[r1_ind-1]-1:a1[r1_ind]][::-1]
            
            self.__pop[c][0] = c1
            
            
            
    @property
    def hospital_loc(self):
        return(self.__hospital_loc)
    
    @property
    def hospitals(self):
        return(self.__hospitals)
    
    @property
    def hospital_size(self):
        return(self.__hospital_size)
    
    @property
    def clusters(self):
        return(self.__clusters)
    
    @property
    def ambulances(self):
        return(self.__ambulances)
    
    @property
    def ambulance_order(self):
        return(self.__ambulance_order)
    
    @property
    def dist_mat(self):
        return(self.__dist_mat)
    
    
        
        

