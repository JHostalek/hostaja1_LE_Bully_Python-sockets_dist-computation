class Address:
    def __init__(self, address: tuple):
        self.address = address
        self.ip = address[0]
        self.port = address[1]
        self.id = self.ip

    def __eq__(self, other):
        return self.ip == other.ip and self.port == other.port

    def __hash__(self):
        return hash((self.ip, self.port))

    def __str__(self):
        return f"{self.ip}:{self.port}"

    def __repr__(self):
        return self.__str__()
