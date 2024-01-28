import click

from datasaver import save_accounts_and_funds


@click.command()
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

@click.command()
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
