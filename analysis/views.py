from datetime import date
from django.shortcuts import render
from .forms import AnalysisForm
from accounts.models import Student, User
import pandas as pd
import plotly.express as px
from scipy import stats
import numpy as np


def analyze(request):
    form = AnalysisForm(request.POST or None)
    plot_html = None
    statistics = None
    column_values = None
    hypothesis_results = None
    analysis_type = request.POST.get('analysis_type', 'descriptive')

    if request.method == 'POST' and form.is_valid():
        column = form.cleaned_data['column']
        group_by = form.cleaned_data.get('group_by')

        students = Student.objects.all()  # No select_related here because there is no FK
        users = User.objects.filter(id__in=[student.student.id for student in students if student.student]).all()

        if column == 'program_name':
            data = [str(student.program.title) if student.program else None for student in students]
        elif column == 'date_of_birth':
            data = [
                (date.today().year - user.date_of_birth.year - ((date.today().month, date.today().day) < (user.date_of_birth.month, user.date_of_birth.day)))
                if user.date_of_birth else None
                for user in users
            ]
        elif column == 'enrollment_date': 
            data = [
                (date.today().year - user.enrollment_date.year) * 12 + date.today().month - user.enrollment_date.month
                if user.enrollment_date else None
                for user in users
            ]
        elif column == 'expected_graduation_date':
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

        if group_by:
            if group_by == 'program_name':
                df['group_by'] = program_names
            elif hasattr(User, group_by):
                df['group_by'] = list(students.values_list(f'student__{group_by}', flat=True))
            elif hasattr(Student, group_by):
                df['group_by'] = list(students.values_list(group_by, flat=True))
            else:
                df['group_by'] = None

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
                    # Chi-square
                    contingency = pd.crosstab(df['column'], df['program'])
                    if contingency.size > 0:
                        chi2, p_value = stats.chi2_contingency(contingency)[:2]
                        hypothesis_results = {
                            'test': 'Chi-square',
                            'question': f"Is there a relationship between the program and {column}?",
                            'p_value': f"{p_value:.4f}",
                            'result': f"{'Significant' if p_value < 0.05 else 'No significant'} association"
                
                        }
                percentages = pd.crosstab(df["column"], df['program'], normalize='index') * 100
                percentages_rounded = percentages.round(2)
                group_program_percentages = percentages_rounded.to_dict()

                # Create Bar Plot for Percentages
                fig = px.bar(
                    percentages_rounded.T,
                    title=f"Program Distribution by {column}",
                    labels={"value": "Percentage (%)", "index": "Program", "variable": column},
                    barmode="group"
                )
                plot_html = fig.to_html(full_html=False)

                # Store the results for rendering
                hypothesis_results['program_percentages'] = group_program_percentages
                hypothesis_results['plot_html'] = plot_html

            else:  # Descriptive analysis
                if 'group_by' in df and not df['group_by'].isnull().all():
                    if pd.api.types.is_numeric_dtype(df['column']):
                        # Numeric data grouped by group_by
                        grouped = df.groupby('group_by')['column'].describe()
                        fig = px.box(df, x='group_by', y='column', title=f"Boxplot of {column} by {group_by}")
                        plot_html = fig.to_html(full_html=False)
                        statistics = grouped.to_dict()
                    else:
                        # Categorical data grouped by group_by
                        grouped = df.groupby('group_by')['column'].value_counts().unstack(fill_value=0)
                        fig = px.bar(grouped, barmode='stack', title=f"Stacked Bar Chart of {column} by {group_by}")
                        plot_html = fig.to_html(full_html=False)
                        statistics = grouped.to_dict()
                else:
                    if pd.api.types.is_numeric_dtype(df['column']):
                        # Numeric data without grouping
                        fig = px.histogram(df, x='column', title=f"Histogram of {column}")
                        plot_html = fig.to_html(full_html=False)
                        statistics = df['column'].describe().to_dict()
                    else:
                        # Categorical data without grouping
                        counts = df['column'].value_counts()
                        fig = px.bar(x=counts.index, y=counts.values, title=f"Counts of {column}")
                        plot_html = fig.to_html(full_html=False)
                        statistics = {'Mode': counts.idxmax(), 'Counts': counts.to_dict()}

    context = {
        'form': form,
        'plot_html': plot_html,
        'column_values': column_values,
        'statistics': statistics,
        'hypothesis_results': hypothesis_results,
        'analysis_type': analysis_type
    }
    return render(request, 'analyze.html', context)
