from rich.tree import Tree
from rich import print

from funds import Account, Fund

def print_fund_tree(funds: dict[str, Fund]):
    fund_tree = funds.get_as_tree(None)
    # fund_tree = Tree("Fondsen")
    # for g in funds.values():
    #     g.get_as_tree(fund_tree)

    print(fund_tree)


def print_account_tree(accounts: dict[str, Account]):
    acct_tree = Tree("Accounts")
    for a in accounts.values():
        a.get_as_tree(acct_tree)

    print(acct_tree)
