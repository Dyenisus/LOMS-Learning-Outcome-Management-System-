from django import forms
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        strip=False,
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput,
        strip=False,
    )

    class Meta:
        model = CustomUser
        fields = [
            "username",
            "email",
            "role",
            "phone",
            "student_number",
            "student_grade",
            "student_faculty",
            "student_program",
            "lecturer_programs",
            "lecturer_courses",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Admin seçeneğini Student Affairs panelinden kaldır
        self.fields["role"].choices = [
            choice
            for choice in self.fields["role"].choices
            if choice[0] != CustomUser.Role.ADMIN
        ]

        # Hepsini opsiyonel başlat, role göre clean'de zorunlu yaparız
        self.fields["student_grade"].required = False
        self.fields["student_faculty"].required = False
        self.fields["student_program"].required = False
        self.fields["student_number"].required = False
        self.fields["lecturer_programs"].required = False
        self.fields["lecturer_courses"].required = False
        self.fields["lecturer_programs"].help_text = ""
        self.fields["lecturer_courses"].help_text = ""

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get("role")

        student_faculty = cleaned.get("student_faculty")
        student_program = cleaned.get("student_program")
        student_grade = cleaned.get("student_grade")
        student_number = cleaned.get("student_number")
        # Şifre kontrolü
        pwd1 = cleaned.get("password1")
        pwd2 = cleaned.get("password2")
        if pwd1 and pwd2 and pwd1 != pwd2:
            self.add_error("password2", "Passwords do not match.")

        # Role bazlı zorunluluklar
        if role == CustomUser.Role.STUDENT:
            missing_student_fields = []
            if not student_faculty:
                self.add_error("student_faculty", "Student faculty is required for students.")
                missing_student_fields.append("faculty")
            if not student_program:
                self.add_error("student_program", "Program is required for students.")
                missing_student_fields.append("program")
            if not student_grade:
                self.add_error("student_grade", "Grade is required for students.")
                missing_student_fields.append("grade")
            if not student_number:
                self.add_error("student_number", "Student number is required for students.")
                missing_student_fields.append("student number")

            if missing_student_fields:
                self.add_error(
                    None,
                    "Students must have faculty, program, grade, and student number before saving.",
                )

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        if commit:
            user.save()
            # M2M'ler
            self.save_m2m()
        return user
