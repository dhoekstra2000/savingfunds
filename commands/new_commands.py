from decimal import Decimal

import click

from funds import Account, FundGroup, FixedEndFund, OpenEndFund, ManualFund, FundGroup
from datasaver import save_funds_data, save_accounts_and_funds


@click.command()
@click.argument('account_key', type=click.STRING)
@click.argument('account_name', type=click.STRING)
@click.argument('group_key', type=click.STRING)
@click.argument('group_name', type=click.STRING)
@click.pass_context
def init(ctx, account_key, account_name, group_key, group_name):
    acct = Account(account_key, account_name)
    group = FundGroup(group_key, group_name)

    accounts = [acct.to_dict()]
    funds = [group.to_dict()]

    if not ctx.obj['DRY_RUN']:
        with open(ctx.obj['PATH'], "w") as file:
            save_funds_data(file, accounts, funds)

    print(f"Initialized new fund collection in '{ctx.obj['PATH']}'.")


@click.command()
@click.argument('key', type=click.STRING)
@click.argument('name', type=click.STRING)
@click.pass_context
def new_account(ctx, key, name):
    accounts = ctx.obj['ACCOUNTS']

    if key in accounts:
        click.echo(f"Account with key '{key}' already exists.")
        raise SystemExit(1)

    new_account = Account(key, name)
    accounts[key] = new_account

    if not ctx.obj['DRY_RUN']:
        path = ctx.obj['PATH']
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, ctx.obj['FUNDS'])

    print(f"Added new account with key '{key}' and name '{name}'.")


@click.command()
@click.argument('parent_group_key', type=click.STRING)
@click.argument('key', type=click.STRING)
@click.argument('name', type=click.STRING)
@click.pass_context
def new_fund_group(ctx, parent_group_key, key, name):
    funds = ctx.obj['FUNDS']

    if funds.contains_key(key):
        click.echo(f"There already exists a fund with key '{key}'.")
        raise SystemExit(1)
    
    new_fund = FundGroup(key, name)

    if not funds.add_fund_to_group(new_fund, parent_group_key):
        click.echo(f"No fund group with key '{parent_group_key}' found.")
        raise SystemExit(1)
    
    if not ctx.obj['DRY_RUN']:
        path = ctx.obj['PATH']
        accounts = ctx.obj['ACCOUNTS']
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Added new fund group with key '{key}' and name '{name}'.")


@click.command()
@click.argument('parent_group_key', type=click.STRING)
@click.argument('key', type=click.STRING)
@click.argument('name', type=click.STRING)
@click.argument('account_key', type=click.STRING)
@click.argument('target', type=click.STRING)
@click.argument('target_date', type=click.DateTime(formats=['%Y-%m-%d']))
@click.pass_context
def new_fixed_end_fund(ctx, parent_group_key, key, name, account_key, target, target_date):
    path = ctx.obj['PATH']
    accounts = ctx.obj['ACCOUNTS']
    funds = ctx.obj['FUNDS']

    if account_key not in accounts.keys():
        click.echo(f"Account with key '{account_key}' not found.")
        raise SystemExit(1)

    if funds.contains_key(key):
        click.echo(f"There already exists a fund with key '{key}'.")
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

    target_date = target_date.date()

    new_fund = FixedEndFund(key, name, accounts[account_key], Decimal(0), target, target_date)

    if not funds.add_fund_to_group(new_fund, parent_group_key):
        click.echo(f"No fund group with key '{parent_group_key}' found.")
        raise SystemExit(1)

    if not ctx.obj['DRY_RUN']:
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"""
Added new fixed-end fund with the following data:
Key: {key}
Name: {name}
Target: € {target:.2f}
Target date: {target_date}
""")


@click.command()
@click.argument('parent_group_key', type=click.STRING)
@click.argument('key', type=click.STRING)
@click.argument('name', type=click.STRING)
@click.argument('account_key', type=click.STRING)
@click.argument('target', type=click.STRING)
@click.argument('days', type=click.INT)
@click.pass_context
def new_open_end_fund(ctx, parent_group_key, key, name, account_key, target, days):
    path = ctx.obj['PATH']
    accounts = ctx.obj['ACCOUNTS']
    funds = ctx.obj['FUNDS']

    if account_key not in accounts.keys():
        click.echo(f"Account with key '{account_key}' not found.")
        raise SystemExit(1)

    if funds.contains_key(key):
        click.echo(f"There already exists a fund with key '{key}'.")
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

    if days <= 0:
        click.echo("Days must be positive.")
        raise SystemExit(1)

    new_fund = OpenEndFund(key, name, accounts[account_key], Decimal(0), target, days)

    if not funds.add_fund_to_group(new_fund, parent_group_key):
        click.echo(f"No fund group with key '{parent_group_key}' found.")
        raise SystemExit(1)

    if not ctx.obj['DRY_RUN']:
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)
    
        print(f"""
Added new open-end fund with the following data:
Key: {key}
Name: {name}
Target: € {target:.2f}
Days: {days}
""")
        
@click.command()
@click.argument('parent_group_key', type=click.STRING)
@click.argument('key', type=click.STRING)
@click.argument('name', type=click.STRING)
@click.argument('account_key', type=click.STRING)
@click.pass_context
def new_manual_fund(ctx, parent_group_key, key, name, account_key):
    path = ctx.obj['PATH']
    accounts = ctx.obj['ACCOUNTS']
    funds = ctx.obj['FUNDS']

    if account_key not in accounts.keys():
        click.echo(f"Account with key '{account_key}' not found.")
        raise SystemExit(1)

    if funds.contains_key(key):
        click.echo(f"There already exists a fund with key '{key}'.")
        raise SystemExit(1)
    
    new_fund = ManualFund(key, name, accounts[account_key], Decimal(0))

    if not funds.add_fund_to_group(new_fund, parent_group_key):
        click.echo(f"No fund group with key '{parent_group_key}' found.")
        raise SystemExit(1)

    if not ctx.obj['DRY_RUN']:
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Added new manual fund with key '{key}' and name '{name}'.")
