import random
import math
import sys


class Event:
    def __init__(self, next=None, prev=None, time=None, type=None, src=None, dest=None):
        self.next = next  # reference to next event in DLL
        self.prev = prev  # reference to previous event in DLL
        self.time = time
        self.type = type  # 1: arrival 2: departure
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
    def __init__(self, service_time):
        self.service_time = service_time


class Buffer:
    def __init__(self, size):
        self.size = size
        self.queue = []

    def insert(self, packet):
        self.queue.append(packet)

    def remove(self):
        if len(self.queue) is 0:
            print("Nothing to remove in this buffer!")
        else:
            self.queue.pop(0)


class Host:
    def __init__(self, host_number, host_buffer):
        self.host_number = host_number
        self.host_buffer = host_buffer


def nedt(rate):  # negative exponentially distributed time
    u = random.uniform(0, 1)
    return (-1 / float(rate)) * math.log(1 - u)


def generate_dest(host_number, N):
    r = random.randint(0,N-2)
    if r >= host_number:
        r += 1
    return r


# 1. Initialize
N = int(input("Please enter the number of wireless hosts:"))
arrival_rate = input("Please enter the arrival rate (lambda) : ")
sifs = 0.00005
difs = 0.0001
sense_interval = 0.00001
GEL = DLL()
host_list = []
time = 0

for i in range(N):
    my_buffer = Buffer(int(sys.maxsize))
    my_host = Host(i, my_buffer)
    host_list.append(my_host)
    GEL.insert(time + nedt(arrival_rate), 1, i, generate_dest(i,N))

GEL.print_list()





