"""
generate_data.py
-----------------
Builds the dataset for the Tableau project
"Program Performance & Outcome Evaluation Dashboard".

Scenario: a government early-childhood program is rolled out across NSW regions.
We track, by region and year, the program's KEY PERFORMANCE INDICATORS and an
OUTCOME measure, so an evaluator can answer: is the program working, where, and
for whom? This mirrors how Report on Government Services (RoGS) presents ECEC
performance indicators across jurisdictions and years.

Output: program_evaluation.csv  (one row per Region x Year), tidy/long-friendly
columns so Tableau can pivot easily.

DATA HONESTY NOTE: simulated, illustrative only. Structure mirrors RoGS-style
performance reporting (participation, expenditure, quality, outcome by region
and year) so the method transfers to real RoGS / ABS / data.NSW data.
"""

import numpy as np
import pandas as pd

RNG = np.random.default_rng(33)

regions = [
    ("Sydney Metro",      0.78, 8200, 0.93),
    ("Hunter",            0.70, 7600, 0.90),
    ("Illawarra",         0.72, 7700, 0.91),
    ("Central Coast",     0.69, 7400, 0.89),
    ("Mid North Coast",   0.63, 7100, 0.86),
    ("New England",       0.60, 6900, 0.85),
    ("Riverina",          0.64, 7000, 0.87),
    ("Far West",          0.55, 6600, 0.82),
]
YEARS = list(range(2020, 2026))   # program introduced 2022

rows = []
for region, base_part, base_spend, base_quality in regions:
    participation = base_part
    enrolled = int(RNG.normal(9000, 2500) * (base_part / 0.7))
    for year in YEARS:
        # Program starts 2022 -> step up in participation & outcomes afterwards
        program_active = year >= 2022
        boost = 0.0
        if program_active:
            years_in = year - 2021
            boost = min(0.015 * years_in, 0.06)   # cumulative program effect

        participation = min(0.98, base_part + boost + RNG.normal(0, 0.008)
                            + 0.004 * (year - 2020))
        spend_per_child = int(base_spend * (1 + 0.03 * (year - 2020))
                              + RNG.normal(0, 150))
        quality = min(0.99, base_quality + (0.01 if program_active else 0)
                      + RNG.normal(0, 0.01))
        # Outcome: % children developmentally on track at school entry
        outcome = (0.55 + 0.45 * participation * quality
                   + (0.02 if program_active else 0) + RNG.normal(0, 0.012))
        outcome = float(np.clip(outcome, 0.4, 0.95))
        enrolled = int(enrolled * (1 + 0.02 + RNG.normal(0, 0.01)))

        rows.append({
            "Region": region,
            "Year": year,
            "ProgramStatus": "Active" if program_active else "Pre-program",
            "ChildrenEnrolled": enrolled,
            "ParticipationRate": round(participation, 4),
            "SpendPerChild": spend_per_child,
            "QualityRating": round(quality, 4),
            "OutcomeOnTrackRate": round(outcome, 4),
        })

df = pd.DataFrame(rows)
df.to_csv("data/program_evaluation.csv", index=False)

print("Wrote data/program_evaluation.csv", df.shape)
print(df.head(8).to_string(index=False))
print("\nState avg outcome by year (watch the 2022 program step-up):")
print(df.groupby("Year")["OutcomeOnTrackRate"].mean().round(3).to_string())
print("\nState avg participation pre vs post program:")
print(df.groupby("ProgramStatus")["ParticipationRate"].mean().round(3).to_string())
