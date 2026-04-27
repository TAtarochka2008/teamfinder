from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        labels = {
            "name": "Название",
            "description": "Описание проекта",
            "github_url": "Ссылка на GitHub",
            "status": "Статус",
        }
        widgets = {
            "status": forms.Select(),
        }

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url", "")
        if url and "github.com" not in url.lower():
            raise forms.ValidationError("Ссылка должна вести на GitHub.")
        return url
