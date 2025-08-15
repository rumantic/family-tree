"""
Utility functions for family tree processing.
"""
import logging
from typing import Dict, List
from ..core.models import FamilyTree, Person


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Setup logging for the application."""
    logger = logging.getLogger('family_tree')
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def analyze_tree_structure(tree: FamilyTree) -> Dict[str, int]:
    """Analyze the structure of a family tree."""
    people = tree.get_all_people()
    generations = tree.get_generations()
    
    analysis = {
        'total_people': len(people),
        'total_generations': len(generations),
        'people_with_photos': sum(1 for p in people if p.photo),
        'people_with_birth_years': sum(1 for p in people if p.birth_year),
        'max_children': max(len(p.parents) for p in people) if people else 0
    }
    
    # Count people per generation
    for level, gen_people in generations.items():
        analysis[f'generation_{level}_count'] = len(gen_people)
    
    return analysis


def validate_tree_data(tree: FamilyTree) -> List[str]:
    """Validate family tree data and return list of issues."""
    issues = []
    
    # Check for people without names
    unnamed_people = [p for p in tree.get_all_people() if not p.name.strip()]
    if unnamed_people:
        issues.append(f"Found {len(unnamed_people)} people without names")
    
    # Check for duplicate IDs
    ids = [p.id for p in tree.get_all_people()]
    duplicates = set([x for x in ids if ids.count(x) > 1])
    if duplicates:
        issues.append(f"Duplicate IDs found: {duplicates}")
    
    # Check for circular references (basic check)
    for person in tree.get_all_people():
        if person in person.parents:
            issues.append(f"Person {person.name} is their own parent")
    
    return issues