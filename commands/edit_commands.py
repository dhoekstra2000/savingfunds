from decimal import Decimal

import click

from datasaver import save_accounts_and_funds
from funds import FundGroup


@click.command()
@click.argument("key", type=click.STRING)
@click.argument("balance", type=click.STRING)
@click.pass_context
def set_balance(ctx, key, balance):
    funds = ctx.obj['FUNDS']
    
    if not funds.contains_key(key):
        click.echo(f"There is no fund with key '{key}'.")
        raise SystemExit(1)
    
    try:
        float(balance)
    except ValueError:
        click.echo("Passed balance is not a valid float.")
        raise SystemExit(1)
    
    balance = Decimal(balance)
    
    if balance <= 0:
        click.echo("The balance must be positive.")
        raise SystemExit(1)
    
    fund = funds.get_fund_by_key(key)
    if type(fund) is FundGroup:
        click.echo("Chosen fund does not own a balance.")
        raise SystemExit(1)
    
    fund.balance = balance

    if not ctx.obj['DRY_RUN']:
        path = ctx.obj['PATH']
        accounts = ctx.obj['ACCOUNTS']
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Set balance of fund '{fund.name}' to € {balance:.2f}.")


@click.command()
@click.argument("key", type=click.STRING)
@click.argument("target", type=click.STRING)
@click.pass_context
def change_target(ctx, key, target):
    funds = ctx.obj['FUNDS']
    
    if not funds.contains_key(key):
        click.echo(f"There is no fund with key '{key}'.")
        raise SystemExit(1)
    
    try:
        float(target)
    except ValueError:
        click.echo("Passed target is not a valid float.")
        raise SystemExit(1)
    
    target = Decimal(target)
    
    if target <= 0:
        click.echo("The target must be positive.")
        raise SystemExit(1)
    
    fund = funds.get_fund_by_key(key)
    if type(fund) is FundGroup:
        click.echo("Chosen fund does not own a balance.")
        raise SystemExit(1)
    
    fund.target = target

    if not ctx.obj['DRY_RUN']:
        path = ctx.obj['PATH']
        accounts = ctx.obj['ACCOUNTS']
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Changed target of fund '{fund.name}' to € {target:.2f}.")
