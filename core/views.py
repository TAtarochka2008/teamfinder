from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import EmailAuthenticationForm, ProfileForm, ProjectForm, SignupForm
from .models import Profile, Project, Skill


def paginate(request, queryset, per_page=12):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))


def home(request):
    projects = Project.objects.select_related("author", "author__profile").prefetch_related("members")
    page_obj = paginate(request, projects)
    return render(request, "core/home.html", {"page_obj": page_obj})


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Аккаунт создан. Теперь можно войти.")
            return redirect("login")
    else:
        form = SignupForm()
    return render(request, "registration/signup.html", {"form": form})


class EmailLoginView(LoginView):
    authentication_form = EmailAuthenticationForm
    template_name = "registration/login.html"


def profile_detail(request, pk):
    profile = get_object_or_404(
        Profile.objects.select_related("user").prefetch_related("skills", "user__projects"),
        pk=pk,
    )
    projects = profile.user.projects.select_related("author", "author__profile")
    return render(
        request,
        "core/profile_detail.html",
        {
            "profile": profile,
            "projects": projects,
            "is_owner": request.user.is_authenticated and request.user == profile.user,
        },
    )


@login_required
def profile_edit(request, pk):
    profile = get_object_or_404(Profile.objects.select_related("user"), pk=pk)
    if request.user != profile.user:
        return redirect("profile_detail", pk=profile.pk)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль обновлён.")
            return redirect("profile_detail", pk=profile.pk)
    else:
        form = ProfileForm(instance=profile)
    return render(request, "core/profile_edit.html", {"form": form, "profile": profile})


def user_list(request):
    active_skill = request.GET.get("skill")
    profiles = Profile.objects.select_related("user").prefetch_related("skills")
    if active_skill:
        profiles = profiles.filter(skills__name=active_skill)
    skills = Skill.objects.all()
    page_obj = paginate(request, profiles.distinct())
    return render(
        request,
        "core/user_list.html",
        {"page_obj": page_obj, "skills": skills, "active_skill": active_skill},
    )


def project_detail(request, pk):
    project = get_object_or_404(
        Project.objects.select_related("author", "author__profile").prefetch_related(
            "members", "members__profile"
        ),
        pk=pk,
    )
    is_owner = request.user.is_authenticated and request.user == project.author
    is_member = request.user.is_authenticated and project.members.filter(pk=request.user.pk).exists()
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


def skill_search(request):
    query = request.GET.get("q", "").strip()
    skills = Skill.objects.filter(name__icontains=query)[:10] if query else Skill.objects.none()
    exact = Skill.objects.filter(name__iexact=query).exists() if query else True
    return JsonResponse(
        {
            "results": [{"id": skill.id, "name": skill.name} for skill in skills],
            "can_create": bool(query and not exact),
            "query": query,
        }
    )


@require_POST
@login_required
def profile_skill_add(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    if request.user != profile.user:
        return JsonResponse({"error": "forbidden"}, status=403)
    name = request.POST.get("name", "").strip()
    if not name:
        return JsonResponse({"error": "empty"}, status=400)
    skill, created = Skill.objects.get_or_create(name=name[:80])
    profile.skills.add(skill)
    return JsonResponse({"id": skill.id, "name": skill.name, "created": created})


@require_POST
@login_required
def profile_skill_delete(request, pk, skill_id):
    profile = get_object_or_404(Profile, pk=pk)
    if request.user != profile.user:
        return JsonResponse({"error": "forbidden"}, status=403)
    profile.skills.remove(skill_id)
    return JsonResponse({"ok": True})
