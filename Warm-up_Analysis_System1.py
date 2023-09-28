"""
This is a code to implement warm-up analysis for system 1.
Normal and moving average for outside, documentation, departure and inspection units are plotted to
collectively decide on the instance system 1 enters warm state.

Authors:
1. Roxana Khabbaz Zadeh Moghaddam
2. Ehsan Kehtari

Date: 08/03/2023
"""


import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib as mpl
from Phase3_System1 import simulation

# Set font and font size
mpl.rc('font', family='Times New Roman')
mpl.rc('font', size=12)

# Create an empty figure with four subplots
fig, ax = plt.subplots(nrows=4, ncols=1, figsize=(8, 6))

# Set up a data structure to save required outputs in each replication
replication_queue_length_frame_outputs = dict()

replication_queue_length_frame_outputs['Outside'] = dict()  # keys are replications
replication_queue_length_frame_outputs['Documentation'] = dict()  # keys are replications
replication_queue_length_frame_outputs['Departure'] = dict()  # keys are replications
replication_queue_length_frame_outputs['Inspection'] = dict()  # keys are replications

# Function to calculate moving average of a list over a sliding window of length m.
def moving_average(input_list, m):
    output_list = []
    n = len(input_list)
    for i in range(n):
        output_list.append(sum(input_list[max(i - m // 2, 2 * i - n + 1, 0):min(i + m // 2 + 1, 2 * i + 1, n)]) / (
                min(i + m // 2, 2 * i, n - 1) - max(i - m // 2, 2 * i - n + 1, 0) + 1))
    return output_list


def calculate_queue_length_by_time_frame(start_time, end_time, queue, data):
    mean_queue_length = 0
    frame_previous_time = start_time
    for discrete_time in list(data['Cold Queue length Analysis'][queue].keys()):
        if discrete_time <= start_time:
            # Too soon to start calculating time-weighted sum of queue length
            frame_previous_queue_length = data['Cold Queue length Analysis'][queue][discrete_time]
        elif start_time < discrete_time <= end_time:
            mean_queue_length += frame_previous_queue_length * (discrete_time - frame_previous_time)
            frame_previous_time = discrete_time
            frame_previous_queue_length = data['Cold Queue length Analysis'][queue][discrete_time]
        else:
            mean_queue_length += frame_previous_queue_length * (end_time - frame_previous_time)
            break

    mean_queue_length /= (end_time - start_time)
    return mean_queue_length

# Initialize parameters
num_of_replications = 25
num_of_days = 120
frame_length = 300
window_size = 9
tick_spacing = 20

simulation_time = num_of_days * 1440
# Just use the frames with full information (drop last 2 frames)
num_of_frames = simulation_time // frame_length - 2
x = [i for i in range(1, num_of_frames + 1)]

for replication in range(1, num_of_replications + 1):
    # Run simulation for a desired length of time
    simulation_data, _ = simulation(simulation_time)

    for queue in list(replication_queue_length_frame_outputs.keys()):
        replication_queue_length_frame_outputs[queue][replication] = []

    # Do calculations frame by frame
    for time in range(0, num_of_frames * frame_length, frame_length):
        for queue in list(replication_queue_length_frame_outputs.keys()):
            replication_queue_length_frame_outputs[queue][replication].append(
                calculate_queue_length_by_time_frame(time, time + frame_length, queue, simulation_data)
            )

cross_replication_queue_length_frame_outputs_average = dict()
cross_replication_queue_length_frame_outputs_average['Outside'] = list()
cross_replication_queue_length_frame_outputs_average['Documentation'] = list()
cross_replication_queue_length_frame_outputs_average['Departure'] = list()
cross_replication_queue_length_frame_outputs_average['Inspection'] = list()

single_frame_cross_replication_average = dict()

for i in range(num_of_frames):
    single_frame_cross_replication_average['Outside'] = 0
    single_frame_cross_replication_average['Documentation'] = 0
    single_frame_cross_replication_average['Departure'] = 0
    single_frame_cross_replication_average['Inspection'] = 0

    for replication in range(1, num_of_replications + 1):
        for queue in list(single_frame_cross_replication_average.keys()):
            single_frame_cross_replication_average[queue] += \
                replication_queue_length_frame_outputs[queue][replication][i] * (1 / num_of_replications)

    for queue in list(cross_replication_queue_length_frame_outputs_average.keys()):
        cross_replication_queue_length_frame_outputs_average[queue].append(
            single_frame_cross_replication_average[queue]
        )

moving_replication_average = dict()
for queue in list(cross_replication_queue_length_frame_outputs_average.keys()):
    moving_replication_average[queue] = moving_average(
        cross_replication_queue_length_frame_outputs_average[queue], window_size
    )


fig.suptitle(f'Warm-up analysis over {num_of_replications} replications - System 1')

for plot_num, queue in enumerate(list(moving_replication_average.keys())):
    ax[plot_num].plot(x, cross_replication_queue_length_frame_outputs_average[queue],
                      'r', linewidth=5, label="Average across replications")
    ax[plot_num].plot(x, moving_replication_average[queue], 'k', label=f'Moving average (m = {window_size})')
    ax[plot_num].set_title(str(queue) + ' Queue Length')
    ax[plot_num].set_xlabel('Frame No.')
    ax[plot_num].set_ylabel('Queue Length')
    ax[plot_num].xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    ax[plot_num].legend()

fig.tight_layout()
fig.show()
fig.savefig('Insurance Center System 1 - Warm-up analysis - Time-Frame Approach')

