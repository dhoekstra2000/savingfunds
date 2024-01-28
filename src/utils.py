from decimal import Decimal


def moneyfmt(value, places=2):
    q = Decimal(10) ** -places
    return str(value.quantize(q))
