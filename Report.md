# Project 2 Report
**Team Members**: Lei Zou, Josue Aleman, Sattar Ehtesham

## **Introduction**

In this project we wanted to simulate the 802.11 based WLAN competing stations model. The measurements we wanted to analyze are the **throughput** and the **average network delay**. 

**Language used**: For this project we decided to use **Python** as our programming language as the global event list and it's features from *Project 1* were implemeneted in Python. 

### **Data Structures Implemented**:

We maintained the same data structures from *Project 1*  such as the `Event` class, the Doubly Linked List, the `Packet` class and the `Buffer` class. 
New structures are as follows:

1. `Host` class which contains and instance of the `Buffer` class, along with some identifying variables such as its `host_number`, the `back_off` quantity in case the host needs to wait to transmit data. 
2. `States` enum class, which allows us to determine in which state the global event list is in.

### **Variables used**:

As with the data structures, we also maintined all of the variables from *Project 1* along with some new ones:

1. `N`- User provided, determines the number of hosts to simulate
2. `T`- User provided, the  max value of the range for the first time a backoff value must be generated
3. `sifs`- per the document is set to 0.05*msec*
4. `difs`- per the document is set to 0.1*msec*
5. `sense_interval`- per the document is set to 0.01 *msec*
6. `host_list` - this is a list that maintains the hosts
7. `state`- an instance of the `States` class which will determine what state the events are in
8. `transmission_rate`- user defined
9. `transmission_host`- 
10. `num_of_bytes`- keeps the sum of packages that were transmitted successfully
11. `total_delay`- an accumulator that keeps a sum of the delay in the system
    
### **Functions used**:
1. Correct ones

## **Implementation**

We follow the logic that was provided in the document on page 2. 
talk about **event type** and **host state**
where 

event types are:
1. Arrival
2. Departure
3. Sensing
4. N/A
5. Entering contention
6. Collition
   
Host State:
1. IDLE
2. BUSY
3. CONTENTION

**Collecting Statistics**:




## **Conclusion**

Analyzing the results we are able to determine that as T increases, there is less collisions, but it comes at the cost of latency increase, creating a system that spends a lot of time in idle, rather than transmitting data. 

