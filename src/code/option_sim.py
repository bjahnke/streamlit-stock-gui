import numpy as np
import matplotlib.pyplot as plt
import math
import typing as t
import pandas as pd


def daily_cumulative_reward_no_compound(option_value: float, apr: float, days: int) -> pd.Series:
    """Calculate the daily cumulative reward without compounding."""
    daily_rate = apr / 365
    days_range = np.arange(0, days + 1)
    cumulative_values = option_value + daily_rate * option_value * days_range
    return pd.Series(cumulative_values, index=days_range)


def calc_break_even_days(premium: float, option_value: float, apr: float, subtract_intrinsic=False) -> int:
    """
    Calculate the number of days until the option breaks even.

    :param premium: Premium paid for the option.
    :param option_value: Intrinsic value of the option.
    :param apr: Annual percentage rate.
    :return: Number of days until the option breaks even.
    """
    assert option_value > 0, "Option value must be greater than zero."
    assert apr > 0, "APR must be greater than zero."
    assert premium >= 0, "Premium must be non-negative."

    b = option_value if subtract_intrinsic else 0

    return math.ceil(365 * (premium - b) / (apr * option_value))

def main(premium, option_value, apr):
    # Calculate daily cumulative reward without compounding
    cumulative_reward = daily_cumulative_reward_no_compound(option_value, apr, 365)
    # Calculate the break-even day
    break_even_day = calc_break_even_days(premium, option_value, apr)
    print(f"Break-even day: {break_even_day}")

    # Subtract the premium from the cumulative reward
    cumulative_reward_minus_premium = cumulative_reward - premium

    # Plot the result
    plt.figure(figsize=(10, 6))
    cumulative_reward_minus_premium.plot(label="Cumulative Reward - Premium")
    plt.axhline(0, color="black", linestyle="--", linewidth=0.8)
    plt.title("Daily Cumulative Reward Minus Premium")
    plt.xlabel("Days")
    plt.ylabel("Value")
    plt.grid()
    plt.legend()
    plt.show()


class Option:
    """
    A class representing an option.
    """
    def __init__(self, type_: str, strike: float, premium: float, expiration: int, intrinsic_value: float = 0.0):
        """
        Initialize an option.

        :param type_: "call" or "put".
        :param strike: Strike price of the option.
        :param premium: Premium paid for the option.
        :param expiration: Expiration time (in days).
        """
        self.type = type_.lower()
        self.strike = strike
        self.premium = premium
        self.expiration = expiration
        self.intrinsic_value = intrinsic_value

    def stake_reward():
        pass

    

    def payoff(self, price: float) -> float:
        """
        Calculate the payoff for the option at a given price.

        :param price: Price of the underlying asset.
        :return: Payoff for the option.
        """
        if self.type == "call":
            return max(0, abs(price - self.strike)) - self.premium
        elif self.type == "put":
            return max(0, self.strike - price) - self.premium
        else:
            raise ValueError("Invalid option type. Use 'call' or 'put'.")

class Strategy:
    """
    A class representing an options strategy.
    """
    def __init__(self):
        self.legs = []

    def add_leg(self, option: Option, quantity: int = 1):
        """
        Add an option leg to the strategy.

        :param option: Option object.
        :param quantity: Number of options in the leg (positive for long, negative for short).
        """
        self.legs.append((option, quantity))

    def calculate_payoff(self, prices: np.ndarray) -> np.ndarray:
        """
        Calculate the total payoff of the strategy over a range of prices.

        :param prices: Array of prices for the underlying asset.
        :return: Array of payoffs for the strategy.
        """
        total_payoff = np.zeros_like(prices, dtype=float)
        for option, quantity in self.legs:
            total_payoff += quantity * np.array([option.payoff(price) for price in prices])
        return total_payoff

def plot_strategy(strategy: Strategy, price_range: tuple, title: str = "Options Strategy"):
    """
    Plot the payoff diagram for the strategy.

    :param strategy: Strategy object.
    :param price_range: Tuple containing the price range (min, max) for the underlying asset.
    :param title: Title of the plot.
    """
    prices = np.linspace(price_range[0], price_range[1], 500)
    payoffs = strategy.calculate_payoff(prices)

    plt.figure(figsize=(10, 6))
    plt.plot(prices, payoffs, label="Net Payoff")
    plt.axhline(0, color="black", linestyle="--", linewidth=0.8)
    plt.title(title)
    plt.xlabel("Underlying Price")
    plt.ylabel("Payoff")
    plt.grid()
    plt.legend()
    plt.show()

import dataclasses
@dataclasses.dataclass
class MaturedOption:
    premium: float
    value: float
    apr: float


def cost_calc(price, amount):
    return price * amount

# Example: Simulating a Bull Call Spread
if __name__ == "__main__":
    # # Define options
    # long_call = Option(type_="call", strike=50, premium=5, expiration=7)
    # short_call = Option(type_="put", strike=50, premium=3, expiration=7)

    # # Create a strategy
    # bull_call_spread = Strategy()
    # bull_call_spread.add_leg(long_call, quantity=1)  # Buy one call
    # bull_call_spread.add_leg(short_call, quantity=1)  # Sell one call

    # # Plot the strategy
    # plot_strategy(bull_call_spread, price_range=(30, 80), title="Bull Call Spread")

    cost = cost_calc(3100, .044766) * 2
    print('Cost:', cost)
    main(premium=900, option_value=3000, apr=110)
