from django.test import TestCase
from django.urls import reverse

from accounts.models import CustomUser


class UserCreationViewTests(TestCase):
    def setUp(self):
        self.student_affairs = CustomUser.objects.create_user(
            username="affairs",
            password="pass1234",
            role=CustomUser.Role.STUDENT_AFFAIRS,
        )

    def test_student_affairs_can_create_lecturer(self):
        self.client.force_login(self.student_affairs)
        response = self.client.post(
            reverse("accounts:user_create"),
            data={
                "username": "lecturer_new",
                "email": "lecturer@example.com",
                "role": CustomUser.Role.LECTURER,
                "phone": "",
                "student_number": "",
                "student_grade": "",
                "student_faculty": "",
                "student_program": "",
                "lecturer_programs": [],
                "lecturer_courses": [],
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )
        self.assertRedirects(response, reverse("accounts:user_create"))
        created = CustomUser.objects.get(username="lecturer_new")
        self.assertEqual(created.role, CustomUser.Role.LECTURER)
        self.assertTrue(created.must_change_password)
