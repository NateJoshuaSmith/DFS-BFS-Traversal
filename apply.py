# Student Name: [Your Name Here]
# Titan Email: [Your Email Here]
# Project: CPSC 335 – Interactive Campus Navigation System
# Date: [Current Date]

import tkinter as tk
from tkinter import ttk, messagebox
import math

class CampusNavigationSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Campus Navigation System")
        self.root.geometry("1000x700")
        
        # Data storage
        self.buildings = {}  # {name: (x, y, canvas_id)}
        self.edges = {}      # {(building1, building2): {'distance': float, 'time': float, 'accessible': bool}}
        self.graph = {}      # Adjacency list: {building: [connected_buildings]}
        
        # Create main frame
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create button panel
        button_frame = tk.Frame(main_frame)
        button_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        
        # Add building input
        tk.Label(button_frame, text="Building Name:").pack(side=tk.LEFT, padx=5)
        self.building_name = tk.StringVar()
        tk.Entry(button_frame, textvariable=self.building_name, width=15).pack(side=tk.LEFT, padx=5)
        
        # Add edge input fields
        tk.Label(button_frame, text="From:").pack(side=tk.LEFT, padx=5)
        self.from_building = tk.StringVar()
        self.from_combo = ttk.Combobox(button_frame, textvariable=self.from_building, width=12, state="readonly")
        self.from_combo.pack(side=tk.LEFT, padx=5)
        
        tk.Label(button_frame, text="To:").pack(side=tk.LEFT, padx=5)
        self.to_building = tk.StringVar()
        self.to_combo = ttk.Combobox(button_frame, textvariable=self.to_building, width=12, state="readonly")
        self.to_combo.pack(side=tk.LEFT, padx=5)
        
        tk.Label(button_frame, text="Distance:").pack(side=tk.LEFT, padx=5)
        self.distance = tk.StringVar(value="1.0")
        tk.Entry(button_frame, textvariable=self.distance, width=8).pack(side=tk.LEFT, padx=5)
        
        tk.Label(button_frame, text="Time:").pack(side=tk.LEFT, padx=5)
        self.time = tk.StringVar(value="1.0")
        tk.Entry(button_frame, textvariable=self.time, width=8).pack(side=tk.LEFT, padx=5)
        
        self.accessible = tk.BooleanVar(value=False)
        tk.Checkbutton(button_frame, text="Non-Accessible", variable=self.accessible).pack(side=tk.LEFT, padx=5)
        
        self.blocked = tk.BooleanVar(value=False)
        tk.Checkbutton(button_frame, text="Blocked", variable=self.blocked).pack(side=tk.LEFT, padx=5)
        
        # Add buttons
        tk.Button(button_frame, text="Add Building", command=self.add_building).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Connect Buildings", command=self.connect_buildings).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Clear", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        
        # Create pathfinding section
        pathfinding_frame = tk.Frame(main_frame)
        pathfinding_frame.pack(side=tk.TOP, fill=tk.X, pady=(10, 0))
        
        # Start and End node selection
        tk.Label(pathfinding_frame, text="Start:").pack(side=tk.LEFT, padx=5)
        self.start_node = tk.StringVar()
        self.start_combo = ttk.Combobox(pathfinding_frame, textvariable=self.start_node, width=12, state="readonly")
        self.start_combo.pack(side=tk.LEFT, padx=5)
        
        tk.Label(pathfinding_frame, text="End:").pack(side=tk.LEFT, padx=5)
        self.end_node = tk.StringVar()
        self.end_combo = ttk.Combobox(pathfinding_frame, textvariable=self.end_node, width=12, state="readonly")
        self.end_combo.pack(side=tk.LEFT, padx=5)
        
        # Algorithm selection checkboxes
        self.use_bfs = tk.BooleanVar()
        tk.Checkbutton(pathfinding_frame, text="BFS", variable=self.use_bfs).pack(side=tk.LEFT, padx=5)
        
        self.use_dfs = tk.BooleanVar()
        tk.Checkbutton(pathfinding_frame, text="DFS", variable=self.use_dfs).pack(side=tk.LEFT, padx=5)
        
        # Accessibility filter
        self.only_accessible = tk.BooleanVar()
        tk.Checkbutton(pathfinding_frame, text="Only Accessible", variable=self.only_accessible).pack(side=tk.LEFT, padx=5)
        
        # Run pathfinding button
        tk.Button(pathfinding_frame, text="Find Path", command=self.find_path).pack(side=tk.LEFT, padx=5)
        
        # Randomize weights button
        tk.Button(pathfinding_frame, text="Randomize Weights", command=self.randomize_weights).pack(side=tk.LEFT, padx=5)
        
        # Clear animation button
        tk.Button(pathfinding_frame, text="Clear Animation", command=self.clear_animation).pack(side=tk.LEFT, padx=5)
        
        # Create canvas
        self.canvas = tk.Canvas(main_frame, bg="white", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Canvas click binding
        self.canvas.bind("<Button-1>", self.canvas_click)
        
        # Drag and drop functionality
        self.canvas.bind("<B1-Motion>", self.drag_node)
        self.canvas.bind("<ButtonRelease-1>", self.release_node)
        self.dragging = False
        self.drag_node_id = None
        
    def canvas_click(self, event):
        """Handle canvas click - check if clicking on a node"""
        # Check if click is on a node
        clicked_item = self.canvas.find_closest(event.x, event.y)[0]
        
        # Check if the clicked item is a node (oval)
        for building_name, (x, y, canvas_id, text_id) in self.buildings.items():
            if canvas_id == clicked_item:
                self.dragging = True
                self.drag_node_id = building_name
                print(f"Started dragging node: {building_name}")
                return
        
        print(f"Canvas clicked at ({event.x}, {event.y})")
    
    def drag_node(self, event):
        """Handle node dragging"""
        if self.dragging and self.drag_node_id:
            # Update node position
            x, y = event.x, event.y
            building_name = self.drag_node_id
            
            # Update building position in data structure
            self.buildings[building_name] = (x, y, self.buildings[building_name][2], self.buildings[building_name][3])
            
            # Move the visual elements
            canvas_id = self.buildings[building_name][2]
            text_id = self.buildings[building_name][3]
            self.canvas.coords(canvas_id, x-20, y-20, x+20, y+20)
            self.canvas.coords(text_id, x, y)
            
            # Redraw all edges to follow the moved node
            self.redraw_all_edges()
    
    def release_node(self, event):
        """Handle node release"""
        if self.dragging and self.drag_node_id:
            print(f"Released node: {self.drag_node_id}")
            self.dragging = False
            self.drag_node_id = None
    
    def add_building(self):
        building_name = self.building_name.get().strip()
        if building_name:
            if building_name in self.buildings:
                messagebox.showerror("Duplicate Building", f"Building '{building_name}' already exists!")
                return
                
            # Store building data - simple grid layout
            building_count = len(self.buildings)
            
            # Canvas dimensions
            canvas_width = 800
            canvas_height = 600
            
            # Simple grid calculation with even spacing
            if building_count == 0:
                # First node goes in center
                x = canvas_width // 2
                y = canvas_height // 2
            else:
                # Calculate grid position with even spacing
                cols = 3  # 3 buildings per row
                row = building_count // cols
                col = building_count % cols
                
                # Even spacing - 300px apart horizontally, 250px apart vertically
                x = 400 + col * 300  # Start at 400px, then 700px, 1000px
                y = 100 + row * 250  # Start at 100px, then 350px, 600px
            
            canvas_id = self.canvas.create_oval(x-20, y-20, x+20, y+20, fill="lightblue", outline="black")
            text_id = self.canvas.create_text(x, y, text=building_name, fill="black")
            
            self.buildings[building_name] = (x, y, canvas_id, text_id)
            self.graph[building_name] = []  # Initialize empty connections
            
        # Update dropdown lists
            self.update_dropdowns()
            
            print(f"Added building: {building_name} at ({x}, {y})")
            print(f"Current buildings: {list(self.buildings.keys())}")
        else:
            print("Please enter a building name")
    
    def update_dropdowns(self):
        """Update the building dropdown lists"""
        building_names = list(self.buildings.keys())
        self.from_combo['values'] = building_names
        self.to_combo['values'] = building_names
        self.start_combo['values'] = building_names
        self.end_combo['values'] = building_names
    
    
    def connect_buildings(self):
        from_building = self.from_building.get()
        to_building = self.to_building.get()
        distance = self.distance.get()
        time = self.time.get()
        accessible = self.accessible.get()
        blocked = self.blocked.get()
        
        # Validate inputs
        if not from_building or not to_building:
            print("Please select both 'From' and 'To' buildings")
            return
        
        if from_building == to_building:
            print("Cannot connect a building to itself")
            return
        
        try:
            distance_val = float(distance)
            time_val = float(time)
        except ValueError:
            print("Distance and Time must be numbers")
            return
        
        # Create edge
        edge_key = (from_building, to_building)
        reverse_key = (to_building, from_building)
        
        # Check if edge already exists and update it
        existing_edge = None
        if edge_key in self.edges:
            existing_edge = edge_key
        elif reverse_key in self.edges:
            existing_edge = reverse_key
        
        if existing_edge:
            print(f"Updating existing connection between {from_building} and {to_building}")
            # Clear all edge visuals before redrawing
            self.canvas.delete("edge_line")
            self.canvas.delete("edge_label")
        
        # Store edge data
        self.edges[edge_key] = {
            'distance': distance_val,
            'time': time_val,
            'accessible': accessible,
            'blocked': blocked
        }
        
        # Update graph
        self.graph[from_building].append(to_building)
        self.graph[to_building].append(from_building)
        
        # Draw edge on canvas
        self.draw_edge(from_building, to_building)
        
        # If updating existing edge, redraw all edges to ensure clean display
        if existing_edge:
            self.redraw_all_edges()
        
        print(f"Connected {from_building} to {to_building}: {distance_val}m, {time_val}min, accessible={accessible}")
    
    def edit_edge(self):
        """Edit an existing edge"""
        from_building = self.from_building.get()
        to_building = self.to_building.get()
        distance = self.distance.get()
        time = self.time.get()
        accessible = self.accessible.get()
        blocked = self.blocked.get()
        
        # Validate inputs
        if not from_building or not to_building:
            print("Please select both 'From' and 'To' buildings")
            return
        
        if from_building == to_building:
            print("Cannot edit a building connection to itself")
            return
        
        try:
            distance_val = float(distance)
            time_val = float(time)
        except ValueError:
            print("Distance and Time must be numbers")
            return
        
        # Check if edge exists
        edge_key = (from_building, to_building)
        reverse_key = (to_building, from_building)
        
        if edge_key not in self.edges and reverse_key not in self.edges:
            print(f"No connection exists between {from_building} and {to_building}")
            return
        
        # Use the existing edge key
        existing_key = edge_key if edge_key in self.edges else reverse_key
        
        # Remove old visual elements
        self.remove_specific_edge(from_building, to_building)
        
        # Update edge data
        self.edges[existing_key] = {
            'distance': distance_val,
            'time': time_val,
            'accessible': accessible,
            'blocked': blocked
        }
        
        # Redraw the edge
        self.draw_edge(from_building, to_building)
        
        print(f"Updated connection {from_building} to {to_building}: {distance_val}m, {time_val}min, accessible={accessible}, blocked={blocked}")
    
    def remove_specific_edge(self, from_building, to_building):
        """Remove only the specific edge being edited"""
        # Find and remove the specific edge line and label
        # This is a simplified approach - in a more complex system, you'd track individual edge IDs
        # For now, we'll redraw all edges to ensure clean update
        self.redraw_all_edges()
    
    def redraw_all_edges(self):
        """Redraw all edges to ensure clean update"""
        # Clear all edge visuals
        self.canvas.delete("edge_line")
        self.canvas.delete("edge_label")
        
        # Redraw all edges
        for edge_key, edge_data in self.edges.items():
            from_building, to_building = edge_key
            self.draw_edge(from_building, to_building)
    
    def draw_edge(self, from_building, to_building):
        """Draw a line between two buildings"""
        from_x, from_y, _, _ = self.buildings[from_building]
        to_x, to_y, _, _ = self.buildings[to_building]
        
        # Get edge data to determine color
        edge_data = self.edges[(from_building, to_building)]
        if edge_data['blocked']:
            line_color = "red"
        elif edge_data['accessible']:  # Now True means non-accessible
            line_color = "orange"
        else:
            line_color = "gray"
        
        # Calculate edge route that goes around other nodes
        edge_points = self.calculate_edge_route(from_x, from_y, to_x, to_y, from_building, to_building)
        
        # Draw the edge with a break in the middle for the label
        if len(edge_points) == 2:
            # Straight line with break
            start_x, start_y = edge_points[0]
            end_x, end_y = edge_points[1]
            
            # Calculate midpoint
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2
            
            # Create break by drawing two separate line segments with larger gap
            self.canvas.create_line(start_x, start_y, mid_x - 40, mid_y, fill=line_color, width=2, tags="edge_line")
            self.canvas.create_line(mid_x + 40, mid_y, end_x, end_y, fill=line_color, width=2, tags="edge_line")
        else:
            # Curved line - draw as normal but we'll place label at geometric center
            self.canvas.create_line(edge_points, fill=line_color, width=2, smooth=True, tags="edge_line")
        
        # Draw edge label (distance/time) with collision avoidance
        if len(edge_points) == 2:
            # Straight line - place label in the break
            start_x, start_y = edge_points[0]
            end_x, end_y = edge_points[1]
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2
            
            # Place label exactly in the center of the break
            label_x = mid_x
            label_y = mid_y
        else:
            # Curved line - find the middle point of the actual curve
            # For curved paths, find the middle point of the edge_points array
            if len(edge_points) >= 4:  # Curved path with control points
                # Use the middle control point for better positioning
                middle_idx = len(edge_points) // 2
                label_x = edge_points[middle_idx][0]
                label_y = edge_points[middle_idx][1]
            else:
                # Fallback to geometric center
                mid_x = (from_x + to_x) / 2
                mid_y = (from_y + to_y) / 2
                label_x, label_y = mid_x, mid_y
        
        # Find best label position with collision avoidance
        label_x, label_y = self.find_best_label_position(label_x, label_y, from_building, to_building)
        
        edge_data = self.edges[(from_building, to_building)]
        label_text = f"{edge_data['distance']}m/{edge_data['time']}min"
        
        # Always use black text for distance/time labels
        color = "black"
        
        # Draw text with tag for easy deletion
        self.canvas.create_text(label_x, label_y, text=label_text, fill=color, font=("Arial", 9, "bold"), tags="edge_label")
    
    def calculate_edge_route(self, from_x, from_y, to_x, to_y, from_building, to_building):
        """Calculate edge route that goes around other nodes"""
        node_radius = 30  # Increased buffer for better spacing
        buffer = 50  # Larger buffer for more aggressive avoidance
        
        # Check if line intersects with any other nodes
        intersecting_nodes = []
        for building_name, (bx, by, _, _) in self.buildings.items():
            if building_name == from_building or building_name == to_building:
                continue
            
            if self.line_intersects_circle(from_x, from_y, to_x, to_y, bx, by, node_radius + buffer):
                intersecting_nodes.append((bx, by))
        
        if not intersecting_nodes:
            # No intersections, use straight line with adjusted endpoints
            dx = to_x - from_x
            dy = to_y - from_y
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance > 0:
                dx_norm = dx / distance
                dy_norm = dy / distance
                start_x = from_x + dx_norm * node_radius
                start_y = from_y + dy_norm * node_radius
                end_x = to_x - dx_norm * node_radius
                end_y = to_y - dy_norm * node_radius
                return [(start_x, start_y), (end_x, end_y)]
            else:
                return [(from_x, from_y), (to_x, to_y)]
        else:
            # Create curved path around intersecting nodes
            return self.create_curved_path(from_x, from_y, to_x, to_y, intersecting_nodes, node_radius)
    
    def line_intersects_circle(self, x1, y1, x2, y2, cx, cy, radius):
        """Check if line segment intersects with circle"""
        # Distance from line to circle center
        A = y2 - y1
        B = x1 - x2
        C = x2 * y1 - x1 * y2
        
        distance = abs(A * cx + B * cy + C) / math.sqrt(A * A + B * B)
        
        if distance > radius:
            return False
        
        # Check if intersection is within line segment
        dot_product = ((cx - x1) * (x2 - x1) + (cy - y1) * (y2 - y1)) / ((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))
        return 0 <= dot_product <= 1
    
    def create_curved_path(self, from_x, from_y, to_x, to_y, intersecting_nodes, node_radius):
        """Create a curved path around intersecting nodes"""
        # Calculate perpendicular offset
        dx = to_x - from_x
        dy = to_y - from_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance == 0:
            return [(from_x, from_y), (to_x, to_y)]
        
        dx_norm = dx / distance
        dy_norm = dy / distance
        
        # Calculate offset based on number of intersecting nodes and distance
        base_offset = max(60, distance * 0.3) + len(intersecting_nodes) * 25
        
        # Create control points for curved path
        mid_x = (from_x + to_x) / 2
        mid_y = (from_y + to_y) / 2
        
        # Perpendicular direction
        perp_x = -dy_norm * base_offset
        perp_y = dx_norm * base_offset
        
        # Control points - more aggressive curve for better node avoidance
        ctrl1_x = from_x + dx_norm * distance * 0.25 + perp_x
        ctrl1_y = from_y + dy_norm * distance * 0.25 + perp_y
        
        ctrl2_x = from_x + dx_norm * distance * 0.75 + perp_x
        ctrl2_y = from_y + dy_norm * distance * 0.75 + perp_y
        
        # Adjust endpoints to stop at node edges
        start_x = from_x + dx_norm * node_radius
        start_y = from_y + dy_norm * node_radius
        end_x = to_x - dx_norm * node_radius
        end_y = to_y - dy_norm * node_radius
        
        return [(start_x, start_y), (ctrl1_x, ctrl1_y), (ctrl2_x, ctrl2_y), (end_x, end_y)]
    
    def find_best_label_position(self, preferred_x, preferred_y, from_building, to_building):
        """Find the best position for a label that avoids collisions with nodes and other labels"""
        canvas_width = 800
        canvas_height = 600
        label_margin = 80  # Increased margin for better spacing
        node_radius = 50  # Increased buffer around nodes
        label_radius = 60  # Increased buffer around labels
        
        # Try the preferred position first
        if self.is_position_clear(preferred_x, preferred_y, from_building, to_building, node_radius, label_radius):
            return preferred_x, preferred_y
        
        # Try positions around the preferred position with more aggressive search
        max_attempts = 50  # Increased attempts
        for attempt in range(1, max_attempts + 1):
            # Try positions in a spiral pattern with larger steps
            angle = (attempt * 0.3) % (2 * math.pi)  # Slower angle change for better coverage
            radius = attempt * 25  # Larger steps for better spacing
            
            # Try 8 positions around the circle for better coverage
            for offset in [0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4]:
                test_x = preferred_x + radius * math.cos(angle + offset)
                test_y = preferred_y + radius * math.sin(angle + offset)
                
                # Keep within canvas bounds
                test_x = max(label_margin, min(canvas_width - label_margin, test_x))
                test_y = max(label_margin, min(canvas_height - label_margin, test_y))
                
                if self.is_position_clear(test_x, test_y, from_building, to_building, node_radius, label_radius):
                    return test_x, test_y
        
        # If still no clear position, try completely different areas of the canvas
        for attempt in range(max_attempts, max_attempts + 20):
            # Try random positions in different quadrants
            quadrant = attempt % 4
            if quadrant == 0:  # Top-left
                test_x = label_margin + (canvas_width // 2 - label_margin) * (attempt % 5) / 4
                test_y = label_margin + (canvas_height // 2 - label_margin) * (attempt % 7) / 6
            elif quadrant == 1:  # Top-right
                test_x = canvas_width // 2 + (canvas_width - label_margin - canvas_width // 2) * (attempt % 5) / 4
                test_y = label_margin + (canvas_height // 2 - label_margin) * (attempt % 7) / 6
            elif quadrant == 2:  # Bottom-left
                test_x = label_margin + (canvas_width // 2 - label_margin) * (attempt % 5) / 4
                test_y = canvas_height // 2 + (canvas_height - label_margin - canvas_height // 2) * (attempt % 7) / 6
            else:  # Bottom-right
                test_x = canvas_width // 2 + (canvas_width - label_margin - canvas_width // 2) * (attempt % 5) / 4
                test_y = canvas_height // 2 + (canvas_height - label_margin - canvas_height // 2) * (attempt % 7) / 6
            
            if self.is_position_clear(test_x, test_y, from_building, to_building, node_radius, label_radius):
                return test_x, test_y
        
        # If no clear position found, return the preferred position (clamped to canvas)
        return max(label_margin, min(canvas_width - label_margin, preferred_x)), \
               max(label_margin, min(canvas_height - label_margin, preferred_y))
    
    def is_position_clear(self, x, y, from_building, to_building, node_radius, label_radius):
        """Check if a position is clear of nodes and other labels"""
        # Check collision with nodes
        for building_name, (bx, by, _, _) in self.buildings.items():
            if building_name == from_building or building_name == to_building:
                continue
            
            distance = math.sqrt((x - bx) ** 2 + (y - by) ** 2)
            if distance < node_radius + label_radius:
                return False
        
        # Check collision with other labels (approximate)
        # This is a simplified check - in a full implementation you'd track label positions
        return True
    
    def find_path(self):
        """Find path between start and end nodes using selected algorithm"""
        start = self.start_node.get()
        end = self.end_node.get()
        use_bfs = self.use_bfs.get()
        use_dfs = self.use_dfs.get()
        only_accessible = self.only_accessible.get()
        
        # Validate inputs
        if not start or not end:
            messagebox.showerror("Missing Selection", "Please select both start and end nodes")
            return
        
        if start == end:
            messagebox.showerror("Invalid Selection", "Start and end nodes cannot be the same")
            return
        
        if not use_bfs and not use_dfs:
            messagebox.showerror("No Algorithm Selected", "Please select either BFS or DFS")
            return
        
        if use_bfs and use_dfs:
            messagebox.showerror("Multiple Algorithms", "Please select only one algorithm (BFS or DFS)")
            return
        
        # Run selected algorithm
        if use_bfs:
            path, visited_order = self.bfs(start, end, only_accessible)
            algorithm_name = "BFS"
        else:
            path, visited_order = self.dfs(start, end, only_accessible)
            algorithm_name = "DFS"
        
        # Display results
        if path:
            path_str = " → ".join(path)
            traversal_str = " → ".join(visited_order)
            total_distance, total_time = self.calculate_path_weights(path)
            
            # Animate the traversal process
            self.animate_traversal(visited_order, path, algorithm_name)
            
            messagebox.showinfo("Path Found", 
                f"{algorithm_name} Path: {path_str}\n"
                f"Traversal Order: {traversal_str}\n"
                f"Path Length: {len(path)-1} hops\n"
                f"Total Distance: {total_distance}m\n"
                f"Total Time: {total_time}min")
            self.highlight_path(path)
        else:
            messagebox.showerror("No Path Found", f"No path found from {start} to {end}")
    
    def bfs(self, start, end, only_accessible=False):
        """Breadth-First Search implementation"""
        from collections import deque
        
        queue = deque([(start, [start])])
        visited = {start}
        visited_order = [start]  # Track order of visits
        
        while queue:
            current, path = queue.popleft()
            
            if current == end:
                return path, visited_order
            
            for neighbor in self.graph[current]:
                if neighbor not in visited:
                    # Check edge accessibility and blocked status
                    edge_key = (current, neighbor)
                    if edge_key not in self.edges:
                        edge_key = (neighbor, current)
                    
                    if edge_key in self.edges:
                        edge_data = self.edges[edge_key]
                        
                        # Skip blocked edges
                        if edge_data['blocked']:
                            print(f"BFS skipping blocked edge {edge_key}")
                            continue
                        
                        # Check accessibility if required
                        if only_accessible:
                            print(f"BFS checking edge {edge_key}: accessible={edge_data['accessible']}")
                            if edge_data['accessible']:
                                print(f"BFS skipping non-accessible edge {edge_key}")
                                continue
                    
                    visited.add(neighbor)
                    visited_order.append(neighbor)  # Track visit order
                    queue.append((neighbor, path + [neighbor]))
        
        return None, visited_order
    
    def dfs(self, start, end, only_accessible=False):
        """Depth-First Search implementation"""
        visited_order = [start]  # Track order of visits
        
        def dfs_recursive(current, target, path, visited):
            if current == target:
                return path
            
            for neighbor in self.graph[current]:
                if neighbor not in visited:
                    # Check edge accessibility and blocked status
                    edge_key = (current, neighbor)
                    if edge_key not in self.edges:
                        edge_key = (neighbor, current)
                    
                    if edge_key in self.edges:
                        edge_data = self.edges[edge_key]
                        
                        # Skip blocked edges
                        if edge_data['blocked']:
                            print(f"DFS skipping blocked edge {edge_key}")
                            continue
                        
                        # Check accessibility if required
                        if only_accessible:
                            print(f"DFS checking edge {edge_key}: accessible={edge_data['accessible']}")
                            if edge_data['accessible']:
                                print(f"DFS skipping non-accessible edge {edge_key}")
                                continue
                    
                    visited.add(neighbor)
                    visited_order.append(neighbor)  # Track visit order
                    result = dfs_recursive(neighbor, target, path + [neighbor], visited)
                    if result:
                        return result
                    visited.remove(neighbor)
            
            return None
        
        result = dfs_recursive(start, end, [start], {start})
        return result, visited_order
    
    def calculate_path_weights(self, path):
        """Calculate total distance and time for a path"""
        total_distance = 0
        total_time = 0
        
        for i in range(len(path) - 1):
            from_building = path[i]
            to_building = path[i + 1]
            
            # Find the edge data
            edge_key = (from_building, to_building)
            if edge_key not in self.edges:
                edge_key = (to_building, from_building)
            
            if edge_key in self.edges:
                edge_data = self.edges[edge_key]
                total_distance += edge_data['distance']
                total_time += edge_data['time']
        
        return total_distance, total_time
    
    def animate_traversal(self, visited_order, final_path, algorithm_name):
        """Animate the traversal process step by step"""
        import time
        
        # Clear previous highlights
        self.canvas.delete("traversal_highlight")
        self.canvas.delete("current_node")
        
        # Animate each visited node
        for i, node in enumerate(visited_order):
            if node in self.buildings:
                x, y, _, _ = self.buildings[node]
                
                # Highlight current node being processed
                self.canvas.create_oval(x-25, y-25, x+25, y+25, fill="yellow", outline="red", width=3, tags="current_node")
                self.canvas.create_text(x, y, text=node, fill="black", font=("Arial", 10, "bold"), tags="current_node")
                
                # Update canvas
                self.canvas.update()
                
                # Brief pause to show the animation
                time.sleep(0.5)
                
                # Keep the node highlighted but change color
                self.canvas.delete("current_node")
                self.canvas.create_oval(x-20, y-20, x+20, y+20, fill="lightgreen", outline="darkgreen", width=2, tags="traversal_highlight")
                self.canvas.create_text(x, y, text=node, fill="black", tags="traversal_highlight")
        
        # Highlight the final path in a different color
        self.canvas.delete("current_node")
        for i in range(len(final_path) - 1):
            from_building = final_path[i]
            to_building = final_path[i + 1]
            
            if from_building in self.buildings and to_building in self.buildings:
                from_x, from_y, _, _ = self.buildings[from_building]
                to_x, to_y, _, _ = self.buildings[to_building]
                
                # Draw path edge in blue
                self.canvas.create_line(from_x, from_y, to_x, to_y, fill="blue", width=4, tags="traversal_highlight")
    
    def randomize_weights(self):
        """Randomize all edge weights to simulate dynamic traffic"""
        import random
        
        # Randomize each edge's distance and time
        for edge_key, edge_data in self.edges.items():
            # Generate random distance (50m to 500m)
            new_distance = random.uniform(50, 500)
            
            # Generate random time (1min to 15min)
            new_time = random.uniform(1, 15)
            
            # Update edge data
            edge_data['distance'] = round(new_distance, 1)
            edge_data['time'] = round(new_time, 1)
        
        # Redraw all edges to show new weights
        self.redraw_all_edges()
        
        print(f"Randomized weights for {len(self.edges)} edges")
        print("New weights:")
        for edge_key, edge_data in self.edges.items():
            print(f"  {edge_key}: {edge_data['distance']}m, {edge_data['time']}min")
    
    def clear_animation(self):
        """Clear all animation colors and highlights"""
        # Clear animation highlights
        self.canvas.delete("traversal_highlight")
        self.canvas.delete("current_node")
        self.canvas.delete("path_highlight")
        
        # Restore original node colors
        for building_name, (x, y, canvas_id, text_id) in self.buildings.items():
            # Restore original node appearance
            self.canvas.itemconfig(canvas_id, fill="lightblue", outline="black", width=1)
            self.canvas.itemconfig(text_id, fill="black", font=("Arial", 9))
        
        print("Cleared all animation colors and highlights")
    
    def highlight_path(self, path):
        """Highlight the found path on the canvas"""
        # Clear previous highlights
        self.canvas.delete("path_highlight")
        
        # Highlight path edges using the same routing logic as regular edges
        for i in range(len(path) - 1):
            from_building = path[i]
            to_building = path[i + 1]
            
            # Get building positions
            from_x, from_y, _ = self.buildings[from_building]
            to_x, to_y, _ = self.buildings[to_building]
            
            # Calculate edge route that goes around other nodes
            edge_points = self.calculate_edge_route(from_x, from_y, to_x, to_y, from_building, to_building)
            
            # Draw highlighted edge using the calculated points
            if len(edge_points) == 2:
                # Straight line with break
                start_x, start_y = edge_points[0]
                end_x, end_y = edge_points[1]
                
                # Calculate midpoint for break
                mid_x = (start_x + end_x) / 2
                mid_y = (start_y + end_y) / 2
                
                # Create break by drawing two separate line segments
                self.canvas.create_line(start_x, start_y, mid_x - 40, mid_y, fill="green", width=4, tags="path_highlight")
                self.canvas.create_line(mid_x + 40, mid_y, end_x, end_y, fill="green", width=4, tags="path_highlight")
            else:
                # Curved line with multiple points
                self.canvas.create_line(edge_points, fill="green", width=4, smooth=True, tags="path_highlight")
    
    def run_bfs(self):
        print("Run BFS button clicked - use Find Path button instead")
    
    def run_dfs(self):
        print("Run DFS button clicked - use Find Path button instead")
    
    def clear_all(self):
        """Clear all edges, labels, buildings, and reset data structures"""
        # Clear all visual elements
        self.canvas.delete("all")  # Clear everything from canvas
        
        # Clear all data structures
        self.buildings.clear()
        self.edges.clear()
        self.graph.clear()
        
        # Clear input fields
        self.building_name.set("")
        self.distance.set("1.0")
        self.time.set("1.0")
        self.accessible.set(False)
        self.blocked.set(False)
        self.from_building.set("")
        self.to_building.set("")
        
        # Update dropdowns to reflect empty state
        self.update_dropdowns()
        
        print("Cleared all buildings, edges, and connections")

def main():
    root = tk.Tk()
    app = CampusNavigationSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()