from openpyxl import load_workbook
import numpy as np
from QuaterTriangle import QuaterTriangle3D
import matplotlib.pyplot as plt
import matplotlib.tri
import matplotlib.collections

wb = load_workbook(filename="./RawData/RawPointData.xlsx", data_only=True)
RADIUS = 1000

if __name__ == '__main__':

    qt = QuaterTriangle3D(wb, RADIUS)
