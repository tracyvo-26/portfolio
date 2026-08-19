def bubbleSort(A):
    if isinstance(A, list):
        n = len(A)
        for x in range(0,n-1):
            for i in range(0,n-1-x):
                if A[i] > A[i+1]:
                    A[i], A[i+1] = A[i+1], A[i]
        return
    try:
        if A.isEmpty():
            return
    except AttributeError:
        raise TypeError("Unsupported type passed to bubbleSort")
    end = None
    while end != A.head:
        cur = A.head
        while cur.getNext() != end:
            nxt = cur.getNext()
            if cur.getValue() > nxt.getValue():
                # swap node values
                cur_val = cur.getValue()
                cur.setValue(nxt.getValue())
                nxt.setValue(cur_val)
            cur = nxt
        end = cur
import numpy as np
