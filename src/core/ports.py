import re

def extract(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Match the entity block
    entity_match = re.search(r'entity\s+\w+\s+is\s+.*?port\s*\((.*?)\);\s*end', content, re.DOTALL | re.IGNORECASE)
    if not entity_match:
        print("No entity port block found.")
        return []

    port_block = entity_match.group(1)

    # Split and clean individual port lines
    ports_in = {}
    ports_out = {}
    entity_name = []
    for line in port_block.split(';'):
        line = line.strip()
        if not line:
            continue
        # Match port name, direction, and type
        match = re.match(r'(\w+)\s*:\s*(in|out|inout|buffer)\s+(.*)', line, re.IGNORECASE)
        if match:
            name, direction, dtype = match.groups()
            if direction == 'in' and name != 'clk': ports_in[name] = dtype
            if direction == 'out': ports_out[name] = dtype

    match = re.search(r'entity\s+(\w+)\s+is', content, re.IGNORECASE)
    if match:
        entity_name = [match.group(1) , match.group(1) + "_tb"]

    out = [ports_in, ports_out, entity_name]

    return out


def extract_component_names(vhdl_file_path):
    """
    Extracts component names from a VHDL file by scanning for 'component <name>' declarations.

    Args:
        vhdl_file_path (str): Path to the VHDL file (e.g., 'system_top.vhd')

    Returns:
        List[str]: A list of component names found in the file
    """
    component_names = []
    pattern = re.compile(r'\bcomponent\s+(\w+)', re.IGNORECASE)

    try:
        with open(vhdl_file_path, 'r') as file:
            for line in file:
                match = pattern.search(line)
                if match:
                    component_names.append(match.group(1))
    except FileNotFoundError:
        print(f"File not found: {vhdl_file_path}")
    except Exception as e:
        print(f"Error reading file: {e}")

    return component_names
