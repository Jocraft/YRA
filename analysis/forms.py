from django import forms
from accounts.models import Student, User

class AnalysisForm(forms.Form):
    def __init__(self, *args, **kwargs):
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
            'username', 'first_name', 'last_name', 'email', 'is_active', 'is_staff', 'is_admin', "picture","address",
            "national_id","phone","student","id"
        ]  

        available_fields = [field for field in all_fields if field not in fields_to_remove]

        # Create the column field dynamically based on available columns
        self.fields['column'] = forms.ChoiceField(
            choices=[(field, field.capitalize()) for field in available_fields],
            required=True,
            label="Column to Analyze"
        )

        # Add an optional "group_by" field for grouping analysis
        self.fields['group_by'] = forms.ChoiceField(
            choices=[('', 'None')] + [(field, field.capitalize()) for field in available_fields],
            required=False,
            label="Group By (Optional)"
        )
