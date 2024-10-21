import copy
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re
import seaborn as sns

from params import prefectures, prefectures_rome

dir = "02_graph_partitioning"

if __name__ == "__main__":
    with open(dir + "/data/FEH_00200523_220412150901.csv", encoding='shift_jis') as f:
        lines0 = f.readlines()
    with open(dir + "/data/FEH_00200523_220412150945.csv", encoding='shift_jis') as f:
        lines1 = f.readlines()
    with open(dir + "/data/FEH_00200523_220412151029.csv", encoding='shift_jis') as f:
        lines2 = f.readlines()
    lines = lines0 + lines1 + lines2
    items = []
    for line in lines:
        if '"18",' in line:
            vals = re.findall('".*?"', line)
            # vals = line.split(',"')
            item = {}
            item["item_code"] = int(vals[0].replace('"', '')) # "表章項目 コード"
            item["item"] = vals[1].replace('"', '') # "表章項目"
            item["nation_code"] = int(vals[2].replace('"', '')) # "国籍 コード"
            item["nation"] = vals[3].replace('"', '') # "国籍"
            item["after_code"] = int(vals[4].replace('"', '')) # "移動後の住所地 コード"
            item["after"] = vals[5].replace('"', '') # "移動後の住所地"
            item["year_code"] = int(vals[6].replace('"', '')) # "時間軸（年次） コード"
            item["year"] = vals[7].replace('"', '') # "時間軸（年次）"
            item["before_code"] = int(vals[8].replace('"', '')) # "移動前の住所地 コード"
            item["before"] = vals[9].replace('"', '') # "移動前の住所地"
            item["sex"] = vals[10].replace('"', '') # "/性別"
            vals[11] = vals[11].replace('"', '') 
            if "," in vals[11]:
                item["total"] = int(vals[11].replace(',', '')) # "総数" 
            else:
                item["total"] = int(vals[11])
            vals[12] = vals[12].replace('"', '')
            if "," in vals[12]:
                item["male"] = int(vals[12].replace(',', '')) # "男"
            else:
                item["male"] = int(vals[12])
            vals[13] = vals[13].replace('"', '')
            if "," in vals[13]:
                item["female"] = int(vals[13].replace(',', '')) # "女"
            else:
                item["female"] = int(vals[13]) # "女"
            items.append(item)
    matrix_df = pd.DataFrame(index=prefectures, columns=prefectures)
    matrix_df = matrix_df.fillna(0)
    for item in items:
        if item["before"] in prefectures and item["after"] in prefectures:
            if item["before"] != item["after"]:
                matrix_df.loc[item["before"], item["after"]] += item["total"]
    fig, ax = plt.subplots(figsize=(12, 9)) 
    matrix_df.index = prefectures_rome
    matrix_df.columns = prefectures_rome
    sns.heatmap(matrix_df, square=True) #, vmax=1, vmin=-1, center=0)
    plt.savefig(dir + '/matrix_org.png')
    matrix_df.to_csv(dir + '/matrix_org.csv')

    # top 10 hate
    matrix = copy.copy(matrix_df.values)
    for i in range(len(matrix_df)):
        temp = copy.copy(matrix[i, :])
        temp = temp[temp.nonzero()]
        temp = sorted(temp)
        thres = temp[9]
        row = copy.copy(matrix[i, :])
        before = prefectures_rome[i]
        for j in range(len(matrix_df)):
            if i != j:
                after = prefectures_rome[j]
                if row[j] < thres:
                    matrix_df.loc[before, after] = 0
                else:
                    matrix_df.loc[before, after] = 1

    fig, ax = plt.subplots(figsize=(12, 9)) 
    sns.heatmap(matrix_df, square=True) #, vmax=1, vmin=-1, center=0)
    plt.savefig(dir + '/matrix.png')

    matrix_df.index = prefectures
    matrix_df.columns = prefectures
    matrix_df.to_csv(dir + '/matrix.csv')
    
