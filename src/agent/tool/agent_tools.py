"""
Agent Tools Module

This module provides tool functions that can be used by the agent to interact
with the Factorio game through the FactorioInterface.
"""

from typing import List, Dict, Any, Optional, Union, Tuple
from agents import function_tool
from api.factorio_interface import FactorioInterface
import toml
from knowledge_base.processor.query_processor import QueryProcessor

# Global variables for lazy loading
_factorio_interface = None
_config = None

def get_factorio_interface():
    """Get the factorio interface instance, creating it if necessary"""
    global _factorio_interface, _config
    
    if _factorio_interface is None:
        if _config is None:
            _config = toml.load("config/config.toml")
        _factorio_interface = FactorioInterface(
            _config["rcon"]["host"], 
            _config["rcon"]["port"], 
            _config["rcon"]["password"]
        )
    
    return _factorio_interface

# @function_tool
# def get_available_prototypes() -> Dict[str, List[str]]:
#     """
#     Get lists of available prototype names in the game.
    
#     Returns:
#         Dict with keys 'entities' and 'items', each containing a list of valid names
#     """
#     return factorio.get_available_prototypes()

@function_tool
def get_player_position() -> Dict[str, float]:
    """
    Get the player's current position in the game.
    
    Returns:
        Dict with 'x' and 'y' coordinates
    """
    factorio = get_factorio_interface()
    position = factorio.get_player_position()
    if position:
        return position
    return {"x": 0, "y": 0}  # Default if position cannot be determined

@function_tool
def move_player(x: float, y: float) -> str:
    """
    Move the player to a specific position.
    
    Args:
        x: The x coordinate to move to
        y: The y coordinate to move to
        
    Returns:
        Status message
    """
    factorio = get_factorio_interface()
    success = factorio.move_player(x, y)
    return "Player moved successfully" if success else "Failed to move player"

@function_tool
def search_entities(name: Optional[str] = None, 
                 type: Optional[str] = None,
                 radius: Optional[float] = None,
                 position_x: Optional[float] = None,
                 position_y: Optional[float] = None,
                 limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Search entities in the current game based on specified filters.
    
    Args:
        name: Entity prototype name to filter by
        type: Entity type to filter by (make sure valid)
        radius: Radius of the search circle
        position_x: X coordinate of the center of the search circle
        position_y: Y coordinate of the center of the search circle
        limit: Maximum number of entities to return
    Returns:
        List of entity data dictionaries
    """
    factorio = get_factorio_interface()
    
    # If position not specified, use player position
    if radius and (position_x is None or position_y is None):
        player_pos = factorio.get_player_position()
        if player_pos:
            position_x = position_x or player_pos.get('x', 0)
            position_y = position_y or player_pos.get('y', 0)
    
    return factorio.search_entities(
        name=name, 
        type=type,
        position_x=position_x,
        position_y=position_y,
        radius=radius,
        limit=limit
    )

@function_tool
def place_entity(name: str, x: float, y: float, direction: int) -> str:
    """
    Place an entity in the game.
    
    Args:
        name: The entity prototype name to create
        x: The x coordinate
        y: The y coordinate
        direction: The direction (0, 4, 8, 12 for N, E, S, W)
        
    Returns:
        Status message
    """
    factorio = get_factorio_interface()
    if direction is None:
        direction = 0  # Default to North
    success, message = factorio.place_entity(name, x, y, direction)
    return message

@function_tool
def remove_entity(name: str, x: float, y: float) -> str:
    """
    Remove an entity from the game.
    
    Args:
        name: The entity prototype name to remove
        x: The x coordinate
        y: The y coordinate
        
    Returns:
        Status message
    """
    factorio = get_factorio_interface()
    success, message = factorio.remove_entity(name, x, y)
    return message

@function_tool
def insert_item(item: str, count: int, 
               entity: str,
               x: Optional[float] = None, 
               y: Optional[float] = None) -> str:
    """
    Insert items into an inventory.
    
    Args:
        item: The item name to insert
        count: The count of the item
        entity: The name of the entity to insert into (default: "player")
        x: The x coordinate of the entity (if not player)
        y: The y coordinate of the entity (if not player)
        
    Returns:
        Status message
    """
    factorio = get_factorio_interface()
    # If entity is not specified, use "player"
    if entity is None:
        entity = "player"
    success, message = factorio.insert_item(item, count, "character_main", entity, x, y)
    return message

@function_tool
def remove_item(item: str, count: int, 
               entity: str ,
               x: Optional[float] = None, 
               y: Optional[float] = None) -> str:
    """
    Remove items from an inventory.
    
    Args:
        item: The item name to remove
        count: The count of the item
        entity: The name of the entity to remove from (default: "player")
        x: The x coordinate of the entity (if not player)
        y: The y coordinate of the entity (if not player)
        
    Returns:
        Status message
    """
    factorio = get_factorio_interface()
    # If entity is not specified, use "player"
    if entity is None:
        entity = "player"
    success, message = factorio.remove_item(item, count, entity, x, y)
    return message

@function_tool
def get_inventory(entity: str,
                 inventory_type: str = None,
                 x: Optional[float] = None, 
                 y: Optional[float] = None) -> Dict[str, int]:
    """
    Get inventory contents.
    
    Args:
        entity: The name of the entity to get from (default: "player")
        inventory_type: The type of inventory to get (if not player, can query 'defines.inventory' from wiki knowledge base)
        x: The x coordinate of the entity (if not player)
        y: The y coordinate of the entity (if not player)
        
    Returns:
        Dictionary mapping item names to counts
    """
    factorio = get_factorio_interface()
    # If entity is not specified, use "player"
    if entity is None:
        entity = "player"
    return factorio.get_inventory(entity, inventory_type, x, y)

# @function_tool
def list_supported_entities(mode: str = "all", search_type: str = None, keyword: str = None) -> List[str]:
    """
    Get a list of all supported entities, may not be all entities in the game.
    
    Args:
        mode: Search mode - "all" for all entities, "type" for entities of specific type,
             "search" for keyword search
        search_type: When mode="type", specify the entity type to filter
        keyword: When mode="search", specify the keyword to search entity names
        
    Returns:
        List of supported entity names
    """
    factorio = get_factorio_interface()
    return factorio.list_supported_entities(mode, search_type, keyword)

# @function_tool
def list_supported_items() -> Dict[str, List[str]]:
    """
    Get a list of all supported items, may not be all items in the game.

    Returns:
        Dictionary with keys 'items', each containing a list of valid names
    """
    factorio = get_factorio_interface()
    return factorio.list_supported_items()

@function_tool
def find_surface_tile(name: Optional[str] = None,
                     position_x: Optional[float] = None,
                     position_y: Optional[float] = None,
                     radius: Optional[float] = None,
                     limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """ 
    Find surface tiles in the current game based on specified filters.
    
    Args:
        name: Tile name to filter by
        position_x: X coordinate of the center of the search circle
        position_y: Y coordinate of the center of the search circle
        radius: Radius of the search circle
        limit: Maximum number of tiles to return
        
    Returns:
        List of tile data dictionaries
    """
    factorio = get_factorio_interface()
    return factorio.find_surface_tile(name, position_x, position_y, radius, limit=limit)

@function_tool
def query_api_knowledge_base(query: str, k: int = 5) -> List[Dict]:
    """
    Query the api documentation knowledge base.

    Args:
        query: The query to search for
        k: The number of results to return

    Returns:
        List of results
    """
    if not hasattr(query_api_knowledge_base, "processor"):
        processor = QueryProcessor()
        processor.load_vector_store("data/processed/kb/api_faiss_index.bin", "data/processed/kb/api_chunks_data.pkl")
        query_api_knowledge_base.processor = processor
    else:
        processor = query_api_knowledge_base.processor

    return processor.query(query, k)

@function_tool
def query_wiki_knowledge_base(query: str, k: int = 5) -> List[Dict]:
    """
    Query the wiki documentation knowledge base.

    Args:
        query: The query to search for
        k: The number of results to return

    Returns:
        List of results
    """
    if not hasattr(query_wiki_knowledge_base, "processor"):
        processor = QueryProcessor()
        processor.load_vector_store("data/processed/kb/wiki_faiss_index.bin", "data/processed/kb/wiki_chunks_data.pkl")
        query_wiki_knowledge_base.processor = processor
    else:
        processor = query_wiki_knowledge_base.processor
    return processor.query(query, k)