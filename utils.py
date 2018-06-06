import socket


def inet_to_str(inet):
    """Convert inet object to a string

        Args:
            inet (inet struct): inet network address
        Returns:
            str: Printable/readable IP address
    """
    try:
        return socket.inet_ntop(socket.AF_INET, inet)
    except ValueError:
        return socket.inet_ntop(socket.AF_INET6, inet)


def str_to_inet(ip_addr):
    """Convert string to int ip

        Args:
            ip_addr: IP address as a string
        Returns:
            int: IP address in integer format
    """
    return socket.inet_aton(ip_addr)


def is_valid_ipv4_address(address):
    """Checks whatever address is valid IPv4 string

        Args:
            address: IP address as a string
        Returns:
            bool: True if address is valid IPv4
    """
    try:
        socket.inet_pton(socket.AF_INET, address)
    except AttributeError:  # no inet_pton here, sorry
        try:
            socket.inet_aton(address)
        except socket.error:
            return False
        return address.count('.') == 3
    except socket.error:  # not a valid address
        return False

    return True
