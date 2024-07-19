from __future__ import print_function
# import typer

import sudoku

algo = 1

def main(filename: str = "problem.txt", solver_name: str = "qpu"):
    if algo == 1:
        ins = sudoku.sudoku(filename)
        ins.solve_initially()
        print("sudoku=")
        print(ins.get_matrix())
        ins.build_variable()
        ins.define_eval_function()
        ins.solve_using_dwave(solver_name=solver_name, simulation=True)
        # Verify
        if ins.is_correct():
            print("The solution is correct")
        else:
            print("The solution is incorrect")
    elif algo == 2: # using sample
        ins = sudoku.sudoku(filename)
        print("sudoku=")
        print(ins.get_matrix())
        ins.build_bqm_sample()
        ins.solve_using_dwave(solver_name=solver_name, simulation=True)
        # Verify
        if ins.is_correct():
            print("The solution is correct")
        else:
            print("The solution is incorrect")

if __name__ == "__main__":
    # typer.run(main)
    filename = "01_sudoku/problems/4x4/problem-00.txt"
    main(filename=filename)
