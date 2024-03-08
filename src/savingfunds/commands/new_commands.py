from decimal import Decimal

import click

from savingfunds.commands.utils import (
    validate_amount,
    validate_existing_account_key,
    validate_new_account_key,
    validate_new_fund_key,
)
from savingfunds.datasaver import save_accounts_and_funds, save_funds_data
from savingfunds.funds import (
    Account,
    FixedEndFund,
    FundGroup,
    ManualFund,
    OpenEndFund,
)


@click.command()
@click.argument("account_key", type=click.STRING)
@click.argument("account_name", type=click.STRING)
@click.argument("group_key", type=click.STRING)
@click.argument("group_name", type=click.STRING)
@click.pass_context
def init(ctx, account_key, account_name, group_key, group_name):
    """Initialize a new file for saving funds."""
    acct = Account(account_key, account_name)
    group = FundGroup(group_key, group_name)

    accounts = [acct.to_dict()]
    funds = [group.to_dict()]

    if not ctx.obj["DRY_RUN"]:
        with open(ctx.obj["PATH"], "w") as file:
            save_funds_data(file, accounts, funds)

    print(f"Initialized new fund collection in '{ctx.obj['PATH']}'.")


@click.command()
@click.argument("key", type=click.STRING)
@click.argument("name", type=click.STRING)
@click.pass_context
def new_account(ctx, key, name):
    """Add a new account to the program."""
    accounts = ctx.obj["ACCOUNTS"]

    validate_new_account_key(accounts, key)

    new_account = Account(key, name)
    accounts[key] = new_account

    if not ctx.obj["DRY_RUN"]:
        path = ctx.obj["PATH"]
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, ctx.obj["FUNDS"])

    print(f"Added new account with key '{key}' and name '{name}'.")


@click.command()
@click.argument("parent_group_key", type=click.STRING)
@click.argument("key", type=click.STRING)
@click.argument("name", type=click.STRING)
@click.pass_context
def new_fund_group(ctx, parent_group_key, key, name):
    """Add a new fund group."""
    funds = ctx.obj["FUNDS"]

    validate_new_fund_key(funds, key)

    new_fund = FundGroup(key, name)

    if not funds.add_fund_to_group(new_fund, parent_group_key):
        click.echo(f"No fund group with key '{parent_group_key}' found.")
        raise SystemExit(1)

    if not ctx.obj["DRY_RUN"]:
        path = ctx.obj["PATH"]
        accounts = ctx.obj["ACCOUNTS"]
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Added new fund group with key '{key}' and name '{name}'.")


@click.command()
@click.argument("parent_group_key", type=click.STRING)
@click.argument("key", type=click.STRING)
@click.argument("name", type=click.STRING)
@click.argument("account_key", type=click.STRING)
@click.argument("target", type=click.STRING)
@click.argument("target_date", type=click.DateTime(formats=["%Y-%m-%d"]))
@click.pass_context
def new_fixed_end_fund(
    ctx, parent_group_key, key, name, account_key, target, target_date
):
    """Add a new fixed end fund."""
    path = ctx.obj["PATH"]
    accounts = ctx.obj["ACCOUNTS"]
    funds = ctx.obj["FUNDS"]

    validate_existing_account_key(accounts, account_key)

    validate_new_fund_key(funds, key)

    target = validate_amount(target)

    target_date = target_date.date()

    new_fund = FixedEndFund(
        key, name, accounts[account_key], Decimal(0), target, target_date
    )

    if not funds.add_fund_to_group(new_fund, parent_group_key):
        click.echo(f"No fund group with key '{parent_group_key}' found.")
        raise SystemExit(1)

    if not ctx.obj["DRY_RUN"]:
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(
        f"""
Added new fixed-end fund with the following data:
Key: {key}
Name: {name}
Target: € {target:.2f}
Target date: {target_date}
"""
    )


@click.command()
@click.argument("parent_group_key", type=click.STRING)
@click.argument("key", type=click.STRING)
@click.argument("name", type=click.STRING)
@click.argument("account_key", type=click.STRING)
@click.argument("target", type=click.STRING)
@click.argument("days", type=click.INT)
@click.pass_context
def new_open_end_fund(
    ctx, parent_group_key, key, name, account_key, target, days
):
    """Add a new open end fund."""
    path = ctx.obj["PATH"]
    accounts = ctx.obj["ACCOUNTS"]
    funds = ctx.obj["FUNDS"]

    validate_existing_account_key(accounts, account_key)

    validate_new_fund_key(funds, key)

    target = validate_amount(target)

    if days <= 0:
        click.echo("Days must be positive.")
        raise SystemExit(1)

    new_fund = OpenEndFund(
        key, name, accounts[account_key], Decimal(0), target, days
    )

    if not funds.add_fund_to_group(new_fund, parent_group_key):
        click.echo(f"No fund group with key '{parent_group_key}' found.")
        raise SystemExit(1)

    if not ctx.obj["DRY_RUN"]:
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

        print(
            f"""
Added new open-end fund with the following data:
Key: {key}
Name: {name}
Target: € {target:.2f}
Days: {days}
"""
        )


@click.command()
@click.argument("parent_group_key", type=click.STRING)
@click.argument("key", type=click.STRING)
@click.argument("name", type=click.STRING)
@click.argument("account_key", type=click.STRING)
@click.pass_context
def new_manual_fund(ctx, parent_group_key, key, name, account_key):
    """Add a new manual fund."""
    path = ctx.obj["PATH"]
    accounts = ctx.obj["ACCOUNTS"]
    funds = ctx.obj["FUNDS"]

    validate_existing_account_key(accounts, account_key)

    validate_new_fund_key(funds, key)

    new_fund = ManualFund(key, name, accounts[account_key], Decimal(0))

    if not funds.add_fund_to_group(new_fund, parent_group_key):
        click.echo(f"No fund group with key '{parent_group_key}' found.")
        raise SystemExit(1)

    if not ctx.obj["DRY_RUN"]:
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Added new manual fund with key '{key}' and name '{name}'.")
