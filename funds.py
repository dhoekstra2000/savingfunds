import calendar
from datetime import date
from decimal import Decimal

from rich.columns import Columns
from rich.console import Group
from rich.progress_bar import ProgressBar
from rich.tree import Tree

from utils import moneyfmt


class Account:
    def __init__(self, key, name):
        self.name = name
        self.key = key
        self.funds = {}

    def get_minimal_balance(self):
        return sum([f.balance for _, f in self.funds.items()])
    
    def has_manual_funds(self):
        return any([type(f) is ManualFund for f in self.funds.values()])
    
    def distribute_interest(self, date, amount):
        manual_funds = {
            k: f for k, f in self.funds.items() if type(f) is ManualFund
        }
        non_manual_funds = {
            k: f for k, f in self.funds.items() if type(f) is not ManualFund
        }
        manual_funds_balance = sum(map(lambda f: f.balance, manual_funds.values()))
        non_manual_funds_balance = sum(map(lambda f: f.balance, non_manual_funds.values()))
        
        manual_funds_amount = None
        non_manual_funds_amount = None
        if manual_funds_balance + non_manual_funds_balance > 0:
            manual_funds_amount = amount * manual_funds_balance / (manual_funds_balance + non_manual_funds_balance)
            non_manual_funds_amount = amount - manual_funds_amount
        else:
            manual_funds_amount = Decimal(0)
            non_manual_funds_amount = amount

        child_dsr = {
            k: f.daily_saving_rate(date) for k, f in non_manual_funds.items()
        }
        total_dsr = sum(child_dsr.values())
        amounts = {}
        if total_dsr == Decimal(0):
            manual_funds_amount = amount
        else:
            amounts = {
                k: non_manual_funds_amount * v / total_dsr for k, v in child_dsr.items()
            }
        
        amounts = { k: min(v, self.funds[k].remainder_to_save()) for k, v in amounts.items() }
        remainder = non_manual_funds_amount - sum(amounts.values())
        manual_funds_amount += remainder

        for k, f in manual_funds.items():
            if manual_funds_amount > 0:
                amounts[k] = f.balance * manual_funds_amount / manual_funds_balance
            else:
                amounts[k] = Decimal(0)

        for k, v in amounts.items():
            self.funds[k].balance += v

        remainder = amount - sum(amounts.values())

        return amounts, remainder
    
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

    def remainder_to_save(self):
        return max(Decimal(0), self.target - self.balance)
    
    def daily_saving_rate(self, date):
        days = (self.target_date - date).days
        if days <= 0:
            return self.remainder_to_save()
        
        return self.remainder_to_save() / days
    
    def ndays_saving(self, date, days):
        dsr = self.daily_saving_rate(date)
        return min(dsr * days, self.remainder_to_save())

    def get_as_tree(self, tree):
        progress = self.balance / self.target * Decimal(100)
        progress_bar = ProgressBar(completed=float(progress), width=40)
        columns = Columns([
            progress_bar,
            f"({self.balance / self.target * 100:.1f} %)"
        ])
        return tree.add(Group(f"[green]{self.name}[/green]: € {self.balance:.2f}/€ {self.target:.2f}", columns))
    
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

    def remainder_to_save(self):
        return max(Decimal(0), self.target - self.balance)
    
    def daily_saving_rate(self, date):
        return self.target / self.days
    
    def ndays_saving(self, date, days):
        dsr = self.daily_saving_rate(date)
        return min(dsr * days, self.remainder_to_save())

    def get_as_tree(self, tree):
        progress = self.balance / self.target * Decimal(100)
        progress_bar = ProgressBar(completed=float(progress), width=40)
        columns = Columns([
            progress_bar,
            f"({self.balance / self.target * 100:.1f} %)"
        ])
        return tree.add(Group(f"[blue]{self.name}[/blue]: € {self.balance:.2f}/€ {self.target:.2f}", columns))
    
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


class ManualFund:
    def __init__(self, key, name, account, balance):
        self.key = key
        self.name = name
        self.account = account
        self.balance = balance
    
    @property
    def target(self):
        return self.balance
    
    def remainder_to_save(self):
        return Decimal(0)
    
    def daily_saving_rate(self, date):
        return Decimal(0)
    
    def ndays_saving(self, date, days):
        return Decimal(0)
    
    def get_as_tree(self, tree):
        return tree.add(f"[cyan]{self.name}[/cyan]: € {self.balance:.2f}")
    
    def get_type(self):
        return "Manual"
    
    def to_dict(self):
        return {
            "type": "manual",
            "key": self.key,
            "name": self.name,
            "account": self.account.key,
            "balance": moneyfmt(self.balance)
        }


class FundGroup:
    def __init__(self, key, name, monthly_factor=Decimal(1)):
        self.name = name
        self.key = key
        self.funds = {}
        self.monthly_factor = monthly_factor

    @property
    def balance(self):
        return sum([f.balance for f in self.funds.values()])
    
    @property
    def target(self):
        return sum([f.target for f in self.funds.values()])

    def remainder_to_save(self):
        return max(Decimal(0), self.target - self.balance)
    
    def daily_saving_rate(self, date):
        return sum([f.daily_saving_rate(date) for f in self.funds.values()])
    
    def ndays_saving(self, date, days):
        return sum([f.ndays_saving(date, days) for f in self.funds.values()])
    
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
    
    def distribute_extra_savings(self, when, amount):
        child_dsr = {
            k: f.daily_saving_rate(when) for k, f in self.funds.items()
        }
        total_child_dsr = sum(child_dsr.values())
        amounts = {}
        if total_child_dsr > 0:
            amounts = {
                k: min(amount * v/total_child_dsr, self.funds[k].remainder_to_save()) for k, v in child_dsr.items()
            }
            remainder = amount - sum(amounts.values())
        
            for f in filter(lambda f: type(f) is FundGroup, self.funds.values()):
                subgroup_amounts, _ = f.distribute_extra_savings(when, amounts[f.key])
                amounts[f.key] = (amounts[f.key], subgroup_amounts)

            for f in filter(lambda f: type(f) is not FundGroup, self.funds.values()):
                f.balance = f.balance + amounts[f.key]

            return amounts, remainder

        return {
            k: Decimal(0) for k in self.funds
        }, amount

    def distribute_monthly_savings_tld(self, year, month, amount):
        _, days_in_month = calendar.monthrange(year, month)
        when = date(year, month, 1)
        
        amounts = {}
        deficits = Decimal(0)
        remainder = amount

        for k, f in self.funds.items():
            subamounts, new_remainder, deficit = f.distribute_monthly_savings(year, month, remainder)
            deficits += deficit
            amounts[k] = (remainder - new_remainder, subamounts)
            remainder = new_remainder

        def upfactor_room(group):
            factor = group.monthly_factor
            amounts = {
                k: min(f.ndays_saving(when, days_in_month)*factor, f.remainder_to_save()) for k, f in group.funds.items()
            }
            return sum(amounts.values()) - group.get_minimal_monthly_amount(year, month)
        
        def summerge_amounts(a, b):
            m = {}
            for k, v in a.items():
                if type(v) is tuple:
                    amount_a, subamounts_a = v
                    amount_b, subamounts_b = b[k]
                    m[k] = amount_a + amount_b, summerge_amounts(subamounts_a, subamounts_b)
                else:
                    m[k] = v + b[k]
            
            return m

        if remainder > 0:
            upfactor_room_d = {
                k: upfactor_room(f) for k, f in self.funds.items()
            }
            for k, f in self.funds.items():
                if upfactor_room_d[k] > 0:
                    dist_amount = min(upfactor_room_d[k], remainder)
                    extra_amounts, new_remainder = f.distribute_extra_savings(when, dist_amount)
                    total_extra = dist_amount - new_remainder
                    
                    orig_amount, subamounts = amounts[k]
                    new_subamounts = summerge_amounts(subamounts, extra_amounts)
                    amounts[k] = orig_amount + total_extra, new_subamounts
                    
                    remainder = remainder - dist_amount + new_remainder

        return amounts, remainder, deficits

    def distribute_monthly_savings(self, year, month, amount):
        """Returns (amounts, remainder, deficit)"""
        _, days_in_month = calendar.monthrange(year, month)
        when = date(year, month, 1)

        minimal_amount = self.get_minimal_monthly_amount(year, month)
        deficit = max(Decimal(0), minimal_amount - amount)
        if minimal_amount == Decimal(0):
            return {
                k: Decimal(0) for k in self.funds
            }, amount, Decimal(0)
        
        correction_ratio = min(Decimal(1), amount/minimal_amount)

        amounts = {
            k: min(f.ndays_saving(when, days_in_month)*correction_ratio, f.remainder_to_save()) for k, f in self.funds.items()
        }
        remainder = amount - sum(amounts.values())

        for f in filter(lambda f: type(f) is FundGroup, self.funds.values()):
            subgroup_amounts, _, _ = f.distribute_monthly_savings(year, month, amounts[f.key])
            amounts[f.key] = (amounts[f.key], subgroup_amounts)
        
        for f in filter(lambda f: type(f) is not FundGroup, self.funds.values()):
                f.balance = f.balance + amounts[f.key]

        return amounts, remainder, deficit


    def get_minimal_monthly_amount(self, year, month):
        _, days_in_month = calendar.monthrange(year, month)
        return self.ndays_saving(date(year, month, 1), days_in_month)

    def contains_manual_fund(self):
        manual_in_subgroup = any([
            f.contains_manual_fund() for f in self.funds.values() 
            if isinstance(f, FundGroup)
            ])
        return any([isinstance(f, ManualFund) for f in self.funds.values()]) or manual_in_subgroup

    def get_as_tree(self, tree):
        group = None
        label = f"{self.name}: € {self.balance:.2f}"
        if self.contains_manual_fund():
            group = Group(label)
        else:
            label += f"/€ {self.target:.2f}"
            progress = self.balance / self.target * Decimal(100)
            progress_bar = ProgressBar(completed=float(progress), width=40)
            columns = Columns([progress_bar, f"({progress:.1f} %)"])
            group = Group(label, columns)

        if tree is None:
            base = Tree(group)
        else:
            base = tree.add(group)
        for f in self.funds.values():
            f.get_as_tree(base)

        return base

    def to_dict(self):
        return {
            "type": "group",
            "key": self.key,
            "name": self.name,
            "funds": [f.to_dict() for f in self.funds.values()],
            "monthly-factor": str(self.monthly_factor)
        }


Fund = FixedEndFund | OpenEndFund | ManualFund | FundGroup
BalanceFund = FixedEndFund | OpenEndFund | ManualFund
TargetFund = FixedEndFund | OpenEndFund
