import pandas as pd
from price_data import get_close_prices

prices = get_close_prices()


def calc_rps(close: pd.DataFrame, periods: list = [120, 250]) -> pd.DataFrame:
    results = {}

    for n in periods:
        returns = close.pct_change(periods=n)
        rps = returns.rank(axis=1, pct=True) * 100
        results[f"RPS_{n}"] = rps.round(2)

    data = pd.concat(results, axis=1)
    data = data.dropna()
    return data


def screen_rps(
        rps_df: pd.DataFrame = None,
        threshold_120: float = 80,
        threshold_250: float = 80,
        check_rising: bool = True) -> pd.DataFrame:

    latest_120 = rps_df["RPS_120"].iloc[-1]
    latest_250 = rps_df["RPS_250"].iloc[-1]

    # Check if RPS is rising (compare with 10 days ago)
    if check_rising and len(rps_df) > 10:
        prev_120 = rps_df["RPS_120"].iloc[-11]
        prev_250 = rps_df["RPS_250"].iloc[-11]
        rising_120 = latest_120 > prev_120
        rising_250 = latest_250 > prev_250
    else:
        rising_120 = pd.Series(True, index=latest_120.index)
        rising_250 = pd.Series(True, index=latest_250.index)

    summary = pd.DataFrame({
        "RPS_120":    latest_120,
        "RPS_250":    latest_250,
        "Rising_120": rising_120,
        "Rising_250": rising_250,
    })

    mask = (summary["RPS_120"] >= threshold_120) & \
           (summary["RPS_250"] >= threshold_250)

    if check_rising:
        mask = mask & summary["Rising_120"] & summary["Rising_250"]

    result = summary[mask].sort_values("RPS_120", ascending=False)
    return result


rps_df = calc_rps(prices, periods=[120, 250])
# rps_df.to_csv("rps.csv")

latest_120 = rps_df["RPS_120"].iloc[-1]
latest_120 = latest_120.sort_values(ascending=False)
print(f"Latest RPS_120:\n{latest_120.head()}")

latest_250 = rps_df["RPS_250"].iloc[-1]
latest_250 = latest_250.sort_values(ascending=False)
print(f"Latest RPS_250:\n{latest_250.head()}")

screened = screen_rps(rps_df, threshold_120=80,
                      threshold_250=80, check_rising=True)

print(f"\n📊 RPS雙週期 ≥80 且上升的強勢股（共 {len(screened)} 隻）：\n")
print(screened.to_string())
