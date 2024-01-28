from decimal import Decimal

import click

from commands.utils import validate_amount, validate_existing_fund_key, validate_fund_type
from datasaver import save_accounts_and_funds
from funds import BalanceFund


@click.command()
@click.argument("key", type=click.STRING)
@click.argument("amount", type=click.STRING)
@click.pass_context
def deposit(ctx, key, amount):
    funds = ctx.obj['FUNDS']
    
    validate_existing_fund_key(funds, key)
    
    amount = validate_amount(amount)
    
    fund = funds.get_fund_by_key(key)
    validate_fund_type(fund, BalanceFund)
    
    fund.balance += amount

    if not ctx.obj['DRY_RUN']:
        path = ctx.obj['PATH']
        accounts = ctx.obj['ACCOUNTS']
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Deposited € {amount:.2f} to '{fund.name}'. New balance: € {fund.balance:.2f}.")


@click.command()
@click.argument("key", type=click.STRING)
@click.argument("amount", type=click.STRING)
@click.pass_context
def withdraw(ctx, key, amount):
    funds = ctx.obj['FUNDS']
    
    validate_existing_fund_key(funds, key)
    
    amount = validate_amount(amount)
    
    fund = funds.get_fund_by_key(key)
    validate_fund_type(fund, BalanceFund)
    
    if amount > fund.balance:
        click.echo(f"The amount is more than the balance (€ {fund.balance:.2f}). You cannot overdraw funds.")
        raise SystemExit(1)
    
    fund.balance -= amount

    if not ctx.obj['DRY_RUN']:  
        path = ctx.obj['PATH']
        accounts = ctx.obj['ACCOUNTS']
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Withdrawn € {amount:.2f} from '{fund.name}'. New balance: € {fund.balance:.2f}.")
