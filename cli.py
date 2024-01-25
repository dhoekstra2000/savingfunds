from decimal import Decimal
from pathlib import Path

import click
from rich import print

from dataloader import load_accounts_and_funds
from datasaver import save_funds_data, save_accounts_and_funds
from funds import Account, FundGroup, FixedEndFund, OpenEndFund
from reporting import print_account_tree, print_fund_tree


@click.group()
@click.option('--file', default="./funds.yaml", type=click.Path())
@click.pass_context
def cli(ctx, file):
    ctx.ensure_object(dict)
    
    path = Path(file)
    
    if path.exists():
        with open(path, "r") as f:
            accounts, funds = load_accounts_and_funds(f)
        
        ctx.obj['FUNDS'] = funds
        ctx.obj['ACCOUNTS'] = accounts
    else:
        ctx.obj['FUNDS'] = {}
        ctx.obj['ACCOUNTS'] = {}
    
    ctx.obj['PATH'] = path


@cli.command("list-accounts")
@click.pass_context
def list_accounts(ctx):
    accounts = ctx.obj['ACCOUNTS']
    print_account_tree(accounts)


@cli.command("list-funds")
@click.pass_context
def list_funds(ctx):
    funds = ctx.obj['FUNDS']
    print_fund_tree(funds)


@cli.command("funds-dict")
@click.pass_context
def funds_dict(ctx):
    funds = ctx.obj['FUNDS']
    fd = [f.to_dict() for f in funds.values()]
    print(fd)


@cli.command("accounts-dict")
@click.pass_context
def accounts_dict(ctx):
    accounts = ctx.obj['ACCOUNTS']
    ad = [a.to_dict() for a in accounts.values()]

    print(ad)


@cli.command()
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

    with open(ctx.obj['PATH'], "w") as file:
        save_funds_data(file, accounts, funds)


@cli.command()
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

    path = ctx.obj['PATH']
    with open(path, "w") as file:
        save_accounts_and_funds(file, accounts, ctx.obj['FUNDS'])


@cli.command()
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
    
    path = ctx.obj['PATH']
    accounts = ctx.obj['ACCOUNTS']
    with open(path, "w") as file:
        save_accounts_and_funds(file, accounts, funds)


@cli.command()
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

    with open(path, "w") as file:
        save_accounts_and_funds(file, accounts, funds)


@cli.command()
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

    with open(path, "w") as file:
        save_accounts_and_funds(file, accounts, funds)


if __name__ == '__main__':
    cli()
