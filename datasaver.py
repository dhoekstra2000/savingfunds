import yaml

def save_funds_data(file, accounts_data, funds_data):
    data = {
        "accounts": accounts_data,
        "funds": funds_data
    }
    yaml.dump(data, file)
