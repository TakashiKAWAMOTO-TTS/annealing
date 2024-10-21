# Japanese region division for Reiwa-era

## 1. Overview

・Trial of D-Wave Leap for graph partitioning  
・Generating Japanese region division for Reiwa-era

## 2. Usage

(1) Create matrix

```
$ python3 calc_matrix.py
```

The followings are created:  
・02_graph_partitioning/matrix.csv  
・02_graph_partitioning/matrix.png  
・02_graph_partitioning/matrix_org.csv  
・02_graph_partitioning/matrix_org.png  

matrix_org.png  
<img src=img/matrix_org.png width=400>

matrix.png  
<img src=img/matrix.png width=400>

(2) Execute graph partitioning

```
$ python3 main.py
```

The results are save into "/partitioned_map**.png"(00 to 09).  
<img src=img/partitioned_map01.png width=300>
<img src=img/partitioned_map02.png width=300>
<img src=img/partitioned_map03.png width=300>
<img src=img/partitioned_map04.png width=300>
<img src=img/partitioned_map05.png width=300>
<img src=img/partitioned_map06.png width=300>

Note that the results are calculated by simulator not an actual quantum computer.

## Original data
https://www.e-stat.go.jp/dbview?sid=0003420473
