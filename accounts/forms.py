from django import forms
from django.db import transaction
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    PasswordResetForm,
)
from course.models import Program
from .models import (
    User,
    Student,
    Parent,
    RELATION_SHIP,
    LEVEL,
    GENDERS,
    NATIONALITIES,
    ETHNICITIES,
    RELIGIONS,
    LANGUAGES,
    FACULTIES,
)


class StaffAddForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Username",
        required=False,
    )

    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="First Name",
    )

    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Last Name",
    )

    gender = forms.CharField(
        widget=forms.Select(
            choices=GENDERS,
            attrs={
                "class": "browser-default custom-select form-control",
            },
        ),
    )

    address = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Address",
    )

    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Mobile No.",
    )

    email = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Email",
    )

    password1 = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "password",
                "class": "form-control",
            }
        ),
        label="Password",
        required=False,
    )

    password2 = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "password",
                "class": "form-control",
            }
        ),
        label="Password Confirmation",
        required=False,
    )

    # --- NEW FIELD: Faculty ---
    faculty = forms.ChoiceField(
        choices=FACULTIES,
        required=False,
        widget=forms.Select(attrs={"class": "browser-default custom-select form-control"}),
        label="Faculty",
    )

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_lecturer = True
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.phone = self.cleaned_data.get("phone")
        user.address = self.cleaned_data.get("address")
        user.email = self.cleaned_data.get("email")
        # Save the faculty field
        user.faculty = self.cleaned_data.get("faculty")

        if commit:
            user.save()
        return user


class StudentAddForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={"type": "text", "class": "form-control", "id": "username_id"}
        ),
        label="Username",
        required=False,
    )
    address = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Address",
    )
    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Mobile No.",
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="First name",
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Last name",
    )
    gender = forms.CharField(
        widget=forms.Select(
            choices=GENDERS,
            attrs={
                "class": "browser-default custom-select form-control",
            },
        ),
    )
    level = forms.CharField(
        widget=forms.Select(
            choices=LEVEL,
            attrs={
                "class": "browser-default custom-select form-control",
            },
        ),
    )
    program = forms.ModelChoiceField(
        queryset=Program.objects.all(),
        widget=forms.Select(
            attrs={"class": "browser-default custom-select form-control"}
        ),
        label="Program",
    )
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "class": "form-control",
            }
        ),
        label="Email Address",
    )
    password1 = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "password",
                "class": "form-control",
            }
        ),
        label="Password",
        required=False,
    )
    password2 = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "password",
                "class": "form-control",
            }
        ),
        label="Password Confirmation",
        required=False,
    )

    # Single-choice drop-downs
    nationality = forms.ChoiceField(
        required=False,
        choices=NATIONALITIES,
        widget=forms.Select(attrs={"class": "browser-default custom-select form-control"}),
        label="Nationality/Citizenship",
    )
    ethnicity = forms.ChoiceField(
        required=False,
        choices=ETHNICITIES,
        widget=forms.Select(attrs={"class": "browser-default custom-select form-control"}),
        label="Ethnicity or Race",
    )
    religion = forms.ChoiceField(
        required=False,
        choices=RELIGIONS,
        widget=forms.Select(attrs={"class": "browser-default custom-select form-control"}),
        label="Religion",
    )

    national_id = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(
            attrs={"type": "text", "class": "form-control"}
        ),
        label="National ID/Passport",
    )
    enrollment_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control"}
        ),
        label="Enrollment Date",
    )
    expected_graduation_date = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control"}
        ),
        label="Expected Graduation Date",
    )

    # Multiple-choice for languages
    languages_spoken = forms.MultipleChoiceField(
        required=False,
        choices=LANGUAGES,
        widget=forms.SelectMultiple(
            attrs={"class": "browser-default custom-select form-control"}
        ),
        label="Languages Spoken",
        help_text="Select one or more languages (hold CTRL or CMD to select multiple)",
    )

    # --- NEW FIELD: Faculty ---
    faculty = forms.ChoiceField(
        choices=FACULTIES,
        required=False,
        widget=forms.Select(attrs={"class": "browser-default custom-select form-control"}),
        label="Faculty",
    )

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_student = True

        # Basic fields
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.gender = self.cleaned_data.get("gender")
        user.address = self.cleaned_data.get("address")
        user.phone = self.cleaned_data.get("phone")
        user.email = self.cleaned_data.get("email")

        # Save the new faculty field
        user.faculty = self.cleaned_data.get("faculty")

        # Additional new fields
        user.nationality = self.cleaned_data.get("nationality")
        user.national_id = self.cleaned_data.get("national_id")
        user.enrollment_date = self.cleaned_data.get("enrollment_date")
        user.expected_graduation_date = self.cleaned_data.get("expected_graduation_date")
        user.ethnicity = self.cleaned_data.get("ethnicity")
        user.religion = self.cleaned_data.get("religion")

        # Join multiple languages
        selected_langs = self.cleaned_data.get("languages_spoken", [])
        user.languages_spoken = ",".join(selected_langs)

        if commit:
            user.save()
            # Create the linked Student record
            Student.objects.create(
                student=user,
                level=self.cleaned_data.get("level"),
                program=self.cleaned_data.get("program"),
            )
        return user


class ProfileUpdateForm(UserChangeForm):
    """
    Used for editing an existing user (Student, Staff, etc.).
    Now includes the extra fields (faculty, nationality, ethnicity, religion, languages_spoken).
    """

    # Basic fields
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "class": "form-control",
            }
        ),
        label="Email Address",
    )
    first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="First Name",
    )
    last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Last Name",
    )
    gender = forms.CharField(
        widget=forms.Select(
            choices=GENDERS,
            attrs={
                "class": "browser-default custom-select form-control",
            },
        ),
    )
    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Phone No.",
    )
    address = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Address / city",
    )

    # --- NEW FIELDS: Single-choice ---
    nationality = forms.ChoiceField(
        required=False,
        choices=NATIONALITIES,
        widget=forms.Select(attrs={"class": "browser-default custom-select form-control"}),
        label="Nationality/Citizenship",
    )
    ethnicity = forms.ChoiceField(
        required=False,
        choices=ETHNICITIES,
        widget=forms.Select(attrs={"class": "browser-default custom-select form-control"}),
        label="Ethnicity",
    )
    religion = forms.ChoiceField(
        required=False,
        choices=RELIGIONS,
        widget=forms.Select(attrs={"class": "browser-default custom-select form-control"}),
        label="Religion",
    )

    # --- NEW FIELDS: ID, enrollment, etc. ---
    national_id = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="National ID/Passport",
    )
    enrollment_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="Enrollment Date",
    )
    expected_graduation_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        label="Expected Graduation Date",
    )

    # --- NEW FIELD: Multiple-choice for languages ---
    languages_spoken = forms.MultipleChoiceField(
        required=False,
        choices=LANGUAGES,
        widget=forms.SelectMultiple(
            attrs={"class": "browser-default custom-select form-control"}
        ),
        label="Languages Spoken",
    )

    # --- NEW FIELD: Faculty ---
    faculty = forms.ChoiceField(
        choices=FACULTIES,
        required=False,
        widget=forms.Select(attrs={"class": "browser-default custom-select form-control"}),
        label="Faculty",
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "gender",
            "email",
            "phone",
            "address",
            "picture",
            "nationality",
            "ethnicity",
            "religion",
            "national_id",
            "enrollment_date",
            "expected_graduation_date",
            "faculty",
        ]

    def __init__(self, *args, **kwargs):
        """
        Pre-fill the languages_spoken multiple-choice from the comma-separated string in the DB.
        """
        super().__init__(*args, **kwargs)
        if self.instance.languages_spoken:
            lang_list = self.instance.languages_spoken.split(",")
            self.fields["languages_spoken"].initial = lang_list

    def save(self, commit=True):
        user = super().save(commit=False)

        # Convert multiple choice (list) back into a comma string
        selected_langs = self.cleaned_data.get("languages_spoken", [])
        user.languages_spoken = ",".join(selected_langs)

        # Make sure faculty is saved
        user.faculty = self.cleaned_data.get("faculty")

        if commit:
            user.save()
        return user


class ProgramUpdateForm(UserChangeForm):
    program = forms.ModelChoiceField(
        queryset=Program.objects.all(),
        widget=forms.Select(
            attrs={"class": "browser-default custom-select form-control"}
        ),
        label="Program",
    )

    class Meta:
        model = Student
        fields = ["program"]


class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data["email"]
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            msg = "There is no user registered with the specified E-mail address."
            self.add_error("email", msg)
            return email


class ParentAddForm(UserCreationForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Username",
    )
    address = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Address",
    )
    phone = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Mobile No.",
    )
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="First name",
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "text",
                "class": "form-control",
            }
        ),
        label="Last name",
    )
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "class": "form-control",
            }
        ),
        label="Email Address",
    )
    student = forms.ModelChoiceField(
        queryset=Student.objects.all(),
        widget=forms.Select(
            attrs={"class": "browser-default custom-select form-control"}
        ),
        label="Student",
    )
    relation_ship = forms.CharField(
        widget=forms.Select(
            choices=RELATION_SHIP,
            attrs={
                "class": "browser-default custom-select form-control",
            },
        ),
    )
    password1 = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "password",
                "class": "form-control",
            }
        ),
        label="Password",
    )
    password2 = forms.CharField(
        max_length=30,
        widget=forms.TextInput(
            attrs={
                "type": "password",
                "class": "form-control",
            }
        ),
        label="Password Confirmation",
    )

    class Meta(UserCreationForm.Meta):
        model = User

    @transaction.atomic()
    def save(self):
        user = super().save(commit=False)
        user.is_parent = True
        user.first_name = self.cleaned_data.get("first_name")
        user.last_name = self.cleaned_data.get("last_name")
        user.address = self.cleaned_data.get("address")
        user.phone = self.cleaned_data.get("phone")
        user.email = self.cleaned_data.get("email")
        user.save()
        parent = Parent.objects.create(
            user=user,
            student=self.cleaned_data.get("student"),
            relation_ship=self.cleaned_data.get("relation_ship"),
        )
        parent.save()
        return user
