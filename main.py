import random
import math
from enum import Enum


class States(Enum):
    IDLE = 1
    BUSY = 2
    CONTENTION = 3  # when it starts to count down back-off


class Event:
    def __init__(self, next=None, prev=None, time=None, type=None, src=None, dest=None):
        self.next = next  # reference to next event in DLL
        self.prev = prev  # reference to previous event in DLL
        self.time = time
        self.type = type  # 1: arrival 2: departure 3: sense
        self.src = src
        self.dest = dest


class DLL:
    def __init__(self):
        self.head = None

    def remove_first(self):
        if self.head is not None:
            self.head = self.head.next
            if self.head is not None:
                self.head.prev = None

    def insert(self, new_time, new_type, new_src, new_dest):
        new_event = Event(time=new_time, type=new_type, src=new_src, dest=new_dest)

        # empty linked list
        if self.head is None:
            new_event.prev = None
            new_event.next = None
            self.head = new_event
        # not empty linked list
        else:
            if self.head.time > new_time:
                new_event.prev = None
                new_event.next = self.head
                self.head.prev = new_event
                self.head = new_event
                return
            temp: Event = self.head
            while temp.next is not None:
                if temp.time <= new_time < temp.next.time:
                    new_event.prev = temp
                    new_event.next = temp.next
                    temp.next.prev = new_event
                    temp.next = new_event
                    return
                temp = temp.next
            temp.next = new_event
            new_event.prev = temp
            new_event.next = None

    def print_list(self):
        if self.head is None:
            print("Empty!")
            return

        print("-----start-----")
        temp = self.head
        while temp is not None and temp.next is not None:
            print("Time:" + str(temp.time) + " Type:" + str(temp.type) + " Source:" + str(temp.src) + " Destination:" + str(temp.dest))
            temp = temp.next

        print("Time:" + str(temp.time) + " Type:" + str(temp.type) + " Source:" + str(temp.src) + " Destination:" + str(temp.dest))
        # while temp is not None:
        #     print("Time:" + str(temp.time) + " Type:" + str(temp.type))
        #     temp = temp.prev

        print("-----end-----")


class Packet:
    def __init__(self, frame_size, src, dest):
        self.frame_size = frame_size
        self.src = src
        self.dest = dest


class Buffer:
    def __init__(self):
        self.queue = []

    def insert(self, packet):
        self.queue.append(packet)

    def remove(self):
        if len(self.queue) is 0:
            print("Nothing to remove in this buffer!")
        else:
            self.queue.pop(0)


class Host:
    def __init__(self, host_number, host_buffer, back_off):
        self.host_number = host_number
        self.host_buffer = host_buffer
        self.back_off = back_off
        self.delay_flag = 0
        self.fail_times = 0


def nedt(rate):  # negative exponentially distributed time
    u = random.uniform(0, 1)
    return (-1 / float(rate)) * math.log(1 - u)


def data_frame_length():
    return nedt(0.001) % 1544


def generate_dest(host_number, N):
    r = random.randint(0,N-2)
    if r >= host_number:
        r += 1
    return r


def back_off_value(fail_times, big_t):
    u = random.randint(0, big_t * fail_times)
    return u


# 1. Initialize
N = int(input("Please enter the number of wireless hosts : "))
arrival_rate = input("Please enter the arrival rate (lambda) : ")
T = int(input("Please enter the T : "))
sifs = 0.00005
difs = 0.0001
sense_interval = 0.00001
GEL = DLL()
host_list = []
time = 0
state = States.IDLE
transmission_rate = 10 * 1024 * 1024
transmitting_host = -1  # no transmitting host
num_of_bytes = 0
total_delay = 0

contention_collision = 0

for i in range(N):
    my_buffer = Buffer()
    my_host = Host(i, my_buffer, -1)  # no random back-off now
    host_list.append(my_host)
    GEL.insert(time + nedt(arrival_rate), 1, i, generate_dest(i,N))

GEL.insert(0, 3, -1, -1)

GEL.print_list()

# 2. Loop
for i in range(1000000):
    this_event = Event(time=GEL.head.time, type=GEL.head.type, src=GEL.head.src, dest=GEL.head.dest)
    GEL.remove_first()

    if this_event.type == 1:  # put this arrival in queue and generate new arrival
        time = this_event.time
        GEL.insert(time + nedt(arrival_rate), 1, this_event.src, generate_dest(this_event.src, N))
        new_packet = Packet(data_frame_length(), this_event.src, this_event.dest)
        host_list[this_event.src].host_buffer.insert(new_packet)
        host_list[this_event.src].delay_flag = time

    if this_event.type == 2:
        time = this_event.time
        state = States.IDLE
        num_of_bytes += host_list[this_event.src].host_buffer.queue[0].frame_size
        host_list[this_event.src].host_buffer.remove()
        total_delay += (time - host_list[this_event.src].delay_flag)
        transmitting_host = -1
        host_list[this_event.src].fail_times = 0

    if this_event.type == 3:  # sense event, generate next sense
        time = this_event.time
        GEL.insert(sense_interval + time, 3, -1, -1)
        if state == States.IDLE:
            all_no_value = True
            non_empty_buffer = []
            for j in range(N):
                if host_list[j].back_off >= 0:
                    all_no_value = False
                if len(host_list[j].host_buffer.queue) > 0:
                    non_empty_buffer.append(j)
            if all_no_value:
                if len(non_empty_buffer) > 0:
                    index = non_empty_buffer[0]
                    data_time = (host_list[index].host_buffer.queue[0].frame_size * 8) / transmission_rate
                    ack_time = (64 * 8) / transmission_rate
                    transmit_src = host_list[index].host_buffer.queue[0].src
                    transmit_dest = host_list[index].host_buffer.queue[0].dest
                    GEL.insert(time + difs + data_time + sifs + ack_time, 2, transmit_src, transmit_dest)
                    state = States.BUSY
                    transmitting_host = index
            else:
                GEL.insert(time + difs, 5, -1, -1)
                state = States.BUSY
        elif state == States.BUSY:
            for j in range(N):
                if j == transmitting_host:  # no modification to the transmitting host
                    continue
                if len(host_list[j].host_buffer.queue) > 0:  # have a frame to transmit
                    if host_list[j].back_off < 0:  # no back-off value
                        host_list[j].back_off = back_off_value(host_list[j].fail_times + 1, T)
        else:
            zero_count_host = []
            have_count_host = []
            maxsize = 0
            for j in range(N):
                if len(host_list[j].host_buffer.queue) > 0:
                    if host_list[j].back_off >= 0:
                        have_count_host.append(j)
                        host_list[j].back_off = max(0, host_list[j].back_off - 1)
                    if host_list[j].back_off == 0:
                        zero_count_host.append(j)
                        maxsize = max(maxsize,host_list[j].host_buffer.queue[0].frame_size)
            if len(zero_count_host) == 1:
                index = zero_count_host[0]
                data_time = (host_list[index].host_buffer.queue[0].frame_size * 8) / transmission_rate
                ack_time = (64 * 8) / transmission_rate
                transmit_src = host_list[index].host_buffer.queue[0].src
                transmit_dest = host_list[index].host_buffer.queue[0].dest
                GEL.insert(time + data_time + sifs + ack_time, 2, transmit_src, transmit_dest)
                transmitting_host = index
                state = States.BUSY
                host_list[index].back_off = -1
            if len(zero_count_host) > 1:
                contention_collision += 1
                if len(have_count_host) == len(zero_count_host):
                    state = States.IDLE
                # GEL.insert(time + maxsize / transmission_rate, 6, -1, -1)
                for k in zero_count_host:
                    host_list[k].fail_times += 1
                    host_list[k].back_off = back_off_value(host_list[k].fail_times + 1, T)

    if this_event.type == 5:
        state = States.CONTENTION
    if this_event.type == 6:
        state = States.IDLE

GEL.print_list()
print("Throughput : "+str(num_of_bytes / time))
print("Average network delay : "+str(total_delay/(num_of_bytes/time)))
print(contention_collision)



















