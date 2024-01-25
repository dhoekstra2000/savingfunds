from rich.tree import Tree

from utils import moneyfmt


class Account:
    def __init__(self, key, name):
        self.name = name
        self.key = key
        self.funds = {}

    def get_minimal_balance(self):
        return sum([f.balance for _, f in self.funds.items()])
    
    def get_as_tree(self, tree):
        base = tree.add(f"Account: {self.name} (≥ € {self.get_minimal_balance():.2f})")
        for f in self.funds.values():
            f.get_as_tree(base)
    
    def __str__(self):
        return f"Account(key='{self.key}', name='{self.name}')"

    def __repr__(self):
        return self.__str__()
    
    def to_dict(self):
        return {
            "key": self.key,
            "name": self.name
        }


class FixedEndFund:
    def __init__(self, key, name, account, balance, target, target_date):
        self.key = key
        self.name = name
        self.balance = balance
        self.account = account
        self.target = target
        self.target_date = target_date

    def get_as_tree(self, tree):
        return tree.add(f"[green]{self.name}[/green]: € {self.balance:.2f}/€ {self.target:.2f} ({self.balance / self.target * 100:.1f} %)")
    
    def get_type(self):
        return "Fixed"

    def to_dict(self):
        return {
            "type": "fixed",
            "key": self.key,
            "name": self.name,
            "account": self.account.key,
            "balance": moneyfmt(self.balance),
            "target": moneyfmt(self.target),
            "target_date": self.target_date.isoformat()
        }


class OpenEndFund:
    def __init__(self, key, name, account, balance, target, days):
        self.key = key
        self.name = name
        self.account = account
        self.balance = balance
        self.target = target
        self.days = days

    def get_as_tree(self, tree):
        return tree.add(f"[blue]{self.name}[/blue]: € {self.balance:.2f}/€ {self.target:.2f} ({self.balance / self.target * 100:.1f} %)")
    
    def get_type(self):
        return "Open"

    def to_dict(self):
        return {
            "type": "open",
            "key": self.key,
            "name": self.name,
            "account": self.account.key,
            "balance": moneyfmt(self.balance),
            "target": moneyfmt(self.target),
            "days": self.days
        }


class FundGroup:
    def __init__(self, key, name):
        self.name = name
        self.key = key
        self.funds = {}

    @property
    def balance(self):
        return sum([f.balance for f in self.funds.values()])
    
    @property
    def target(self):
        return sum([f.target for f in self.funds.values()])
    
    def get_type(self):
        return "Group"

    def contains_key(self, key):
        if self.key == key or key in self.funds:
            return True
        
        for f in filter(lambda f: type(f) is FundGroup, self.funds.values()):
            if f.contains_key(key):
                return True
            
        return False
    
    def add_fund_to_group(self, fund, group_key):
        if self.key == group_key:
            self.funds[fund.key] = fund
            return True
        
        for f in filter(lambda f: type(f) is FundGroup, self.funds.values()):
            if f.add_fund_to_group(fund, group_key):
                return True
            
        return False

    def get_fund_by_key(self, key):
        if self.key == key:
            return self
        
        if key in self.funds:
            return self.funds[key]
        
        for f in filter(lambda f: type(f) is FundGroup, self.funds.values()):
            tmp = f.get_fund_by_key(key)
            if tmp is not None:
                return tmp
            
    def remove_fund_by_key(self, key):
        if key in self.funds:
            fund = self.funds[key]
            if type(fund) is FundGroup:
                if len(fund.funds) > 0:
                    raise Exception(f"Fund with key '{key}' is a non-empty fund group.")
            
            del self.funds[key]
            return True
        
        for f in filter(lambda f: type(f) is FundGroup, self.funds.values()):
            if f.remove_fund_by_key(key):
                return True
            
        return False

    def get_as_tree(self, tree):
        label = f"{self.name}: € {self.balance:.2f}/€ {self.target:.2f} ({self.balance / self.target * 100:.1f} %)"
        if tree is None:
            base = Tree(label)
        else:
            base = tree.add(label)
        for f in self.funds.values():
            f.get_as_tree(base)

        return base

    def to_dict(self):
        return {
            "type": "group",
            "key": self.key,
            "name": self.name,
            "funds": [f.to_dict() for f in self.funds.values()]
        }


Fund = FixedEndFund | OpenEndFund | FundGroup
