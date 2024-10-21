import pandas as pd

import graph_partition

dir = "02_graph_partitioning"

if __name__ == "__main__":
    prefectures = pd.read_csv(dir + "/matrix.csv", index_col=0)
    matrix_df = pd.read_csv(dir + "/matrix.csv", header=0, index_col=0)
    num_reads = 1000
    for i in range(10):
        ins = graph_partition.graph_partition(matrix_df, prefectures, num_reads)
        t1 = ins.calc_qubo_PyQUBO()
        t2 = ins.solve_using_dwave(solver_name="qpu", simulation=True)
        ins.output_partitioned(dir + "/partitioned_map%02d.png"%i)
