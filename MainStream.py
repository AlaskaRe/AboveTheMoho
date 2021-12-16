from math import radians
from openpyxl import load_workbook
import numpy as np
from delaunay2D import Delaunay2D
import matplotlib.pyplot as plt
import matplotlib.tri
import matplotlib.collections

wb = load_workbook(filename="./RawData/RawPointData.xlsx", data_only=True)
wksht_pt = wb["POSTION"]
wksht_lib = wb["LAYER_LIBARY"]
wksht_args = wb["POINT_ARGS"]
RADIUS = 1000

if __name__ == '__main__':
    # 1.Read the data from the excel, and generate the Point and Stratums_lib;
    Point = {}
    Stratums_lib = []

    # 1.1 Generate the Stratums_lib;
    # read the worksheet"LAYER_LIBARY", get the information of the layers
    for row in wksht_lib.iter_rows(min_row=2, max_row=20, max_col=3):

        if row[0].value != None:

            T = (row[0].value, row[1].value)
            Stratums_lib.append(T)

    # 1.2 Generate the Point;
    # Read the worksheet "POSTION",get the point data.
    for r in wksht_pt.iter_rows(min_row=2, max_col=3):

        if r[0].value == None:
            break

        Point[r[0].value, r[1].value] = []

    # Read the worksheet "POINT_ARGS", get the stratums of each point.
    for r in wksht_args.iter_rows(min_row=2, max_col=13):

        if r[0].value == None:
            break

        else:
            # Read the row and get the value of every stratum for each point.
            kywd = (r[2].value, r[3].value)
            da = [r[7].value, r[8].value, r[11].value]
            stratumslist = Point[kywd]
            stratumslist.append(da)

    # 2. Generate the delaunay TIN

    seeds = np.asarray(list(Point.keys()))
    center = np.mean(seeds, axis=0)
    dt = Delaunay2D(center, RADIUS)

    for s in seeds:
        dt.addPoint(s)

    # Create a demo of the TIN

    # Create a plot with matplotlib.pyplot
    fig, ax = plt.subplots()
    ax.margins(0.1)
    ax.set_aspect('equal')
    plt.axis([center[0]-RADIUS, center[0] + RADIUS,
             center[1]-RADIUS, center[1]+RADIUS])

    # Plot our Delaunay triangulation (plot in blue)
    cx, cy = zip(*seeds)
    dt_tris = dt.exportTriangles()
    ax.triplot(matplotlib.tri.Triangulation(cx, cy, dt_tris), 'bo--')

    plt.show()
