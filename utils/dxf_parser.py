import re
import ezdxf

def extract_parameters_from_dxf(file):
    try:
        doc = ezdxf.readfile(file)
        parameters = []
        
        # Updated pattern to match dimensions with optional spaces around "X"
        dimension_pattern = re.compile(r"(\d+\.\d+)\s*[xX]\s*(\d+\.\d+)", re.IGNORECASE)
        # Specific pattern to remove only "/P" occurrences
        cleanup_pattern = re.compile(r"\\P|[\\pxqc;]")

        for entity in doc.modelspace():
            if entity.dxftype() == 'TEXT' or entity.dxftype() == 'MTEXT':
                text_content = entity.dxf.text
                
                # Search for dimensions in text
                match = dimension_pattern.search(text_content)
                if match:
                    # Extract room name (text without dimensions)
                    room_name = re.sub(dimension_pattern, "", text_content).strip()
                    
                    # Apply cleanup to remove specific "/P"
                    room_name = cleanup_pattern.sub("", room_name)
                    
                    # Additional pattern to extract text between "H" values in curly braces
                    if "{" in room_name and "}" in room_name:
                        room_name = re.sub(r"\{H\d+\.\d+(.*?)H\d+\.\d+\}", r"\1", room_name).strip()

                    length, breadth = match.groups()

                    parameters.append({
                        'name': 'Room Name',
                        'value': room_name
                    })
                    parameters.append({
                        'name': 'Length (in Meters)',
                        'value': float(length)
                    })
                    parameters.append({
                        'name': 'Breadth (in Meters)',
                        'value': float(breadth)
                    })
                    parameters.append({
                        'name': 'Area (in Meter Sq.)',
                        'value': round(float(length) * float(breadth), 2)
                    })
                    parameters.append({
                        'name': 'Perimeter (in Meters)',
                        'value': round(2 * (float(length) + float(breadth)), 2)
                    })
                    parameters.append({
                        'name': 'Aspect Ratio',
                        'value': round(float(length) / float(breadth), 2)
                    })

        # print("Extracted Parameters:", parameters)  # Debugging print statement
        return parameters
    except Exception as e:
        print("Error reading DXF file:", e)
        return []
