# Simulation of an insurance claim center
## Abstract
This project has performed an insurance claim center simulation for one month. In this insurance center, the complainant and the guilty party pass through photography units, file opening, claim investigation, registering complaints if needed, and finally completing their file.

In the first phase, static and dynamic descriptions are presented after modeling the problem using simulation methods. Performance evaluation criteria have also been proposed for the insurance claim center.

In the second phase, the insurance center was simulated using Python, and its performance was measured using cumulative statistics. Sensitivity analysis was also performed by changing some system parameters.

In the third phase, two alternative systems are modeled and evaluated at a stable state by eliminating the transient period. The Independent sampling method was used to determine the better proposal.

Finally, three other solutions are proposed using sensitivity analysis and step-by-step improvement to reduce service and the real closure time as the critical performance measures of the system.
## Problem description
The project involves modeling an auto insurance claim center that accepts customers daily from 8 a.m. to 6 p.m. However, the center will continue operating until all customers have been served. The complainant and defendant must be together for the entire process, yet some customers may arrive separately. Upon reaching the center, these single customers must wait in the parking until the other party arrives. All customers go through photography, documentation, investigation, and complaint filing if needed, before finalizing their claim file.
Key results of the simulation.

There is a 9-hour difference between the actual closing time (average 2:58 AM) and the official 6 PM closing time, which means employees work approximately nine extra hours beyond their scheduled hours. Each customer spends an average of 355 minutes (over 5 hours) in the system. These results are highly problematic for the center and unsatisfactory for customers. 

The investigation unit has the highest employee utilization at 95%, much higher than other units and very close to 100% utilized. Customers wait almost 2 hours on average in the investigation queue, more than double the wait times in other queues. This queue’s length averages 55 customers, far exceeding other units. These results indicate that the investigation unit is a significant bottleneck. Increasing investigation staffing or reducing load could significantly improve system performance and customer satisfaction.

Sensitivity analysis is next used to quantify how changes like altering staffing impact system performance to aid data-driven management decision-making.
## Results of sensitivity analysis
1) Investigation Staffing Increase: Increasing investigation staff beyond three people does not improve overall system time or investigation wait times since it creates bottlenecks at other units without added benefit. The system closing time fluctuates around a constant value after three staff.
2) Photography Duration Increase: Increasing photography duration reduces system time and investigation waits, supporting the hypothesis of reducing investigation load. An increase to 8 minutes provides significant reductions, beyond which metrics remain relatively constant. This change has a much more significant positive impact than investigation staffing.
3) Investigation Duration Decrease: Decreasing the investigation service time by 1-2 minutes substantially reduces investigation wait time. However, it only significantly improves the overall system closing time.
4) Complaint Probability Increase: Higher complaint probability considerably increases system time and investigation waits. Thus, if the complaint rate rises, interventions are needed to prevent growing delays.

The sensitivity analysis provides quantifiable insights into the system's reactions to parameter changes. Increasing photography duration emerges as the most effective improvement lever without requiring costly added staffing.

## Alternative systems proposed and the results of their comparison
The two proposed alternative systems modify arrival patterns, staffing levels, service times, and complaint handling. Key performance measures are calculated in a steady state after determining and eliminating warm-up periods. Finally, these metrics are used to compare the alternative systems.
### Alternative System 1:
* Eliminates all individual customer arrivals, only allowing paired arrivals following an exponential distribution with a mean of five minutes.
* Removes the 6 PM closure event since the system runs 24/7.
* The warm-up period is analyzed by plotting queue lengths over time. The system reaches a steady state after around 55 days.
### Alternative System 2:
* The arrival distribution mean is reduced to 3.2 minutes.
* Documentation staff and servers are increased as per project specifications.
* Investigation duration is decreased to 8 minutes on average.
* The complaint probability is set to zero since complaints are handled externally.
* The warm-up period takes around 67 days.
## Proposed improvement policies
Sensitivity analysis provides a suitable approach for suggesting improvement policies. In the second phase, sensitivity analysis is applied, focusing on scattered improvement suggestions, and a more organized reference to its outcomes is provided.
The initial system bottleneck was the inspection unit. Three solutions are feasible for addressing this:
1) Increasing staff in the photography unit to resolve the bottleneck.
2) Enhancing pre-inspection unit service time to ease the bottleneck caused by workload.
3) Improving the service rate of the bottlenecked unit through training or facility enhancement.

Sensitivity analysis examines the efficacy of these three solutions. Given the simulations' low time and financial costs, a general algorithm is proposed for improving the initial system, which involves sensitivity analysis for problematic parameters at each step, prioritizing the most impactful change until the system achieves the desired performance.
Performance metrics include time within the system and actual center operation time. Initial metrics are 347.316 and 1138.148 minutes, respectively.

In the first step, the average service time of the imaging unit was gradually increased up to 11 increments. As a result, the average time spent within the system decreased to 287.771, and the actual center operation time reduced to 787.649, signifying a significant improvement from the initial state. However, in this scenario, waiting time in the external queue and the photoshoot process remained notably high. Further staffing in the photography unit would create a bottleneck behind the assessment unit, suggesting an initial increase in inspection staff. Consequently, the average waiting time was reduced to 280.39, and the actual center operation time decreased to 765.181, slightly enhancing the previous state.

The second step gradually reduced the photography queue’s limit inside the center. Removing the limit had a considerable impact, reducing the average time spent within the system to 40.586 and the actual center operation time to 682.342. With these changes, customers form a queue outside the photo shoot area, and paired vehicles enter the first position in the photography queue directly from the parking.

Considering the decrease in service efficiency across all units in the previous step, it appeared that one of the main reasons for the long waiting time in the external queue was the time interval between the complainant and the defendant's entry in the single-entry scenario. Moreover, since service providers have a service capacity, quicker arrival of the second vehicle could improve system performance. This case was tested by reducing the successive average time interval between the entry of two test vehicles, and ultimately, completely removing single entries reduced the studied metrics to 38.326 and 654.435 minutes.

As a final solution, parameters related to service time for completing the documentation and case assessment were altered to assess its impact on the system. Reducing these parameters resulted in an average time spent within the system of 37.438 and an actual center closing time of 642.23 minutes which is an exceptional improvement in the performance of the insurance claim center.
