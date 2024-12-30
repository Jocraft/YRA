from django.db import models
from django.urls import reverse
from django.contrib.auth.models import AbstractUser, UserManager
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count
from PIL import Image

from course.models import Program
from .validators import ASCIIUsernameValidator


# Defining degree levels
BACHELOR_DEGREE = _("Bachelor")
MASTER_DEGREE = _("Master")
ASSOCIATE_DEGREE = _("Associate")
DOCTORATE_DEGREE = _("Doctorate")
DIPLOMA = _("Diploma")
HIGH_SCHOOL = _("High School")
MIDDLE_SCHOOL = _("Middle School")

# Creating the LEVEL tuple
LEVEL = (
    (HIGH_SCHOOL, _("High School")),
    (MIDDLE_SCHOOL, _("Middle School")),
    (ASSOCIATE_DEGREE, _("Associate Degree")),
    (BACHELOR_DEGREE, _("Bachelor Degree")),
    (DIPLOMA, _("Diploma")),
    (MASTER_DEGREE, _("Master Degree")),
    (DOCTORATE_DEGREE, _("Doctorate Degree")),
)


FATHER = _("Father")
MOTHER = _("Mother")
BROTHER = _("Brother")
SISTER = _("Sister")
GRAND_MOTHER = _("Grand mother")
GRAND_FATHER = _("Grand father")
OTHER = _("Other")

RELATION_SHIP = (
    (FATHER, _("Father")),
    (MOTHER, _("Mother")),
    (BROTHER, _("Brother")),
    (SISTER, _("Sister")),
    (GRAND_MOTHER, _("Grand mother")),
    (GRAND_FATHER, _("Grand father")),
    (OTHER, _("Other")),
)

GENDERS = ((_("M"), _("Male")), (_("F"), _("Female")))

# -----------------------------
# CHOICE LISTS FOR SINGLE FIELDS
# -----------------------------
NATIONALITIES = [
    ("Egyption", _("Egyption")),
    ("american", _("American")),
    ("british", _("British")),
    ("canadian", _("Canadian")),
    ("other", _("Other")),
]

ETHNICITIES = [
    ("asian", _("Asian")),
    ("black", _("Black")),
    ("hispanic", _("Hispanic")),
    ("white", _("White")),
    ("other", _("Other")),
]

RELIGIONS = [
    ("christian", _("Christianity")),
    ("muslim", _("Islam")),
    ("jewish", _("Judaism")),
    ("hindu", _("Hinduism")),
    ("buddhist", _("Buddhism")),
    ("other", _("Other / Prefer not to say")),
]

# -----------------------------
# LIST FOR MULTIPLE LANGUAGES
# (Will be used in forms.py)
# -----------------------------
LANGUAGES = [
    ("english", _("English")),
    ("french", _("French")),
    ("spanish", _("Spanish")),
    ("arabic", _("Arabic")),
    ("mandarin", _("Mandarin")),
    ("other", _("Other")),
]

# Define faculties and institutes
FACULTIES = [
    ("None", _("None")),
    ("Faculty of Arts", _("Faculty of Arts")),
    ("Faculty of Science", _("Faculty of Science")),
    ("Faculty of Engineering", _("Faculty of Engineering")),
    ("Faculty of Medicine", _("Faculty of Medicine")),
    ("Faculty of Agriculture", _("Faculty of Agriculture")),
    ("Faculty of Law", _("Faculty of Law")),
    ("Faculty of Commerce", _("Faculty of Commerce")),
    ("Faculty of Education", _("Faculty of Education")),
    ("Faculty of Veterinary Medicine", _("Faculty of Veterinary Medicine")),
    ("Faculty of Dentistry", _("Faculty of Dentistry")),
    ("Faculty of Pharmacy", _("Faculty of Pharmacy")),
    ("Faculty of Physical Education", _("Faculty of Physical Education")),
    ("Faculty of Nursing", _("Faculty of Nursing")),
    ("Faculty of Computer Science", _("Faculty of Computer Science")),
    ("Faculty of Business Administration", _("Faculty of Business Administration")),
    ("Faculty of Fine Arts", _("Faculty of Fine Arts")),
    ("Faculty of Tourism and Hotels", _("Faculty of Tourism and Hotels")),
    ("Faculty of Environmental Sciences", _("Faculty of Environmental Sciences")),
    ("Faculty of Specific Education", _("Faculty of Specific Education")),
    ("Faculty of Oral and Dental Medicine", _("Faculty of Oral and Dental Medicine")),
    ("Higher Institute for Cooperative and Administrative Studies", _("Higher Institute for Cooperative and Administrative Studies")),
    ("Intermediate Institute of Social Service", _("Intermediate Institute of Social Service")),
    ("Institute of Administration, Secretarial Work and Computers", _("Institute of Administration, Secretarial Work and Computers")),
    ("Higher Institute of Languages and Translation", _("Higher Institute of Languages and Translation")),
    ("Higher Institute of Agricultural Cooperation and Guidance", _("Higher Institute of Agricultural Cooperation and Guidance")),
    ("Higher Institute of Computers, Administrative Information and Management Science", _("Higher Institute of Computers, Administrative Information and Management Science")),
    ("Higher Institute of Languages", _("Higher Institute of Languages")),
    ("Egyptian Higher Institute of Tourism and Hotels", _("Egyptian Higher Institute of Tourism and Hotels")),
    ("Higher Institute of Optic Technology", _("Higher Institute of Optic Technology")),
    ("Institute of Specific Studies", _("Institute of Specific Studies")),
    ("Higher Institute of Social Work", _("Higher Institute of Social Work")),
    ("Higher Institute of Agricultural Cooperation and Guidance", _("Higher Institute of Agricultural Cooperation and Guidance"))
]

class CustomUserManager(UserManager):
    def search(self, query=None):
        queryset = self.get_queryset()
        if query is not None:
            or_lookup = (
                Q(username__icontains=query)
                | Q(first_name__icontains=query)
                | Q(last_name__icontains=query)
                | Q(email__icontains=query)
            )
            queryset = queryset.filter(or_lookup).distinct()
        return queryset

    def get_student_count(self):
        return self.model.objects.filter(is_student=True).count()

    def get_lecturer_count(self):
        return self.model.objects.filter(is_lecturer=True).count()

    def get_superuser_count(self):
        return self.model.objects.filter(is_superuser=True).count()


class User(AbstractUser):
    is_student = models.BooleanField(default=False)
    is_lecturer = models.BooleanField(default=False)
    is_parent = models.BooleanField(default=False)
    is_dep_head = models.BooleanField(default=False)
    # New date_of_birth field
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        help_text=_("Optional. Format: YYYY-MM-DD.")
    )
    gender = models.CharField(max_length=1, choices=GENDERS, blank=True, null=True)
    phone = models.CharField(max_length=60, blank=True, null=True)
    address = models.CharField(max_length=60, blank=True, null=True)
    picture = models.ImageField(
        upload_to="profile_pictures/%y/%m/%d/", default="default.png", null=True
    )
    email = models.EmailField(blank=True, null=True)

    # Single-choice fields with predefined lists
    nationality = models.CharField(
        max_length=100, choices=NATIONALITIES, blank=True, null=True
    )
    ethnicity = models.CharField(
        max_length=100, choices=ETHNICITIES, blank=True, null=True
    )
    religion = models.CharField(
        max_length=100, choices=RELIGIONS, blank=True, null=True
    )

    # Single text field to store comma-separated languages for multi-select
    languages_spoken = models.CharField(max_length=255, blank=True, null=True)

    # Additional fields
    national_id = models.CharField(max_length=50, blank=True, null=True)
    enrollment_date = models.DateField(blank=True, null=True)
    expected_graduation_date = models.DateField(blank=True, null=True)

    # New field for faculty
    faculty = models.CharField(max_length=150, choices=FACULTIES, blank=True, null=True)

    username_validator = ASCIIUsernameValidator()

    objects = CustomUserManager()

    class Meta:
        ordering = ("-date_joined",)

    @property
    def get_full_name(self):
        full_name = self.username
        if self.first_name and self.last_name:
            full_name = self.first_name + " " + self.last_name
        return full_name

    def __str__(self):
        return "{} ({})".format(self.username, self.get_full_name)

    @property
    def get_user_role(self):
        if self.is_superuser:
            return _("Admin")
        elif self.is_student:
            return _("Student")
        elif self.is_lecturer:
            return _("Lecturer")
        elif self.is_parent:
            return _("Parent")

    def get_picture(self):
        try:
            return self.picture.url
        except:
            no_picture = settings.MEDIA_URL + "default.png"
            return no_picture

    def get_absolute_url(self):
        return reverse("profile_single", kwargs={"user_id": self.id})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Resize the picture if too large
        try:
            img = Image.open(self.picture.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.picture.path)
        except:
            pass

    def delete(self, *args, **kwargs):
        if self.picture.url != settings.MEDIA_URL + "default.png":
            self.picture.delete()
        super().delete(*args, **kwargs)


class StudentManager(models.Manager):
    def search(self, query=None):
        qs = self.get_queryset()
        if query is not None:
            or_lookup = Q(level__icontains=query) | Q(program__icontains=query)
            qs = qs.filter(or_lookup).distinct()
        return qs


class Student(models.Model):
    student = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.CharField(max_length=25, choices=LEVEL, null=True)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)

    objects = StudentManager()

    class Meta:
        ordering = ("-student__date_joined",)

    def __str__(self):
        return self.student.get_full_name()

    def program_name(self):
        if self.program:
            return self.program.title
        return None

    @classmethod
    def get_gender_count(cls):
        males_count = cls.objects.filter(student__gender="M").count()
        females_count = cls.objects.filter(student__gender="F").count()
        return {"M": males_count, "F": females_count}

    @classmethod
    def get_college_count(cls):
        """
        Returns a QuerySet (or dict) of the number of students
        in each faculty (college).
        
        Example return format if you turn it into a dict:
        {
            'Faculty of Engineering': 10,
            'Faculty of Medicine': 7,
            ...
        }
        """
        data = (
            cls.objects
            .values("student__faculty")         # group by faculty
            .annotate(count=Count("student__faculty"))  # count
            .order_by("student__faculty")       # optional ordering
        )

        # If you want a dict {faculty_name: count}:
        return {
            item["student__faculty"]: item["count"] 
            for item in data if item["student__faculty"]
        }

    @classmethod
    def get_level_count(cls):
        """
        Returns a QuerySet (or dict) of the number of students
        in each level.
        
        Example return format if you turn it into a dict:
        {
            'High School': 3,
            'Bachelor Degree': 15,
            'Master Degree': 4,
            ...
        }
        """
        data = (
            cls.objects
            .values("level")              
            .annotate(count=Count("level"))  
            .order_by("level")             # optional ordering
        )

        # If you want a dict {level: count}:
        return {item["level"]: item["count"] for item in data if item["level"]}

    def get_absolute_url(self):
        return reverse("profile_single", kwargs={"user_id": self.id})

    def delete(self, *args, **kwargs):
        # Deleting the student also deletes the associated User.
        self.student.delete()
        super().delete(*args, **kwargs)

class Parent(models.Model):
    """
    Connect student with their parent, parents can
    only view their connected student's information
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student = models.OneToOneField(Student, null=True, on_delete=models.SET_NULL)
    first_name = models.CharField(max_length=120)
    last_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=60, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    relation_ship = models.TextField(choices=RELATION_SHIP, blank=True)

    class Meta:
        ordering = ("-user__date_joined",)

    def __str__(self):
        return self.user.username


class DepartmentHead(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Program, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ("-user__date_joined",)

    def __str__(self):
        return "{}".format(self.user)
