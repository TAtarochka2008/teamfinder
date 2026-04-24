const tags = document.querySelector("#skill-tags");
const openButton = document.querySelector("#skill-open");
const box = document.querySelector("#skill-box");
const input = document.querySelector("#skill-input");
const suggestions = document.querySelector("#skill-suggestions");
const profileId = tags?.dataset.profile;

function csrfToken() {
    const value = document.cookie
        .split("; ")
        .find((item) => item.startsWith("csrftoken="));
    return value ? decodeURIComponent(value.split("=")[1]) : "";
}

function emptyLabel() {
    return document.querySelector("#skills-empty");
}

function renderSkill(skill) {
    const existing = tags.querySelector(`[data-id="${skill.id}"]`);
    if (existing) {
        return;
    }
    const label = emptyLabel();
    if (label) {
        label.remove();
    }
    const tag = document.createElement("span");
    tag.className = "tag";
    tag.dataset.id = skill.id;
    tag.textContent = skill.name;
    const remove = document.createElement("button");
    remove.type = "button";
    remove.textContent = "×";
    tag.append(remove);
    tags.append(tag);
}

async function addSkill(name) {
    const body = new URLSearchParams({ name });
    const response = await fetch(`/users/${profileId}/skills/add/`, {
        method: "POST",
        headers: { "X-CSRFToken": csrfToken() },
        body,
    });
    if (response.ok) {
        renderSkill(await response.json());
        input.value = "";
        suggestions.innerHTML = "";
    }
}

async function deleteSkill(skillId, node) {
    const response = await fetch(`/users/${profileId}/skills/${skillId}/delete/`, {
        method: "POST",
        headers: { "X-CSRFToken": csrfToken() },
    });
    if (response.ok) {
        node.remove();
        if (!tags.querySelector(".tag")) {
            const label = document.createElement("span");
            label.className = "muted";
            label.id = "skills-empty";
            label.textContent = "Навыки пока не указаны.";
            tags.append(label);
        }
    }
}

let timer = null;

function showSuggestions(data) {
    suggestions.innerHTML = "";
    data.results.forEach((skill) => {
        const option = document.createElement("button");
        option.type = "button";
        option.textContent = skill.name;
        option.addEventListener("click", () => addSkill(skill.name));
        suggestions.append(option);
    });
    if (data.can_create) {
        const create = document.createElement("button");
        create.type = "button";
        create.textContent = `Создать "${data.query}"`;
        create.addEventListener("click", () => addSkill(data.query));
        suggestions.append(create);
    }
}

openButton?.addEventListener("click", () => {
    box.classList.toggle("hidden");
    input.focus();
});

input?.addEventListener("input", () => {
    clearTimeout(timer);
    const query = input.value.trim();
    timer = setTimeout(async () => {
        if (!query) {
            suggestions.innerHTML = "";
            return;
        }
        const response = await fetch(`/skills/search/?q=${encodeURIComponent(query)}`);
        showSuggestions(await response.json());
    }, 250);
});

input?.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        event.preventDefault();
        const query = input.value.trim();
        if (query) {
            addSkill(query);
        }
    }
});

tags?.addEventListener("click", (event) => {
    const button = event.target.closest("button");
    if (!button) {
        return;
    }
    const tag = button.closest(".tag");
    deleteSkill(tag.dataset.id, tag);
});
