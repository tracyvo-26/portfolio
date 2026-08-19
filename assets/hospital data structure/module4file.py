# -------------------------------------------------------------------------
# MODULE 4: Patient Data Generation and Sorting Benchmarking
# -------------------------------------------------------------------------
# Purpose:
# This module is responsible for generating simulated patient datasets and
# benchmarking the performance of different sorting algorithms (Merge Sort
# and Quick Sort with Median-of-Three pivot) on these datasets.
# It uses the hospital navigation graph (from Module 1) for pathfinding
# to determine expected patient treatment times, which are then used as
# the sorting key.
# -------------------------------------------------------------------------

import numpy as np
import time
import sys
from module2file import *
from module1file import *
from linkedlist import *


# ---------------------------------------------------------
# Helper: Build Hospital Graph
# ---------------------------------------------------------
def build_hospital_graph():
    hospital_graph = HospitalNavigationGraph()

    # Add departments (nodes)
    hospital_graph.add_department("Emergency")
    hospital_graph.add_department("Radiology")
    hospital_graph.add_department("ICU")
    hospital_graph.add_department("Wards")
    hospital_graph.add_department("Pharmacy")
    hospital_graph.add_department("Laboratories")
    hospital_graph.add_department("Operating Theatres")
    hospital_graph.add_department("Outpatient Units")

    # Add paths (edges) — define realistic travel times (minutes)
    hospital_graph.add_path("Emergency", "Radiology", 10)
    hospital_graph.add_path("Radiology", "ICU", 15)
    hospital_graph.add_path("ICU", "Wards", 5)
    hospital_graph.add_path("Radiology", "Pharmacy", 8)
    hospital_graph.add_path("Pharmacy", "Laboratories", 7)
    hospital_graph.add_path("Emergency", "Wards", 20)
    hospital_graph.add_path("ICU", "Operating Theatres", 6)
    hospital_graph.add_path("Wards", "Outpatient Units", 12)

    return hospital_graph


# ---------------------------------------------------------
# Generate Patient Dataset
# ---------------------------------------------------------
def generate_patient_dataset(num_patients: int, hospital_graph=None, seed=42):
    if hospital_graph is None:
        hospital_graph = build_hospital_graph()

    np.random.seed(seed)

    departments = np.array([
        "Emergency", "ICU", "Pharmacy", "Radiology",
        "Laboratories", "Operating Theatres", "Wards", "Outpatient Units"
    ])

    patients_array = np.empty(num_patients, dtype=object)

    for i in range(num_patients):
        patient_id = i
        name = f"Patient {patient_id}"
        age = np.random.randint(1, 90)
        department = np.random.choice(departments)
        destination_department = np.random.choice(departments)
        urgency_level = np.random.randint(1, 5)
        treatment_status = "Under Treatment"
        mock_procedure_time = round(np.random.uniform(5.0, 300.0), 2)

        # Pathfinding between departments
        try:
            result = hospital_graph.find_shortest_path_a_star(department, destination_department)
            if result is None or len(result) < 2:
                path_str = None
                travel_time_to_destination = 0
            else:
                path_str, travel_time_to_destination = result
        except ValueError:
            # If department missing or no path exists
            path_str = None
            travel_time_to_destination = 0

        expected_treatment_time = travel_time_to_destination + mock_procedure_time

        patient = PatientDetailsEntry(
            PatientID=patient_id,
            Name=name,
            Age=age,
            Department=department,
            UrgencyLevel=urgency_level,
            TreatmentStatus=treatment_status,
            DestinationDepartment=destination_department,
            MockProcedureTime=mock_procedure_time,
            ExpectedTreatmentTime=expected_treatment_time
        )

        patients_array[i] = patient

    return patients_array


# ---------------------------------------------------------
# Merge Sort Implementation
# ---------------------------------------------------------
def mergeSort(A):
    if not isinstance(A, np.ndarray): #checks if the input A is not already a NumPy 
        A = np.array(A) # converts A into a NumPy array
    mergeSortRec(A, 0, (len(A) - 1))

def mergeSortRec(A, leftIdx, rightIdx):
    if leftIdx < rightIdx:
        midIdx = (leftIdx + rightIdx)//2
        mergeSortRec(A, leftIdx, midIdx)
        mergeSortRec(A, midIdx+1, rightIdx)
        merge(A, leftIdx, midIdx, rightIdx)

def merge(A, leftIdx, midIdx, rightIdx):
    size = (rightIdx-leftIdx+1)
    tempArray = np.empty(size, dtype=object)
    ii = leftIdx
    jj = midIdx + 1
    kk = 0
    while ii <= midIdx and jj <= rightIdx:
        if A[ii].expected_treatment_time <= A[jj].expected_treatment_time:
            tempArray[kk] = A[ii]
            ii += 1
        else:
            tempArray[kk] = A[jj]
            jj += 1
        kk += 1
    for ii in range(ii, midIdx+1):
        tempArray[kk] = A[ii]
        kk += 1
    for jj in range(jj, rightIdx+1):
        tempArray[kk] = A[jj]
        kk += 1
    for kk in range(leftIdx, rightIdx+1):
        A[kk] = tempArray[kk - leftIdx]


# ---------------------------------------------------------
# Quick Sort Implementation (Median-of-Three)
# ---------------------------------------------------------
def quickSortMedian3(A):
    """ quickSortMedian3 - front-end for kick-starting the recursive algorithm with Median-of-Three pivot selection
    """
    if not isinstance(A, np.ndarray): #checks if the input A is not already a NumPy
        A = np.array(A) # converts A into a NumPy array
    quickSortRecurseMedian3(A, 0, (len(A) - 1))

def quickSortRecurseMedian3(A, leftIdx, rightIdx):
    if rightIdx > leftIdx:
        midIdx = (leftIdx + rightIdx) // 2
        if A[leftIdx].expected_treatment_time > A[midIdx].expected_treatment_time:
            A[leftIdx], A[midIdx] = A[midIdx], A[leftIdx]
        if A[leftIdx].expected_treatment_time > A[rightIdx].expected_treatment_time:
            A[leftIdx], A[rightIdx] = A[rightIdx], A[leftIdx]
        if A[midIdx].expected_treatment_time > A[rightIdx].expected_treatment_time:
            A[midIdx], A[rightIdx] = A[rightIdx], A[midIdx]
        
        pivotIdx = midIdx 

        newPivotIdx = doPartitioning(A,leftIdx,rightIdx,pivotIdx)
        quickSortRecurseMedian3(A, leftIdx, newPivotIdx - 1)
        quickSortRecurseMedian3(A, newPivotIdx + 1, rightIdx)

def doPartitioning(A, leftIdx, rightIdx, pivotIdx):
    pivotVal = A[pivotIdx]
    A[pivotIdx] = A[rightIdx]
    A[rightIdx] = pivotVal
    currIdx = leftIdx
    for i in range(leftIdx, rightIdx+1):
        if A[i].expected_treatment_time < pivotVal.expected_treatment_time:
            temp = A[i]
            A[i] = A[currIdx]
            A[currIdx] = temp
            currIdx += 1
    newPivIdx = currIdx
    A[rightIdx] = A[newPivIdx]
    A[newPivIdx] = pivotVal
    return newPivIdx

# ---------------------------------------------------------
# Benchmarking
# ---------------------------------------------------------
def benchmark_algorithms():
    hospital_graph = build_hospital_graph()
        # --- Small Validation Test for Correctness of Sorting Algorithms ---
    print("\n=== Module 4: Sorting Correctness Validation (Size 10, Random Data) ===")
    validation_size = 10
    validation_data_original = generate_patient_dataset(validation_size, hospital_graph, seed=100)
    validation_data_merge = np.copy(validation_data_original)
    validation_data_quick = np.copy(validation_data_original)

    print("\n--- Original Dataset (first 10 patient ExpectedTreatmentTime): ---")
    for i in range(len(validation_data_original)):
        patient = validation_data_original[i]
        print(f"ID {patient.patient_id}: {patient.expected_treatment_time:.2f} min")

    print("\n--- Merge Sort Result: ---")
    mergeSort(validation_data_merge)
    for i in range(len(validation_data_merge)):
        patient = validation_data_merge[i]
        print(f"ID {patient.patient_id}: {patient.expected_treatment_time:.2f} min")
    
    print("\n--- Quick Sort Result: ---")
    quickSortMedian3(validation_data_quick)
    for i in range(len(validation_data_quick)):
        patient = validation_data_quick[i]
        print(f"ID {patient.patient_id}: {patient.expected_treatment_time:.2f} min")

    # --- Using DSALinkedList for sizes and conditions ---
    sizes_ll = DSALinkedList()
    sizes_ll.insertLast(100)
    sizes_ll.insertLast(500)
    sizes_ll.insertLast(1000)

    conditions_ll = DSALinkedList()
    conditions_ll.insertLast("random")
    conditions_ll.insertLast("nearly_sorted")
    conditions_ll.insertLast("reversed")
    # --- End DSALinkedList usage ---
    print("\n=== Module 4: Sorting Benchmark Results ===")
    print(f"{'Condition':<20}{'Size':<10}{'MergeSort (s)':<20}{'QuickSort (s)':<20}")

    # Iterate through DSALinkedList for conditions
    current_cond_node = conditions_ll.head
    while current_cond_node:
        cond = current_cond_node.getValue()
        
        # Iterate through DSALinkedList for sizes
        current_size_node = sizes_ll.head
        while current_size_node:
            size = current_size_node.getValue()
            
            # Generate new datasets for each run to ensure fair comparison
            dataset_merge = generate_patient_dataset(size, hospital_graph)
            dataset_quick = np.copy(dataset_merge) # Use a copy for QuickSort

            # Pre-sort/reverse if condition requires
            if cond == "nearly_sorted":
                # Sort once, then slightly disturb
                mergeSort(dataset_merge) # Sort the base dataset
                dataset_quick = np.copy(dataset_merge) # Copy the nearly sorted state
                
                # Shuffle a small percentage of elements to make it "nearly sorted"
                idx = np.arange(size)
                np.random.shuffle(idx[:int(size * 0.1)])
                dataset_merge = dataset_merge[idx[np.argsort(idx)]] # Re-index based on shuffled indices
                dataset_quick = dataset_quick[idx[np.argsort(idx)]] # Re-index based on shuffled indices
                
            elif cond == "reversed":
                # Sort once, then reverse
                mergeSort(dataset_merge) # Sort the base dataset
                dataset_merge = dataset_merge[::-1] # Reverse it (NumPy array slicing)
                dataset_quick = np.copy(dataset_merge) # Copy the reversed state

            start = time.time()
            mergeSort(dataset_merge)
            merge_time = time.time() - start

            start = time.time()
            quickSortMedian3(dataset_quick)
            quick_time = time.time() - start

            print(f"{cond:<20}{size:<10}{merge_time:<20.6f}{quick_time:<20.6f}")
            
            current_size_node = current_size_node.getNext() # Move to next size
        
        current_cond_node = current_cond_node.getNext() # Move to next condition


# ---------------------------------------------------------
# Main Driver
# ---------------------------------------------------------
if __name__ == "__main__":
    benchmark_algorithms()