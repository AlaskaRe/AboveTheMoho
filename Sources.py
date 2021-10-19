from openpyxl import load_workbook

Point = {}
stratums_lib = []

wb = load_workbook(filename="./RawData/RawPointData.xlsx")
wksht_pt = wb["POSTION"]
wksht_lib = wb["LAYER_LIBARY"]
wksht_args = wb["POINT_ARGS"]

# read the worksheet"LAYER_LIBARY", get the information of the layers
for row in wksht_lib.iter_rows(min_row=2, max_row=20, max_col=3):
    if row[0].value != None:
        T = (row[0].value, row[1].value, row[2].value)
        stratums_lib.append(T)

layerInformation = [None for i in range(len(stratums_lib))]

# get the point data from the sheet
for r in wksht_pt.iter_rows(min_row=2, max_col=3):
    if r[0].value == None:
        break
    Point[r[0].value, r[1].value, r[2].value] = layerInformation

for r in wksht_args.iter_rows(min_row=2, max_col=13):
