from openpyxl import load_workbook
from openpyxl.descriptors.base import Length


wb = load_workbook(filename="./RawData/RawPointData.xlsx", data_only=True)
wksht_pt = wb["POSTION"]
wksht_lib = wb["LAYER_LIBARY"]
wksht_args = wb["POINT_ARGS"]

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

    layerInformation = [None for i in range(len(Stratums_lib))]
    Point[r[0].value, r[1].value] = layerInformation

# Read the worksheet "POINT_ARGS", get the stratums of each point.
for r in wksht_args.iter_rows(min_row=2, max_col=13):

    if r[0].value == None:

        break

    else:
        # Read the row and get the value of every stratum for each point.

        kywd = (r[2].value, r[3].value)
        da = [r[7].value, r[8].value, r[11].value]
        Point[kywd]
        layers = len(Stratums_lib)
        for i in Stratums_lib:
            if i[0] == r[11].value:
                idx = Stratums_lib.index(i)
                break

        # give the stratum value to the dict if not exists, else add another value to this list
        sttms = Point[kywd][idx]

        if sttms == None:
            Point[kywd][idx] = da

        elif sttms != None:
            t = []
            t.append(sttms)
            t.append(da)
            Point[kywd][idx] = t

# print(Point)
