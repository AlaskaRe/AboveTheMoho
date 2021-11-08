import numpy as np
from numpy.lib.twodim_base import tri

Tri = (4, 1, 2)
a = np.array(Tri, dtype=np.int16)
n = np.transpose(a)
b = np.matmul(n, [1, 1])

x = b[0]
y = b[1]
z = b[2]
print(x)

print(y)

print(z)
