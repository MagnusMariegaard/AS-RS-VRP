import Data2index as Data
import copy 
import random
import math
import big_o

def NN_open(current, open_loc, c):
        nearest = min(open_loc, key=lambda i: c[(current, i)])
        current = nearest
        open_loc.remove(current)

        return current, open_loc


#returns nearest retrieval location
#Adds the location that opens from retrieval to open_loc
#delets the location from S_tilde
def NN_ret(current, R, c, S_tilde, open_loc):
    #print('R3: ',R)
    #finds the nearest location from current location
    nearest = min(R, key=lambda i: c[(current, i)])

    #sets curennt location to nearest location
    current = nearest

    #find the new location open made from the retrieval
    new_open = S_tilde[R.index(current)]

    #remove this location from S_tilde
    S_tilde.remove(new_open)

    #add the new open to the set of open locations
    open_loc.append(new_open)

    #Remove the current from R
    R.remove(current)
    return current, R, S_tilde, open_loc

def NN(R,S,S_tilde,s,c, routes):
    R = copy.deepcopy(R)
    S_tilde = copy.deepcopy(S_tilde)
    S = copy.deepcopy(S)

    stopper = 0
    open_loc = S
    S_vis = []
    route = []
    while len(R) > 0 or len(S_vis) < s:
        #emergency break
        stopper += 1
        if stopper == 100:
            break

        route = [0]
        current = 0

        if len(S_vis) < s:            

            current, open_loc = NN_open(current, open_loc, c)
            route.append(current)
            S_vis.append(current)

            if len(R) > 0:

                current, R, S_tilde, open_loc = NN_ret(current, R, c, S_tilde, open_loc)
                route.append(current)

                if len(S_vis) < s:

                    current, open_loc = NN_open(current, open_loc, c)
                    route.append(current)
                    S_vis.append(current)

                    if len(R) > 0:
                        current, R, S_tilde, open_loc = NN_ret(current, R, c, S_tilde, open_loc)
                        route.append(current)
                        route.append(0)
                        routes.append(route)
                    
                    else:

                        route.append(0)
                        routes.append(route)
                        
                
                elif len(R) > 0:

                    current, R, S_tilde, open_loc = NN_ret(current, R, c, S_tilde, open_loc)
                    route.append(current)
                    route.append(0)
                    routes.append(route)
                
                else:
                    route.append(0)
                    routes.append(route)

            elif len(S_vis) < s:
                current, open_loc = NN_open(current, open_loc, c)
                S_vis.append(current)
                route.append(current)
                route.append(0)
                routes.append(route)
            
            else:

                route.append(0)
                routes.append(route)
        
        elif len(R) > 0:

            current, R, S_tilde, open_loc = NN_ret(current, R, c, S_tilde, open_loc)
            route.append(current)

            if len(R) > 0:

                current, R, S_tilde, open_loc = NN_ret(current, R, c, S_tilde, open_loc)
                route.append(current)
                route.append(0)
                routes.append(route)
            
            else:

                route.append(0)
                routes.append(route)

        else:
            print("mistake somewhere")
    
    return routes, S_vis, R
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################
#Reduces the number of retrievals if there are more retrievals needed than storages
def reduce_NN(R, S, S_tilde, s, c):

    r_needed = math.ceil(len(R)/2) - math.ceil(s/2)

    R = copy.deepcopy(R)
    S_tilde = copy.deepcopy(S_tilde)
    open_loc = S = copy.deepcopy(S)

    routes = []
    for i in range(r_needed):
        route = [0]
        current = 0
        #use NN_ret
        for i in range(2):
            current, R, S_tilde, open_loc = NN_ret(current, R, c, S_tilde, open_loc)
            route.append(current)
        route.append(0)
        routes.append(route)
    return routes, R, S, S_tilde

def rand_open(open_loc):
    nearest = random.choice(open_loc)
    current = nearest
    open_loc.remove(current)

    return current, open_loc

def NN_rand_start(R,S,S_tilde,s,c, routes):
    R = copy.deepcopy(R)
    S_tilde = copy.deepcopy(S_tilde)
    S = copy.deepcopy(S)

    stopper = 0
    open_loc = S
    S_vis = []
    route = []
    while len(R) > 0 or len(S_vis) < s:
        #emergency break
        stopper += 1
        if stopper == 100:
            break

        route = [0]
        current = 0

        if len(S_vis) < s:            

            current, open_loc = rand_open(open_loc)
            route.append(current)
            S_vis.append(current)

            if len(R) > 0:

                current, R, S_tilde, open_loc = NN_ret(current, R, c, S_tilde, open_loc)
                route.append(current)

                if len(S_vis) < s:

                    current, open_loc = NN_open(current, open_loc, c)
                    route.append(current)
                    S_vis.append(current)

                    if len(R) > 0:
                        current, R, S_tilde, open_loc = NN_ret(current, R, c, S_tilde, open_loc)
                        route.append(current)
                        route.append(0)
                        routes.append(route)
                    
                    else:

                        route.append(0)
                        routes.append(route)
                        
                
                elif len(R) > 0:

                    current, R, S_tilde, open_loc = NN_ret(current, R, c, S_tilde, open_loc)
                    route.append(current)
                    route.append(0)
                    routes.append(route)
                
                else:
                    route.append(0)
                    routes.append(route)

            elif len(S_vis) < s:
                current, open_loc = NN_open(current, open_loc, c)
                S_vis.append(current)
                route.append(current)
                route.append(0)
                routes.append(route)
            
            else:

                route.append(0)
                routes.append(route)
        
        elif len(R) > 0: #Uses the non stochastic method since all routes start from a storage when using the reduced version

            current, R, S_tilde, open_loc = NN_ret(current, R, c, S_tilde, open_loc)
            route.append(current)

            if len(R) > 0:

                current, R, S_tilde, open_loc = NN_ret(current, R, c, S_tilde, open_loc)
                route.append(current)
                route.append(0)
                routes.append(route)
            
            else:

                route.append(0)
                routes.append(route)

        else:
            print("mistake somewhere")
    
    return routes, S_vis, R



# def random_reduce(R, S, S_tilde, s):
#     r_needed = math.ceil(len(R)/2) - math.ceil(s/2)
#     R = copy.deepcopy(R)
#     S_tilde = copy.deepcopy(S_tilde)
#     open_loc = S = copy.deepcopy(S)

#     routes = []
#     for i in range(r_needed):
#         route = [0]
#         current = 0
#         #introduce some randomness
#         for i in range(2):
#             current = random.choice(R)
#             #add new open location
#             new_open = S_tilde[R.index(current)]
#             S_tilde.remove(new_open)
#             open_loc.append(new_open)
#             #remove current from R
#             R.remove(current)
#             route.append(current)
#         route.append(0)
#         routes.append(route)
#     return routes, R, S, S_tilde

def random_reduce(R, S, S_tilde, s, c):
    r_needed = math.ceil(len(R)/2) - math.ceil(s/2)
    R = copy.deepcopy(R)
    S_tilde = copy.deepcopy(S_tilde)
    open_loc = S = copy.deepcopy(S)
    #print("helooooooooooooooooooooooooo")
    routes = []
    for i in range(r_needed):
        route = [0]
        current = 0
        #introduce some randomness
        #print('R1: ',R)
        current = random.choice(R)
        #add new open location
        new_open = S_tilde[R.index(current)]
        S_tilde.remove(new_open)
        open_loc.append(new_open)
        #remove current from R
        R.remove(current)
        route.append(current)
        #print('R2: ',R)
        #print('current: ',current)
        #from current find the nearest retrieval
        current, R, S_tilde, open_loc = NN_ret(current, R, c, S_tilde, open_loc)

        route.append(current)

        route.append(0)
        routes.append(route)
    return routes, R, S, S_tilde

def with_random(R, S, S_tilde, s, c):
    
    
    routes, R, S, S_tilde = random_reduce(R, S, S_tilde, s, c)
    #print('Here here here: ', len(c))
    #routes, S_vis, R = NN(R, S, S_tilde, s, c, routes)
    routes, S_vis, R = NN_rand_start(R,S,S_tilde,s,c, routes)
    return routes, S_vis, R

# for i in range(5):
#     routes1 = with_random(R, S, S_tilde, s, c)[0]
#     print(calculate_cost(routes1, c))

def multi_random(R, S, S_tilde, s, c, n):
    best_value = 999999
    best_routes = []
    for i in range(n):
        candidate = with_random(R, S, S_tilde, s, c)[0]
        candidate_value = calculate_cost(candidate, c)
        if candidate_value < best_value:
            best_value = candidate_value
            best_routes = candidate

    return best_routes



def with_reduce(R, S, S_tilde, s, c):
    routes, R, S, S_tilde = reduce_NN(R, S, S_tilde, s, c)
    routes, S_vis, R = NN(R, S, S_tilde, s, c, routes)
    return routes, S_vis, R


def calculate_cost(routes, c):
    cost = 0
    for route in routes:
        for i in range(len(route)-1):
            cost += c[(route[i], route[i+1])]
    return cost

def test_of_3(R, S, S_tilde, s, c):
    result = {'total': 0, 'single_random': 0, 'multi_random': 0, 'with_reduce': 0, 'tie': 0}
    for i in range(1000):
        r1 = with_random(R, S, S_tilde, s, c)[0]
        r2 = with_reduce(R, S, S_tilde, s, c)[0]
        r3 = multi_random(R, S, S_tilde, s, c, 1000)

        c1 = calculate_cost(r1, c)
        c2 = calculate_cost(r2, c)
        c3 = calculate_cost(r3, c)

        if c1 < c2 and c1 < c3:
            result['single_random'] += 1
            result['total'] += 1
        elif c2 < c1 and c2 < c3:
            result['with_reduce'] += 1
            result['total'] += 1
        elif c3 < c1 and c3 < c2:
            result['multi_random'] += 1
            result['total'] += 1
        else:
            result['tie'] += 1
            result['total'] += 1

    print(result)

if __name__ == '__main__':
    #instance size
    n = 40
    m = 10
    n_len = 1
    m_len = 4
    r = 395
    open = 5  #also seen as open storages
    s = 396 #this is the number of storages needed

    #now is perftimer
    
    R, S, S_tilde, N, N_plus, A, c, d, _ = Data.combine_data(n,m,n_len,m_len,r,open)
    
    #get cost for NN
    NN_routs = NN(R, S, S_tilde, s, c, routes = [])[0]
    print('NN routes: ', NN_routs)
    NN_cost = calculate_cost(NN_routs, c)

    

    #run multi random and get cost
    multi_random_routs = multi_random(R, S, S_tilde, s, c, 1000)
    multi_random_cost = calculate_cost(multi_random_routs, c)

    print('multi random cost: ', multi_random_cost)
