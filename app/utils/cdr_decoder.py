import struct

def decode_imu(data: bytes):
    # Skip the 4-byte CDR encapsulation header
    # Typically: 00 01 00 00 indicates little-endian CDR
    offset = 4

    # 1) Decode Header
    #   a) stamp.sec (int32), stamp.nanosec (uint32)
    sec, = struct.unpack_from('<i', data, offset)
    offset += 4
    nanosec, = struct.unpack_from('<I', data, offset)
    offset += 4

    #   b) frame_id (string)
    #      Read length (including null terminator)
    frame_id_len, = struct.unpack_from('<I', data, offset)
    offset += 4
    frame_id = data[offset:offset+frame_id_len-1].decode('utf-8')  # exclude null terminator
    offset += frame_id_len
    # Note: CDR strings are padded to 4-byte boundaries if needed.
    # Calculate padding:
    pad = (4 - (frame_id_len % 4)) % 4
    offset += pad

    # 2) orientation (4 x float64)
    orientation = struct.unpack_from('<dddd', data, offset)
    offset += 32  # 4 * 8 bytes = 32

    # 3) orientation_covariance (9 x float64)
    orientation_covariance = struct.unpack_from('<' + 'd'*9, data, offset)
    offset += 72  # 9 * 8 bytes = 72

    # 4) angular_velocity (3 x float64)
    angular_velocity = struct.unpack_from('<ddd', data, offset)
    offset += 24  # 3 * 8 bytes = 24

    # 5) angular_velocity_covariance (9 x float64)
    angular_velocity_covariance = struct.unpack_from('<' + 'd'*9, data, offset)
    offset += 72

    # 6) linear_acceleration (3 x float64)
    linear_acceleration = struct.unpack_from('<ddd', data, offset)
    offset += 24

    # 7) linear_acceleration_covariance (9 x float64)
    linear_acceleration_covariance = struct.unpack_from('<' + 'd'*9, data, offset)
    offset += 72

    # Build a dictionary to represent the decoded IMU message
    imu_msg = {
        'header': {
            'stamp': {
                'sec': sec,
                'nanosec': nanosec
            },
            'frame_id': frame_id
        },
        'orientation': {
            'x': orientation[0],
            'y': orientation[1],
            'z': orientation[2],
            'w': orientation[3]
        },
        'orientation_covariance': list(orientation_covariance),
        'angular_velocity': {
            'x': angular_velocity[0],
            'y': angular_velocity[1],
            'z': angular_velocity[2]
        },
        'angular_velocity_covariance': list(angular_velocity_covariance),
        'linear_acceleration': {
            'x': linear_acceleration[0],
            'y': linear_acceleration[1],
            'z': linear_acceleration[2]
        },
        'linear_acceleration_covariance': list(linear_acceleration_covariance)
    }

    return imu_msg


def decode_navsatfix(data: bytes):
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
    frame_id = data[offset:offset+frame_id_len-1].decode('utf-8')
    offset += frame_id_len
    # Align to 4-byte boundary after string
    pad = (4 - (frame_id_len % 4)) % 4
    offset += pad

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

def decode_sensorstatus(data: bytes):
    offset = 0

    # Skip 4-byte CDR encapsulation header
    offset += 4

    # Decode Header (std_msgs/Header)
    sec, = struct.unpack_from('<i', data, offset)
    offset += 4
    nanosec, = struct.unpack_from('<I', data, offset)
    offset += 4

    # frame_id (string)
    frame_id_len, = struct.unpack_from('<I', data, offset)
    offset += 4
    frame_id = data[offset:offset + frame_id_len - 1].decode('utf-8')
    offset += frame_id_len
    pad = (4 - (frame_id_len % 4)) % 4
    offset += pad

    # status array length
    status_len, = struct.unpack_from('<I', data, offset)
    offset += 4

    name_message_dict = {}

    for _ in range(status_len):
        # level (byte)
        level, = struct.unpack_from('<b', data, offset)
        offset += 1
        # Align to 4-byte boundary
        pad = (4 - (offset % 4)) % 4
        offset += pad

        # name (string)
        name_len, = struct.unpack_from('<I', data, offset)
        offset += 4
        name_str = data[offset:offset + name_len - 1].decode('utf-8')
        offset += name_len
        pad = (4 - (name_len % 4)) % 4
        offset += pad

        # message (string)
        message_len, = struct.unpack_from('<I', data, offset)
        offset += 4
        message_str = data[offset:offset + message_len - 1].decode('utf-8')
        offset += message_len
        pad = (4 - (message_len % 4)) % 4
        offset += pad

        # hardware_id (string)
        hardware_id_len, = struct.unpack_from('<I', data, offset)
        offset += 4
        hardware_id_str = data[offset:offset + hardware_id_len - 1].decode('utf-8')
        offset += hardware_id_len
        pad = (4 - (hardware_id_len % 4)) % 4
        offset += pad

        # values (KeyValue[])
        values_len, = struct.unpack_from('<I', data, offset)
        offset += 4

        # Skip parsing values since we only need name:message.
        for __ in range(values_len):
            # key (string)
            pad = (4 - (offset % 4)) % 4
            offset += pad
            key_len, = struct.unpack_from('<I', data, offset)
            offset += 4
            offset += key_len
            pad = (4 - (key_len % 4)) % 4
            offset += pad

            # value (string)
            pad = (4 - (offset % 4)) % 4
            offset += pad
            val_len, = struct.unpack_from('<I', data, offset)
            offset += 4
            offset += val_len
            pad = (4 - (val_len % 4)) % 4
            offset += pad

        # Add the name:message pair to our dictionary
        name_message_dict[name_str] = message_str

    return name_message_dict

