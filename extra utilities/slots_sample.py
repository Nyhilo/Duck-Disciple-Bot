from random import choice
from typing import List
from operator import attrgetter


# Slot weights
class Symbol:
    def __init__(self, symbol: str, weight: int):
        self.symbol = symbol
        self.weight = weight


class Slot:
    def __init__(self, symbols: Symbol):
        self.values = []

        for s in symbols:
            for _ in range(s.weight):
                self.values.append(s.symbol)

    def roll(self) -> str:
        return choice(self.values)


class Machine:
    def __init__(self, slots: List[Slot]):
        self.slots = slots


class Payout:
    def __init__(self,
                 amount: int,
                 priority: int,
                 dead: bool = False,
                 symbols: str = None):
        self.priority = priority
        self.amount = amount
        self.dead = dead
        self.symbols = symbols


_trials = 10000
_cost = 6

possible_payouts = {
    '🦆🦆🦆': Payout(0, 130, True),
    '🦆🦆': Payout(0, 120),
    '♾♾♾': Payout(100, 110),
    '♾♾': Payout(50, 100),
    '♾': Payout(25, 90),
    '🔺🔺🔺': Payout(24, 80),
    '🔺🔺': Payout(20, 70),
    '🃏🃏🃏': Payout(18, 60),
    '🃏🃏': Payout(12, 50),
    '✨✨✨': Payout(10, 40),
    '✨✨': Payout(6, 30),
    '🤔🤔🤔': Payout(3, 20),
    '🤔🤔': Payout(1, 10)
}

base_slot = Slot([
    Symbol('🦆', 5),
    Symbol('🤔', 4),
    Symbol('✨', 4),
    Symbol('🃏', 3),
    Symbol('🔺', 3),
    Symbol('♾', 1)
])

print("Symbols:", len(base_slot.values))


class Result:
    def __init__(self, spent: int, profit: int, payouts: List[Payout]):
        self.spent = spent
        self.profit = profit
        self.payouts = payouts


# Analyze
def spin(slots: List[Slot]) -> Payout:
    plays = []
    for slot in slots:
        plays.append(slot.roll())

    length = len(plays) - 1

    # Build the payouts
    payouts = []

    # Check for single slot payouts
    for play in plays:
        if play in possible_payouts:
            payout = possible_payouts[play]
            payouts.append(payout)

    # Check for double slot payouts
    for i in range(length):
        if i+1 <= length:
            play = plays[i] + plays[i+1]
            if play in possible_payouts:
                payout = possible_payouts[play]
                payouts.append(payout)

    # Check for triple slot payouts
    for i in range(length):
        if i+2 <= length:
            play = plays[i] + plays[i+1] + plays[i+2]
            if play in possible_payouts:
                payout = possible_payouts[play]
                payouts.append(payout)

    # Return only the highest priority payout
    if len(payouts) == 0:
        return Payout(0, 0, False, ''.join(plays))

    highest = max(payouts, key=attrgetter('priority'))
    highest.symbols = ''.join(plays)
    return highest


def play(fee: int, limit: int, machine: Machine) -> Result:
    '''Plays the slots a number of times, stopping if it gets a None payout'''

    payouts = []
    spent = 0
    brk = False
    for _ in range(limit):
        spent += fee
        payout = spin(machine.slots)

        # 🦆🦆🦆
        if payout.dead:
            payouts.append(payout)
            brk = True
            break

        if not brk:
            payouts.append(payout)

    profit = sum(payout.amount for payout in payouts) - spent
    return Result(spent, profit, payouts)


if __name__ == '__main__':
    machine = Machine([base_slot, base_slot, base_slot])

    data = ["Spent,Profit,Payouts,Plays\n"]
    for week in range(_trials):
        result = play(_cost, 3, machine)

        amounts = [payout.amount for payout in result.payouts]
        symbols = [payout.symbols for payout in result.payouts]

        payout_str = '|'.join([str(a) for a in amounts])
        symbols_str = '|'.join(symbols)
        data.append(
            f'{result.spent},{result.profit},{payout_str},{symbols_str}\n'
        )

    with open('payouts.csv', 'w') as file:
        file.writelines(data)
