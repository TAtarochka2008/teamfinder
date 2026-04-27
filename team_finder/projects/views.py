from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import Project


def paginate(request, queryset, per_page=12):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))


def home(request):
    projects = Project.objects.select_related("author", "author__profile").prefetch_related(
        "members"
    )
    page_obj = paginate(request, projects)
    return render(request, "core/home.html", {"page_obj": page_obj})


def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.select_related("author", "author__profile").prefetch_related(
            "members", "members__profile"
        ),
        pk=pk,
    )
    is_owner = request.user.is_authenticated and request.user == project.author
    is_member = (
        request.user.is_authenticated
        and project.members.filter(pk=request.user.pk).exists()
    )
    return render(
        request,
        "core/project_detail.html",
        {"project": project, "is_owner": is_owner, "is_member": is_member},
    )


@login_required
def project_create(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.author = request.user
            project.save()
            project.members.add(request.user)
            messages.success(request, "Проект опубликован.")
            return redirect("project_detail", pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, "core/project_form.html", {"form": form, "is_edit": False})


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user != project.author:
        return redirect("project_detail", pk=project.pk)
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Проект сохранён.")
            return redirect("project_detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)
    return render(
        request,
        "core/project_form.html",
        {"form": form, "project": project, "is_edit": True},
    )


@require_POST
@login_required
def project_join(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.status == Project.OPEN:
        project.members.add(request.user)
        messages.success(request, "Вы присоединились к проекту.")
    return redirect("project_detail", pk=project.pk)


@require_POST
@login_required
def project_finish(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.user == project.author:
        project.status = Project.CLOSED
        project.save(update_fields=["status", "updated_at"])
        messages.success(request, "Проект закрыт.")
    return redirect("project_detail", pk=project.pk)
