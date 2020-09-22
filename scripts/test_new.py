# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 16:55:30 2020

@author: sinha
"""

import pandas as pd
import xlsxwriter

df1 = pd.DataFrame()
df2 = pd.DataFrame()

path = "../Sessions/"
# book = load_workbook(path)

writer = pd.ExcelWriter(path + 'out.xlsx', engine = 'xlsxwriter')

df1.to_excel(writer, sheet_name = "sheet1")
df2.to_excel(writer, sheet_name = "sheet2")

writer.save()
writer.close()