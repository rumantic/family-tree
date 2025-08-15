"""
Alternative tree renderer using matplotlib for environments without Graphviz.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import networkx as nx
import numpy as np
from typing import Dict, Tuple, Optional
from PIL import Image

from ..core.models import FamilyTree, Person


class MatplotlibTreeRenderer:
    """Renders family trees using matplotlib when Graphviz is not available."""
    
    def __init__(self, tree: FamilyTree):
        self.tree = tree
        self.node_positions = {}
        self.fig_size = (16, 12)  # Default figure size
    
    def render_to_png(self, output_path: str, 
                     background_image: Optional[str] = None,
                     style: str = "classic") -> str:
        """
        Render family tree to PNG file using matplotlib.
        
        Args:
            output_path: Path for output PNG file
            background_image: Optional background image path
            style: Rendering style ('classic', 'modern')
            
        Returns:
            Path to generated PNG file
        """
        # Create the layout
        self._calculate_layout()
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.fig_size, dpi=300)
        
        # Set background
        if style == "classic":
            fig.patch.set_facecolor('#f9f9f9')
            ax.set_facecolor('#f9f9f9')
        else:
            fig.patch.set_facecolor('white')
            ax.set_facecolor('white')
        
        # Draw connections first (so they appear behind nodes)
        self._draw_connections(ax, style)
        
        # Draw nodes
        self._draw_nodes(ax, style)
        
        # Style the plot
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Set margins
        plt.tight_layout(pad=1.0)
        
        # Save to file
        plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                   facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close()
        
        # Apply background if specified
        if background_image:
            self._apply_background(output_path, background_image)
        
        return output_path
    
    def _calculate_layout(self):
        """Calculate positions for all nodes using a hierarchical layout."""
        generations = self.tree.get_generations()
        
        # Calculate vertical spacing
        max_generation = max(generations.keys())
        y_spacing = 2.0
        
        # Calculate positions for each generation
        for level, people in generations.items():
            y = max_generation * y_spacing - level * y_spacing
            
            # Calculate horizontal spacing for this level
            count = len(people)
            if count == 1:
                x_positions = [0]
            else:
                x_spacing = max(3.0, 8.0 / count)  # Adjust spacing based on number of people
                x_positions = [(i - (count - 1) / 2) * x_spacing for i in range(count)]
            
            # Assign positions
            for i, person in enumerate(people):
                self.node_positions[person.id] = (x_positions[i], y)
    
    def _draw_nodes(self, ax, style: str):
        """Draw all person nodes."""
        for person in self.tree.get_all_people():
            if person.id in self.node_positions:
                x, y = self.node_positions[person.id]
                self._draw_person_node(ax, person, x, y, style)
    
    def _draw_person_node(self, ax, person: Person, x: float, y: float, style: str):
        """Draw a single person node."""
        # Node styling based on type and style
        if style == "classic":
            if person.type == 'root':
                box_color = '#e6f2ff'
                border_color = '#4169E1'
                border_width = 3
            elif person.type == 'parent':
                box_color = '#fff0e6'
                border_color = '#D2691E'
                border_width = 2
            else:
                box_color = '#f9f9f9'
                border_color = '#8B4513'
                border_width = 1
        else:  # modern
            box_color = 'white'
            border_color = '#333333'
            border_width = 1
        
        # Create text
        text_lines = self._format_person_text(person)
        text = '\n'.join(text_lines)
        
        # Calculate text dimensions for box sizing
        text_width = max(len(line) for line in text_lines) * 0.08
        text_height = len(text_lines) * 0.15
        
        # Draw box
        box = FancyBboxPatch(
            (x - text_width/2, y - text_height/2),
            text_width, text_height,
            boxstyle="round,pad=0.1",
            facecolor=box_color,
            edgecolor=border_color,
            linewidth=border_width
        )
        ax.add_patch(box)
        
        # Draw text
        ax.text(x, y, text, ha='center', va='center',
               fontsize=8, fontfamily='serif' if style == "classic" else 'sans-serif',
               weight='bold' if person.type == 'root' else 'normal')
    
    def _format_person_text(self, person: Person) -> list:
        """Format person information for display."""
        lines = []
        
        # Split long names
        name_parts = person.name.split()
        if len(name_parts) > 2:
            # Split into first names and last name
            first_names = ' '.join(name_parts[:-1])
            last_name = name_parts[-1]
            lines.append(first_names)
            lines.append(last_name)
        else:
            lines.append(person.name)
        
        # Add birth year
        if person.birth_year:
            lines.append(f"({person.birth_year})")
        
        return lines
    
    def _draw_connections(self, ax, style: str):
        """Draw lines connecting parents to children."""
        line_color = '#8B4513' if style == "classic" else '#666666'
        line_width = 2 if style == "classic" else 1
        
        for person in self.tree.get_all_people():
            if person.id in self.node_positions:
                child_pos = self.node_positions[person.id]
                
                for parent in person.parents:
                    if parent.id in self.node_positions:
                        parent_pos = self.node_positions[parent.id]
                        
                        # Draw line from parent to child
                        ax.plot([parent_pos[0], child_pos[0]], 
                               [parent_pos[1], child_pos[1]],
                               color=line_color, linewidth=line_width, alpha=0.7)
    
    def _apply_background(self, image_path: str, background_path: str):
        """Apply background image to the rendered tree."""
        try:
            # Open images
            tree_img = Image.open(image_path)
            background = Image.open(background_path)
            
            # Convert tree image to RGBA if not already
            if tree_img.mode != 'RGBA':
                tree_img = tree_img.convert('RGBA')
            
            # Resize background to fit tree image
            background = background.resize(tree_img.size, Image.LANCZOS)
            
            # Composite images
            result = Image.alpha_composite(
                background.convert('RGBA'), 
                tree_img
            )
            
            # Save result
            result.convert('RGB').save(image_path)
            
        except Exception as e:
            print(f"Warning: Could not apply background - {e}")
            # Continue without background