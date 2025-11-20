from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import PermissionDenied

from accounts.decorators import role_required
from accounts.models import CustomUser
from organizations.models import Program
from curriculum.models import Curriculum
from .models import ProgramOutcome, LearningOutcome, LearningOutcomeProgramOutcome
from .forms import ProgramOutcomeForm, LearningOutcomeForm


def _check_program_permission(user: CustomUser, program: Program):
    """
    Faculty Member sadece sorumlu olduğu faculty'deki programlar için
    PO düzenleyebilsin. Admin her yere girebilir.
    """
    if user.is_admin:
        return
    if program.faculty.responsible_id != user.id:
        raise PermissionDenied("You are not allowed to manage this program.")


@role_required(CustomUser.Role.FACULTY_MEMBER)
def program_outcome_manage(request, program_id):
    program = get_object_or_404(Program, id=program_id)
    _check_program_permission(request.user, program)

    outcomes = ProgramOutcome.objects.filter(program=program).order_by("order", "code")

    if request.method == "POST":
        form = ProgramOutcomeForm(request.POST)
        if form.is_valid():
            po = form.save(commit=False)
            po.program = program
            po.save()
            return redirect("outcomes:program_outcome_manage", program_id=program.id)
    else:
        form = ProgramOutcomeForm()

    context = {
        "program": program,
        "outcomes": outcomes,
        "form": form,
    }
    return render(request, "outcomes/program_outcome_manage.html", context)


@role_required(CustomUser.Role.FACULTY_MEMBER)
def program_outcome_edit(request, pk):
    po = get_object_or_404(ProgramOutcome, pk=pk)
    program = po.program
    _check_program_permission(request.user, program)

    if request.method == "POST":
        form = ProgramOutcomeForm(request.POST, instance=po)
        if form.is_valid():
            form.save()
            return redirect("outcomes:program_outcome_manage", program_id=program.id)
    else:
        form = ProgramOutcomeForm(instance=po)

    context = {
        "program": program,
        "form": form,
        "po": po,
    }
    return render(request, "outcomes/program_outcome_edit.html", context)


@role_required(CustomUser.Role.FACULTY_MEMBER)
def program_outcome_delete(request, pk):
    po = get_object_or_404(ProgramOutcome, pk=pk)
    program = po.program
    _check_program_permission(request.user, program)

    if request.method == "POST":
        po.delete()
        return redirect("outcomes:program_outcome_manage", program_id=program.id)

    context = {
        "program": program,
        "po": po,
    }
    return render(request, "outcomes/program_outcome_confirm_delete.html", context)


def _check_curriculum_permission_for_lecturer(user: CustomUser, curriculum: Curriculum):
    """
    Lecturer sadece kendisine atanmış curriculum'lar için LO yönetebilsin.
    Admin her şeye girebilir.
    """
    if user.is_admin:
        return
    if curriculum.lecturer_id != user.id:
        raise PermissionDenied("You are not allowed to manage this curriculum.")


@role_required(CustomUser.Role.LECTURER)
def learning_outcome_manage(request, curriculum_id):
    curriculum = get_object_or_404(
        Curriculum.objects.select_related("program"),
        id=curriculum_id,
    )
    _check_curriculum_permission_for_lecturer(request.user, curriculum)

    los = LearningOutcome.objects.filter(
        curriculum=curriculum
    ).prefetch_related("program_outcomes")

    if request.method == "POST":
        form = LearningOutcomeForm(request.POST)
        if form.is_valid():
            lo = form.save(commit=False)
            lo.curriculum = curriculum
            lo.save()
            return redirect("outcomes:learning_outcome_manage", curriculum_id=curriculum.id)
    else:
        form = LearningOutcomeForm()

    context = {
        "curriculum": curriculum,
        "los": los,
        "form": form,
    }
    return render(request, "outcomes/learning_outcome_manage.html", context)


@role_required(CustomUser.Role.LECTURER)
def learning_outcome_edit(request, pk):
    lo = get_object_or_404(
        LearningOutcome.objects.select_related("curriculum", "curriculum__program"),
        pk=pk,
    )
    curriculum = lo.curriculum
    _check_curriculum_permission_for_lecturer(request.user, curriculum)

    if request.method == "POST":
        form = LearningOutcomeForm(request.POST, instance=lo)
        if form.is_valid():
            form.save()
            return redirect("outcomes:learning_outcome_manage", curriculum_id=curriculum.id)
    else:
        form = LearningOutcomeForm(instance=lo)

    context = {
        "curriculum": curriculum,
        "form": form,
        "lo": lo,
    }
    return render(request, "outcomes/learning_outcome_edit.html", context)


@role_required(CustomUser.Role.LECTURER)
def learning_outcome_delete(request, pk):
    lo = get_object_or_404(
        LearningOutcome.objects.select_related("curriculum", "curriculum__program"),
        pk=pk,
    )
    curriculum = lo.curriculum
    _check_curriculum_permission_for_lecturer(request.user, curriculum)

    if request.method == "POST":
        lo.delete()
        return redirect("outcomes:learning_outcome_manage", curriculum_id=curriculum.id)

    context = {
        "curriculum": curriculum,
        "lo": lo,
    }
    return render(request, "outcomes/learning_outcome_confirm_delete.html", context)


@role_required(CustomUser.Role.LECTURER)
def learning_outcome_mapping(request, pk):
    """
    Tek bir LO için:
    - Programdaki tüm PO'ları listeler
    - Her PO için yüzde girilerek mapping yapılır.
    """
    lo = get_object_or_404(
        LearningOutcome.objects.select_related("curriculum", "curriculum__program"),
        pk=pk,
    )
    curriculum = lo.curriculum
    _check_curriculum_permission_for_lecturer(request.user, curriculum)

    program = curriculum.program
    pos = ProgramOutcome.objects.filter(program=program).order_by("order", "code")

    # Mevcut mapping'leri dictionary olarak tutalım
    existing = {
        m.program_outcome_id: m
        for m in lo.lo_po_mappings.all()
    }

    if request.method == "POST":
        for po in pos:
            field_name = f"po_{po.id}"
            raw_value = request.POST.get(field_name, "").strip()

            # Boş → mapping sil
            if raw_value == "":
                mapping = existing.get(po.id)
                if mapping:
                    mapping.delete()
                continue

            # Sayıya çevir
            try:
                weight = int(raw_value)
            except ValueError:
                continue  # invalid input'u şimdilik ignore

            # 0 veya altı → mapping sil
            if weight <= 0:
                mapping = existing.get(po.id)
                if mapping:
                    mapping.delete()
                continue

            # 100'den büyükse clamp
            if weight > 100:
                weight = 100

            mapping = existing.get(po.id)
            if mapping:
                mapping.weight = weight
                mapping.save()
            else:
                LearningOutcomeProgramOutcome.objects.create(
                    learning_outcome=lo,
                    program_outcome=po,
                    weight=weight,
                )

        return redirect("outcomes:learning_outcome_manage", curriculum_id=curriculum.id)

    # GET → template'e PO + mevcut weight listesi gönder
    rows = []
    for po in pos:
        mapping = existing.get(po.id)
        rows.append(
            {
                "po": po,
                "weight": mapping.weight if mapping else "",
            }
        )

    context = {
        "curriculum": curriculum,
        "lo": lo,
        "rows": rows,
    }
    return render(request, "outcomes/learning_outcome_mapping.html", context)
