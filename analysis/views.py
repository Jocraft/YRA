from django.shortcuts import render
from .forms import AnalysisForm
from accounts.models import Student, User
from collections import Counter
import plotly.express as px
import pandas as pd
from scipy import stats
import numpy as np

def analyze(request):
    form = AnalysisForm(request.POST or None)
    plot_html = None
    pie_chart_html = None  # For pie chart
    statistics = None
    column_values = None
    hypothesis_results = None
    analysis_type = request.POST.get('analysis_type', 'descriptive')

    if request.method == 'POST' and form.is_valid():
        column = form.cleaned_data['column']
        
        # Fetch data
        students = Student.objects.all()
        
        # Get column data
        if hasattr(User, column):
            data = list(students.values_list(f'student__{column}', flat=True))
        elif hasattr(Student, column):
            data = list(students.values_list(column, flat=True))
        else:
            data = []

        column_values = data

        if analysis_type == 'hypothesis':
            # Always get program data for hypothesis testing
            program_data = list(students.values_list('program', flat=True))

            # Convert the program IDs to their respective string representations (program titles)
            program_names = [str(student.program.title) if student.program else None for student in students]
            
            if data and program_names:
                # Create DataFrame with both column and program data
                df = pd.DataFrame({
                    'column': data,
                    'program': program_names
                }).dropna()  # Remove null values
                
                if len(df) > 0:  # Ensure valid data exists
                    if pd.api.types.is_numeric_dtype(df['column']):
                        # Numeric data - ANOVA
                        programs = df['program'].unique()
                        if len(programs) >= 2:
                            groups = [df[df['program'] == prog]['column'].values 
                                      for prog in programs if len(df[df['program'] == prog]) > 0]
                            
                            if len(groups) >= 2:
                                f_stat, p_value = stats.f_oneway(*groups)
                                means = df.groupby('program')['column'].mean()
                                means_text = ', '.join([f"{prog}: {mean:.2f}" 
                                                        for prog, mean in means.items()])
                                
                                hypothesis_results = {
                                    'test': 'ANOVA',
                                    'question': f"Does {column} differ significantly across programs?",
                                    'p_value': f"{p_value:.4f}",
                                    'result': f"{'Significant differences' if p_value < 0.05 else 'No significant differences'} (Program means: {means_text})"
                                }
                    else:
                        # Categorical data - Chi-square
                            contingency = pd.crosstab(df['column'], df['program'])
                            if contingency.size > 0:
                                chi2, p_value = stats.chi2_contingency(contingency)[:2]
                                dist = pd.crosstab(df['column'], df['program'], normalize='columns') * 100
                                dist_text = '; '.join([
                                    f"{val}: {', '.join([f'{col}  :{pct:.1f}%' for col, pct in row.items()])} \n " 
                                    for val, row in dist.iterrows()
                                
                                ])
                                
                                hypothesis_results = {
                                    'test': 'Chi-square',
                                    'question': f"Is there a relationship between the program and the {column}?",
                                    'p_value': f"{p_value:.4f}",
                                    'result': f"{'Significant association' if p_value < 0.05 else 'No significant association'} (Distributions: {dist_text})"
                                }


        else:  # Descriptive analysis
            group_by = form.cleaned_data.get('group_by')
            if group_by:
                if hasattr(User, group_by):
                    group_data = list(students.values_list(f'student__{group_by}', column))
                elif hasattr(Student, group_by):
                    group_data = list(students.values_list(group_by, column))
                else:
                    group_data = []

                df = pd.DataFrame(group_data, columns=[group_by, column])
                
                if not df.empty and pd.api.types.is_numeric_dtype(df[column]):
                    # Numerical Data with grouping
                    grouped = df.groupby(group_by)[column].agg(['mean', 'median', 'min', 'max', 'std'])
                    fig = px.box(df, x=group_by, y=column)
                    plot_html = fig.to_html(full_html=False)
                    statistics = grouped.to_dict()
                else:
                    # Categorical Data with grouping
                    grouped = df.groupby(group_by)[column].value_counts().unstack(fill_value=0)
                    fig = px.bar(grouped, barmode='stack')
                    plot_html = fig.to_html(full_html=False)
                    statistics = grouped.to_dict()
            else:
                if data:
                    if isinstance(data[0], str):  # Categorical
                        counts = Counter(data)
                        fig = px.bar(x=list(counts.keys()), y=list(counts.values()))
                        plot_html = fig.to_html(full_html=False)
                        statistics = {
                            'Mode': max(counts, key=counts.get),
                            'Total Categories': len(counts),
                            'Unique Values': len(set(data))
                        }
                    else:  # Numerical
                        fig = px.histogram(data)
                        plot_html = fig.to_html(full_html=False)
                        statistics = {
                            'Mean': np.mean(data),
                            'Median': np.median(data),
                            'Std': np.std(data),
                            'Min': min(data),
                            'Max': max(data)
                        }

    context = {
        'form': form,
        'plot_html': plot_html,
        'column_values': column_values,
        'statistics': statistics,
        'hypothesis_results': hypothesis_results,
        'analysis_type': analysis_type
    }
    
    return render(request, 'analyze.html', context)
