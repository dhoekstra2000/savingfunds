import decimal
from decimal import Decimal


def moneyfmt(value, places=2):
    q = Decimal(10) ** -places
    return str(value.quantize(q, decimal.ROUND_HALF_UP))


def dec_round(value, places=2):
    q = Decimal(10) ** -places
    return value.quantize(q, decimal.ROUND_HALF_UP)
