from decimal import getcontext
from pathlib import Path

import click

from commands.delete_commands import remove_account, remove_fund
from commands.distribution_commands import (
    distribute_extra,
    distribute_interest,
    distribute_monthly,
)
from commands.edit_commands import (
    change_account,
    change_monthly_factor,
    change_name,
    change_parent_group,
    change_saving_days,
    change_target,
    change_target_date,
    set_balance,
)
from commands.money_commands import deposit, withdraw
from commands.new_commands import (
    init,
    new_account,
    new_fixed_end_fund,
    new_fund_group,
    new_manual_fund,
    new_open_end_fund,
)
from commands.reporting_commands import (
    fund_details,
    funds_table,
    list_accounts,
    list_funds,
    total_daily_saving_rate,
)
from dataloader import load_accounts_and_funds

getcontext().prec = 100


@click.group()
@click.option("--file", default="./funds.yaml", type=click.Path())
@click.option("--dry-run", is_flag=True)
@click.pass_context
def cli(ctx, file, dry_run):
    ctx.ensure_object(dict)

    path = Path(file)

    if path.exists():
        with open(path, "r") as f:
            accounts, funds = load_accounts_and_funds(f)

        ctx.obj["FUNDS"] = funds
        ctx.obj["ACCOUNTS"] = accounts
    else:
        ctx.obj["FUNDS"] = {}
        ctx.obj["ACCOUNTS"] = {}

    ctx.obj["PATH"] = path
    ctx.obj["DRY_RUN"] = dry_run


cli.add_command(list_accounts)
cli.add_command(list_funds)
cli.add_command(funds_table)
cli.add_command(total_daily_saving_rate)
cli.add_command(fund_details)

cli.add_command(init)
cli.add_command(new_account)
cli.add_command(new_fund_group)
cli.add_command(new_fixed_end_fund)
cli.add_command(new_open_end_fund)
cli.add_command(new_manual_fund)

cli.add_command(set_balance)
cli.add_command(change_target)
cli.add_command(change_target_date)
cli.add_command(change_saving_days)
cli.add_command(change_name)
cli.add_command(change_monthly_factor)
cli.add_command(change_account)
cli.add_command(change_parent_group)

cli.add_command(remove_account)
cli.add_command(remove_fund)

cli.add_command(deposit)
cli.add_command(withdraw)

cli.add_command(distribute_extra)
cli.add_command(distribute_interest)
cli.add_command(distribute_monthly)


if __name__ == "__main__":
    cli()
