from decimal import Decimal

def moneyfmt(value, places=2):
    q = Decimal(10) ** -places
    sign, digits, exp = value.quantize(q).as_tuple()
    digits = list(map(str, digits))
    if digits == ['0']:
        return "0." + "0" * places
    if len(digits) == places:
        digits.insert(0, '0')
    digits.insert(len(digits) - places, '.')
    return ''.join(digits)
