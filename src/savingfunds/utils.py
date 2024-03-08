import decimal
from decimal import Decimal
import random


def moneyfmt(value, places=2):
    q = Decimal(10) ** -places
    return str(value.quantize(q, decimal.ROUND_HALF_UP))


def dec_round(value, places=2):
    q = Decimal(10) ** -places
    return value.quantize(q, decimal.ROUND_HALF_UP)


def fix_overdistribution(amounts, amount, funds):
    amount_funds_left_sum = sum([amounts[k] for k in funds])
    if amount_funds_left_sum > amount:
        diff = amount_funds_left_sum - amount
        # Remove cents from random funds until no difference is left.
        for k in random.sample(funds, len(funds)):
            if amounts[k] >= diff:
                amounts[k] -= diff
                break
            else:
                amounts[k] -= Decimal("0.01")
                diff -= Decimal("0.01")
                if diff == Decimal(0):
                    break

    return amounts


def fix_underdistribution(amounts, amount, funds):
    amount_funds_left_sum = sum([amounts[k] for k in funds])
    if amount > amount_funds_left_sum:
        # Find fund to deposit extra randomly.
        diff = amount - amount_funds_left_sum
        k = random.sample(funds, len(funds))[0]
        amounts[k] += diff

    return amounts
