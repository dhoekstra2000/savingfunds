from datetime import date
from decimal import Decimal

import yaml
from yaml import BaseLoader

from funds import FixedEndFund, OpenEndFund, FundGroup, Account

def build_fund_tree(fund_data, accounts, group):
    for fnd in fund_data:
            match fnd['type']:
                case 'fixed':
                    acct = accounts[fnd['account']]
                    target_date = date.fromisoformat(fnd['target_date'])
                    fund = FixedEndFund(fnd['key'], fnd['name'], acct, Decimal(fnd['balance']), Decimal(fnd['target']), target_date)
                    acct.funds[fund.key] = fund
                    group.funds[fund.key] = fund
                case 'open':
                    acct = accounts[fnd['account']]
                    fund = OpenEndFund(fnd['key'], fnd['name'], acct, Decimal(fnd['balance']), Decimal(fnd['target']), int(fnd['days']))
                    acct.funds[fund.key] = fund
                    group.funds[fund.key] = fund
                case 'group':
                    fund_group = FundGroup(fnd['key'], fnd['name'])
                    build_fund_tree(fnd['funds'], accounts, fund_group)
                    group.funds[fund_group.key] = fund_group


def convert_data_to_accounts_and_funds(data):
    acct_data = data['accounts']
    accounts = {}
    for acct in acct_data:
        accounts[acct['key']] = Account(**acct)

    fund_groups = {}
    for fund_data in data['funds']:
        key = fund_data['key']
        group = FundGroup(key, fund_data['name'])
        build_fund_tree(fund_data['funds'], accounts, group)
        fund_groups[key] = group

    return accounts, fund_groups


def load_accounts_and_funds(file):
    data = yaml.load(file, BaseLoader)

    return convert_data_to_accounts_and_funds(data)
