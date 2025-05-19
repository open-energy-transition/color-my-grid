import jinja2
import re
import sys
import os
from typing import Dict, List, Tuple, Any

DEFAULT_VALUES = {
    # Node styling variables
    "basic_power_node_symbol_size_low": 3,
    "basic_power_node_symbol_size_mid": 5,
    "basic_power_node_symbol_size_high": 8,
    
    # Area styling variables
    "substation_area_width_low": 1,
    "substation_area_width_mid": 2,
    "substation_area_width_high": 3,
    "substation_default_color": "#FFFFFF",
    "substation_transmission_color": "#DC143C",
    "substation_distribution_color": "#008F11",
    
    "power_plant_area_width_low": 1,
    "power_plant_area_width_mid": 2,
    "power_plant_area_width_high": 3,
    "power_plant_color": "#000000",
    
    "power_generator_area_width_low": 1,
    "power_generator_area_width_mid": 2,
    "power_generator_area_width_high": 3,
    "power_generator_color": "#FFFF00",
    
    "industrial_area_width_low": 1,
    "industrial_area_width_mid": 2,
    "industrial_area_width_high": 3,
    
    # Line styling variables
    "line_cable_width_low": 2,
    "line_cable_width_mid": 3,
    "line_cable_width_high": 4,
    
    "line_busbar_bay_casing_width_low": 1,
    "line_busbar_bay_casing_width_mid": 2,
    "line_busbar_bay_casing_width_high": 3,
    
    "multi_circuit_line_left_casing_width_low": 1,
    "multi_circuit_line_left_casing_width_mid": 2,
    "multi_circuit_line_left_casing_width_high": 3,
}

DENSE_VALUES = {
    # Node styling variables
    "basic_power_node_symbol_size_low": 2,
    "basic_power_node_symbol_size_mid": 4,
    "basic_power_node_symbol_size_high": 6,
    
    # Area styling variables
    "substation_area_width_low": 0.5,
    "substation_area_width_mid": 1,
    "substation_area_width_high": 2,
    "substation_default_color": "#FFFFFF",
    "substation_transmission_color": "#DC143C",
    "substation_distribution_color": "#008F11",
    
    "power_plant_area_width_low": 0.5,
    "power_plant_area_width_mid": 1,
    "power_plant_area_width_high": 2,
    "power_plant_color": "#000000",
    
    "power_generator_area_width_low": 0.5,
    "power_generator_area_width_mid": 1,
    "power_generator_area_width_high": 2,
    "power_generator_color": "#FFFF00",
    
    "industrial_area_width_low": 0.5,
    "industrial_area_width_mid": 1,
    "industrial_area_width_high": 2,
    
    # Line styling variables
    "line_cable_width_low": 1,
    "line_cable_width_mid": 2,
    "line_cable_width_high": 3,
    
    "line_busbar_bay_casing_width_low": 0.5,
    "line_busbar_bay_casing_width_mid": 1,
    "line_busbar_bay_casing_width_high": 2,
    
    "multi_circuit_line_left_casing_width_low": 0.5,
    "multi_circuit_line_left_casing_width_mid": 1,
    "multi_circuit_line_left_casing_width_high": 2,
}

# Define default voltage rules
DEFAULT_VOLTAGE_RULES = [
    (0, 132000, "#deb887"),     
    (132001, 220000, "#FF7F50"),  
    (220001, 310000, "#cd5c5c"), 
    (310001, 550000, "#9400D3"), 
    (550001, 1000000, "#00ced1") 
]

# Define dense voltage rules
DENSE_VOLTAGE_RULES = [
    (0, 132000, "#deb887"),     
    (132001, 220000, "#FF7F50"),  
    (220001, 310000, "#cd5c5c"), 
    (310001, 550000, "#9400D3"), 
    (550001, 1000000, "#00ced1") 
]

# User-friendly descriptions for variable categories
FRIENDLY_DESCRIPTIONS = {
    "basic_power_node_symbol_size_low": "Size of power node symbols at low zoom levels",
    "basic_power_node_symbol_size_mid": "Size of power node symbols at medium zoom levels",
    "basic_power_node_symbol_size_high": "Size of power node symbols at high zoom levels",
    
    "substation_area_width_low": "Border width for substations at low zoom levels",
    "substation_area_width_mid": "Border width for substations at medium zoom levels",
    "substation_area_width_high": "Border width for substations at high zoom levels",
    "substation_default_color": "Default color for substations (hex code)",
    "substation_transmission_color": "Color for transmission substations (hex code)",
    "substation_distribution_color": "Color for distribution substations (hex code)",
    
    "power_plant_area_width_low": "Border width for power plants at low zoom levels",
    "power_plant_area_width_mid": "Border width for power plants at medium zoom levels",
    "power_plant_area_width_high": "Border width for power plants at high zoom levels",
    "power_plant_color": "Color for power plants (hex code)",
    
    "power_generator_area_width_low": "Border width for generators at low zoom levels",
    "power_generator_area_width_mid": "Border width for generators at medium zoom levels",
    "power_generator_area_width_high": "Border width for generators at high zoom levels",
    "power_generator_color": "Color for generators (hex code)",
    
    "industrial_area_width_low": "Border width for industrial areas at low zoom levels",
    "industrial_area_width_mid": "Border width for industrial areas at medium zoom levels",
    "industrial_area_width_high": "Border width for industrial areas at high zoom levels",
    
    "line_cable_width_low": "Width of power lines and cables at low zoom levels",
    "line_cable_width_mid": "Width of power lines and cables at medium zoom levels",
    "line_cable_width_high": "Width of power lines and cables at high zoom levels",
    
    "line_busbar_bay_casing_width_low": "Width of busbar and bay casings at low zoom levels",
    "line_busbar_bay_casing_width_mid": "Width of busbar and bay casings at medium zoom levels",
    "line_busbar_bay_casing_width_high": "Width of busbar and bay casings at high zoom levels",
    
    "multi_circuit_line_left_casing_width_low": "Width of multi-circuit line casings at low zoom levels",
    "multi_circuit_line_left_casing_width_mid": "Width of multi-circuit line casings at medium zoom levels",
    "multi_circuit_line_left_casing_width_high": "Width of multi-circuit line casings at high zoom levels",
}

def get_user_input_for_variable(var_name: str, default_value: Any) -> Any:
    """Get user input for a variable with a default value."""
    description = FRIENDLY_DESCRIPTIONS.get(var_name, var_name.replace("_", " ").title())
    prompt = f"📏 {description} (default: {default_value}): "
    user_input = input(prompt).strip()
    
    if not user_input:
        return default_value
    
    try:
        if isinstance(default_value, int):
            return int(user_input)
        elif isinstance(default_value, float):
            return float(user_input)
        else:
            return user_input
    except ValueError:
        print(f"❌ Oops! That doesn't look right. Using the default value: {default_value}")
        return default_value

def get_user_voltage_rules() -> List[Tuple[int, int, str]]:
    """Get user input for voltage rules."""
    voltage_rules = []
    
    print("\n🔌 Let's set up how different voltage levels will look on your map!")
    print("For each voltage range, you'll need to provide:")
    print("  • Lower voltage (in volts)")
    print("  • Upper voltage (in volts)")
    print("  • Line color (as a hex code like #FF0000)")
    print("Example: 0 1000 #7B7B7B would create a rule for 0-1000V lines in gray")
    print("Type 'done' when you've added all your voltage ranges")
    
    while True:
        try:
            user_input = input("\n⚡ Voltage rule (or 'done'): ")
            
            if user_input.lower() == 'done':
                break
            
            parts = user_input.split()
            if len(parts) != 3:
                print("❌ Hmm, that format doesn't look right. Please use: lower_voltage upper_voltage color")
                continue
            
            lower = int(parts[0])
            upper = int(parts[1])
            color = parts[2]
            
            voltage_rules.append((lower, upper, color))
            print(f"✅ Added rule: {lower}V to {upper}V in {color}")
        except ValueError as e:
            print(f"❌ Oops! {e}. Please try again.")
    
    return voltage_rules

def extract_vars_from_template(template_content: str) -> List[str]:
    """Extract all non-voltage variables from the template."""
    vars_pattern = r'{{([^{}]+?)}}'
    all_vars = re.findall(vars_pattern, template_content)
    
    non_voltage_vars = [
        var.strip() 
        for var in all_vars 
        if var.strip() not in ['lower_voltage', 'upper_voltage', 'line_color', 'line']
    ]
    
    unique_vars = []
    for var in non_voltage_vars:
        if var not in unique_vars:
            unique_vars.append(var)
    
    return unique_vars

def process_template(template_content: str, voltage_rules: List[Tuple[int, int, str]]) -> str:
    """Process the template to replace voltage rules and fix any syntax issues."""
    # Find sections between "/* Voltage-based styling..." and "/* Proposed and construction..."
    start_pattern = r'/\* Voltage-based styling with voltage labels for all lines/cables \*/'
    end_pattern = r'/\* Proposed and construction power lines \*/'
    
    start_match = re.search(start_pattern, template_content)
    end_match = re.search(end_pattern, template_content)
    
    if start_match and end_match:
        # Replace the entire section with our new voltage rules
        start_pos = start_match.start()
        end_pos = end_match.start()
        
        # Build new voltage rules
        new_rules = "/* Voltage-based styling with voltage labels for all lines/cables */\n"
        
        # Add main voltage rules
        for lower, upper, color in voltage_rules:
            new_rules += f"""
way[power=line][voltage>{lower}][voltage<={upper}] {{
    color: {color};
    z-index: 5;
}}

way[power=minor_line][voltage>{lower}][voltage<={upper}] {{
    color: {color};
    z-index: 5;
}}

way[power=cable][voltage>{lower}][voltage<={upper}] {{
    color: {color};
    z-index: 5;
}}

way|z18-[power=line][voltage>{lower}][voltage<={upper}] {{
    text: "voltage";
    text-color: black;
    font-size: 10;
    font-weight: bold;
    text-allow-overlap: true;
    text-opacity: 0.5;
    text-position: line;
}}
"""
        
        # Add circuit voltage coloring rules
        new_rules += "\n/* Circuit voltage coloring */\n"
        for lower, upper, color in voltage_rules:
            new_rules += f"""
way[power=line][circuits>1][voltage>{lower}][voltage<={upper}] {{
    left-casing-color: {color};
    right-casing-color: {color};
    z-index: 5;
}}

way[power=minor_line][circuits>1][voltage>{lower}][voltage<={upper}] {{
    left-casing-color: {color};
    right-casing-color: {color};
    z-index: 5;
}}

way[power=cable][circuits>1][voltage>{lower}][voltage<={upper}] {{
    left-casing-color: {color};
    right-casing-color: {color};
    z-index: 5;
}}
"""

        # Replace the section
        template_content = template_content[:start_pos] + new_rules + template_content[end_pos:]
    
    return template_content

def main():
    print("╔════════════════════════════════════════════════════════════╗")
    print("║ 🎨 Welcome to ColorMyMap! -  Power Grid Style Generator 🎨 ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print("Let's create a beautiful, customized MapCSS style for")
    print("mapping electrical transmission networks in JOSM.\n")
    
    # Check if template file exists
    if len(sys.argv) > 1:
        template_file = sys.argv[1]
    else:
        template_file = input("📄 Which template should we use? (default: oh_my_grid_template.mapcss): ").strip() or "oh_my_grid_template.mapcss"
    
    if not os.path.exists(template_file):
        print(f"❌ Hmm, I can't find the file '{template_file}'. Please check the path and try again.")
        return
    
    # Read template file
    with open(template_file, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Extract variables from template
    template_vars = extract_vars_from_template(template_content)
    print(f"\n🔍 I found {len(template_vars)} style variables in your template that we can customize!")
    
    # Ask user to choose between Default case, Dense case, or custom values
    print("\n🎨 First, let's choose a base style for your map:")
    print("  1️⃣  Default style - Optimized for normal grid density")
    print("  2️⃣  Dense network style - Better for areas with many power features")
    print("  3️⃣  Custom style - Customize each setting yourself")
    
    while True:
        try:
            choice = input("\n👉 Your choice (1-3): ").strip()
            if choice in ["1", "2", "3"]:
                choice = int(choice)
                break
            else:
                print("❌ Please enter 1, 2, or 3 to select a style.")
        except ValueError:
            print("❌ Please enter 1, 2, or 3 to select a style.")
    
    # Set values based on user choice
    if choice == 1:  
        values = DEFAULT_VALUES.copy()
        voltage_rules = DEFAULT_VOLTAGE_RULES
        print("\n✅ Great! Using the default style as a base.")
    elif choice == 2:  
        values = DENSE_VALUES.copy()
        voltage_rules = DENSE_VOLTAGE_RULES
        print("\n✅ Great! Using the dense network style as a base.")
    else: 
        values = DEFAULT_VALUES.copy()  
        print("\n✅ Custom style selected! Let's color your map exactly how you want it.")
        print("Just press Enter to keep the default value, or type a new value.")
        
        categories = {
            "Node styling 🏠": [var for var in template_vars if "node" in var],
            "Area styling 🔷": [var for var in template_vars if "area" in var or "substation" in var or "power_plant" in var or "power_generator" in var or "industrial" in var],
            "Line styling 📏": [var for var in template_vars if "line" in var or "cable" in var or "busbar" in var or "casing" in var],
            "Other settings 🛠️": [var for var in template_vars if not any(category in var for category in ["node", "area", "substation", "power_plant", "power_generator", "industrial", "line", "cable", "busbar", "casing"])]
        }
        
        for category, vars_in_category in categories.items():
            if vars_in_category:
                print(f"\n{category}")
                print("─" * 50)
                for var in vars_in_category:
                    if var in DEFAULT_VALUES:
                        values[var] = get_user_input_for_variable(var, DEFAULT_VALUES[var])
        
        print("\n🔌 Now, let's set up how different voltage levels will appear on your map.")
        custom_voltage_rules = get_user_voltage_rules()
        
        if custom_voltage_rules:
            voltage_rules = custom_voltage_rules
        else:
            print("ℹ️ No voltage rules provided. I'll use the default voltage rules.")
            voltage_rules = DEFAULT_VOLTAGE_RULES
    
    print("\n⚙️ Processing your template and adding the colors...")
    
    # Process the template to replace voltage rules and fix syntax issues
    processed_template = process_template(template_content, voltage_rules)
    
    # Apply the user-defined variable values with Jinja2
    jinja2_env = jinja2.Environment()
    template = jinja2_env.from_string(processed_template)
    result = template.render(**values)
    
    print("✅ Template processed successfully!")
    
    output_file = input(f"\n💾 What should I name your MapCSS file? (default: output_{os.path.basename(template_file)}): ").strip() or f"output_{os.path.basename(template_file)}"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print(f"\n🎉 Success! Your custom MapCSS file has been saved as '{output_file}'")
    print("You can now load this style in JOSM to enjoy your beautifully colored power grid map!")
    print("Thanks for using ColorMyMap! Happy mapping! 🗺️")

if __name__ == "__main__":
    main()