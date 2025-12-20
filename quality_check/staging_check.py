from utils.connect_postgres import connect_to_postgres
from utils.database_function import sql_command
from quality_check.sql_command import CREATE_VIEW_QUALITY_CHECK_STAGING_ZONE, SELECT_QUALITY_CHECK_STAGING_ZONE
import pandas as pd
import plotly.express as px
from config.path import DASHBOARD_DIR

def get_quality_data():
    connection = connect_to_postgres()
    cursor = connection.cursor()
    
    try:
        cursor.execute("SELECT 1 FROM pg_views WHERE viewname = 'quality_check_staging_zone'")
        if not cursor.fetchone():
            sql_command(cursor, CREATE_VIEW_QUALITY_CHECK_STAGING_ZONE)
    except Exception as e:
        print(e)
    
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
            'rate_null_search_keyword',
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
            <div class="col-md-6 mb-5">
                <div class="card chart-card">
                    <div class="card-body">
                        {fig.to_html(full_html=False, include_plotlyjs=False)}
                    </div>
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
            <!-- Bootswatch Flatly Theme -->
            <link rel="stylesheet" href="https://bootswatch.com/4/flatly/bootstrap.min.css">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css">
            <link rel="stylesheet" href="https://cdn.datatables.net/1.10.22/css/dataTables.bootstrap4.min.css">
            <style>
                body {{ background-color: #ecf0f1; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
                .navbar {{ margin-bottom: 30px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .card {{ border: none; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); transition: transform 0.2s; }}
                .card:hover {{ transform: translateY(-5px); }}
                .stat-card .card-body {{ display: flex; align-items: center; justify-content: space-between; }}
                .stat-icon {{ font-size: 2.5rem; opacity: 0.3; }}
                .chart-card {{ height: 100%; }}
                footer {{ margin-top: 50px; padding: 20px 0; color: #7f8c8d; text-align: center; }}
                .mb-5 {{ margin-bottom: 3rem !important; }}
            </style>
        </head>
        <body>
            <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
                <div class="container-fluid">
                    <a class="navbar-brand" href="#"><i class="fas fa-chart-line mr-2"></i>Data Quality Dashboard</a>
                    <span class="navbar-text text-white">
                        Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
                    </span>
                </div>
            </nav>

            <div class="container-fluid">
                <!-- Summary Stats -->
                <div class="row mb-4">
                    <div class="col-md-3">
                        <div class="card stat-card bg-primary text-white">
                            <div class="card-body">
                                <div>
                                    <h6 class="card-title mb-0">Latest Date</h6>
                                    <h3 class="font-weight-bold">{latest_date.strftime('%Y-%m-%d')}</h3>
                                </div>
                                <i class="fas fa-calendar-alt stat-icon"></i>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card bg-success text-white">
                            <div class="card-body">
                                <div>
                                    <h6 class="card-title mb-0">Total Records (Latest Date)</h6>
                                    <h3 class="font-weight-bold">{total_records_latest:,.0f}</h3>
                                </div>
                                <i class="fas fa-database stat-icon"></i>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card bg-info text-white">
                            <div class="card-body">
                                <div>
                                    <h6 class="card-title mb-0">Distinct Source Sites (Latest Date)</h6>
                                    <h3 class="font-weight-bold">{source_count_latest}</h3>
                                </div>
                                <i class="fas fa-network-wired stat-icon"></i>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stat-card bg-warning text-white">
                            <div class="card-body">
                                <div>
                                    <h6 class="card-title mb-0">Avg Pass Rate (Latest Date)</h6>
                                    <h3 class="font-weight-bold">{weighted_pass_rate:.2f}%</h3>
                                </div>
                                <i class="fas fa-check-circle stat-icon"></i>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Charts Grid -->
                <div class="row">
                    <div class="col-md-12 mb-5">
                        <div class="card chart-card">
                            <div class="card-body">
                                {fig_volume.to_html(full_html=False, include_plotlyjs='cdn')}
                            </div>
                        </div>
                    </div>
                </div>

                <div class="row">
                    <div class="col-md-6 mb-5">
                        <div class="card chart-card">
                            <div class="card-body">
                                {fig_pass.to_html(full_html=False, include_plotlyjs=False)}
                            </div>
                        </div>
                    </div>
                    <div class="col-md-6 mb-5">
                        <div class="card chart-card">
                            <div class="card-body">
                                {fig_quarantine.to_html(full_html=False, include_plotlyjs=False)}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="row">
                    {null_charts_html}
                </div>

                <!-- Data Table -->
                <div class="card table-card">
                    <div class="card-header bg-white">
                        <i class="fas fa-table mr-2"></i> Detailed Quality Data (Latest Date: {latest_date.strftime('%Y-%m-%d')})
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            {html_table}
                        </div>
                    </div>
                </div>
            </div>
            
            <footer>
                <p>Data Quality Monitoring System &copy; {pd.Timestamp.now().year}</p>
            </footer>

            <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
            <script src="https://cdn.datatables.net/1.10.22/js/jquery.dataTables.min.js"></script>
            <script src="https://cdn.datatables.net/1.10.22/js/dataTables.bootstrap4.min.js"></script>
            <script>
                $(document).ready(function() {{
                    $('#dataTable').DataTable({{
                        "order": [[ 1, "desc" ]],
                        "pageLength": 25,
                        "language": {{
                            "search": "Filter records:"
                        }}
                    }});
                }});
            </script>
        </body>
        </html>
        """
        
        output_file = f"{DASHBOARD_DIR}/quality_check_report.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        print(f"Successfully generated dashboard: {output_file}")
    else:
        print("No data found to generate report.")
