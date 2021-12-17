import numpy as np
from delaunay2D import Delaunay2D


class QuaterTriangle3D:

    def __init__(self, wbook, rad=9999):

        # 1.Read the data from the excel, and generate the Point and Stratums_lib;
        self.wksht_pt = wbook["POSTION"]
        self.wksht_lib = wbook["LAYER_LIBARY"]
        self.wksht_args = wbook["POINT_ARGS"]

        self.Point = {}
        self.Stratums_lib = []

        # 1.1 Generate the Stratums_lib;
        # read the worksheet"LAYER_LIBARY", get the information of the layers
        for row in self.wksht_lib.iter_rows(min_row=2, max_row=20, max_col=3):

            if row[0].value != None:

                T = (row[0].value, row[1].value)
                self.Stratums_lib.append(T)

        # 1.2 Generate the Point;
        # Read the worksheet "POSTION",get the point data.
        for r in self.wksht_pt.iter_rows(min_row=2, max_col=3):

            if r[0].value == None:
                break

            self.Point[r[0].value, r[1].value] = []

        # Read the worksheet "POINT_ARGS", get the stratums of each point.
        for r in self.wksht_args.iter_rows(min_row=2, max_col=13):

            if r[0].value == None:
                break
            else:
                # Read the row and get the value of every stratum for each point.
                kywd = (r[2].value, r[3].value)
                da = [r[7].value, r[8].value, r[11].value]
                stratumslist = self.Point[kywd]
                stratumslist.append(da)

        # 2. Generate the delaunay TIN

        seeds = np.asarray(list(self.Point.keys()))
        center = np.mean(seeds, axis=0)
        dt = Delaunay2D(center, rad)

        for s in seeds:
            dt.addPoint(s)

        # 3. Generate the Quater Triangles net
        self.edges = dt.exportEdges()
        self.pointcoord = dt.exportSequence()

        self.edgeToMidPoint = {}
        self.midPoint = {}

        # 3.1 EdgeToMidPoint

        for e in self.edges:
            self.edgeToMidPoint[e] = self.pointcoord[e[0]
                                                     ] + self.pointcoord[e[1]]

        # 3.2 MidPoint
        for key in self.edgeToMidPoint.keys():
            listA = self.Point[self.pointcoord[key[0]]]
            listB = self.Point[self.pointcoord[key[1]]]

            self.midPoint[key] = self.generateMidPointList(listA, listB)

    def generateMidPointList(self, a, b):
        """这他喵的是个迭代函数，惊讶出中文，研究研究
        """
        idxA, idxB = 0, 0

        for i in self.Stratums_lib:
            contA, contB = [], []
            contBetA, contBetB = [], []
            for x in range(idxA, len(a)):
                if a[x][2] == i[0]:
                    contA.append(a[x])
                    contBetA.append(a[idxA:x])
                    idxA = x+1

            for y in range(idxB, len(b)):
                if b[y][2] == i[0]:
                    contB.append(b[y])
                    contBetB.append(b[idxB:y])
                    idxB = y+1
