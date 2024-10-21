import copy
import matplotlib.pyplot as plt
import dimod
import time
import os
import pyqubo

from japanmap import picture
from pylab import rcParams

from solvers import solve_by_qpu, solve_by_kerberos, solve_by_tabu_search, solve_by_sa, solve_by_qpu_subproblem_sampler

group_num = 4
logout_qubo = True

class graph_partition:
    def __init__(self, matrix_df_, prefectures_, num_reads_):
        self.matrix_df = matrix_df_.copy()
        self.prefectures = prefectures_
        self.num_reads = num_reads_
        self.N = len(self.matrix_df)*group_num
        print("number of variable = %d"%(self.N))        

    def calc_qubo_PyQUBO(self):
        print("calculating qubo...")
        start = time.time()
        self.bqm = dimod.BinaryQuadraticModel({}, {}, 0.0, dimod.BINARY)

        #---- define Σ(Σ(xjQxj))
        f1 = 0
        coef = 0.1
        for i, ken_before in enumerate(self.prefectures):
            for j, ken_after in enumerate(self.prefectures):
                if i == j: continue
                temp = 0
                for k in range(group_num):                    
                    temp += pyqubo.Binary("x_%02d_%02d"%(i, k))*pyqubo.Binary("x_%02d_%02d"%(j, k))
                weight = 1.0 - self.matrix_df.loc[ken_before, ken_after]
                f1 += coef*weight*temp
        E = f1
        # E = 0.1*f1

        #---- define (Σxi)**2
        f2 = 0
        for k in range(group_num):
            temp = 0
            for i, ken in enumerate(self.prefectures):
                temp += pyqubo.Binary("x_%02d_%02d"%(i, k))
            f2 += (temp - len(self.prefectures)/group_num)**2
        E += f2

        #---- define Σ(Σxk - 1)**2
        f3 = 0
        for i, ken in enumerate(self.prefectures):
            temp = 0
            for k in range(group_num):
                temp += pyqubo.Binary("x_%02d_%02d"%(i, k))
            f3 += (temp - 1)**2
        E += f3

        model = E.compile()
        qubo, offset = model.to_qubo()
        self.bqm.update(dimod.BinaryQuadraticModel.from_qubo(qubo, offset))
        elapsed_time = time.time() - start
        print ("elapsed_time: %.3f"%elapsed_time + "[sec]")
        if logout_qubo:
            qubo, offset = self.bqm.to_qubo()
            qubo = sorted(qubo.items())
            with open("qubo_pyqubo.csv", "w") as f:
                for line in qubo:
                    msg = ""
                    for key in line[0]:
                        msg += key + ","
                    msg += str(line[1]) + "\n"
                    f.write(msg)
        return elapsed_time
    
    def solve_using_dwave(self, solver_name="qpu", simulation=True):
        solver = {
            'qpu': solve_by_qpu,
            'tabu_hybrid': solve_by_tabu_search,
            'sa_hybrid': solve_by_sa,
            'qpu_hybrid': solve_by_qpu_subproblem_sampler,
            'kerberos_hybrid': solve_by_kerberos,
        }.get(solver_name, solve_by_qpu_subproblem_sampler)

        start = time.time()
        if simulation:
            print("simulating...")
            solution = dimod.SimulatedAnnealingSampler().sample(self.bqm, num_reads=self.num_reads)
        else:
            print("solving in cloud...")
            solution = solver(self.bqm, self.num_reads)
        best_solution = solution.first.sample
        self.result = {}
        for item in best_solution.items():
            label = item[0]
            i = int(label.split("_")[1])
            j = int(label.split("_")[2])
            val = item[1]
            if val == 1:
                ken = self.prefectures.index[i]
                self.result[ken] = j
        elapsed_time = time.time() - start
        print ("elapsed_time: %.3f"%elapsed_time + "[sec]")
        print("bqm energy: ", solution.first.energy)
        # if not simulation:
        #     print("qpu_access_time: %.2f us"%solution.info['timing']["qpu_access_time"])
        return elapsed_time
    
    def output_partitioned(self, filename):
        rcParams['figure.figsize'] = (8, 8)
        colors = {}
        errors = 0
        for key in self.result:
            counter = 0
            if self.result[key] == 0:
                colors[key] = (255, 0, 255)
                counter += 1
            if self.result[key] == 1:
                colors[key] = (0, 255, 0)
                counter += 1
            if self.result[key] == 2:
                colors[key] = (0, 255, 255)
                counter += 1
            if self.result[key] == 3:
                colors[key] = (255, 255, 0)
                counter += 1
            if counter != 1:
                errors += 0
        print("error(multi group): %d"%errors)
        plt.imshow(picture(colors))
        plt.savefig(filename)



