from datetime import date
from decimal import Decimal

import yaml
from schwifty import IBAN
from schwifty.exceptions import SchwiftyException
from yaml import BaseLoader

from savingfunds.funds import (
    Account,
    FixedEndFund,
    FundGroup,
    ManualFund,
    OpenEndFund,
)


def build_fund_tree(fund_data, accounts, group):
    for fnd in fund_data:
        match fnd["type"]:
            case "fixed":
                acct = accounts[fnd["account"]]
                target_date = date.fromisoformat(fnd["target_date"])
                fund = FixedEndFund(
                    fnd["key"],
                    fnd["name"],
                    acct,
                    Decimal(fnd["balance"]),
                    Decimal(fnd["target"]),
                    target_date,
                )
                acct.funds[fund.key] = fund
                group.funds[fund.key] = fund
            case "open":
                acct = accounts[fnd["account"]]
                fund = OpenEndFund(
                    fnd["key"],
                    fnd["name"],
                    acct,
                    Decimal(fnd["balance"]),
                    Decimal(fnd["target"]),
                    int(fnd["days"]),
                )
                acct.funds[fund.key] = fund
                group.funds[fund.key] = fund
            case "group":
                fund_group = FundGroup(fnd["key"], fnd["name"])
                build_fund_tree(fnd["funds"], accounts, fund_group)
                group.funds[fund_group.key] = fund_group
            case "manual":
                acct = accounts[fnd["account"]]
                fund = ManualFund(
                    fnd["key"], fnd["name"], acct, Decimal(fnd["balance"])
                )
                acct.funds[fund.key] = fund
                group.funds[fund.key] = fund


def convert_data_to_accounts_and_funds(data):
    acct_data = data["accounts"]
    accounts = {}
    for acct in acct_data:
        if acct["iban"] != "":
            try:
                iban = IBAN(acct["iban"])
            except SchwiftyException as e:
                print(
                    "There is a problem with the iban of '"
                    + acct["name"]
                    + "'."
                )
                print(e.args[0])
            acct["iban"] = iban
        else:
            acct["iban"] = None
        accounts[acct["key"]] = Account(**acct)

    root_fund_group = FundGroup("root", "Root")
    for fund_data in data["funds"]:
        key = fund_data["key"]
        group = FundGroup(key, fund_data["name"])
        if "monthly-factor" in fund_data:
            group.monthly_factor = Decimal(fund_data["monthly-factor"])
        build_fund_tree(fund_data["funds"], accounts, group)
        root_fund_group.funds[key] = group

    return accounts, root_fund_group


def load_accounts_and_funds(file):
    data = yaml.load(file, BaseLoader)

    return convert_data_to_accounts_and_funds(data)
