from dataloader import (
    load_accounts_and_funds,
    convert_data_to_accounts_and_funds,
)
from reporting import print_fund_tree

with open("funds.yaml", "r") as f:
    accounts, funds = load_accounts_and_funds(f)

    print_fund_tree(funds)

    fd = [f.to_dict() for f in funds.values()]

    new_data = {
        "accounts": [a.to_dict() for a in accounts.values()],
        "funds": fd,
    }

    accounts2, funds2 = convert_data_to_accounts_and_funds(new_data)

    print_fund_tree(funds)
