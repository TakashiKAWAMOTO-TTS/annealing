# Solve Sudoku using D-Wave Leap

## 1. Overview

・Trial of D-Wave Leap for solving sudoku

## 2. Usage

main.py
```
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
```

### (1) Simulation

Use algo = 1, and set "simulation" as "True" for the arguments of solve_using_wave


### (2) Calculate with leap

Use algo = 1, and set "simulation" as "False" for the arguments of solve_using_wave

**Note:**
algo = 2 works but takes a lot of calculation time.

## Reference

https://zenn.dev/airev/articles/airev-quantum-02
https://lp-tech.net/articles/jbkhW
