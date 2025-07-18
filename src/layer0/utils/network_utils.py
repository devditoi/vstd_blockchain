import ipaddress

def is_valid_origin(origin) -> tuple[str, int] | None:
    try:
        ip_str, port_str = origin.split(":")
        ipaddress.ip_address(ip_str)  # Raise ValueError nếu IP không hợp lệ
        port = int(port_str)
        if not (0 <= port <= 65535):
            return None
        return ip_str, port
    except ValueError:
        return None