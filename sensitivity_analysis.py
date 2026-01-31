from network_model import NetworkModel
import random
import copy 
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
import os

# # make sure 'plots' directory exists to save plots in
os.makedirs('plots', exist_ok=True)

def max_absolute_difference(lst):
    """
    Returns the maximum absolute difference |lst[i] - lst[i+1]| such that i in {0,1,...,len(lst)-2}
    """
    max_diff = 0
    for i in range(0,len(lst)-1):
        diff = abs(lst[i]-lst[i+1])
        if diff > max_diff:
            max_diff = diff
    return max_diff

def make_range_0_upper_bound(perturbation_size, upper_bound):
    """
    returns a list of values from 0 (including) to upper_bound (including) with step size pertubation_size*upper_bound
    """
    step = upper_bound * perturbation_size
    values = []

    x = 0.0
    while x <= upper_bound:
        values.append(x)
        x += step

    # make sure that upper_bound is also included
    if values[-1] < upper_bound:
        values.append(upper_bound)

    return values

def f(params):
    """
    returns amount of susceptible persons after 10 years and input parameters (params)
    :params:    dictionary with as items the parameters names and as keys their values 
    """
    # Parameters that assume their default values
    model = NetworkModel()

    model.rng = random.Random(None)
    model.network_seed = None
    model.states_per_time = []

    model.seed = None
    model.num_nodes = 1000
    model.mode = "standard" # # <-
    model.prep_amount = 0.3
    model.infection_multipliers = {'acute': 26, 'chronic': 1, 'aids': 7}
    model.acute_to_chronic = 12
    model.infection_to_aids = 52*8.5
    
    # Parameters that may be altered in the sensitivity analysis
    model.initial_outbreak_proportion = params["initial_outbreak_proportion"]
    model.virus_spread_msm = params["virus_spread_msm"]
    model.virus_spread_msf = params["virus_spread_msf"]
    model.virus_spread_fsm = params["virus_spread_fsm"]
    model.virus_spread_fsf = params["virus_spread_fsf"]
    model.prep_multiplier = params["prep_multiplier"]
    model.art_multiplier = params["art_multiplier"]
    model.check_frequencies = params["check_frequencies"]
    model.sexual_frequencies = params["sexual_frequencies"]
    model.condom_usage = params["condom_usage"]
    model.condom_efficacy = params["condom_efficacy"]
    model.infection_chances = params["infection_chances"]
    model.intervention_multipliers = params["intervention_multipliers"]
  
    for t in range(520):
        model.step()
    
    return model.count_states()["susceptible"]

def calculate_max_deviation(parameters, pertubation_size):
    """
    Let k = pertubation_size*maximal_value_of_parameter for some parameter for which is_analysed == True,
    the function calculates

    f(params(y)):   f evaluated at default parameter values, except that there is exactly one variable with value set to y for which 
                    y is a multiple of k, by that is meant f is evaluated at params(x)
    f(params(x)):   f evaluated at params(x) except that x  = y - k 
    f(params(z)):   f evaluated at params(x) except that  z  = y + k 

    and calculates  max({|f(params(x))-f(params(y))| : x,y are in the domain of f} ∪ {f(params(y)) - f(params(z)) : y, z in the domain of f})
    that it stores  as value in the max_dev_dict with as key the name of the variable that was varied.

    :pertubation_size:  by what proportion of the variable's maximum value the variable will be pertubated
    :parameters:        dictionary with as keys the parameter names and as items their default values 
    """
    max_dev_dict = dict()
    default_parameters = copy.deepcopy(parameters)
    
    # Create a range from 0 (including) to 1 (including) of step size pertubation_size
    proportional_range = make_range_0_upper_bound(perturbation_size=pertubation_size, upper_bound=1)
    
    for param_name, default_value in parameters.items():

        if isinstance(default_value, dict):

            if param_name == "sexual_frequencies": # the range of sexual frequency is assumed to be [0,70]
                max_dev_dict[param_name] = dict()
                for inner_param_name, inner_default_value in default_value.items():
                    # pertubate the inner_default value by pertubation_size*70
                    var_range = make_range_0_upper_bound(perturbation_size=pertubation_size, upper_bound=70)

                    f_values = []
                    for var_val in var_range:
                        default_parameters = copy.deepcopy(parameters)
                        default_parameters[param_name][inner_param_name] = var_val 
                        f_values.append(f(default_parameters))

                    # calculate the biggest absolute difference and update the max_dev_dict
                    max_diff = max_absolute_difference(f_values)
                    max_dev_dict[param_name][inner_param_name] = max_diff
                    
            else: # the range of the inner_default_values is [0,1]
                max_dev_dict[param_name] = dict()
                for inner_param_name, inner_default_value in default_value.items():

                    f_values = []
                    for var_val in proportional_range:
                        default_parameters = copy.deepcopy(parameters)
                        default_parameters[param_name][inner_param_name] = var_val
                        f_values.append(f(default_parameters))
                    
                    max_diff = max_absolute_difference(f_values)
                    max_dev_dict[param_name][inner_param_name] = max_diff
                    
        else: # default_value is a float

            f_values = []
            for var_val in proportional_range:
                default_parameters = copy.deepcopy(parameters)
                default_parameters[param_name] = var_val
                f_values.append(f(default_parameters))

            max_diff = max_absolute_difference(f_values) 
            max_dev_dict[param_name] = max_diff
    return max_dev_dict

parameters = {
    "initial_outbreak_proportion" : 0.01,
    "virus_spread_msm" : 1.49/100,
    "virus_spread_msf" : 0.08/100,
    "virus_spread_fsm" : 0.04/100,
    "virus_spread_fsf" : 0.0/100,
    "prep_multiplier" : 0.14,
    "art_multiplier" : 0.04,
    "check_frequencies" : {
            "female homosexual": 0.0,
            "male homosexual": 0.02,
            "female heterosexual": 0.004,
            "male heterosexual": 0.004,
            "female bisexual": 0.004,
            "male bisexual": 0.02,
        },
    "sexual_frequencies" : {
        "female homosexual": 1.25,
        "male homosexual": 2.25,
        "female heterosexual": 1.65,
        "male heterosexual": 1.65,
        "female bisexual": 1.65,
        "male bisexual": 2.25,
    },
    "condom_usage" : {'male-male': 0.258, 'male-female': 0.200, 
                    'female-male': 0.200, 'female-female': 0.0},
    "condom_efficacy" : {'male-male': 0.25, 'male-female': 0.20, 
                        'female-male': 0.20, 'female-female': 0.0},
    "infection_chances" : {'male-male': 1.49/100, 'male-female': 0.08/100, 
                        'female-male': 0.04/100, 'female-female': 0.0/100},
    "intervention_multipliers" : {'prep': 0.14, 'art': 0.04, 'none': 1}

}
    

# Result of sensitivity analysis which pertubated one parameter by 10% whilst keeping the other parameters at their default values:

analysis_results = {'initial_outbreak_proportion': 16,
 'virus_spread_msm': 25, 
'virus_spread_msf': 57,
 'virus_spread_fsm': 48, 
'virus_spread_fsf': 28, 
'prep_multiplier': 22,
 'art_multiplier': 24, 
'check_frequencies': {'female homosexual': 19, 'male homosexual': 46, 'female heterosexual': 31, 'male heterosexual': 18, 'female bisexual': 25, 'male bisexual': 27}, 
'sexual_frequencies': {'female homosexual': 26, 'male homosexual': 28, 'female heterosexual': 40, 'male heterosexual': 41, 'female bisexual': 23, 'male bisexual': 20}, 
'condom_usage': {'male-male': 37, 'male-female': 27, 'female-male': 46, 'female-female': 36}, 
'condom_efficacy': {'male-male': 15, 'male-female': 43, 'female-male': 22, 'female-female': 25}, 
'infection_chances': {'male-male': 40, 'male-female': 82, 'female-male': 52, 'female-female': 54}, 
'intervention_multipliers': {'prep': 28, 'art': 30, 'none': 12}
}

labels = []
values = []
list_of_parameters_that_cannot_be_altered = [
"condom_efficacy male-female",
"condom_efficacy female-female",
"condom_efficacy female-male",
"condom_efficacy male-male",
"infection_chances male-female",
"infection_chances female-female",
"infection_chances female-male",
"infection_chances male-male",
"virus_spread_msf",
"virus_spread_fsm",
"virus_spread_fsf",
"virus_spread_msm",
"sexual_frequencies male heterosexual",
"sexual_frequencies female heterosexual",
"sexual_frequencies male homosexual",
"sexual_frequencies female homosexual",
"sexual_frequencies male bisexual",
"sexual_frequencies female bisexual",
"intervention_multipliers art",
"intervention_multipliers prep",
"art_multiplier",
"prep_multiplier",
"initial_outbreak_proportion",
"intervention_multipliers none"
]
for key, val in analysis_results.items():
    if isinstance(val, dict):
        for subkey, subval in val.items():
            labels.append(f"{key} {subkey}")
            values.append(subval)
    else:
        labels.append(key)
        values.append(val)

# Sort by value (descending)
sorted_items = sorted(zip(labels, values), key=lambda x: x[1], reverse=True)
labels_sorted, values_sorted = zip(*sorted_items)
colors = [
    "#7b0306" if label in list_of_parameters_that_cannot_be_altered else "gray"
    for label in labels_sorted
]
labels_sorted = [label.replace("_", " ") for label in labels_sorted]
# Plot
plt.figure(figsize=(14, 6))
plt.bar(labels_sorted, values_sorted, color=colors)
legend_elements = [
    Patch(facecolor="#7b0306", label="Cannot be controlled by government policy"),
    Patch(facecolor="gray", label="Might be controlled by government policy")
]
plt.legend(handles=legend_elements)
plt.xticks(rotation=30, ha="right") 
plt.ylabel("Maximum deviation in susceptible population")
plt.title("Sensitivity Analysis (10% Parameter Perturbation)")
plt.tight_layout()
filename = 'plots/sensitivity_analysis.png'
plt.savefig(filename, dpi=300, bbox_inches='tight')
print(f"Saved: {filename}")
plt.show()
