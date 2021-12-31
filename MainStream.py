
from openpyxl import load_workbook
import numpy as np
from QuaterTriangle import QuaterTriangle3D
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import matplotlib.collections

wb = load_workbook(filename="./RawData/RawPointData.xlsx", data_only=True)
RADIUS = 1000

if __name__ == '__main__':

    quat = QuaterTriangle3D(wb, RADIUS)
    quatdic = quat.exportStratumsSheet()
    quatertriangle = quat.exportQuaterTriangle()
    colol = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'w']

    fig = plt.figure(figsize=plt.figaspect(3))
    ax = fig.add_subplot(1, 2, 1, projection='3d')

    for cl, item in enumerate(quatdic):

        for arr in quatdic[item]:

            x, y, z = np.hsplit(arr, 3)
            x = x.reshape(x.size)
            y = y.reshape(y.size)
            z = z.reshape(z.size)
            T = mtri.Triangulation(x, y, quatertriangle)
            newvar = z[T.triangles]
            newvar2 = newvar[:, 0] * newvar[:, 1]*newvar[:, 2]
            mask = newvar2 <= 0
            T.set_mask(mask)

            ax.plot_trisurf(T, z, color=colol[cl % 8])
            # ax.plot_trisurf(T, z, cmap=plt.cm.CMRmap)

        plt.show()

"""

x = []
y = []
z = []
triangle = []

T = mtri.Triangulation(x, y, triangle)
zf = z[T].mean(axis=1)
mask = (zf == None)
T.set_mask(mask)
# then do what u want

"""
