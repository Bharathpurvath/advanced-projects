from __future__ import annotations
import sqlite3
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "jobs.db"
OUT = ROOT / "reports"


def main():
    OUT.mkdir(exist_ok=True)
    if not DB.exists():
        (OUT / "findings.md").write_text("# Findings\n\nNo collected job postings yet. Add Adzuna API credentials and run `python src/collect.py`, then rerun `python src/analyze.py`. This report deliberately contains no sample or fabricated findings.\n", encoding="utf-8")
        print("No database yet; wrote a clear pending-data report.")
        return
    con = sqlite3.connect(DB)
    try:
        pulls = pd.read_sql_query("SELECT pull_id, scope, collected_at, records_received, status FROM pulls WHERE status='success' ORDER BY collected_at", con)
        if pulls.empty:
            print("No successful pulls yet; rerun after collecting data.")
            (OUT / "findings.md").write_text("# Findings\n\nNo successful collection runs yet.\n", encoding="utf-8")
            return
        latest = pulls.groupby("scope", as_index=False).tail(1)
        latest_ids = latest["pull_id"].tolist()
        placeholders = ",".join("?" for _ in latest_ids)
        demand = pd.read_sql_query(f"""SELECT pj.pull_id,s.skill,COUNT(DISTINCT pj.ad_id) postings,
        ROUND(100.0 * COUNT(DISTINCT pj.ad_id) / NULLIF((SELECT COUNT(DISTINCT allp.ad_id) FROM pull_jobs allp WHERE allp.pull_id=pj.pull_id),0),1) pct_postings
        FROM pull_jobs pj JOIN pull_skills ps ON ps.pull_id=pj.pull_id AND ps.ad_id=pj.ad_id
        JOIN skills s ON s.skill_id=ps.skill_id
        WHERE pj.pull_id IN ({placeholders}) GROUP BY pj.pull_id,s.skill ORDER BY postings DESC""",con,params=latest_ids)
        coverage = pd.read_sql_query(f"""SELECT pj.pull_id,p.scope,p.collected_at,COUNT(DISTINCT pj.ad_id) postings,
        SUM(CASE WHEN j.salary_min IS NOT NULL OR j.salary_max IS NOT NULL THEN 1 ELSE 0 END) salary_ads
        FROM pull_jobs pj JOIN pulls p ON p.pull_id=pj.pull_id JOIN jobs j ON j.ad_id=pj.ad_id
        WHERE pj.pull_id IN ({placeholders}) GROUP BY pj.pull_id,p.scope,p.collected_at""",con,params=latest_ids)
        salary = pd.read_sql_query(f"""SELECT p.scope,j.city,j.experience_level,COUNT(*) salary_ads,
        AVG((COALESCE(j.salary_min,j.salary_max)+COALESCE(j.salary_max,j.salary_min))/2.0) AS mean_midpoint,
        MIN(j.salary_min) salary_min,MAX(j.salary_max) salary_max
        FROM pull_jobs pj JOIN pulls p ON p.pull_id=pj.pull_id JOIN jobs j ON j.ad_id=pj.ad_id
        WHERE pj.pull_id IN ({placeholders}) AND (j.salary_min IS NOT NULL OR j.salary_max IS NOT NULL)
        GROUP BY p.scope,j.city,j.experience_level""",con,params=latest_ids)
        series = pd.read_sql_query("""SELECT p.scope,p.collected_at,COUNT(DISTINCT pj.ad_id) postings
        FROM pulls p LEFT JOIN pull_jobs pj ON pj.pull_id=p.pull_id WHERE p.status='success'
        GROUP BY p.pull_id,p.scope,p.collected_at ORDER BY p.collected_at""",con)
        skills_all = pd.read_sql_query("SELECT skill_id,skill FROM skills",con)
        skills_by_pull = pd.read_sql_query("""SELECT pull_id,skill_id,COUNT(DISTINCT ad_id) postings FROM pull_skills GROUP BY pull_id,skill_id""",con)
    finally: con.close()
    pulls.to_csv(OUT/"pull_history.csv",index=False)
    demand.to_csv(OUT/"skill_demand_latest.csv",index=False)
    coverage.to_csv(OUT/"salary_coverage_latest.csv",index=False)
    salary.to_csv(OUT/"salary_by_city_experience.csv",index=False)
    series.to_csv(OUT/"posting_counts_over_time.csv",index=False)
    if not demand.empty:
        fig,ax=plt.subplots(figsize=(9,5)); d=demand.sort_values("postings").tail(15)
        ax.barh(d["skill"],d["postings"],color="#3767a5"); ax.set_title("Skills mentioned in latest collected postings"); ax.set_xlabel("Distinct postings mentioning skill"); fig.tight_layout(); fig.savefig(OUT/"skill_demand.png",dpi=160); plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4))
    for scope,g in series.groupby("scope"):
        ax.plot(g["collected_at"],g["postings"],marker="o",label=scope)
    ax.set_title("Postings returned by each weekly collection"); ax.set_ylabel("Distinct ads in pull"); ax.tick_params(axis="x",rotation=35); ax.legend(); fig.tight_layout(); fig.savefig(OUT/"posting_counts.png",dpi=160); plt.close(fig)
    lines=["# Findings", "", "Generated from successful Adzuna API pulls. This is an API search sample, not a census of vacancies.", "", f"Successful pull runs: {len(pulls)}.", ""]
    if demand.empty: lines += ["No extracted skills available in the latest successful pulls.",""]
    else:
        ids=set(latest_ids)
        d=demand[demand.pull_id.isin(ids)].groupby("skill",as_index=False).postings.sum().sort_values("postings",ascending=False).head(10)
        total_scope_ads = int(coverage[coverage.pull_id.isin(ids)].postings.sum())
        d["pct_postings"] = 100.0 * d["postings"] / total_scope_ads if total_scope_ads else 0.0
        lines += ["## Most frequently detected skills", "", "Counts combine latest successful India and Chennai scopes. Ads may appear in both scopes; deduplication is per scope.", ""]
        for _,r in d.iterrows(): lines.append(f"- {r.skill}: {int(r.postings)} scope-posting mentions ({r.pct_postings:.1f}% of that pull).")
        lines.append("")
    lines += ["## Salary and experience", "", f"Salary-bearing city/experience groups: {len(salary)}. Interpret only groups with adequate sample sizes; salaries are preserved in the API's reported units and period. See `salary_by_city_experience.csv`.", "", "## Change over time", "", "See `posting_counts_over_time.csv`. Compare the first and latest pull within each scope. API coverage, ranking, duplicate handling, and job expirations can change the observed sample; this is not direct evidence of labor-market growth.", "", "## Limits", "", "Skill matches are transparent keyword heuristics, experience is a text heuristic, and salary is missing for many ads. The analysis does not infer undisclosed compensation or causal trends."]
    (OUT/"findings.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    skill_rows = "".join(f"<tr><td>{r.skill}</td><td>{int(r.postings)}</td><td>{r.pct_postings:.1f}%</td></tr>" for _,r in demand.sort_values("postings",ascending=False).head(15).iterrows()) if not demand.empty else "<tr><td colspan='3'>No skill records yet</td></tr>"
    salary_rows = "".join(f"<tr><td>{r.scope}</td><td>{r.city}</td><td>{r.experience_level}</td><td>{int(r.salary_ads)}</td><td>{r.mean_midpoint:,.0f}</td></tr>" for _,r in salary.sort_values("salary_ads",ascending=False).head(30).iterrows()) if not salary.empty else "<tr><td colspan='5'>No disclosed salaries in latest pulls</td></tr>"
    counts_rows = "".join(f"<tr><td>{r.scope}</td><td>{r.collected_at}</td><td>{int(r.postings)}</td></tr>" for _,r in series.iterrows())
    html = f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>India Data Analyst Job Market</title>
    <style>body{{font:16px system-ui,sans-serif;max-width:1100px;margin:32px auto;padding:0 20px;color:#192332}}h1{{color:#173b68}}.note{{background:#eef4fb;padding:14px;border-radius:8px}}section{{margin:30px 0}}table{{border-collapse:collapse;width:100%}}th,td{{text-align:left;padding:9px;border-bottom:1px solid #dce2e9}}th{{background:#f3f6f9}}img{{max-width:100%;height:auto}}small{{color:#506070}}</style>
    <h1>India Data Analyst Job Market</h1><p class="note">Generated from Adzuna API research pulls. Search results are an API sample, not a census. Salary values use the API-reported units/period; keyword and experience categories are heuristic.</p>
    <section><h2>Skill demand in latest pulls</h2>{'<img src="skill_demand.png" alt="Skill demand chart">' if (OUT/'skill_demand.png').exists() else '<p>No skill chart yet.</p>'}<table><thead><tr><th>Skill</th><th>Scope-posting mentions</th><th>% of scope postings</th></tr></thead><tbody>{skill_rows}</tbody></table></section>
    <section><h2>Salary by city and experience</h2><table><thead><tr><th>Scope</th><th>City</th><th>Experience</th><th>Salary ads</th><th>Mean midpoint</th></tr></thead><tbody>{salary_rows}</tbody></table><small>Use sample sizes before comparing groups. Undisclosed salaries are excluded.</small></section>
    <section><h2>Posting counts across pulls</h2>{'<img src="posting_counts.png" alt="Postings over time chart">' if (OUT/'posting_counts.png').exists() else '<p>No pull chart yet.</p>'}<table><thead><tr><th>Scope</th><th>Collected at (UTC)</th><th>Distinct postings</th></tr></thead><tbody>{counts_rows}</tbody></table></section>
    <p><a href="findings.md">Written findings</a> · <a href="skill_demand_latest.csv">Skill CSV</a> · <a href="salary_by_city_experience.csv">Salary CSV</a></p></html>'''
    (OUT/"dashboard.html").write_text(html,encoding="utf-8")
    print(f"Wrote aggregate reports to {OUT}")

if __name__ == "__main__": main()






