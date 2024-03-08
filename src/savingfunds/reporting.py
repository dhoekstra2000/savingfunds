from decimal import Decimal

from rich import print
from rich.columns import Columns
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from savingfunds.funds import (
    Account,
    FixedEndFund,
    Fund,
    FundGroup,
    OpenEndFund,
)
from savingfunds.utils import moneyfmt


def get_flat_funds_dict(funds):
    flat_funds = {}
    for k, f in funds.funds.items():
        if type(f) is not FundGroup:
            flat_funds[k] = f
        else:
            flat_funds[k] = f
            sub_flat_funds = get_flat_funds_dict(f)
            flat_funds = {**flat_funds, **sub_flat_funds}

    return flat_funds


def print_fund_tree(funds: dict[str, Fund]):
    fund_tree = funds.get_as_tree(None)

    print(fund_tree)


def print_account_tree(accounts: dict[str, Account]):
    acct_tree = Tree("Accounts")
    for a in accounts.values():
        a.get_as_tree(acct_tree)

    print(acct_tree)


def print_funds_table(funds):
    table = Table(title="Funds")

    table.add_column("Key")
    table.add_column("Name")
    table.add_column("Type")
    table.add_column("Balance (€)", justify="right")
    table.add_column("Target (€)", justify="right")

    flat_funds = get_flat_funds_dict(funds)

    for fund in flat_funds.values():
        key = fund.key
        name = fund.name
        tpe = fund.get_type()
        balance = f"{fund.balance:.2f}"
        target = f"{fund.target:.2f}"

        table.add_row(key, name, tpe, balance, target)

    print(table)


def print_savings_amounts_as_tree(funds, amounts):
    tree = tree_for_savings_amounts_as_tree(funds, amounts)
    print(tree)


def tree_for_savings_amounts_as_tree(funds, amounts):
    tree = Tree("Root")

    flat_funds = get_flat_funds_dict(funds)

    def build_tree(data, tree):
        for k, v in data.items():
            fund = flat_funds[k]
            if type(v) is tuple:
                amount, subdata = v
                if amount == Decimal(0):
                    continue
                base = tree.add(f"{fund.name}: € {moneyfmt(amount)}")
                build_tree(subdata, base)
            else:
                if v == Decimal(0):
                    continue
                tree.add(f"{fund.name}: € {moneyfmt(v)}")

    build_tree(amounts, tree)

    return tree


def print_savings_amounts_for_accounts(accounts, amounts):
    tree = tree_for_savings_amounts_for_accounts(accounts, amounts)
    print(tree)


def tree_for_savings_amounts_for_accounts(accounts, amounts):
    tree = Tree("Root")

    def flatten_amounts(amounts):
        flat_amounts = {}
        for k, v in amounts.items():
            if type(v) is tuple:
                amount, subamounts = v
                flat_amounts[k] = amount
                flat_subamounts = flatten_amounts(subamounts)
                flat_amounts = {**flat_amounts, **flat_subamounts}
            else:
                flat_amounts[k] = v

        return flat_amounts

    flat_amounts = flatten_amounts(amounts)
    for _, acct in accounts.items():
        acct_amount = sum(
            [v for k, v in flat_amounts.items() if k in acct.funds]
        )

        rows = [f"{acct.name}: € {moneyfmt(acct_amount)}."]
        if acct.iban is not None:
            rows.append(f"IBAN: {acct.get_iban_as_str()}")
        if acct.comments != "":
            rows.append(f"Comments: {acct.comments}")

        tree.add(Group(*rows))

    return tree


def print_savings_report(accounts, funds, amounts, info_contents):
    funds_tree = tree_for_savings_amounts_as_tree(funds, amounts)
    accounts_tree = tree_for_savings_amounts_for_accounts(accounts, amounts)

    info_panel = Panel(info_contents, title="Information")
    funds_panel = Panel(funds_tree, title="Funds distribution")
    accts_panel = Panel(accounts_tree, title="Accounts increase")

    print(info_panel)

    columns = Columns([funds_panel, accts_panel], expand=True)

    print(columns)


def print_fund_details(fund):
    table = Table(title=f"Details on '{fund.name}'")

    table.add_column("Property")
    table.add_column("Value")

    table.add_row("Type", fund.get_type().capitalize())
    table.add_row("Key", fund.key)
    table.add_row("Name", fund.name)
    table.add_row("Balance", "€ " + moneyfmt(fund.balance))
    table.add_row("Target", "€ " + moneyfmt(fund.target))
    table.add_row("Remainder", "€ " + moneyfmt(fund.remainder_to_save()))

    if isinstance(fund, FixedEndFund):
        table.add_row("Target date", f"{fund.target_date}")
    elif isinstance(fund, OpenEndFund):
        table.add_row("Saving days", f"{fund.days}")
    elif isinstance(fund, FundGroup):
        table.add_row("Contained funds", f"{len(fund.funds)}")

    print(table)


def print_account_details(account):
    table = Table(title=f"Details of '{account.name}'")

    table.add_column("Property")
    table.add_column("Value")

    table.add_row("Key", account.key)
    table.add_row("Name", account.name)
    table.add_row("IBAN", account.get_iban_as_str())
    table.add_row(
        "Manual funds?", "Yes" if account.has_manual_funds() else "No"
    )
    table.add_row(
        "Minimal balance", f"€ {moneyfmt(account.get_minimal_balance())}"
    )
    table.add_row("Comments", account.comments)

    print(table)
