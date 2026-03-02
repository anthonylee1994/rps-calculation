import pandas as pd
from price_data import get_close_prices

prices: pd.DataFrame = get_close_prices()


def calc_rps(close: pd.DataFrame, periods: list[int] = [120, 250]) -> pd.DataFrame:
    results: dict[str, pd.DataFrame] = {}

    for n in periods:
        returns: pd.DataFrame = close.pct_change(periods=n)
        rps: pd.DataFrame = returns.rank(axis=1, pct=True) * 100
        results[f"RPS_{n}"] = rps.round(2)

    data: pd.DataFrame = pd.concat(results, axis=1)
    data: pd.DataFrame = data.dropna()
    return data


def screen_rps(
        rps_df: pd.DataFrame = None,
        threshold_120: float = 80,
        threshold_250: float = 80,
        check_rising: bool = True) -> pd.DataFrame:

    latest_120: pd.Series = rps_df["RPS_120"].iloc[-1]
    latest_250: pd.Series = rps_df["RPS_250"].iloc[-1]

    # Check if RPS is rising (compare with 10 days ago)
    if check_rising and len(rps_df) > 10:
        prev_120: pd.Series = rps_df["RPS_120"].iloc[-11]
        prev_250: pd.Series = rps_df["RPS_250"].iloc[-11]
        rising_120: pd.Series = latest_120 > prev_120
        rising_250: pd.Series = latest_250 > prev_250
    else:
        rising_120: pd.Series = pd.Series(True, index=latest_120.index)
        rising_250: pd.Series = pd.Series(True, index=latest_250.index)

    summary: pd.DataFrame = pd.DataFrame({
        "RPS_120":    latest_120,
        "RPS_250":    latest_250,
        "Rising_120": rising_120,
        "Rising_250": rising_250,
    })

    mask: pd.Series = (summary["RPS_120"] >= threshold_120) & \
                      (summary["RPS_250"] >= threshold_250)

    if check_rising:
        mask: pd.Series = mask & summary["Rising_120"] & summary["Rising_250"]

    result: pd.DataFrame = summary[mask].sort_values(
        "RPS_120", ascending=False)
    return result


rps_df: pd.DataFrame = calc_rps(prices, periods=[120, 250])
# rps_df.to_csv("rps.csv")

latest_120: pd.Series = rps_df["RPS_120"].iloc[-1]
latest_120: pd.Series = latest_120.sort_values(ascending=False)
print(f"Latest RPS_120:\n{latest_120.head()}")

latest_250: pd.Series = rps_df["RPS_250"].iloc[-1]
latest_250: pd.Series = latest_250.sort_values(ascending=False)
print(f"Latest RPS_250:\n{latest_250.head()}")

screened: pd.DataFrame = screen_rps(rps_df, threshold_120=80,
                                    threshold_250=80, check_rising=True)

print(f"\n📊 RPS雙週期 ≥80 且上升的強勢股（共 {len(screened)} 隻）：\n")
print(screened.to_string())
