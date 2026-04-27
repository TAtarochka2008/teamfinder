from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from projects.models import Project

from .forms import EmailAuthenticationForm, ProfileForm, SignupForm
from .models import Profile, Skill


def paginate(request, queryset, per_page=12):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))


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
    projects = Project.objects.filter(author=profile.user).select_related(
        "author", "author__profile"
    )
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
