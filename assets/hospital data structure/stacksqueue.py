import numpy as np

class DSAStack:
    DEFAULT_CAPACITY = 100

    def __init__(self, maxCapacity=None):
        if maxCapacity is None:
            self.stack = np.zeros(self.DEFAULT_CAPACITY, dtype=object)
            self.capacity = self.DEFAULT_CAPACITY
        else:
            self.stack = np.zeros(self.DEFAULT_CAPACITY, dtype=object)
            self.capacity = self.DEFAULT_CAPACITY
        self.count = 0

    def getCount(self):
        return self.count

    def isEmpty(self):
        return self.count == 0

    def isFull(self):
        return self.count == len(self.stack)

    def push(self, value):
        if self.isFull():
            raise Exception("Stack is full")
        else:
            self.stack[self.count] = value
            self.count += 1

    def pop(self):
        if self.isEmpty():
            raise Exception("Stack is empty")
        else:
            top_val = self.stack[self.count - 1]
            self.count -= 1
            return top_val

    def top(self):
        if self.isEmpty():
            raise Exception("Stack is empty")
        else:
            return self.stack[self.count - 1]

# Parent class for queues
class DSAQueue:
    DEFAULT_CAPACITY = 100

    def __init__(self, maxCapacity=None):
        if maxCapacity is None:
            self.queue = np.zeros(self.DEFAULT_CAPACITY, dtype=object)
            self.capacity = self.DEFAULT_CAPACITY
        else:
            self.queue = np.zeros(maxCapacity, dtype=object)
            self.capacity = maxCapacity
        self.count = 0

    def getCount(self):
        return self.count

    def isEmpty(self):
        return self.count == 0

    def isFull(self):
        return self.count == len(self.queue)

    def enqueue(self, value):
        if self.isFull():
            raise Exception("Queue is full")
        else:
            self.queue[self.count] = value
            self.count += 1

    def dequeue(self):
        if self.isEmpty():
            raise Exception("Queue is empty")
        else:
            front_val = self.queue[0]
            for i in range(self.count - 1):
                self.queue[i] = self.queue[i + 1]
            self.count -= 1
            return front_val

    def peek(self):
        if self.isEmpty():
            raise Exception("Queue is empty")
        else:
            return self.queue[0]