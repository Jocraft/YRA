from django import forms
from accounts.models import Student, User

class AnalysisForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # Get the years from the request if available
        available_years = kwargs.pop('available_years', [])
        super().__init__(*args, **kwargs)

        # Dynamically get the field names from the User and Student models
        User_fields = [field.name for field in User._meta.get_fields() if field.concrete]
        Student_fields = [field.name for field in Student._meta.get_fields() if field.concrete]

        # Combine both lists but avoid duplicates
        all_fields = set(User_fields + Student_fields)

        # Remove fields you don't want
        fields_to_remove = [
            'password', 'last_login', 'is_superuser', 'user_permissions', 'groups', 
            'is_student', 'is_lecturer', 'is_parent', 'is_dep_head', 'date_joined', 
            'username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_admin', "picture", "address",
            "national_id", "phone", "student", "id", "program", "date_of_birth", "enrollment_date", "expected_graduation_date","languages_spoken"
        ]  

        available_fields = [field for field in all_fields if field not in fields_to_remove]

        # Create choices for the column field
        column_choices = [(field, field.capitalize()) for field in available_fields]
        
        # Add special fields with custom labels
        special_fields = [
            ('program_name', 'Program'),
            ('date_of_birth', 'Student Age'),
            ('enrollment_date', 'Enrollment Duration'),
            ('expected_graduation_date', 'Time to Graduation'),
            ("languages_spoken", "Languages Spoken")
        ]
        
        column_choices.extend(special_fields)

        # Create the column field
        self.fields['column'] = forms.ChoiceField(
            choices=column_choices,
            required=True,
            label="Column to Analyze"
        )

        # Create the group_by field with the same choices
        group_by_choices = [('', 'None')] + column_choices
        self.fields['group_by'] = forms.ChoiceField(
            choices=group_by_choices,
            required=False,
            label="Group By (Optional)"
        )

        # Add visualization type field for date fields
        self.fields['visualization_type'] = forms.ChoiceField(
            choices=[
                ('numerical', 'Numerical Analysis'),
                ('date', 'Date-based Analysis')
            ],
            required=False,
            label="Visualization Type (for date fields)"
        )

        # Add year filter field
        year_choices = [('', 'All Years')] + [(str(year), str(year)) for year in available_years]
        self.fields['selected_year'] = forms.ChoiceField(
            choices=year_choices,
            required=False,
            label="Filter by Year"
        )

