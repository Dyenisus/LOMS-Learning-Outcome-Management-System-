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
            "student_grade",
            "student_faculty",
            "student_program",
            "faculty_member_faculty",
            "lecturer_programs",
            "lecturer_curricula",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Hepsini opsiyonel başlat, role göre clean'de zorunlu yaparız
        self.fields["student_grade"].required = False
        self.fields["student_faculty"].required = False
        self.fields["student_program"].required = False
        self.fields["faculty_member_faculty"].required = False
        self.fields["lecturer_programs"].required = False
        self.fields["lecturer_curricula"].required = False

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get("role")

        student_faculty = cleaned.get("student_faculty")
        student_program = cleaned.get("student_program")
        student_grade = cleaned.get("student_grade")
        faculty_member_faculty = cleaned.get("faculty_member_faculty")

        # Şifre kontrolü
        pwd1 = cleaned.get("password1")
        pwd2 = cleaned.get("password2")
        if pwd1 and pwd2 and pwd1 != pwd2:
            self.add_error("password2", "Passwords do not match.")

        # Role bazlı zorunluluklar
        if role == CustomUser.Role.STUDENT:
            if not student_faculty:
                self.add_error("student_faculty", "Student faculty is required for students.")
            if not student_program:
                self.add_error("student_program", "Program is required for students.")
            if not student_grade:
                self.add_error("student_grade", "Grade is required for students.")

        elif role == CustomUser.Role.FACULTY_MEMBER:
            if not faculty_member_faculty:
                self.add_error("faculty", "Faculty is required for faculty members.")

        # Lecturer için en az bir program isteyebiliriz (zorunlu yapmak istersen açarsın)
        # elif role == CustomUser.Role.LECTURER:
        #     if not cleaned.get("lecturer_programs"):
        #         self.add_error("lecturer_programs", "At least one program is required for lecturers.")

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
