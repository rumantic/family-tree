"""
Data loader for JSON family tree files.
"""
import json
from typing import Dict, Any
from .models import Person, FamilyTree


class TreeLoader:
    """Loads family tree data from JSON files."""
    
    @staticmethod
    def load_from_json(file_path: str) -> FamilyTree:
        """Load family tree from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return TreeLoader._parse_tree_data(data)
    
    @staticmethod
    def _parse_tree_data(data: Dict[str, Any]) -> FamilyTree:
        """Parse JSON data into FamilyTree structure."""
        # Track all people by ID to avoid duplicates
        people_cache = {}
        
        def parse_person(person_data: Dict[str, Any]) -> Person:
            """Recursively parse person and their parents."""
            person_id = person_data.get('id')
            
            # Return cached person if already parsed
            if person_id in people_cache:
                return people_cache[person_id]
            
            # Create person without parents first
            person = Person(
                id=person_id,
                name=person_data.get('name', ''),
                birth_year=person_data.get('birthyear'),
                photo=person_data.get('photo'),
                type=person_data.get('type', 'person'),
                stock=person_data.get('stock', False),
                parents=[]
            )
            
            # Cache the person before parsing parents to avoid infinite recursion
            people_cache[person_id] = person
            
            # Parse parents
            parents_data = person_data.get('parents', [])
            for parent_data in parents_data:
                parent = parse_person(parent_data)
                person.add_parent(parent)
            
            return person
        
        # Parse the root person
        root_person = parse_person(data)
        
        # Create the family tree
        tree = FamilyTree(
            root=root_person,
            last_id=data.get('lastId', 0),
            all_people=people_cache
        )
        
        return tree