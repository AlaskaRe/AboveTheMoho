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
            self.edgeToMidPoint[e] = (
                self.pointSequence[e[0]] + self.pointSequence[e[1]])/2

        # 3.2 MidPoint
        for key in self.edgeToMidPoint.keys():
            A = tuple(self.pointSequence[key[0]])
            listA = self.Point[A]
            B = tuple(self. pointSequence[key[1]])
            listB = self.Point[B]
            kwd = tuple(self.edgeToMidPoint[key])
            self.midPoint[kwd] = self.generateMidPointList(listA, listB, 0)

            # print(self.midPoint)

        # 3.3 Extended sequence
        # Using the extend method built in list, that's not a deepcopy
        self.extendedSq.extend(self.edgeToMidPoint.values())
        arr = np.asarray(self.extendedSq)
        self.extendedSq = arr.tolist()

        # 3.4 QuaterTriangles
        self.quaterTriangles = self.generateQuaterTriangles()

        # 3.5 Ordered Triangles
        self.orderedTriangles = {i: [] for i in range(len(self.extendedSq))}
        for tri in self.quaterTriangles:
            self.orderedTriangles[tri[0]].append(tri)
            self.orderedTriangles[tri[1]].append(tri)
            self.orderedTriangles[tri[2]].append(tri)

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

            if len(a) == idxA and len(b) == idxB:
                return c

            CutFromA, contA, contBetA, idxA = generateList(
                a, idxA, self.Stratums_lib[i][0])

            CutFromB, contB, contBetB, idxB = generateList(
                b, idxB, self.Stratums_lib[i][0])

            # For convience, I take contA as a, contBetA as b, contB as c, contBetB as d. 1 means not null, 0 means null.
            # If b=0, it represents that a only has one element, so does the c and d.So where is the data check process?!

            # case0. (a=0, b=0) and (c=0, d=0)
            if(contA == [] and contBetA == []) and (contB == [] and contBetB == []):
                continue

            # case1. break the loop and raise the error
            elif (contA == [] and contBetA != []) or (contB == [] and contBetB != []):
                # that means the data are not right, error should be raised, but here I just ignore this data.
                return c

            # case2. (a=1, b = 0/1) and (c = 0/1, d = 0)
            elif contA != [] and contBetB == []:
                if contB != []:
                    top = (contA[0][0] + contB[0][0])/2
                    bottom = (contA[-1][1] + contB[0][1])/2
                else:
                    try:
                        bstms = listidx(self.Stratums_lib, b[idxB][2])
                    except IndexError:
                        idxB -= 1
                        bstms = listidx(self.Stratums_lib, b[idxB][2])
                    if i < bstms:
                        topb = b[idxB][0]
                        bottomb = b[idxB][0]
                    else:
                        topb = b[idxB][1]
                        bottomb = b[idxB][1]
                        idxB += 1

                    top = (contA[0][0] + topb)/2
                    bottom = (contA[-1][1] + bottomb)/2

                c.append((top, bottom, self.Stratums_lib[i][0]))

                if contBetA != []:

                    if len(contA) != 1:
                        l = len(contBetA)+1
                        thickness = c[-1][0] - c[-1][1]
                        piecethk = thickness/l
                        for acc in range(len(contBetA)):
                            hight = (top - (acc + 1) * piecethk)
                            c.append((hight, hight, contBetA[acc][2]))

                    # with my oponion, only one reverse stratums is reasonable
                    elif len(contBetA) == 1:

                        if contB == []:
                            betastms = listidx(
                                self.Stratums_lib, contBetA[0][2])
                            if betastms == bstms:
                                del c[-1]
                                subtop = (contBetA[0][0] + b[idxB][0])/2
                                subbottom = (contBetA[0][1] + b[idxB][1])/2
                                c.append((subtop, subbottom, contBetA[0][2]))

                                subtop = (contA[-1][0] + b[idxB][1])/2
                                subbottom = (contA[-1][1] + b[idxB][1])/2
                                c.append((subtop, subbottom, contA[-1][2]))
                                idxB += 1
                            else:
                                subtop = (contBetA[0][0] + topb)/2
                                subbottom = (contBetA[0][1] + bottomb)/2
                                c.append((subtop, subbottom, contBetA[0][2]))
                        else:
                            subtop = (contBetA[0][0] + contB[0][0])/2
                            subbottom = (contBetA[0][1] + contB[0][0])/2
                            c.append((subtop, subbottom, contBetA[0][2]))

                    # More complicatied situation........HEADACHE...
                    # step1.raise error, to check the data.
                    # step2.if nothing wrong with the data, then send email to me(wukong14@outlook.com)
                    # ---------------------------------------------
                    else:
                        continue

            # case3. (a = 1, b = 1) and (c = 1, d = 1)
            elif (contA != [] and contBetA != []) and (contB != [] and contBetB != []):
                mini = min(len(contA), len(contB))
                ixa, ixb = 0, 0
                if mini > 1:
                    for slp in range(1, mini):
                        ixa2 = CutFromA.index(contA[slp])
                        ixb2 = CutFromB.index(contB[slp])
                        c.extend(self.generateMidPointList(
                            CutFromA[ixa:ixa2], CutFromB[ixb:ixb2], i))
                        ixa = copy.deepcopy(ixa2)
                        ixb = copy.deepcopy(ixb2)
                else:
                    c.extend(self.generateMidPointList(
                        CutFromA[:-1], CutFromB[:-1], i))

                c.extend(self.generateMidPointList(
                    CutFromA[-1:], CutFromB[-1:], i))
            # case4. reverse the a and b.
            else:
                if a[idxA:] == []:
                    c.extend(self.generateMidPointList(
                        b[b.index(CutFromB[0]):], a[-1:], i))
                else:
                    try:
                        c.extend(self.generateMidPointList(
                            b[b.index(CutFromB[0]):], a[a.index(CutFromA[0]):], i))
                    except IndexError:
                        c.extend(self.generateMidPointList(
                            b[b.index(CutFromB[0]):], a[idxA:], i))

                return c

        return c

    def generateQuaterTriangles(self):
        quaterNet = []
        for tri in self.baseTriangles:
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

            i = self.extendedSq.index(mbccoord.tolist())
            j = self.extendedSq.index(maccoord.tolist())
            k = self.extendedSq.index(mabcoord.tolist())
            new_tri = [(i, j, k), (a, k, j), (k, b, i), (j, i, c)]
            quaterNet.extend(new_tri)

        return quaterNet

    def generateQuaterNet(self):
        dic = {}
        for idx0 in self.Stratums_lib:
            n = np.zeros(shape=len(self.extendedSq), dtype=int)

            for j, item in enumerate(self.extendedPoint):
                for subj in self.extendedPoint[item]:
                    if subj[2] == idx0[0]:
                        n[j] += 1
            nmax = n.max()*2

            listI = np.zeros(shape=(nmax, len(self.extendedSq), 3))
            listI[:, :, :2] = self.extendedSq

            for nmb, pt in enumerate(self.extendedPoint):
                ix = 0
                for stm in self.extendedPoint[pt]:
                    if stm[2] == idx0[0]:
                        listI[ix, nmb, 2] = stm[0]
                        listI[ix+1, nmb, 2] = stm[1]
                        ix += 2
            dic[idx0] = copy.deepcopy(listI)

        return dic

    def exportQuaterTriangle(self):
        return self.quaterTriangles

    def exportStratumsSheet(self):
        return self.stratumsDic

    def generateGroundSurface(self):
        pass


def listidx(listA, b):

    for i in range(len(listA)):
        if listA[i][0] == b:
            return i


def generateList(listOri, idx, targetvule):

    cutFromOri = listOri[idx:]
    contI, contInsideI = [], []
    for i in range(idx, len(listOri)):
        if listOri[i][2] == targetvule:
            contI.append(listOri[i])
            idx = i + 1
    try:
        remainderI = listOri[idx:]
        n = cutFromOri.index(remainderI[0])
        cutFromOri = cutFromOri[:n]
    except IndexError:
        pass
    contInsideI = copy.deepcopy(cutFromOri)

    for ele in contI:
        contInsideI.remove(ele)

    return cutFromOri, contI, contInsideI, idx
