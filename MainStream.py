
from openpyxl import load_workbook
import numpy as np
from QuaterTriangle import QuaterTriangle3D
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import matplotlib.collections

wb = load_workbook(filename="./RawData/RawPointData.xlsx", data_only=True)
RADIUS = 1000

if __name__ == '__main__':

    qt = QuaterTriangle3D(wb, RADIUS)

x = []
y = []
z = []
triangle = []

T = mtri.Triangulation(x, y, triangle)
zf = z[T].mean(axis=1)
mask = (zf == None)
T.set_mask(mask)
# then do what u want
