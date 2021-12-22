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
                da = (r[7].value, r[8].value, r[11].value)
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
        self.pointSequence = dt.exportSequence()
        self.extendedSq = copy.deepcopy(self.pointSequence)
        self.baseTriangles = dt.exportTriangles()

        self.edgeToMidPoint = {}
        self.midPoint = {}
        self.quaterTriangles = []

        # 3.1 EdgeToMidPoint

        for e in self.edges:
            self.edgeToMidPoint[e] = self.pointSequence[e[0]
                                                        ] + self.pointSequence[e[1]]

        # 3.2 MidPoint
        for key in self.edgeToMidPoint.keys():
            A = tuple(self.pointSequence[key[0]])
            listA = self.Point[A]
            B = tuple(self. pointSequence[key[1]])
            listB = self.Point[B]

            self.midPoint[key] = self.generateMidPointList(listA, listB, 0)

        # 3.3 Extended sequence
        # Using the extend method built in list, that's not a deepcopy
        self.extendedSq.extend(self.edgeToMidPoint.values())

        # 3.4 QuaterTriangles
        self.quaterTriangles = self.generateQuaterTriangles()

        # 3.5 Ordered Triangles
        self.orderedTriangles = {i: [] for i in range(len(self.extendedSq))}
        for tri in self.quaterTriangles:
            self.orderedTriangles[tri[0]] += tri
            self.orderedTriangles[tri[1]] += tri
            self.orderedTriangles[tri[2]] += tri

        # 4. the net of every stratums
        self.extendedPoint = copy.deepcopy(self.Point)
        self.extendedPoint.update(self.midPoint)
        self.stratumsDic = self.generateQuaterNet()

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
                    contA.append(a[x])
                    idxA = x+1
            try:
                remainderA = copy.deepcopy(a[idxA:len(a)])
                for item in remainderA:
                    contBetA.remove(item)
            except IndexError:
                pass

            for valA in contA:
                try:
                    CutFromA = copy.deepcopy(contBetA)
                    contBetA.remove(valA)
                except ValueError:
                    pass

            contBetB = copy.deepcopy(b[idxB:len(b)])
            for y in range(idxB, len(b)):
                if b[y][2] == self.Stratums_lib[i][0]:
                    contB.append(b[y])
                    idxB = y+1
            try:
                remainderB = copy.deepcopy(b[idxB:len(b)])
                for item in remainderB:
                    contBetB.remove(item)
            except IndexError:
                pass

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
                    c.append((top, bottom, a[i][2]))
                else:
                    top = (contA[0][0] + contB[0][0])/2
                    bottom = (contA[-1][1] + contB[0][1])/2
                    c.append(top, bottom, a[i][2])
                if contBetA != []:
                    l = len(contBetA)+1
                    thickness = c[-1][0] - c[-1][1]
                    piecethk = thickness/l
                    for acc in len(contBetA):
                        newlayer = (top - acc * piecethk)
                        c.append((newlayer, newlayer, contBetA[acc][2]))

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
                return self.generateMidPointList(a, b, startpoint+1)

            # case5. the mirror of the itself.
            else:
                return c.extend(self.generateMidPointList(b, a, startpoint))

    def generateQuaterTriangles(self):
        quaterNet = []
        for tri in self.baseTriangles.keys():
            a, b, c = tri[0], tri[1], tri[2]
            try:
                mabcoord = self.edgeToMidPoint[(a, b)]
            except:
                mabcoord = self.edgeToMidPoint[(b, a)]

            try:
                mbccoord = self.edgeToMidPoint[(b, c)]
            except:
                mbccoord = self.edgeToMidPoint[(c, b)]

            try:
                maccoord = self.edgeToMidPoint[(a, c)]
            except:
                maccoord = self.edgeToMidPoint[(c, a)]

            i = self.extendedSq.index(mbccoord)
            j = self.extendedSq.index(maccoord)
            k = self.extendedSq.index(mabcoord)
            new_tri = [(i, j, k), (a, k, j), (k, b, i), (j, i, c)]
            quaterNet.extend(new_tri)

        return quaterNet

    def generateQuaterNet(self):
        dic = {}
        for idx0 in self.Stratums_lib:
            n = np.ones(shape=len(self.extendedSq), dtype=int)
            for j in self.extendedPoint.values():
                if self.point[idx0] == idx0[0]:
                    n[j] += 1
            nmax = n.amax()*2
            listI = [[] for aa in range(nmax)]
            for itr in range(nmax):
                listxy = np.asarray(self.extendedSq)
                listz = np.asarray(np.zeros(len(self.extendedSq), int))
                listI[itr] = np.column_stack(listxy, listz)
            idx1 = 0
            for j in self.midPoint:
                if self.midPoint[j][2] == idx0[0]:
                    idx2 = self.extendedSq.index(j)
                    listI[2*idx1][idx2] = (j[0], j[1], self.midPoint[j][0])
                    listI[2*idx1][idx2] = (j[0], j[1], self.midPoint[j][1])
            dic[idx0] = copy.deepcopy(listI)

        return dic

    def exportQuaterTriangle(self):
        return self.quaterTriangles

    def exportStratumsSheet(self):
        return self.stratumsDic

    def generateSurface(self):
        pass
