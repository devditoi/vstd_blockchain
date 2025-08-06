import ipaddress

def is_valid_origin(origin) -> tuple[str, int] | None:
    """Validate origin format and return (ip, port) tuple or None if invalid."""
    try:
        if not isinstance(origin, str):
            print(f"[DEBUG] Invalid origin type: {type(origin)}, value: {origin}")
            return None
            
        ip_str, port_str = origin.split(":")
        ipaddress.ip_address(ip_str)  # Raise ValueError nếu IP không hợp lệ
        port = int(port_str)
        if not (0 <= port <= 65535):
            print(f"[DEBUG] Invalid port: {port}")
            return None
        return ip_str, port
    except ValueError as e:
        print(f"[DEBUG] Origin validation failed: {origin}, error: {e}")
        return None