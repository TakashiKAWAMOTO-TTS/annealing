import copy
import dimod
import itertools
import math
import numpy as np
import pandas as pd
import re
# import wildqat
# import blueqat.utils as wq

from dimod.generators import combinations
from solvers import solve_by_tabu_search, solve_by_sa, solve_by_qpu_subproblem_sampler
from sympy import Symbol, expand

class sudoku:
    def __init__(self, filename):
        self.org = self.read_matrix(filename)
        self.matrix = np.array(copy.copy(self.org))
        self.n = len(self.matrix)          # Number of rows/columns in sudoku
        self.m = int(math.sqrt(self.n))    # Number of rows/columns in sudoku subsquare
        self.digit = range(1, self.n + 1)
    
    def read_matrix(self, filename):
        with open(filename, "r") as f:
            content = f.readlines()
        lines = []
        for line in content:
            new_line = line.rstrip()    # Strip any whitespace after last value
            if new_line:
                new_line = list(map(int, new_line.split(' ')))
                lines.append(new_line)
        return lines

    def check_line(self, matrix_, id_row):
        digit_fill = matrix_[id_row][matrix_[id_row]>0]
        digit_blank = np.setdiff1d(self.digit, digit_fill)
        return digit_blank

    def check_block(self, id_row, id_col):
        id_row = id_row//self.m
        id_col = id_col//self.m
        quiz_block = self.matrix.reshape((self.m, self.m, self.m, self.m))[id_row, :, id_col]

        digit_fill = quiz_block[quiz_block>0]
        digit_blank = np.setdiff1d(self.digit, digit_fill)
        return digit_blank

    def solve_initially(self):
        id_blank = []
        while True:
            #---- if 'len(id_blank)' is the same as the previous loop, 'while loop' ends
            if len(id_blank) == len(np.array(np.where(self.matrix==0)).T):
                break
            #---- obtain 'candidate' that can be filled in the blank
            #---- then, if the number of 'candidate' is one, fill in the blank
            id_blank = np.array(np.where(self.matrix==0)).T
            for id_blank_row, id_blank_col in id_blank:    
                candidate_row = self.check_line(self.matrix, id_blank_row)
                candidate_col = self.check_line(self.matrix.T, id_blank_col)
                candidate_block = self.check_block(id_blank_row, id_blank_col)

                candidate_concat = np.concatenate((candidate_row, candidate_col, candidate_block))
                candidate_unique = np.unique(candidate_concat, return_counts=True)
                candidate = candidate_unique[0][candidate_unique[1]==3]
                if len(candidate) == 1:
                    self.matrix[id_blank_row, id_blank_col] = int(candidate)

    def build_variable(self):
        id_blank = np.array(np.where(self.matrix==0)).T
        self.x_vec = []

        for id_blank_row, id_blank_col in id_blank:    
            candidates_row = self.check_line(self.matrix, id_blank_row)
            candidates_col = self.check_line(self.matrix.T, id_blank_col)
            candidates_block = self.check_block(id_blank_row, id_blank_col)
            
            candidates_concat = np.concatenate((candidates_row, candidates_col, candidates_block))
            candidates_unique = np.unique(candidates_concat, return_counts=True)
            candidates = candidates_unique[0][candidates_unique[1]==3]

            for candidate in candidates:
                temp = {}
                temp["row"] = id_blank_row
                temp["col"] = id_blank_col
                temp["block"] = (id_blank_row//self.m)*self.m +  (id_blank_col//self.m)
                temp["candidate"] = candidate
                temp["symbol"] = "x%d%d%d"%(id_blank_row, id_blank_col, candidate)
                self.x_vec.append(temp)
        # print(len(self.x_vec))
    
    def define_eval_function(self):
        self.E = 0
        self.bqm = dimod.BinaryQuadraticModel({}, {}, 0.0, dimod.BINARY)

        #---- define (Σqi -1)**2 for each cells
        f1 = {}
        for x in self.x_vec:
            loc = "%d_%d"%(x["row"], x["col"])
            if loc in f1:
                f1[loc] += Symbol(x["symbol"])
                f1[loc + "-list"].append(x["symbol"])
            else:
                f1[loc] = Symbol(x["symbol"])
                f1[loc + "-list"] = []
                f1[loc + "-list"].append(x["symbol"])
        for key in f1:
            if "-list" not in key:
                f = f1[key] - 1
                f = f**2
                self.E += expand(f)
            else:
                self.bqm.update(combinations(f1[key], 1))

        #---- define (Σqi - 1)**2 for each rows
        f2 = {}
        for x in self.x_vec:
            loc = "%d_%d"%(x["row"], x["candidate"])
            if loc in f2:
                f2[loc] += Symbol(x["symbol"])
                f2[loc + "-list"].append(x["symbol"])
            else:
                f2[loc] = Symbol(x["symbol"])
                f2[loc + "-list"] = []
                f2[loc + "-list"].append(x["symbol"])
        for key in f2:
            if "-list" not in key:
                f = f2[key] - 1
                f = f**2
                self.E += expand(f)
            else:
                self.bqm.update(combinations(f2[key], 1))
                
        # #---- define (Σqi - 1)**2 for each cols
        f3 = {}
        for x in self.x_vec:
            loc = "%d_%d"%(x["col"], x["candidate"])
            if loc in f3:
                f3[loc] += Symbol(x["symbol"])
                f3[loc + "-list"].append(x["symbol"])
            else:
                f3[loc] = Symbol(x["symbol"])
                f3[loc + "-list"] = []
                f3[loc + "-list"].append(x["symbol"])
        for key in f3:
            if "-list" not in key:
                f = f3[key] - 1
                f = f**2
                self.E += expand(f)
            else:
                self.bqm.update(combinations(f3[key], 1))

        #---- define (Σqi - 1)**2 for each blocks
        f4 = {}
        for x in self.x_vec:
            loc = "%d_%d"%(x["candidate"], x["block"])
            if loc in f4:
                f4[loc] += Symbol(x["symbol"])
                f4[loc + "-list"].append(x["symbol"])
            else:
                f4[loc] = Symbol(x["symbol"])
                f4[loc + "-list"] = []
                f4[loc + "-list"].append(x["symbol"])
        for key in f4:
            if "-list" not in key:
                f = f4[key] - 1
                f = f**2
                self.E += expand(f)
            else:
                self.bqm.update(combinations(f4[key], 1))

    def calc_qubo(self):
        terms = []
        for x in self.x_vec:
            terms.append(x["symbol"])
        self.qubo = pd.DataFrame(index=terms, columns=terms)
        self.qubo = self.qubo.fillna(0)

        self.coeff_di = self.E.as_coefficients_dict()
        for var, coeff in self.coeff_di.items():
            if var == 1: # ignore constant term
                continue
            var = str(var)
            if "**" in var:
                var = var.split("**")
                self.qubo.loc[var[0], var[0]] += int(coeff)
            elif "*" in var:
                var = var.split("*")
                self.qubo.loc[var[0], var[1]] += int(coeff)
            else:
                self.qubo.loc[var, var] += int(coeff)
        self.qubo.to_csv('qubo.csv')

    def simulate_by_wildqat(self):
        # E_lowest = 100000
        i = 0
        while True:
            i += 1
            # a = wildqat.opt()
            a = wq.opt()
            a.qubo = self.qubo.values
            pred = a.run()
            print('{}/{}: {}'.format(i+1, 100, a.E[-1] + self.coeff_di[1]))
            if a.E[-1] + self.coeff_di[1] == 0:
                pred_best = pred
                break

        for i, val in enumerate(pred_best):
            if val == 1:
                row = self.x_vec[i]["row"]
                col = self.x_vec[i]["col"]
                candidate = self.x_vec[i]["candidate"]
                self.matrix[row, col] = candidate
        print("answer=")
        print(self.matrix)
    
    def get_matrix(self):
        return self.matrix

    def get_bqm(self):
        return self.bqm

    def solve_using_dwave(self, solver_name="qpu", simulation=True):
        solver = {
            'tabu': solve_by_tabu_search,
            'sa': solve_by_sa,
            'qpu': solve_by_qpu_subproblem_sampler,
        }.get(solver_name, solve_by_qpu_subproblem_sampler)

        if simulation:
            print("simulating...")
            num_reads = 1000
            solution = dimod.SimulatedAnnealingSampler().sample(self.bqm, num_reads=num_reads)
        else:
            solution = solver(self.bqm)
        best_solution = solution.first.sample
        solution_list = [k for k, v in best_solution.items() if v == 1]
        for label in solution_list:
            row = int(label[1])
            col = int(label[2])
            val = int(label[3])
            if self.matrix[row][col] > 0:
                continue
            self.matrix[row][col] = val
        print("bqm energy: ", solution.first.energy)
        print("answer=")
        print(self.matrix)

    def is_correct(self):
        unique_digits = set(self.digit)  # Digits in a solution

        # Verifying rows
        for row in self.matrix:
            if set(row) != unique_digits:
                print("Error in row: ", row)
                return False

        # Verifying columns
        for j in range(self.n):
            col = [self.matrix[i][j] for i in range(self.n)]
            if set(col) != unique_digits:
                print("Error in col: ", col)
                return False

        # Verifying subsquares
        subsquare_coords = [(i, j) for i in range(self.m) for j in range(self.m)]
        for r_scalar in range(self.m):
            for c_scalar in range(self.m):
                subsquare = [self.matrix[i + r_scalar * self.m][j + c_scalar * self.m] for i, j
                            in subsquare_coords]
                if set(subsquare) != unique_digits:
                    print("Error in sub-square: ", subsquare)
                    return False
        return True

    def build_bqm_sample(self):
        digits = list(self.digit)
        self.bqm = dimod.BinaryQuadraticModel({}, {}, 0.0, dimod.BINARY)

        # 各セルには digits のいずれかの値が入る
        for i, j in itertools.product(range(self.n), range(self.n)):
            node_digits = ["x%d%d%d"%(i, j, v) for v in digits]
            self.bqm.update(combinations(node_digits, 1))

        # 各行で値は重複しない
        for i, v in itertools.product(range(self.n), digits):
            row_nodes = ["x%d%d%d"%(i, j, v) for j in range(self.n)]
            self.bqm.update(combinations(row_nodes, 1))

        # 各列で値は重複しない
        for j, v in itertools.product(range(self.n), digits):
            col_nodes = ["x%d%d%d"%(i, j, v) for i in range(self.n)]
            self.bqm.update(combinations(col_nodes, 1))

        # 各ブロックで値は重複しない
        for digit in digits:
            for mi, mj in itertools.product(range(self.m), range(self.m)):
                ij = itertools.product(
                    range(mi * self.m, (mi + 1) * self.m),
                    range(mj * self.m, (mj + 1) * self.m),
                )
                square_nodes = ["x%d%d%d"%(i, j, digit) for i, j in ij]
                self.bqm.update(combinations(square_nodes, 1))

        fixed_labels: set[tuple[str, int]] = set()
        for i, row in enumerate(self.matrix):
            for j, val in enumerate(row):
                if val > 0:
                    fixed_labels |= {("x%d%d%d"%(i, j, val), 1)}
        self.bqm.fix_variables(list(fixed_labels))
