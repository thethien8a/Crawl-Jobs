from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from config.path import DASHBOARD_DIR
from scripts.utils.connect_postgres import connect_to_postgres
from scripts.utils.database_function import sql_command

TABLE_NAME = "public_intermediate_bronze_silver.int_jobs_cleaned"

SQL_RATIO_OTHER_INDUSTRY = f"""
SELECT
    DATE(scraped_at) AS scraped_date,
    COUNT(*) FILTER (WHERE job_industry = 'Khác')::float
        / NULLIF(COUNT(*), 0) * 100 AS ratio_other_industry
FROM {TABLE_NAME}
WHERE source_site = 'linkedin.com'
GROUP BY DATE(scraped_at)
ORDER BY DATE(scraped_at)
"""

SQL_RATIO_NO_JOB_POSITION = f"""
SELECT
    DATE(scraped_at) AS scraped_date,
    COUNT(*) FILTER (WHERE job_position = 'Không đề cập')::float
        / NULLIF(COUNT(*), 0) * 100 AS ratio_no_job_position
FROM {TABLE_NAME}
WHERE source_site = 'vietnamworks.com'
GROUP BY DATE(scraped_at)
ORDER BY DATE(scraped_at)
"""


def _fetch_dataframe(sql: str, columns: list[str]) -> pd.DataFrame:
    connection = connect_to_postgres()
    if connection is None:
        raise RuntimeError("Cannot connect to PostgreSQL database.")

    cursor = connection.cursor()
    try:
        results = sql_command(cursor, sql) or []
        return pd.DataFrame(results, columns=columns)
    finally:
        cursor.close()
        connection.close()


def _build_line_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    y_label: str,
) -> go.Figure:
    if df.empty:
        fig = go.Figure()
        fig.add_annotation(
            text="No data available",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16),
        )
        fig.update_layout(title=title, template="plotly_white")
        return fig

    df = df.copy()
    df[x_col] = pd.to_datetime(df[x_col])
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        title=title,
        labels={x_col: "Date", y_col: y_label},
    )
    fig.update_layout(
        template="plotly_white",
        yaxis=dict(range=[0, 100], ticksuffix="%")
    )
    return fig


def generate_quality_gate_report(output_path: Path) -> Path:
    df_other_industry = _fetch_dataframe(
        SQL_RATIO_OTHER_INDUSTRY,
        columns=["scraped_date", "ratio_other_industry"],
    )
    df_no_job_position = _fetch_dataframe(
        SQL_RATIO_NO_JOB_POSITION,
        columns=["scraped_date", "ratio_no_job_position"],
    )

    fig_other_industry = _build_line_chart(
        df_other_industry,
        x_col="scraped_date",
        y_col="ratio_other_industry",
        title="LinkedIn: Rate of 'Khác' in job_industry",
        y_label="Rate (%)",
    )
    fig_no_job_position = _build_line_chart(
        df_no_job_position,
        x_col="scraped_date",
        y_col="ratio_no_job_position",
        title="VietnamWorks: Rate of 'Không đề cập' in job_position",
        y_label="Rate (%)",
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quality Check Gate</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        :root {{
            --bg-primary: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            --bg-card: rgba(255, 255, 255, 0.05);
            --text-primary: #ffffff;
            --text-secondary: #a0aec0;
            --accent-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --success-gradient: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            --warning-gradient: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            --info-gradient: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            --border-radius: 16px;
            --shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            background: var(--bg-primary);
            min-height: 100vh;
            font-family: 'Inter', sans-serif;
            color: var(--text-primary);
            padding: 0;
        }}
        
        .navbar {{
            background: rgba(255, 255, 255, 0.05) !important;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            padding: 1rem 2rem;
            margin-bottom: 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .navbar-brand {{
            font-weight: 700;
            font-size: 1.5rem;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-decoration: none;
        }}
        
        .navbar-brand i {{
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-right: 0.5rem;
        }}
        
        .navbar-text {{
            color: var(--text-secondary);
            font-size: 0.875rem;
        }}
        
        .container-fluid {{
            padding: 0 2rem;
            max-width: 1800px;
            margin: 0 auto;
        }}
        
        .section-header {{
            display: flex;
            align-items: center;
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .section-header i {{
            font-size: 1.25rem;
            margin-right: 0.75rem;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .section-header h2 {{
            font-size: 1.25rem;
            font-weight: 600;
            margin: 0;
        }}
        
        .chart-card {{
            background: var(--bg-card);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: var(--border-radius);
            padding: 1.5rem;
            transition: all 0.3s ease;
            height: 100%;
        }}
        
        .chart-card:hover {{
            box-shadow: var(--shadow);
            border-color: rgba(255, 255, 255, 0.2);
        }}
        
        .row {{
            display: flex;
            flex-wrap: wrap;
            margin: 0 -0.75rem;
            margin-bottom: 1.5rem;
        }}
        
        .col-lg-6 {{
            flex: 0 0 50%;
            max-width: 50%;
            padding: 0 0.75rem;
        }}
        
        .mb-4 {{ margin-bottom: 1.5rem; }}
        
        footer {{
            margin-top: 3rem;
            padding: 2rem;
            text-align: center;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            background: linear-gradient(180deg, transparent 0%, rgba(102, 126, 234, 0.05) 100%);
        }}
        
        footer p {{
            color: var(--text-secondary);
            font-size: 0.875rem;
            margin: 0;
        }}
        
        .plotly-graph-div {{
            border-radius: 8px;
        }}
        
        @media (max-width: 992px) {{
            .col-lg-6 {{ flex: 0 0 100%; max-width: 100%; }}
        }}
        
        @media (max-width: 768px) {{
            .container-fluid {{ padding: 0 1rem; }}
            .navbar {{ padding: 1rem; flex-direction: column; gap: 0.5rem; }}
        }}
    </style>
</head>
<body>
    <nav class="navbar">
        <a class="navbar-brand" href="#"><i class="fas fa-shield-halved"></i>Quality Check Gate</a>
        <span class="navbar-text">
            <i class="fas fa-clock"></i> Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
        </span>
    </nav>

    <div class="container-fluid">
        <div class="section-header">
            <i class="fas fa-chart-line"></i>
            <h2>Quality Gate Metrics</h2>
        </div>
        
        <div class="row">
            <div class="col-lg-6 mb-4">
                <div class="chart-card">
                    {fig_other_industry.to_html(full_html=False, include_plotlyjs=False)}
                </div>
            </div>
            <div class="col-lg-6 mb-4">
                <div class="chart-card">
                    {fig_no_job_position.to_html(full_html=False, include_plotlyjs=False)}
                </div>
            </div>
        </div>
    </div>

    <footer>
        <p><i class="fas fa-shield-halved"></i> Data Quality Gate Report &copy; {pd.Timestamp.now().year}</p>
    </footer>
</body>
</html>
"""

    output_path.write_text(html_content, encoding="utf-8")
    return output_path


if __name__ == "__main__":
    report_path = DASHBOARD_DIR / "quality_check_gate.html"
    generate_quality_gate_report(report_path)
    print(f"Generated report: {report_path}")
