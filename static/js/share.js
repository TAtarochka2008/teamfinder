document.addEventListener("click", async (event) => {
    const button = event.target.closest(".share-button");
    if (!button) {
        return;
    }
    const url = window.location.href;
    if (navigator.clipboard) {
        await navigator.clipboard.writeText(url);
        if (button.classList.contains("share-icon-button")) {
            [...button.childNodes].forEach((node) => {
                if (node.nodeType === Node.TEXT_NODE) {
                    node.remove();
                }
            });
        }
        button.classList.add("copied");
        setTimeout(() => {
            button.classList.remove("copied");
        }, 1800);
    } else {
        window.prompt("Скопируйте ссылку", url);
    }
});
