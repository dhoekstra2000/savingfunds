import yaml


def funds_group_to_funds_data(funds_group):
    return funds_group.to_dict()["funds"]


def accounts_dict_to_accounts_data(accounts):
    return [a.to_dict() for a in accounts.values()]


def save_funds_data(file, accounts_data, funds_data):
    data = {"accounts": accounts_data, "funds": funds_data}
    yaml.dump(data, file)


def save_accounts_and_funds(file, accounts, funds):
    save_funds_data(
        file,
        accounts_dict_to_accounts_data(accounts),
        funds_group_to_funds_data(funds),
    )
