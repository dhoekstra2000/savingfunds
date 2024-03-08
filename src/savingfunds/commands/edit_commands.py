from decimal import Decimal

import click
from schwifty import IBAN
from schwifty.exceptions import SchwiftyException

from savingfunds.commands.utils import (
    validate_amount,
    validate_existing_account_key,
    validate_existing_fund_key,
    validate_fund_type,
)
from savingfunds.datasaver import save_accounts_and_funds
from savingfunds.funds import (
    AccountFund,
    BalanceFund,
    FixedEndFund,
    Fund,
    FundGroup,
    OpenEndFund,
    TargetFund,
)


@click.command()
@click.argument("key", type=click.STRING)
@click.argument("balance", type=click.STRING)
@click.pass_context
def set_balance(ctx, key, balance):
    """Set the balance of a fund."""
    funds = ctx.obj["FUNDS"]

    validate_existing_fund_key(funds, key)

    balance = validate_amount(balance)

    fund = funds.get_fund_by_key(key)
    validate_fund_type(fund, BalanceFund)

    fund.balance = balance

    if not ctx.obj["DRY_RUN"]:
        path = ctx.obj["PATH"]
        accounts = ctx.obj["ACCOUNTS"]
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Set balance of fund '{fund.name}' to € {balance:.2f}.")


@click.command()
@click.argument("key", type=click.STRING)
@click.argument("name", type=click.STRING)
@click.pass_context
def rename_fund(ctx, key, name):
    """Rename a fund."""
    funds = ctx.obj["FUNDS"]
    validate_existing_fund_key(funds, key)

    fund = funds.get_fund_by_key(key)
    validate_fund_type(fund, Fund)
    old_name = fund.name
    fund.name = name

    if not ctx.obj["DRY_RUN"]:
        path = ctx.obj["PATH"]
        accounts = ctx.obj["ACCOUNTS"]
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Changed name of fund from '{old_name}' to '{name}'.")


@click.command()
@click.argument("key", type=click.STRING)
@click.argument("name", type=click.STRING)
@click.pass_context
def rename_account(ctx, key, name):
    """Rename an account."""
    accounts = ctx.obj["ACCOUNTS"]
    validate_existing_account_key(accounts, key)

    account = accounts["key"]
    old_name = account.name
    account.name = name

    if not ctx.obj["DRY_RUN"]:
        path = ctx.obj["PATH"]
        funds = ctx.obj["FUNDS"]
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Changed name of account from '{old_name}' to '{name}'.")


@click.command()
@click.argument("key", type=click.STRING)
@click.argument("target", type=click.STRING)
@click.pass_context
def change_target(ctx, key, target):
    """Change the target of a fund with a target."""
    funds = ctx.obj["FUNDS"]

    validate_existing_fund_key(funds, key)

    target = validate_amount(target)

    fund = funds.get_fund_by_key(key)
    validate_fund_type(fund, TargetFund)

    fund.target = target

    if not ctx.obj["DRY_RUN"]:
        path = ctx.obj["PATH"]
        accounts = ctx.obj["ACCOUNTS"]
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Changed target of fund '{fund.name}' to € {target:.2f}.")


@click.command()
@click.argument("key", type=click.STRING)
@click.argument("target_date", type=click.DateTime(formats=["%Y-%m-%d"]))
@click.pass_context
def change_target_date(ctx, key, target_date):
    """Change the target date of a fixed end fund."""
    target_date = target_date.date()

    funds = ctx.obj["FUNDS"]
    validate_existing_fund_key(funds, key)

    fund = funds.get_fund_by_key(key)
    validate_fund_type(fund, FixedEndFund)

    fund.target_date = target_date

    if not ctx.obj["DRY_RUN"]:
        path = ctx.obj["PATH"]
        accounts = ctx.obj["ACCOUNTS"]
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Changed target date of fund '{fund.name}' to {target_date}.")


@click.command()
@click.argument("key", type=click.STRING)
@click.argument("days", type=click.IntRange(0))
@click.pass_context
def change_saving_days(ctx, key, days):
    """Change the number of saving days for an open end fund"""
    funds = ctx.obj["FUNDS"]
    validate_existing_fund_key(funds, key)

    fund = funds.get_fund_by_key(key)
    validate_fund_type(fund, OpenEndFund)

    fund.days = days

    if not ctx.obj["DRY_RUN"]:
        path = ctx.obj["PATH"]
        accounts = ctx.obj["ACCOUNTS"]
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Changed saving days of fund '{fund.name}' to {days}.")


@click.command()
@click.argument("key", type=click.STRING)
@click.argument("factor", type=click.STRING)
@click.pass_context
def change_monthly_factor(ctx, key, factor):
    """Change the monthly surplus factor of a fundgroup."""
    funds = ctx.obj["FUNDS"]
    validate_existing_fund_key(funds, key)

    factor = validate_amount(factor)
    if factor < Decimal(1):
        click.echo("Factor must be at least 1.")
        raise SystemExit(1)

    fund = funds.get_fund_by_key(key)
    validate_fund_type(fund, FundGroup)

    fund.monthly_factor = factor

    if not ctx.obj["DRY_RUN"]:
        path = ctx.obj["PATH"]
        accounts = ctx.obj["ACCOUNTS"]
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(
        f"Monthly factor of fund group '{fund.name}' is set to {str(factor)}."
    )


@click.command()
@click.argument("key", type=click.STRING)
@click.argument("account_key", type=click.STRING)
@click.pass_context
def change_account(ctx, key, account_key):
    """Change the account of a fund."""
    funds = ctx.obj["FUNDS"]
    validate_existing_fund_key(funds, key)

    accounts = ctx.obj["ACCOUNTS"]
    validate_existing_account_key(accounts, account_key)

    fund = funds.get_fund_by_key(key)
    validate_fund_type(fund, AccountFund)

    account = accounts[account_key]
    fund.account.funds.pop(key)
    fund.account = account
    account.funds[key] = fund

    if not ctx.obj["DRY_RUN"]:
        path = ctx.obj["PATH"]
        accounts = ctx.obj["ACCOUNTS"]
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Changed account of fund '{fund.name}' to '{account.name}'.")


@click.command()
@click.argument("key", type=click.STRING)
@click.argument("parent_key", type=click.STRING)
@click.pass_context
def change_parent_group(ctx, key, parent_key):
    """Change the parent fund group of a fund."""
    funds = ctx.obj["FUNDS"]
    validate_existing_fund_key(funds, key)
    validate_existing_fund_key(funds, parent_key)

    new_parent_fund = funds.get_fund_by_key(parent_key)
    validate_fund_type(new_parent_fund, FundGroup)

    fund = funds.get_fund_by_key(key)
    if key == "root":
        validate_fund_type(fund, FundGroup)

    funds.remove_fund_by_key(key)
    new_parent_fund.funds[fund.key] = fund

    if not ctx.obj["DRY_RUN"]:
        path = ctx.obj["PATH"]
        accounts = ctx.obj["ACCOUNTS"]
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Changed parent of fund '{fund.name}' to '{new_parent_fund.name}'")


@click.command()
@click.argument("key", type=click.STRING)
@click.argument("iban", type=click.STRING)
@click.pass_context
def change_iban(ctx, key, iban):
    """Change the IBAN of an account."""
    accounts = ctx.obj["ACCOUNTS"]
    validate_existing_account_key(accounts, key)

    try:
        iban = IBAN(iban)
    except SchwiftyException as e:
        print(f"Problem with IBAN: {e.args[0]}")
        raise SystemExit(1)

    account = accounts[key]
    account.iban = iban

    if not ctx.obj["DRY_RUN"]:
        path = ctx.obj["PATH"]
        funds = ctx.obj["FUNDS"]
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Changed IBAN of '{account.name}' to '{iban.formatted}'.")


@click.command()
@click.argument("key", type=click.STRING)
@click.argument("comments", type=click.STRING)
@click.pass_context
def change_comments(ctx, key, comments):
    """Change the comments of an account."""
    accounts = ctx.obj["ACCOUNTS"]
    validate_existing_account_key(accounts, key)

    account = accounts[key]
    account.comments = comments

    if not ctx.obj["DRY_RUN"]:
        path = ctx.obj["PATH"]
        funds = ctx.obj["FUNDS"]
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Changed comment of '{account.name}' to:\n{comments}")
