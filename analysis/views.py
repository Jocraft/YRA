from django.shortcuts import render
from .forms import AnalysisForm
from accounts.models import Student, User
from collections import Counter
import plotly.express as px
import pandas as pd  # Useful for grouping data

def analyze(request):
    form = AnalysisForm(request.POST or None)
    plot_html = None
    column_values = None
    statistics = None

    if request.method == 'POST' and form.is_valid():
        column = form.cleaned_data['column']
        group_by = form.cleaned_data.get('group_by')  # Get the optional group_by value

        # Fetch data for the selected column
        students = Student.objects.all()
        if hasattr(User, column):
            data = list(students.values_list(f'student__{column}', flat=True))
        elif hasattr(Student, column):
            data = list(students.values_list(column, flat=True))
        else:
            data = []

        column_values = data

        # Handle grouping logic
        if group_by:
            if hasattr(User, group_by):
                group_data = list(students.values_list(f'student__{group_by}', column))
            elif hasattr(Student, group_by):
                group_data = list(students.values_list(group_by, column))
            else:
                group_data = []
            
            # Convert to a DataFrame for easy grouping
            df = pd.DataFrame(group_data, columns=[group_by, column])

            # Group by the selected column and calculate counts or statistics
            if df[column].dtype == 'O':  # If the column is categorical
                grouped = df.groupby(group_by)[column].value_counts().unstack(fill_value=0)
                fig = px.bar(grouped, barmode='stack', labels={'value': 'Count', 'index': group_by})
                plot_html = fig.to_html(full_html=False)

                statistics = grouped.to_dict()

            else:  # If the column is numerical
                grouped = df.groupby(group_by)[column].agg(['mean', 'median', 'min', 'max', 'std'])
                fig = px.box(df, x=group_by, y=column, labels={group_by: group_by.capitalize(), column: column.capitalize()})
                plot_html = fig.to_html(full_html=False)

                statistics = grouped.to_dict()

        else:  # No grouping
            if data and isinstance(data[0], str):  # Categorical data
                value_counts = Counter(data)
                labels = list(value_counts.keys())
                counts = list(value_counts.values())

                # Plot bar chart
                fig = px.bar(x=labels, y=counts, labels={'x': column.capitalize(), 'y': 'Count'})
                plot_html = fig.to_html(full_html=False)

                statistics = {
                    'Mode': max(value_counts, key=value_counts.get),
                    'Total Categories': len(value_counts),
                    'Unique Values': len(set(data))
                }

            elif data and isinstance(data[0], (int, float)):  # Numerical data
                sorted_data = sorted(data)
                n = len(sorted_data)

                # Plot histogram
                fig = px.histogram(data, nbins=10, labels={column: column.capitalize()})
                plot_html = fig.to_html(full_html=False)

                statistics = {
                    'Mean': sum(data) / n,
                    'Median': sorted_data[n // 2],
                    'Q1': sorted_data[n // 4],
                    'Q3': sorted_data[3 * n // 4],
                    'Range': max(data) - min(data),
                    'Min': min(data),
                    'Max': max(data)
                }

    return render(request, 'analyze.html', {
        'form': form,
        'plot_html': plot_html,
        'column_values': column_values,
        'statistics': statistics
    })
