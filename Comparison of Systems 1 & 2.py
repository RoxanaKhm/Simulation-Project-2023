"""
This is a code to further investigate two system configurations for the insurance center and compare their performance
based on following performance measures:
1. Mean Photography Server Utilization
2. Mean Total Time Spent in System
3. Outside Maximum Queue Length.
4. Complaint Maximum Queue Length.
5. Mean Documentation Queue Waiting Time
6. Mean Departure Queue Waiting Time

Finally, the superior system design in each category is introduced.

Authors:
1. Roxana Khabbaz Zadeh Moghaddam
2. Ehsan Kehtari

Date: 08/03/2023
"""


import math
import numpy as np
import scipy.stats
from Phase3_System1 import simulation as system1_simulation
from Phase3_System2 import simulation as system2_simulation


def statistics(system_performance_measures_dictionary):
    global replication_num
    global list_of_measures
    performance_measures_statistics = dict()
    performance_measures_array = np.zeros([replication_num, 6], dtype=float)
    # Put measures in array
    for replication_idx, replication in enumerate(list(system_performance_measures_dictionary.keys())):
        for measure_idx, measure in enumerate(list(system_performance_measures_dictionary[replication].keys())):
            performance_measures_array[replication_idx, measure_idx] += \
                system_performance_measures_dictionary[replication][measure]

    # Compute mean & variance
    measures_mean = np.mean(performance_measures_array, axis=0).reshape((1, -1))
    measures_variance = np.var(performance_measures_array, axis=0).reshape((1, -1))

    # Add statistics for each measure to performance_measures_statistics
    for measure_idx, measure in enumerate(list_of_measures):
        performance_measures_statistics[measure] = [measures_mean[0, measure_idx], measures_variance[0, measure_idx]]

    return performance_measures_statistics


def system_designs_statistical_analysis(systems_performance_measures, n_digits=3):
    global list_of_measures
    global list_of_superiority_direction
    global alpha
    global replication_num
    # Obtain systems' performance measures' mean and variance
    system1_performance_measures_statistics = statistics(systems_performance_measures['System 1'])
    system2_performance_measures_statistics = statistics(systems_performance_measures['System 2'])

    # Do statistical tests with respect to each performance measure
    for measure_idx, measure in enumerate(list_of_measures):
        system1_measure_mean = system1_performance_measures_statistics[measure][0]
        system1_measure_variance = system1_performance_measures_statistics[measure][1]

        system2_measure_mean = system2_performance_measures_statistics[measure][0]
        system2_measure_variance = system2_performance_measures_statistics[measure][1]

        # Compute t_value
        degree_of_freedom = (((system1_measure_variance + system2_measure_variance) / replication_num) ** 2) / \
                            (((system1_measure_variance / replication_num) ** 2) / (replication_num - 1) +
                             ((system2_measure_variance / replication_num) ** 2) / (replication_num - 1))
        proba = 1 - (alpha / 2)

        t_value = scipy.stats.t.ppf(q=proba, df=degree_of_freedom)

        # Compute C.I.
        pooled_mean = system1_measure_mean - system2_measure_mean
        lower_bound = pooled_mean - \
                      (t_value * math.sqrt((system1_measure_variance + system2_measure_variance) / replication_num))
        upper_bound = pooled_mean + \
                      (t_value * math.sqrt((system1_measure_variance + system2_measure_variance) / replication_num))

        print('---------------------------------------------------------------------------------------')
        print('\033[1;0m C.I. from ' +
              '\x1B[3m' +
              '\x1B[1m' +
              str(measure) +
              '\x1B[0m' +
              '\033[1;0m point of view is (' +
              str(round(lower_bound, n_digits)) +
              ',' +
              str(round(upper_bound, n_digits)) +
              ');')

        # Final judgment
        if lower_bound > 0:
            if list_of_superiority_direction[measure_idx]:
                print('>>> strong statistical evidence for\033[1;32m system 1\033[1;0m superiority.')
            else:
                print('>>> strong statistical evidence for\033[1;32m system 2\033[1;0m superiority.')
        elif upper_bound < 0:
            if list_of_superiority_direction[measure_idx]:
                print('>>> strong statistical evidence for\033[1;32m system 2\033[1;0m superiority.')
            else:
                print('>>> strong statistical evidence for\033[1;32m system 1\033[1;0m superiority.')
        else:
            print('>>> no strong statistical evidence that one system design is better than the other.')

    print('---------------------------------------------------------------------------------------')


# Define simulation end_clock and cold_end_clock for systems 1 & 2 separately
# System 1
system1_end_day = 610
system1_cold_end_day = 55
system1_end_clock = system1_end_day * 1440
system1_cold_end_clock = system1_cold_end_day * 1440
# System 2
system2_end_day = 750
system2_cold_end_day = 67
system2_end_clock = system2_end_day * 1440
system2_cold_end_clock = system2_cold_end_day * 1440

# Define statistical test parameters for the comparison among two system designs
alpha = .05
replication_num = 10

# A list containing the names of all performance measures
list_of_measures = [
    'Mean Photography Server Utilization',
    'Mean Total Time Spent in System',
    'Outside Maximum Queue Length',
    'Complaint Maximum Queue Length',
    'Mean Documentation Queue Waiting Time',
    'Mean Departure Queue Waiting Time'
]
# A list of superiority direction based on measures stated above
list_of_superiority_direction = [
    True, False, False, False, False, False
]

# A dictionary to store performance measure for each replication
replication_specific_performance_measures = dict()
replication_specific_performance_measures['System 1'] = dict()
replication_specific_performance_measures['System 2'] = dict()

# Execute simulation for the specified number of replications among two system designs
# System 1
for replication in range(1, replication_num + 1):
    _, replication_specific_performance_measures['System 1']['Replication ' + str(replication)] = \
        system1_simulation(
            system1_end_clock,
            system1_cold_end_clock
        )

# System 2
for replication in range(1, replication_num + 1):
    _, replication_specific_performance_measures['System 2']['Replication ' + str(replication)] = \
        system2_simulation(
            system2_end_clock,
            system2_cold_end_clock
        )

# Compare system designs
system_designs_statistical_analysis(
    replication_specific_performance_measures
)
