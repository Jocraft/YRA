from datetime import date
from django.shortcuts import render
from .forms import AnalysisForm
from accounts.models import Student, User
import pandas as pd
import plotly.express as px
from scipy import stats
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go


def analyze(request):
    # Get initial data for the form
    initial_data = {}
    available_years = []
    
    if request.method == 'POST':
        column = request.POST.get('column')
        visualization_type = request.POST.get('visualization_type', 'numerical')
        
        if visualization_type == 'date' and column:
            students = Student.objects.all()
            users = User.objects.filter(id__in=[student.student.id for student in students if student.student]).all()
            
            # Get dates based on column
            if column == 'date_of_birth':
                dates = [user.date_of_birth for user in users if user.date_of_birth]
            elif column == 'enrollment_date':
                dates = [user.enrollment_date for user in users if user.enrollment_date]
            elif column == 'expected_graduation_date':
                dates = [user.expected_graduation_date for user in users if user.expected_graduation_date]
            else:
                dates = []
            
            # Get unique years
            available_years = sorted(list(set(date.year for date in dates if date)))
    
    # Initialize form with available years
    form = AnalysisForm(request.POST or None, available_years=available_years)
    plot_html = None
    statistics = None
    column_values = None
    hypothesis_results = None
    analysis_type = request.POST.get('analysis_type', 'descriptive')

    if request.method == 'POST' and form.is_valid():
        column = form.cleaned_data['column']
        group_by = form.cleaned_data.get('group_by')
        visualization_type = form.cleaned_data.get('visualization_type', 'numerical')
        selected_year = form.cleaned_data.get('selected_year')

        students = Student.objects.all()
        users = User.objects.filter(id__in=[student.student.id for student in students if student.student]).all()

        # Store original dates for date-based visualization
        original_dates = []
        
        if column == 'program_name':
            data = [str(student.program.title) if student.program else None for student in students]
        elif column == 'date_of_birth':
            if visualization_type == 'date':
                data = [user.date_of_birth for user in users if user.date_of_birth]
                original_dates = data.copy()
            else:
                data = [
                    (date.today().year - user.date_of_birth.year - ((date.today().month, date.today().day) < (user.date_of_birth.month, user.date_of_birth.day)))
                    if user.date_of_birth else None
                    for user in users
                ]
        elif column == 'enrollment_date':
            if visualization_type == 'date':
                data = [user.enrollment_date for user in users if user.enrollment_date]
                original_dates = data.copy()
            else:
                data = [
                    (date.today().year - user.enrollment_date.year) * 12 + date.today().month - user.enrollment_date.month
                    if user.enrollment_date else None
                    for user in users
                ]
        elif column == 'expected_graduation_date':
            if visualization_type == 'date':
                data = [user.expected_graduation_date for user in users if user.expected_graduation_date]
                original_dates = data.copy()
            else:
                data = [
                    (user.expected_graduation_date.year - date.today().year) * 12 + user.expected_graduation_date.month - date.today().month
                    if user.expected_graduation_date else None
                    for user in users
                ]
        elif hasattr(User, column):
            data = list(students.values_list(f'student__{column}', flat=True))
        elif hasattr(Student, column):
            data = list(students.values_list(column, flat=True))
        else:
            data = []

        # Prepare DataFrame
        program_names = [str(student.program.title) if student.program else None for student in students]
        column_values = data
        df = pd.DataFrame({'column': data, 'program': program_names}).dropna()

        if group_by and group_by != '':
            if group_by == 'program_name':
                df['group_by'] = program_names
            elif group_by == 'date_of_birth':
                df['group_by'] = [
                    (date.today().year - user.date_of_birth.year - ((date.today().month, date.today().day) < (user.date_of_birth.month, user.date_of_birth.day)))
                    if user.date_of_birth else None
                    for user in users
                ]
            elif group_by == 'enrollment_date':
                df['group_by'] = [
                    (date.today().year - user.enrollment_date.year) * 12 + date.today().month - user.enrollment_date.month
                    if user.enrollment_date else None
                    for user in users
                ]
            elif group_by == 'expected_graduation_date':
                df['group_by'] = [
                    (user.expected_graduation_date.year - date.today().year) * 12 + user.expected_graduation_date.month - date.today().month
                    if user.expected_graduation_date else None
                    for user in users
                ]
            elif hasattr(User, group_by):
                df['group_by'] = list(students.values_list(f'student__{group_by}', flat=True))
            elif hasattr(Student, group_by):
                df['group_by'] = list(students.values_list(group_by, flat=True))

        if not df.empty:
            if analysis_type == 'hypothesis':
                if pd.api.types.is_numeric_dtype(df['column']):
                    programs = df['program'].unique()
                    if len(programs) >= 2:
                        groups = [df[df['program'] == prog]['column'].values for prog in programs]
                        if len(groups) >= 2:
                            f_stat, p_value = stats.kruskal(*groups)
                            means = df.groupby('program')['column'].median()
                            hypothesis_results = {
                                'test': 'Kruskal-Wallis',
                                'question': f"Does {column} differ significantly across programs?",
                                'p_value': f"{p_value:.4f}",
                                'result': f"{'Significant' if p_value < 0.05 else 'No significant'} differences (Averages (Medians): {means.to_dict()})"
                            }
                else:
                    # Chi-square test
                    contingency = pd.crosstab(df['column'], df['program'])
                    if contingency.size > 0:
                        chi2, p_value = stats.chi2_contingency(contingency)[:2]
                        hypothesis_results = {
                            'test': 'Chi-square',
                            'question': f"Is there a relationship between the program and {column}?",
                            'p_value': f"{p_value:.4f}",
                            'result': f"{'Significant' if p_value < 0.05 else 'No significant'} association"
                        }
                
                # Create visualization
                if pd.api.types.is_numeric_dtype(df['column']):
                    fig = px.box(df, x='program', y='column', 
                               title=f"Distribution of {column} by Program")
                else:
                    percentages = pd.crosstab(df['column'], df['program'], normalize='columns') * 100
                    percentages_rounded = percentages.round(2)
                    fig = px.bar(
                        percentages_rounded.T,
                        title=f"Program Distribution by {column}",
                        labels={"value": "Percentage (%)", "index": "Program", "variable": column},
                        barmode="group"
                    )
                
                plot_html = fig.to_html(full_html=False)
                hypothesis_results['plot_html'] = plot_html

            else:  # Descriptive analysis
                if visualization_type == 'date' and original_dates:
                    # Date-based visualization code
                    df['date'] = pd.to_datetime(original_dates)
                    
                    # Filter by year if selected
                    if selected_year:
                        df = df[df['date'].dt.year == int(selected_year)]
                    
                    if df.empty:
                        statistics = {'Message': f'No data available for year {selected_year}'}
                    else:
                        df = df.sort_values('date')
                        
                        if selected_year:
                            # Single bar plot for selected year
                            df['month'] = df['date'].dt.month
                            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                         'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                            
                            if 'group_by' in df.columns:
                                # Create pivot table for grouped monthly data
                                monthly_grouped = pd.pivot_table(
                                    df,
                                    values='date',
                                    index='month',
                                    columns='group_by',
                                    aggfunc='count',
                                    fill_value=0
                                ).reindex(range(1, 13), fill_value=0)
                                
                                # Rename index with month names
                                monthly_grouped.index = month_names
                                
                                fig = go.Figure()
                                
                                # Add bars for each group
                                for group in monthly_grouped.columns:
                                    fig.add_trace(go.Bar(
                                        name=str(group),
                                        x=month_names,
                                        y=monthly_grouped[group],
                                        text=monthly_grouped[group],
                                        textposition='auto'
                                    ))
                                
                                fig.update_layout(
                                    title_text=f"Monthly Distribution for {column} by {group_by} in {selected_year}",
                                    xaxis_title="Month",
                                    yaxis_title="Count",
                                    height=500,
                                    barmode='group',
                                    bargap=0.2,
                                    showlegend=True
                                )
                                
                                # Update statistics for grouped data
                                statistics = {
                                    'Year Statistics': {
                                        'Total Count': len(df),
                                        'Group Totals': monthly_grouped.sum().to_dict(),
                                        'Most Common Month by Group': {
                                            str(group): month_names[monthly_grouped[group].argmax()]
                                            for group in monthly_grouped.columns
                                        }
                                    }
                                }
                            
                            else:
                                # Original single group visualization
                                monthly_counts = df['month'].value_counts().sort_index()
                                
                                # Create a complete series with all months (1-12)
                                all_months = pd.Series(0, index=range(1, 13))
                                # Update with actual counts
                                all_months.update(monthly_counts)
                                # Sort to ensure months are in order
                                monthly_counts = all_months.sort_index()
                                
                                fig = go.Figure()
                                fig.add_trace(go.Bar(
                                    x=month_names,
                                    y=monthly_counts.values,
                                    name='Count',
                                    text=monthly_counts.values,
                                    textposition='auto'
                                ))
                                
                                fig.update_layout(
                                    title_text=f"Monthly Distribution for {column} in {selected_year}",
                                    xaxis_title="Month",
                                    yaxis_title="Count",
                                    height=500,
                                    showlegend=False,
                                    bargap=0.2
                                )
                                
                                # Update statistics to use the complete monthly counts
                                max_month_idx = monthly_counts.idxmax() - 1  # Convert to 0-based index
                                statistics = {
                                    'Year Statistics': {
                                        'Total Count': len(df),
                                        'Most Common Month': month_names[max_month_idx],
                                        'Highest Count': monthly_counts.max(),
                                        'Average Monthly Count': f"{monthly_counts.mean():.1f}"
                                    }
                                }
                        else:
                            # Original four plots for all years
                            fig = make_subplots(rows=2, cols=2,
                                              subplot_titles=("Timeline Distribution",
                                                            "Monthly Distribution",
                                                            "Yearly Distribution",
                                                            "Cumulative Distribution"))

                            # Timeline plot
                            fig.add_trace(go.Scatter(x=df['date'], y=[1]*len(df), mode='markers',
                                                   name='Individual Dates'), row=1, col=1)

                            # Monthly distribution
                            monthly_counts = df['date'].dt.month.value_counts().sort_index()
                            fig.add_trace(go.Bar(x=monthly_counts.index, y=monthly_counts.values,
                                               name='Monthly Distribution'), row=1, col=2)

                            # Yearly distribution
                            yearly_counts = df['date'].dt.year.value_counts().sort_index()
                            fig.add_trace(go.Bar(x=yearly_counts.index, y=yearly_counts.values,
                                               name='Yearly Distribution'), row=2, col=1)

                            # Cumulative distribution
                            df_sorted = df.sort_values('date')
                            df_sorted['cumcount'] = range(1, len(df_sorted) + 1)
                            fig.add_trace(go.Scatter(x=df_sorted['date'], y=df_sorted['cumcount'],
                                                   name='Cumulative Count'), row=2, col=2)

                            fig.update_layout(height=800, showlegend=True,
                                            title_text=f"Date-based Analysis of {column}",
                                            title_x=0.5)

                            fig.update_xaxes(title_text="Date", row=1, col=1)
                            fig.update_yaxes(title_text="Count", row=1, col=1)
                            fig.update_xaxes(title_text="Month", row=1, col=2)
                            fig.update_yaxes(title_text="Count", row=1, col=2)
                            fig.update_xaxes(title_text="Year", row=2, col=1)
                            fig.update_yaxes(title_text="Count", row=2, col=1)
                            fig.update_xaxes(title_text="Date", row=2, col=2)
                            fig.update_yaxes(title_text="Cumulative Count", row=2, col=2)

                            statistics = {
                                'Date Range': {
                                    'Start': df['date'].min().strftime('%Y-%m-%d'),
                                    'End': df['date'].max().strftime('%Y-%m-%d')
                                },
                                'Distribution': {
                                    'Most Common Year': yearly_counts.index[0],
                                    'Most Common Month': monthly_counts.index[0],
                                    'Total Count': len(df)
                                }
                            }

                        plot_html = fig.to_html(full_html=False)

                elif pd.api.types.is_numeric_dtype(df['column']):
                    # Numeric data visualization
                    if 'group_by' in df.columns:
                        # Grouped numeric data
                        fig = make_subplots(rows=1, cols=2,
                                          subplot_titles=("Box Plot by Group",
                                                        "Distribution by Group"))
                        
                        # Box plot
                        fig.add_trace(go.Box(x=df['group_by'], y=df['column'],
                                           name='Distribution'), row=1, col=1)
                        
                        # Violin plot
                        for group in df['group_by'].unique():
                            group_data = df[df['group_by'] == group]['column']
                            fig.add_trace(go.Violin(x=[group] * len(group_data),
                                                  y=group_data,
                                                  name=str(group)), row=1, col=2)
                        
                        fig.update_layout(height=500, showlegend=False,
                                        title_text=f"Analysis of {column} by {group_by}")
                        
                        statistics = df.groupby('group_by')['column'].describe().to_dict()
                    else:
                        # Non-grouped numeric data
                        from scipy import stats as scipy_stats
                        
                        basic_stats = df['column'].describe()
                        skewness = df['column'].skew()
                        kurtosis = df['column'].kurtosis()
                        
                        _, normality_p_value = scipy_stats.shapiro(df['column'])
                        
                        fig = make_subplots(rows=2, cols=2,
                                          subplot_titles=("Distribution",
                                                        "Box Plot",
                                                        "Q-Q Plot",
                                                        "Trend"))
                        
                        # Histogram with normal curve
                        hist_data = df['column']
                        counts, bins = np.histogram(hist_data, bins=30)
                        bins_mean = 0.5 * (bins[:-1] + bins[1:])
                        
                        mu, std = scipy_stats.norm.fit(hist_data)
                        pdf = scipy_stats.norm.pdf(bins_mean, mu, std) * len(hist_data) * (bins[1] - bins[0])
                        
                        fig.add_trace(go.Histogram(x=hist_data, name="Frequency", nbinsx=30),
                                    row=1, col=1)
                        fig.add_trace(go.Scatter(x=bins_mean, y=pdf, name="Normal Fit",
                                               line=dict(color='red')), row=1, col=1)
                        
                        # Box plot
                        fig.add_trace(go.Box(y=df['column'], name=column,
                                           boxpoints='outliers'), row=1, col=2)
                        
                        # Q-Q plot
                        qq = scipy_stats.probplot(df['column'], dist="norm")
                        fig.add_trace(go.Scatter(x=qq[0][0], y=qq[0][1],
                                               mode='markers', name='Q-Q Plot'),
                                    row=2, col=1)
                        
                        line_x = np.linspace(min(qq[0][0]), max(qq[0][0]), 100)
                        line_y = qq[1][0] * line_x + qq[1][1]
                        fig.add_trace(go.Scatter(x=line_x, y=line_y, mode='lines',
                                               name='Normal Line',
                                               line=dict(color='red')), row=2, col=1)
                        
                        # Trend plot
                        fig.add_trace(go.Scatter(y=df['column'], mode='markers+lines',
                                               name='Trend'), row=2, col=2)
                        
                        fig.update_layout(height=800, showlegend=True,
                                        title_text=f"Analysis of {column}")
                        
                        statistics = {
                            'Basic Statistics': basic_stats.to_dict(),
                            'Additional Metrics': {
                                'Skewness': f"{skewness:.3f}",
                                'Kurtosis': f"{kurtosis:.3f}",
                                'Normality Test': {
                                    'Test': 'Shapiro-Wilk',
                                    'p-value': f"{normality_p_value:.3f}",
                                    'Interpretation': 'Normal' if normality_p_value > 0.05 else 'Non-normal'
                                }
                            }
                        }
                else:
                    # Categorical data visualization
                    if 'group_by' in df.columns:
                        grouped = df.groupby('group_by')['column'].value_counts().unstack(fill_value=0)
                        fig = px.bar(grouped, barmode='stack',
                                   title=f"Distribution of {column} by {group_by}")
                        category_mode = grouped.idxmax(axis=1)  
                        statistics = {
                                    'Category Mode': category_mode.to_dict(),
                                    'Grouped Category Counts': {
                                        group: "<br>&nbsp;&nbsp;&nbsp;&nbsp;".join([f"{category}={count}" for category, count in counts.items()])

                                        for group, counts in grouped.to_dict().items()
                                    },}

                    else:
                        counts = df['column'].value_counts()
                        fig = px.bar(x=counts.index, y=counts.values,
                                   title=f"Distribution of {column}")
                        category_mode = counts.idxmax()
                        total_count = counts.sum()
                        category_percentages = {category: f"{(count / total_count * 100):.2f}%" for category, count in counts.items()}
                        min_count = counts.min()  # Minimum count
                        max_count = counts.max()  # Maximum count
                        std_dev = counts.std()  # Standard deviation of category counts

                        statistics = {
                                'Most Frequent Category': category_mode,
                                'Counts': counts.to_dict(),
                                'Category Percentages': category_percentages,  # Percent distribution
                                'Minimum Count': min_count,  # Minimum category count
                                'Maximum Count': max_count,  # Maximum category count
                                'Standard Deviation': std_dev, 
                            }
                        

                plot_html = fig.to_html(full_html=False)

    context = {
        'form': form,
        'plot_html': plot_html,
        'column_values': column_values,
        'statistics': statistics,
        'hypothesis_results': hypothesis_results,
        'analysis_type': analysis_type
    }
    return render(request, 'analyze.html', context)
