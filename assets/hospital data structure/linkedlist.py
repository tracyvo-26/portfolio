class DSALinkedList:
    class DSAListNode:
        def __init__(self,value):
            self.value = value
            self.next = None
            self.prev = None
        def getValue(self):
            return self.value
        def setValue(self,inValue):
            self.value = inValue
        def getNext(self):
            return self.next
        def setNext(self,newNext):
            self.next = newNext
        def getPrev(self):
            return self.prev
        def setPrev(self,newPrev):
            self.prev = newPrev
    def __init__(self):
        self.head = None
        self.tail = None

    def insertFirst(self,newValue):
        newNd = self.DSAListNode(newValue)
        if self.isEmpty():
            self.head = newNd
            self.tail = newNd
        else:
            newNd.setNext(self.head)
            self.head.setPrev(newNd)
            self.head = newNd

    def insertLast(self,newValue):
        newNd = self.DSAListNode(newValue)
        if self.isEmpty():
            self.head = newNd
            self.tail = newNd
        else:
            self.tail.setNext(newNd)
            newNd.setPrev(self.tail)
            self.tail = newNd
        
    def isEmpty(self):
        return self.head is None
    
    def peekFirst(self):
        if self.isEmpty():
            raise IndexError("List is empty")
        else:
            return self.head.getValue()
    def peekLast(self):
        if self.isEmpty():
            raise IndexError("List is empty")
        else:
            return self.tail.getValue()
        
    def removeFirst(self):
        if self.isEmpty():
            raise IndexError("List is empty")
        
        value = self.head.getValue()
        if self.head == self.tail: # Only one node
            self.head = None
            self.tail = None
        else:
            self.head = self.head.getNext()
            self.head.setPrev(None) # Ensure the new head's prev is None
        return value
        
    def removeNode(self, value):
        if self.isEmpty():
            raise ValueError("List is empty")

        current = self.head

        while current:
            if current.getValue() == value:
                # Case 1: only one node
                if self.head == self.tail:
                    self.head = None
                    self.tail = None
                # Case 2: removing head
                elif current == self.head:
                    self.head = self.head.getNext()
                    self.head.setPrev(None)
                # Case 3: removing tail
                elif current == self.tail:
                    self.tail = self.tail.getPrev()
                    self.tail.setNext(None)
                # Case 4: middle node
                else:
                    prev_node = current.getPrev()
                    next_node = current.getNext()
                    prev_node.setNext(next_node)
                    next_node.setPrev(prev_node)

                return  # node removed, exit function

            current = current.getNext()

        raise ValueError("Value not found in list")
    
    def removeLast(self):
        if self.isEmpty():
            raise IndexError("List is empty")
    
        value = self.tail.getValue()
        if self.head == self.tail: # Only one node
            self.head = None
            self.tail = None
        else:
            self.tail = self.tail.getPrev()
            self.tail.setNext(None) # Ensure the new tail's next is None
        return value

    
    def display(self):
        current = self.head
        if self.isEmpty():
            print("The list is empty.")
            return

        print("List (head to tail):", end=" ")
        while current:
            print(current.getValue(), end=" <-> ")
            current = current.getNext()
        print("None")

    def to_string(self):
        current = self.head # Assuming 'head' is the first node
        result_parts = []
        while current is not None:
            # Assuming your nodes store their data in a 'value' attribute
            result_parts.append(str(current.value)) 
            current = current.next # Assuming 'next' points to the next node
        return "[" + ", ".join(result_parts) + "]" # Formats as [item1, item2, ...]

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()
    
    def getCount(self):
        count = 0
        current = self.head
        while current:
            count += 1
            current = current.next
        return count