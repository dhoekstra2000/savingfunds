import click

from savingfunds.commands.utils import (
    validate_existing_account_key,
    validate_existing_fund_key,
)
from savingfunds.datasaver import save_accounts_and_funds


@click.command()
@click.argument("key")
@click.pass_context
def remove_fund(ctx, key):
    """Remove a fund from the tree of saving funds."""
    funds = ctx.obj["FUNDS"]

    validate_existing_fund_key(funds, key)

    try:
        funds.remove_fund_by_key(key)
    except Exception as e:
        print(e.args[0])
        raise SystemExit(1)

    if not ctx.obj["DRY_RUN"]:
        path = ctx.obj["PATH"]
        accounts = ctx.obj["ACCOUNTS"]
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Removed fund with key '{key}'.")


@click.command()
@click.argument("key")
@click.pass_context
def remove_account(ctx, key):
    """Remove an account."""
    accounts = ctx.obj["ACCOUNTS"]

    validate_existing_account_key(accounts, key)

    account = accounts[key]
    if len(account.funds) > 0:
        click.echo(
            f"Account with key '{key}' still has registered funds to it."
        )
        raise SystemExit(1)

    del accounts[key]

    if not ctx.obj["DRY_RUN"]:
        path = ctx.obj["PATH"]
        funds = ctx.obj["FUNDS"]
        with open(path, "w") as file:
            save_accounts_and_funds(file, accounts, funds)

    print(f"Removed account with key '{key}'.")
