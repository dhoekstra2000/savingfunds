from datetime import date
from decimal import Decimal, getcontext
from pathlib import Path

import click
from rich import print
from rich.markdown import Markdown

from dataloader import load_accounts_and_funds
from datasaver import save_funds_data, save_accounts_and_funds
from funds import Account, FundGroup, FixedEndFund, OpenEndFund, ManualFund
from reporting import print_account_tree, print_fund_tree, print_funds_table, print_savings_amounts_as_tree, print_savings_amounts_for_accounts, print_savings_report
from utils import moneyfmt


getcontext().prec = 10


@click.group()
@click.option('--file', default="./funds.yaml", type=click.Path())
@click.option('--dry-run', is_flag=True)
@click.pass_context
def cli(ctx, file, dry_run):
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
    ctx.obj['DRY_RUN'] = dry_run


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

    if not ctx.obj['DRY_RUN']:
        with open(ctx.obj['PATH'], "w") as file:
            save_funds_data(file, accounts, funds)

    print(f"Initialized new fund collection in '{ctx.obj['PATH']}'.")


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

    if not ctx.obj['DRY_RUN']:
        path = ctx.obj['PATH']
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, ctx.obj['FUNDS'])

    print(f"Added new account with key '{key}' and name '{name}'.")


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
    
    if not ctx.obj['DRY_RUN']:
        path = ctx.obj['PATH']
        accounts = ctx.obj['ACCOUNTS']
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Added new fund group with key '{key}' and name '{name}'.")


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
        
@cli.command()
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


@cli.command()
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


@cli.command()
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


@cli.command()
@click.argument("key")
@click.pass_context
def remove_fund(ctx, key):
    funds = ctx.obj['FUNDS']

    if not funds.contains_key(key):
        click.echo(f"There is no fund with key '{key}'.")
        raise SystemExit(1)
    
    try:
        funds.remove_fund_by_key(key)
    except Exception as e:
        print(e.args[0])
        raise SystemExit(1)
    
    if not ctx.obj['DRY_RUN']:
        path = ctx.obj['PATH']
        accounts = ctx.obj['ACCOUNTS']
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Removed fund with key '{key}'.")

@cli.command()
@click.argument("key")
@click.pass_context
def remove_account(ctx, key):
    accounts = ctx.obj['ACCOUNTS']

    if key not in accounts:
        click.echo(f"There is no account with key '{key}'.")
        raise SystemExit(1)
    
    account = accounts[key]
    if len(account.funds) > 0:
        click.echo(f"Account with key '{key}' still has registered funds to it.")
        raise SystemExit(1)
    
    del accounts[key]
    
    if not ctx.obj['DRY_RUN']:
        path = ctx.obj['PATH']
        funds = ctx.obj['FUNDS']
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Removed account with key '{key}'.")


@cli.command()
@click.argument("key", type=click.STRING)
@click.argument("amount", type=click.STRING)
@click.pass_context
def deposit(ctx, key, amount):
    funds = ctx.obj['FUNDS']
    
    if not funds.contains_key(key):
        click.echo(f"There is no fund with key '{key}'.")
        raise SystemExit(1)
    
    try:
        float(amount)
    except ValueError:
        click.echo("Passed amount is not a valid float.")
        raise SystemExit(1)
    
    amount = Decimal(amount)
    
    if amount <= 0:
        click.echo("The amount must be positive.")
        raise SystemExit(1)
    
    fund = funds.get_fund_by_key(key)
    fund.balance += amount

    if not ctx.obj['DRY_RUN']:
        path = ctx.obj['PATH']
        accounts = ctx.obj['ACCOUNTS']
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Deposited € {amount:.2f} to '{fund.name}'. New balance: € {fund.balance:.2f}.")


@cli.command()
@click.argument("key", type=click.STRING)
@click.argument("amount", type=click.STRING)
@click.pass_context
def withdraw(ctx, key, amount):
    funds = ctx.obj['FUNDS']
    
    if not funds.contains_key(key):
        click.echo(f"There is no fund with key '{key}'.")
        raise SystemExit(1)
    
    try:
        float(amount)
    except ValueError:
        click.echo("Passed amount is not a valid float.")
        raise SystemExit(1)
    
    amount = Decimal(amount)
    
    if amount <= 0:
        click.echo("The amount must be positive.")
        raise SystemExit(1)
    
    fund = funds.get_fund_by_key(key)
    
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


@cli.command()
@click.pass_context
def funds_table(ctx):
    funds = ctx.obj['FUNDS']
    print_funds_table(funds)


@cli.command()
@click.option("--when", default=date.today().isoformat(), type=click.DateTime(["%Y-%m-%d"]))
@click.pass_context
def total_daily_saving_rate(ctx, when):
    when = when.date()
    funds = ctx.obj['FUNDS']
    tdsr = funds.daily_saving_rate(when)

    print(f"Total daily saving rate: € {moneyfmt(tdsr, 4)}")


@cli.command()
@click.option("--when", default=date.today().isoformat(), type=click.DateTime(["%Y-%m-%d"]))
@click.argument("amount", type=click.STRING)
@click.pass_context
def distribute_extra(ctx, when, amount):
    when = when.date()
    
    try:
        float(amount)
    except ValueError:
        click.echo("Passed amount is not a valid float.")
        raise SystemExit(1)
    
    amount = Decimal(amount)
    
    if amount <= 0:
        click.echo("The amount must be positive.")
        raise SystemExit(1)
    
    funds = ctx.obj['FUNDS']
    
    amounts, remainder = funds.distribute_extra_savings(when, amount)

    markdown = f"""
Distributing extra amount: € {amount:.2f}

Remaining amount: € {remainder:.2f}
"""

    accounts = ctx.obj['ACCOUNTS']
    if amount != remainder:
        print_savings_report(accounts, funds, amounts, Markdown(markdown))
    else:
        print("No funds to fill!")

    if not ctx.obj['DRY_RUN']:  
        path = ctx.obj['PATH']
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)


@cli.command()
@click.option("--when", default=date.today().isoformat(), type=click.DateTime(["%Y-%m-%d"]))
@click.argument("key", type=click.STRING)
@click.argument("amount", type=click.STRING)
@click.pass_context
def distribute_interest(ctx, when, key, amount):
    when = when.date()

    accounts = ctx.obj['ACCOUNTS']

    if key not in accounts:
        click.echo(f"Account with key '{key}' not found.")
        raise SystemExit(1)
    
    try:
        float(amount)
    except ValueError:
        click.echo("Passed amount is not a valid float.")
        raise SystemExit(1)
    
    amount = Decimal(amount)
    
    if amount <= 0:
        click.echo("The amount must be positive.")
        raise SystemExit(1)
    
    account = accounts[key]
    amounts, remainder = account.distribute_interest(when, amount)

    funds = ctx.obj['FUNDS']
    if remainder != amount:
        print(f"Distributing interest of account '{account.name}' as follows:")
        print_savings_amounts_as_tree(funds, amounts)
    else:
        print(f"No accounts to distribute to.")

    print(f"Remaining interest: € {remainder:.2f}.")

    if not ctx.obj['DRY_RUN']:  
        path = ctx.obj['PATH']
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)


@cli.command()
@click.argument("year", type=click.INT)
@click.argument("month", type=click.IntRange(min=1, max=12))
@click.argument("amount", type=click.STRING)
@click.pass_context
def distribute_monthly(ctx, year, month, amount):
    try:
        float(amount)
    except ValueError:
        click.echo("Passed amount is not a valid float.")
        raise SystemExit(1)
    
    amount = Decimal(amount)
    
    if amount <= 0:
        click.echo("The amount must be positive.")
        raise SystemExit(1)
    
    funds = ctx.obj['FUNDS']

    minimal_monthly_amounts = {f: f.get_minimal_monthly_amount(year, month) for f in funds.funds.values()}
    total_mma = sum(minimal_monthly_amounts.values())
    amounts, remainder, deficit = funds.distribute_monthly_savings_tld(year, month, amount)
    markdown = f"""
Distributing monthly amount: € {amount:.2f}
Month and year: {str(month):0>2}-{year}

Minimal monthly amount: € {moneyfmt(total_mma)}

Minimal monthly amount per tranche:
"""
    markdown += '\n'.join([
        f"+ {f.name}: € {moneyfmt(v)}" for f, v in minimal_monthly_amounts.items()
        if v > Decimal(0)
        ]) + "\n"
    if remainder > 0:
        markdown += f"\nRemainder: € {moneyfmt(remainder)}"
    elif deficit > 0:
        markdown += f"\n**Deficit: € {moneyfmt(deficit)}**"
    accounts = ctx.obj['ACCOUNTS']
    print_savings_report(accounts, funds, amounts, Markdown(markdown))

    if not ctx.obj['DRY_RUN']:  
        path = ctx.obj['PATH']
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

if __name__ == '__main__':
    cli()
