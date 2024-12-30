import struct
import numpy as np

def generate_random_events(events, parameters):
    # Generate a NumPy array of random floats
    events = np.random.rand(events, parameters) * 1024  # Scale to 0-1024
    return events

def create_fcs32_template(filename):
    # Initial header with placeholders
    header = (
        "FCS3.2    "  # FCS version
        "        "  # Text start
        "        "  # Text end
        "        "  # Data start
        "        "  # Data end
        "        "  # Analysis start
        "        "  # Analysis end
    )

    # Example values for the text segment
    num_events = 1000  # Total number of events (EDIT)
    num_parameters = 3  # Number of measurements per event (EDIT?)
    random_events = generate_random_events(num_events, num_parameters)
    random_events_list = random_events.tolist()

    # Placeholder for TEXT segment with newline characters for readability
    text_segment = (
        "$BEGINDATA878"
        "$ENDDATA12877"
        "$BEGINSTEXT257"
        "$ENDSTEXT877"
        "$BYTEORD1,2,3,4"
        "$CELLSDROPLETS"
        "$CYTFADS"
        "$DATATYPEF"
        "$EXPTobias Wenzel"
        "INSTIIBM"
        "$NEXTDATA0"
        f"$PAR{num_parameters}"
        f"$TOT{num_events}"

        "$P1B32"
        "P1DETSP1"
        "$P1E0.0"
        "$P1FEATUREArea"
        f"P1G0" #Edit
        "P1L405"
        "$P1Npeak1"
        f"$P1O0" #Edit
        "$P1R1024"
        "$P1TPM3315-WL SiPM"
        "$P1TAGDAPI"
        "$P1TYPERaw Fluorescence"
        f"$P1V0" #Edit

        "$P2B32"
        "P2DETSP2"
        "$P2E0.0"
        "$P2FEATUREArea"
        f"P2G0" #Edit
        "P2L488"
        "$P2Npeak2"
        f"$P2O0" #Edit
        "$P2R1024"
        "$P2TPM3315-WL SiPM"
        "$P2TAGGFP"
        "$P2TYPERaw Fluorescence"
        f"$P2V0" #Edit

        "$P3B32"
        "P3DETSP3"
        "$P3E0.0"
        "$P3FEATUREArea"
        f"P3G0" #Edit
        "P3L638"
        "$P3Npeak3"
        f"$P3O0" #Edit
        "$P3R1024"
        "$P3TPM3315-WL SiPM"
        "$P3TAGActin" #Maybe?
        "$P1TYPERaw Fluorescence"
        f"$P3V0" #Edit
    )

    # Example data for the DATA segment
    data = random_events_list

    # Pack the data into binary format
    data_segment = b''.join(struct.pack('fff', *event) for event in data)

    # Placeholder for ANALYSIS segment (empty in this example)
    analysis_segment = b''

    # Calculate positions
    text_start = 257  # Start after the header
    text_end = text_start + len(text_segment) - 1
    data_start = text_end + 1
    data_end = data_start + len(data_segment) - 1
    analysis_start = 0  # Not used in this example
    analysis_end = 0    # Not used in this example

    # Update header with correct positions and pad to 256 bytes
    header = (
        f"FCS3.2    "  # FCS version
        f"{text_start: 8d}"     # Text start position
        f"{text_end: 8d}"       # Text end position
        f"{data_start: 8d}"     # Data start position
        f"{data_end: 8d}"       # Data end position
        f"{analysis_start: 8d}" # Analysis start (optional)
        f"{analysis_end: 8d}"   # Analysis end (optional)
    ).ljust(256, ' ')           # Ensure the header is 256 bytes

    # Write to file
    with open(filename, 'wb') as f:
        f.write(header.encode('ascii'))
        f.write(text_segment.encode('ascii'))
        f.write(data_segment)
        f.write(analysis_segment)

# Usage
create_fcs32_template('template.fcs')