"""
Spatial grid management - pure functions for grid operations
"""
import random

def create_grid(width, height, topology="torus"):
    """
    Create spatial grid
    
    Args:
        width: Grid width
        height: Grid height
        topology: "torus" or "bounded"
        
    Returns:
        grid: Dictionary containing grid state
    """
    return {
        "width": width,
        "height": height,
        "topology": topology,
        "cells": {}  # Will store cell contents if needed
    }

def get_random_position(grid):
    """
    Get random position within grid bounds
    
    Args:
        grid: Grid dictionary
        
    Returns:
        position: Dictionary with x, y coordinates
    """
    return {
        "x": random.randint(0, grid["width"] - 1),
        "y": random.randint(0, grid["height"] - 1)
    }

def get_adjacent_positions(position, grid):
    """
    Get all adjacent positions to given position
    
    Args:
        position: Dictionary with x, y coordinates
        grid: Grid dictionary
        
    Returns:
        positions: List of adjacent position dictionaries
    """
    x, y = position["x"], position["y"]
    adjacent = []
    
    # All 8 directions (including diagonals)
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
                
            new_x = x + dx
            new_y = y + dy
            
            # Handle boundaries based on topology
            if grid["topology"] == "torus":
                new_x = new_x % grid["width"]
                new_y = new_y % grid["height"]
            elif grid["topology"] == "bounded":
                if new_x < 0 or new_x >= grid["width"] or new_y < 0 or new_y >= grid["height"]:
                    continue
            
            adjacent.append({"x": new_x, "y": new_y})
    
    return adjacent

def get_random_adjacent(position, grid):
    """
    Get random adjacent position
    
    Args:
        position: Dictionary with x, y coordinates
        grid: Grid dictionary
        
    Returns:
        position: Random adjacent position dictionary
    """
    adjacent = get_adjacent_positions(position, grid)
    if not adjacent:
        return position  # No valid adjacent positions
    return random.choice(adjacent)

def distance(pos1, pos2, grid=None):
    """
    Calculate distance between two positions
    
    Args:
        pos1: First position dictionary
        pos2: Second position dictionary
        grid: Grid dictionary (for torus distance calculation)
        
    Returns:
        distance: Euclidean distance
    """
    dx = abs(pos1["x"] - pos2["x"])
    dy = abs(pos1["y"] - pos2["y"])
    
    # Handle torus topology
    if grid and grid["topology"] == "torus":
        dx = min(dx, grid["width"] - dx)
        dy = min(dy, grid["height"] - dy)
    
    return (dx**2 + dy**2)**0.5

def get_neighbors(position, grid, radius=1):
    """
    Get all positions within radius
    
    Args:
        position: Center position dictionary
        grid: Grid dictionary
        radius: Search radius
        
    Returns:
        positions: List of position dictionaries within radius
    """
    neighbors = []
    x, y = position["x"], position["y"]
    
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            if dx == 0 and dy == 0:
                continue
                
            new_x = x + dx
            new_y = y + dy
            
            # Handle boundaries
            if grid["topology"] == "torus":
                new_x = new_x % grid["width"]
                new_y = new_y % grid["height"]
            elif grid["topology"] == "bounded":
                if new_x < 0 or new_x >= grid["width"] or new_y < 0 or new_y >= grid["height"]:
                    continue
            
            # Check if within radius
            neighbor_pos = {"x": new_x, "y": new_y}
            if distance(position, neighbor_pos, grid) <= radius:
                neighbors.append(neighbor_pos)
    
    return neighbors
