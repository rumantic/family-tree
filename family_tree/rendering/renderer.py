"""
Tree renderer using Graphviz for creating beautiful family trees.
Falls back to matplotlib if Graphviz is not available.
"""
import os
import tempfile
from typing import Optional, Tuple, Dict
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO

from ..core.models import FamilyTree, Person

# Try to import Graphviz, fall back to matplotlib if not available
try:
    from graphviz import Digraph
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False

# Always import matplotlib renderer as fallback
try:
    from .matplotlib_renderer import MatplotlibTreeRenderer
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class FamilyTreeRenderer:
    """Renders family trees using Graphviz with classic styling."""
    
    def __init__(self, tree: FamilyTree):
        self.tree = tree
        self.node_images = {}  # Cache for person photos
        
    def render_to_png(self, output_path: str, 
                     background_image: Optional[str] = None,
                     style: str = "classic") -> str:
        """
        Render family tree to PNG file.
        
        Args:
            output_path: Path for output PNG file
            background_image: Optional background image path
            style: Rendering style ('classic', 'modern')
            
        Returns:
            Path to generated PNG file
        """
        # Check if Graphviz is available, fall back to matplotlib if not
        try:
            if GRAPHVIZ_AVAILABLE:
                return self._render_with_graphviz(output_path, background_image, style)
            else:
                return self._render_with_matplotlib(output_path, background_image, style)
        except Exception as e:
            # If Graphviz fails, try matplotlib as fallback
            if GRAPHVIZ_AVAILABLE:
                print(f"Graphviz failed ({e}), falling back to matplotlib...")
                return self._render_with_matplotlib(output_path, background_image, style)
            else:
                raise e
    
    def _render_with_matplotlib(self, output_path: str, background_image: Optional[str], style: str) -> str:
        """Render using matplotlib fallback."""
        if not MATPLOTLIB_AVAILABLE:
            raise ImportError("Matplotlib renderer not available")
        renderer = MatplotlibTreeRenderer(self.tree)
        return renderer.render_to_png(output_path, background_image, style)
    
    def _render_with_graphviz(self, output_path: str, background_image: Optional[str], style: str) -> str:
        """Render using Graphviz."""
        # Generate the graph
        dot = self._create_graphviz_tree(style)
        
        # Render to temporary file first
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Render the graph
        dot.render(temp_path, format='png', cleanup=True)
        rendered_path = temp_path + '.png'
        
        # Apply background if specified
        if background_image and os.path.exists(background_image):
            final_image = self._apply_background(rendered_path, background_image)
        else:
            final_image = Image.open(rendered_path)
        
        # Save final image
        final_image.save(output_path, 'PNG', dpi=(300, 300))
        
        # Cleanup temporary files
        if os.path.exists(rendered_path):
            os.unlink(rendered_path)
        if os.path.exists(temp_path):
            os.unlink(temp_path)
            
        return output_path
    
    def _create_graphviz_tree(self, style: str = "classic") -> Digraph:
        """Create Graphviz representation of the family tree."""
        # Create directed graph
        dot = Digraph(comment='Family Tree', format='png')
        
        # Set graph attributes for classic look
        if style == "classic":
            dot.attr(
                rankdir='TB',  # Top to bottom
                bgcolor='transparent',
                dpi='300',
                size='11,8.5',  # Letter size
                ratio='auto'
            )
            dot.attr('node', 
                    shape='box',
                    style='rounded,filled',
                    fillcolor='#f9f9f9',
                    fontname='Times-Roman',
                    fontsize='10',
                    margin='0.3,0.1')
            dot.attr('edge',
                    color='#8B4513',  # Brown color for classic look
                    penwidth='2',
                    arrowhead='none')
        
        # Add all people as nodes
        generations = self.tree.get_generations()
        for level, people in generations.items():
            # Group people in same generation using subgraph
            with dot.subgraph() as sub:
                sub.attr(rank='same')
                for person in people:
                    self._add_person_node(sub, person, style)
        
        # Add edges (parent-child relationships)
        for person in self.tree.get_all_people():
            for parent in person.parents:
                dot.edge(str(parent.id), str(person.id))
        
        return dot
    
    def _add_person_node(self, graph: Digraph, person: Person, style: str):
        """Add a person as a node to the graph."""
        # Create label with person info
        label = self._create_person_label(person, style)
        
        # Set node attributes based on type
        node_attrs = {'label': label}
        
        if person.type == 'root':
            node_attrs.update({
                'fillcolor': '#e6f2ff',
                'penwidth': '3',
                'color': '#4169E1'
            })
        elif person.type == 'parent':
            node_attrs.update({
                'fillcolor': '#fff0e6',
                'penwidth': '2',
                'color': '#D2691E'
            })
        
        graph.node(str(person.id), **node_attrs)
    
    def _create_person_label(self, person: Person, style: str) -> str:
        """Create label text for a person node."""
        lines = []
        
        # Name (split long names)
        name_parts = person.name.split()
        if len(name_parts) > 2:
            # Split into first names and last name
            first_names = ' '.join(name_parts[:-1])
            last_name = name_parts[-1]
            lines.append(first_names)
            lines.append(last_name)
        else:
            lines.append(person.name)
        
        # Birth year
        if person.birth_year:
            lines.append(f"({person.birth_year})")
        
        return '\\n'.join(lines)
    
    def _apply_background(self, tree_image_path: str, background_path: str) -> Image.Image:
        """Apply background image to the family tree."""
        # Open images
        background = Image.open(background_path)
        tree_img = Image.open(tree_image_path)
        
        # Convert tree image to RGBA if not already
        if tree_img.mode != 'RGBA':
            tree_img = tree_img.convert('RGBA')
        
        # Resize background to fit tree image while maintaining aspect ratio
        bg_ratio = background.width / background.height
        tree_ratio = tree_img.width / tree_img.height
        
        if bg_ratio > tree_ratio:
            # Background is wider - scale by height
            new_height = tree_img.height
            new_width = int(new_height * bg_ratio)
        else:
            # Background is taller - scale by width
            new_width = tree_img.width
            new_height = int(new_width / bg_ratio)
        
        background = background.resize((new_width, new_height), Image.LANCZOS)
        
        # Create new image with background size
        result = Image.new('RGBA', background.size, (255, 255, 255, 0))
        result.paste(background, (0, 0))
        
        # Center the tree on the background
        x_offset = (background.width - tree_img.width) // 2
        y_offset = (background.height - tree_img.height) // 2
        
        # Composite tree image onto background
        result.paste(tree_img, (x_offset, y_offset), tree_img)
        
        return result.convert('RGB')