# -------------------------------------------------------------------------
# INTEGRATION TEST
# -------------------------------------------------------------------------
# Purpose:
# This file is orchestrates a comprehensive end-to-end test that shows
# the flow of data and interactions between 4 modules. It simulates a 
# hospital's daily operations by loading patient data from a CSV file, 
# processing it through each module, and generating reports.
# -------------------------------------------------------------------------

import csv
import sys
import os
import numpy as np 

output_filename = "integrated_test_report.txt"
sys.stdout = open(output_filename, 'w', encoding='utf-8')
output_sorted_csv_file_path = 'sorted_under_treatment_patients.csv'

# Import all modules
from module1file import *
from module2file import *
from module3file import *
from module4file import *

print("--- Starting Integrated Test Case ---")

# --- Setup Module 1: Hospital Graph ---
print("\n--- Module 1: Hospital Graph Setup ---")
hospital_graph = HospitalNavigationGraph()
print("--- Adding Departments ---")
hospital_graph.add_department("Emergency")
hospital_graph.add_department("ICU")
hospital_graph.add_department("Pharmacy")
hospital_graph.add_department("Radiology")
hospital_graph.add_department("Laboratories")
hospital_graph.add_department("Operating Theatres")
hospital_graph.add_department("Wards")
hospital_graph.add_department("Outpatient Units")

hospital_graph.add_path("Emergency", "Radiology", 10)
hospital_graph.add_path("Radiology", "Laboratories", 8)
hospital_graph.add_path("Laboratories", "Emergency", 12) # Completes first cycle
hospital_graph.add_path("Laboratories", "Pharmacy", 5)
hospital_graph.add_path("Laboratories", "ICU", 2)
hospital_graph.add_path("Laboratories", "Wards", 5)
hospital_graph.add_path("Pharmacy", "ICU", 7)
hospital_graph.add_path("ICU", "Wards", 9)
hospital_graph.add_path("Wards", "Pharmacy", 6) # Completes second cycle
hospital_graph.add_path("ICU", "Operating Theatres", 4)
hospital_graph.add_path("Radiology", "Wards", 15)

hospital_graph.display_path_list()
print(f"Total departments: {hospital_graph.get_department_count()}")
print(f"Total paths: {hospital_graph.get_path_count()}")

# --- Setup Module 2: Patient Hash Table ---
print("\n--- Module 2: Patient Management System (Hash Table) Setup ---")
patient_table = PatientDetailHashTable(tableSize=200) # Initial size, will resize if needed

# --- Setup Module 3: Patient Priority Heap ---
print("\n--- Module 3: Patient Priority Heap Setup ---")
patient_priority_heap = DSAHeap(size=20) # Initial heap size

# --- CSV File Processing and Integration ---
print("\n--- Processing Patient Data from CSV and Integrating Modules ---")
csv_file_path = 'patients.csv'
processed_patients_for_sorting = [] # To collect valid 'Under Treatment' patients with calculated ETT for Module 4 sorting


try:
    with open(csv_file_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        line_num = 1
        for row in reader:
            line_num += 1
            print(f"\nProcessing row {line_num-1}: {row['Name']} (ID: {row['PatientID']})...")
            try:
                # Convert relevant fields to their correct types
                patient_id = int(row['PatientID'])
                age = int(row['Age'])
                urgency_level = int(row['UrgencyLevel'])
                
                # Handling empty strings for optional fields from CSV
                destination_department = row['DestinationDepartment'].strip() if row['DestinationDepartment'] else None
                mock_procedure_time_str = row['MockProcedureTime'].strip() if row['MockProcedureTime'] else None
                mock_procedure_time = float(mock_procedure_time_str) if mock_procedure_time_str else None
                expected_treatment_time = 0
                # Create a PatientDetailsEntry object (initially without ExpectedTreatmentTime)
                patient_entry = PatientDetailsEntry(
                    PatientID=patient_id,
                    Name=row['Name'],
                    Age=age,
                    Department=row['Department'],
                    UrgencyLevel=urgency_level,
                    TreatmentStatus=row['TreatmentStatus'],
                    DestinationDepartment=destination_department,
                    MockProcedureTime=mock_procedure_time,
                    ExpectedTreatmentTime = expected_treatment_time
                )
                
                # --- Crucial step for Module 4: Calculate ExpectedTreatmentTime for 'Under Treatment' patients ---
                
                if patient_entry.treatment_status == "Under Treatment":
                    # Validate if essential fields for ETT calculation are present
                    is_valid_for_ett, ett_error_msg = patient_entry.is_valid_patient_data(
                        graph_instance=hospital_graph, stage="module3") # Use module3 stage for stricter validation

                    if is_valid_for_ett:
                        # Find travel time using Module 1
                        travel_path_str, travel_time = hospital_graph.find_shortest_path_a_star(
                            patient_entry.department, patient_entry.destination_department)

                        if travel_time is None: # If A* couldn't find a path
                            print(f"  Warning: No path found for Patient ID {patient_id} from {patient_entry.department} to {patient_entry.destination_department}. Assuming travel time 0.")
                            travel_time = 0

                        # Ensure mock_procedure_time is a valid number, default to 0 if not provided
                        if patient_entry.mock_procedure_time is None:
                            print(f"  Warning: MockProcedureTime not provided for Patient ID {patient_id}. Assuming 0.")
                            patient_entry.mock_procedure_time = 0.0 

                        patient_entry.expected_treatment_time = travel_time + patient_entry.mock_procedure_time
                        #patient_entry.ExpectedTreatmentTime = expected_treatment_time # Assign to the patient_entry object
                        print(f"  Calculated Expected Treatment Time for Patient ID {patient_id}: {patient_entry.expected_treatment_time} min (Travel: {travel_time}, Proc: {patient_entry.mock_procedure_time})")
                    else:
                        print(f"  Warning: Patient ID {patient_id} ('Under Treatment') data invalid for ETT calculation: {ett_error_msg}. Setting ETT to 0.")
                        patient_entry.expected_treatment_time = 0.0 # Default to 0 if data is not valid for calculation
                else: # For 'Completed' patients, ETT is not relevant for active treatment sorting
                    patient_entry.expected_treatment_time = None # Explicitly set to None for completed patients


                # Module 2: Insert into Hash Table (after initial validation)
                patient_table.insert(
                    patient_entry.patient_id,
                    patient_entry.name,
                    patient_entry.age,
                    patient_entry.department,
                    patient_entry.urgency_level,
                    patient_entry.treatment_status,
                    patient_entry.destination_department,
                    patient_entry.mock_procedure_time,
                    patient_entry.expected_treatment_time,
                    graph_instance=hospital_graph # Pass graph for department validation
                )
                print(f"  Patient ID {patient_entry.patient_id} successfully added to hash table as {patient_entry.treatment_status} with ETT {patient_entry.expected_treatment_time}.")

                # Module 3: Calculate priority and add to Heap
                # The calculate_priority function also performs validation relevant to active patients.
                priority = calculate_priority(patient_entry, hospital_graph)
                if priority is not None:
                    patient_priority_heap.insert(priority, patient_entry.patient_id)
                    print(f"  Patient ID {patient_id} added to priority heap with priority: {priority:.2f}")
                else:
                    print(f"  Patient ID {patient_id} did not qualify for priority heap (e.g., 'Completed' status or invalid data).")

                # Collect valid 'Under Treatment' patients with calculated ETT for Module 4 sorting
                # Only add if ETT was actually calculated (i.e., not None) and status is "Under Treatment"
                if patient_entry.treatment_status == "Under Treatment" and patient_entry.expected_treatment_time is not None:
                     processed_patients_for_sorting.append(patient_entry)

            except ValueError as e:
                print(f"  Error parsing data for Patient ID {row.get('PatientID', 'N/A')} on line {line_num}: {e}")
            except Exception as e:
                print(f"  An unexpected error occurred for Patient ID {row.get('PatientID', 'N/A')} on line {line_num}: {e}")




except FileNotFoundError:
    print(f"Error: The file '{csv_file_path}' was not found.")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred while reading the CSV file: {e}")
    sys.exit(1)

# --- Demonstrating Module 2 (Hash Table) Functionality ---
print("\n--- Module 2: Hash Table State After CSV Load ---")
patient_table.print_table_state()

print("\n--- Module 2: Searching and Updating ---")
try:
    search_id = 100
    found_patient = patient_table.search(search_id)
    print(f"  Found patient {search_id}: {found_patient.name}, Age: {found_patient.age}")

    # Update patient 101's urgency and treatment status
    patient_table.update(
        patient_id=search_id,
        name="Alice Smith-Updated",
        age=36,
        department="Emergency",
        urgency_level=2, # Changed from 1 to 2
        treatment_status="Under Treatment",
        graph_instance=hospital_graph
    )
    print(f"  Patient {search_id} updated in hash table. New urgency level: {patient_table.search(search_id).urgency_level}")

    # Re-calculate and update priority for patient 101 in the heap
    # This also re-validates and re-inserts into hash table via update_patient_urgency_and_new_priority
    updated_patient_entry_for_prio = patient_priority_heap.update_patient_urgency_and_new_priority(
        patient_id=search_id,
        new_urgency_level=2,
        patient_table=patient_table,
        hospital_graph=hospital_graph
    )
    print(f"  Patient {search_id}'s priority updated in heap due to urgency change.")

    # Remove a patient from the hash table and heap
    remove_id = 104 # Diana Prince (Completed status, but demonstrate removal)
    patient_table.remove(remove_id)
    print(f"  Patient {remove_id} removed from hash table.")
    try:
        # Before attempting to remove from heap, check if it was ever there
        if patient_priority_heap.find_index(remove_id) != -1:
            patient_priority_heap.remove(remove_id)
            print(f"  Patient {remove_id} also removed from priority heap.")
        else:
            print(f"  Patient {remove_id} was not in the priority heap (expected for 'Completed' status).")
    except (IndexError, ValueError):
        print(f"  Patient {remove_id} not found in heap for removal (may have already been handled or not present).")

except Exception as e:
    print(f"  Error during Module 2/3 demonstration: {e}")

# --- Demonstrating Module 3 (Heap) Functionality ---
print("\n--- Module 3: Priority Heap Operations ---")
patient_priority_heap._print_heap_state("Heap before extractions")

# Extract highest priority patients
print("\n  Extracting 3 highest priority patients:")
for _ in range(min(3, patient_priority_heap.count)):
    try:
        highest_prio_entry = patient_priority_heap.extract_priority()
        extracted_patient_id = highest_prio_entry.get_value()
        extracted_priority = highest_prio_entry.get_priority()

        # Retrieve full details from hash table for extracted patient
        extracted_patient_details = patient_table.search(extracted_patient_id)
        print(f"  Extracted Patient ID: {extracted_patient_id}, Name: {extracted_patient_details.name}, "
              f"Prio: {extracted_priority:.2f}, Current Dept: {extracted_patient_details.department}")
    except IndexError:
        print("  Heap is empty, no more patients to extract.")
        break
    except Exception as e:
        print(f"  Error during patient extraction: {e}")

patient_priority_heap._print_heap_state("Heap after extractions")

# --- Demonstrating Module 1 (Graph) Functionality ---
print("\n--- Module 1: Graph Pathfinding and Traversal ---")
start_dep = "Emergency"
goal_dep = "Operating Theatres"
try:
    path_str, total_time = hospital_graph.find_shortest_path_a_star(start_dep, goal_dep)
    if path_str:
        print(f"  Shortest path from {start_dep} to {goal_dep}: {path_str} ({total_time} minutes)")
    else:
        print(f"  No path found from {start_dep} to {goal_dep}.")
except ValueError as e:
    print(f"  Error finding path: {e}")

# BFS Traversal
try:
    hospital_graph.find_reachable_departments_by_level("Emergency")
except ValueError as e:
    print(f"  Error during BFS: {e}")

# DFS Cycle Detection
try:
    hospital_graph.detect_cycles_dfs("Emergency")
except ValueError as e:
    print(f"  Error during DFS cycle detection: {e}")

# --- Module 4: Sorting Benchmarking with collected data ---
print("\n--- Module 4: Sorting Benchmarking (Expected Treatment Time for 'Under Treatment' Patients) ---")
if not processed_patients_for_sorting:
    print("  No 'Under Treatment' patients with valid Expected Treatment Time were collected for sorting.")
else:
    print(f"  Benchmarking sorting for {len(processed_patients_for_sorting)} 'Under Treatment' patients based on ExpectedTreatmentTime.")

    # Convert list to NumPy array for sorting functions
    patients_array_for_merge = np.array(processed_patients_for_sorting, dtype=object)
    patients_array_for_quick = np.copy(patients_array_for_merge)

    print("\n  Original (first 5 patients with ETT):")
    for i in range(min(5, len(patients_array_for_merge))):
        p = patients_array_for_merge[i]
        print(f"    ID {p.patient_id}: {p.expected_treatment_time} min")

    # Merge Sort
    import time
    start_time = time.time()
    mergeSort(patients_array_for_merge)
    merge_sort_time = time.time() - start_time
    print(f"\n  Merge Sort completed in {merge_sort_time:.6f} seconds.")
    print("  Sorted by Merge Sort (first 5 patients with ETT):")
    for i in range(min(5, len(patients_array_for_merge))):
        p = patients_array_for_merge[i]
        print(f"    ID {p.patient_id}: {p.expected_treatment_time} min")

    # Quick Sort
    start_time = time.time()
    quickSortMedian3(patients_array_for_quick)
    quick_sort_time = time.time() - start_time
    print(f"\n  Quick Sort (Median-of-Three) completed in {quick_sort_time:.6f} seconds.")
    print("  Sorted by Quick Sort (first 5 patients with ETT):")
    for i in range(min(5, len(patients_array_for_quick))):
        p = patients_array_for_quick[i]
        print(f"    ID {p.patient_id}: {p.expected_treatment_time} min")

    print(f"\nSorting benchmark summary:")
    print(f"  Merge Sort Time: {merge_sort_time:.6f} s")
    print(f"  Quick Sort Time: {quick_sort_time:.6f} s")

# --- Output Sorted Patients to CSV ---
    print(f"\n--- Outputting sorted patients to '{output_sorted_csv_file_path}' ---")
    try:
        fieldnames = ['PatientID', 'Name', 'Age', 'Department', 'UrgencyLevel', 
                      'TreatmentStatus', 'DestinationDepartment', 'MockProcedureTime', 
                      'ExpectedTreatmentTime']

        with open(output_sorted_csv_file_path, mode='w', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for patient_entry in patients_array_for_merge: # Use the merge-sorted array for output
                # Create a dictionary for each patient_entry
                row_dict = {
                    'PatientID': patient_entry.patient_id,
                    'Name': patient_entry.name,
                    'Age': patient_entry.age,
                    'Department': patient_entry.department,
                    'UrgencyLevel': patient_entry.urgency_level,
                    'TreatmentStatus': patient_entry.treatment_status,
                    'DestinationDepartment': patient_entry.destination_department if patient_entry.destination_department is not None else '',
                    'MockProcedureTime': f"{patient_entry.mock_procedure_time:.2f}" if patient_entry.mock_procedure_time is not None else '',
                    'ExpectedTreatmentTime': f"{patient_entry.expected_treatment_time:.2f}" if patient_entry.expected_treatment_time is not None else ''
                }
                writer.writerow(row_dict)
        print(f"Successfully wrote {len(patients_array_for_merge)} sorted patients to '{output_sorted_csv_file_path}'.")
    except Exception as e:
        print(f"Error writing sorted patients to CSV: {e}")

print("\n--- Integrated Test Case Finished ---")

sys.stdout.close()