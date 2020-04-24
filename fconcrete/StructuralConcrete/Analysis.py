from fconcrete.helpers import printProgressBar
import numpy as np
import pandas as pd
import time

class Analysis:

    @staticmethod
    def create_samples(kwargs, sort_by_multiplication, must_test_for_each):
        possible_values = []
        for kwarg_value in kwargs.values():
            possible_values = [*possible_values, np.arange(*kwarg_value)] if (len(kwarg_value) == 3 and type(kwarg_value)==tuple) else [*possible_values, kwarg_value]

        combinations = np.array(np.meshgrid(*possible_values)).T.reshape(-1,len(possible_values))
        combinations_table = pd.DataFrame(combinations, columns=kwargs.keys())

        # sorting the combinations
        if sort_by_multiplication:
            combinations_table["multiply"] = combinations_table.apply(lambda row: np.array([ v for k, v in row.to_dict().items() if k not in must_test_for_each ]).prod(), axis=1)
            combinations_table = combinations_table.sort_values(by=[*must_test_for_each, "multiply"])
            combinations_table = combinations_table.drop(columns="multiply")
        else:
            combinations_table = combinations_table.sort_values(by=must_test_for_each)

        combinations_table.reset_index(inplace=True, drop=True)

        return combinations_table

    @staticmethod
    def _checkNextStep(combination_kwarg, step, must_test_for_each, combinations_table):
        current_must_test_for_each = { k: v for k, v in combination_kwarg.items() if k in must_test_for_each }
        current_to_test_table = combinations_table.loc[step+1:]
        if len(current_to_test_table)==0: return
        step = np.inf
        for k in current_must_test_for_each.keys():
            new_table = current_to_test_table[current_to_test_table[k] > combination_kwarg[k]]
            if len(new_table)==0: return
            new_index_p = new_table.iloc[0].name
            step = min(step, new_index_p)
        if len(new_table)==0: return
        return step
    
    @staticmethod
    def getBestSolution(concrete_beam_function,
                max_steps_without_decrease = float("inf"),
                avoid_estimate=False,
                show_progress=True,
                sort_by_multiplication=False,
                must_test_for_each=[],
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
                
            must_test_for_each: list, optional
                From the kwargs parameters, define the ones that must be tested for all their values.
                Useful, for example, when you want to test for all possible lengths, but not all height and width.
            
            kwargs
                Possible arguments for the concrete_beam_function.
                If a set of 3 elements is given, np.arange(\*kwarg_value) will be called.
                The kwargs must have the same name that the concrete_beam_function expects as arguments.
                The combination is made with np.meshgrid.
            
                
        """
        
        combinations_table = Analysis.create_samples(kwargs, sort_by_multiplication, must_test_for_each)
        total_of_combinations = len(combinations_table)

        if avoid_estimate == False:
            max_variable_values = combinations_table.iloc[-1].to_dict()
            try:
                one_precesing_time, not_precise = concrete_beam_function(**max_variable_values).processing_time, False
            except:
                one_precesing_time, not_precise = 80, True
            continue_script = input("There are {} combinations. The estimate time to process all of them is {}s ({} minutes).{}\nType 'y' to continue or another char to cancel.\n".format(total_of_combinations, round(total_of_combinations*one_precesing_time), round(total_of_combinations*one_precesing_time/60), "\nThis measure is not precise!\n" if not_precise else ""))         
            
        if avoid_estimate!=False or continue_script=="y":
            start_time = time.time()
            report = pd.DataFrame(columns=[*list(kwargs.keys()), "cost", "error", 'Concrete', 'Longitudinal bar', 'Transversal bar'])
            min_value, steps_without_decrease, step = np.inf, 0, 0

            while step<total_of_combinations:
                combination_kwarg = combinations_table.loc[step].to_dict()
                try:
                    beam = concrete_beam_function(**combination_kwarg)
                    error, cost = "", beam.cost
                    cost_table = list(beam.subtotal_table[:, 1:2].T[0][1:].astype(float))
                except Exception as excep:
                    error, cost, cost_table = str(excep), -1, [-1, -1, -1]
                    
                report.loc[step] = [*combination_kwarg.values(), cost, error, *cost_table]
                
                if (cost != -1) and (cost != min(cost, min_value)):
                    steps_without_decrease += 1
                    if steps_without_decrease >= max_steps_without_decrease:
                        step = Analysis._checkNextStep(combination_kwarg, step, must_test_for_each, combinations_table)
                        if step == None: break
                        steps_without_decrease = 0
                        continue
                else:
                    steps_without_decrease, min_value = 0, cost
                
                if show_progress: printProgressBar(step + 1, total_of_combinations, prefix = 'Progress:', suffix = 'Complete', length = 50)
                
                step+=1
                    
            full_report = report.copy()
            solution_report = report[report["error"] == ""]
            solution_report = solution_report.sort_values(by="cost")
            if len(solution_report)>0:
                if len(must_test_for_each)==0:
                    best_solution = solution_report.iloc[0]
                else:
                    best_solution = solution_report.drop_duplicates(subset=must_test_for_each) 
            else:
                best_solution = None
            
            end_time = time.time()
            
            if show_progress: printProgressBar(total_of_combinations, total_of_combinations, prefix = 'Progress:', suffix = 'Complete', length = 50)
            if show_progress: print("Executed in {}s".format(end_time-start_time))
            
            return full_report, solution_report, best_solution
        
    