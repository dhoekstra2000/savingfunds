import click

from savingfunds.commands.utils import (
    validate_amount,
    validate_existing_fund_key,
    validate_fund_type,
)
from savingfunds.datasaver import save_accounts_and_funds
from savingfunds.funds import BalanceFund, TargetFund


@click.command()
@click.argument("key", type=click.STRING)
@click.argument("amount", type=click.STRING)
@click.pass_context
def deposit(ctx, key, amount):
    """Deposit money into a fund."""
    funds = ctx.obj["FUNDS"]

    validate_existing_fund_key(funds, key)

    amount = validate_amount(amount)

    fund = funds.get_fund_by_key(key)
    validate_fund_type(fund, BalanceFund)

    fund.balance += amount

    if not ctx.obj["DRY_RUN"]:
        path = ctx.obj["PATH"]
        accounts = ctx.obj["ACCOUNTS"]
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(
        f"Deposited € {amount:.2f} to '{fund.name}'."
        + f" New balance: € {fund.balance:.2f}."
    )


@click.command()
@click.argument("key", type=click.STRING)
@click.argument("amount", type=click.STRING)
@click.option("--lower-target", is_flag=True)
@click.pass_context
def withdraw(ctx, key, amount, lower_target):
    """Withdraw money from a fund."""
    funds = ctx.obj["FUNDS"]

    validate_existing_fund_key(funds, key)

    amount = validate_amount(amount)

    fund = funds.get_fund_by_key(key)
    validate_fund_type(fund, BalanceFund)

    if amount > fund.balance:
        click.echo(
            f"The amount is more than the balance (€ {fund.balance:.2f})."
            + " You cannot overdraw funds."
        )
        raise SystemExit(1)

    fund.balance -= amount

    if lower_target and not isinstance(fund, TargetFund):
        print(f"Warning: Fund '{fund.name}' does not have a target.")
    elif lower_target:
        fund.target -= amount

    if not ctx.obj["DRY_RUN"]:
        path = ctx.obj["PATH"]
        accounts = ctx.obj["ACCOUNTS"]
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(
        f"Withdrawn € {amount:.2f} from '{fund.name}'."
        + f" New balance: € {fund.balance:.2f}."
    )
