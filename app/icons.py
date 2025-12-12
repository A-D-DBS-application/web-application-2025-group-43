# app/icons.py

PLANT_ICONS = {
    'beans': '🌱',
    'carrot': '🥕',
    'leek': '🥬',
    'lettuce': '🥬',
    'onion': '🧅',
    'shallot': '🧅',
    'paprika': '🌶️',
    'pepper': '🌶️',
    'pumpkin': '🎃',
    'strawberry': '🍓',
    'tomato': '🍅',
    'zucchini': '🥒',
    # Default
    'default': '🌱',
}

def get_plant_icon(plant_name: str) -> str:
    """Get icon for a given plant name, with fallback to a default icon."""
    if plant_name is None:
        return PLANT_ICONS['default']
    
    # Normalize plant_name to a list of keywords
    # e.g. "Onion/shallot" -> ["onion", "shallot"]
    # e.g. "Paprika/pepper" -> ["paprika", "pepper"]
    keywords = plant_name.lower().replace('/', ' ').replace('_', ' ').split()
    
    for key in keywords:
        if key in PLANT_ICONS:
            return PLANT_ICONS[key]
            
    return PLANT_ICONS['default']
