from scripts.utils.connect_postgres import connect_to_postgres
from scripts.utils.database_function import sql_command
from config.sql_script import CREATE_VIEW_QUALITY_CHECK_STAGING_ZONE, SELECT_QUALITY_CHECK_STAGING_ZONE
import pandas as pd
import plotly.express as px
from config.path import DASHBOARD_DIR
import os

def get_quality_data():
    connection = connect_to_postgres()
    cursor = connection.cursor()
    
    try:
        cursor.execute("DROP VIEW IF EXISTS quality_check_staging_zone CASCADE")
        sql_command(cursor, CREATE_VIEW_QUALITY_CHECK_STAGING_ZONE)
        connection.commit()
    except Exception as e:
        print(f"Error creating view: {e}")
        connection.rollback()
    
    results = sql_command(cursor, SELECT_QUALITY_CHECK_STAGING_ZONE)

    return results



if __name__ == "__main__":
    data = get_quality_data()
    
    columns = [
        "source_site",
        "ngay_cao",
        "total_data",
        "pass_rate",
        "quarantine_rate",
        "null_salary",
        "null_requirements",
        "null_benefits",
        "null_job_deadline",
        "null_search_keyword",
        "null_job_type",
        "null_job_industry",
        "null_experience_level",
        "null_education_level",
        "null_job_position",
        "null_scraped_at"
    ]
    
    df = pd.DataFrame(data, columns=columns)
    
    if not df.empty:
        # Ensure ngay_cao is datetime
        df['ngay_cao'] = pd.to_datetime(df['ngay_cao'])
        df = df.sort_values(by=['ngay_cao', 'source_site'], ascending=[False, True])
        
        # Calculate rates for null columns
        null_cols = [c for c in columns if c.startswith('null_')]
        for col in null_cols:
            rate_col = col.replace('null_', 'rate_null_')
            df[rate_col] = (df[col] / df['total_data'] * 100).round(2)

        # --- Summary Statistics ---
        latest_date = df['ngay_cao'].max()
        latest_df = df[df['ngay_cao'] == latest_date]
        
        total_records_latest = latest_df['total_data'].sum()
        source_count_latest = latest_df['source_site'].nunique()
        
        # Weighted pass rate for latest date
        if total_records_latest > 0:
            weighted_pass_rate = (latest_df['pass_rate'] * latest_df['total_data']).sum() / total_records_latest
        else:
            weighted_pass_rate = 0

        # --- Charts ---
        template = "plotly_white"
        
        # 1. Total Data Volume over Time
        fig_volume = px.bar(df, x='ngay_cao', y='total_data', color='source_site', 
                            title='Total Data Collected Over Time',
                            labels={'ngay_cao': 'Date', 'total_data': 'Total Records'})
        fig_volume.update_layout(template=template, legend_title_text='Source Site')
        
        # 2. Pass Rate over Time
        fig_pass = px.line(df, x='ngay_cao', y='pass_rate', color='source_site', 
                           title='Pass Rate Over Time (%)',
                           labels={'ngay_cao': 'Date', 'pass_rate': 'Pass Rate (%)'})
        fig_pass.update_layout(template=template, legend_title_text='Source Site')

        # 3. Quarantine Rate over Time
        fig_quarantine = px.line(df, x='ngay_cao', y='quarantine_rate', color='source_site', 
                           title='Quarantine Rate Over Time (%)',
                           labels={'ngay_cao': 'Date', 'quarantine_rate': 'Quarantine Rate (%)'})
        fig_quarantine.update_layout(template=template, legend_title_text='Source Site')
        
        # 4. Null Rates
        null_metrics_to_show = [
            'rate_null_salary',
            'rate_null_requirements',
            'rate_null_benefits',
            'rate_null_job_deadline',
            'rate_null_job_type',
            'rate_null_job_industry',
            'rate_null_experience_level',
            'rate_null_education_level',
            'rate_null_job_position'
        ]
        
        null_charts_html = ""
        for metric in null_metrics_to_show:
            title = metric.replace('rate_null_', '').replace('_', ' ').title() + ' Null Rate (%)'
            fig = px.line(df, x='ngay_cao', y=metric, color='source_site', 
                          title=title,
                          labels={'ngay_cao': 'Date', metric: 'Null Rate (%)'})
            fig.update_layout(template=template, legend_title_text='Source Site')
            
            null_charts_html += f"""
            <div class="col-lg-6 mb-5">
                <div class="chart-card">
                    {fig.to_html(full_html=False, include_plotlyjs=False)}
                </div>
            </div>
            """

        # Data Table - Only show data from the latest date
        latest_df_display = latest_df.copy()
        html_table = latest_df_display.to_html(index=False, classes='table table-striped table-bordered table-hover', table_id='dataTable')

        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Quality Check Dashboard</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/dataTables.bootstrap5.min.css">
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
                }}
                
                .navbar-brand {{
                    font-weight: 700;
                    font-size: 1.5rem;
                    background: var(--accent-gradient);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }}
                
                .navbar-brand i {{
                    background: var(--accent-gradient);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    margin-right: 0.5rem;
                }}
                
                .navbar-text {{
                    color: var(--text-secondary) !important;
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
                
                .stat-card {{
                    background: var(--bg-card);
                    backdrop-filter: blur(20px);
                    -webkit-backdrop-filter: blur(20px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: var(--border-radius);
                    padding: 1.5rem;
                    position: relative;
                    overflow: hidden;
                    transition: all 0.3s ease;
                    height: 100%;
                }}
                
                .stat-card:hover {{
                    transform: translateY(-5px);
                    box-shadow: var(--shadow);
                    border-color: rgba(255, 255, 255, 0.2);
                }}
                
                .stat-card::before {{
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 4px;
                    border-radius: var(--border-radius) var(--border-radius) 0 0;
                }}
                
                .stat-card.accent::before {{ background: var(--accent-gradient); }}
                .stat-card.success::before {{ background: var(--success-gradient); }}
                .stat-card.info::before {{ background: var(--info-gradient); }}
                .stat-card.warning::before {{ background: var(--warning-gradient); }}
                
                .stat-card-content {{
                    display: flex;
                    align-items: flex-start;
                    justify-content: space-between;
                }}
                
                .stat-card-info h6 {{
                    font-size: 0.75rem;
                    font-weight: 500;
                    color: var(--text-secondary);
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    margin-bottom: 0.5rem;
                }}
                
                .stat-card-info h3 {{
                    font-size: 1.75rem;
                    font-weight: 700;
                    margin: 0;
                }}
                
                .stat-card.accent .stat-card-info h3 {{
                    background: var(--accent-gradient);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }}
                
                .stat-card.success .stat-card-info h3 {{
                    background: var(--success-gradient);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }}
                
                .stat-card.info .stat-card-info h3 {{
                    background: var(--info-gradient);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }}
                
                .stat-card.warning .stat-card-info h3 {{
                    background: var(--warning-gradient);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }}
                
                .stat-icon {{
                    width: 50px;
                    height: 50px;
                    border-radius: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 1.25rem;
                }}
                
                .stat-card.accent .stat-icon {{
                    background: var(--accent-gradient);
                    color: white;
                }}
                
                .stat-card.success .stat-icon {{
                    background: var(--success-gradient);
                    color: white;
                }}
                
                .stat-card.info .stat-icon {{
                    background: var(--info-gradient);
                    color: white;
                }}
                
                .stat-card.warning .stat-icon {{
                    background: var(--warning-gradient);
                    color: white;
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
                
                .table-card {{
                    background: var(--bg-card);
                    backdrop-filter: blur(20px);
                    -webkit-backdrop-filter: blur(20px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: var(--border-radius);
                    overflow: hidden;
                    margin-bottom: 2rem;
                }}
                
                .table-card-header {{
                    background: rgba(255, 255, 255, 0.03);
                    padding: 1rem 1.5rem;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                    display: flex;
                    align-items: center;
                }}
                
                .table-card-header i {{
                    margin-right: 0.75rem;
                    background: var(--accent-gradient);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }}
                
                .table-card-header span {{
                    font-weight: 600;
                }}
                
                .table-card-body {{
                    padding: 1.5rem;
                }}
                
                .table {{
                    color: var(--text-primary) !important;
                    margin-bottom: 0;
                }}
                
                .table thead th {{
                    background: rgba(255, 255, 255, 0.05);
                    border-color: rgba(255, 255, 255, 0.1) !important;
                    color: var(--text-secondary);
                    font-weight: 600;
                    font-size: 0.75rem;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    padding: 1rem;
                }}
                
                .table tbody td {{
                    border-color: rgba(255, 255, 255, 0.05) !important;
                    padding: 0.875rem 1rem;
                    vertical-align: middle;
                }}
                
                .table-striped tbody tr:nth-of-type(odd) {{
                    background-color: rgba(255, 255, 255, 0.02);
                }}
                
                .table-hover tbody tr:hover {{
                    background-color: rgba(255, 255, 255, 0.05);
                }}
                
                .dataTables_wrapper .dataTables_length,
                .dataTables_wrapper .dataTables_filter,
                .dataTables_wrapper .dataTables_info,
                .dataTables_wrapper .dataTables_paginate {{
                    color: var(--text-secondary) !important;
                    padding: 0.5rem 0;
                }}
                
                .dataTables_wrapper .dataTables_filter input,
                .dataTables_wrapper .dataTables_length select {{
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    color: var(--text-primary);
                    padding: 0.5rem 1rem;
                }}
                
                .dataTables_wrapper .dataTables_filter input:focus {{
                    outline: none;
                    border-color: rgba(102, 126, 234, 0.5);
                    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
                }}
                
                .dataTables_wrapper .dataTables_paginate .paginate_button {{
                    color: var(--text-secondary) !important;
                    background: transparent !important;
                    border: 1px solid rgba(255, 255, 255, 0.1) !important;
                    border-radius: 8px !important;
                    margin: 0 2px;
                }}
                
                .dataTables_wrapper .dataTables_paginate .paginate_button:hover {{
                    background: rgba(255, 255, 255, 0.05) !important;
                    color: var(--text-primary) !important;
                }}
                
                .dataTables_wrapper .dataTables_paginate .paginate_button.current {{
                    background: var(--accent-gradient) !important;
                    color: white !important;
                    border: none !important;
                }}
                
                .row {{ margin-bottom: 1.5rem; }}
                .mb-4 {{ margin-bottom: 1.5rem !important; }}
                .mb-5 {{ margin-bottom: 2rem !important; }}
                
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
                
                @media (max-width: 768px) {{
                    .container-fluid {{ padding: 0 1rem; }}
                    .stat-card {{ margin-bottom: 1rem; }}
                    .navbar {{ padding: 1rem; }}
                }}
            </style>
        </head>
        <body>
            <nav class="navbar">
                <div class="container-fluid d-flex justify-content-between align-items-center">
                    <a class="navbar-brand" href="#"><i class="fas fa-chart-line"></i>Data Quality Dashboard</a>
                    <span class="navbar-text">
                        <i class="fas fa-clock me-1"></i> Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
                    </span>
                </div>
            </nav>

            <div class="container-fluid">
                <div class="section-header">
                    <i class="fas fa-chart-pie"></i>
                    <h2>Summary Statistics</h2>
                </div>
                
                <div class="row mb-5">
                    <div class="col-md-6 col-lg-3 mb-4">
                        <div class="stat-card accent">
                            <div class="stat-card-content">
                                <div class="stat-card-info">
                                    <h6>Latest Date</h6>
                                    <h3>{latest_date.strftime('%Y-%m-%d')}</h3>
                                </div>
                                <div class="stat-icon">
                                    <i class="fas fa-calendar-alt"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-3 mb-4">
                        <div class="stat-card success">
                            <div class="stat-card-content">
                                <div class="stat-card-info">
                                    <h6>Total Records</h6>
                                    <h3>{total_records_latest:,.0f}</h3>
                                </div>
                                <div class="stat-icon">
                                    <i class="fas fa-database"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-3 mb-4">
                        <div class="stat-card info">
                            <div class="stat-card-content">
                                <div class="stat-card-info">
                                    <h6>Source Sites</h6>
                                    <h3>{source_count_latest}</h3>
                                </div>
                                <div class="stat-icon">
                                    <i class="fas fa-network-wired"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6 col-lg-3 mb-4">
                        <div class="stat-card warning">
                            <div class="stat-card-content">
                                <div class="stat-card-info">
                                    <h6>Avg Pass Rate</h6>
                                    <h3>{weighted_pass_rate:.2f}%</h3>
                                </div>
                                <div class="stat-icon">
                                    <i class="fas fa-check-circle"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="section-header">
                    <i class="fas fa-chart-bar"></i>
                    <h2>Data Volume</h2>
                </div>
                
                <div class="row">
                    <div class="col-12 mb-5">
                        <div class="chart-card">
                            {fig_volume.to_html(full_html=False, include_plotlyjs='cdn')}
                        </div>
                    </div>
                </div>

                <div class="section-header">
                    <i class="fas fa-chart-line"></i>
                    <h2>Quality Metrics</h2>
                </div>
                
                <div class="row">
                    <div class="col-lg-6 mb-5">
                        <div class="chart-card">
                            {fig_pass.to_html(full_html=False, include_plotlyjs=False)}
                        </div>
                    </div>
                    <div class="col-lg-6 mb-5">
                        <div class="chart-card">
                            {fig_quarantine.to_html(full_html=False, include_plotlyjs=False)}
                        </div>
                    </div>
                </div>
                
                <div class="section-header">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h2>Null Rate Analysis</h2>
                </div>
                
                <div class="row">
                    {null_charts_html}
                </div>

                <div class="section-header">
                    <i class="fas fa-table"></i>
                    <h2>Detailed Data</h2>
                </div>
                
                <div class="table-card">
                    <div class="table-card-header">
                        <i class="fas fa-table"></i>
                        <span>Quality Data (Latest Date: {latest_date.strftime('%Y-%m-%d')})</span>
                    </div>
                    <div class="table-card-body">
                        <div class="table-responsive">
                            {html_table}
                        </div>
                    </div>
                </div>
            </div>
            
            <footer>
                <p><i class="fas fa-shield-halved me-2"></i>Data Quality Monitoring System &copy; {pd.Timestamp.now().year}</p>
            </footer>

            <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
            <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
            <script src="https://cdn.datatables.net/1.13.6/js/dataTables.bootstrap5.min.js"></script>
            <script>
                $(document).ready(function() {{
                    $('#dataTable').DataTable({{
                        "order": [[ 1, "desc" ]],
                        "pageLength": 25,
                        "language": {{
                            "search": "<i class='fas fa-search me-2'></i>",
                            "searchPlaceholder": "Filter records..."
                        }}
                    }});
                }});
            </script>
        </body>
        </html>
        """
        
        # Tạo folder nếu chưa có
        os.makedirs(DASHBOARD_DIR, exist_ok=True)
        
        output_file = f"{DASHBOARD_DIR}/quality_check_report.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"Successfully generated dashboard: {output_file}")
    else:
        print("No data found to generate report.")
