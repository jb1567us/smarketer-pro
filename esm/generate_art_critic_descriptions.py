import json
import random
import sys

# Load Data
json_path = 'collections_data.json'
try:
    with open(json_path, 'r') as f:
        data = json.load(f)
except Exception as e:
    print(f"Error loading JSON: {e}")
    sys.exit(1)

# --- REFINED COLOR MAPPING (V2) ---
COLOR_CATEGORIES = {
    'warm': {
        'Red', 'Orange', 'Yellow', 'Gold', 'Brown', 'Pink', 'Brass', 'Bronze', 'Ochre', 
        'Amber', 'Saffron', 'Canary', 'Crimson', 'Scarlet', 'Burgundy', 'Rust', 'Coral', 
        'Terra Cotta', 'Blush', 'Mauve', 'Cream'
    },
    'cool': {
        'Blue', 'Green', 'Purple', 'Turquoise', 'Silver', 'Navy', 'Midnight', 'Sapphire', 
        'Cobalt', 'Cerulean', 'Teal', 'Ice', 'Emerald', 'Forest', 'Olive', 'Sage', 'Moss', 
        'Mint', 'Jade', 'Amethyst', 'Plum', 'Lavender', 'Indigo'
    },
    'neutral': {
        'Black', 'White', 'Grey', 'Obsidian', 'Ebony', 'Charcoal', 'Slate', 'Graphite', 
        'Platinum', 'Alabaster', 'Ivory', 'Pearl', 'Taupe', 'Espresso', 'Sand', 'Birch'
    }
}

# --- SENIOR ART CRITIC VOCABULARY ---

FORMAL_STRUCTURES = {
    'abstract': [
        "negotiating the tension between rigid geometry and organic gesture",
        "utilizing expansive negative space to frame its central motif",
        "relying on asymmetrical balance to drive visual movement",
        "employing a flattened plane that emphasizes surface continuity",
        "distilling form into essential rhythmic iterations"
    ],
    'geometric': [
        "establishing a rigorous architectonic logic",
        "dividing the field through precise linear interventions",
        "exploring the interplay of repeating modular forms",
        "anchoring the composition with decisive structural weight"
    ],
    'expressionism': [
        "privileging gestural immediacy over calculated finish",
        "recording the physical velocity of the artist's hand",
        "building density through layered, frenetic mark-making"
    ]
}

COLOR_TEMPS = {
    'warm': [ 
        "radiating a saturated, thermal warmth",
        "grounded in earthy, resonant octaves",
        "smoldering with latent intensity",
        "projecting an optimistic, solar luminosity"
    ],
    'cool': [
        "maintaining a cool, atmospheric detachment",
        "evoking the clarity of northern light",
        "receding visually to create optical depth",
        "possessing a crisp, mineral serenity"
    ],
    'neutral': [
        "operating within a restrained, monochromatic discipline",
        "focusing on value contrast rather than chromatic complexity",
        "emphasizing the sculptural quality of light and shadow"
    ]
}

UNIFICATION_STRATEGIES = {
    'geometric': [
        "By introducing a consistent structural rhythm, it serves as an architectural anchor that organizes an open-plan space.",
        "The precise linearity provides a counterpoint to soft furnishings, tightening the overall design scheme.",
        "Its calculated maximizing of form brings an intellectual order to eclectically styled rooms."
    ],
    'minimalist': [
        "Acting as a moment of visual silence, it unifies disparately styled elements by providing a neutral focal point.",
        "The reductive composition centers the room, allowing surrounding textures to breathe without competition.",
        "Its quiet authority subtly aligns the room's energy, making it ideal for spaces demanding mental clarity."
    ],
    'expressionism': [
        "Serving as a dynamic chromatic pivot, it ties together accent colors from across the room into a single cohesive statement.",
        "The kinetic energy of the brushwork invigorates static interiors, bridging the gap between architecture and decor.",
        "It acts as a sophisticated disruption, breaking the monotony of a uniform palette to energize the viewing distance."
    ],
    'default': [
        "Its balanced composition allows it to bridge the gap between classic architectural details and modern furnishings.",
        "By harmonizing complex tones, it creates a sophisticated backdrop that unifies the room's color story.",
        "The work's commanding presence draws the eye, establishing a clear hierarchy within the interior layout."
    ]
}

COLOR_INTERACTION_STRATEGIES = {
    'warm': [
        "Specifically, the warm palette complements natural wood grains and brass hardware, enhancing the organic character of the room.",
        "These solar tones are particularly effective in north-facing rooms, compensating for the lack of direct natural light.",
        "The rich warmth interacts beautifully with leather upholstery and beige textiles, deepening the interior's cozy atmosphere."
    ],
    'cool': [
        "The cool tones offer a refreshing counterpoint to warm oak flooring or cream walls, preventing the scheme from feeling oversaturated.",
        "Ideally placed against white or light grey walls, the aquatics and cool hues expand the perceived volume of the room.",
        "This palette harmonizes effortlessly with modern chrome fixtures and glass surfaces, reinforcing a sleek, contemporary aesthetic."
    ],
    'neutral': [
        "The monochromatic scheme provides a grounding anchor in colorful rooms, preventing visual fatigue.",
        "Its neutrality allows it to absorb and reflect the changing ambient light of the day without clashing with seasonal decor changes.",
        "Functioning as a versatile foundation, it supports bold accent colors in pillows or rugs without competing for attention."
    ],
    'gold': [
        "The metallic elements catch ambient light to create a dynamic focal point that shifts throughout the day.",
        "These gilded tones introduce a layer of luxury that highlights other metallic finishes in lighting or furniture.",
        "Acting as a source of warmth, the gold accents breathe life into minimal, cool-toned interiors."
    ]
}

# --- GENERATOR LOGIC ---

def get_formal_phrase(styles_str):
    styles = [s.strip().lower() for s in styles_str.split(',')]
    for key in ['geometric', 'expressionism', 'minimalist']:
        for s in styles:
            if key in s and key in FORMAL_STRUCTURES:
                return random.choice(FORMAL_STRUCTURES[key])
    return random.choice(FORMAL_STRUCTURES['abstract'])

def get_color_category(c_name):
    if c_name in COLOR_CATEGORIES['warm']: return 'warm'
    if c_name in COLOR_CATEGORIES['cool']: return 'cool'
    if c_name in COLOR_CATEGORIES['neutral']: return 'neutral'
    # Fallback
    cn = c_name.lower()
    if any(x in cn for x in ['red', 'orange', 'yellow', 'gold', 'brown', 'pink']): return 'warm'
    if any(x in cn for x in ['blue', 'green', 'purple', 'silver', 'mint', 'cyan']): return 'cool'
    return 'neutral'

def get_color_temp_phrase(colors):
    if not colors: return "balancing tonal values with precision"
    
    top_colors = colors[:2]
    c_list = [c for c in colors]
    
    warm = sum(1 for c in c_list if get_color_category(c) == 'warm')
    cool = sum(1 for c in c_list if get_color_category(c) == 'cool')
    
    phrase = ""
    if warm > cool: phrase = random.choice(COLOR_TEMPS['warm'])
    elif cool > warm: phrase = random.choice(COLOR_TEMPS['cool'])
    else: phrase = random.choice(COLOR_TEMPS['neutral'])
    
    if len(top_colors) >= 2:
        return phrase + f", anchored by {top_colors[0]} and {top_colors[1]} tones"
    elif len(top_colors) == 1:
        return phrase + f", centered on a study of {top_colors[0]}"
    return phrase

def get_unification_phrase(styles_str):
    styles = [s.strip().lower() for s in styles_str.split(',')]
    if any('geometric' in s or 'pattern' in s for s in styles):
        return random.choice(UNIFICATION_STRATEGIES['geometric'])
    if any('minimalist' in s for s in styles):
        return random.choice(UNIFICATION_STRATEGIES['minimalist'])
    if any('expressionism' in s or 'abstract expressionism' in s for s in styles):
        return random.choice(UNIFICATION_STRATEGIES['expressionism'])
    return random.choice(UNIFICATION_STRATEGIES['default'])

def get_color_interaction_phrase(colors):
    if not colors: return random.choice(COLOR_INTERACTION_STRATEGIES['neutral'])
    
    if any(c in ['Gold', 'Brass', 'Bronze', 'Amber'] for c in colors):
        return random.choice(COLOR_INTERACTION_STRATEGIES['gold'])
        
    c_list = [c for c in colors]
    warm = sum(1 for c in c_list if get_color_category(c) == 'warm')
    cool = sum(1 for c in c_list if get_color_category(c) == 'cool')
    
    if warm > cool: return random.choice(COLOR_INTERACTION_STRATEGIES['warm'])
    elif cool > warm: return random.choice(COLOR_INTERACTION_STRATEGIES['cool'])
    return random.choice(COLOR_INTERACTION_STRATEGIES['neutral'])

def generate_refined_label(aw):
    styles = aw.get('styles') or 'Abstract'
    colors = aw.get('detected_colors', [])
    
    formal = get_formal_phrase(styles)
    temp = get_color_temp_phrase(colors)
    s1 = f"{formal.capitalize()}, this work is {temp}."
    
    unify = get_unification_phrase(styles)
    interact = get_color_interaction_phrase(colors)
    
    return f"{s1} {unify} {interact}"

# --- MAIN EXECUTION ---

target_collections = [
    'gold-collection',
    'blue-turquoise-collection',
    'oversized-statement-pieces',
    'sculpture-collection',
    'pattern-geometric',
    'minimalist-abstract',
    'neutral-tones'
]

count = 0
for slug in target_collections:
    if slug not in data: continue
    
    collection = data[slug]
    for aw in collection.get('artworks', []):
        
        current_desc = aw.get('description', '')
        personal_statement = ""
        dividers = ["Curator's Note:", "<strong>Curator's Note:</strong>"]
        
        for div in dividers:
            if div in current_desc:
                parts = current_desc.split(div)
                potential = parts[0]
                if "<hr" in potential: potential = potential.split("<hr")[0]
                potential = potential.strip()
                if len(potential) > 40: personal_statement = potential
                break
        
        wall_label = generate_refined_label(aw)
        
        final_desc = ""
        if personal_statement:
            final_desc = personal_statement + "\n\n" + "<hr style='width: 30px; border-top: 1px solid #ccc; margin: 15px 0;'>" + "\n\n"
        
        final_desc += f"Curator's Note: {wall_label}"
        aw['description'] = final_desc
        count += 1

with open(json_path, 'w') as f:
    json.dump(data, f, indent=4)

print(f"DONE. Refined {count} descriptions (V2 Palette Support).")
