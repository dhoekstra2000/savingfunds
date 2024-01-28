from decimal import Decimal

import click


def validate_amount(amount):
    try:
        float(amount)
    except ValueError:
        click.echo("Passed amount is not a valid float.")
        raise SystemExit(1)
    
    amount = Decimal(amount)
    
    if amount <= 0:
        click.echo("The amount must be positive.")
        raise SystemExit(1)
    
    return amount


def validate_existing_account_key(accounts, key):
    if key not in accounts:
        click.echo(f"There is no account with key '{key}'.")
        raise SystemExit(1)


def validate_new_account_key(accounts, key):
    if key in accounts:
        click.echo(f"Account with key '{key}' already exists.")
        raise SystemExit(1)


def validate_existing_fund_key(funds, key):
    if not funds.contains_key(key):
        click.echo(f"There is no fund with key '{key}'.")
        raise SystemExit(1)

def validate_new_fund_key(funds, key):
    if funds.contains_key(key):
        click.echo(f"There already exists a fund with key '{key}'.")
        raise SystemExit(1)
    

def validate_fund_type(fund, T):
    if not isinstance(fund, T):
        click.echo(f"The fund does not have the right type.")
        raise SystemExit(1)
