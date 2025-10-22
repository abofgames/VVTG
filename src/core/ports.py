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
