def max_profit(max_trades, daily_prices):
    n = len(daily_prices)

    if n == 0 or max_trades == 0:
        return 0

    # DP table
    dp = [[0] * n for _ in range(max_trades + 1)]

    for t in range(1, max_trades + 1):
        max_diff = -daily_prices[0]

        for d in range(1, n):
            dp[t][d] = max(dp[t][d-1], daily_prices[d] + max_diff)
            max_diff = max(max_diff, dp[t-1][d] - daily_prices[d])

    return dp[max_trades][n-1]


# Example
max_trades = 2
daily_prices = [2000, 4000, 1000]

print("Maximum Profit:", max_profit(max_trades, daily_prices))