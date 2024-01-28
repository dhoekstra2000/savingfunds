from decimal import Decimal

import click

from commands.utils import validate_existing_fund_key, validate_amount, validate_fund_type
from datasaver import save_accounts_and_funds
from funds import Fund, BalanceFund, TargetFund, FixedEndFund, OpenEndFund


@click.command()
@click.argument("key", type=click.STRING)
@click.argument("balance", type=click.STRING)
@click.pass_context
def set_balance(ctx, key, balance):
    funds = ctx.obj['FUNDS']
    
    validate_existing_fund_key(funds, key)
    
    balance = validate_amount(balance)
    
    fund = funds.get_fund_by_key(key)
    validate_fund_type(fund, BalanceFund)
    
    fund.balance = balance

    if not ctx.obj['DRY_RUN']:
        path = ctx.obj['PATH']
        accounts = ctx.obj['ACCOUNTS']
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Set balance of fund '{fund.name}' to € {balance:.2f}.")


@click.command()
@click.argument("key", type=click.STRING)
@click.argument("name", type=click.STRING)
@click.pass_context
def change_name(ctx, key, name):
    funds = ctx.obj['FUNDS']
    validate_existing_fund_key(funds, key)

    fund = funds.get_fund_by_key(key)
    validate_fund_type(fund, Fund)
    old_name = fund.name
    fund.name = name

    if not ctx.obj['DRY_RUN']:
        path = ctx.obj['PATH']
        accounts = ctx.obj['ACCOUNTS']
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Changed name of fund from '{old_name}' to '{name}'.")


@click.command()
@click.argument("key", type=click.STRING)
@click.argument("target", type=click.STRING)
@click.pass_context
def change_target(ctx, key, target):
    funds = ctx.obj['FUNDS']
    
    validate_existing_fund_key(funds, key)
    
    target = validate_amount(target)
    
    fund = funds.get_fund_by_key(key)
    validate_fund_type(fund, TargetFund)
    
    fund.target = target

    if not ctx.obj['DRY_RUN']:
        path = ctx.obj['PATH']
        accounts = ctx.obj['ACCOUNTS']
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Changed target of fund '{fund.name}' to € {target:.2f}.")


@click.command()
@click.argument("key", type=click.STRING)
@click.argument('target_date', type=click.DateTime(formats=['%Y-%m-%d']))
@click.pass_context
def change_target_date(ctx, key, target_date):
    target_date = target_date.date()

    funds = ctx.obj['FUNDS']
    validate_existing_fund_key(funds, key)

    fund = funds.get_fund_by_key(key)
    validate_fund_type(fund, FixedEndFund)

    fund.target_date = target_date

    if not ctx.obj['DRY_RUN']:
        path = ctx.obj['PATH']
        accounts = ctx.obj['ACCOUNTS']
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Changed target date of fund '{fund.name}' to {target_date}.")


@click.command()
@click.argument("key", type=click.STRING)
@click.argument("days", type=click.IntRange(0))
@click.pass_context
def change_saving_days(ctx, key, days):
    funds = ctx.obj['FUNDS']
    validate_existing_fund_key(funds, key)

    fund = funds.get_fund_by_key(key)
    validate_fund_type(fund, OpenEndFund)

    fund.days = days

    if not ctx.obj['DRY_RUN']:
        path = ctx.obj['PATH']
        accounts = ctx.obj['ACCOUNTS']
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Changed saving days of fund '{fund.name}' to {days}.")
