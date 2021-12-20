import numpy as np
from delaunay2D import Delaunay2D
import copy


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
                self.Stratums_lib.extend(T)

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
                da = (r[7].value, r[8].value, r[11].value)
                stratumslist = self.Point[kywd]
                stratumslist.extend(da)

        # 2. Generate the delaunay TIN
        seeds = np.asarray(list(self.Point.keys()))
        center = np.mean(seeds, axis=0)
        dt = Delaunay2D(center, rad)

        for s in seeds:
            dt.addPoint(s)

        # 3. Generate the Quater Triangles net
        self.edges = dt.exportEdges()
        self.pointSequence = dt.exportSequence()
        self.extendedSq = copy.deepcopy(self.pointSequence)

        self.edgeToMidPoint = {}
        self.midPoint = {}
        self.quaterTriangles = []

        # 3.1 EdgeToMidPoint

        for e in self.edges:
            self.edgeToMidPoint[e] = self.pointSequence[e[0]
                                                        ] + self.pointSequence[e[1]]

        # 3.2 MidPoint
        for key in self.edgeToMidPoint.keys():
            listA = self.Point[self. pointSequence[key[0]]]
            listB = self.Point[self. pointSequence[key[1]]]

            self.midPoint[key] = self.generateMidPointList(listA, listB, 0)

        # 3.3 Extended sequence
        # Using the extend method built in list, that's not a deepcopy
        self.extendedSq.extend(self.edgeToMidPoint.values())

        # 3.4 QuaterTriangles

    def generateMidPointList(self, a, b, startpoint):
        """This is an iterate function, which constructed not very perfect, but can be deployed in most situations.
        And further more, maybe the thread method should be used to achieve the goal.
        """
        idxA, idxB = 0, 0
        c = []

        # A great error has not been into consideration, to be contributed...
        # WHAT SHOULD TO DO WHEN THE INDEX IS OUT OF THE RANGE.
        # ALL IN ALL, this method is based on the absolute correct data of the stratums, and the algorithm I made here is not the same as what happened in nature.
        # But, with more correct data and more powerful mathematic and computer science tool, we may could get the true information of the form of the all kinds of stratums.
        for i in range(startpoint, len(self.Stratums_lib)):
            contA, contB = [], []
            contBetA, contBetB = [], []
            CutFromA, CutFromB = [], []

            contBetA = copy.deepcopy(a[idxA:len(a)])
            for x in range(idxA, len(a)):
                if a[x][2] == self.Stratums_lib[i][0]:
                    contA.extend(a[x])
                    idxA = x+1
            try:
                remainderA = copy.deepcopy(a[idxA:len(a)])
            except IndexError:
                pass
            contBetA.remove(remainderA)
            for valA in contA:
                try:
                    CutFromA = copy.deepcopy(contBetA)
                    contBetA.remove(valA)
                except ValueError:
                    pass

            contBetB = copy.deepcopy(b[idxB:len(b)])
            for y in range(idxB, len(b)):
                if b[y][2] == self.Stratums_lib[i][0]:
                    contB.extend(b[y])
                    idxB = y+1
            try:
                remainderB = copy.deepcopy(b[idxB:len(b)])
            except IndexError:
                pass
            contBetB.remove(remainderB)
            for valB in contB:
                try:
                    CutFromB = copy.deepcopy(contBetB)
                    contBetB.remove(valB)
                except ValueError:
                    pass

            # For convience, I take contA as a, contBetA as b, contB as c, contBetB as d. 1 means not null, 0 means null.
            # If b=0, it represents that a only has one element, so does the c and d.So where is the data check process?!
            # case1. break the loop and raise the error
            if (contA == [] and contBetA != []) or (contB == [] and contBetB != []):
                # that means the data are not right, error should be raised, but here I just ignore this data.
                return c

            # case2. (a=1, b = 0/1) and (c = 0/1, d = 0)
            elif contA != [] and contBetB == []:
                if contB == []:
                    try:
                        top = (contA[0][0] + b[idxB][0])/2
                        bottom = (contA[-1][1] + b[idxB][0])/2
                    except IndexError:
                        top = (contA[0][0] + b[-1][1])/2
                        bottom = (contA[-1][1] + b[-1][1])/2
                    c.extend((top, bottom, a[x][2]))
                else:
                    top = (contA[0][0] + contB[0][0])/2
                    bottom = (contA[-1][1] + contB[0][1])/2
                    c.extend(top, bottom, a[x][2])
                if contBetA != []:
                    l = len(contBetA)+1
                    thickness = c[-1][0] - c[-1][1]
                    piecethk = thickness/l
                    for acc in len(contBetA):
                        newlayer = (top - acc * piecethk)
                        c.extend((newlayer, newlayer, contBetA[acc][2]))

            # case3. (a = 1, b = 1) and (c = 1, d = 1)
            elif (contA != [] and contBetA != []) and (contB != [] and contBetB != []):
                # More complicated case is beyond my IQ
                mini = min(len(contA), len(contB))
                for slp in range(mini):
                    try:
                        ixa = CutFromA.index(contA[slp+1])
                        ixb = CutFromB.index(contB[slp+1])
                        return c.extend(self.generateMidPointList(CutFromA[:ixa], CutFromB[:ixb], startpoint))
                    except IndexError:
                        ixa = CutFromA.index(contA[slp])
                        ixb = CutFromB.index(contB[slp])
                        return c.extend(self.generateMidPointList(CutFromA[ixa:], CutFromB[ixb:], startpoint))

            # case4. (a=0, b=0) and (c=0, d=0)
            elif(contA == [] and contBetA == []) and (contB == [] and contBetB == []):
                return c

            # case5. the mirror of the itself.
            else:
                return c.extend(self.generateMidPointList(b, a, startpoint))
