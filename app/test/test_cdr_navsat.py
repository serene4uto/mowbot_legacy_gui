import struct


def decode_navsatfix(data: bytes):
    offset = 4

    # 1) Decode Header
    #   a) stamp.sec (int32), stamp.nanosec (uint32)
    sec, = struct.unpack_from('<i', data, offset)
    offset += 4
    nanosec, = struct.unpack_from('<I', data, offset)
    offset += 4

    #   b) frame_id (string)
    #      Read length (including null terminator)
    # Read frame_id string length (includes null terminator)
    frame_id_len, = struct.unpack_from('<I', data, offset)
    offset += 4  # Move past the length field (4 bytes)
    # Extract the frame_id string (excluding null terminator)
    frame_id = data[offset:offset+frame_id_len-1].decode('utf-8')
    offset += frame_id_len  # Move past the string (including null terminator)
    # CDR alignment: strings with their length field must be aligned to 8-byte boundaries
    # Calculate required padding to reach next 8-byte boundary
    total_string_size = 4 + frame_id_len  # 4 bytes for length field + string bytes
    padding_bytes = (8 - (total_string_size % 8)) % 8  # Calculate needed padding (0-7 bytes)
    offset += padding_bytes  # Move past the padding
    
    print(f"Frame ID: {frame_id}, Length: {frame_id_len}, Padding: {padding_bytes}")

    # 3) NavSatStatus
    # status (int8)
    status_val, = struct.unpack_from('<b', data, offset)
    offset += 1
    # Align for next field if needed
    # Next field is uint16. It's 2-byte aligned. If offset is not even, pad by 1 byte.
    if offset % 2 != 0:
        offset += 1
    # service (uint16)
    service_val, = struct.unpack_from('<H', data, offset)
    offset += 2

    # 4) NavSatFix fields
    # latitude, longitude, altitude (each float64)
    latitude, longitude, altitude = struct.unpack_from('<ddd', data, offset)
    offset += 24  # 3 * 8 bytes

    # position_covariance (9 x float64)
    position_covariance = struct.unpack_from('<' + 'd'*9, data, offset)
    offset += 72  # 9 * 8 bytes

    # position_covariance_type (uint8)
    position_covariance_type, = struct.unpack_from('<B', data, offset)
    offset += 1
    # Since this is the last field, no need for special padding afterward

    # Construct a dictionary with the decoded data
    navsatfix_msg = {
        'header': {
            'stamp': {
                'sec': sec,
                'nanosec': nanosec
            },
            'frame_id': frame_id
        },
        'status': {
            'status': status_val,
            'service': service_val
        },
        'latitude': latitude,
        'longitude': longitude,
        'altitude': altitude,
        'position_covariance': list(position_covariance),
        'position_covariance_type': position_covariance_type
    }

    return navsatfix_msg

def decode_navsatfix2(data: bytes):
    offset = 0

    # 1) Skip 4-byte CDR encapsulation header (usually 00 01 00 00 for little-endian)
    # If your data does not have this header, remove these lines.
    offset += 4

    # 2) Decode Header
    # Header.stamp
    sec, = struct.unpack_from('<i', data, offset)
    offset += 4
    nanosec, = struct.unpack_from('<I', data, offset)
    offset += 4

    # Header.frame_id (string)
    frame_id_len, = struct.unpack_from('<I', data, offset)
    offset += 4
    frame_id = data[offset:offset+frame_id_len-1].decode('utf-8') # Exclude null terminator
    offset += frame_id_len
    # Align to 4-byte boundary after string
    pad = (4 - (frame_id_len % 4)) % 4
    # offset += pad
    
    print(f"Frame ID: {frame_id}, Length: {frame_id_len}")
    print(f"pad: {pad}")
    

    print(f"status bytes: {data[offset:offset+1]}")
    
    # 3) NavSatStatus
    # status (int8)
    status_val, = struct.unpack_from('<b', data, offset)
    offset += 1
    # Align for next field if needed
    print(f"service bytes: {data[offset:offset+2]}")
    # Next field is uint16. It's 2-byte aligned. If offset is not even, pad by 1 byte.
    if offset % 2 != 0:
        offset += 1
    # service (uint16)
    service_val, = struct.unpack_from('<H', data, offset)
    offset += 2
    
    print(f"status: {status_val}, service: {service_val}")
    
    offset+= 0

    # 4) NavSatFix fields
    # latitude, longitude, altitude (each float64)
    latitude, longitude, altitude = struct.unpack_from('<ddd', data, offset)
    offset += 24  # 3 * 8 bytes

    # position_covariance (9 x float64)
    position_covariance = struct.unpack_from('<' + 'd'*9, data, offset)
    offset += 72  # 9 * 8 bytes

    # position_covariance_type (uint8)
    position_covariance_type, = struct.unpack_from('<B', data, offset)
    offset += 1
    # Since this is the last field, no need for special padding afterward

    # Construct a dictionary with the decoded data
    navsatfix_msg = {
        'header': {
            'stamp': {
                'sec': sec,
                'nanosec': nanosec
            },
            'frame_id': frame_id
        },
        'status': {
            'status': status_val,
            'service': service_val
        },
        'latitude': latitude,
        'longitude': longitude,
        'altitude': altitude,
        'position_covariance': list(position_covariance),
        'position_covariance_type': position_covariance_type
    }

    return navsatfix_msg

cdr = b'\x00\x01\x00\x00\x83R\xfdgC\xa4\x1a\x16\t\x00\x00\x00imu_link\x00\x01\x00\x00\xcd_\xc5\xc0\x97\x0eB@\x92T\x16xc\r`@\xd9\xce\xf7S\xe3\xc5E@\xd4_u\x05W\xd4\x15@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x11a\xecR]\x83\x1d@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xb9]\x05\x84\x18`F@\x00\x00\x00\x00'
cdr2 = b'\x00\x01\x00\x00\xf9S\xfdg\xe6X4\x18\x0e\x00\x00\x00gps_left_link\x00\x02\x00\x00\x00\x00\x00q\x0c \xc6\x97\x0eB@\xd5\x16`Bc\r`@\xa1g\xb3\xeas\x85G@\xbb\x08S\x94K\xe3G?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00e*\xed\xa2"-9?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00T\x1b\x18P\xda\xe1p?\x00\x00\x00\x00'
print(decode_navsatfix2(cdr))