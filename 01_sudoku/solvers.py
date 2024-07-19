import copy
import dimod
import hybrid

from dwave.system.samplers import DWaveSampler
from typing import List, Tuple

def _solve(race: hybrid.Race, bqm) -> hybrid.SampleSet:
    init_state_gen = lambda: hybrid.State.from_sample(hybrid.random_sample(bqm), bqm)

    max_iter = 10
    max_time = 2000
    convergence = 3
    num_reads = 1

    workflow = hybrid.Loop(
        race,
        max_iter=max_iter,
        max_time=max_time,
        convergence=convergence,
        terminate=None,
    )

    samples = list()
    energies = list()
    for _ in range(num_reads):
        init_state = init_state_gen()
        final_state = workflow.run(init_state)
        ss = final_state.result().samples
        ss.change_vartype(bqm.vartype, inplace=True)
        samples.append(ss.first.sample)
        energies.append(ss.first.energy)
    return dimod.SampleSet.from_samples(samples, vartype=bqm.vartype, energy=energies)

def solve_by_tabu_search(bqm) -> hybrid.SampleSet:
    tabu_timeout = 500
    iteration = hybrid.Race(
        hybrid.InterruptableTabuSampler(timeout=tabu_timeout)
    ) | hybrid.ArgMin()
    return _solve(iteration, bqm)

def solve_by_sa(bqm) -> hybrid.SampleSet:
    iteration = hybrid.Race(
        hybrid.BlockingIdentity(),
        hybrid.InterruptableSimulatedAnnealingProblemSampler(
            num_reads=1, num_sweeps=10000,
        )
    ) | hybrid.ArgMin()
    return _solve(iteration, bqm)

def solve_by_qpu_subproblem_sampler(bqm) -> hybrid.SampleSet:
    decomposer = hybrid.EnergyImpactDecomposer(
        size=50, # default value of `max_subproblem_size` is 50.
        rolling=True,
        rolling_history=0.3,
        traversal='bfs'
    )
    sampler = hybrid.QPUSubproblemAutoEmbeddingSampler(
        num_reads=100, # default value of `qpu_reads` in KerberosSampler is 100
        qpu_sampler=DWaveSampler(), # default value of `qpu_sampler` in KerberosSampler is None
        sampling_params={
            'label': 'Sudoku - Solver:QPUSubproblemAutoEmbeddingSampler'
        }, # default value of `sampling_params` in KerberosSampler is None
    )
    composer = hybrid.SplatComposer()
    iteration = hybrid.Race(
        hybrid.BlockingIdentity(),
        decomposer | sampler | composer
    ) | hybrid.ArgMin()
    return _solve(iteration, bqm)

