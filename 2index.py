import Data2index as Data
from gurobipy import * 
import math
import Heuristics as Heur
import networkx as nx
import pickle as pkl


#create a function get_nodes that returns a list of nodes that are in the selected edges
def get_nodes(edges):
    nodes = []
    for i in edges:
        nodes.append(i[0])
        nodes.append(i[1])
    return list(set(nodes))

def connected_components(graph): #creates a list of lists with connected components
    #works with a tuplelist
    G_star = nx.Graph()
    G_star.add_edges_from(graph)
    connected = nx.connected_components(G_star) #connected is a list of list of connected components
    return connected


def sub_elim(model, where):
    #get N from the pickle file
    if where == GRB.callback.MIPSOL:
        sol = model.cbGetSolution(model._x) #sol is a dict with pairs of edges and their values
        selected = tuplelist((i,j) for i,j in model._x if sol[i,j] > 0 if i != 0 if j != 0) #is the list of edges that are selected i.e. have value not equal to 0
        

        #check if selected holds
        sum_selected = sum([sol[i,j] for i,j in selected])
        if sum_selected <= len(get_nodes(selected)) - min_route_length(selected): #checks the subtour elimination constraint for the whole selected nodes as "S"
            model.cbLazy(quicksum(model._x[i,j] for i,j in selected) <= len(get_nodes(selected)) - min_route_length(selected))


        components = connected_components(selected) #components is the list of connected components
        for component in components: #component is a list of nodes
            if len(component) > 2:
                #find the sum of values from the component
                sum_component = sum([sol[i,j] for i,j in selected if i in component and j in component])
                if sum_component >= len(component) - min_route_length(component):
                    model.cbLazy(quicksum(quicksum(model._x[i,j] for i in component if i != j) for j in component) <= len(component) - min_route_length(component))
                

        #check for the set N\S_i
        #create all sets of N that does not contrain component from components
        without_components = []
        for component in components:
            without_components.append([i for i in N if i not in component])
        #check if the sum of the values of the sets in without_components is greater than len(without) - min_route_length(without)
        for without in without_components:
            if len(without) > 2:
                sum_without = sum([sol[i,j] for i,j in selected if i in without and j in without])
                if sum_without >= len(without) - min_route_length(without):

                    model.cbLazy(quicksum(quicksum(model._x[i,j] for i in without if i != j) for j in without) <= len(without) - min_route_length(without))


def min_route_length(tour):
    #import the pickle file R_S.pkl 
    ret = [i for i in tour if i in R]
    stor = [i for i in tour if i in S + S_tilde]
    #ret = [i for i in tour if i in R]
    #stor = [i for i in tour if i in S + S_tilde]
    min_route = math.ceil(max([len(ret), len(stor)])/2)
    return min_route


def ASRS(R, S, S_tilde, N, N_plus, A, c, Q, s, d, timelimit, lift, val_eq, initial, with_sub):
    K = len(Data.create_K(len(R), s))
    T = len(R) + s

    mdl = Model('ASRS')

    #add binary variable x
    x = {}
    for i,j in A:
        #x[i,j] = mdl.addVar(vtype= GRB.BINARY, name='x_%d_%d' % (i,j))
        x[i,j] = mdl.addVar(vtype= GRB.BINARY, name='x_%d_%d' % (i,j))
        
    #add binary variable w
    w = {}
    for i in N:
        for j in N:
            if i != j:
                #w[i,j] = mdl.addVar(vtype=GRB.BINARY, name = f'w_{i}_{j}')
                w[i,j] = mdl.addVar(vtype=GRB.BINARY, name = f'w_{i}_{j}')
    
    #add variable u
    u = {}
    for i in N:
        u[i] = mdl.addVar(lb = 1, ub = Q, vtype=GRB.CONTINUOUS, name='u_%d' % (i))
    
    #add variable v
    v = {}
    for i in N:
        v[i] = mdl.addVar(lb = d[i][1], ub = Q, vtype=GRB.CONTINUOUS, name='v_%d' % (i))
    
    t = {}
    for i in N:
        t[i] = mdl.addVar(lb = 1, ub= T, vtype=GRB.CONTINUOUS, name='t%d' % (i)) 
    
    #print(f'x: {[i for i in x if i[0] == 377]}')
    #set objective
    mdl.setObjective(quicksum(c[(i,j)] * x[i,j] for i, j in A), GRB.MINIMIZE)


    #add the constraints
    #equal degree
    mdl.addConstrs(quicksum(x[i,h] for i in N_plus if i != h) - quicksum(x[h,j] for j in N_plus if j != h) == 0 for h in N)

    #All retrievals
    mdl.addConstrs(quicksum(x[i,j] for j in N_plus if j != i) == 1 for i in R)

    #in total s storages
    mdl.addConstr(quicksum(quicksum(x[i,j] for i in N_plus if i != j) for j in S + S_tilde) == s)

    #Set number of routes
    #This may need changed and may improve computation
    mdl.addConstr(quicksum(x[0,j] for j in N) >= K)

    #capacity constraint
    mdl.addConstrs(u[i] - v[i] <= Q for i in N)
    mdl.addConstrs(u[i] - v[i] >= 0 for i in N)



    #MTZ for u
    mdl.addConstrs(u[i] - u[j] + Q * x[i,j] + (Q - d[i][0] - d[j][0]) * x[j,i] <= Q - d[j][0] for i in N for j in N if i != j)


    #for v
    mdl.addConstrs(v[i]-v[j]+Q*x[i,j]+(Q - d[i][1] - d[j][1])*x[j,i] <= Q - d[j][1] for i in N for j in N if i!=j)


    #for t 
    mdl.addConstrs(t[i]-t[j]+T*x[i,j]+(T-2)*x[j,i] <= T - 1 for i in N for j in N if j!=i)



    #t and w
    #mdl.addConstrs(t[i]-t[j] + (T+1)*w[i,j] <= T for i in N for j in N if j != i)
    mdl.addConstrs(t[i]-t[j] + (T+1)*w[i,j] + (T-1)*w[j,i] <= T for i in N for j in N if j != i)
    


    #w can at most use the same node once
    mdl.addConstrs(quicksum(w[i,j] for j in N if j != i) <= x[i,0] for i in N)
    mdl.addConstrs(quicksum(w[i,j] for i in N if i != j) <= x[0,j] for j in N)

    #set number of w_ij
    mdl.addConstr(quicksum(x[0,j] for j in N)-quicksum(quicksum(w[i,j] for i in N if i != j) for j in N) ==1)


    #set precedence constraint
    mdl.addConstrs(t[R[i]] <= t[S_tilde[i]] for i in range(len(R)))


    if lift == True:
        mdl.addConstrs(u[i] >= d[i][0] + quicksum(d[j][0] * x[j,i] for j in N if j != i) for i in N)
        mdl.addConstrs(v[i] >= d[i][1] + quicksum(d[j][1] * x[j,i] for j in N if j != i) for i in N)
        mdl.addConstrs(t[i] >= 1 + quicksum(x[j,i] for j in N if j != i) for i in N) # 


        mdl.addConstrs(v[i] <= Q - (Q - max([d[j][1] for j in d if j != i]) - d[i][1])*x[0,i] - quicksum(d[j][1]*x[i,j] for j in N if j != i) for i in N)



    ########################################################################
    ############################## valid ineq ##############################
    if val_eq == True:

        #All nodes from S_tilde can at first be visited at t = 2
        mdl.addConstrs(t[i] >= 2 for i in S_tilde)

        #if a storage is done, then v_i must be at most 1
        mdl.addConstrs(v[i] <= 1 for i in S + S_tilde)

        #first in new route must be 2 or higher
        mdl.addConstrs(t[j] - quicksum(w[i,j] for i in N if i !=j) >= 1 for j in N)

        #strengthening of the relaxation
        mdl.addConstrs(x[i,j] + x[j,i] <= 1 for i in N for j in N if i != j)



    ############################## set parameters ##############################
    mdl.setParam('TimeLimit', timelimit)

    
    ########################################################
    #            IMPLEMENT OF HEURISTIC                    #
    ########################################################

    if initiate == True:

        #print(f'initial: {initial}')
        start_x = []
        for route in initial:
            for i in range(len(route)-1):
                start_x.append((route[i], route[i+1]))
        
        # start_w = [] 
        # for i in range(len(initial) -1):
        #     start_w.append((initial[i][-2], initial[i+1][1]))
        
        ############################## Give initial solution ##############################
        init_x = {}
        for i in x:
            if i in start_x:
                init_x[i] = 1
            else:
                init_x[i] = 0


        for i in x:
            x[i].start = init_x[i]


    #with_sub = True
    if with_sub == True:
        mdl.Params.lazyConstraints = 1
        if initiate == True:
            for i in x:
                x[i].start = init_x[i]
        mdl.update()

        mdl._x = x
        mdl.optimize(sub_elim)

    else:
        mdl.optimize()


    mdl._x = x
    mdl._w = w
    mdl._t = t
    mdl._u = u
    mdl._v = v
    var = [x,w,t,u,v]
    return mdl, var



    

if __name__ == '__main__':
    def best_heuristic():
        NN_rand = Heur.multi_random(R, S, S_tilde, s, c, 1000)
        #get cost from NN_rand
        NN_rand_cost = Heur.calculate_cost(NN_rand, c)

        #get reduced
        reduced = Heur.with_reduce(R, S, S_tilde, s, c)[0]
        #get reduced cost
        reduced_cost = Heur.calculate_cost(reduced, c)

        if reduced_cost < NN_rand_cost:
            initial = reduced
        else:
            initial = NN_rand
        return initial


    timelimit = 60 #set the timelimit for the model

    lift = True #adds the extended lifts if true
    val_eq = True #adds extra polynomial inequalities if true
    initiate = True #adds initial solution if true
    with_sub = True #adds the Generalized sub-tour elimination if true


    instance = "inst_4_4_4.pkl" #choose instance

    #load instance
    with open(instance, 'rb') as f:
        R, S, S_tilde, N, N_plus, A, c, d, _, s = pkl.load(f)

    initial = best_heuristic() #gets the best performing heuristic


    #A heuristic needs to be imported or initiate needs to be set to False
    mdl, var = ASRS(R, S, S_tilde, N, N_plus, A, c, 2, s, d, timelimit, lift, val_eq, initial, with_sub)
    print(f'Start R: {R}')
    print(f'Start S: {S}')
    
    print('Objective value: ', mdl.objVal)
    print('Time: ', mdl.Runtime)
    #print the gap
    print('Gap: ', mdl.MIPGap)
