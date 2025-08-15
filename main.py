#!/usr/bin/env python3
"""
Family Tree Visualization Application

Creates beautiful family tree visualizations from JSON data with support for
background images and classic styling resembling history textbook illustrations.
"""
import os
import sys
import argparse
from pathlib import Path

from family_tree.core.loader import TreeLoader
from family_tree.rendering.renderer import FamilyTreeRenderer
from family_tree.assets.manager import AssetManager
from family_tree.utils.helpers import setup_logging, analyze_tree_structure, validate_tree_data


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(
        description="Generate beautiful family tree visualizations"
    )
    parser.add_argument(
        "tree_file", 
        nargs="?",
        default="tree.json",
        help="Path to JSON file containing family tree data (default: tree.json)"
    )
    parser.add_argument(
        "-o", "--output",
        default="family_tree.png",
        help="Output PNG file path (default: family_tree.png)"
    )
    parser.add_argument(
        "-b", "--background",
        help="Background image to use (e.g., vintage scroll)"
    )
    parser.add_argument(
        "-s", "--style",
        choices=["classic", "modern"],
        default="classic",
        help="Rendering style (default: classic)"
    )
    parser.add_argument(
        "--create-background",
        choices=["vintage_scroll", "classic_paper"],
        help="Create a default background image"
    )
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze and display tree structure information"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level)
    
    try:
        # Check if tree file exists
        if not os.path.exists(args.tree_file):
            logger.error(f"Tree file not found: {args.tree_file}")
            return 1
        
        # Initialize asset manager
        asset_manager = AssetManager()
        
        # Handle background creation
        if args.create_background:
            logger.info(f"Creating {args.create_background} background...")
            if args.create_background == "vintage_scroll":
                bg_path = asset_manager.create_vintage_scroll_background()
            else:  # classic_paper
                bg_path = asset_manager.create_classic_paper_background()
            logger.info(f"Background created: {bg_path}")
            return 0
        
        # Load family tree data
        logger.info(f"Loading family tree from {args.tree_file}...")
        tree = TreeLoader.load_from_json(args.tree_file)
        logger.info(f"Loaded tree with {len(tree.get_all_people())} people")
        
        # Validate tree data
        issues = validate_tree_data(tree)
        if issues:
            logger.warning("Tree validation issues found:")
            for issue in issues:
                logger.warning(f"  - {issue}")
        
        # Analyze tree if requested
        if args.analyze:
            analysis = analyze_tree_structure(tree)
            logger.info("Tree structure analysis:")
            for key, value in analysis.items():
                logger.info(f"  {key}: {value}")
            return 0
        
        # Handle background selection
        background_path = None
        if args.background:
            background_path = asset_manager.get_background_path(args.background)
            if not background_path:
                # Try to find exact file
                if os.path.exists(args.background):
                    background_path = args.background
                else:
                    logger.warning(f"Background not found: {args.background}")
                    logger.info("Available backgrounds:")
                    for bg in asset_manager.list_backgrounds():
                        logger.info(f"  - {bg}")
        
        # Create renderer and generate tree
        logger.info("Rendering family tree...")
        renderer = FamilyTreeRenderer(tree)
        
        output_path = renderer.render_to_png(
            args.output,
            background_image=background_path,
            style=args.style
        )
        
        logger.info(f"Family tree saved to: {output_path}")
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    import logging
    sys.exit(main())
