import pandas as pd
from price_data import get_close_prices


def calc_rps(close: pd.DataFrame, periods: list[int] = [120, 250]) -> pd.DataFrame:
    """
    Calculate Relative Price Strength (RPS) for given periods.

    Args:
        close: DataFrame of close prices.
        periods: List of periods (days) to calculate RPS for.

    Returns:
        DataFrame containing RPS values.
    """
    results: dict[str, pd.DataFrame] = {}

    for n in periods:
        returns: pd.DataFrame = close.pct_change(periods=n)
        ranks: pd.DataFrame = returns.rank(
            axis=1, ascending=False, method="min")
        counts: pd.Series = returns.notna().sum(axis=1)
        rps: pd.DataFrame = (1 - ranks.div(counts, axis=0)) * 100
        results[f"RPS_{n}"] = rps.round(2)

    data: pd.DataFrame = pd.concat(results, axis=1)
    data = data.dropna()
    return data


def screen_rps(
        rps_df: pd.DataFrame,
        threshold_120: float = 80,
        threshold_250: float = 80,
        check_rising: bool = True) -> pd.DataFrame:
    """
    Screen stocks based on RPS thresholds and trend.

    Args:
        rps_df: DataFrame containing RPS_120 and RPS_250 columns.
        threshold_120: Minimum RPS_120 value.
        threshold_250: Minimum RPS_250 value.
        check_rising: If True, requires current RPS to be higher than 10 days ago.

    Returns:
        Filtered DataFrame sorted by RPS_120.
    """
    latest_120: pd.Series = rps_df["RPS_120"].iloc[-1]
    latest_250: pd.Series = rps_df["RPS_250"].iloc[-1]

    # Check if RPS is rising (compare with 10 days ago)
    if check_rising and len(rps_df) > 10:
        prev_120: pd.Series = rps_df["RPS_120"].iloc[-11]
        prev_250: pd.Series = rps_df["RPS_250"].iloc[-11]
        rising_120: pd.Series = latest_120 > prev_120
        rising_250: pd.Series = latest_250 > prev_250
    else:
        # If check_rising is False or not enough data, assume True
        rising_120 = pd.Series(True, index=latest_120.index)
        rising_250 = pd.Series(True, index=latest_250.index)

    summary: pd.DataFrame = pd.DataFrame({
        "RPS_120":    latest_120,
        "RPS_250":    latest_250,
        "Rising_120": rising_120,
        "Rising_250": rising_250,
    })

    # Apply thresholds
    mask: pd.Series = (summary["RPS_120"] >= threshold_120) & \
                      (summary["RPS_250"] >= threshold_250)

    # Apply rising trend check
    if check_rising:
        mask = mask & summary["Rising_120"] & summary["Rising_250"]

    result: pd.DataFrame = summary[mask].sort_values(
        "RPS_120", ascending=False)
    return result


def main():
    print("🚀 Starting RPS Calculation...")

    # 1. Get Data
    try:
        prices: pd.DataFrame = get_close_prices()
        if prices.empty:
            print("❌ No price data downloaded. Exiting.")
            return
    except Exception as e:
        print(f"❌ Error downloading data: {e}")
        return

    # 2. Calculate RPS
    print("📈 Calculating RPS...")
    rps_df: pd.DataFrame = calc_rps(prices, periods=[120, 250])

    # Optional: Save to CSV
    # rps_df.to_csv("rps.csv")

    # 3. Show Latest Top Rankings
    print("\n🏆 Top 5 RPS_120:")
    latest_120 = rps_df["RPS_120"].iloc[-1].sort_values(ascending=False)
    print(latest_120.head())

    print("\n🏆 Top 5 RPS_250:")
    latest_250 = rps_df["RPS_250"].iloc[-1].sort_values(ascending=False)
    print(latest_250.head())

    # 4. Screen for Strong Stocks
    print("\n🔍 Screening for strong stocks (RPS >= 80 & Rising)...")
    screened: pd.DataFrame = screen_rps(
        rps_df,
        threshold_120=80,
        threshold_250=80,
        check_rising=True
    )

    print(f"\n📊 RPS雙週期 ≥80 且上升的強勢股（共 {len(screened)} 隻）：\n")
    print(screened.to_string())


if __name__ == "__main__":
    main()
