
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
    for i in quatdic:
        fig = plt.figure(figsize=plt.figaspect(0.5))
        for j in range(i.shape[0]):
            arr = np.asarray(quatdic[i][j])
            x, y, z = np.hsplit(arr, 3)
            T = mtri.Triangulation(x, y, quatertriangle)
            zf = z[T].mean(axis=1)
            mask = zf <= 0
            T.set_mask(mask)
            ax = fig.add_subplot(1, 2, 1, projection='3d')
            ax.plot_trisurf(T, z, cmap=plt.cm.CMRmap)


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
