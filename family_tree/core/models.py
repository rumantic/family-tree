"""
Core data models for family tree representation.
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import base64
from io import BytesIO
from PIL import Image


@dataclass
class Person:
    """Represents a person in the family tree."""
    id: int
    name: str
    birth_year: Optional[str] = None
    photo: Optional[str] = None  # Base64 encoded image
    type: str = "person"
    stock: bool = False
    parents: List['Person'] = None
    
    def __post_init__(self):
        if self.parents is None:
            self.parents = []
    
    def get_photo_image(self) -> Optional[Image.Image]:
        """Convert base64 photo data to PIL Image."""
        if not self.photo or not self.photo.startswith('data:image'):
            return None
        
        try:
            # Extract base64 data after comma
            base64_data = self.photo.split(',', 1)[1]
            image_data = base64.b64decode(base64_data)
            return Image.open(BytesIO(image_data))
        except Exception:
            return None
    
    def add_parent(self, parent: 'Person'):
        """Add a parent to this person."""
        if parent not in self.parents:
            self.parents.append(parent)
    
    def get_all_descendants(self) -> List['Person']:
        """Get all descendants (children, grandchildren, etc.) of this person."""
        descendants = []
        for parent in self.parents:
            descendants.extend(parent.get_all_descendants())
        descendants.extend(self.parents)
        return list(set(descendants))  # Remove duplicates
    
    def __str__(self):
        birth_info = f" ({self.birth_year})" if self.birth_year else ""
        return f"{self.name}{birth_info}"
    
    def __hash__(self):
        return hash(self.id)
    
    def __eq__(self, other):
        if not isinstance(other, Person):
            return False
        return self.id == other.id


@dataclass 
class FamilyTree:
    """Represents the complete family tree structure."""
    root: Person
    last_id: int
    all_people: Dict[int, Person] = None
    
    def __post_init__(self):
        if self.all_people is None:
            self.all_people = {}
            self._collect_all_people(self.root)
    
    def _collect_all_people(self, person: Person):
        """Recursively collect all people in the tree."""
        if person.id not in self.all_people:
            self.all_people[person.id] = person
            for parent in person.parents:
                self._collect_all_people(parent)
    
    def get_person_by_id(self, person_id: int) -> Optional[Person]:
        """Get a person by their ID."""
        return self.all_people.get(person_id)
    
    def get_all_people(self) -> List[Person]:
        """Get all people in the tree."""
        return list(self.all_people.values())
    
    def get_generations(self) -> Dict[int, List[Person]]:
        """Organize people by generation level (0=root, 1=parents, etc.)."""
        generations = {}
        
        def assign_generation(person: Person, level: int):
            if level not in generations:
                generations[level] = []
            if person not in generations[level]:
                generations[level].append(person)
            
            # Parents are one generation up
            for parent in person.parents:
                assign_generation(parent, level + 1)
        
        assign_generation(self.root, 0)
        return generations