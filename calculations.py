import numpy_financial as npf
import numpy as np
import pandas as pd


def calculate_metrics(projects):
    results = []
    for project in projects:
        name = project['name']
        cash_flows = project['cash_flows']
        cost = project['initial_cost']
        rate = project['discount_rate']

        npt = ((sum(cash_flows)) - cost)
        npv = npf.npv(rate, [-cost] + cash_flows)
        irr_raw = npf.irr([-cost] + cash_flows)
        irr = irr_raw if np.isfinite(irr_raw) else None
        roi = (((( sum(cash_flows)) - cost) / cost) * 100) if cost != 0 else 0
        payback = get_payback_period(cash_flows, cost)
        # bcr = (
        #     sum([cf / (1 + rate) ** i for i, cf in enumerate(cash_flows, start=1)]) / cost
        #     if cost != 0 else 0
        # )

        results.append({
            "Project": name.upper(),
            "net profit": round(npt, 2),
            "NPV": round(npv, 2),
            "IRR (%)": round(irr * 100, 2) if irr else "N/A",
            "ROI (%)": round(roi, 2),
            "Payback (yrs)": round(payback, 2) if payback else "Not recovered",
            # "BCR": round(bcr, 2)
        })

    df = pd.DataFrame(results)
    df_sorted = df.sort_values(by="NPV", ascending=False).reset_index(drop=True)

    best = df_sorted.iloc[0]
    recommendation = (
        f"📌 Recommended Project: {best['Project']}\n"
        f"- Net Profit: &#163;{best['net profit']}\n"
        f"- NPV: &#163;{best['NPV']}\n"
        f"- IRR: {best['IRR (%)']}%\n"
        f"- Payback: {best['Payback (yrs)']}\n"
        f"- ROI: {best['ROI (%)']}%\n"
        # f"- BCR: {best['BCR']}"
    )
    return df_sorted.to_string(index=False), recommendation


def calculate_single_metric(project, metric):
    cost = project["initial_cost"]
    rate = project["discount_rate"]
    cash_flows = project["cash_flows"]

    if metric == "npv":
        npv = npf.npv(rate, [-cost] + cash_flows)
        return f"&#163;{round(npv, 2)}"

    elif metric == "irr":
        irr = npf.irr([-cost] + cash_flows)
        return f"{round(irr * 100, 2)}%" if np.isfinite(irr) else "N/A"
    
    elif metric == "net profit":
        netprft = ((sum(cash_flows)) - cost)
        return netprft

    elif metric == "roi":
        roi = (((sum(cash_flows) - cost) / len(cash_flows)) / cost) * 100 if cost != 0 else 0
        return f"{round(roi, 2)}%"

    elif metric == "payback":
        cumulative = 0
        for i, cf in enumerate(cash_flows):
            cumulative += cf
            if cumulative >= cost:
                return f"{round(i + (cost - (cumulative - cf)) / cf, 2)} years"
        return "Not recovered"

    # elif metric == "bcr":
    #     bcr = sum(cf / (1 + rate) ** (i + 1) for i, cf in enumerate(cash_flows)) / cost if cost != 0 else 0
    #     return f"{round(bcr, 2)}"

    else:
        raise ValueError("Unknown metric. Try: net profit, npv, irr, roi, payback")

def get_payback_period(cash_flows, initial_cost):
    cumulative = 0
    for i, cf in enumerate(cash_flows):
        if cf == 0:
            continue
        cumulative += cf
        if cumulative >= initial_cost:
            return i + (initial_cost - (cumulative - cf)) / cf
    return None


