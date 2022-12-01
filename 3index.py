import Data2index as Data
from gurobipy import * 
import math
import Heuristics as Near



def ASRS(R, S, S_tilde, N, N_plus, A, c, Q, s, d, timelimit, lift, val_eq):

    #add (0,0): 0 to c
    c[(0,0)] = 0

    print(f'R: {R}')
    print(f'S_tilde: {S_tilde}')
    print(f'S: {S}')

    #[x+1 if x >= 45 else x+5 for x in xs]
    q = {i: -1 if d[i][0] == 1 else 1 for i in d}
    #q = {i: 1 if d[i][0] == 1 else -1 for i in d}

    #change q 

    print(f'q: {q}')
    A.append((0,0))
    
    K = len(Data.create_K(len(R), s))
    K = [i for i in range(1, K+1)]

    T = 4


    mdl = Model('ASRS')


    #add binary variable x
    x = {}
    for i,j in A:
        for r in K:
            x[i,j,r] = mdl.addVar(vtype= GRB.BINARY, name='x_%d_%d' % (i,j))
    print('N', len(N_plus))
    print('len(K)', len(K))
    print('x', len(x))

    #add variable u
    u = {}
    for i in N:
        u[i] = mdl.addVar(lb = 1, ub = Q, vtype=GRB.CONTINUOUS, name='u_%d' % (i))
    
    u0 = {}
    for r in K:
        u0[r] = mdl.addVar(lb = 0, ub = Q, vtype=GRB.CONTINUOUS, name='u0_%d' % (r))
    
    t = {}
    for i in N:
        t[i] = mdl.addVar(lb = 1, ub= T, vtype=GRB.CONTINUOUS, name='t%d' % (i))
    

    #set objective
    mdl.setObjective(quicksum(quicksum(c[(i,j)] * x[i,j,r] for i, j in A) for r in K), GRB.MINIMIZE)


    #start from 0
    mdl.addConstrs(quicksum(x[0,i,r] for i in N_plus) == 1 for r in K)

    #degree constraint
    mdl.addConstrs(quicksum(x[i,h,r] for i in N_plus if i != h) == quicksum(x[h,j,r] for j in N_plus if j != h) for h in N for r in K)

    #all retrievals
    mdl.addConstrs(quicksum(quicksum(x[i,j,r] for j in N_plus if j != i) for r in K) == 1 for i in R)

    #Not all storages
    mdl.addConstr(quicksum(quicksum(quicksum(x[i,j,r] for j in N_plus if j != i) for r in K) for i in S + S_tilde) == s)

    #initial capacity
    mdl.addConstrs(u0[r] == - quicksum(quicksum(x[i,j,r] * q[j] for i in N_plus if i != j) for j in S + S_tilde) for r in K)

    #MTZ for u
    mdl.addConstrs(u[i] - u[j] + Q * x[i,j,r] + (Q - q[i]-q[j])*x[j,i,r] <= Q - q[j] for i in N for j in N if j != i for r in K)

    #Capacity for initial
    mdl.addConstrs(u[i] >= quicksum(x[0,i,r]*(u0[r]+q[i]) for r in K) for i in N)
    # mdl.addConstrs(quicksum(quicksum(x[i,j,r] for j in N_plus if j != i) for i in R) <= 2 for r in K)
    # mdl.addConstrs(quicksum(quicksum(x[i,j,r] for j in N_plus if j != i) for i in S+S_tilde) <= 2 for r in K)


    #subtour eliminations t
    mdl.addConstrs(t[i] - t[j] + T * x[i,j,r] + (T - 2) * x[j,i,r] <= T - 1 for i in N for j in N if j != i for r in K)

    #precedence constraint
    mdl.addConstrs( t[R[i]] + quicksum(quicksum(x[R[i],j,r]*2*r for j in N_plus if j != R[i]) for r in K) <= 
                    t[S_tilde[i]] + quicksum(quicksum(x[S_tilde[i],j,r]*2*r for j in N_plus if j != S_tilde[i]) for r in K)+ 1000*(1-quicksum(quicksum(x[S_tilde[i],j,r] for j in N_plus if j != S_tilde[i]) for r in K)) for i in range(len(R)))


    if lift == True:
        mdl.addConstrs(u[i] >= q[i] + quicksum(q[i] * x[j,i,r] for j in N if j != i) for i in N for r in K)
        mdl.addConstrs(t[i] >= 1 + quicksum(x[j,i,r] for j in N if j != i) for i in N for r in K) # 


        #mdl.addConstrs(u[i] <= Q - (Q - max([q[j] for j in d if j != i]) - q[i])*x[0,i,r] - quicksum(q[j]*x[i,j,r] for j in N if j != i) for i in N for r in K)
        mdl.addConstrs(t[i] <= T - (T -2)*x[0,i,r] - quicksum(x[i,j,r] for j in N if j != i) for i in N for r in K) #


    ######################################################################################################################################################
    ############################## valid ineq ##############################
    if val_eq == True:

        #strengthening of the relaxation
        mdl.addConstrs(x[i,j,r] + x[j,i,r] <= 1 for i in N for j in N if i != j for r in K)

        #If a retrieval is done, then u_i must be at least 1
        #mdl.addConstrs(u[i] >= 1 for i in R)



    ############################## set parameters ##############################
    mdl.setParam('TimeLimit', timelimit)
    mdl.setParam('LiftProjectCuts', 0)
    #set heuristics to 0
    #mdl.setParam('Heuristics', 0)


    ########################################################
    #            IMPLEMENT OF HEURISTIC                    #
    ########################################################
    initiate = False
    if initiate == True:
        initial = Near.NN(R, S, S_tilde, s, c, routes = [])[0]

        print(f'initial: {initial}')
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
        
        #set initial solution in gurobi
        #use the gurobi start attribute
        for i in x:
            x[i].start = init_x[i]
        # for i in w:
        #     w[i].start = init_w[i]

    mdl.optimize()

    mdl._x = x
    #mdl._w = w
    mdl._t = t
    mdl._u = u
    #mdl._v = v
    mdl._u0 = u0
    var = [x,t,u, u0]
    return mdl, var



    

if __name__ == '__main__':
    lift = True
    val_eq = False

    import pickle as pkl

    instance = 'inst_4_4_4.pkl' 
    #open the pickle file from instance
    with open(instance, 'rb') as f:
        R, S, S_tilde, N, N_plus, A, c, d, _, s = pkl.load(f)
    
    timelimit = 60*3


    print(f'Start R: {R}')
    print(f'Start S: {S}')

    mdl, var = ASRS(R, S, S_tilde, N, N_plus, A, c, 2, s, d, timelimit, lift, val_eq)
    print(f'Start R: {R}')
    print(f'Start S: {S}')
    
    print('Objective value: ', mdl.objVal)
    print('Time: ', mdl.Runtime)
    #print the gap
    print('Gap: ', mdl.MIPGap)