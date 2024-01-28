from decimal import Decimal
from datetime import date

import click
from rich.markdown import Markdown

from commands.utils import validate_amount, validate_existing_account_key
from datasaver import save_accounts_and_funds
from reporting import print_savings_report, print_savings_amounts_as_tree
from utils import moneyfmt

@click.command()
@click.option("--when", default=date.today().isoformat(), type=click.DateTime(["%Y-%m-%d"]))
@click.argument("amount", type=click.STRING)
@click.pass_context
def distribute_extra(ctx, when, amount):
    when = when.date()
    
    amount = validate_amount(amount)
    
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


@click.command()
@click.option("--when", default=date.today().isoformat(), type=click.DateTime(["%Y-%m-%d"]))
@click.argument("key", type=click.STRING)
@click.argument("amount", type=click.STRING)
@click.pass_context
def distribute_interest(ctx, when, key, amount):
    when = when.date()

    accounts = ctx.obj['ACCOUNTS']

    validate_existing_account_key(accounts, key)
    
    amount = validate_amount(amount)
    
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


@click.command()
@click.argument("year", type=click.INT)
@click.argument("month", type=click.IntRange(min=1, max=12))
@click.argument("amount", type=click.STRING)
@click.pass_context
def distribute_monthly(ctx, year, month, amount):
    amount = validate_amount(amount)
    
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
