from datetime import date
from decimal import Decimal

import click
from rich import print
from rich.markdown import Markdown

from savingfunds.commands.utils import (
    validate_existing_account_key,
    validate_existing_fund_key,
)
from savingfunds.reporting import (
    print_account_details,
    print_account_tree,
    print_fund_details,
    print_fund_tree,
    print_funds_table,
)
from savingfunds.utils import moneyfmt


@click.command("list-accounts")
@click.pass_context
def list_accounts(ctx):
    """Print a tree of all the accounts."""
    accounts = ctx.obj["ACCOUNTS"]
    print_account_tree(accounts)


@click.command("list-funds")
@click.pass_context
def list_funds(ctx):
    """Print a tree of all the funds."""
    funds = ctx.obj["FUNDS"]
    print_fund_tree(funds)


@click.command()
@click.pass_context
def funds_table(ctx):
    """Print a table with all funds."""
    funds = ctx.obj["FUNDS"]
    print_funds_table(funds)


@click.command()
@click.option(
    "--when",
    default=date.today().isoformat(),
    type=click.DateTime(["%Y-%m-%d"]),
)
@click.pass_context
def total_daily_saving_rate(ctx, when):
    """Print the total daily saving rate on a given date."""
    when = when.date()
    funds = ctx.obj["FUNDS"]
    tdsr = funds.daily_saving_rate(when)

    print(f"Total daily saving rate: € {moneyfmt(tdsr, 4)}")


@click.command()
@click.pass_context
@click.argument("year", type=click.INT)
@click.argument("month", type=click.IntRange(min=1, max=12))
def monthly_amount(ctx, year, month):
    "Calculate the minimal monthly amount for the given month."
    funds = ctx.obj["FUNDS"]

    minimal_monthly_amounts = {
        f: f.get_minimal_monthly_amount(year, month)
        for f in funds.funds.values()
    }
    total_mma = sum(minimal_monthly_amounts.values())

    markdown = f"""
Month and year: {str(month):0>2}-{year}

Minimal monthly amount: € {moneyfmt(total_mma)}

Minimal monthly amount per tranche:
"""
    markdown += (
        "\n".join(
            [
                f"+ {f.name}: € {moneyfmt(v)}"
                for f, v in minimal_monthly_amounts.items()
                if v > Decimal(0)
            ]
        )
        + "\n"
    )

    print(Markdown(markdown))


@click.command()
@click.argument("key", type=click.STRING)
@click.pass_context
def fund_details(ctx, key):
    """Print the details of a given fund."""
    funds = ctx.obj["FUNDS"]
    validate_existing_fund_key(funds, key)

    fund = funds.get_fund_by_key(key)

    print_fund_details(fund)


@click.command()
@click.argument("key", type=click.STRING)
@click.pass_context
def account_details(ctx, key):
    """Print the details of a given account."""
    accounts = ctx.obj["ACCOUNTS"]
    validate_existing_account_key(accounts, key)

    account = accounts[key]

    print_account_details(account)
