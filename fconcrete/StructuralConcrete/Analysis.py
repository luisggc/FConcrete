from fconcrete.helpers import printProgressBar
import numpy as np

class Analysis:
    @staticmethod
    def getBestSolution(concrete_beam_function,
                max_steps_without_decrease = float("inf"),
                avoid_estimate=False,
                show_progress=True,
                sort_by_multiplication=False,
                **kwargs):

        possible_values = []
        for kwarg_value in kwargs.values():
            possible_values = [*possible_values, np.arange(*kwarg_value)] if len(kwarg_value) == 3 else [*possible_values, kwarg_value]
                
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
                    cost_table = []
                
                if show_progress: printProgressBar(step + 1, total_of_combinations, prefix = 'Progress:', suffix = 'Complete', length = 50)
                row = [*combination_kwarg.values(), cost, error, *cost_table]
                report = [*report, row]
                
            return report