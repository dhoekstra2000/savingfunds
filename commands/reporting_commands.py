from datetime import date

import click

from reporting import print_account_tree, print_fund_tree, print_funds_table
from utils import moneyfmt


@click.command("list-accounts")
@click.pass_context
def list_accounts(ctx):
    accounts = ctx.obj['ACCOUNTS']
    print_account_tree(accounts)


@click.command("list-funds")
@click.pass_context
def list_funds(ctx):
    funds = ctx.obj['FUNDS']
    print_fund_tree(funds)


@click.command()
@click.pass_context
def funds_table(ctx):
    funds = ctx.obj['FUNDS']
    print_funds_table(funds)


@click.command()
@click.option("--when", default=date.today().isoformat(), type=click.DateTime(["%Y-%m-%d"]))
@click.pass_context
def total_daily_saving_rate(ctx, when):
    when = when.date()
    funds = ctx.obj['FUNDS']
    tdsr = funds.daily_saving_rate(when)

    print(f"Total daily saving rate: € {moneyfmt(tdsr, 4)}")
