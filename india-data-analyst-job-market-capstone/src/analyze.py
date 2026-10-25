from __future__ import annotations
import sqlite3
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/"data"/"himalayas_jobs.db"
OUT=ROOT/"reports"

def main():
    OUT.mkdir(exist_ok=True)
    if not DB.exists():
        (OUT/"findings.md").write_text("# Findings\n\nNo real job postings have been collected yet. Run `python src/collect.py`, then `python src/analyze.py`.\n",encoding="utf-8")
        return
    con=sqlite3.connect(DB)
    try:
        pulls=pd.read_sql_query("SELECT pull_id,scope,collected_at,total_reported,records_received,status FROM pulls WHERE status='success' ORDER BY collected_at",con)
        if pulls.empty:
            (OUT/"findings.md").write_text("# Findings\n\nNo successful data pulls yet.\n",encoding="utf-8"); return
        latest=pulls.groupby("scope",as_index=False).tail(1)
        ids=latest.pull_id.tolist(); marks=",".join("?" for _ in ids)
        demand=pd.read_sql_query(f"""SELECT pj.pull_id,s.skill,COUNT(DISTINCT pj.ad_id) postings,
        ROUND(100.0*COUNT(DISTINCT pj.ad_id)/NULLIF((SELECT COUNT(DISTINCT a.ad_id) FROM pull_jobs a WHERE a.pull_id=pj.pull_id),0),1) pct_postings
        FROM pull_jobs pj JOIN pull_skills ps ON ps.pull_id=pj.pull_id AND ps.ad_id=pj.ad_id
        JOIN skills s ON s.skill_id=ps.skill_id WHERE pj.pull_id IN ({marks})
        GROUP BY pj.pull_id,s.skill ORDER BY postings DESC""",con,params=ids)
        coverage=pd.read_sql_query(f"""SELECT pj.pull_id,p.scope,p.collected_at,COUNT(DISTINCT pj.ad_id) postings,
        SUM(CASE WHEN j.salary_min IS NOT NULL OR j.salary_max IS NOT NULL THEN 1 ELSE 0 END) salary_ads
        FROM pull_jobs pj JOIN pulls p ON p.pull_id=pj.pull_id JOIN jobs j ON j.ad_id=pj.ad_id
        WHERE pj.pull_id IN ({marks}) GROUP BY pj.pull_id,p.scope,p.collected_at""",con,params=ids)
        salary=pd.read_sql_query(f"""SELECT j.experience_level,j.salary_currency,j.salary_period,COUNT(*) salary_ads,
        AVG((COALESCE(j.salary_min,j.salary_max)+COALESCE(j.salary_max,j.salary_min))/2.0) mean_midpoint,
        MIN(j.salary_min) salary_min,MAX(j.salary_max) salary_max
        FROM pull_jobs pj JOIN jobs j ON j.ad_id=pj.ad_id WHERE pj.pull_id IN ({marks})
        AND (j.salary_min IS NOT NULL OR j.salary_max IS NOT NULL)
        GROUP BY j.experience_level,j.salary_currency,j.salary_period ORDER BY salary_ads DESC""",con,params=ids)
        series=pd.read_sql_query("""SELECT p.scope,p.collected_at,COUNT(DISTINCT pj.ad_id) postings
        FROM pulls p LEFT JOIN pull_jobs pj ON pj.pull_id=p.pull_id WHERE p.status='success'
        GROUP BY p.pull_id,p.scope,p.collected_at ORDER BY p.collected_at""",con)
    finally: con.close()
    pulls.to_csv(OUT/"pull_history.csv",index=False)
    demand.to_csv(OUT/"skill_demand_latest.csv",index=False)
    coverage.to_csv(OUT/"salary_coverage_latest.csv",index=False)
    salary.to_csv(OUT/"salary_by_experience.csv",index=False)
    series.to_csv(OUT/"posting_counts_over_time.csv",index=False)
    if not demand.empty:
        d=demand.groupby("skill",as_index=False).postings.sum().sort_values("postings").tail(15)
        fig,ax=plt.subplots(figsize=(9,5)); ax.barh(d.skill,d.postings,color="#3767a5")
        ax.set_title("Skills mentioned in latest India-eligible remote analyst postings"); ax.set_xlabel("Distinct postings")
        fig.tight_layout(); fig.savefig(OUT/"skill_demand.png",dpi=160); plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4))
    for scope,g in series.groupby("scope"): ax.plot(g.collected_at,g.postings,marker="o",label=scope)
    ax.set_title("Listings returned by weekly search snapshots"); ax.set_ylabel("Distinct listings"); ax.tick_params(axis="x",rotation=35); ax.legend()
    fig.tight_layout(); fig.savefig(OUT/"posting_counts.png",dpi=160); plt.close(fig)
    latest_ids=set(ids); d=demand[demand.pull_id.isin(latest_ids)].groupby("skill",as_index=False).postings.sum().sort_values("postings",ascending=False).head(10)
    total=int(coverage.postings.sum())
    latest_candidates=int(latest.iloc[-1].total_reported or 0)
    lines=["# Findings","","Data source: [Himalayas public jobs API](https://himalayas.app/api). This is a remote-job search sample filtered for India eligibility, not all jobs in India.","",f"Successful pulls: {len(pulls)}. The latest API search reported {latest_candidates} keyword candidates; the title filter retained {total} distinct analyst listings.","", "The collector keeps data analyst, analytics analyst, and business-intelligence analyst titles; content-only matches are excluded.",""]
    if total:
        lines += ["## Most frequently detected skills","",f"Counts are from the latest pull ({total} listings); a listing may mention multiple skills.",""]
        for _,r in d.iterrows(): lines.append(f"- {r.skill}: {int(r.postings)} listings ({100*r.postings/total:.1f}%).")
        salary_n=int(coverage.salary_ads.sum())
        lines += ["", "## Advertised salary coverage", "", f"{salary_n} of {total} latest listings ({100*salary_n/total:.1f}%) disclose a salary range. See `salary_by_experience.csv` for salary groups split by experience label, currency, and period. Values are not converted across currencies or periods.", ""]
    else: lines += ["No jobs were returned in the latest pull.",""]
    trend_note = "Only one successful pull exists, so this snapshot establishes the baseline; no week-over-week change can be inferred yet." if len(pulls) < 2 else "Compare the first and latest pull in the CSV. Changes reflect this API's remote listings and search coverage, not overall labor-market growth."
    lines += ["## Change across weekly pulls","", trend_note,"", "## Limits","", "The API supports country eligibility filtering but does not provide a reliable Chennai worksite filter. The project therefore measures remote roles open to people in India, not Chennai or on-site roles. Skill counts use transparent keyword matches, salary is missing for many listings, and Experience uses API labels when available plus explicit wording as a fallback."]
    (OUT/"findings.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    skill_rows="".join(f"<tr><td>{r.skill}</td><td>{int(r.postings)}</td><td>{100*r.postings/total:.1f}%</td></tr>" for _,r in d.iterrows()) if total and not d.empty else "<tr><td colspan='3'>No skill records yet</td></tr>"
    salary_rows="".join(f"<tr><td>{r.experience_level}</td><td>{r.salary_currency or 'Unspecified'}</td><td>{r.salary_period or 'Unspecified'}</td><td>{int(r.salary_ads)}</td><td>{r.mean_midpoint:,.0f}</td></tr>" for _,r in salary.iterrows()) if not salary.empty else "<tr><td colspan='5'>No disclosed salaries in the latest pull</td></tr>"
    counts_rows="".join(f"<tr><td>{r.collected_at}</td><td>{int(r.postings)}</td></tr>" for _,r in series.iterrows())
    html=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>India Remote Data Analyst Job Market</title>
    <style>:root{{color-scheme:dark;--bg:#080b11;--panel:#101622;--line:#243044;--text:#ecf2ff;--muted:#9ba9bd;--accent:#91a8ff;--mint:#79e0c1}}*{{box-sizing:border-box}}body{{margin:0;background:radial-gradient(ellipse at 80% -20%,#182441 0,transparent 46%),var(--bg);color:var(--text);font:16px/1.6 Inter,system-ui,sans-serif}}main{{max-width:1040px;margin:auto;padding:34px 22px 70px}}nav,footer{{color:var(--muted);font-size:13px;border-bottom:1px solid var(--line);padding:12px 0 20px}}footer{{border:0;border-top:1px solid var(--line);margin-top:32px;padding-top:20px}}h1{{font-size:clamp(38px,7vw,68px);line-height:1.05;letter-spacing:-.06em}}.note,.panel{{padding:20px;border:1px solid var(--line);border-radius:14px;background:var(--panel);margin:24px 0}}.note{{border-color:#48537a}}table{{border-collapse:collapse;width:100%}}th,td{{text-align:left;padding:10px;border-bottom:1px solid var(--line)}}th{{color:var(--mint)}}img{{max-width:100%;height:auto}}a{{color:var(--accent)}}</style>
    <main><nav>BHARATH B · DATA ANALYTICS</nav><h1>What do data analyst job ads ask for?</h1><p>India-eligible remote listings · refreshed by weekly snapshots</p>
    <section class="note">Source: <a href="https://himalayas.app/api">Himalayas public jobs API</a>. The API returned {latest_candidates} keyword candidates; the title filter retained {total} analyst listings. This is a remote-job sample filtered for India eligibility, not a census, and does not represent Chennai or on-site roles.</section>
    <section class="panel"><h2>Skills mentioned</h2>{'<img src="skill_demand.png" alt="Skill demand chart">' if (OUT/'skill_demand.png').exists() else ''}<table><thead><tr><th>Skill</th><th>Listings</th><th>Share</th></tr></thead><tbody>{skill_rows}</tbody></table></section>
    <section class="panel"><h2>Advertised salaries by experience label</h2><table><thead><tr><th>Experience</th><th>Currency</th><th>Period</th><th>Salary listings</th><th>Mean midpoint</th></tr></thead><tbody>{salary_rows}</tbody></table><p>Only postings with disclosed salary are included. Currencies and pay periods are kept separate.</p></section>
    <section class="panel"><h2>Weekly listing counts</h2>{'<img src="posting_counts.png" alt="Listing counts across weekly pulls">' if len(series)>1 else '<p>One pull establishes the baseline; repeat weekly to observe changes.</p>'}<table><thead><tr><th>Collected (UTC)</th><th>Listings</th></tr></thead><tbody>{counts_rows}</tbody></table></section>
    <p><a href="findings.md">Written findings</a> · <a href="skill_demand_latest.csv">Skill data</a> · <a href="salary_by_experience.csv">Salary data</a></p><footer>Analysis of remote listings available to India-based applicants. Source: Himalayas. Raw descriptions are not published.</footer></main></html>'''
    (OUT/"dashboard.html").write_text(html,encoding="utf-8")
    print(f"Wrote aggregate reports to {OUT}")

if __name__=="__main__": main()

