from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from accounts.decorators import role_required
from .models import CustomUser
from courses.models import Course
from .forms import UserCreateForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from assessments.models import Assessment, StudentAssessmentResult, AssessmentLearningOutcome

@role_required(CustomUser.Role.STUDENT_AFFAIRS)
def user_create(request):
    """
    Student Affairs:
    - Student
    - Lecturer
    - Faculty Member
    hesaplarını buradan oluşturabilsin.
    """
    if request.method == "POST":
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("accounts:user_create")  # tekrar boş form
    else:
        form = UserCreateForm()

    users = (
        CustomUser.objects
        .exclude(role=CustomUser.Role.ADMIN)
        .order_by("username")
        .select_related(
            "student_faculty",
            "student_program",
            "faculty_member_faculty",
        )
    )

    context = {
        "form": form,
        "users": users,
    }
    return render(request, "accounts/user_create.html", context)


@role_required(CustomUser.Role.STUDENT_AFFAIRS)
def user_edit(request, pk):
    """
    Student Affairs mevcut kullanıcıların temel bilgilerini güncelleyebilsin.
    """
    user_obj = get_object_or_404(CustomUser, pk=pk)

    if user_obj.is_superuser:
        raise PermissionDenied("You cannot edit superuser accounts.")

    if request.method == "POST":
        form = UserCreateForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            return redirect("accounts:user_create")
    else:
        form = UserCreateForm(instance=user_obj)

    context = {
        "form": form,
        "edited_user": user_obj,
    }
    return render(request, "accounts/user_edit.html", context)


@role_required(CustomUser.Role.STUDENT_AFFAIRS)
def user_delete(request, pk):
    """
    Student Affairs kullanıcıları silebilsin.
    """
    user_obj = get_object_or_404(CustomUser, pk=pk)

    if user_obj.is_superuser:
        raise PermissionDenied("You cannot delete superuser accounts.")

    if request.method == "POST":
        user_obj.delete()
        return redirect("accounts:user_create")

    return render(request, "accounts/user_confirm_delete.html", {"user_obj": user_obj})

@login_required
def role_redirect(request):
    user: CustomUser = request.user

    # 1) Admin → Django admin
    if user.is_admin or user.is_superuser:
        return redirect(reverse("admin:index"))

    # 2) Student Affairs → Org Panel (fakülte / program yönetimi)
    if user.is_student_affairs:
        return redirect("organizations:faculty_program_list")

    # 3) Faculty Member → Faculty Panel
    if user.is_faculty_member:
        return redirect("organizations:faculty_member_dashboard")

    # 4) Lecturer → Lecturer Dashboard
    if user.is_lecturer:
        return redirect("courses:lecturer_dashboard")

    # 5) Student → şimdilik Org Panel veya ileride Student Dashboard
    if user.is_student:
        return redirect("accounts:student_dashboard")
    
    # Fallback: login sayfasına veya ana sayfaya dön
    return redirect("accounts:login")

@role_required(CustomUser.Role.STUDENT)
def student_dashboard(request):
    user: CustomUser = request.user

    # Öğrencinin programı ve sınıfı (grade)
    student_program = user.student_program      
    student_grade = user.student_grade          

    courses = Course.objects.none()
    if student_program and student_grade:
        courses = (
            Course.objects
            .filter(
                program=student_program,        
                year=student_grade,             
            )
            .order_by("semester", "code")
        )

    context = {
        "student": user,
        "program": student_program,
        "grade": student_grade,
        "courses": courses,
    }
    return render(request, "accounts/student_dashboard.html", context)

@role_required(CustomUser.Role.STUDENT)
def student_course_detail(request, course_id):
    """
    Öğrenci için tek bir dersin:
    - temel bilgileri
    - assessment listesi + kendi notu
    - assessment → LO → PO mapping
    gösterilir.
    """
    user: CustomUser = request.user

    student_program = getattr(user, "student_program", None)
    student_grade = getattr(user, "student_grade", None)

    # Öğrencinin program + grade'ine ait olmayan derse girmesin
    course = get_object_or_404(
        Course.objects.select_related("program", "lecturer"),
        id=course_id,
        program=student_program,
        year=student_grade,
    )

    # İlgili dersin tüm assessment'ları
    assessments = (
        Assessment.objects.filter(course=course)
        .prefetch_related(
            "lo_mappings__learning_outcome__lo_po_mappings__program_outcome",
            "results",
        )
        .order_by("date", "name")
    )

    # Bu öğrenciye ait notlar
    results_by_assessment = {
        r.assessment_id: r
        for r in StudentAssessmentResult.objects.filter(
            assessment__course=course,
            student=user,
        )
    }

    rows = []
    lo_totals = {}
    po_totals = {}
    for a in assessments:
        result = results_by_assessment.get(a.id)

        # yaklaşık katkı hesabı (score / max_score * weight_in_course)
        contribution = None
        if (
            result is not None
            and result.raw_score is not None
            and a.max_score
        ):
            try:
                contribution = (
                    Decimal(result.raw_score)
                    / Decimal(a.max_score)
                    * Decimal(a.weight_in_course)
                )
            except ZeroDivisionError:
                contribution = None

        # Assessment → LO → PO yapısı
        lo_rows = []
        for mapping in a.lo_mappings.all():
            lo = mapping.learning_outcome

            lo_contrib = None
            if contribution is not None:
                lo_contrib = contribution * (
                    Decimal(mapping.weight_in_assessment) / Decimal(100)
                )
                lo_totals[lo.id] = lo_totals.get(lo.id, Decimal(0)) + lo_contrib

                # PO katkılarını güncelle
                for lo_po in lo.lo_po_mappings.all():
                    po_contrib = lo_contrib * (Decimal(lo_po.weight) / Decimal(100))
                    po_totals[lo_po.program_outcome_id] = po_totals.get(
                        lo_po.program_outcome_id, Decimal(0)
                    ) + po_contrib

            po_rows = []
            for lo_po in lo.lo_po_mappings.all():
                po_rows.append(
                    {
                        "po": lo_po.program_outcome,
                        "weight": lo_po.weight,
                        "po_score": po_totals.get(lo_po.program_outcome_id),
                    }
                )

            lo_rows.append(
                {
                    "lo": lo,
                    "weight_in_assessment": mapping.weight_in_assessment,
                    "po_rows": po_rows,
                    "lo_score": lo_totals.get(lo.id),
                }
            )

        score_value = None
        if result is not None:
            score_value = getattr(result, "raw_score", None)
            if score_value is None:
                score_value = getattr(result, "score", None)

        rows.append(
            {
                "assessment": a,
                "result": result,
                "contribution": contribution,
                "lo_rows": lo_rows,
                "score_value": score_value,
            }
        )

    context = {
        "student": user,
        "course": course,
        "rows": rows,
    }
    return render(request, "accounts/student_course_detail.html", context)
