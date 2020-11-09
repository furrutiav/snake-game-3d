# coding=utf-8
"""
Daniel Calderon, CC3501, 2019-1
Finite Differences for Partial Differential Equations

Solving the Laplace equation in 2D with Dirichlet border
conditions over a square domain.
"""

import numpy as np
import matplotlib.pyplot as mpl

# Problem setup
H = 4
W = 3
h = 0.1

# Boundary Dirichlet Conditions:
TOP = 20
BOTTOM = 0
LEFT = 5
RIGHT = 15

# Number of unknowns
# left, bottom and top sides are known (Dirichlet condition)
# right side is unknown (Neumann condition)
nh = int(W / h) - 1
nv = int(H / h) - 1

# In this case, the domain is just a rectangle
N = nh * nv

# We define a function to convert the indices from i,j to k and viceversa
# i,j indexes the discrete domain in 2D.
# k parametrize those i,j, this way we can tidy the unknowns
# in a column vector and use the standard algebra

def getK(i,j):
    return j * nh + i

def getIJ(k):
    i = k % nh
    j = k // nh
    return (i, j)

"""
# This code is useful to debug the indexation functions above
print("="*10)
print(getK(0,0), getIJ(0))
print(getK(1,0), getIJ(1))
print(getK(0,1), getIJ(2))
print(getK(1,1), getIJ(3))
print("="*10)

import sys
sys.exit(0)
"""

# In this matrix we will write all the coefficients of the unknowns
A = np.zeros((N,N))

# In this vector we will write all the right side of the equations
b = np.zeros((N,))

# Note: To write an equation is equivalent to write a row in the matrix system

# We iterate over each point inside the domain
# Each point has an equation associated
# The equation is different depending on the point location inside the domain
for i in range(0, nh):
    for j in range(0, nv):

        # We will write the equation associated with row k
        k = getK(i,j)

        # We obtain indices of the other coefficients
        k_up = getK(i, j+1)
        k_down = getK(i, j-1)
        k_left = getK(i-1, j)
        k_right = getK(i+1, j)

        # Depending on the location of the point, the equation is different
        # Interior
        if 1 <= i and i <= nh - 2 and 1 <= j and j <= nv - 2:
            A[k, k_up] = 1
            A[k, k_down] = 1
            A[k, k_left] = 1
            A[k, k_right] = 1
            A[k, k] = -4
            b[k] = 0
        
        # left side
        elif i == 0 and 1 <= j and j <= nv - 2:
            A[k, k_up] = 1
            A[k, k_down] = 1
            A[k, k_right] = 1
            A[k, k] = -4
            b[k] = -LEFT
        
        # right side
        elif i == nh - 1 and 1 <= j and j <= nv - 2:
            A[k, k_up] = 1
            A[k, k_down] = 1
            A[k, k_left] = 1
            A[k, k] = -4
            b[k] = -RIGHT
        
        # bottom side
        elif 1 <= i and i <= nh - 2 and j == 0:
            A[k, k_up] = 1
            A[k, k_left] = 1
            A[k, k_right] = 1
            A[k, k] = -4
            b[k] = -BOTTOM
        
        # top side
        elif 1 <= i and i <= nh - 2 and j == nv - 1:
            A[k, k_down] = 1
            A[k, k_left] = 1
            A[k, k_right] = 1
            A[k, k] = -4
            b[k] = -TOP

        # corner lower left
        elif (i, j) == (0, 0):
            A[k, k_up] = 1
            A[k, k_right] = 1
            A[k, k] = -4
            b[k] = -BOTTOM - LEFT

        # corner lower right
        elif (i, j) == (nh - 1, 0):
            A[k, k_up] = 1
            A[k, k_left] = 1
            A[k, k] = -4
            b[k] = -BOTTOM - RIGHT

        # corner upper left
        elif (i, j) == (0, nv - 1):
            A[k, k_down] = 1
            A[k, k_right] = 1
            A[k, k] = -4
            b[k] = -TOP - LEFT

        # corner upper right
        elif (i, j) == (nh - 1, nv - 1):
            A[k, k_down] = 1
            A[k, k_left] = 1
            A[k, k] = -4
            b[k] = -TOP - RIGHT

        else:
            print("Point (" + str(i) + ", " + str(j) + ") missed!")
            print("Associated point index is " + str(k))
            raise Exception()


# A quick view of a sparse matrix
#mpl.spy(A)

# Solving our system
x = np.linalg.solve(A, b)

# Now we return our solution to the 2d discrete domain
# In this matrix we will store the solution in the 2d domain
u = np.zeros((nh,nv))

for k in range(0, N):
    i,j = getIJ(k)
    u[i,j] = x[k]

# Adding the borders, as they have known values
ub = np.zeros((nh + 2, nv + 2))
ub[1:nh + 1, 1:nv + 1] = u[:,:]

# Dirichlet boundary condition
# top 
ub[0:nh + 2, nv + 1] = TOP
# bottom 
ub[0:nh + 2, 0] = BOTTOM
# left
ub[0, 1:nv + 1] = LEFT
# right
ub[nh + 1, 1:nv + 1] = RIGHT

# this visualization locates the (0,0) at the lower left corner
# given all the references used in this example.
fig, ax = mpl.subplots(1,1)
pcm = ax.pcolormesh(ub.T, cmap='RdBu_r')
fig.colorbar(pcm)
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_title('Laplace equation solution')
ax.set_aspect('equal', 'datalim')

# Note:
# imshow is also valid but it uses another coordinate system,
# a data transformation is required
#ax.imshow(ub.T)
mpl.show()