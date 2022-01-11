from random import randint
from statistics import NormalDist
import numpy
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


# "Proper" market simulation
def normal_simulation():
    mu = .01
    sigma = .2
    start_price = 5

    returns = numpy.random.normal(loc=mu, scale=sigma, size=100)
    price = start_price*(1+returns).cumprod()
    print(returns)
    plt.plot(price)
    plt.savefig('imgs/cached/graph.png')


# "Nomic-y" market simulation
def nomic_iterate(currentValue, restingValue, delta, interactionBonus, roll):
    seed = .5-(roll/100)
    return (currentValue * (1 + (seed + NormalDist().cdf(delta) + interactionBonus/100)))


def nomic_iterate_2(current, resting, delta, roll, diff):
    newValue = (roll-diff) + current + (resting-current)/5 + delta/4
    newValue = newValue if newValue > 1 else 1
    return newValue


def plotArray(array, title, output):
    plt.figure().gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.figure().gca().xaxis.set_major_locator(MaxNLocator(integer=True))
    plt.title(title)
    plt.plot(array)
    plt.savefig(output)
    plt.clf()

    print(f'{title} min: {min(array)}')
    print(f'{title} max: {max(array)}')


def main():
    value = 200
    rest = value
    change = 0
    roll = 100
    shares = 21
    BBBShares = 155
    amendedShares = shares+1
    rule = 'RULE'

    marketcap = [value]
    share = [int(value/shares)]
    ammendShare = [int(value/amendedShares)]
    BBB = [int(value/BBBShares)]
    for i in range(20):
        # newValue = nomic_iterate(value, rest, change, bonus, randint(1, 100))
        newValue = nomic_iterate_2(value, rest, change, randint(1, roll), int(roll/2))
        change = newValue - value
        value = newValue

        _value = int(value)
        marketcap.append(_value)
        share.append(1 if _value/shares < 1 else int(_value/shares))
        ammendShare.append(1 if _value/amendedShares < 1 else int(_value/amendedShares))
        BBB.append(1 if _value/BBBShares < 1 else int(_value/BBBShares))

    plotArray(numpy.array(marketcap), f'${rule} Value', 'imgs/cached/marketgraph.png')
    plotArray(numpy.array(share), f'${rule} Share Value', 'imgs/cached/sharevalue.png')
    # plotArray(numpy.array(share), f'${rule} Share Value after Rule is Ammended', 'imgs/cached/sharevalue2.png')
    plotArray(numpy.array(BBB), f'${rule} Share Value if it was actually BBB', 'imgs/cached/bbbsharevalue.png')


if __name__ == '__main__':
    main()
