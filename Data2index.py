import numpy as np
rnd = np.random


rnd.seed(3)

#n and m are the number of locations in the horizontal and vertical direction
#n_len and m_len are the length of the each location
def create_asrs(n, m, n_len, m_len):
    #n and m are quantities
    #locations are all locations from combinations of n and m plus a zero for the IO
    locations = list(range(0, n*m + 1))
    xc = [0] + [n_len * i for j in range(m) for i in range(1, n+1)]
    yc = [0] + [m_len * j for j in range(n) for i in range(1, n+1)]
    return locations, xc, yc

#create R, S and S_tilde
#this is giving lists of size r and s with location as a list
#also gives the coordinates for all lists
def get_RSS(r, s, locations, xc, yc):
    locations.remove(0)
    R = np.random.choice(locations, r, replace = False).tolist()
    S = np.random.choice([i for i in locations if i not in R], s, replace = False).tolist()
    S_tilde = list(range(locations[-1]+1, locations[-1]+1+r))

    R_coor = {i: (xc[i], yc[i]) for i in R}
    S_coor = {i: (xc[i], yc[i]) for i in S}
    S_tilde_coor = {S_tilde[i]: (xc[R[i]], yc[R[i]]) for i in range(len(R))}
    coordinates = {0: (0,0)} | R_coor | S_coor | S_tilde_coor
    return R, S, S_tilde, coordinates

def get_N(R,S,S_t):
    N = R + S + S_t
    N_plus = [0] + N 
    return N, N_plus

def get_A(N_plus):
    A = [(i,j) for i in N_plus for j in N_plus if i != j]
    return A

def get_cost(A, coor):
    c = {i: max(abs(coor[i[0]][0] - coor[i[1]][0]), abs(coor[i[0]][1] - coor[i[1]][1])) for i in A}
    return c

def create_K(r,s):
    n = [int(np.ceil(r/2)), int(np.ceil(s/2))]
    K = list(range(1, max(n) + 1))
    return K

def create_d(R, S, S_tilde):
    dR = {i: 1 for i in R}
    dS = {i: -1 for i in S + S_tilde}
    foo = dR | dS
    #need to change d from a dict of {key, value+-1} to {key, (u, v)}
    # if value = -1 -> u = 1, v = 0 
    # if value = 1 -> u = 0, v = 1
    d = {}
    for i in foo:
        if foo[i] == 1:
            d[i] = (0,1)
        elif foo[i] == -1:
            d[i] = (1,0)
        else:
            print('mistake: ', i)
    return d

#the as/rs rack is nxm openings with n_len and m_len as the dimensions for each spot
#r is the number of retrievals
#s is the number of open locations NOT the actual number of storages needed
def combine_data(n, m, n_len, m_len, r, s):
    locations, xc, yc = create_asrs(n,m,n_len,m_len)
    R, S, S_tilde, coordinates = get_RSS(r, s, locations, xc, yc)
    N, N_plus = get_N(R,S,S_tilde)
    A = get_A(N_plus)
    c = get_cost(A, coordinates)
    d = create_d(R,S,S_tilde)


    return R, S, S_tilde, N, N_plus, A, c, d, coordinates

if __name__ == '__main__':
    R, S, S_tilde, N, N_plus, A, c, d, coor = combine_data(5,5,1,1,2,2)
    print(R)
    print(d)