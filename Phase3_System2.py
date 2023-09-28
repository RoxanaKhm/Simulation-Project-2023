"""
This is a simulation code for an insurance center.

In the event of an accident, two cars are involved, and they arrive simultaneously.
Initially, a photograph is taken of the cars as evidence. Subsequently, all the relevant information is compiled into
a document. In the next stage, a professional examines the file and provides a verdict.
Finally, once all the necessary procedures are completed and the case is closed, the cars can leave the center.

Following performance measures are collected to further analyze insurance center:
1. Mean Photography Server Utilization
2. Mean Total Time Spent in System
3. Outside Maximum Queue Length.
4. Complaint Maximum Queue Length.
5. Mean Documentation Queue Waiting Time
6. Mean Departure Queue Waiting Time


Authors:
1. Roxana Khabbaz Zadeh Moghaddam
2. Ehsan Kehtari

Date: 07/23/2023
"""


import random
import math
import pandas as pd

# random.seed(1)

inputs = dict()
# inputs['Precipitation Probability'] = 0.31
inputs['Single-Arrival Probability'] = 0
inputs['Sue Probability'] = 0
inputs['Photography Queue Capacity'] = 20  # Pairs of cars
"""
inputs['Arrival Rate'] = {'Rainy': {'8-10': 1., '10-13': 0.5, '13-15': 4., '15-18': 2.},
                          'Normal': {'8-10': 2., '10-13': 3., '13-15': 5., '15-18': 3.}}  # Minutes per arrival
"""
inputs['Arrival Rate'] = 3.2
inputs['Number of Servers'] = {'Photography': 2,
                               'Documentation': 4,
                               'Inspection': 3,
                               'Complaint': 1}
inputs['Distribution Parameter'] = {'Photography Service Time': 6.,  # Mean in minutes
                                    'Waiting Time for Second Arrival': 30.,  # Mean in minutes
                                    'Documentation Service Time': [6., 8., 10.],  # [minimum, most likely, maximum] in
                                    # minutes
                                    'Inspection Service Time': 8.,  # Mean in minutes
                                    'D1 Service Time': [3., 3.5, 4.],  # [minimum, most likely, maximum] in minutes
                                    'Complaint Service Time': 15.,  # Mean in minutes
                                    }

"""
def weather():
    random_number = random.random()
    weather_condition = str()
    if random_number <= inputs['Precipitation Probability']:
        weather_condition = 'Rainy'
    else:
        weather_condition = 'Normal'
    return weather_condition
"""


def exponential(parameter):
    random_number = random.random()
    random_variable = - parameter * math.log(random_number)
    return random_variable


def triangular(parameters):
    random_number = random.random()

    minimum = parameters[0]
    most_likely = parameters[1]
    maximum = parameters[2]

    random_variable = 0.
    parser = (most_likely - minimum) / (maximum - minimum)
    if random_number <= parser:
        random_variable += minimum + math.sqrt((most_likely - minimum) * (maximum - minimum) * random_number)
    else:
        random_variable += maximum - math.sqrt((maximum - minimum) * (maximum - most_likely) * (1 - random_number))
    return random_variable


def starting_state():
    # State variables
    state = dict()
    state['Server Status'] = dict()
    state['Queue Length'] = dict()
    state['Parking Status'] = 0

    # Server Status
    state['Server Status']['Photography'] = 0
    state['Server Status']['Documentation'] = 0
    state['Server Status']['Inspection'] = 0
    state['Server Status']['Complaint'] = 0

    # Queue Length
    state['Queue Length']['Outside'] = 0
    state['Queue Length']['Photography'] = 0
    state['Queue Length']['Documentation'] = 0
    state['Queue Length']['Departure'] = 0
    state['Queue Length']['Inspection'] = 0
    state['Queue Length']['Complaint'] = 0

    # Data: will save everything
    data = dict()
    data['Cold Queue length Analysis'] = dict()  # To track queue length of specific units and mark the end of cold state
    data['Customers'] = dict()  # To track each customer, saving their arrival time, time service begins, etc.
    data['Queue Customers'] = dict()  # Used to find first customer in each queue
    data['Last Time Queue Length Changed'] = dict()  # Needed to calculate area under queue length curve
    data['Last Time Empty'] = dict()  # used to calculate the duration parking or documentation queues are empty
    data['Cumulative Stats'] = dict()  # To store cumulative stats
    data['Total Time Spent in System'] = 0.  # Needed to calculate mean time spent in system
    # (i.e., nominator of the fraction)
    data['Total Paired Customers Serviced'] = 0  # Needed to calculate mean time spent in system
    # (i.e., denominator of the fraction)
    data['Previous Clock'] = 0.  # Needed to calculate mean server utilization for each unit

    # Cold Queue Length Analysis
    data['Cold Queue length Analysis']['Outside'] = dict()  # time (key): queue length (value)
    data['Cold Queue length Analysis']['Documentation'] = dict()  # time (key): queue length (value)
    data['Cold Queue length Analysis']['Departure'] = dict()  # time (key): queue length (value)
    data['Cold Queue length Analysis']['Inspection'] = dict()  # time (key): queue length (value)

    # Last Time Empty
    data['Last Time Empty']['Documentation'] = 0.
    data['Last Time Empty']['Parking'] = 0.

    # Queue Customers
    data['Queue Customers']['Outside'] = dict()  # Customer: Arrival in outside queue
    data['Queue Customers']['Parking'] = dict()  # Customer: Arrival in parking queue
    data['Queue Customers']['Photography'] = dict()  # Customer: Arrival in photography queue
    data['Queue Customers']['Documentation'] = dict()  # Customer: Arrival in documentation queue
    data['Queue Customers']['Departure'] = dict()  # Customer: Arrival in departure queue
    data['Queue Customers']['Inspection'] = dict()  # Customer: Arrival in inspection queue
    data['Queue Customers']['Complaint'] = dict()  # Customer: Arrival in complaint queue

    # Last Time Queue Length Changed
    data['Last Time Queue Length Changed']['Outside'] = 0.
    data['Last Time Queue Length Changed']['Photography'] = 0.
    data['Last Time Queue Length Changed']['Complaint'] = 0.
    data['Last Time Queue Length Changed']['Inspection'] = 0.

    # Cumulative Stats
    data['Cumulative Stats']['Empty Duration'] = dict()  # Used to calculate the probability of being empty
    data['Cumulative Stats']['Maximum Queue Time'] = dict()  # To calculate maximum time spent in each queue
    data['Cumulative Stats']['Service Starters'] = dict()  # To calculate mean queue waiting time for each unit
    # (i.e., denominator of the fraction)
    data['Cumulative Stats']['Queue Waiting Time'] = dict()  # To calculate mean queue waiting time for each unit
    # (i.e., nominator of the fraction)
    data['Cumulative Stats']['Maximum Queue Length'] = dict()  # To calculate maximum queue length for each unit
    data['Cumulative Stats']['Server Spare Time'] = dict()  # To calculate mean server utilization for each unit
    data['Cumulative Stats']['Area Under Queue Length Curve'] = dict()  # To calculate mean queue length for each unit
    #  (i.e., nominator of the fraction)

    # Cumulative Stats -> Empty Duration
    data['Cumulative Stats']['Empty Duration']['Documentation'] = 0.
    data['Cumulative Stats']['Empty Duration']['Parking'] = 0.

    # Cumulative Stats -> Maximum Queue Time
    data['Cumulative Stats']['Maximum Queue Time']['Outside'] = 0.
    data['Cumulative Stats']['Maximum Queue Time']['Photography'] = 0.
    data['Cumulative Stats']['Maximum Queue Time']['Complaint'] = 0.
    data['Cumulative Stats']['Maximum Queue Time']['Inspection'] = 0.

    # Cumulative Stats -> Service Starters
    data['Cumulative Stats']['Service Starters']['Outside'] = 0
    data['Cumulative Stats']['Service Starters']['Photography'] = 0
    data['Cumulative Stats']['Service Starters']['Documentation'] = 0
    data['Cumulative Stats']['Service Starters']['Departure'] = 0
    data['Cumulative Stats']['Service Starters']['Photography'] = 0
    data['Cumulative Stats']['Service Starters']['Complaint'] = 0
    data['Cumulative Stats']['Service Starters']['Inspection'] = 0

    # Cumulative Stats -> Queue Waiting Time
    data['Cumulative Stats']['Queue Waiting Time']['Outside'] = 0.
    data['Cumulative Stats']['Queue Waiting Time']['Photography'] = 0.
    data['Cumulative Stats']['Queue Waiting Time']['Documentation'] = 0.
    data['Cumulative Stats']['Queue Waiting Time']['Departure'] = 0.
    data['Cumulative Stats']['Queue Waiting Time']['Complaint'] = 0.
    data['Cumulative Stats']['Queue Waiting Time']['Inspection'] = 0.

    # Cumulative Stats -> Maximum Queue Length
    data['Cumulative Stats']['Maximum Queue Length']['Outside'] = 0
    data['Cumulative Stats']['Maximum Queue Length']['Photography'] = 0
    data['Cumulative Stats']['Maximum Queue Length']['Complaint'] = 0
    data['Cumulative Stats']['Maximum Queue Length']['Inspection'] = 0

    # Cumulative Stats -> Server Spare Time
    data['Cumulative Stats']['Server Spare Time']['Photography'] = 0.
    data['Cumulative Stats']['Server Spare Time']['Documentation'] = 0.
    data['Cumulative Stats']['Server Spare Time']['Inspection'] = 0.
    data['Cumulative Stats']['Server Spare Time']['Complaint'] = 0.

    # Cumulative Stats -> Area Under Queue Length Curve
    data['Cumulative Stats']['Area Under Queue Length Curve']['Outside'] = 0.
    data['Cumulative Stats']['Area Under Queue Length Curve']['Photography'] = 0.
    data['Cumulative Stats']['Area Under Queue Length Curve']['Complaint'] = 0.
    data['Cumulative Stats']['Area Under Queue Length Curve']['Inspection'] = 0.

    # Starting FEL
    future_event_list = list()

    # Determine arrival rate based on weather condition and arrival time interval
    # weather_condition = weather()
    param = inputs['Arrival Rate'] #  [weather_condition]['8-10']
    arrival_time = exponential(param)

    first_arrival_random_number = random.random()
    if first_arrival_random_number <= inputs['Single-Arrival Probability']:
        customer_type = 'Type I'
    else:
        customer_type = 'Type III'

    # Append first arrival and closing event to FEL
    future_event_list.append({'Event Type': 'Arrival',
                              'Event Time': arrival_time,
                              'Customer': 'C1',
                              'Customer Type': customer_type})
    """
        future_event_list.append({'Event Type': '6:00',
                              'Event Time': 600.,
                              'Customer': None,
                              'Customer Type': None})
    """

    return state, future_event_list, data


def fel_maker(future_event_list, event_type, clock,
              customer=None, customer_type=None, second_arrival=False, sued=False):
    if event_type == 'Arrival':
        # Second arrival is insensitive to weather conditions
        if second_arrival:
            param = inputs['Distribution Parameter']['Waiting Time for Second Arrival']
            event_time = clock + exponential(param)
            customer_type = 'Type II'

        # To find the suitable parameter, weather condition and clock interval is required
        else:
            param = inputs['Arrival Rate']
            event_time = clock + exponential(param)
            """
            weather_condition = weather()
            if clock <= (10 - 8) * 60:
                param = inputs['Arrival Rate'][weather_condition]['8-10']
                event_time = clock + exponential(param)
            elif (10 - 8) * 60 < clock <= (13 - 8) * 60:
                param = inputs['Arrival Rate'][weather_condition]['10-13']
                event_time = clock + exponential(param)
            elif (13 - 8) * 60 < clock <= (15 - 8) * 60:
                param = inputs['Arrival Rate'][weather_condition]['13-15']
                event_time = clock + exponential(param)
            elif (15 - 8) * 60 < clock <= (18 - 8) * 60:
                param = inputs['Arrival Rate'][weather_condition]['15-18']
                event_time = clock + exponential(param)
            """

            # Determine customer type (either single-arrival or paired-arrival)
            arrival_type_random_number = random.random()
            if arrival_type_random_number <= inputs['Single-Arrival Probability']:
                customer_type = 'Type I'
            else:
                customer_type = 'Type III'

    elif event_type == 'End of Photography':
        param = inputs['Distribution Parameter']['Photography Service Time']
        event_time = clock + exponential(param)

    elif event_type == 'End of Documentation':
        param = inputs['Distribution Parameter']['Documentation Service Time']
        event_time = clock + triangular(param)

    elif event_type == 'End of Inspection':
        param = inputs['Distribution Parameter']['Inspection Service Time']
        event_time = clock + exponential(param)

    elif event_type == 'End of Complaint':
        param = inputs['Distribution Parameter']['Complaint Service Time']
        event_time = clock + exponential(param)

    elif event_type == 'Departure':
        # Sue case changes service time distribution
        if sued:
            param = inputs['Distribution Parameter']['Documentation Service Time']
            event_time = clock + triangular(param)
        else:
            param = inputs['Distribution Parameter']['D1 Service Time']
            event_time = clock + triangular(param)

    new_event = {'Event Type': event_type,
                 'Event Time': event_time,
                 'Customer': customer,
                 'Customer Type': customer_type}

    future_event_list.append(new_event)


def arrival(future_event_list, state, clock, data, customer, customer_type):
    # Save arrival times & set default value of sue attribute for each pair of customers: False
    if customer_type != 'Type II':
        data['Customers'][customer] = dict()
        data['Customers'][customer]['Arrival Time'] = dict()
        # Sue attribute
        data['Customers'][customer]['Sue'] = False
        if customer_type != 'Type III':
            data['Customers'][customer]['Arrival Time']['First Car'] = clock
        else:
            data['Customers'][customer]['Arrival Time']['First Car'] = clock
            data['Customers'][customer]['Arrival Time']['Second Car'] = clock

    # Arrival of type ii customer means a dict has already been created
    else:
        data['Customers'][customer]['Arrival Time']['Second Car'] = clock

    if state['Server Status']['Photography'] < inputs['Number of Servers']['Photography']:
        # Arrival of type i customers implies a single customer with no companion
        if customer_type == 'Type I':
            # First arrivals before 18:00 are accepted
            if clock <= (18 - 8) * 60:
                # Mean outside queue waiting time
                data['Cumulative Stats']['Service Starters']['Outside'] += 1
                # Put customer in parking
                data['Queue Customers']['Parking'][customer] = dict()
                data['Queue Customers']['Parking'][customer]['First Arrival in Parking'] = clock
                data['Queue Customers']['Parking'][customer]['Second Arrival in Parking'] = False
                # Parking empty probability
                if state['Parking Status'] == 0:
                    parking_empty_duration = clock - data['Last Time Empty']['Parking']
                    data['Cumulative Stats']['Empty Duration']['Parking'] += parking_empty_duration
                    data['Last Time Empty']['Parking'] = clock
                state['Parking Status'] += 1
                # Schedule second arrival
                fel_maker(future_event_list, 'Arrival', clock, customer,
                          customer_type='Type II', second_arrival=True)
                # Schedule next customer arrival
                next_customer_to_arrive = 'C' + str(int(customer[1:]) + 1)
                fel_maker(future_event_list, 'Arrival', clock, next_customer_to_arrive)

        elif customer_type == 'Type II':
            # Note that customer type ii may arrive after 18:00 and photography servers be idle;
            # In such a case customer type i is removed from outside queue due to late arrival of type ii customer
            if customer in data['Queue Customers']['Parking']:
                # Mean outside queue waiting time
                data['Cumulative Stats']['Service Starters']['Outside'] += 1
                # Remove first-arrived customer from parking
                data['Queue Customers']['Parking'].pop(customer)
                state['Parking Status'] -= 1
                # Parking empty probability
                if state['Parking Status'] == 0:
                    data['Last Time Empty']['Parking'] = clock
                # Schedule end of photography
                fel_maker(future_event_list, 'End of Photography', clock, customer)
                state['Server Status']['Photography'] += 1
                # Mean photography queue waiting time
                data['Cumulative Stats']['Service Starters']['Photography'] += 1

        elif customer_type == 'Type III':
            # Mean outside queue waiting time
            data['Cumulative Stats']['Service Starters']['Outside'] += 2
            # Schedule end of photography
            fel_maker(future_event_list, 'End of Photography', clock, customer)
            state['Server Status']['Photography'] += 1
            # Mean photography queue waiting time
            data['Cumulative Stats']['Service Starters']['Photography'] += 1
            # Schedule next customer arrival
            next_customer_to_arrive = 'C' + str(int(customer[1:]) + 1)
            fel_maker(future_event_list, 'Arrival', clock, next_customer_to_arrive)

    # If state['Server Status']['Photography'] == inputs['Number of Servers']['Photography']
    else:
        if state['Queue Length']['Photography'] < inputs['Photography Queue Capacity']:
            # Arrival of type i customer implies a single customer with no companion
            if customer_type == 'Type I':
                # First arrivals before 18:00 are accepted
                if clock <= (18 - 8) * 60:
                    # Mean outside queue waiting time
                    data['Cumulative Stats']['Service Starters']['Outside'] += 1
                    # Put customer in parking
                    data['Queue Customers']['Parking'][customer] = dict()
                    data['Queue Customers']['Parking'][customer]['First Arrival in Parking'] = clock
                    data['Queue Customers']['Parking'][customer]['Second Arrival in Parking'] = False
                    # Parking empty probability
                    if state['Parking Status'] == 0:
                        parking_empty_duration = clock - data['Last Time Empty']['Parking']
                        data['Cumulative Stats']['Empty Duration']['Parking'] += parking_empty_duration
                        data['Last Time Empty']['Parking'] = clock
                    state['Parking Status'] += 1
                    # Schedule Second Arrival
                    fel_maker(future_event_list, 'Arrival', clock, customer,
                              customer_type='Type II', second_arrival=True)
                    # Schedule next customer arrival
                    next_customer_to_arrive = 'C' + str(int(customer[1:]) + 1)
                    fel_maker(future_event_list, 'Arrival', clock, next_customer_to_arrive)

            elif customer_type == 'Type II':
                # Note that customer type ii may arrive after 18:00 and photography queue hold less than its capacity;
                # In such a case customer type i is removed from outside queue due to late arrival of type ii customer
                if customer in data['Queue Customers']['Parking']:
                    # Mean outside queue waiting time
                    data['Cumulative Stats']['Service Starters']['Outside'] += 1
                    # Remove customer type i from parking
                    data['Queue Customers']['Parking'].pop(customer)
                    state['Parking Status'] -= 1
                    # Parking empty probability
                    if state['Parking Status'] == 0:
                        data['Last Time Empty']['Parking'] = clock
                    # Mean photography queue length
                    data['Cumulative Stats']['Area Under Queue Length Curve']['Photography'] += \
                        (clock - data['Last Time Queue Length Changed']['Photography']) * \
                        state['Queue Length']['Photography']
                    data['Last Time Queue Length Changed']['Photography'] = clock
                    # Add newly-paired customers to photography queue
                    state['Queue Length']['Photography'] += 1
                    data['Queue Customers']['Photography'][customer] = clock
                    # Maximum photography queue length
                    data['Cumulative Stats']['Maximum Queue Length']['Photography'] = \
                        max(data['Cumulative Stats']['Maximum Queue Length']['Photography'],
                            state['Queue Length']['Photography'])

            # if customer_type == 'Type III'
            else:
                # Mean outside queue waiting time
                data['Cumulative Stats']['Service Starters']['Outside'] += 2
                # Mean photography queue length
                data['Cumulative Stats']['Area Under Queue Length Curve']['Photography'] += \
                    (clock - data['Last Time Queue Length Changed']['Photography']) * \
                    state['Queue Length']['Photography']
                data['Last Time Queue Length Changed']['Photography'] = clock
                # Add paired customers to photography queue
                state['Queue Length']['Photography'] += 1
                data['Queue Customers']['Photography'][customer] = clock
                # Maximum photography queue length
                data['Cumulative Stats']['Maximum Queue Length']['Photography'] = \
                    max(data['Cumulative Stats']['Maximum Queue Length']['Photography'],
                        state['Queue Length']['Photography'])
                # Schedule next customer arrival
                next_customer_to_arrive = 'C' + str(int(customer[1:]) + 1)
                fel_maker(future_event_list, 'Arrival', clock, next_customer_to_arrive)

        # if state['Queue Length']['Photography'] == inputs['Photography Queue Capacity']
        else:
            if customer_type == 'Type I':
                # First arrivals before 18:00 are accepted
                if clock <= (18 - 8) * 60:
                    if state['Queue Length']['Outside'] == 0:
                        # Mean outside queue waiting time
                        data['Cumulative Stats']['Service Starters']['Outside'] += 1
                        # Put customer in parking
                        data['Queue Customers']['Parking'][customer] = dict()
                        data['Queue Customers']['Parking'][customer]['First Arrival in Parking'] = clock
                        data['Queue Customers']['Parking'][customer]['Second Arrival in Parking'] = False
                        # Parking empty probability
                        if state['Parking Status'] == 0:
                            parking_empty_duration = clock - data['Last Time Empty']['Parking']
                            data['Cumulative Stats']['Empty Duration']['Parking'] += parking_empty_duration
                            data['Last Time Empty']['Parking'] = clock
                        state['Parking Status'] += 1
                    else:
                        # Mean outside queue length
                        data['Cumulative Stats']['Area Under Queue Length Curve']['Outside'] += \
                            (clock - data['Last Time Queue Length Changed']['Outside']) * \
                            state['Queue Length']['Outside']
                        data['Last Time Queue Length Changed']['Outside'] = clock
                        # Put customer in outside queue
                        data['Queue Customers']['Outside'][customer] = dict()
                        data['Queue Customers']['Outside'][customer]['First Arrival in Outside'] = clock
                        data['Queue Customers']['Outside'][customer]['Second Arrival in Outside'] = False
                        state['Queue Length']['Outside'] += 1
                        # Maximum outside queue length
                        data['Cumulative Stats']['Maximum Queue Length']['Outside'] = \
                            max(
                                data['Cumulative Stats']['Maximum Queue Length']['Outside'],
                                state['Queue Length']['Outside']
                            )
                    # Schedule second arrival
                    fel_maker(future_event_list, 'Arrival', clock, customer,
                              customer_type='Type II', second_arrival=True)
                    # Schedule next customer arrival
                    next_customer_to_arrive = 'C' + str(int(customer[1:]) + 1)
                    fel_maker(future_event_list, 'Arrival', clock, next_customer_to_arrive)

            elif customer_type == 'Type II':
                if customer in data['Queue Customers']['Parking']:
                    data['Cumulative Stats']['Service Starters']['Outside'] += 1
                    data['Queue Customers']['Parking'][customer]['Second Arrival in Parking'] = clock

                # else is wrong, since first customer might've been removed from Outside queue due to late arrival of
                # second customer (i.e., after 18:00)
                if customer in data['Queue Customers']['Outside']:
                    # Mean outside queue length
                    data['Cumulative Stats']['Area Under Queue Length Curve']['Outside'] += \
                        (clock - data['Last Time Queue Length Changed']['Outside']) * \
                        state['Queue Length']['Outside']
                    data['Last Time Queue Length Changed']['Outside'] = clock
                    # Put customer right next to its pair in outside queue
                    data['Queue Customers']['Outside'][customer]['Second Arrival in Outside'] = clock
                    state['Queue Length']['Outside'] += 1
                    # Maximum outside queue length
                    data['Cumulative Stats']['Maximum Queue Length']['Outside'] = \
                        max(data['Cumulative Stats']['Maximum Queue Length']['Outside'],
                            state['Queue Length']['Outside'])

            # if customer_type == 'Type III'
            else:
                # Mean outside queue length
                data['Cumulative Stats']['Area Under Queue Length Curve']['Outside'] += \
                    (clock - data['Last Time Queue Length Changed']['Outside']) * \
                    state['Queue Length']['Outside']
                data['Last Time Queue Length Changed']['Outside'] = clock
                # Put customers in outside queue
                data['Queue Customers']['Outside'][customer] = dict()
                data['Queue Customers']['Outside'][customer]['First Arrival in Outside'] = clock
                data['Queue Customers']['Outside'][customer]['Second Arrival in Outside'] = clock
                state['Queue Length']['Outside'] += 2
                # Maximum outside queue length
                data['Cumulative Stats']['Maximum Queue Length']['Outside'] = \
                    max(data['Cumulative Stats']['Maximum Queue Length']['Outside'],
                        state['Queue Length']['Outside'])
                # Schedule next arrival
                next_customer_to_arrive = 'C' + str(int(customer[1:]) + 1)
                fel_maker(future_event_list, 'Arrival', clock, next_customer_to_arrive)


def end_of_photography(future_event_list, state, clock, data, customer):
    # Forward look to Documentation unit
    if state['Server Status']['Documentation'] < inputs['Number of Servers']['Documentation']:
        state['Server Status']['Documentation'] += 1
        # Mean documentation queue waiting time
        data['Cumulative Stats']['Service Starters']['Documentation'] += 1
        fel_maker(future_event_list, 'End of Documentation', clock, customer)

    # if state['Server Status']['Documentation'] == inputs['Number of Servers']['Documentation']
    else:
        # Empty documentation queue probability
        if state['Queue Length']['Documentation'] == 0:
            documentation_queue_empty_duration = clock - data['Last Time Empty']['Documentation']
            data['Cumulative Stats']['Empty Duration']['Documentation'] += documentation_queue_empty_duration
            data['Last Time Empty']['Documentation'] = clock
        # Put customers in documentation queue
        state['Queue Length']['Documentation'] += 1
        data['Queue Customers']['Documentation'][customer] = clock

    # Backward look from Photography unit
    if state['Queue Length']['Photography'] == 0:
        state['Server Status']['Photography'] -= 1
    else:
        # Find first customer in queue
        # Raises error if
        # photography queue length is not compatible with the length of data['Queue Customers']['Photography']
        first_customer_in_photography_queue = min(data['Queue Customers']['Photography'],
                                                  key=data['Queue Customers']['Photography'].get)
        # Mean waiting time in photography queue
        data['Cumulative Stats']['Queue Waiting Time']['Photography'] += \
            clock - data['Queue Customers']['Photography'][first_customer_in_photography_queue]
        # Maximum waiting time in photography queue
        data['Cumulative Stats']['Maximum Queue Time']['Photography'] = max(
            data['Cumulative Stats']['Maximum Queue Time']['Photography'],
            clock - data['Queue Customers']['Photography'][first_customer_in_photography_queue])
        # Remove this customer from queue
        # Further impacts on queue (mean & max photography queue length) postponed until no proper replacement found
        data['Queue Customers']['Photography'].pop(first_customer_in_photography_queue)
        # Schedule End of Photography for this customer (first_customer_in_queue)
        fel_maker(future_event_list, 'End of Photography', clock, first_customer_in_photography_queue)
        data['Cumulative Stats']['Service Starters']['Photography'] += 1

        # Fill the empty spot in photography queue
        # Paired customers in parking are in priority, then paired customers in outside queue

        # First find paired customers in parking
        paired_waiting_customers_in_parking = dict()
        for parking_customer in list(data['Queue Customers']['Parking'].keys()):
            if data['Queue Customers']['Parking'][parking_customer]['Second Arrival in Parking']:
                paired_waiting_customers_in_parking[parking_customer] = \
                    data['Queue Customers']['Parking'][parking_customer]['Second Arrival in Parking']

        # To check later if anyone was moved to photography queue
        is_paired_customer_found = False

        if len(paired_waiting_customers_in_parking) != 0:
            is_paired_customer_found = True
            first_customer_in_parking = min(paired_waiting_customers_in_parking,
                                            key=paired_waiting_customers_in_parking.get)
            # Remove customer from parking
            data['Queue Customers']['Parking'].pop(first_customer_in_parking)
            state['Parking Status'] -= 1
            # Parking empty probability
            if state['Parking Status'] == 0:
                data['Last Time Empty']['Parking'] = clock
            # Put first customers in photography queue
            data['Queue Customers']['Photography'][first_customer_in_parking] = clock

        # If no paired customers in parking
        else:
            current_outside_queue_length = len(data['Queue Customers']['Outside'])

            for i in range(current_outside_queue_length):
                # First create a temporary dictionary containing customers and their first arrival time in outside queue
                waiting_customers_in_outside = dict()
                for outside_customer in list(data['Queue Customers']['Outside'].keys()):
                    waiting_customers_in_outside[outside_customer] = \
                        data['Queue Customers']['Outside'][outside_customer]['First Arrival in Outside']
                # Find first customer in queue
                first_customer_in_outside_queue = min(waiting_customers_in_outside,
                                                      key=waiting_customers_in_outside.get)
                # Check if first customer in queue is paired
                if data['Queue Customers']['Outside'][first_customer_in_outside_queue]['Second Arrival in Outside']:
                    # Mean waiting time in outside queue;
                    # first customer's contribution to waiting time
                    data['Cumulative Stats']['Queue Waiting Time']['Outside'] += \
                        clock - data['Queue Customers']['Outside'][first_customer_in_outside_queue][
                            'First Arrival in Outside']
                    # second customer's contribution to waiting time
                    data['Cumulative Stats']['Queue Waiting Time']['Outside'] += \
                        clock - data['Queue Customers']['Outside'][first_customer_in_outside_queue][
                            'Second Arrival in Outside']
                    # Maximum waiting time in outside queue
                    data['Cumulative Stats']['Maximum Queue Time']['Outside'] = \
                        max(
                            data['Cumulative Stats']['Maximum Queue Time']['Outside'],
                            clock - data['Queue Customers']['Outside'][first_customer_in_outside_queue][
                                'First Arrival in Outside'],
                            clock - data['Queue Customers']['Outside'][first_customer_in_outside_queue][
                                'Second Arrival in Outside']
                        )
                    # Mean outside queue length
                    data['Cumulative Stats']['Area Under Queue Length Curve']['Outside'] += \
                        (clock - data['Last Time Queue Length Changed']['Outside']) * \
                        state['Queue Length']['Outside']
                    data['Last Time Queue Length Changed']['Outside'] = clock
                    # Remove first customer from outside queue
                    data['Queue Customers']['Outside'].pop(first_customer_in_outside_queue)
                    state['Queue Length']['Outside'] -= 2
                    # Put first paired-customers in photography queue
                    data['Cumulative Stats']['Service Starters']['Outside'] += 2
                    data['Queue Customers']['Photography'][first_customer_in_outside_queue] = clock
                    # Since paired-customers were found
                    is_paired_customer_found = True
                    # No more searching required, so break!
                    break

                # First customer is single, so put it in parking
                else:
                    # Mean waiting time in outside queue
                    data['Cumulative Stats']['Queue Waiting Time']['Outside'] += \
                        clock - data['Queue Customers']['Outside'][first_customer_in_outside_queue][
                            'First Arrival in Outside']
                    data['Cumulative Stats']['Service Starters']['Outside'] += 1
                    # Maximum waiting time in outside queue
                    data['Cumulative Stats']['Maximum Queue Time']['Outside'] = \
                        max(
                            data['Cumulative Stats']['Maximum Queue Time']['Outside'],
                            clock - data['Queue Customers']['Outside'][first_customer_in_outside_queue][
                                'First Arrival in Outside']
                        )
                    # Mean outside queue length
                    data['Cumulative Stats']['Area Under Queue Length Curve']['Outside'] += \
                        (clock - data['Last Time Queue Length Changed']['Outside']) * \
                        state['Queue Length']['Outside']
                    data['Last Time Queue Length Changed']['Outside'] = clock
                    # Remove first customer from outside queue
                    data['Queue Customers']['Outside'].pop(first_customer_in_outside_queue)
                    state['Queue Length']['Outside'] -= 1
                    # Put first customer in parking
                    data['Queue Customers']['Parking'][first_customer_in_outside_queue] = dict()
                    data['Queue Customers']['Parking'][first_customer_in_outside_queue]['First Arrival in Parking'] = \
                        clock
                    data['Queue Customers']['Parking'][first_customer_in_outside_queue]['Second Arrival in Parking'] = \
                        False
                    # Parking empty probability
                    if state['Parking Status'] == 0:
                        parking_empty_duration = clock - data['Last Time Empty']['Parking']
                        data['Cumulative Stats']['Empty Duration']['Parking'] += parking_empty_duration
                        data['Last Time Empty']['Parking'] = clock
                    state['Parking Status'] += 1

        # If not able to fill the empty spot in photography queue
        if not is_paired_customer_found:
            # Mean photography queue length
            data['Cumulative Stats']['Area Under Queue Length Curve']['Photography'] += \
                (clock - data['Last Time Queue Length Changed']['Photography']) * \
                state['Queue Length']['Photography']
            data['Last Time Queue Length Changed']['Photography'] = clock
            state['Queue Length']['Photography'] -= 1


def six_o_clock(state, data):
    clock = (18 - 8) * 60

    # Mean outside queue length
    data['Cumulative Stats']['Area Under Queue Length Curve']['Outside'] += \
        (clock - data['Last Time Queue Length Changed']['Outside']) * state['Queue Length']['Outside']
    data['Last Time Queue Length Changed']['Outside'] = clock

    # Empty outside
    current_outside_queue_length = len(data['Queue Customers']['Outside'])
    for j in range(current_outside_queue_length):
        # First create a temporary dictionary containing customers and their first arrival time in outside queue
        waiting_customers_in_outside = dict()
        for outside_customer in list(data['Queue Customers']['Outside'].keys()):
            waiting_customers_in_outside[outside_customer] = \
                data['Queue Customers']['Outside'][outside_customer]['First Arrival in Outside']
        # Find first customer in queue
        first_customer_in_outside_queue = min(waiting_customers_in_outside,
                                              key=waiting_customers_in_outside.get)
        # Mean waiting time in outside queue;
        # first customer's contribution to waiting time
        data['Cumulative Stats']['Queue Waiting Time']['Outside'] += \
            clock - data['Queue Customers']['Outside'][first_customer_in_outside_queue]['First Arrival in Outside']

        if data['Queue Customers']['Outside'][first_customer_in_outside_queue]['Second Arrival in Outside']:
            # second customer's contribution to waiting time
            data['Cumulative Stats']['Queue Waiting Time']['Outside'] += \
                clock - data['Queue Customers']['Outside'][first_customer_in_outside_queue]['Second Arrival in Outside']

        # Maximum waiting time in outside queue
        if data['Queue Customers']['Outside'][first_customer_in_outside_queue]['Second Arrival in Outside']:
            data['Cumulative Stats']['Maximum Queue Time']['Outside'] = \
                max(
                    data['Cumulative Stats']['Maximum Queue Time']['Outside'],
                    clock - data['Queue Customers']['Outside'][first_customer_in_outside_queue][
                        'First Arrival in Outside'],
                    clock - data['Queue Customers']['Outside'][first_customer_in_outside_queue][
                        'Second Arrival in Outside']
                )

        else:
            data['Cumulative Stats']['Maximum Queue Time']['Outside'] = \
                max(
                    data['Cumulative Stats']['Maximum Queue Time']['Outside'],
                    clock - data['Queue Customers']['Outside'][first_customer_in_outside_queue][
                        'First Arrival in Outside']
                )

        # Remove this customer from outside queue
        data['Queue Customers']['Outside'].pop(first_customer_in_outside_queue)

    state['Queue Length']['Outside'] = 0
    assert len(data['Queue Customers']['Outside']) == 0, "Outside queue not fully emptied"


def end_of_documentation(future_event_list, state, clock, data, customer):
    # Forward look to inspection unit
    if state['Server Status']['Inspection'] < inputs['Number of Servers']['Inspection']:
        state['Server Status']['Inspection'] += 1
        fel_maker(future_event_list, 'End of Inspection', clock, customer)
        data['Cumulative Stats']['Service Starters']['Inspection'] += 1

    # if state['Server Status']['Inspection'] == inputs['Number of Servers']['Inspection']
    else:
        # Mean inspection queue length
        data['Cumulative Stats']['Area Under Queue Length Curve']['Inspection'] += \
            (clock - data['Last Time Queue Length Changed']['Inspection']) * state['Queue Length']['Inspection']
        # Put customer in inspection queue
        state['Queue Length']['Inspection'] += 1
        data['Queue Customers']['Inspection'][customer] = clock
        # Maximum inspection queue length
        data['Cumulative Stats']['Maximum Queue Length']['Inspection'] = \
            max(
                data['Cumulative Stats']['Maximum Queue Length']['Inspection'],
                state['Queue Length']['Inspection']
            )

    # Backward look from documentation
    # Customers in departure queue are in priority
    if state['Queue Length']['Departure'] == 0:
        if state['Queue Length']['Documentation'] > 0:
            # Find first customer in documentation queue
            first_customer_in_documentation_queue = min(data['Queue Customers']['Documentation'],
                                                        key=data['Queue Customers']['Documentation'].get)
            # Mean documentation queue waiting time
            data['Cumulative Stats']['Queue Waiting Time']['Documentation'] += \
                clock - data['Queue Customers']['Documentation'][first_customer_in_documentation_queue]
            data['Cumulative Stats']['Service Starters']['Documentation'] += 1
            # Remove first customer from documentation queue
            data['Queue Customers']['Documentation'].pop(first_customer_in_documentation_queue)
            state['Queue Length']['Documentation'] -= 1
            # Empty documentation queue probability
            if state['Queue Length']['Documentation'] == 0:
                data['Last Time Empty']['Documentation'] = clock
            # Schedule end of documentation
            fel_maker(future_event_list, 'End of Documentation', clock, first_customer_in_documentation_queue)

        elif state['Queue Length']['Documentation'] == 0:
            state['Server Status']['Documentation'] -= 1

    elif state['Queue Length']['Departure'] > 0:
        # Find first customer in departure queue
        first_customer_in_departure_queue = min(data['Queue Customers']['Departure'],
                                                key=data['Queue Customers']['Departure'].get)
        # Mean departure queue waiting time
        data['Cumulative Stats']['Queue Waiting Time']['Departure'] += \
            clock - data['Queue Customers']['Departure'][first_customer_in_departure_queue]
        data['Cumulative Stats']['Service Starters']['Departure'] += 1
        # Remove first customer from departure queue
        data['Queue Customers']['Departure'].pop(first_customer_in_departure_queue)
        state['Queue Length']['Departure'] -= 1
        # Check for sue case
        if_sued = data['Customers'][first_customer_in_departure_queue]['Sue']
        # Schedule departure
        fel_maker(future_event_list, 'Departure', clock, first_customer_in_departure_queue, sued=if_sued)


def departure(future_event_list, state, clock, data, customer):
    # Save departure time for every pair of customers to later compute mean time spent in system
    data['Customers'][customer]['Departure Time'] = dict()
    data['Customers'][customer]['Departure Time']['First Car'] = clock
    data['Customers'][customer]['Departure Time']['Second Car'] = clock
    # compute and accumulate total time spent in system (cumulative stats)
    # First car's contribution
    data['Total Time Spent in System'] += \
        data['Customers'][customer]['Departure Time']['First Car'] - \
        data['Customers'][customer]['Arrival Time']['First Car']
    # Second car's contribution
    data['Total Time Spent in System'] += \
        data['Customers'][customer]['Departure Time']['Second Car'] - \
        data['Customers'][customer]['Arrival Time']['Second Car']
    # Increase total paired customers serviced
    data['Total Paired Customers Serviced'] += 1

    # Backward look from documentation
    # Customers in departure queue are in priority
    if state['Queue Length']['Departure'] == 0:
        if state['Queue Length']['Documentation'] > 0:
            # Find first customer in documentation queue
            first_customer_in_documentation_queue = min(data['Queue Customers']['Documentation'],
                                                        key=data['Queue Customers']['Documentation'].get)
            # Mean documentation queue waiting time
            data['Cumulative Stats']['Queue Waiting Time']['Documentation'] += \
                clock - data['Queue Customers']['Documentation'][first_customer_in_documentation_queue]
            data['Cumulative Stats']['Service Starters']['Documentation'] += 1
            # Remove first customer from documentation queue
            data['Queue Customers']['Documentation'].pop(first_customer_in_documentation_queue)
            state['Queue Length']['Documentation'] -= 1
            # Empty documentation queue probability
            if state['Queue Length']['Documentation'] == 0:
                data['Last Time Empty']['Documentation'] = clock
            # Schedule end of documentation
            fel_maker(future_event_list, 'End of Documentation', clock, first_customer_in_documentation_queue)

        elif state['Queue Length']['Documentation'] == 0:
            state['Server Status']['Documentation'] -= 1

    elif state['Queue Length']['Departure'] > 0:
        # Find first customer in departure queue
        first_customer_in_departure_queue = min(data['Queue Customers']['Departure'],
                                                key=data['Queue Customers']['Departure'].get)
        # Mean departure queue waiting time
        data['Cumulative Stats']['Queue Waiting Time']['Departure'] += \
            clock - data['Queue Customers']['Departure'][first_customer_in_departure_queue]
        data['Cumulative Stats']['Service Starters']['Departure'] += 1
        # Remove first customer from departure queue
        data['Queue Customers']['Departure'].pop(first_customer_in_departure_queue)
        state['Queue Length']['Departure'] -= 1
        # Check for sue case
        if_sued = data['Customers'][first_customer_in_departure_queue]['Sue']
        # Schedule departure
        fel_maker(future_event_list, 'Departure', clock, first_customer_in_departure_queue, sued=if_sued)


def end_of_inspection(future_event_list, state, clock, data, customer):
    # Forward look to complaint or departure; Based on customer type 'sue'
    # If already sued, send it to documentation completion (departure)
    if data['Customers'][customer]['Sue']:
        if state['Server Status']['Documentation'] < inputs['Number of Servers']['Documentation']:
            state['Server Status']['Documentation'] += 1
            # Mean departure queue waiting time
            data['Cumulative Stats']['Service Starters']['Departure'] += 1
            fel_maker(future_event_list, 'Departure', clock, customer, sued=True)
        elif state['Server Status']['Documentation'] == inputs['Number of Servers']['Documentation']:
            data['Queue Customers']['Departure'][customer] = clock
            state['Queue Length']['Departure'] += 1
    # If customer comes from documentation, decide on whether to sue
    else:
        sue = random.random()

        if sue <= inputs['Sue Probability']:
            data['Customers'][customer]['Sue'] = True

            if state['Server Status']['Complaint'] < inputs['Number of Servers']['Complaint']:
                state['Server Status']['Complaint'] += 1
                # Schedule end of complaint
                fel_maker(future_event_list, 'End of Complaint', clock, customer)
                # Mean waiting time in complaint queue
                data['Cumulative Stats']['Service Starters']['Complaint'] += 1

            elif state['Server Status']['Complaint'] == inputs['Number of Servers']['Complaint']:
                # Mean complaint queue length
                data['Cumulative Stats']['Area Under Queue Length Curve']['Complaint'] += \
                    (clock - data['Last Time Queue Length Changed']['Complaint']) * state['Queue Length']['Complaint']
                data['Last Time Queue Length Changed']['Complaint'] = clock
                # Put customer in complaint queue
                state['Queue Length']['Complaint'] += 1
                data['Queue Customers']['Complaint'][customer] = clock
                # Maximum complaint queue length
                data['Cumulative Stats']['Maximum Queue Length']['Complaint'] = \
                    max(
                        data['Cumulative Stats']['Maximum Queue Length']['Complaint'],
                        state['Queue Length']['Complaint']
                    )

        elif sue > inputs['Sue Probability']:
            if state['Server Status']['Documentation'] < inputs['Number of Servers']['Documentation']:
                state['Server Status']['Documentation'] += 1
                # Mean departure Queue waiting time
                data['Cumulative Stats']['Service Starters']['Departure'] += 1
                # Schedule departure
                fel_maker(future_event_list, 'Departure', clock, customer)

            elif state['Server Status']['Documentation'] == inputs['Number of Servers']['Documentation']:
                # Put customer in departure queue
                data['Queue Customers']['Departure'][customer] = clock
                state['Queue Length']['Departure'] += 1

    # Backward look from inspection
    if state['Queue Length']['Inspection'] == 0:
        state['Server Status']['Inspection'] -= 1

    elif state['Queue Length']['Inspection'] > 0:
        # Find first customer in queue
        # Raises error if
        # inspection queue length is not compatible with the length of data['Queue Customers']['Inspection']
        first_customer_in_inspection_queue = min(data['Queue Customers']['Inspection'],
                                                 key=data['Queue Customers']['Inspection'].get)
        # Mean waiting time in inspection queue
        data['Cumulative Stats']['Queue Waiting Time']['Inspection'] += \
            clock - data['Queue Customers']['Inspection'][first_customer_in_inspection_queue]
        # Maximum waiting time in inspection queue
        data['Cumulative Stats']['Maximum Queue Time']['Inspection'] = \
            max(
                data['Cumulative Stats']['Maximum Queue Time']['Inspection'],
                clock - data['Queue Customers']['Inspection'][first_customer_in_inspection_queue]
            )
        # Mean inspection queue length
        data['Cumulative Stats']['Area Under Queue Length Curve']['Inspection'] += \
            (clock - data['Last Time Queue Length Changed']['Inspection']) * state['Queue Length']['Inspection']
        data['Last Time Queue Length Changed']['Inspection'] = clock
        # Remove from inspection queue
        data['Queue Customers']['Inspection'].pop(first_customer_in_inspection_queue)
        state['Queue Length']['Inspection'] -= 1
        # Schedule end of inspection for first customer in inspection queue
        fel_maker(future_event_list, 'End of Inspection', clock, first_customer_in_inspection_queue)
        data['Cumulative Stats']['Service Starters']['Inspection'] += 1


def end_of_complaint(future_event_list, state, clock, data, customer):
    # Forward look to inspection
    if state['Server Status']['Inspection'] < inputs['Number of Servers']['Inspection']:
        state['Server Status']['Inspection'] += 1
        # Schedule end of inspection
        fel_maker(future_event_list, 'End of Inspection', clock, customer)
        # Mean waiting time in inspection queue
        data['Cumulative Stats']['Service Starters']['Inspection'] += 1

    elif state['Server Status']['Inspection'] == inputs['Number of Servers']['Inspection']:
        # Mean inspection queue length
        data['Cumulative Stats']['Area Under Queue Length Curve']['Inspection'] += \
            (clock - data['Last Time Queue Length Changed']['Inspection']) * state['Queue Length']['Inspection']
        data['Last Time Queue Length Changed']['Inspection'] = clock
        # Maximum inspection queue length
        data['Cumulative Stats']['Maximum Queue Length']['Inspection'] = \
            max(
                data['Cumulative Stats']['Maximum Queue Length']['Inspection'],
                state['Queue Length']['Inspection']
            )
        # Put customer in inspection queue length
        data['Queue Customers']['Inspection'][customer] = clock
        state['Queue Length']['Inspection'] += 1

    # Backward look from complaint
    if state['Queue Length']['Complaint'] == 0:
        state['Server Status']['Complaint'] -= 1

    elif state['Queue Length']['Complaint'] > 0:
        # Find first customer in queue
        # Raises error if
        # complaint queue length is not compatible with the length of data['Queue Customers']['Complaint']
        first_customer_in_complaint_queue = min(data['Queue Customers']['Complaint'],
                                                key=data['Queue Customers']['Complaint'].get)
        # Mean waiting time in complaint queue
        data['Cumulative Stats']['Queue Waiting Time']['Complaint'] += \
            clock - data['Queue Customers']['Complaint'][first_customer_in_complaint_queue]
        # Maximum waiting time in Complaint queue
        data['Cumulative Stats']['Maximum Queue Time']['Complaint'] = \
            max(
                data['Cumulative Stats']['Maximum Queue Time']['Complaint'],
                clock - data['Queue Customers']['Complaint'][first_customer_in_complaint_queue]
            )
        # Mean complaint queue length
        data['Cumulative Stats']['Area Under Queue Length Curve']['Complaint'] += \
            (clock - data['Last Time Queue Length Changed']['Complaint']) * state['Queue Length']['Complaint']
        data['Last Time Queue Length Changed']['Complaint'] = clock
        # Remove from complaint queue
        data['Queue Customers']['Complaint'].pop(first_customer_in_complaint_queue)
        state['Queue Length']['Complaint'] -= 1
        # Schedule end of complaint for first customer in complaint queue
        fel_maker(future_event_list, 'End of Complaint', clock, first_customer_in_complaint_queue)
        data['Cumulative Stats']['Service Starters']['Complaint'] += 1


def create_row(step, current_event, state, data, future_event_list):
    # This function will create a list, which will eventually become a row of the output Excel file

    sorted_fel = sorted(future_event_list, key=lambda x: x['Event Time'])

    # What should this row contain?
    # 1. Step, Clock, Event Type, Event Customer and Event Customer Type
    row = [
        step,
        current_event['Event Time'],
        current_event['Event Type'],
        current_event['Customer'],
        current_event['Customer Type'],
        state['Parking Status']
    ]
    # 2. All state variables
    # states == 'Server Status' & 'Queue Length'
    for states in ['Server Status', 'Queue Length']:
        row.extend(list(state[states].values()))
    # 3. All Cumulative Stats
    for stats in list(data['Cumulative Stats'].keys()):
        row.extend(list(data['Cumulative Stats'][stats].values()))
    row.append('Total Time Spent in System')
    row.append('Total Paired Customers Serviced')
    # 4. All events in fel ('Event Time', 'Event Type', 'Event Customer' & 'Event Customer Type' for each event)
    for event in sorted_fel:
        row.append(event['Event Time'])
        row.append(event['Event Type'])
        row.append(event['Customer'])
        row.append((event['Customer Type']))
    return row


def justify(table):
    # This function adds blanks to short rows in order to match their lengths to the maximum row length

    # Find maximum row length in the table
    row_max_len = 0
    for row in table:
        if len(row) > row_max_len:
            row_max_len = len(row)

    # For each row, add enough blanks
    for row in table:
        row.extend([""] * (row_max_len - len(row)))

def create_main_header(state, data):
    # This function creates the main part of header (returns a list)
    # A part of header which is used for future events will be created in create_excel()

    # Header consists of ...
    # 1. Step, Clock, Event Type and Event Customer
    header = ['Step', 'Clock', 'Event Type', 'Event Customer', 'Event Customer Type', 'Parking Status']
    # 2. Names of the state variables
    for unit in list(state['Server Status'].keys()):
        header.append('Server Status ' + str(unit))
    for queue in list(state['Queue Length'].keys()):
        header.append('Queue Length ' + str(queue))
    # 3. Names of the cumulative stats
    for stat in list(data['Cumulative Stats'].keys()):
        for unit in list(data['Cumulative Stats'][stat].keys()):
            header.append(str(stat) + ' ' + str(unit))
    header.append('Total Time Spent in System')
    header.append('Total Paired Customers Serviced')
    return header


def create_excel(table, header, name_of_sheet, name_of_workbook):
    # This function creates and fine-tunes the Excel output file

    # Find length of each row in the table
    row_len = len(table[0])

    # Find length of header (header does not include cells for fel at this moment)
    header_len = len(header)

    # row_len exceeds header_len by (max_fel_length * 4);
    # i.e., Event Type, Event Time, Customer & Customer type for each event in FEL
    # Extend the header with 'Future Event Time', 'Future Event Type',
    # 'Future Event Customer', 'Future Event Customer Type'
    # for each event in the fel with maximum size
    i = 1
    for col in range((row_len - header_len) // 4):
        header.append('Future Event Time ' + str(i))
        header.append('Future Event Type ' + str(i))
        header.append('Future Event Customer ' + str(i))
        header.append('Future Event Customer Type ' + str(i))
        i += 1

    # Dealing with the output
    # First create a pandas DataFrame
    df = pd.DataFrame(table, columns=header, index=None)

    # Create a handle to work on the Excel file
    writer = pd.ExcelWriter(str(name_of_workbook) + '.xlsx', engine='xlsxwriter')

    # Write out the Excel file to the hard drive
    df.to_excel(writer, sheet_name=name_of_sheet, header=False, startrow=1, index=False)

    # Use the handle to get the workbook (just library syntax, can be found with a simple search)
    workbook = writer.book

    # Get the sheet you want to work on
    worksheet = writer.sheets[name_of_sheet]

    # Create a cell-formatter object (this will be used for the cells in the header, hence: header_formatter!)
    header_formatter = workbook.add_format()

    # Define whatever format you want
    header_formatter.set_align('center')
    header_formatter.set_align('vcenter')
    header_formatter.set_font('Times New Roman')
    header_formatter.set_bold('True')

    # Write out the column names and apply the format to the cells in the header row
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_formatter)

    # Auto-fit columns
    # Copied from https://stackoverflow.com/questions/29463274/simulate-autofit-column-in-xslxwriter
    for i, width in enumerate(get_col_widths(df)):
        worksheet.set_column(i - 1, i - 1, width)

    # Create a cell-formatter object for the body of Excel file
    main_formatter = workbook.add_format()
    main_formatter.set_align('center')
    main_formatter.set_align('vcenter')
    main_formatter.set_font('Times New Roman')

    # Apply the format to the body cells
    for row in range(1, len(df) + 1):
        worksheet.set_row(row, None, main_formatter)

    # Save your edits
    writer.save()


def get_col_widths(dataframe):
    # Copied from https://stackoverflow.com/questions/29463274/simulate-autofit-column-in-xslxwriter
    # First we find the maximum length of the index column
    idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
    # Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
    return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) for col in dataframe.columns]


def print_header():
    print(
        'Event Type'.ljust(
            30) + '\t' + 'Time'.ljust(
            30) + '\t' + 'Customer'.ljust(
            30) + '\t' + 'Customer type'.ljust(
            30) + '\t' + 'Outside Queue Length'.ljust(
            30) + '\t' + 'Photography Queue Length'.ljust(30) + '\t' + 'Photography Server Status'.ljust(
            30) + '\t' + 'Documentation Queue Length'.ljust(30) + '\t' + 'Departure Queue Length'.ljust(
            30) + '\t' + 'Documentation Server Status'.ljust(30) + '\t' + 'Inspection Queue Length'.ljust(
            30) + '\t' + 'Inspection Server Status'.ljust(30) + '\t' + 'Complaint Queue Length'.ljust(
            30) + '\t' + 'Complaint Server Status'.ljust(30) + '\t')

    print('-------------------------------------------------------------------------------------------------')


def nice_print(current_state, current_event):
    print(
        str(current_event['Event Type']).ljust(
            30) + '\t' + str(round(current_event['Event Time'], 3)).ljust(
            30) + '\t' + str(current_event['Customer']).ljust(
            30) + '\t' + str(current_event['Customer Type']).ljust(
            30) + '\t' + str(current_state['Queue Length']['Outside']).ljust(
            30) + '\t' + str(current_state['Queue Length']['Photography']).ljust(
            30) + '\t' + str(current_state['Server Status']['Photography']).ljust(
            30) + '\t' + str(current_state['Queue Length']['Documentation']).ljust(
            30) + '\t' + str(current_state['Queue Length']['Departure']).ljust(
            30) + '\t' + str(current_state['Server Status']['Documentation']).ljust(
            30) + '\t' + str(current_state['Queue Length']['Inspection']).ljust(
            30) + '\t' + str(current_state['Server Status']['Inspection']).ljust(
            30) + '\t' + str(current_state['Queue Length']['Complaint']).ljust(
            30) + '\t' + str(current_state['Server Status']['Complaint']).ljust(
            30)
    )


def simulation(end_clock, cold_end_clock=0, print_results=False, print_performance_measures=False):
    # Sanity check
    assert cold_end_clock < end_clock, \
        'Not enough time to reach warm state!'
    if print_results:
        # Print results in Python Console
        print_header()
    # A dictionary to store performance measures of interest
    performance_measures = dict()
    # Initialization
    state, future_event_list, data = starting_state()

    # Cold state queue length analysis initialization
    for queue in list(data['Cold Queue length Analysis'].keys()):
        data['Cold Queue length Analysis'][queue][0.0] = 0

    # Reset clock
    clock = 0

    while clock < end_clock:
        # Sort fel based on event times
        sorted_fel = sorted(future_event_list, key=lambda x: x['Event Time'])

        # Find imminent event
        current_event = sorted_fel[0]

        # Restore additional info about current event
        clock = current_event['Event Time']
        customer = current_event['Customer']
        customer_type = current_event['Customer Type']

        # Only data gathered after cold_end_clock is valid
        if clock > cold_end_clock:
            # Mean server utilization for photography unit;
            # Compute and accumulate server spare time for photography unit from previous clock till now
            data['Cumulative Stats']['Server Spare Time']['Photography'] += \
                (inputs['Number of Servers']['Photography'] - state['Server Status']['Photography']) * \
                (clock - data['Previous Clock'])

        # Execute events
        if current_event['Event Type'] == 'Arrival':
            arrival(future_event_list, state, clock, data, customer, customer_type)
        elif current_event['Event Type'] == 'End of Photography':
            end_of_photography(future_event_list, state, clock, data, customer)
        elif current_event['Event Type'] == 'End of Documentation':
            end_of_documentation(future_event_list, state, clock, data, customer)
        elif current_event['Event Type'] == 'End of Inspection':
            end_of_inspection(future_event_list, state, clock, data, customer)
        elif current_event['Event Type'] == 'End of Complaint':
            end_of_complaint(future_event_list, state, clock, data, customer)
        elif current_event['Event Type'] == 'Departure':
            departure(future_event_list, state, clock, data, customer)

        # Remove current event from fel
        future_event_list.remove(current_event)

        # Check violations for bounded values (i.e., # servers & queue lengths)
        # number of servers
        for server in list(state['Server Status'].keys()):
            assert state['Server Status'][server] >= 0, \
                'Negative value for number of idle ' + str(server) + ' servers detected.'
            assert state['Server Status'][server] <= inputs['Number of Servers'][server], \
                'Over-allocated servers in ' + str(server) + ' unit.'
        # Queue length
        for queue in list(state['Queue Length'].keys()):
            assert state['Queue Length'][queue] >= 0, \
                'Over-emptied queue in ' + str(queue) + ' queue.'
        # Photography queue capacity
        assert state['Queue Length']['Photography'] <= inputs['Photography Queue Capacity'], \
            'Over-crowded photography queue'
        # Parking
        assert state['Parking Status'] >= 0, \
            'Over-emptied parking'

        # Check Complaint Unit to always be empty
        assert state['Server Status']['Complaint'] == 0, \
            'Busy Complaint Unit!'

        # Update previous clock
        data['Previous Clock'] = clock

        # Cold state queue length analysis
        for queue in list(data['Cold Queue length Analysis'].keys()):
            data['Cold Queue length Analysis'][queue][clock] = state['Queue Length'][queue]

        # Only data gathered after cold_end_clock is valid
        if clock < cold_end_clock:
            # Mean total time spent in system
            data['Total Time Spent in System'] = 0.
            data['Total Paired Customers Serviced'] = 0
            # Outside maximum queue length
            data['Cumulative Stats']['Maximum Queue Length']['Outside'] = 0
            # Complaint maximum queue length
            data['Cumulative Stats']['Maximum Queue Length']['Complaint'] = 0
            # Mean documentation queue waiting time
            data['Cumulative Stats']['Queue Waiting Time']['Documentation'] = 0
            data['Cumulative Stats']['Service Starters']['Documentation'] = 0
            # Mean departure queue waiting time
            data['Cumulative Stats']['Queue Waiting Time']['Departure'] = 0
            data['Cumulative Stats']['Service Starters']['Departure'] = 0

        if print_results:
            # Print results in Python Console
            nice_print(state, current_event)

    # Compute performance measures of interest
    # Mean photography server utilization
    performance_measures['Mean Photography Server Utilization'] = \
        1 - (data['Cumulative Stats']['Server Spare Time']['Photography'] /
             (inputs['Number of Servers']['Photography'] * (end_clock - cold_end_clock)))
    # Mean total time spent in system
    performance_measures['Mean Total Time Spent in System'] = \
        data['Total Time Spent in System'] / (data['Total Paired Customers Serviced'] * 2)
    # Outside maximum queue length
    performance_measures['Outside Maximum Queue Length'] = \
        data['Cumulative Stats']['Maximum Queue Length']['Outside']
    # Complaint maximum queue length
    performance_measures['Complaint Maximum Queue Length'] = \
        data['Cumulative Stats']['Maximum Queue Length']['Complaint']
    # Mean documentation queue waiting time
    performance_measures['Mean Documentation Queue Waiting Time'] = \
        data['Cumulative Stats']['Queue Waiting Time']['Documentation'] / \
        data['Cumulative Stats']['Service Starters']['Documentation']
    # Mean departure queue waiting time
    performance_measures['Mean Departure Queue Waiting Time'] = \
        data['Cumulative Stats']['Queue Waiting Time']['Departure'] / \
        data['Cumulative Stats']['Service Starters']['Departure']

    if print_performance_measures:
        # System 2 performance measures
        print('\n')
        print('+++++++++++++++++++++++++++++++++++++++++')
        print('System 2 performance measures')
        print('+++++++++++++++++++++++++++++++++++++++++')
        for measure in list(performance_measures.keys()):
            print('\x1B[3m\x1B[1m' + str(measure) + '\x1B[0m: ')
            print('>> ' + str(round(performance_measures[measure], 3)))
            print('-----------------------------------------')

    return data, performance_measures


