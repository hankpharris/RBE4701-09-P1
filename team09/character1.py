# This is necessary to find the main code
import sys
import heapq
import math

#This is the start of our code, algorithmically controlling behavior
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back

class Character1(CharacterEntity):

    def __init__(self, name, avatar, x, y):
        super().__init__(name, avatar, x, y)
        self.path = []
        self.path_index = 0

    def do(self, wrld):
        # Find the exit
        exit_pos = self.find_exit(wrld)
        if not exit_pos:
            return  # No exit found, stay still
        
        # If we're at the exit, we're done
        if (self.x, self.y) == exit_pos:
            return
        
        # If we have a valid path and haven't reached the end
        if self.path_index < len(self.path):
            next_pos = self.path[self.path_index]
            dx = next_pos[0] - self.x
            dy = next_pos[1] - self.y
            self.move(dx, dy)
            self.path_index += 1
        else:
            # Find a new path using A*
            self.path = self.astar_pathfinding(wrld, (self.x, self.y), exit_pos)
            self.path_index = 0
            if self.path:
                next_pos = self.path[0]
                dx = next_pos[0] - self.x
                dy = next_pos[1] - self.y
                self.move(dx, dy)
                self.path_index = 1

    def find_exit(self, wrld):
        """Find the exit position in the world"""
        for x in range(wrld.width()):
            for y in range(wrld.height()):
                if wrld.exit_at(x, y):
                    return (x, y)
        return None

    def manhattan_distance(self, pos1, pos2):
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def get_neighbors(self, pos, wrld):
        """Get valid neighboring positions (8-directional movement)"""
        neighbors = []
        x, y = pos
        
        # 8-directional movement: N, NE, E, SE, S, SW, W, NW
        directions = [
            (0, -1),   # North
            (1, -1),   # Northeast
            (1, 0),    # East
            (1, 1),    # Southeast
            (0, 1),    # South
            (-1, 1),   # Southwest
            (-1, 0),   # West
            (-1, -1)   # Northwest
        ]
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            
            # Check bounds
            if (0 <= new_x < wrld.width() and 0 <= new_y < wrld.height()):
                # Check if position is walkable (not a wall, not occupied by bomb/explosion)
                if (not wrld.wall_at(new_x, new_y) and 
                    not wrld.bomb_at(new_x, new_y) and 
                    not wrld.explosion_at(new_x, new_y)):
                    neighbors.append((new_x, new_y))
        
        return neighbors

    def astar_pathfinding(self, wrld, start, goal):
        """A* pathfinding algorithm with 8-directional movement"""
        # Priority queue: (f_score, position)
        open_set = [(0, start)]
        heapq.heapify(open_set)
        
        # Dictionaries to store costs and paths
        g_score = {start: 0}
        f_score = {start: self.manhattan_distance(start, goal)}
        came_from = {}
        
        # Set to track positions in open set
        open_set_positions = {start}
        
        # Set to track explored positions
        closed_set = set()
        
        while open_set:
            # Get position with lowest f_score
            current_f, current = heapq.heappop(open_set)
            
            if current in open_set_positions:
                open_set_positions.remove(current)
            
            # If we reached the goal, reconstruct path
            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.reverse()
                return path
            
            closed_set.add(current)
            
            # Check all neighbors
            for neighbor in self.get_neighbors(current, wrld):
                if neighbor in closed_set:
                    continue
                
                # Calculate movement cost (diagonal movement costs more)
                dx = abs(neighbor[0] - current[0])
                dy = abs(neighbor[1] - current[1])
                if dx == 1 and dy == 1:  # Diagonal movement
                    move_cost = math.sqrt(2)
                else:  # Orthogonal movement
                    move_cost = 1
                
                tentative_g = g_score[current] + move_cost
                
                # If this path to neighbor is better than any previous one
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + self.manhattan_distance(neighbor, goal)
                    
                    # Add to open set if not already there
                    if neighbor not in open_set_positions:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
                        open_set_positions.add(neighbor)
        
        # No path found
        return []
