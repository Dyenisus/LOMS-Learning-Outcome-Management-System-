from decimal import Decimal, InvalidOperation

from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied
from django.forms import modelform_factory

from accounts.decorators import role_required
from accounts.models import CustomUser
from courses.models import Course
from outcomes.models import LearningOutcome
from .models import (
    Assessment,
    AssessmentLearningOutcome,
    StudentAssessmentResult,
)


def _check_course_permission_for_lecturer(user: CustomUser, course: Course):
    """
    Lecturer sadece kendisine atanmış course'lar için assessment yönetebilsin.
    Admin her şeye girebilir.
    """
    if user.is_admin:
        return

    # Ana lecturer FK kontrolü
    if getattr(course, "lecturer_id", None) == user.id:
        return

    # Eğer M2M 'lecturers' alanı varsa, onu da kontrol et
    if hasattr(course, "lecturers") and course.lecturers.filter(id=user.id).exists():
        return

    raise PermissionDenied("You are not allowed to manage assessments for this course.")


@role_required(CustomUser.Role.LECTURER)
def assessment_manage(request, course_id):
    """
    Belirli bir course için assessment listesi + yeni assessment ekleme formu.
    """
    course = get_object_or_404(
        Course.objects.select_related("program"),
        id=course_id,
    )
    _check_course_permission_for_lecturer(request.user, course)

    assessments = course.assessments.all().order_by("date", "name")

    AssessmentForm = modelform_factory(
        Assessment,
        fields=["name", "type", "weight_in_course", "max_score", "date"],
    )

    if request.method == "POST":
        form = AssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.course = course
            assessment.save()
            return redirect("assessments:assessment_manage", course_id=course.id)
    else:
        form = AssessmentForm()

    context = {
        "course": course,
        "assessments": assessments,
        "form": form,
    }
    return render(request, "assessments/assessment_manage.html", context)


@role_required(CustomUser.Role.LECTURER)
def assessment_edit(request, pk):
    assessment = get_object_or_404(
        Assessment.objects.select_related("course", "course__program"),
        pk=pk,
    )
    course = assessment.course
    _check_course_permission_for_lecturer(request.user, course)

    AssessmentForm = modelform_factory(
        Assessment,
        fields=["name", "type", "weight_in_course", "max_score", "date"],
    )

    if request.method == "POST":
        form = AssessmentForm(request.POST, instance=assessment)
        if form.is_valid():
            form.save()
            return redirect("assessments:assessment_manage", course_id=course.id)
    else:
        form = AssessmentForm(instance=assessment)

    context = {
        "course": course,
        "assessment": assessment,
        "form": form,
    }
    return render(request, "assessments/assessment_edit.html", context)


@role_required(CustomUser.Role.LECTURER)
def assessment_delete(request, pk):
    assessment = get_object_or_404(
        Assessment.objects.select_related("course", "course__program"),
        pk=pk,
    )
    course = assessment.course
    _check_course_permission_for_lecturer(request.user, course)

    if request.method == "POST":
        assessment.delete()
        return redirect("assessments:assessment_manage", course_id=course.id)

    context = {
        "course": course,
        "assessment": assessment,
    }
    return render(request, "assessments/assessment_confirm_delete.html", context)


@role_required(CustomUser.Role.LECTURER)
def assessment_lo_mapping(request, pk):
    """
    Tek bir assessment için:
    - Course'daki tüm LO'ları listeler
    - Her LO için yüzde girilerek mapping yapılır.
    """
    assessment = get_object_or_404(
        Assessment.objects.select_related("course", "course__program"),
        pk=pk,
    )
    course = assessment.course
    _check_course_permission_for_lecturer(request.user, course)

    los = LearningOutcome.objects.filter(
        course=course
    ).order_by("code")

    existing = {
        m.learning_outcome_id: m
        for m in assessment.lo_mappings.all()
    }

    if request.method == "POST":
        for lo in los:
            field_name = f"lo_{lo.id}"
            raw_value = request.POST.get(field_name, "").strip()

            # Boş ise → mapping sil
            if raw_value == "":
                mapping = existing.get(lo.id)
                if mapping:
                    mapping.delete()
                continue

            try:
                weight = int(raw_value)
            except ValueError:
                continue  # invalid input'u ignore

            if weight <= 0:
                mapping = existing.get(lo.id)
                if mapping:
                    mapping.delete()
                continue

            if weight > 100:
                weight = 100

            mapping = existing.get(lo.id)
            if mapping:
                mapping.weight_in_assessment = weight
                mapping.save()
            else:
                AssessmentLearningOutcome.objects.create(
                    assessment=assessment,
                    learning_outcome=lo,
                    weight_in_assessment=weight,
                )

        return redirect("assessments:assessment_manage", course_id=course.id)

    # GET: template için satır listesi
    rows = []
    for lo in los:
        mapping = existing.get(lo.id)
        rows.append(
            {
                "lo": lo,
                "weight": mapping.weight_in_assessment if mapping else "",
            }
        )

    context = {
        "course": course,
        "assessment": assessment,
        "rows": rows,
    }
    return render(request, "assessments/assessment_lo_mapping.html", context)


@role_required(CustomUser.Role.LECTURER)
def assessment_grade_manage(request, pk):
    """
    Tek bir assessment için öğrencilerin notlarını girme / güncelleme ekranı.
    Burada **raw_score** alanını kullanıyoruz; `score` field'ı yok.
    """
    assessment = get_object_or_404(
        Assessment.objects.select_related("course", "course__program"),
        pk=pk,
    )
    course = assessment.course
    _check_course_permission_for_lecturer(request.user, course)

    # Bu dersin öğrencileri
    students = course.students.all().order_by("last_name", "first_name", "username")

    # Mevcut sonuçları çek
    existing_results = StudentAssessmentResult.objects.filter(
        assessment=assessment,
        student__in=students,
    )
    results_by_student = {r.student_id: r for r in existing_results}

    if request.method == "POST":
        for student in students:
            field_name = f"student_{student.id}"
            raw_value = request.POST.get(field_name, "").strip()

            # Boş bırakıldıysa → kaydı sil veya dokunma
            if raw_value == "":
                # İstersen burada var olan kaydı silebilirsin:
                # existing = results_by_student.get(student.id)
                # if existing:
                #     existing.delete()
                continue

            try:
                score_val = Decimal(raw_value)
            except (InvalidOperation, ValueError):
                # Geçersiz giriş → ignore
                continue

            # update_or_create: aynı öğrenci+assessment için tek kayıt
            StudentAssessmentResult.objects.update_or_create(
                student=student,
                assessment=assessment,
                defaults={
                    "raw_score": score_val,      # 🟩 asıl not
                },
            )

        return redirect("assessments:assessment_grade_manage", pk=assessment.id)

    # GET: tablo için satırları hazırla
    rows = []
    for student in students:
        result = results_by_student.get(student.id)

        score_value = None
        if result is not None:
            # Hem eski hem yeni world ile uyumlu kalmak için:
            score_value = getattr(result, "score", None)
            if score_value is None:
                score_value = getattr(result, "raw_score", None)

        rows.append(
            {
                "student": student,
                "result": result,
                "score": score_value,
            }
        )

    context = {
        "course": course,
        "assessment": assessment,
        "rows": rows,
    }
    return render(request, "assessments/assessment_grade_manage.html", context)
