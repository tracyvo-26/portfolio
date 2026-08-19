# -------------------------------------------------------------------------
# MODULE 3: Patient Priority and Heap Management
# -------------------------------------------------------------------------
# Purpose:
# This module implements a Max-Heap data structure to manage patient priorities.
# It includes a function to calculate patient priority based on urgency level
# and estimated total treatment time (combining travel time from Module 1
# and mock procedure time). Patients are managed in a priority queue,
# allowing the highest priority patient to be efficiently extracted.
# -------------------------------------------------------------------------

from stacksqueue import *
from module2file import *
from module1file import *
from sorts import *
import numpy as np # Make sure numpy is imported for np.empty

# -------------------------------------------------------------------------
# Custom Class: DSAHeapEntry
# -------------------------------------------------------------------------
class DSAHeapEntry:
    """
    Represents an entry in the heap, containing a priority and an associated value.
    This value will typically be a PatientID or a request object.
    """
    def __init__(self, prio, val):
        """
        Initializes a DSAHeapEntry.
        """
        self.priority = prio
        self.value = val # This will hold PatientID or a request object
    def get_priority(self):
        return self.priority
    def set_priority(self, new_prio):
        self.priority = new_prio
    def get_value(self):
        return self.value
    def set_value(self, new_val):
        self.value = new_val
    def __str__(self):
        return (f"Prio: {self.priority:.2f}, Val: {self.value}")

# -------------------------------------------------------------------------
# Main Class: DSAHeap
# -------------------------------------------------------------------------
class DSAHeap:
    """
    Implements a Max-Heap data structure using a NumPy array.
    A Max-Heap ensures that the element with the highest priority is always at the root (index 0).
    It supports insertion, peeking at the highest priority element, and extracting the highest priority element.
    The heap automatically resizes if its capacity is reached during insertion.
    """
    def __init__(self, size):
        """
        Initializes an empty Max-Heap with a specified initial capacity.
        """
        if size <= 0:
            raise ValueError("Heap size must be positive.")
        self.heap = np.empty(size, dtype = object)
        self.count = 0
        self.capacity = size
        print(f"Heap initialized with capacity {self.capacity}.")

    def _print_heap_state(self, message="Current Heap"):
        """
        Helper method to print the current state of the heap for debugging purposes.
        Shows the priority and value of each element in the underlying array.
        """
        print(f"\n--- {message} (Count: {self.count}/{self.capacity}) ---")
        if self.count == 0:
            print("Heap is empty.")
            return
        for i in range(self.count):
            entry = self.heap[i]
            if entry is not None:
                print(f"Prio: {entry.priority:.2f}, Val: {entry.value}")
            else:
                print(f"Index {i}: None")
        print("--- End Heap State ---")

    def insert(self, priority, value):
        """
        Inserts a new item with its priority into the heap.
        If the heap capacity is reached, it automatically resizes to double its current capacity.
        After insertion, it calls `_trickleUp` to maintain the heap property.
        """
        # Step 1: Validate input priority.
        if priority is None:
            raise ValueError("Priority cannot be None. Skipping insertion.")
        if not isinstance(priority, (int, float)):
            raise TypeError("Priority must be a number.")
        # Step 2: Check if heap needs resizing.
        if self.count >= self.capacity:
            print("  Heap capacity reached, resizing heap...")
            new_capacity = self.capacity * 2
            # Check for potential overflow during resizing for extremely large heaps.
            if new_capacity < self.capacity: # Check for overflow
                raise OverflowError("Heap capacity overflow during resize.")
            
            # Create a new, larger NumPy array and copy existing elements.
            resized_heap = np.empty(new_capacity, dtype = object)
            for i in range(self.count):
                resized_heap[i] = self.heap[i]
            # Update the heap reference and capacity
            self.heap = resized_heap
            self.capacity = new_capacity
            print(f"  Heap resized to capacity: {self.capacity}")
        # Step 3: Create a new DSAHeapEntry and insert it at the next available position.
        new_entry = DSAHeapEntry(priority, value)
        self.heap[self.count] = new_entry
        # Step 4: Call `_trickleUp` to restore the heap property, starting from the newly inserted element's position.
        self._trickleUp(self.count)
        self.count += 1
        print(f"  Log: Inserted: Patient ID {new_entry.value} (Prio: {new_entry.priority:.2f})")

    def peek(self):
        """
        Returns the value of the highest priority element in the heap without removing it.
        """
        if self.count == 0:
            raise IndexError("Heap is empty. Cannot peek element.")
        return self.heap[0].get_value()

    def extract_priority(self):
        """
        Removes and returns the DSAHeapEntry object with the highest priority from the heap.
        After extraction, the heap property is restored by moving the last element to the root
        and then calling `_trickleDown`.
        """
        # Step 1: Check if the heap is empty.
        if self.count == 0:
            raise IndexError("Heap is empty. Cannot extract element.")
        # Step 2: Store the highest priority entry (at the root) to be returned.
        highest_priority_entry = self.heap[0]
        # Step 3: Decrement the count of elements in the heap.
        self.count -= 1
        # Step 4: If there are still elements in the heap after decrementing the count.
        if self.count > 0:
            # Move last element to root
            self.heap[0], self.heap[self.count] = self.heap[self.count], self.heap[0] 
            self.heap[self.count] = None # Clear old last position
            self._trickleDown(0, self.count)
        else: # Heap becomes empty
            self.heap[0] = None # Clear root if it was the last element
        # Step 5: Return the highest priority entry that was extracted. 
        print(f"  Log: Extracted: Patient ID {highest_priority_entry.value} (Prio: {highest_priority_entry.priority:.2f})")
        return highest_priority_entry
    

    def _trickleUp(self, curIdx):
        """
        Recursively restores the Max-Heap property by moving an element up the heap
        from `curIdx` until it is in its correct position. This is typically called
        after an insertion.
        """
        parentIdx = (curIdx - 1) // 2
        # Base case for recursion: If `curIdx` is the root (0) or invalid, stop.
        if curIdx > 0 and self.heap[curIdx] is not None and self.heap[parentIdx] is not None: # Ensure not at the root
            # Max-heap: if current child's priority > parent's priority, swap
            if self.heap[curIdx].get_priority() > self.heap[parentIdx].get_priority():
                self.heap[parentIdx], self.heap[curIdx] = self.heap[curIdx], self.heap[parentIdx]
                self._trickleUp(parentIdx) # Continue trickling up

    def _trickleDown(self, curIdx, numItems):
        """
        Recursively restores the Max-Heap property by moving an element down the heap
        from `curIdx` until it is in its correct position. This is typically called
        after an extraction or removal.
        """
        lChildIdx = curIdx * 2 + 1
        rChildIdx = curIdx * 2 + 2
        
        largeIdx = curIdx # Assume current is largest

        # If the left child exists within the active heap size (`numItems`)
        # AND it's not None (robustness) AND its priority is greater than the current `largeIdx`'s priority.
        if lChildIdx < numItems and self.heap[lChildIdx] is not None and self.heap[lChildIdx].get_priority() > self.heap[largeIdx].get_priority():
            largeIdx = lChildIdx
        
        # If the right child exists within the active heap size (`numItems`)
        # AND it's not None (robustness) AND its priority is greater than the current `largeIdx`'s priority.
        # This comparison is against `largeIdx`, which might now be `lChildIdx` if left was larger than parent.
        if rChildIdx < numItems and self.heap[rChildIdx] is not None and self.heap[rChildIdx].get_priority() > self.heap[largeIdx].get_priority():
            largeIdx = rChildIdx
            
        # If largest is not current, swap and continue trickling down
        if largeIdx != curIdx:
            self.heap[largeIdx], self.heap[curIdx] = self.heap[curIdx], self.heap[largeIdx]
            self._trickleDown(largeIdx, numItems)

    def find_index(self, patient_id):
        """
        Finds the array index of a DSAHeapEntry whose `value` matches the given `patient_id`.
        This is a linear search operation, thus O(N) in the worst case.
        """
        for i in range(self.count):
            if self.heap[i] is not None and self.heap[i].get_value() == patient_id:
                return i
        return -1

    def remove(self, patient_id):
        """
        Removes an item with the specified `patient_id` (value) from the heap.
        This operation involves a linear search (O(N)) to find the element,
        and then heap re-organization (O(log N)).
        """
        # Step 1: Check if the heap is empty.
        if self.count == 0:
            raise IndexError("Heap is empty. Cannot remove element.")
        # Step 2: Find the index of the element to be removed.
        remove_idx = self.find_index(patient_id)
        if remove_idx == -1:
            raise ValueError(f"Value {patient_id} not found in heap. Cannot remove.")
        # Step 3: Store the entry to be removed for logging and return.
        removed_entry = self.heap[remove_idx]
        print(f"  Log: Removing: Patient ID {removed_entry.get_value()} (Prio: {removed_entry.get_priority():.2f}) from index {remove_idx}")
        # Step 4: Decrement the count of elements in the heap.
        self.count -= 1
        # Step 5: Handle the removal based on whether the element to be removed is the last element.
        if remove_idx != self.count: # If not the last element, swap with last
            self.heap[remove_idx], self.heap[self.count] = self.heap[self.count], self.heap[remove_idx]
            self.heap[self.count] = None 
            # The element now at remove_idx needs to be correctly positioned
            # Compare with its new parent to see if it needs to trickle up or down
            parent_of_moved = (remove_idx - 1) // 2
            if remove_idx > 0 and self.heap[remove_idx] is not None and self.heap[parent_of_moved] is not None and \
               self.heap[remove_idx].get_priority() > self.heap[parent_of_moved].get_priority():
                self._trickleUp(remove_idx)
            else: # Otherwise, it might need to trickle down
                self._trickleDown(remove_idx, self.count)
        # If the element to be removed IS the last element in the heap.
        # Just clear the last element's position.
        else:
            self.heap[self.count] = None
        # Step 6: Return the removed heap entry.
        return removed_entry
    
    def reinsert_updated_priority(self, patient_id, new_priority):
        """
        Updates the priority of a patient in the heap. This is achieved by:
        1. Searching for and removing the existing patient entry (if found).
        2. Inserting a new entry with the specified `patient_id` and `new_priority`.
        This method ensures that if a patient's priority changes, their position in the
        heap is correctly adjusted, and no duplicate `patient_id` entries exist.
        """
        # Step 1: Check if the patient already exists in the heap.
        existing_idx = self.find_index(patient_id)

        # If the patient is found, remove their old entry.
        if existing_idx != -1:
            try:
                self.remove(patient_id)
                print(f"  Log: Old entry for Patient ID {patient_id} removed before re-insertion.")
            except IndexError:
                # This case is unlikely if find_index returned != -1, but included for robust error handling.
                print(f"  Warning: Heap became empty while trying to remove Patient ID {patient_id}.")
            except ValueError as e:
                # Catch if find_index returned true but remove didn't find it (potential logic error or race condition).
                print(f"  Error during removal for update of Patient ID {patient_id}: {e}")
        # If the patient is not found, a new insertion will be performed.
        else:
            print(f"  Log: Patient ID {patient_id} not found in heap for update, performing a new insertion.")
        
        # Step 2: Insert the patient with the new priority.
        # This will either be a fresh insertion or re-insertion after removal, correctly positioning the patient.
        self.insert(new_priority, patient_id)
        print(f"  Log: Patient ID {patient_id} re-inserted with new priority {new_priority:.2f}.")


    def old_record(self, patient_id, patient_table: PatientDetailHashTable):
        """
        Searches for a patient's record in the provided `patient_table` using their ID.
        This method simplifies retrieving an existing `PatientDetailsEntry` object.
        """
        # Step 1: Validate the `patient_table` input.
        if not isinstance(patient_table, PatientDetailHashTable):
            raise TypeError("`patient_table` must be an instance of PatientDetailHashTable from Module 2.")
        
        print(f"\n  Log: Searching for old record for Patient ID: {patient_id}...")
        # Step 2: Use the `search` method of the `patient_table` to find the record.
        old_patient_record = patient_table.search(patient_id) # This call handles Not Found internally or by raising.

        # Case 2.1: If `old_patient_record` is None, it means the search failed (e.g., if search returns None).
        if old_patient_record is None:
            raise ValueError(f"Patient ID {patient_id} not found in the patient table.")
        
        # Step 3: Print details of the found record for confirmation.
        print(f"  Old record found for {patient_id}: Urgency {old_patient_record.urgency_level}, "
              f"Current Dept: {old_patient_record.department}, "
              f"Dest Dept: {old_patient_record.destination_department}, "
              f"Proc Time: {old_patient_record.mock_procedure_time}")
        
        return old_patient_record

    def update_patient_urgency_and_new_priority(self, patient_id, new_urgency_level, patient_table: PatientDetailHashTable, hospital_graph: HospitalNavigationGraph):
        """
        Updates an existing patient record in the `patient_table` and then re-calculates
        and updates their priority in the heap.
        This method streamlines the process of modifying patient details and reflecting
        those changes in the priority queue.
        """
        # Step 1: Validate inputs for patient_table and hospital_graph.
        if not isinstance(patient_table, PatientDetailHashTable):
            raise TypeError("`patient_table` must be an instance of PatientTable from Module 2.")
        if not isinstance(hospital_graph, HospitalNavigationGraph):
            raise TypeError("`hospital_graph` must be an instance of HospitalNavigationGraph from Module 1.")
        
        # Step 2: Validate `new_urgency_level`.
        if not isinstance(new_urgency_level, int) or not (1 <= new_urgency_level <= 5):
            raise ValueError("New urgency level must be an integer between 1 and 5.")

        print(f"\n  Log: Attempting to update record for Patient ID {patient_id} with new urgency {new_urgency_level}...")
        
        # Step 3: Retrieve the existing patient record using `old_record` helper.
        try:
            old_record_entry = self.old_record(patient_id, patient_table)
        except (ValueError, TypeError) as e:
            print(f"  Error: Could not retrieve old record for Patient ID {patient_id}. {e}")
            return None # Cannot proceed if old record is not found or invalid.

        # Step 4: Create a new PatientDetailsEntry object with the updated urgency level,
        # retaining all other details from the old record.
        updated_record_entry = PatientDetailsEntry(
            PatientID=old_record_entry.patient_id,
            Name=old_record_entry.name,
            Age=old_record_entry.age,
            Department=old_record_entry.department,
            UrgencyLevel=new_urgency_level, # Apply the new urgency level
            TreatmentStatus=old_record_entry.treatment_status,
            DestinationDepartment=old_record_entry.destination_department,
            MockProcedureTime=old_record_entry.mock_procedure_time
        )

        # Step 5: Update the record in the main patient_table (Module 2's PatientTable).
        patient_table.insert(
            updated_record_entry.patient_id,
            updated_record_entry.name,
            updated_record_entry.age,
            updated_record_entry.department,
            updated_record_entry.urgency_level,
            updated_record_entry.treatment_status,
            updated_record_entry.destination_department,
            updated_record_entry.mock_procedure_time
        )
        print(f"\n  Log: Patient record for ID {patient_id} updated in patient_table with new urgency {new_urgency_level}.")

        # Step 6: Recalculate the priority for the updated patient record.
        new_priority = calculate_priority(updated_record_entry, hospital_graph)
        
        # Case 6.1: If priority calculation returns None (e.g., patient completed treatment or invalid data).
        if new_priority is None:
            print(f"  Log: Priority for Patient ID {patient_id} not recalculated (e.g., completed or invalid).")
            # If the patient was previously in the heap, they should be removed.
            try:
                if self.find_index(patient_id) != -1:
                    self.remove(patient_id)
                    print(f"  Log: Patient ID {patient_id} removed from heap as no longer requiring active priority.")
            except (IndexError, ValueError):
                pass # Already not in heap, or heap empty.
            return updated_record_entry

        # Step 7: Update the patient's priority in the heap.
        # This will remove the old entry (if any) and insert the new one.
        self.reinsert_updated_priority(patient_id, new_priority)

        return updated_record_entry

    def _department_exists_in_graph(department_name, graph_instance):
        """
        Helper method to check if a department name exists in the graph.
        This function is intended for internal use or as a utility.
        """
        all_valid_names_list = graph_instance.get_all_department_names()
        current_name_node = all_valid_names_list.head
        while current_name_node:
            if current_name_node.getValue() == department_name:
                return True
            current_name_node = current_name_node.getNext()
        return False
                
# --- Priority Calculation Function ---
def calculate_priority(patient_record: PatientDetailsEntry, hospital_graph: HospitalNavigationGraph):
    """
    Calculates priority based on urgency level and estimated total treatment time.
    Receives a PatientDetailsEntry object and validates its relevant fields.
    Priority = (6 - U) + 1000 / T
    Higher priority value means higher priority for treatment.
    """
    # Step 1: Validate input types for `patient_record` and `hospital_graph`.
    if not isinstance(patient_record, PatientDetailsEntry):
        raise TypeError("Input must be a PatientDetailsEntry object.")
    if not isinstance(hospital_graph, HospitalNavigationGraph):
        raise TypeError("Input 'hospitali_graph' must be a HospitalNavigationGraph object.")

    # Step 2: Access relevant fields from the patient record for initial checks.
    treatment_status = patient_record.treatment_status
    patient_id = patient_record.patient_id

    # Step 3: IMPORTANT: Prioritize checking `treatment_status`.
    # If the patient's treatment is "Completed", no priority calculation is needed.
    if treatment_status == "Completed":
        print(f"  Patient ID {patient_id} has treatment status 'Completed'. No priority needed; skipping.")
        return None # Return None if no priority is to be calculated

    # Step 4: For "Under Treatment" cases, perform full data validation using Module 2's `is_valid_patient_data`.
    # This ensures that all necessary fields for priority calculation are valid.
    is_valid, error_msg = patient_record.is_valid_patient_data(graph_instance=hospital_graph, stage="module3")
    if not is_valid:    # If patient data is invalid for an active patient.
        print(f"  Invalid patient data for priority calculation (ID {patient_id}): {error_msg}. Skipping.")
        return None # Return None if patient data is invalid for scheduling an active patient

    # Step 5: If we reach here, the patient is "Under Treatment" and their data is valid.
    # Extract necessary details for priority calculation.
    urgency_level = patient_record.urgency_level
    patient_current_department = patient_record.department
    destination_department = patient_record.destination_department
    mock_procedure_time = patient_record.mock_procedure_time

    print(f"\n  Log: Calculating Priority for Patient ID {patient_id} (U={urgency_level}, Current='{patient_current_department}', Dest='{destination_department}', ProcTime={mock_procedure_time})...")

    # Step 6: Determine travel time using Module 1's A* shortest path algorithm.
    travel_time_from_module1 = 0
    try:
        # Call Module 1's shortest path algorithm
        path_str, travel_time_from_module1 = hospital_graph.find_shortest_path_a_star(
            patient_current_department, destination_department
        )
        if path_str is None: # A* returns None for path_str if no path found
             print(f"  Log: No path found from {patient_current_department} to {destination_department}. Defaulting travel time to 0.")
             travel_time_from_module1 = 0
        else:
             print(f"  Log: Module 1 returned travel time: {travel_time_from_module1} minutes for path: {path_str}.")

    except ValueError as e: # Catch specific error if path not found in Module 1
        print(f"  Error getting travel time for ID {patient_id}: {e}. Defaulting travel time to 0.")
        travel_time_from_module1 = 0
    except Exception as e:
        print(f"  Unexpected error getting travel time for ID {patient_id} from Module 1: {e}. Defaulting travel time to 0.")
        travel_time_from_module1 = 0

    # Step 7: Ensure `mock_procedure_time` is a valid number.
    if not isinstance(mock_procedure_time, (int, float)):
        print(f"  Validation Warning: MockProcedureTime for ID {patient_id} is not a number ({mock_procedure_time}). Using 1 for calculation.")
        mock_procedure_time = 1

    # Step 8: Calculate the total estimated treatment time.
    total_treatment_time = travel_time_from_module1 + mock_procedure_time

    # Step 9: Prevent division by zero or negative total treatment time in the priority formula.
    if total_treatment_time <= 0:
        print(f"  Validation Warning: Calculated TotalTreatmentTime '{total_treatment_time}' for ID {patient_id} is non-positive. Using 1 for calculation.")
        total_treatment_time = 1 # Prevent division by zero

    # Step 10: Calculate the final priority using the defined formula.
    # The (6 - urgency_level) component means lower urgency levels (1 is highest, 5 is lowest)
    # result in a higher base priority.
    # The (1000 / total_treatment_time) component means shorter treatment times result in higher priority.
    priority = (6 - urgency_level) + (1000 / total_treatment_time)
    print(f"  Log: Final Priority (U={urgency_level}, T_travel={travel_time_from_module1}, T_proc={mock_procedure_time}): {priority:.2f}")
    
    return priority


# --- Example Usage (Test Harness Module 3) ---
if __name__ == "__main__":
    print("--- Module 3 Test Cases: Heap-Based Emergency Scheduling ---")

    # 1. Setup Hospital Graph (Module 1 Dependency)
    print("\n--- Setting up Hospital Graph for Department Validation and Pathfinding ---")
    hospital_graph = HospitalNavigationGraph()
    hospital_graph.add_department("Emergency")
    hospital_graph.add_department("ICU")
    hospital_graph.add_department("Pharmacy")
    hospital_graph.add_department("Radiology")
    hospital_graph.add_department("Laboratories")
    hospital_graph.add_department("Operating Theatres")
    hospital_graph.add_department("Wards")
    hospital_graph.add_department("Outpatient Units") # Isolated department

    hospital_graph.print_all_department_names()

    # Adding corridors (paths) to create a connected network for A*
    hospital_graph.add_path("Emergency", "Radiology", 10)
    hospital_graph.add_path("Radiology", "Laboratories", 8)
    hospital_graph.add_path("Laboratories", "Emergency", 12) # Completes first cycle
    hospital_graph.add_path("Laboratories", "Pharmacy", 5)
    hospital_graph.add_path("Pharmacy", "ICU", 7)
    hospital_graph.add_path("ICU", "Wards", 9)
    hospital_graph.add_path("Wards", "Pharmacy", 6) # Completes second cycle
    hospital_graph.add_path("ICU", "Operating Theatres", 4)
    hospital_graph.add_path("Radiology", "Wards", 15) # Example additional edge
    hospital_graph.add_path("Emergency", "Wards", 20) # Another path for varied test

    # 2. Setup Patient Hash Table (Module 2 Dependency)
    print("\n--- Initializing Patient Hash Table (Module 2) ---")
    patient_table = PatientDetailHashTable(tableSize=11) # Initial size for 10-20 records. Let's use 11 to ensure prime.

    print("\n--- Inserting Patient Records into Hash Table ---")
    # PatientID, Name, Age, Department, Urgency, TreatmentStatus, Destination, ProcTime
    # The `insert` method is now corrected to properly receive and store DestinationDepartment and MockProcedureTime
    patient_table.insert(1001, "Alice Smith", 30, "Emergency", 3, "Under Treatment", "Radiology", 60, graph_instance=hospital_graph)
    patient_table.insert(1002, "Bob Johnson", 65, "ICU", 5, "Under Treatment", "Wards", 45, graph_instance=hospital_graph)
    patient_table.insert(1003, "Charlie Brown", 25, "Pharmacy", 1, "Under Treatment", "Radiology", 30, graph_instance=hospital_graph) 
    patient_table.insert(1004, "Diana Prince", 40, "Wards", 2, "Completed", "Emergency", 0, graph_instance=hospital_graph) 
    patient_table.insert(1005, "Eve Adams", 50, "Emergency", 4, "Under Treatment", "ICU", 75, graph_instance=hospital_graph)
    patient_table.insert(1006, "Frank Green", 35, "Pharmacy", 3, "Under Treatment", "Emergency", 40, graph_instance=hospital_graph) 
    patient_table.insert(1007, "Grace Lee", 22, "Radiology", 2, "Under Treatment", "ICU", 50, graph_instance=hospital_graph) 
    patient_table.insert(1008, "Heidi Klum", 70, "Wards", 5, "Completed", "Pharmacy", 20, graph_instance=hospital_graph) 
    patient_table.insert(1009, "Ivan Petrov", 45, "ICU", 1, "Under Treatment", "Emergency", 90, graph_instance=hospital_graph)
    patient_table.insert(1010, "Julia Roberts", 55, "Emergency", 4, "Under Treatment", "ICU", 30, graph_instance=hospital_graph)
    patient_table.insert(1011, "Kyle Walker", 60, "ICU", 2, "Completed", "ICU", 10, graph_instance=hospital_graph)
    patient_table.insert(1012, "Liam White", 33, "Emergency", 2, "Under Treatment", "Wards", 55, graph_instance=hospital_graph)
    patient_table.insert(1013, "Mia Stone", 48, "Radiology", 1, "Under Treatment", "Wards", 100, graph_instance=hospital_graph)
    patient_table.insert(1014, "Noah King", 75, "Pharmacy", 3, "Under Treatment", "ICU", 25, graph_instance=hospital_graph)
    patient_table.insert(1015, "Olivia Ray", 18, "Wards", 4, "Under Treatment", "Emergency", 35, graph_instance=hospital_graph)
    patient_table.insert(1016, "Peter Hall", 52, "Radiology", 2, "Under Treatment", "ICU", 40, graph_instance=hospital_graph)
    patient_table.insert(1017, "Quinn Lee", 28, "Emergency", 1, "Under Treatment", "Wards", 60, graph_instance=hospital_graph)
    patient_table.insert(1018, "Unreachable Pat", 30, "Outpatient Units", 1, "Under Treatment", "ICU", 10, graph_instance=hospital_graph)

    print("\n--- Hash Table Contents After All Inserts (for verification) ---")
    patient_table.print_table_state()

    # 3. Heap-Based Scheduling
    print("\n--- Initializing Emergency Scheduler (DSAHeap) ---")
    emergency_scheduler = DSAHeap(size=5) # Start with a small heap size to demonstrate resizing

    print("\n--- Demonstrating Inserts into the Heap ---")
    # Export all active patient records from the hash table to a queue
    patients_to_schedule_queue = patient_table.export()

    # Process patients one by one from the queue directly
    num_inserts = 0

    while not patients_to_schedule_queue.isEmpty():
        current_patient_record = patients_to_schedule_queue.dequeue() # Dequeue directly
        priority = calculate_priority(current_patient_record, hospital_graph)

        if priority is not None: # Only schedule if a valid priority was calculated
            emergency_scheduler.insert(priority, current_patient_record.patient_id)
            num_inserts += 1
    print(f"\n--- Total patients successfully inserted into heap: {num_inserts} ---")
    emergency_scheduler._print_heap_state("Final Heap after all inserts")


    print("\n--- Demonstrating Extractions from the Heap (5 extractions) ---")
    num_extractions = 0
    # Create a DSALinkedList to store extracted patient IDs in order for verification
    extracted_order = DSALinkedList()

    for _ in range(5): # Extract 5 highest priority patients
        try:
            extracted_entry = emergency_scheduler.extract_priority()
            extracted_patient_id = extracted_entry.get_value()
            extracted_order.insertLast(extracted_patient_id)

            # Retrieve full patient record to show it was served
            patient_record_full = patient_table.search(extracted_patient_id)
            print(f"  --> Served Patient: ID {patient_record_full.patient_id}, Name: {patient_record_full.name}, Urgency: {patient_record_full.urgency_level}")

            num_extractions += 1
        except IndexError:
            print("  Heap is empty, cannot extract more patients.")
        except Exception as e:
            print(f"  Error during extraction: {e}")

    print(f"\n--- Extractions Complete ({num_extractions} patients served) ---")
    print("  Order of patients served (by ID):")
    current_id_node = extracted_order.head
    while current_id_node:
        print(f"  - {current_id_node.getValue()}")
        current_id_node = current_id_node.getNext()

    emergency_scheduler._print_heap_state("Heap after extractions")

    print("\n--- Demonstrating Update of Patient Urgency ---")
    patient_id_to_update = 1010
    print(f"\n  Simulating urgency change for Patient ID {patient_id_to_update}.")
    updated_record_for_prio = emergency_scheduler.update_patient_urgency_and_new_priority(patient_id_to_update,1,patient_table=patient_table,hospital_graph=hospital_graph)
    emergency_scheduler._print_heap_state("Heap after urgency update for Patient 1010")

    print("\n--- Extracting another patient to see effect of update ---")
    print("Note: Patient 1010 should be extracted first, following the previous update of urgency level.")
    try:
        extracted_entry = emergency_scheduler.extract_priority()
        extracted_patient_id = extracted_entry.get_value()
        patient_record_full = patient_table.search(extracted_patient_id)
        print(f"  --> Served Patient: ID {patient_record_full.patient_id}, Name: {patient_record_full.name}, Urgency: {patient_record_full.urgency_level}")
    except IndexError:
        print("  Heap is empty, cannot extract.")

    emergency_scheduler._print_heap_state("Heap after final extraction")