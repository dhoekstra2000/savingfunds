from rich.table import Table
from rich.tree import Tree
from rich import print

from funds import Account, Fund, FundGroup


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
        target = f"{fund.balance:.2f}"

        table.add_row(key, name, tpe, balance, target)
    
    print(table)
