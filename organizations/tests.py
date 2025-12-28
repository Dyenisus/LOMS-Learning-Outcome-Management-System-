from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser
from .models import Faculty, Program


class OrganizationViewTests(TestCase):
    def setUp(self):
        self.student_affairs = CustomUser.objects.create_user(
            username="affairs",
            password="pass1234",
            role=CustomUser.Role.STUDENT_AFFAIRS,
        )

    def test_student_affairs_can_create_faculty(self):
        self.client.force_login(self.student_affairs)
        response = self.client.post(
            reverse("organizations:faculty_create"),
            data={
                "code": "ENG",
                "name": "Engineering",
                "responsible": "",
            },
        )
        self.assertRedirects(response, reverse("organizations:faculty_program_list"))
        self.assertTrue(Faculty.objects.filter(code="ENG").exists())

    def test_student_affairs_can_create_program(self):
        faculty = Faculty.objects.create(code="SCI", name="Science")
        self.client.force_login(self.student_affairs)
        response = self.client.post(
            reverse("organizations:program_create"),
            data={
                "code": "BIO",
                "name": "Biology",
                "faculty": faculty.id,
            },
        )
        self.assertRedirects(response, reverse("organizations:faculty_program_list"))
        self.assertTrue(Program.objects.filter(code="BIO", faculty=faculty).exists())
