from fconcrete.helpers import printProgressBar
import numpy as np
import pandas as pd

class Analysis:

    @staticmethod
    def getBestSolution(concrete_beam_function,
                max_steps_without_decrease = float("inf"),
                avoid_estimate=False,
                show_progress=True,
                sort_by_multiplication=False,
                **kwargs):
        r"""
            Returns a report with all materials and cost.
            
                Call signatures:
                        
                    `fc.Analysis.getBestSolution(concrete_beam_function,
                    ...              max_steps_without_decrease = float("inf"),
                    ...              avoid_estimate=False,
                    ...              show_progress=True,
                    ...              sort_by_multiplication=False,
                    ...              **kwargs)`
                                                            
                >>> def concrete_beam_function(width, height, length):
                ...        slab_area = 5*5
                ...        kn_per_m2 = 5
                ...        distributed_load = -slab_area*kn_per_m2/500
                ...        pp = fc.Load.UniformDistributedLoad(-width*height*25/1000000, x_begin=0, x_end=length)
                ...        n1 = fc.Node.SimpleSupport(x=0, length=20)
                ...        n2 = fc.Node.SimpleSupport(x=400, length=20)
                ...        f1 = fc.Load.UniformDistributedLoad(-0.01, x_begin=0, x_end=1)
                ...        beam = fc.ConcreteBeam(
                ...            loads = [f1, pp],
                ...            nodes = [n1, n2],
                ...            section = fc.Rectangle(width, height),
                ...            division = 200
                ...        )
                ...        return beam
                >>> full_report, solution_report, best_solution = fc.Analysis.getBestSolution(concrete_beam_function,
                ...                                     max_steps_without_decrease=15,
                ...                                     sort_by_multiplication=True,
                ...                                     avoid_estimate=True,
                ...                                     show_progress=False,
                ...                                     width=[15],
                ...                                     height=(30, 34, 2),
                ...                                     length=[150])
                >>> # Table is sorted by cost ascending, so the first one is the most economic solution.
                >>> # Alternative way to look to the best solution
                >> print(best_solution)
                {'width': 15.0, 'height': 30.0, 'length': 150.0, 'cost': 126.2650347902965, 'error': '', 'Concrete': 63.59, 'Longitudinal bar': 35.31, 'Transversal bar': 27.36}
            
            Parameters
            ----------
            concrete_beam_function
                Define the function that is going to create the beam given the parameters.
                
            max_steps_without_decrease : int, optional
                If the cost has not decrescead after max_steps_without_decrease steps, the loop breaks.
                Only use it in case your parameter combination has a logical order.
                Default inf.
            
            show_progress : `bool`, optional
                Estimate time using the last combination.
                If a exception is found, 80s per loop is set and a message about the not precision is shown.
                Also show progress bar in percentage.
                Default True.
            
            sort_by_multiplication : `bool`, optional
                Sort combinations by the multiplication os all parameter. Useful to use with max_steps_without_decrease when the is a logical order.
                Default False.
                
            kwargs
                Possible arguments for the concrete_beam_function.
                If a set of 3 elements is given, np.arange(\*kwarg_value) will be called.
                The kwargs must have the same name that the concrete_beam_function expects as arguments.
                The combination is made with np.meshgrid.
            
                
        """
        
        possible_values = []
        for kwarg_value in kwargs.values():
            possible_values = [*possible_values, np.arange(*kwarg_value)] if (len(kwarg_value) == 3 and type(kwarg_value)==tuple) else [*possible_values, kwarg_value]

        combinations = np.array(np.meshgrid(*possible_values)).T.reshape(-1,len(possible_values))

        # sorting the combinations
        if sort_by_multiplication:
            combinations_t = combinations.T
            multiply = np.ones((1,len(combinations)))
            for i in combinations_t:
                multiply = multiply*i
            combinations = np.append(combinations, multiply.T, axis=1)
            combinations = combinations[np.argsort(combinations[:,-1])][:, 0:-1]

        # combinations to dict
        combination_kwargs = [ { key: combination[i] for i, key in enumerate(kwargs.keys()) } for combination in combinations ]
        total_of_combinations = len(combination_kwargs)

        if avoid_estimate == False:
            max_variable_values = combination_kwargs[-1] 
            try:
                one_precesing_time, not_precise = concrete_beam_function(**max_variable_values).processing_time, False
            except:
                one_precesing_time, not_precise = 80, True
            continue_script = input("There are {} combinations. The estimate time to process all of them is {}s ({} minutes).{}\nType 'y' to continue or another char to cancel.\n".format(total_of_combinations, round(total_of_combinations*one_precesing_time), round(total_of_combinations*one_precesing_time/60), "\nThis measure is not precise!\n" if not_precise else ""))

        if avoid_estimate!=False or continue_script=="y":
            report = (["cost", "error", 'Concrete', 'Longitudinal bar', 'Transversal bar'])
            report = [[*list(kwargs.keys()), *report]]
            min_value, steps_without_decrease = np.inf, 0
            
            for step, combination_kwarg in enumerate(combination_kwargs):
                try:
                    beam = concrete_beam_function(**combination_kwarg)
                    error = ""
                    cost = beam.cost
                    cost_table = list(beam.subtotal_table[:, 1:2].T[0][1:].astype(float))
                    if cost != min(cost, min_value):
                        steps_without_decrease += 1
                        if steps_without_decrease >= max_steps_without_decrease:
                            if show_progress:
                                printProgressBar(total_of_combinations, total_of_combinations, prefix = 'Progress:', suffix = 'Complete', length = 50)
                                print("\n", "Ended in step {} out of {}. Because max_steps_without_decrease was reached.".format(step + 1, total_of_combinations))                        
                            break
                    else:
                        steps_without_decrease = 0
                        min_value = cost
                        
                except Exception as excep:
                    error = str(excep)
                    cost = -1
                    cost_table = [-1, -1, -1]
                
                if show_progress: printProgressBar(step + 1, total_of_combinations, prefix = 'Progress:', suffix = 'Complete', length = 50)
                row = [*combination_kwarg.values(), cost, error, *cost_table]
                report = [*report, row]
            
            full_report = pd.DataFrame(report)
            full_report.columns = full_report.loc[0]
            full_report = full_report[1:]
            
            solution_report = full_report[full_report["error"] == ""]
            solution_report = solution_report.sort_values(by="cost")
            
            best_solution = solution_report.iloc[0,:].to_dict() if len(solution_report)>0 else None
            
            return full_report, solution_report, best_solution
        