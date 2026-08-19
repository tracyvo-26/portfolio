# COMP5008 Final Assignment: Critical Care Optimisation

**Author:** [Thuy Tram Vo] ([22074430])
**Date:** [Submission Date - October 22, 2025]

This repository contains the solution for the COMP5008 Final Assignment, implementing a modular hospital resource management system. The system demonstrates efficient patient information storage, hospital navigation, priority-based scheduling, and patient record sorting.

The project is structured into four main modules, along with supporting data structures and an integrated test script:

*   `module1_graph.py`: Graph-Based Hospital Navigation
*   `module2_hashtable.py`: Hash-Based Patient Lookup
*   `module3_heap.py`: Heap-Based Emergency Scheduling (Placeholder)
*   `module4_sorting.py`: Sorting Patient Records (Placeholder)
*   `integrated_test.py`: Script to demonstrate the integration of all modules.
*   `linkedlist.py`: Custom Linked List implementation.
*   `stacksqueue.py`: Custom Stack and Queue implementations.
*   `sorts.py`: Custom Bubble Sort implementations.

## Overall Setup Instructions

To run this project, you will need Python 3 installed.

 **Install numpy:**
    This project uses `numpy` for array initialization in the hash table.
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: The assignment disallows built-in functions for core logic, but `numpy` is used here for array creation, which is an acceptable external library for array structures if not replacing core algorithm logic.)*

## Module 1: Graph-Based Hospital Navigation (`module1_graph.py`)

### Description
This module models the hospital's departments and corridors as a weighted, undirected graph. It supports dynamic insertion/removal of departments and corridors, Breadth-First Search (BFS) for level-wise traversal, Depth-First Search (DFS) for cycle detection, and the A* algorithm (implemented as Dijkstra's) for finding the shortest path between departments.

### How to Run
To run the main demonstration for the Graph module, execute the `module1_graph.py` script directly:
```bash
python module1_graph.py
```

### Sample Input
The run_test_case() function within module1_graph.py contains hardcoded test data for departments and paths. This includes:

Adding at least 8 departments (Emergency, ICU, Pharmacy, Radiology, Laboratories, Operating Theatres, Wards, Outpatient Units).
Adding 10-12 weighted corridors, ensuring at least one cycle and one isolated department (Outpatient Units).
Demonstrations of adding/removing departments and paths.

### Expected Output
The script will print a detailed log to the console, including:

Confirmation of department and path additions/removals.
A textual representation of the graph's adjacency list (Hospital Paths (Adjacency List)).
The total number of departments and paths.
BFS results, showing reachable departments grouped by level (hops) from specified source departments (e.g., "Emergency", "Outpatient Units"). Departments within each level are sorted alphabetically.
DFS cycle detection results, indicating whether cycles exist and listing cycle members if found (sorted alphabetically within each cycle).
Shortest path and total walking time (in minutes) from various source to destination departments using the A* algorithm (e.g., "Emergency to Wards", "Radiology to Operating Theatres", and a case of an unreachable department).
Demonstration of graph state changes after path and department removals.

### How to Test
The if __name__ == "__main__": block in module1_graph.py executes the run_test_case() function. This function serves as the primary test driver for Module 1, covering all required functionalities. The outputs described above confirm the correctness of the implementation.

## Module 2: Hash-Based Patient Lookup (module2_hashtable.py)
### Description
This module implements a hash table to store, retrieve, update, and delete patient records efficiently. It uses open addressing with double hashing for collision resolution and supports dynamic resizing (up and down) to maintain performance. It integrates with Module 1 by validating department names against the HospitalNavigationGraph.

### How to Run
To run the main demonstration for the Hash Table module, execute the module2_hashtable.py script directly:
``` bash
python module2_hashtable.py
```
### Sample Input
The run_module2_tests() function within module2_hashtable.py includes:
Initialization of a HospitalNavigationGraph (from Module 1) to provide valid department names for patient data validation.
Validation tests for PatientDetailsEntry with various valid and invalid data scenarios (e.g., negative ID, bad age, non-existent department).
Insertion of at least 20 diverse patient records (with varying urgency levels and departments).
Demonstrations of successful and unsuccessful searches.
Demonstrations of patient record updates.
Demonstrations of deletions and their effect on subsequent searches.
Examples showing collision scenarios (via probe sequences) and how resizing is triggered.

### Expected Output
The script will print a detailed log to the console, including:
Messages confirming hash table initialization and size.
Output from PatientDetailsEntry validation tests, indicating whether data is valid and why.
For each insert, search, and delete operation:
The PatientID and the Probe sequence (the indices visited during the hash table operation). This explicitly demonstrates collision handling.
Confirmation messages (e.g., "Record inserted successfully.", "Patient not found.").
Messages indicating when resizing (up or down) occurs, along with the old and new table sizes.
--- Current Hash Table State --- printouts at various points, showing the index, state (NEVER_USED, USED, FORMERLY_USED), PatientID, and Name for each slot. This provides clear intermediate states and verifies collision resolution.
Confirmation of patient data after updates and verification that deleted patients are no longer found.
Output from exporting active patients to a queue.

### How to Test
The if __name__ == '__main__': block in module2_hashtable.py executes the run_module2_tests() function. This function serves as the primary test driver for Module 2. The printed logs and table states confirm the correctness of insertion, search, deletion, collision handling, and resizing. Error handling for invalid inputs is also demonstrated.


## Module 3: Heap-Based Emergency Scheduling (module3.py)
### Description
This module implements a Max-Heap data structure (DSAHeap) to manage patient priorities for emergency scheduling. It defines DSAHeapEntry for storing priority and patient ID. It includes a calculate_priority function that computes a patient's priority based on their urgency level and estimated total treatment time (combining travel time from Module 1's graph and a mock procedure time). The DSAHeap supports efficient insertion, peeking, extraction of the highest priority patient, and updating patient priorities by re-insertion.

### Dependencies
This module depends on module1file.py (for HospitalNavigationGraph) and module2file.py (for PatientDetailHashTable and PatientDetailsEntry). It also uses numpy for array-based heap implementation and stacksqueue for internal queue operations (though direct from stacksqueue import * may need adjustment for specific classes).

### How to Run
To run the main demonstration for the Heap module, execute the module3.py script directly:
``` Bash
python module3.py
```

### Input for Testing

Hospital Graph Setup: Initializes a HospitalNavigationGraph (from module1file.py) with 8 departments and 10-12 weighted corridors, including cycles and an isolated department, mimicking a hospital layout.

Patient Hash Table Setup: Initializes a PatientDetailHashTable (from module2file.py) and inserts at least 10-20 diverse patient records. These records include PatientID, Name, Age, Department, UrgencyLevel, TreatmentStatus, DestinationDepartment, and MockProcedureTime. It specifically includes patients with "Completed" status and one patient in an "Outpatient Units" (isolated) department to test edge cases for priority calculation.

Heap Operations:
Creates a DSAHeap with an initial small size to demonstrate resizing.
Inserts all "Under Treatment" patients from the hash table into the heap after calculating their priority.
Performs 5 extractions to demonstrate that higher-priority patients are consistently served first.
Demonstrates updating a patient's urgency level (e.g., Patient 1010's urgency changed to 1) and re-calculating/re-inserting their priority into the heap, followed by another extraction to show the effect.

### Expected Output
The script will print a detailed log to the console, including:

Initialization messages for the hospital graph, patient hash table, and the heap.
Confirmation of patient insertions into the hash table.
"Log" messages for each priority calculation, showing U (Urgency), T_travel (travel time from Module 1), T_proc (mock procedure time), and the Final Priority.
A sequence of heap states (readable array printout of Prio: X.XX, Val: PatientID) after each insert and extract_priority operation. This visually demonstrates the heap property being maintained.
"Log" messages for each insertion and extraction, indicating the Patient ID and calculated Priority.
Evidence that higher-priority patients are consistently served first during extractions, including the order of Patient IDs served.
Detailed logs for patient urgency updates, including removal of old entries and re-insertion with new priorities, followed by the heap state.
Confirmation of served patients (ID, Name, Urgency) after extraction.

### How to Test
The if __name__ == "__main__": block within module3.py acts as the comprehensive test harness. Running the script directly executes a full demonstration that covers:

Integration with Module 1 (for shortest path/travel time) and Module 2 (for patient data).
Correctness of the DSAHeap implementation (insert, peek, extract_priority, trickleUp, trickleDown).
Accurate priority calculation based on the formula (6 - U) + 1000 / T.
Heap property maintenance during all operations, demonstrated by heap state printouts.
Handling of edge cases such as "Completed" patients, invalid patient data, unreachable departments (travel time = 0), and heap resizing.
The update_patient_urgency_and_new_priority method demonstrating updates.

## Module 4: Patient Data Generation and Sorting Benchmarking (module4.py)
### Description
This module focuses on generating simulated patient datasets and benchmarking the performance of two comparison-based sorting algorithms: Merge Sort (top-down) and Quick Sort (with Median-of-Three pivot strategy). Datasets are generated with varying sizes and conditions (random, nearly sorted, reversed), and sorting is performed based on the expected_treatment_time attribute of PatientDetailsEntry objects. The expected_treatment_time is derived from a mock procedure time combined with travel time calculated using Module 1's HospitalNavigationGraph.

### Dependencies
This module depends on numpy for array manipulation, module1file.py (for HospitalNavigationGraph), module2file.py (for PatientDetailsEntry), and linkedlist.py (for DSALinkedList used in benchmarking control flow).

### How to Run
To run the benchmarking and correctness validation for the Sorting module, execute the module4.py script directly:
``` Bash
python module4.py
```
### Sample Input
The benchmark_algorithms() function in module4.py generates synthetic patient datasets dynamically for testing:

Dataset Sizes: 100, 500, and 1000 patients are generated.
Input Conditions: For each size, datasets are created under three conditions:
"random": Newly generated, unsorted data.
"nearly_sorted": A dataset is sorted and then approximately 10% of its elements are randomly displaced.
"reversed": A dataset is sorted and then completely reversed.
Graph Integration: The generate_patient_dataset function internally uses build_hospital_graph() (which utilizes module1file.py's HospitalNavigationGraph) to calculate realistic travel times, which contribute to the expected_treatment_time of each patient.

### Expected Output
The script will print results to the console, including:

#### Correctness Validation:
A small example dataset (e.g., 10 patients) with their expected_treatment_time before sorting.
The same dataset after being sorted by Merge Sort, showing Patient ID and expected_treatment_time in ascending order.
The same dataset after being sorted by Quick Sort, showing Patient ID and expected_treatment_time in ascending order. This visually confirms the correctness of both sorting implementations.
#### Benchmarking Results:
A formatted table summarizing the execution times (in seconds) for Merge Sort and Quick Sort.
The table will display results for each Condition (random, nearly_sorted, reversed) and Size (100, 500, 1000).

### How to Test
The if __name__ == "__main__": block in module4.py directly executes the benchmark_algorithms() function, which acts as the comprehensive test driver. Running this script performs:
Algorithm Correctness: The initial validation test with a small dataset visually confirms that both mergeSort and quickSortMedian3 correctly sort the PatientDetailsEntry objects based on their expected_treatment_time.
Performance Benchmarking: The subsequent benchmark loop automatically generates datasets, applies the specified conditions, runs both sorting algorithms, and records/prints their execution times. This allows for direct comparison and analysis of their performance characteristics under varying inputs, fulfilling the assignment requirements for benchmarking.

## Integrated Test: Comprehensive System Flow (integrated_test.py)
### Description
This file orchestrates a comprehensive end-to-end test of all four modules working together, demonstrating the flow of data and interactions between the HospitalNavigationGraph (Module 1), PatientDetailHashTable (Module 2), DSAHeap (Module 3), and the sorting algorithms (Module 4). It simulates a hospital's daily operations by loading patient data from a CSV file, processing it through each module, and generating reports.

### Dependencies
This file imports module1file.py, module2file.py, module3file.py, and module4file.py. It also relies on numpy, csv, sys, and os for file operations and system-level control. An external patients.csv file is required as input.

### How to Run
To execute the integrated test, ensure you have a patients.csv file in the same directory as integrated_test.py. Then, run the script directly:

```Bash
python integrated_test.py
```
Important: The script redirects all console output to integrated_test_report.txt. After execution, open this file to view the detailed report. It also generates a sorted_under_treatment_patients.csv file.

### Sample Input
The primary input for this integrated test is a patients.csv file. This CSV file is expected to contain patient records with fields such as: PatientID, Name, Age, Department, UrgencyLevel, TreatmentStatus, DestinationDepartment, and MockProcedureTime. An example patients.csv might look like:

```bash
Csv
PatientID,Name,Age,Department,UrgencyLevel,TreatmentStatus,DestinationDepartment,MockProcedureTime
100,Alice Smith,35,Emergency,1,Under Treatment,Radiology,50.0
101,Bob Johnson,60,ICU,3,Under Treatment,Wards,40.0
102,Charlie Brown,28,Pharmacy,2,Under Treatment,Emergency,30.0
103,Diana Prince,45,Wards,4,Completed,,
104,Eve Adams,55,Emergency,1,Under Treatment,Operating Theatres,70.0
... (more patient records)
```
The script also internally sets up a HospitalNavigationGraph with predefined departments and paths, which serves as an implicit input for Module 1's pathfinding and Module 2/3's validation.

### Expected Output
All output from the integrated test will be redirected to a file named integrated_test_report.txt. Additionally, a new CSV file, sorted_under_treatment_patients.csv, will be created.

The integrated_test_report.txt will contain a comprehensive log, including:

#### Module 1 Setup:
Confirmation of department and path additions to the HospitalNavigationGraph.
A display of the hospital's path list (adjacency list).
#### CSV Processing and Integration:
Detailed logs for each patient record processed from patients.csv.
Warnings for missing or invalid data (e.g., MockProcedureTime not provided, no path found between departments).
Calculated ExpectedTreatmentTime for "Under Treatment" patients, showing components from travel time (Module 1) and mock procedure time.
Confirmation of patient insertion into the PatientDetailHashTable (Module 2).
Confirmation of patient insertion into the DSAHeap (Module 3) with their calculated priority, or a note if they did not qualify (e.g., "Completed" status).
#### Module 2 Functionality Demonstration:
The complete state of the PatientDetailHashTable after all CSV data has been loaded.
Demonstration of searching for a patient by ID.
Demonstration of updating a patient's record in the hash table (e.g., changing urgency, name).
Demonstration of removing a patient from the hash table.
#### Module 3 Functionality Demonstration:
The state of the DSAHeap before and after extracting highest priority patients.
Detailed logs of priority updates for patients (e.g., Patient 100's urgency changed, leading to re-calculation and re-insertion into the heap).
Logs of extracted patients, showing their PatientID, Name, Priority, and current Department, confirming that the highest-priority patients are served first.
#### Module 1 Functionality Demonstration (Ad-hoc):
Shortest path calculation between specified departments using A*.
Results of BFS traversal from a source department.
Results of DFS cycle detection from a source department.
#### Module 4 Functionality Demonstration:
Confirmation of the number of "Under Treatment" patients collected for sorting.
The expected_treatment_time for the first few "Under Treatment" patients before sorting.
Execution times for Merge Sort and Quick Sort on this collected data.
The expected_treatment_time for the first few patients after being sorted by each algorithm, demonstrating correctness.
#### CSV Output:
A message confirming the successful writing of the sorted_under_treatment_patients.csv file, which will contain all "Under Treatment" patients sorted by their ExpectedTreatmentTime.
### How to Test
This integrated_test.py file is the primary test driver for system integration. To test the complete flow and interaction between modules:

#### Prepare patients.csv:
Ensure a valid patients.csv file is available in the same directory, containing a mix of patient statuses, valid/invalid data, and departments.
#### Run the script: 
Execute python integrated_test.py.
#### Review integrated_test_report.txt: Open the generated integrated_test_report.txt and carefully review the logs.
Verify that data from the CSV is parsed and validated correctly by Module 2.
Check that Module 1's pathfinding is correctly used to calculate ExpectedTreatmentTime.
Confirm that patients are inserted into Module 2's hash table and Module 3's heap as expected, with correct priorities.
Observe the heap's state changes and verify that extractions follow priority.
Ensure updates (e.g., urgency changes) correctly propagate through Module 2 and Module 3.
Verify the ad-hoc Module 1 operations (shortest path, BFS, DFS) work as expected.
Confirm that "Under Treatment" patients are correctly collected and sorted by Module 4, and that the output CSV is generated correctly.
Look for any Error or Warning messages in the report, indicating issues with data handling or algorithm execution.