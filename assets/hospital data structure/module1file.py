# -------------------------------------------------------------------------
# MODULE 1: Hospital Navigation Graph
# -------------------------------------------------------------------------
# Purpose:
# This module models the hospital’s departments and corridors as a graph.
# Each department is a node, and each corridor is an edge with a travel time.
# It supports adding/removing departments, BFS/DFS traversal, cycle detection,
# and A* shortest path calculation.
# -------------------------------------------------------------------------


from linkedlist import *
from stacksqueue import *
from sorts import *

# -------------------------------------------------------------------------
# Custom Data Structures for Graph Relationships since tuple is prohibited
# -------------------------------------------------------------------------
# These classes implement __gt__ for comparison by bubbleSort

class PathInfo:
    """
    Stores connection (edge) details between two departments
    Replaces (neighbor_department_node, travel_time) tuple
    """
    def __init__(self, neighbor_node, travel_time):
        self.neighbor_node = neighbor_node
        self.travel_time = travel_time

    def __gt__(self, other):
        if isinstance(other, PathInfo):
            return self.neighbor_node > other.neighbor_node
        return NotImplemented # Delegate to other type if not PathInfo

    def __eq__(self, other):
        if isinstance(other, PathInfo):
            return self.neighbor_node == other.neighbor_node and self.travel_time == other.travel_time
        return False

class LevelEntry:
    """
    Represents one BFS level — a group of departments reachable in N steps
    Replaces (level_number, DSALinkedList_of_department_names) tuple
    """
    def __init__(self, level_number, department_names_list):
        self.level_number = level_number
        self.department_names_list = department_names_list

    def __gt__(self, other):
        if isinstance(other, LevelEntry):
            return self.level_number > other.level_number
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, LevelEntry):
            return self.level_number == other.level_number
        return False

class PriorityQueueEntry:
    """Wraps a department node for A* pathfinding, sorted by f_score
    Replaces (f_score, department_node) tuple for A*
    """
    def __init__(self, f_score, department_node):
        self.f_score = f_score
        self.department_node = department_node

    def __gt__(self, other):
        # A* priority queue sorts by f_score
        if isinstance(other, PriorityQueueEntry):
            return self.f_score > other.f_score
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, PriorityQueueEntry):
            # Equality primarily for node identity in a priority queue context if scores are same
            return self.f_score == other.f_score and self.department_node == other.department_node
        return False

# -------------------------------------------------------------------------
# MAIN CLASS: HospitalNavigationGraph
# -------------------------------------------------------------------------

class HospitalNavigationGraph:
    """
    Represents the hospital’s layout as an undirected weighted graph.
    Nodes = Departments
    Edges = Paths between departments with travel time in minutes
    """
    # ---------------------------------------------------------------------
    # Inner Class: DepartmentNode
    # ---------------------------------------------------------------------
    class DepartmentNode:
        """
        Represents a single department (vertex) in the hospital graph.
        Stores its label (department name), an optional value (department information),
        and a list of adjacent departments (path list) with their corresponding travel times (edge weights).
        """
        def __init__(self, department_name, department_info=None):
            self.department_name = department_name
            self.department_info = department_info
            self.path_list = DSALinkedList() # linked list of connected departments of this department. Stores PathInfo objects.
            self.is_visited = False          # Flag for BFS/DFS traversal
            self.recursion_stack = False     # Flag for cycle detection in DFS (indicates node is in current recursion path)

            self.g_score = float('inf')   # A* cost from start to this node
            self.f_score = float('inf')   # A* estimated total cost from start to goal through this node
            self.path_predecessor = None  # A* parent node in the shortest path

        def add_path_to_neighbor(self, neighbor_department_node, travel_time):
            """
            Adds an outgoing path (edge) to a neighboring department with a specified travel time.
            Prevents duplicate edges to the same neighbor with the same weight.
            """
            current_path_entry = self.path_list.head
            while current_path_entry:
                path_info = current_path_entry.getValue() # PathInfo object
                adj_neighbor_dep = path_info.neighbor_node
                existing_travel_time = path_info.travel_time
                # Case 1: Connection between apartments already existed
                # In this case, do nothing and return.
                if adj_neighbor_dep == neighbor_department_node and existing_travel_time==travel_time:
                    return
                # Case 2: No connect yet, create new connection to department
                current_path_entry = current_path_entry.getNext()
            self.path_list.insertLast(PathInfo(neighbor_department_node, travel_time))

        def remove_path_to_neighbor(self, target_neighbor_node):
            """
            Remove any adjacency entries to `target_neighbor_node`.
            Rebuilds a temp DSALinkedList excluding the removed neighbor to avoid in-place deletion using lists.
            """
            temp_path_list = DSALinkedList()
            current_path_entry = self.path_list.head
            found_and_removed = False   # Flag to track if the target neighbor was found and excluded
            while current_path_entry:
                path_info = current_path_entry.getValue() # PathInfo object
                adjacent_dep_node = path_info.neighbor_node
                travel_time = path_info.travel_time

                # Case 1: The current path leads to a different neighbor. Keep this path.
                if adjacent_dep_node != target_neighbor_node:
                    temp_path_list.insertLast(PathInfo(adjacent_dep_node, travel_time))
                
                # Case 2: The current path leads to the target neighbor. Do not add it to temp_path_list, effectively removing it.
                else:
                    found_and_removed = True
                current_path_entry = current_path_entry.getNext()
            # If the target neighbor was found and removed, replace the old path_list with the new one.
            if found_and_removed:
                self.path_list = temp_path_list

        def get_all_adjacent_paths(self):
            """
            Return a shallow copy of this node's adjacency DSALinkedList (PathInfo objects)
            so callers can iterate or sort independently.
            """
            adjacent_connections = DSALinkedList()
            current_path_entry = self.path_list.head
            while current_path_entry:
                adjacent_connections.insertLast(current_path_entry.getValue()) # Stores PathInfo objects
                current_path_entry = current_path_entry.getNext()
            return adjacent_connections
        
        #Comparison operators for sorting departments alphabetically
        def __gt__(self, other):
            # Compare by department_name if other is DepartmentNode or str
            if isinstance(other, HospitalNavigationGraph.DepartmentNode):
                return self.department_name > other.department_name
            if isinstance(other, str):
                return self.department_name > other
            return NotImplemented 

        def __eq__(self, other):
            if isinstance(other, HospitalNavigationGraph.DepartmentNode):
                return self.department_name == other.department_name
            return False
        
    # ---------------------------------------------------------------------
    # Graph constructor and Core Utility Methods
    # ---------------------------------------------------------------------
    def __init__(self):
        """Initializes an empty hospital graph."""
        self.hospital_departments = DSALinkedList()  # list of DSAGraphNode

    def _reset_algorithm_states(self):
        """Resets all traversal-related flags before running BFS/DFS/A*."""
        current_department_entry = self.hospital_departments.head
        while current_department_entry:
            department = current_department_entry.getValue()
            department.is_visited = False
            department.recursion_stack = False # Reset recursion stack flag
            department.g_score = float('inf')
            department.f_score = float('inf')
            department.path_predecessor = None
            current_department_entry = current_department_entry.getNext()

    def find_department(self, department_name):
        """
        Linear search through hospital_departments to locate a DepartmentNode by name.
        Returns the DepartmentNode or None if not found.
        """
        current_department_entry = self.hospital_departments.head
        while current_department_entry:
            department = current_department_entry.getValue()
            if department.department_name == department_name:
                return department
            current_department_entry = current_department_entry.getNext()
        return None

    def remove_department(self,department_name):
        """
        Remove a department node and all adjacency references to it.
        """
        # Step 1: Locate the department node to be deleted.
        delete_dep = self.find_department(department_name)
        # Case 1: The department to remove does not exist. Raise an error.
        if delete_dep is None:
            raise ValueError(f"Department '{department_name}' not found")
        # Step 2: Iterate through all other departments in the hospital graph.
        # For each department, remove any paths (edges) that lead to the department being deleted.
        current_department = self.hospital_departments.head
        while current_department:
            department = current_department.getValue()
            # If the current department is NOT the one we are deleting,
            # then check its adjacency list and remove any path to `delete_dep`.
            if department != delete_dep:
                department.remove_path_to_neighbor(delete_dep)
            current_department = current_department.getNext()
        # Step 3: Remove the `delete_dep` node itself from the graph's main list of departments.
        self.hospital_departments.removeNode(delete_dep)
        print(f"Department '{department_name}' and all its corridors removed.")

    def add_department(self,department_name):
        """
        Add a department node if it doesn't already exist.
        """
        # Case 1: Department does not exist. Create a new DepartmentNode and add it to the graph.
        if not self.find_department(department_name):
            new_department = self.DepartmentNode(department_name)
            self.hospital_departments.insertLast(new_department)
            print(f"Department '{department_name}' added.")
        # Case 2: Department already exists. Print a message indicating this.
        else:
            print(f"Department '{department_name}' already exists.")

    def add_path(self, department_name1, department_name2, travel_time):
        """
        Add a undirected path between two department names with weight travel_time.
        """
        # Step 1: Find the DepartmentNode objects for both department names.
        dep1 = self.find_department(department_name1)
        dep2 = self.find_department(department_name2)
        # Case 1: One or both departments do not exist. Raise an error.
        if dep1 is None or dep2 is None:
            raise ValueError("Source or destination department not found.")
        # Case 2: Both departments exist
        # Step 2: checking data type of travel_time.
        if not isinstance(travel_time, int):
            travel_time = int(travel_time)
        # Step 3: Add the path from department 1 to department 2 and vice versa, to ensure undirected graph.
        dep1.add_path_to_neighbor(dep2, travel_time)
        dep2.add_path_to_neighbor(dep1, travel_time)
        print(f"Path added between '{department_name1}' and '{department_name2}', travel time: {travel_time} minutes.")

    def remove_path(self, department_name1, department_name2):
        """
        Remove undirected adjacency between two departments (if present).
        """
        # Step 1: Find the DepartmentNode objects for both department names.
        dep1 = self.find_department(department_name1)
        dep2 = self.find_department(department_name2)
        # Case 1: One or both departments do not exist. Raise an error.
        if dep1 is None or dep2 is None:
            raise ValueError("One or both departments not found")
        # Case 2: Both departments exist
        # Step 2: Remove the path from department 1's adjacency list to department 2 and vice versa.
        dep1.remove_path_to_neighbor(dep2) # Remove node2 from node1's adjacency list
        dep2.remove_path_to_neighbor(dep1) # Remove node1 from node2's adjacency list
        print(f"Path between {department_name1} and {department_name2} is removed.")

    def has_department(self, department_name):
        department = self.find_department(department_name)
        # Case 1: Department was found.
        if department:
            print(f"Department '{department_name}' exists in the hospital.")
            return True
        # Case 2: Department was not found.
        else:
            print(f"Department '{department_name}' does not exist in the hospital.")
            return False

    def get_department_count(self):
        """
        Counts total adjacency entries then divides by two (because undirected edges stored twice).
        """
        count = self.hospital_departments.getCount()
        print(f"There are {count} departments in the hospital.")
        return count
    
    def get_all_department_names(self):
        """
        Returns a DSALinkedList containing the names (strings) of all
        departments currently in the hospital graph.
        Returns an empty DSALinkedList if no departments exist.
        """
        department_names_list = DSALinkedList()
        current_department_entry = self.hospital_departments.head
        while current_department_entry:
            department = current_department_entry.getValue()
            department_names_list.insertLast(department.department_name)
            current_department_entry = current_department_entry.getNext()
        return department_names_list

    def print_all_department_names(self):
        """
        Prints the names of all departments currently in the hospital
        """
        # Step 1: Retrieve a linked list of all department names.
        names_list = self.get_all_department_names()

        # Case 1: If the list of names is empty, there are no departments and return.
        if names_list.isEmpty():
            print("No departments currently in the hospital.")
            return
        
        # Case 2: there are departments existing in the hospital.
        # Step 2: Get the total count of departments for the header message.
        department_count = self.get_department_count() # Call existing method for count
        print(f"The hospital includes {department_count} departments:")
        
        # Step 3: Iterate through the linked list of department names and print each one.
        current_name_node = names_list.head
        idx = 1
        while current_name_node:
            print(f"- {idx}. {current_name_node.getValue()}")
            current_name_node = current_name_node.getNext() # CORRECTED LINE HERE
            idx += 1

    def get_path_count(self):
        """
        Calculates and returns the total number of unique paths (undirected edges) in the graph.
        Since each undirected edge is stored twice (once for each direction), the total count
        of adjacency entries is divided by two.
        """
        count = 0
        current_department_entry = self.hospital_departments.head
        while current_department_entry:
            department = current_department_entry.getValue()
            count += department.path_list.getCount()
            current_department_entry = current_department_entry.getNext()
        print(f"There are {count//2} paths connected between hospital departments")
        return count // 2

    def are_departments_adjacent(self,department_name1,department_name2):
        """
        Return True if there's a direct corridor between two departments.
        """
        # Step 1: Find the DepartmentNode objects for both department names.
        dep1 = self.find_department(department_name1)
        dep2 = self.find_department(department_name2)
        # One or both departments do not exist. They cannot be adjacent.
        if dep1 is None or dep2 is None:
            return False  # one or both nodes don't exist

        # Step 2: Iterate through the `path_list` of `dep1` to check for `dep2` as a neighbor.
        current_path_entry = dep1.path_list.head
        while current_path_entry:
            path_info = current_path_entry.getValue() # PathInfo object
            neighbor_dep_node = path_info.neighbor_node
            # `dep2` is found in `dep1`'s adjacency list. They are adjacent.
            if neighbor_dep_node == dep2:
                return True
            current_path_entry = current_path_entry.getNext()
        return False

    def get_adjacent_department_names(self,department_name):
        """
        Return a DSALinkedList of neighbor department names for the given department.
        """
        # Step 1: Find the DepartmentNode object for the given department name.
        adjacent_names_list = DSALinkedList()
        department_node = self.find_department(department_name)
        # Case 1: The department does not exist. Raise an error.
        if department_node is None:
            raise ValueError(f"Department '{department_name}' not found")
        # Case 2: The department exists
        # Step 2: Iterate through the `path_list` of the found department node.
        current_path_entry = department_node.path_list.head
        while current_path_entry:
            path_info = current_path_entry.getValue() # PathInfo object
            neighbor_dep_node = path_info.neighbor_node
            # Step 3: Add the name of each neighbor department to the result list.
            adjacent_names_list.insertLast(neighbor_dep_node.department_name)  # store label
            current_path_entry = current_path_entry.getNext()
        return adjacent_names_list

    def display_path_list(self):
        """
        Prints the adjacency list for the entire graph in a user-friendly format.
        For each department, it lists all its direct neighbors along with the travel time to them.
        """
        print("\nHospital Paths (Adjacency List):")
        # Step 1: Start iterating through the main list of all hospital departments.
        current_dep_node_entry = self.hospital_departments.head
        while current_dep_node_entry:
            department = current_dep_node_entry.getValue()
            # Step 2: For each department, collect formatted strings for its adjacent paths.
            path_info_strings = DSALinkedList() # Stores strings like "Name (X min)"
            adjacent_paths = department.get_all_adjacent_paths()    # Get all PathInfo objects for neighbors
            current_adj_path_entry = adjacent_paths.head

            while current_adj_path_entry:
                path_info = current_adj_path_entry.getValue() # PathInfo object
                neighbor_dep_node = path_info.neighbor_node
                travel_time = path_info.travel_time
                formatted_string = f"{neighbor_dep_node.department_name} ({travel_time} min)"
                path_info_strings.insertLast(formatted_string)
                current_adj_path_entry = current_adj_path_entry.getNext()
            # Step 3: Concatenate the formatted path strings with commas.
            final_path_string = ""
            current_formatted_string_entry = path_info_strings.head
            first = True
            while current_formatted_string_entry:
                if not first:
                    final_path_string += ", " # Add comma and space separator
                final_path_string += current_formatted_string_entry.getValue()
                first = False
                current_formatted_string_entry = current_formatted_string_entry.getNext()
            # Step 4: Print the department name followed by its list of neighbors.
            print(f"{current_dep_node_entry.getValue().department_name} -> {final_path_string}")
            current_dep_node_entry = current_dep_node_entry.getNext()

    def find_reachable_departments_by_level(self, start_department_name):
        """
        Performs a Breadth-First Search (BFS) starting from the given department.
        It identifies and groups departments by their 'level' (the minimum number of hops/edges
        required to reach them from the start department).
        The results are printed, with departments at each level sorted alphabetically.
        """
        # Step 1: Reset all algorithm-specific flags (visited, recursion_stack, A* scores)
        # to ensure a clean state for the new BFS traversal.
        self._reset_algorithm_states()
        # Step 2: Locate the starting department node.
        start_node = self.find_department(start_department_name)
        # Case 1: If the start department is not found, raise an error.
        if start_node is None:
            raise ValueError(f"Start department '{start_department_name}' not found.")
        # Case 2: The start node is founded, continue.
        # Step 3: Initialize the BFS queue and mark the start node as visited.
        exploration_queue = DSAQueue()
        start_node.is_visited = True
        # Enqueue the starting node as a LevelEntry at level 0. The `department_names_list`
        # field of LevelEntry is temporarily used to store the DepartmentNode itself here.
        exploration_queue.enqueue(LevelEntry(0, start_node))

        # Step 4: Initialize a DSALinkedList to store the final grouped results.
        # This list will hold LevelEntry objects, each containing a level number
        # and a DSALinkedList of department names for that level.
        departments_by_level_storage = DSALinkedList()

        # Step 5: Begin the main BFS loop. Continue as long as there are departments to explore.
        while not exploration_queue.isEmpty():
            # Step 5.1: Dequeue the next LevelEntry. This entry holds the current department node
            # and its level from the start.
            current_level_entry = exploration_queue.dequeue() # This is a LevelEntry object
            current_level = current_level_entry.level_number
            current_department = current_level_entry.department_names_list

            # Step 5.2: Add the `current_department_node`'s name to the appropriate level group
            # in `departments_by_level_storage`. If the level group doesn't exist yet, create it.
            found_level_group = False
            temp_level_group_entry = departments_by_level_storage.head
            while temp_level_group_entry:
                existing_level_entry = temp_level_group_entry.getValue() # This is a LevelEntry object
                if existing_level_entry.level_number == current_level:
                    existing_level_entry.department_names_list.insertLast(current_department.department_name)
                    found_level_group = True
                temp_level_group_entry = temp_level_group_entry.getNext()

            if not found_level_group:
                new_dep_names_list = DSALinkedList()
                new_dep_names_list.insertLast(current_department.department_name)
                # Store a new LevelEntry object with the current department's name
                departments_by_level_storage.insertLast(LevelEntry(current_level, new_dep_names_list))

            # Step 5.3: Explore neighbors of the `current_department_node`.
            neighbors_dsa_list = current_department.get_all_adjacent_paths()

            # Step 5.4: Collect unvisited neighbors and sort them alphabetically by name.
            unvisited_sorted_neighbors = DSALinkedList()
            current_adj_path_entry = neighbors_dsa_list.head
            while current_adj_path_entry:
                path_info = current_adj_path_entry.getValue() # PathInfo object
                neighbor_dep_node = path_info.neighbor_node
                if not neighbor_dep_node.is_visited:
                    unvisited_sorted_neighbors.insertLast(neighbor_dep_node)
                current_adj_path_entry = current_adj_path_entry.getNext()

            # Step 5.5: Sort the collected unvisited neighbors by their department names.
            if unvisited_sorted_neighbors.getCount() > 1:
                bubbleSort(unvisited_sorted_neighbors) # Sorts DepartmentNode objects by name

            # Step 5.6: Enqueue the unvisited, sorted neighbors.
            current_neighbor_node_entry = unvisited_sorted_neighbors.head
            while current_neighbor_node_entry:
                neighbor_node = current_neighbor_node_entry.getValue()
                if not neighbor_node.is_visited:
                    neighbor_node.is_visited = True
                    exploration_queue.enqueue(LevelEntry(current_level + 1, neighbor_node)) # Enqueue LevelEntry
                current_neighbor_node_entry = current_neighbor_node_entry.getNext()

        # Step 6: After BFS completes, sort the `departments_by_level_storage` by `level_number`
        # to ensure output is in ascending order of levels.
        if departments_by_level_storage.getCount() > 1:
            bubbleSort(departments_by_level_storage) # Sorts LevelEntry objects by level_number

        # Step 7: Print the final grouped-by-level output.
        print(f"\nBFS from '{start_department_name}': Reachable departments by level:")
        current_level_entry_in_storage = departments_by_level_storage.head
        while current_level_entry_in_storage:
            level_entry_obj = current_level_entry_in_storage.getValue() # This is a LevelEntry object
            lvl_num = level_entry_obj.level_number
            dep_names_at_level = level_entry_obj.department_names_list

            # Step 7.1: Ensure alphabetical order of department names *within* each level.
            if dep_names_at_level.getCount() > 1:
                bubbleSort(dep_names_at_level)
            # Step 7.2: Format the department names at the current level into a comma-separated string.
            labels_str = ""
            current_name_in_list = dep_names_at_level.head
            first_label = True
            while current_name_in_list:
                if not first_label:
                    labels_str += ", "
                labels_str += current_name_in_list.getValue()
                first_label = False
                current_name_in_list = current_name_in_list.getNext()
            # Step 7.3: Print the level number and the formatted list of department names.
            print(f"Level {lvl_num}: {labels_str}")
            current_level_entry_in_storage = current_level_entry_in_storage.getNext()

    def _are_cycles_equal(self, cycle_a, cycle_b):
        """
        Compares two cycles (each represented as a DSALinkedList of department names)
        to determine if they are identical in sequence and length.
        Note: The cycle members are already sorted alphabetically before being stored,
        which simplifies equality checking to a direct sequence comparison.
        """
        # Case 1: number of elements in each cycle is different, cycles cannot be equal.
        if cycle_a.getCount() != cycle_b.getCount():
            return False
        # Case 2: number of elements in each cycle is the same, cycles might be equal.
        entry_a = cycle_a.head
        entry_b = cycle_b.head
        while entry_a and entry_b:
            # If any corresponding department names are different, cycles are not equal.
            if entry_a.getValue() != entry_b.getValue():
                return False
            # As corresponding department names are similar, loop continues.
            entry_a = entry_a.getNext()
            entry_b = entry_b.getNext()
        # If loop completes, all elements matched, so cycles are equal.
        return True

    def detect_cycles_dfs(self, start_department_name):
        """
        Perform DFS starting from start_department_name and detect unique cycles.
        Cycles are reconstructed from the current DFS path stack when a back-edge is found.
        """
        # Step 1: Reset all algorithm-specific flags (visited, recursion_stack, A* scores)
        # to ensure a clean state for the new DFS traversal.
        self._reset_algorithm_states()

        # Step 2: Locate the starting department node.
        start_node = self.find_department(start_department_name)
        # Case 1: If the start department is not found, raise an error.
        if start_node is None:
            raise ValueError(f"Start department '{start_department_name}' not found.")
        # Case 2: The start node is founded, continue.
        # Step 3: Initialize the stack to keep track of the current DFS path (recursion stack simulation)
        current_dfs_path = DSAStack()
        # Step 4: Initialize a DSALinkedList to store all unique cycles found.
        detected_cycles = DSALinkedList()
        # Step 5: Define the recursive helper function for DFS traversal and cycle detection.
        def _dfs_recursive_cycle_check(department_node, parent_node=None):
            # Step 5.1: Mark the current node as visited and add it to the recursion stack.
            department_node.is_visited = True
            department_node.recursion_stack = True  # Node is currently being processed in the DFS path
            current_dfs_path.push(department_node)
            # Step 5.2: Get all adjacent paths (neighbors) of the current department.
            neighbors_dsa_list = department_node.get_all_adjacent_paths() # Stores PathInfo objects
            # Step 5.3: Extract neighbor nodes and sort them alphabetically for consistent traversal.
            sorted_neighbors = DSALinkedList()
            current_path_entry = neighbors_dsa_list.head
            while current_path_entry:
                path_info = current_path_entry.getValue() # PathInfo object
                neighbor_dep_node = path_info.neighbor_node
                sorted_neighbors.insertLast(neighbor_dep_node)
                current_path_entry = current_path_entry.getNext()

            if sorted_neighbors.getCount() > 1:
                bubbleSort(sorted_neighbors) # Sorts DepartmentNode objects by their department_name
            # Step 5.4: Iterate through each sorted neighbor.
            current_neighbor_node_entry = sorted_neighbors.head
            while current_neighbor_node_entry:
                neighbor_node = current_neighbor_node_entry.getValue()
                # Only process the neighbor if it is NOT the parent node.
                if neighbor_node != parent_node:
                    # If the neighbor is in the current recursion stack (recursion_stack is True),
                    # a back-edge is detected, which means a cycle is found.
                    if neighbor_node.recursion_stack:
                        # Back-edge detected -> Cycle found!
                        cycle_members = DSALinkedList()
                        path_temp_stack = DSAStack() # Temporary stack to store popped elements
                        # Reconstruct the cycle by popping elements from `current_dfs_path`
                        # until the `neighbor_node` (the back-edge's target) is reached.
                        current_popped_node = current_dfs_path.top()
                        while current_popped_node != neighbor_node:
                            cycle_members.insertLast(current_popped_node.department_name)
                            path_temp_stack.push(current_dfs_path.pop())
                            current_popped_node = current_dfs_path.top()
                        cycle_members.insertLast(current_popped_node.department_name)
                        # Restore the `current_dfs_path` by pushing elements back from the temporary stack.
                        while not path_temp_stack.isEmpty():
                            current_dfs_path.push(path_temp_stack.pop())

                        # Sort the cycle members alphabetically.
                        if cycle_members.getCount() > 1:
                            bubbleSort(cycle_members)

                        # Create a copy of the cycle for storage to avoid modification during sorting.
                        cycle_copy_for_storage = DSALinkedList()
                        temp_entry = cycle_members.head
                        while temp_entry:
                            cycle_copy_for_storage.insertLast(temp_entry.getValue())
                            temp_entry = temp_entry.getNext()

                        # Add the detected cycle to `detected_cycles` only if it's unique.
                        is_duplicate_cycle = False
                        current_cycle_in_list = detected_cycles.head
                        while current_cycle_in_list and not is_duplicate_cycle:
                            existing_cycle = current_cycle_in_list.getValue() # This is a DSALinkedList of names
                            # Use the helper function to compare cycles.
                            if self._are_cycles_equal(existing_cycle, cycle_copy_for_storage):
                                is_duplicate_cycle = True
                            current_cycle_in_list = current_cycle_in_list.getNext()

                        if not is_duplicate_cycle:
                            detected_cycles.insertLast(cycle_copy_for_storage) # Store the DSALinkedList of names
                # If the neighbor has not been visited, recursively call DFS on it.
                    if not neighbor_node.is_visited:
                        _dfs_recursive_cycle_check(neighbor_node, department_node)

                current_neighbor_node_entry = current_neighbor_node_entry.getNext()
            # Step 5.5: After visiting all neighbors and their subgraphs, remove the current node
            # from the recursion stack (backtrack).
            department_node.recursion_stack = False
            current_dfs_path.pop()

        # Step 6: Start the recursive DFS process from the `start_node`.
        _dfs_recursive_cycle_check(start_node)
        # Step 7: Print the detected cycles
        print(f"\nDFS from '{start_department_name}': Cycle Detection:")
        # Case 1: If no cycles were detected.
        if detected_cycles.isEmpty():
            print("No cycles detected.")
        # Case 2: If cycles were detected, print each unique cycle.
        else:
            print(f"Cycles detected ({detected_cycles.getCount()} unique cycles):")
            current_cycle_entry = detected_cycles.head
            cycle_num = 1
            while current_cycle_entry:
                cycle_members_list = current_cycle_entry.getValue() # This is a DSALinkedList of names
                cycle_members_str = ""
                first_member = True
                temp_name_entry = cycle_members_list.head
                while temp_name_entry:
                    if not first_member:
                        cycle_members_str += ", "
                    cycle_members_str += temp_name_entry.getValue()
                    first_member = False
                    temp_name_entry = temp_name_entry.getNext()
                print(f"  Cycle {cycle_num}: {cycle_members_str}")
                current_cycle_entry = current_cycle_entry.getNext()
                cycle_num += 1

    def find_shortest_path_a_star(self, start_department_name, goal_department_name):
        """
        Implements the A* search algorithm to find the shortest path (in terms of travel time)
        between a `start_department_name` and a `goal_department_name`.
        Currently uses a heuristic that returns 0, effectively making it Dijkstra's algorithm.
        The open set is managed as a DSALinkedList that is sorted by f_score before each removal.
        Source code: https://www.w3schools.com/dsa/dsa_algo_graphs_dijkstra.php
        """
        # Step 1: Reset all algorithm-specific flags and scores (visited, g_score, f_score, path_predecessor)
        # for a clean start to the A* algorithm.
        self._reset_algorithm_states()
        # Step 2: Locate the start and goal department nodes.
        start_node = self.find_department(start_department_name)
        goal_node = self.find_department(goal_department_name)
        # If the start department is not found, raise an error.
        if start_node is None:
            raise ValueError(f"Start department '{start_department_name}' not found.")
        # If the goal department is not found, raise an error.
        if goal_node is None:
            raise ValueError(f"Goal department '{goal_department_name}' not found.")

        # Step 3: Initialize the 'open set' (priority queue) as a DSALinkedList.
        # This will store PriorityQueueEntry objects, sorted by their f_score.
        open_set_priority_queue = DSALinkedList() 
        # Step 4: Set the initial scores for the start node.
        start_node.g_score = 0 # Cost from start to start is 0.
        # Calculate f_score: g_score + heuristic estimate.
        start_node.f_score = self._calculate_heuristic(start_node, goal_node)
        # Add the start node to the open set.
        open_set_priority_queue.insertLast(PriorityQueueEntry(start_node.f_score, start_node))

        # Step 5: Begin the main A* loop. Continue as long as there are nodes to explore in the open set.
        while not open_set_priority_queue.isEmpty():
            # Step 5.1: Sort the open set to ensure the element with the lowest f_score is at the front.
            # This simulates a priority queue's `get_min` operation.
            if open_set_priority_queue.getCount() > 1:
                bubbleSort(open_set_priority_queue) 

            # Step 5.2: Remove the node with the lowest f_score from the open set.
            min_entry = open_set_priority_queue.removeFirst() # This is a PriorityQueueEntry object
            current_f_score = min_entry.f_score # Store its f_score
            current_department = min_entry.department_node # Get the actual DepartmentNode

            # If this department has already been visited (meaning a shorter path to it was finalized), skip it.
            # This is an optimization for A* when nodes can be re-added to the open set with better scores.
            if not current_department.is_visited:
                # Mark the current department as visited (finalized)
                current_department.is_visited = True

                # If the current department is the goal node, a shortest path has been found.
                if current_department == goal_node:
                    # Reconstruct the path from the goal node back to the start using `path_predecessor` 
                    path_str, total_travel_time = self._reconstruct_path(goal_node)
                    return path_str, total_travel_time
                # Step 5.3: Explore neighbors of the `current_department`.
                adjacent_paths_dsa_list = current_department.get_all_adjacent_paths() # Stores PathInfo objects
                current_adj_path_entry = adjacent_paths_dsa_list.head
                while current_adj_path_entry:
                    path_info = current_adj_path_entry.getValue() # PathInfo object
                    neighbor_dep_node = path_info.neighbor_node
                    path_time = path_info.travel_time
                    # Calculate the tentative g_score for the neighbor:
                    # Current department's g_score + cost to reach this neighbor from current department.
                    tentative_g_score = current_department.g_score + path_time
                    # If this new path to the neighbor is shorter (has a lower g_score)
                    # than any previously found path to this neighbor.
                    if tentative_g_score < neighbor_dep_node.g_score:
                        # Update the neighbor's path information.
                        neighbor_dep_node.path_predecessor = current_department # Set current as predecessor
                        neighbor_dep_node.g_score = tentative_g_score # Update g_score
                        # Calculate and update f_score: g_score + heuristic.
                        neighbor_dep_node.f_score = neighbor_dep_node.g_score + self._calculate_heuristic(neighbor_dep_node, goal_node)
                        # Add the neighbor to the open set for future consideration.
                        open_set_priority_queue.insertLast(PriorityQueueEntry(neighbor_dep_node.f_score, neighbor_dep_node))

                    current_adj_path_entry = current_adj_path_entry.getNext()
        # Step 6: If the loop finishes and the goal node was never reached, no path exists.
        print(f"\nNo path found from '{start_department_name}' to '{goal_department_name}'.")
        return None, None


    def _calculate_heuristic(self, current_node, goal_node):
        """
        Placeholder for the A* heuristic function.
        Currently returns 0, which makes A* behave exactly like Dijkstra's algorithm
        (only considering actual path costs, no estimated cost to goal).
        """
        return 0

    def _reconstruct_path(self, goal_node):
        """
        Reconstructs the shortest path from the goal node back to the start node
        using the `path_predecessor` links established during A* search.
        """
        # Step 1: Initialize a DSALinkedList to store the path segments (department names) in reverse order.
        path_segments = DSALinkedList()
        # Step 2: The total travel time is simply the g_score of the goal node.
        total_travel_time = goal_node.g_score
        # Step 3: Traverse backward from the goal node to the start node using `path_predecessor`.
        current_department_in_path = goal_node
        while current_department_in_path is not None:
            # Insert department name at the beginning of the list to build the path in correct order.
            path_segments.insertFirst(current_department_in_path.department_name)
            current_department_in_path = current_department_in_path.path_predecessor

        # Step 4: Convert the linked list of path segments into a formatted string (e.g., "A -> B -> C").
        path_str = ""
        current_node_entry = path_segments.head
        first = True
        while current_node_entry:
            if not first:
                path_str += " -> "
            path_str += current_node_entry.getValue()
            first = False
            current_node_entry = current_node_entry.getNext()

        return path_str, total_travel_time
    
def run_test_case():
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
    hospital_graph.add_department("Emergency") # Test adding existing department

    hospital_graph.print_all_department_names()

    print("\n--- Adding Paths (Corridors) ---")
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

    print("\n--- Graph Structure Overview ---")
    hospital_graph.display_path_list()

    print("\n--- Department and Path Counts ---")
    hospital_graph.get_department_count()
    hospital_graph.get_path_count()

    print("\n--- BFS: Reachable Departments by Level (from Emergency) ---")
    hospital_graph.find_reachable_departments_by_level("Emergency")

    print("\n--- BFS: Reachable Departments by Level (from Outpatient Units - isolated) ---")
    hospital_graph.find_reachable_departments_by_level("Outpatient Units")

    print("\n--- DFS: Cycle Detection (from Emergency) ---")
    hospital_graph.detect_cycles_dfs("Emergency")

    print("\n--- DFS: Cycle Detection (from a node within another cycle - Pharmacy) ---")
    hospital_graph.detect_cycles_dfs("Pharmacy")

    print("\n--- Shortest Path (A* / Dijkstra's) from Emergency to Wards ---")
    path, time = hospital_graph.find_shortest_path_a_star("Emergency", "Wards")
    if path is not None: 
        print(f"Path: {path}, Total Time: {time} minutes.")

    print("\n--- Shortest Path (A* / Dijkstra's) from Radiology to Operating Theatres ---")
    path, time = hospital_graph.find_shortest_path_a_star("Radiology", "Operating Theatres")
    if path is not None:
        print(f"Path: {path}, Total Time: {time} minutes.")

    print("\n--- Shortest Path (A* / Dijkstra's) to an unreachable department (Emergency to Outpatient Units) ---")
    path, time = hospital_graph.find_shortest_path_a_star("Emergency", "Outpatient Units")
    if path is not None:
        print(f"Path: {path}, Total Time: {time} minutes.")

    print("\n--- Removing a Path ---")
    hospital_graph.remove_path("Emergency", "Radiology")
    hospital_graph.display_path_list()

    print("\n--- Shortest Path after path removal (Emergency to Wards) ---")
    hospital_graph.find_shortest_path_a_star("Emergency", "Wards") 
    path, time = hospital_graph.find_shortest_path_a_star("Emergency", "Wards")
    if path is not None:
        print(f"Path: {path}, Total Time: {time} minutes.")

    print("\n--- Removing a Department ---")
    hospital_graph.remove_department("Radiology")
    hospital_graph.display_path_list()

    print("\n--- Shortest Path after department removal (Emergency to Wards) ---")
    hospital_graph.find_shortest_path_a_star("Emergency", "Wards") 

if __name__ == "__main__":
    run_test_case()