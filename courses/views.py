from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from accounts.decorators import role_required
from accounts.models import CustomUser
from organizations.models import Program
from .models import Course
from .forms import CourseForm


@role_required(CustomUser.Role.STUDENT_AFFAIRS)
def course_list(request):
    program_id = request.GET.get("program")
    if program_id:
        program = get_object_or_404(Program, id=program_id)
        courses = Course.objects.filter(program=program).select_related("program")
    else:
        program = None
        courses = Course.objects.select_related("program").all()

    context = {
        "courses": courses,
        "selected_program": program,
    }
    return render(request, "courses/course_list.html", context)


@role_required(CustomUser.Role.STUDENT_AFFAIRS)
def course_create(request):
    initial = {}
    program_id = request.GET.get("program")
    if program_id:
        initial["program"] = get_object_or_404(Program, id=program_id)

    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            return redirect(f"/courses/?program={course.program.id}")
    else:
        form = CourseForm(initial=initial)

    context = {
        "form": form,
        "course": None,  # edit ile aynı template'i kullanacağız
    }
    return render(request, "courses/course_form.html", context)


@role_required(CustomUser.Role.STUDENT_AFFAIRS)
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == "POST":
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()  # save içinde zaten auto-enroll çalışıyor
            # Program filtresini korumak için query param ekleyelim
            return redirect(f"/courses/?program={course.program.id}")
    else:
        form = CourseForm(instance=course)

    context = {
        "form": form,
        "course": course,
    }
    return render(request, "courses/course_form.html", context)


@role_required(CustomUser.Role.STUDENT_AFFAIRS)
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)

    if request.method == "POST":
        program_id = course.program.id
        course.delete()
        return redirect(f"/courses/?program={program_id}")

    return render(
        request,
        "courses/course_confirm_delete.html",
        {"course": course},
    )


@role_required(CustomUser.Role.LECTURER)
def lecturer_dashboard(request):
    """
    Lecturer kendi sorumlu olduğu course'ları görsün.
    """
    user = request.user
    courses = (
        Course.objects.filter(
            Q(lecturer=user) | Q(id__in=user.lecturer_courses.values("id"))
        )
        .select_related("program")
        .distinct()
    )

    context = {
        "courses": courses,
    }
    return render(request, "courses/lecturer_dashboard.html", context)
