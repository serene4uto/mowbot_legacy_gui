import struct


cdr = b"\x00\x01\x00\x00\xd1\x10\xfcg1,\xf3-\x0e\x00\x00\x00gps_left_link\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfa\x02ZQ\x95\xbc\xef?\x80'DuAc\xc0?\xd8\xf0\xf4JY\x86\xa8?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00{\x14\xaeG\xe1z\x94?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\x1b\x9e^)\xcbp?\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

def decode_imu(data: bytes) -> dict:
    offset = 0
    # 1. Header
    # Read sequence number (even if not needed in the output)
    seq, = struct.unpack_from('<I', data, offset)
    offset += 4
    # Stamp seconds and nanoseconds
    stamp_sec, = struct.unpack_from('<I', data, offset)
    offset += 4
    stamp_nanosec, = struct.unpack_from('<I', data, offset)
    offset += 4
    # Frame id: first read the length (as a uint32)
    frame_id_len, = struct.unpack_from('<I', data, offset)
    offset += 4
    
    print(f"Frame ID length: {frame_id_len}")
    
    # Now read the frame_id string bytes (it is null-terminated within the length)
    frame_id_bytes = struct.unpack_from(f'<{frame_id_len}s', data, offset)[0]
    # Remove any trailing null bytes and decode as UTF-8
    frame_id = frame_id_bytes.rstrip(b'\x00').decode('utf-8')
    
    print(f"Frame ID bytes: {frame_id_bytes}")
    print(f"Frame ID: {frame_id}")
    
    offset += frame_id_len
    offset += (8-2) # TODO: unknown 6 bytes gap 

    print(f"Orientation x: {data[offset:offset+8]}")
    print(f"Orientation y: {data[offset+8:offset+16]}")
    print(f"Orientation z: {data[offset+16:offset+24]}")
    print(f"Orientation w: {data[offset+24:offset+32]}")
    
    # 2. Orientation (Quaternion: x, y, z, w)
    orientation = struct.unpack_from('<4d', data, offset)
    offset += 8 * 4
    
    # 3. Orientation covariance (9 doubles)
    orientation_covariance = struct.unpack_from('<9d', data, offset)
    offset += 8 * 9

    # 4. Angular velocity (Vector3: x, y, z)
    angular_velocity = struct.unpack_from('<3d', data, offset)
    offset += 8 * 3

    # 5. Angular velocity covariance (9 doubles)
    angular_velocity_covariance = struct.unpack_from('<9d', data, offset)
    offset += 8 * 9

    # 6. Linear acceleration (Vector3: x, y, z)
    linear_acceleration = struct.unpack_from('<3d', data, offset)
    offset += 8 * 3

    # 7. Linear acceleration covariance (9 doubles)
    linear_acceleration_covariance = struct.unpack_from('<9d', data, offset)
    offset += 8 * 9

    # Build the decoded message dictionary
    imu_msg = {
        'header': {
            'stamp': {
                'sec': stamp_sec,
                'nanosec': stamp_nanosec,
            },
            'frame_id': frame_id,
        },
        'orientation': {
            'x': orientation[0],
            'y': orientation[1],
            'z': orientation[2],
            'w': orientation[3],
        },
        'orientation_covariance': list(orientation_covariance),
        'angular_velocity': {
            'x': angular_velocity[0],
            'y': angular_velocity[1],
            'z': angular_velocity[2],
        },
        'angular_velocity_covariance': list(angular_velocity_covariance),
        'linear_acceleration': {
            'x': linear_acceleration[0],
            'y': linear_acceleration[1],
            'z': linear_acceleration[2],
        },
        'linear_acceleration_covariance': list(linear_acceleration_covariance),
    }

    return imu_msg



# print(cdr)

print(decode_imu(cdr))

test_bytes = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xfa\x02ZQ\x95\xbc\xef?\x80'DuAc\xc0?\xd8\xf0"

# for i, b in enumerate(test_bytes):
#     print(f"Byte {i}: {b:02x} (decimal: {b})")

# print(struct.unpack_from('<4d', test_bytes, 0))