class Port:
    def __init__(self, number: str) -> None:
        self.number = number
        self.protocol = ""
        self.service_name = ""
        self.service_version = ""
        self.service_product = ""
        self.cpes: list[str] = []

    def update(self, info: dict) -> None:
        self.protocol = info.get('protocol', '')
        self.service_name = info.get('service_name', '')
        self.service_version = info.get('service_version', '')
        self.service_product = info.get('service_product', '')
        self.cpes = info.get('cpes', [])