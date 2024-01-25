from pathlib import Path

import click
from rich import print

from dataloader import load_accounts_and_funds
from datasaver import save_funds_data
from funds import Account, FundGroup
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
@click.argument('account_key')
@click.argument('account_name')
@click.argument('group_key')
@click.argument('group_name')
@click.pass_context
def init(ctx, account_key, account_name, group_key, group_name):
    acct = Account(account_key, account_name)
    group = FundGroup(group_key, group_name)

    accounts = [{ account_key: acct.to_dict() }]
    funds = [{ group_key: group.to_dict() }]

    with open(ctx.obj['PATH'], "w") as file:
        save_funds_data(file, accounts, funds)


if __name__ == '__main__':
    cli()
