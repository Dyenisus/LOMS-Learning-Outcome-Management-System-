from django.shortcuts import render, redirect, get_object_or_404
from accounts.decorators import role_required
from accounts.models import CustomUser
from .models import Faculty, Program
from .forms import FacultyForm, ProgramForm


@role_required(CustomUser.Role.STUDENT_AFFAIRS)
def faculty_program_list(request):
    """
   For Student Affairs: 
   - Lists all Faculties + Programs
   - Shows a form to add a new Faculty
    """
    faculties = Faculty.objects.prefetch_related("programs").all()
    faculty_form = FacultyForm()

    if request.method == "POST":
        faculty_form = FacultyForm(request.POST)
        if faculty_form.is_valid():
            faculty_form.save()
            return redirect("organizations:faculty_program_list")

    context = {
        "faculties": faculties,
        "faculty_form": faculty_form,
    }
    return render(request, "organizations/faculty_program_list.html", context)


@role_required(CustomUser.Role.STUDENT_AFFAIRS)
def program_create(request):
    """
    For Student Affairs: 
    - New Program Addition page
    """
    if request.method == "POST":
        form = ProgramForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("organizations:faculty_program_list")
    else:
        form = ProgramForm()

    context = {"form": form}
    return render(request, "organizations/program_form.html", context)


@role_required(CustomUser.Role.STUDENT_AFFAIRS)
def program_edit(request, pk):
    program = get_object_or_404(Program, pk=pk)

    if request.method == "POST":
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            return redirect("organizations:faculty_program_list")
    else:
        form = ProgramForm(instance=program)

    context = {
        "form": form,
        "program": program,
    }
    return render(request, "organizations/program_form.html", context)


@role_required(CustomUser.Role.STUDENT_AFFAIRS)
def program_delete(request, pk):
    program = get_object_or_404(Program, pk=pk)

    if request.method == "POST":
        program.delete()
        return redirect("organizations:faculty_program_list")

    context = {
        "program": program,
    }
    return render(request, "organizations/program_confirm_delete.html", context)


@role_required(CustomUser.Role.FACULTY_MEMBER)
def faculty_member_dashboard(request):
    user = request.user

    if user.is_admin:
        faculties = Faculty.objects.all()
    else:
        faculties = Faculty.objects.filter(responsible=user)

    programs = Program.objects.filter(faculty__in=faculties).select_related("faculty")

    context = {
        "faculties": faculties,
        "programs": programs,
    }
    return render(request, "organizations/faculty_member_dashboard.html", context)

@role_required(CustomUser.Role.STUDENT_AFFAIRS)
def faculty_edit(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)

    if request.method == "POST":
        form = FacultyForm(request.POST, instance=faculty)
        if form.is_valid():
            form.save()
            return redirect("organizations:faculty_program_list")
    else:
        form = FacultyForm(instance=faculty)

    context = {
        "faculty": faculty,
        "form": form,
    }
    return render(request, "organizations/faculty_form.html", context)

@role_required(CustomUser.Role.STUDENT_AFFAIRS)
def faculty_delete(request, pk):
    faculty = get_object_or_404(Faculty, pk=pk)

    if request.method == "POST":
        faculty.delete()
        return redirect("organizations:faculty_program_list")

    return render(request, "organizations/faculty_confirm_delete.html", {"faculty": faculty})
