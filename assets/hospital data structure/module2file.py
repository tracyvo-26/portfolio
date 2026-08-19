# -------------------------------------------------------------------------
# MODULE 2: Patient Management System - Hash Table
# -------------------------------------------------------------------------
# Purpose:
# This module implements a hash table to efficiently store, retrieve, update,
# and delete patient demographic and location details. It uses double hashing
# for collision resolution and supports dynamic resizing to maintain performance.
# It integrates with Module 1 to validate department existence.
# -------------------------------------------------------------------------

from stacksqueue import *
from linkedlist import *
from module1file import *

class PatientDetailsEntry:
    """
    Represents a single patient's detailed information.
    Includes flags for hash table state (NEVER_USED, USED, FORMERLY_USED)
    to support open addressing with deletion.
    """
    STATE_NEVER_USED = 0        # Slot has never held data. Probing stops here.
    STATE_USED = 1              # Slot currently holds an active patient record.
    STATE_FORMERLY_USED = -1    # Slot previously held data but it was deleted. Probing continues past this.

    def __init__(self, PatientID=None, Name=None, Age=None, Department=None, UrgencyLevel=None, TreatmentStatus=None,
                 DestinationDepartment=None, MockProcedureTime=None, ExpectedTreatmentTime=None):
        """
        Initializes a PatientDetailsEntry object with patient data.
        If PatientID is None, it's considered an empty/placeholder entry.
        Definition of the entries:
            PatientID (int, optional): Unique identifier for the patient. Defaults to None.
            Name (str, optional): Patient's full name. Defaults to None.
            Age (int, optional): Patient's age. Defaults to None.
            Department (str, optional): Current department the patient is in. Defaults to None.
            UrgencyLevel (int, optional): Urgency of patient's condition (1-5). Defaults to None.
            TreatmentStatus (str, optional): Current treatment status ("Under Treatment", "Completed"). Defaults to None.
            DestinationDepartment (str, optional): Department patient is scheduled to move to. Defaults to None.
            MockProcedureTime (int/float, optional): Estimated time for a procedure (in minute). Defaults to None.
            ExpectedTreatmentTime (int/float, optional): Total expected treatment duration. Defaults to None.
        """
        self.patient_id = PatientID
        self.name = Name
        self.age = Age
        self.department = Department
        self.urgency_level = UrgencyLevel
        self.treatment_status = TreatmentStatus
        self.destination_department = DestinationDepartment
        self.mock_procedure_time = MockProcedureTime
        self.expected_treatment_time = ExpectedTreatmentTime

        # Set the initial state based on whether a PatientID was provided.
        # If PatientID is provided, it's an active record (STATE_USED).
        # Otherwise, it's an empty placeholder (STATE_NEVER_USED).
        if PatientID is not None:
            self.state = PatientDetailsEntry.STATE_USED
        else: 
            self.state = PatientDetailsEntry.STATE_NEVER_USED

    def is_valid_patient_data(self, graph_instance=None, stage="module2"):
        """
        Validates the patient data fields according to predefined rules.
        Includes optional validation against a `HospitalNavigationGraph` instance
        to check if department names actually exist in the hospital layout.
        The `stage` parameter allows for different validation strictness,
        e.g., "module3" might require `destination_department` and `mock_procedure_time`.
        """
        # --- VALIDATION FOR PATIENT ID: PatientID must be an integer and positive. ---
        if not isinstance(self.patient_id, int) or self.patient_id <= 0:
            return False, "PatientID must be a positive integer."
        # --- VALIDATION FOR PATIENT NAME: Name must be a string and not empty after stripping whitespace. ---
        if not isinstance(self.name, str) or not self.name.strip():
            return False, "Name cannot be empty."
        # --- VALIDATION FOR PATIENT AGE: Age must be an integer within a reasonable range (0-120). ---
        if not isinstance(self.age, int) or not (0 <= self.age <= 120):
            return False, "Age must be an integer between 0 and 120."
        # --- VALIDATION FOR PATIENT CURRENTLY STAYING DEPARTMENT ---
        # Department must be a string and not empty.
        if not isinstance(self.department, str) or not self.department.strip():
            return False, "Department cannot be empty."
        # Check if the department exists in the hospital graph -> Integration of Module 1 and 2
        if graph_instance:
            if not self._department_exists_in_graph(self.department, graph_instance):
                return False, f"Department '{self.department}' does not exist in the hospital."
        # --- VALIDATION FOR PATIENT URGENCY LEVEL: UrgencyLevel must be an integer between 1 and 5. ---
        if not isinstance(self.urgency_level, int) or not (1 <= self.urgency_level <= 5):
            return False, "UrgencyLevel must be an integer between 1 and 5."
        # --- VALIDATION FOR PATIENT CURRENT TREATMENT STATUS: must be "Under Treatment" or "Completed". ---
        if not isinstance(self.treatment_status, str) or not self.treatment_status.strip():
            return False, "TreatmentStatus cannot be empty."
        if (self.treatment_status != "Under Treatment" and \
            self.treatment_status != "Completed"):
            return False, "Invalid TreatmentStatus. Must be 'Under Treatment' or 'Completed'."
        # --- VALIDATION FOR PATIENT DESTINATION DEPARTMENT AND MOCK PROCEDURE TIME ---
        # These fields are primarily relevant for patients *Under Treatment* and moving.
        # If treatment status is 'Completed', we can relax the requirements for these fields.
        if self.treatment_status == "Under Treatment" and (stage == "module3" or stage == "module4"):
            if not isinstance(self.destination_department, str) or not self.destination_department.strip():
                return False, "Destination Department cannot be empty."
            if graph_instance:
                if not self._department_exists_in_graph(self.destination_department, graph_instance):
                    return False, f"Destination Department '{self.destination_department}' does not exist in the hospital."
            
            # This is the key change: only enforce positive time if *Under Treatment*
            if not isinstance(self.mock_procedure_time, (int, float)) or not (self.mock_procedure_time > 0):
                return False, "MockProcedureTime must be positive."
        # If all checks pass, the patient record is valid.
        return True, None
    
    def _department_exists_in_graph(self, department_name, graph_instance):
        """
        Helper method to check if a given department name exists within the provided graph instance.
        Assumes `graph_instance` has a `get_all_department_names()` method that returns a DSALinkedList.
        """
        all_valid_names_list = graph_instance.get_all_department_names()
        current_name_node = all_valid_names_list.head
        while current_name_node:
            if current_name_node.getValue() == department_name:
                return True
            current_name_node = current_name_node.getNext()
        return False

class PatientDetailHashTable:
    UPPER_THRESHOLD = 0.7
    LOWER_THRESHOLD = 0.3
    MIN_SIZE = 20 # Minimum table size for at least 20 records. Next prime will be used.
    """
    Implements a hash table to store PatientDetailsEntry objects,
    using double hashing for collision resolution and dynamic resizing.
    """

    def __init__(self, tableSize=MIN_SIZE):
        """
        Initializes the hash table with a size that is the next prime number
        greater than or equal to `tableSize`.
        """
        self.size = self._next_prime(tableSize)
        self.count = 0 # Number of currently active (STATE_USED) elements
        self.actual_elements_in_array = 0 # Number of slots that are not STATE_NEVER_USED
        
        # Initialize hashArray with PatientDetailsEntry objects representing empty slots
        # This replaces numpy.empty and adheres to "no built-in lists in implementing... hashmap"
        self.hashArray = np.empty(self.size, dtype=object)
        for i in range(self.size):
            self.hashArray[i] = PatientDetailsEntry()

        print(f"Initialized hash table with size {self.size}.")

    def _next_prime(self, num):
        """
        Calculates the next prime number greater than or equal to `num`.
        """
        if num < 2: return 2
        if num % 2 == 0: num += 1
        while not self._is_prime(num):
            num += 2
        return num

    def _is_prime(self, num):
        """
        Checks if a given number is a prime number.
        """
        if num <= 1:
            return False
        if num <= 3:
            return True
        if num % 2 == 0 or num % 3 == 0:
            return False
        i = 5
        while i * i <= num:
            if num % i == 0 or num % (i + 2) == 0:
                return False
            i += 6
        return True

    def _hash(self, inKey):
        """
        Primary hash function for integer PatientIDs, using multiplication method.
        """
        if not isinstance(inKey, int):
            raise TypeError("Hash key (PatientID) must be an integer.")
        A_prime = 2654435761
        mixed_key = inKey * A_prime
        return mixed_key % self.size


    def _stepHash(self, inkey):
        """
        Secondary hash function for double hashing, used to determine the step size
        when a collision occurs. This ensures a different probe sequence for different keys.
        """
        hashStep = 0
        if isinstance(inkey, int):
            hashStep = 7 - (inkey % 7)  
        else:
            for i in range(len(inkey)):
                hashStep += ord(inkey[i])
            hashStep = 7 - (hashStep % 7)

        if hashStep != 0:
            return hashStep
        else:
            return 1

    def _find_slot(self, inKey):
        """
        Finds the appropriate slot for a given key using double hashing for collision resolution.
        It searches for either the key itself or an available slot for insertion.
        """
        # Step 1: Calculate the initial hash (h1) and the step hash (h2).
        h1 = self._hash(inKey)
        h2 = self._stepHash(inKey)
        current_index = h1
        i = 0
        first_formerly_used = -1
        probe_sequence = DSALinkedList() # For logging collision scenario
        # Step 2: Begin probing loop. Continue until all slots are checked or an empty slot is found.
        while i < self.size:
            probe_sequence.insertLast(current_index)
            entry = self.hashArray[current_index]
            # Case 1: Slot is `STATE_NEVER_USED`.
            # This means the key is not in the table, and this is a suitable spot for insertion.
            if entry.state == PatientDetailsEntry.STATE_NEVER_USED:
                return current_index, False, first_formerly_used, probe_sequence
            # Case 2: Slot is `STATE_USED`.
            # Check if this active entry holds the target key.
            elif entry.state == PatientDetailsEntry.STATE_USED:
                if entry.patient_id == inKey:
                    # Key found
                    return current_index, True, first_formerly_used, probe_sequence
            # Case 3: Slot is `STATE_FORMERLY_USED`.
            # This slot is available for insertion but does not stop probing for an existing key.
            # Store its index if it's the first one encountered (prioritized for insertion).
            elif entry.state == PatientDetailsEntry.STATE_FORMERLY_USED:
                if first_formerly_used == -1:
                    first_formerly_used = current_index
            # Move to the next slot in the probe sequence using double hashing.
            i += 1
            current_index = (h1 + i * h2) % self.size
        
        # Step 3: If the loop finishes, it means the table is full, or severely clustered,
        # and the key was not found. Return -1 to indicate no suitable slot was found.
        return -1, False, first_formerly_used, probe_sequence


    def search(self, patient_id):
        """
        Retrieves a `PatientDetailsEntry` object (patient record) by `PatientID`        
        """
        slot_idx, found_key, _, probe_sequence = self._find_slot(patient_id)
        print(f"\n  Search for ID {patient_id}. Probe sequence: {probe_sequence.to_string()}")
        if found_key:
            return self.hashArray[slot_idx]
        else:
            raise Exception(f"Patient with ID {patient_id} not found.")

    def insert(self, patient_id, name, age, department, urgency_level, treatment_status,
               destination_department=None, mock_procedure_time=None, expected_treatment_time = None,
               graph_instance=None, is_resizing=False):
        """
        Inserts a new patient record into the hash table. If a patient with the same ID
        already exists, it indicates a duplicate.
        It performs data validation and triggers resizing if the load factor is too high.
        """
        # Step 1: Create a temporary `PatientDetailsEntry` to validate the incoming data.
        temp_entry = PatientDetailsEntry(
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

        # Step 2: Determine validation stage based on presence of journey details.
        # This ensures that if destination/mock_procedure_time are provided, they are validated,
        # otherwise, only core fields are validated if `stage` isn't explicitly set to require them.
        validation_stage = "module2"
        if temp_entry.treatment_status == "Under Treatment" and \
           (temp_entry.destination_department is not None and temp_entry.mock_procedure_time is not None):
            validation_stage = "module3" # Use a stricter validation for module3/4 if transfer details are provided.
        # Step 3: Validate the patient data using the `is_valid_patient_data` method.
        is_valid, error_msg = temp_entry.is_valid_patient_data(graph_instance=graph_instance, stage=validation_stage)
        if not is_valid:
            raise ValueError(f"Invalid patient data for ID {patient_id}: {error_msg}")

        # Step 4: Check if resizing is needed *before* attempting insertion, unless already resizing.
        # This prevents the load factor from becoming too high, which degrades performance.
        if not is_resizing and self.getLoadFactor() > PatientDetailHashTable.UPPER_THRESHOLD:
            print(f"  Load factor ({self.getLoadFactor():.2f}) > {PatientDetailHashTable.UPPER_THRESHOLD}. Resizing...")
            self.resize(self.size * 2)
            print(f"  New table size after resize: {self.size}")
        
        # Step 5: Find the appropriate slot for the patient_id (after potential resize).
        slot_idx, found_key, formerly_used_idx, probe_sequence = self._find_slot(patient_id)
        print(f"  Insert for ID {patient_id}. Probe sequence: {probe_sequence.to_string()}")
        
        # Case 1: If no suitable slot could be found, even after potential resize.
        if slot_idx == -1:
             raise Exception("Hash table full or severely clustered, cannot insert.")
        
        # Case 2: If the key (patient_id) was already found.
        if found_key:
            print(f"  Patient {patient_id} already exists. No new record inserted.")
            return (f"Patient {patient_id} already exists.")
        # Case 3: Key not found, proceed with insertion.
        else:
            target_idx = -1
            # Prioritize inserting into a `STATE_FORMERLY_USED` slot if one was found.
            if formerly_used_idx != -1:
                target_idx = formerly_used_idx
            # Otherwise, use the `STATE_NEVER_USED` slot found by `_find_slot`.
            elif self.hashArray[slot_idx].state == PatientDetailsEntry.STATE_NEVER_USED:
                target_idx = slot_idx 
            # If a valid target index for insertion was determined.
            if target_idx != -1:
                # Place the new patient data into the `PatientDetailsEntry` at `target_idx`.
                entry = self.hashArray[target_idx]
                entry.patient_id = patient_id
                entry.name = name
                entry.age = age
                entry.department = department
                entry.urgency_level = urgency_level
                entry.treatment_status = treatment_status
                entry.destination_department = destination_department 
                entry.mock_procedure_time = mock_procedure_time       
                entry.state = PatientDetailsEntry.STATE_USED
                self.count += 1
                print(f"  Patient ID {patient_id} inserted successfully at index {target_idx}.")
                return "Record inserted successfully."
            else:
                raise Exception("Could not find a suitable slot for insertion (even after resize). Table might be full or severely clustered.")
            
    def update(self, patient_id, name, age, department, urgency_level, treatment_status, graph_instance=None):
        """
        Updates the details of an existing patient record identified by `patient_id`.
        Performs data validation before applying updates.
        """
        # Step 1: Create a temporary `PatientDetailsEntry` for validation purposes.
        temp_entry = PatientDetailsEntry(patient_id, name, age, department, urgency_level, treatment_status)
        # Step 2: Validate the updated data.
        is_valid, error_msg = temp_entry.is_valid_patient_data(graph_instance=graph_instance)
        if not is_valid:
            raise ValueError(f"Invalid patient data for ID {patient_id}: {error_msg}")
        # Step 3: Find the slot where the patient record is located.
        slot_idx, found_key, formerly_used_idx, probe_sequence = self._find_slot(patient_id)
        print(f"  Update for ID {patient_id}. Probe sequence: {probe_sequence}")
        if found_key:
            # Key already exists, update the existing entry's attributes
            existing_entry = self.hashArray[slot_idx]
            existing_entry.name = name
            existing_entry.age = age
            existing_entry.department = department
            existing_entry.urgency_level = urgency_level
            existing_entry.treatment_status = treatment_status
            print(f"  Patient ID {patient_id} record updated successfully at index {slot_idx}.")
            return "Record updated successfully."

    def remove(self, patient_id):
        """
        Removes a patient record identified by `patient_id` from the hash table.
        It doesn't physically delete the entry but marks its slot as `STATE_FORMERLY_USED`
        and clears sensitive data, allowing for future insertions to reuse the slot.
        Triggers a resize-down if the load factor falls below the lower threshold.
        """
        # Step 1: Validate input type.
        if not isinstance(patient_id, int):
            raise TypeError("Key for removal (PatientID) must be an integer.")
        
        # Step 2: Find the slot where the patient record is located.
        slot_idx, found_key, _, probe_sequence = self._find_slot(patient_id)
        print(f"  Remove for ID {patient_id}. Probe sequence: {probe_sequence}")

        if found_key:
            entry_to_remove = self.hashArray[slot_idx]
            entry_to_remove.state = PatientDetailsEntry.STATE_FORMERLY_USED
            # Clear other data to save memory, but keep patient_id (or mark as None) for future insertions
            entry_to_remove.name = None
            entry_to_remove.age = None
            entry_to_remove.department = None
            entry_to_remove.urgency_level = None
            entry_to_remove.treatment_status = None
            self.count -= 1
            print(f"  Patient ID {patient_id} removed (marked FORMERLY_USED) at index {slot_idx}.")

            # Check for resize down AFTER removal if load factor is low
            # Resize to half its current size, but not smaller than MIN_SIZE
            if self.getLoadFactor() < PatientDetailHashTable.LOWER_THRESHOLD and self.size > PatientDetailHashTable.MIN_SIZE:
                print(f"  Load factor ({self.getLoadFactor():.2f}) < {PatientDetailHashTable.LOWER_THRESHOLD}. Resizing down...")
                self.resize(max(self.size // 2, PatientDetailHashTable.MIN_SIZE)) # Resize down
            return "Record deleted successfully."
        else:
            raise Exception(f"Patient with ID {patient_id} not found for removal.")

    def getLoadFactor(self):
        """
        Calculates the current load factor of the hash table.
        """
        return self.count / self.size if self.size > 0 else 0

    def export(self):
        """
        Exports all active (`STATE_USED`) `PatientDetailsEntry` objects from the hash table into a DSAQueue.
        This is useful for iterating over all current patient records or for resizing operations.
        """
        item_queue = DSAQueue()
        for i in range(self.size):
            entry = self.hashArray[i]
            if entry.state == PatientDetailsEntry.STATE_USED:
                item_queue.enqueue(entry) # Enqueue the entire PatientDetailsEntry object
        return item_queue

    def resize(self, newSize):
        """
        Resizes the hash table to a new prime size
        """
        # Step 1: Calculate the new prime size for the table.
        new_prime_size = self._next_prime(newSize)
        print(f"  Resizing from {self.size} to new capacity {new_prime_size}...")
        # Step 2: Export all currently active entries into a queue.
        old_entries_queue = self.export() # Get all currently used entries
        # Step 3: Update the hash table's size to the new prime size.
        self.size = new_prime_size
        # Step 4: Re-initialize the hash array for the new size with empty `PatientDetailsEntry` objects.
        self.hashArray = np.empty(new_prime_size, dtype=object)
        for i in range(self.size):
            self.hashArray[i] = PatientDetailsEntry()
        # Step 5: Reset `count` (active elements) as they will be re-incremented during re-insertion.
        self.count = 0 
        self.actual_elements_in_array = 0
        # Step 6: Re-insert all previously active patient records into the newly sized table.
        # Pass `is_resizing=True` to prevent recursive resize calls during this process.
        while not old_entries_queue.isEmpty():
           old_entry = old_entries_queue.dequeue()
           # Re-insert, preserving all original data.
           self.insert(old_entry.patient_id, old_entry.name, old_entry.age,
                       old_entry.department, old_entry.urgency_level,
                       old_entry.treatment_status, old_entry.destination_department,
                       old_entry.mock_procedure_time, is_resizing=True)
        print("  Resize complete.")

    def print_table_state(self):
        """
        Prints the current internal state of the hash table.
        This method is very useful for debugging and understanding hash table behavior.
        """        
        print("\n--- Current Hash Table State ---")
        print(f"Table Size: {self.size}, Active Count: {self.count}, Load Factor: {self.getLoadFactor():.2f}")
        for i in range(self.size):
            entry = self.hashArray[i]
            state_str = ""
            # Determine the string representation of the slot's state.
            if entry.state == PatientDetailsEntry.STATE_NEVER_USED:
                state_str = "NEVER_USED"
            elif entry.state == PatientDetailsEntry.STATE_USED:
                state_str = "USED"
            elif entry.state == PatientDetailsEntry.STATE_FORMERLY_USED:
                state_str = "FORMERLY_USED"
            # Format patient ID and name for display, handling None values.
            display_id = entry.patient_id if entry.patient_id is not None else 'None'
            display_name = entry.name if entry.name is not None else 'None'
            # Print the details of the current slot.
            print(f"[{i:2}] State: {state_str:<15} ID: {str(display_id):<10} Name: {str(display_name):<15}")
        print("-------------------------------")

# --- Test Driver for Module 2 ---
def run_module2_tests():
    print("\n" + "="*50)
    print("             MODULE 2 TEST CASES           ")
    print("="*50)

    # 1. Setup Hospital Graph for Department Validation
    print("\n--- Setting up Hospital Graph for Department Validation ---")
    hospital_graph = HospitalNavigationGraph()
    hospital_graph.add_department("Emergency")
    hospital_graph.add_department("ICU")
    hospital_graph.add_department("Pharmacy")
    hospital_graph.add_department("Radiology")
    hospital_graph.add_department("Wards")
    hospital_graph.print_all_department_names() # Use the print method from Module 1

    # 2. Test PatientDetailsEntry Validation 
    print("\n--- Testing PatientDetailsEntry Validation ---")
    # Valid patient
    patient_valid = PatientDetailsEntry(101, "Alice", 30, "Emergency", 3, "Under Treatment", "ICU", 60)
    is_valid, msg = patient_valid.is_valid_patient_data(hospital_graph, stage="module3")
    print(f"Patient 101 valid: {is_valid}, Message: {msg}") # Expected: True

    # Invalid Patient ID
    patient_invalid_id = PatientDetailsEntry(-1, "Bob", 25, "ICU", 2, "Under Treatment")
    is_valid, msg = patient_invalid_id.is_valid_patient_data(hospital_graph)
    print(f"Patient -1 valid: {is_valid}, Message: {msg}") # Expected: False, PatientID must be positive

    # Invalid Department (without graph_instance it would pass previously)
    patient_invalid_dept = PatientDetailsEntry(102, "Charlie", 45, "NonExistentDept", 4, "Completed")
    is_valid, msg = patient_invalid_dept.is_valid_patient_data(hospital_graph)
    print(f"Patient 102 valid (bad dept): {is_valid}, Message: {msg}") # Expected: False, NonExistentDept

    # Invalid Destination Department (for stage 3)
    patient_invalid_dest_dept = PatientDetailsEntry(103, "David", 55, "Wards", 5, "Under Treatment", "AnotherBadDept", 90)
    is_valid, msg = patient_invalid_dest_dept.is_valid_patient_data(hospital_graph, stage="module3")
    print(f"Patient 103 valid (bad dest dept): {is_valid}, Message: {msg}") # Expected: False, AnotherBadDept

    # Invalid Age
    patient_invalid_age = PatientDetailsEntry(104, "Eve", 150, "Pharmacy", 1, "Under Treatment")
    is_valid, msg = patient_invalid_age.is_valid_patient_data(hospital_graph)
    print(f"Patient 104 valid (bad age): {is_valid}, Message: {msg}") # Expected: False, Age must be between 0 and 120

    # Invalid Urgency Level
    patient_invalid_urgency = PatientDetailsEntry(105, "Frank", 22, "Radiology", 0, "Under Treatment")
    is_valid, msg = patient_invalid_urgency.is_valid_patient_data(hospital_graph)
    print(f"Patient 105 valid (bad urgency): {is_valid}, Message: {msg}") # Expected: False, UrgencyLevel must be between 1 and 5

    # Invalid Treatment Status
    patient_invalid_status = PatientDetailsEntry(106, "Grace", 60, "Wards", 3, "In Progress")
    is_valid, msg = patient_invalid_status.is_valid_patient_data(hospital_graph)
    print(f"Patient 106 valid (bad status): {is_valid}, Message: {msg}") # Expected: False, Invalid TreatmentStatus


    # 3. Test PatientDetailHashTable Functionality
    print("\n--- Testing PatientDetailHashTable Operations ---")
    hash_table = PatientDetailHashTable(tableSize=5) # Start with a small size to force resizes quickly

    # Insert records
    print("\n--- Inserting Patients ---")
    try:
        hash_table.insert(10, "Something Ten", 25, "Emergency", 3, "Under Treatment", graph_instance=hospital_graph)
        hash_table.insert(21, "Twenty One", 40, "ICU", 4, "Under Treatment", graph_instance=hospital_graph) 
        hash_table.insert(32, "Thirty Two", 60, "Pharmacy", 5, "Completed", graph_instance=hospital_graph)
        hash_table.insert(43, "Forty Three", 35, "Radiology", 2, "Under Treatment", graph_instance=hospital_graph)
        hash_table.insert(54, "Victor Four", 50, "Wards", 1, "Under Treatment", graph_instance=hospital_graph)
        hash_table.insert(15, "Wendy Five", 28, "Emergency", 3, "Under Treatment", graph_instance=hospital_graph)
        hash_table.insert(26, "Xavier Six", 70, "ICU", 4, "Completed", graph_instance=hospital_graph)
        hash_table.insert(37, "Yara Seven", 18, "Pharmacy", 2, "Under Treatment", graph_instance=hospital_graph)
        hash_table.insert(48, "Zoe Eight", 42, "Radiology", 3, "Under Treatment", graph_instance=hospital_graph)
        hash_table.insert(59, "Alice Nine", 33, "Wards", 5, "Under Treatment", graph_instance=hospital_graph)
        hash_table.insert(11, "Pat Eleven", 25, "Emergency", 3, "Under Treatment", graph_instance=hospital_graph)
        hash_table.insert(22, "Sam Two", 40, "Emergency", 4, "Under Treatment", graph_instance=hospital_graph) 
        hash_table.insert(35, "Tina Five", 60, "Radiology", 5, "Completed", graph_instance=hospital_graph)
        hash_table.insert(41, "Uma One", 35, "ICU", 2, "Under Treatment", graph_instance=hospital_graph)
        hash_table.insert(49, "Victoria Nine", 50, "Wards", 1, "Under Treatment", graph_instance=hospital_graph)
        hash_table.insert(13, "Zack Three", 28, "Radiology", 3, "Under Treatment", graph_instance=hospital_graph)
        hash_table.insert(29, "Jane Nine", 70, "ICU", 4, "Completed", graph_instance=hospital_graph)
        hash_table.insert(31, "Tina One", 18, "Pharmacy", 2, "Under Treatment", graph_instance=hospital_graph)
        hash_table.insert(44, "Fanny Four", 42, "Wards", 3, "Completed", graph_instance=hospital_graph)
        hash_table.insert(58, "Fang Eight", 33, "Radiology", 5, "Under Treatment", graph_instance=hospital_graph)

        # Attempt to insert patient with invalid department
        print("\nAttempting to insert patient with invalid department:")
        hash_table.insert(999, "Bad Dept Patient", 30, "NonExistentDept", 3, "Under Treatment", graph_instance=hospital_graph)
    except ValueError as e:
        print(f"Caught expected error: {e}")
    except Exception as e:
        print(f"Caught unexpected error: {e}")

    hash_table.print_table_state()

    # Test search
    print("\n--- Searching for Patients ---")
    try:
        patient = hash_table.search(32)
        print(f"Found patient ID 32: {patient.name}, Department: {patient.department}, Status: {patient.treatment_status}")
        patient = hash_table.search(10)
        print(f"Found patient ID 10: {patient.name}, Department: {patient.department}, Status: {patient.treatment_status}")
        # Search for non-existent patient
        patient = hash_table.search(99)
        print(f"Found patient ID 99: {patient.name}") # Should raise exception
    except Exception as e:
        print(f"Caught expected error: {e}")

    # Test update
    print("\n--- Updating Patients ---")
    try:
        hash_table.update(21, "Sam Updated", 41, "Emergency", 3, "Completed", graph_instance=hospital_graph)
        patient = hash_table.search(21)
        print(f"Updated patient ID 21: {patient.name}, Age: {patient.age}, Department: {patient.department}, Status: {patient.treatment_status}")
        
        # Attempt to update with invalid data (e.g., bad department)
        print("\nAttempting to update patient with invalid department:")
        hash_table.update(10, "Pat Ten", 25, "BadDepartment", 3, "Under Treatment", graph_instance=hospital_graph)
    except ValueError as e:
        print(f"Caught expected error: {e}")
    except Exception as e:
        print(f"Caught unexpected error: {e}")

    hash_table.print_table_state()

    # Test remove
    print("\n--- Removing Patients ---")
    try:
        hash_table.remove(43)
        print("Removed patient ID 43.")
        hash_table.remove(15)
        print("Removed patient ID 15.")
        hash_table.remove(21) 
        print("Removed patient ID 21.")
        
        # Attempt to remove non-existent patient
        hash_table.remove(99)
    except Exception as e:
        print(f"Caught expected error: {e}")

    try:
        hash_table.search(43)
    except Exception as e:
        print(f"Verified: {e}")

    try:
        hash_table.search(15)
    except Exception as e:
        print(f"Verified: {e}")

    try:
        hash_table.search(21)
    except Exception as e:
        print(f"Verified: {e}")

    hash_table.print_table_state()

    # Test exporting to queue
    print("\n--- Exporting to Queue ---")
    exported_patients = hash_table.export()
    print(f"Exported {exported_patients.getCount()} patients to queue.")
    print("Patients in exported queue:")
    while not exported_patients.isEmpty():
        patient_entry = exported_patients.dequeue()
        print(f"- ID: {patient_entry.patient_id}, Name: {patient_entry.name}, Department: {patient_entry.department}")

    print("\n--- Testing Hash Table after Export (should still contain data) ---")
    hash_table.print_table_state()
    

    print("\n--- Module 2 Test Cases Complete ---")

if __name__ == '__main__':
    run_module2_tests()