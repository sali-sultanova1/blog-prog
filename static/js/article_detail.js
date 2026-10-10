document.addEventListener("DOMContentLoaded", () => {
    "use strict";

    const csrfToken = document.querySelector(
        "[name=csrfmiddlewaretoken]"
    )?.value;

    const comments = document.getElementById("comments");
    const commentForm = document.getElementById("comment-form");

    function notify(message) {
        if (window.NewsUI) {
            window.NewsUI.notify(message);
        } else {
            window.alert(message);
        }
    }

    async function request(url, method, body) {
        const headers = {
            "Accept": "application/json",
            "X-CSRFToken": csrfToken || "",
        };

        if (body !== undefined) headers["Content-Type"] = "application/json";

        const response = await fetch(url, {
            method,
            headers,
            credentials: "same-origin",
            body: body === undefined ? undefined : JSON.stringify(body),
        });

        if (!response.ok) {
            if (response.status === 401 || response.status === 403) {
                throw new Error("Не удалось выполнить действие. Проверьте, что вы вошли в аккаунт, и обновите страницу.");
            }

            if (response.status === 400) {
                throw new Error("Проверьте введённые данные и попробуйте ещё раз.");
            }

            throw new Error("Не удалось сохранить изменения. Попробуйте ещё раз.");
        }

        if (response.status === 204) return null;
        return response.json();
    }

    async function run(button, action) {
        if (button.disabled) return;

        button.disabled = true;
        button.setAttribute("aria-busy", "true");

        try {
            await action();
        } catch (error) {
            notify(error instanceof TypeError
                ? "Нет связи с сервером. Проверьте интернет и повторите действие."
                : error.message);
        } finally {
            button.disabled = false;
            button.removeAttribute("aria-busy");
        }
    }

    const likeButton = document.getElementById("like-button");
    const bookmarkButton = document.getElementById("bookmark-button");

    [likeButton, bookmarkButton].forEach((button) => {
        if (button) {
            button.setAttribute(
                "aria-pressed",
                String(button.classList.contains("is-active"))
            );
        }
    });

    likeButton?.addEventListener("click", () => {
        run(likeButton, async () => {
            const data = await request(likeButton.dataset.url, "POST");

            likeButton.classList.toggle("is-active", data.liked);
            likeButton.setAttribute("aria-pressed", String(data.liked));
            document.getElementById("likes-count").textContent = data.likes_count;
        });
    });

    bookmarkButton?.addEventListener("click", () => {
        run(bookmarkButton, async () => {
            const data = await request(bookmarkButton.dataset.url, "POST");

            bookmarkButton.classList.toggle("is-active", data.bookmarked);
            bookmarkButton.setAttribute("aria-pressed", String(data.bookmarked));
            bookmarkButton.querySelector("span").textContent =
                data.bookmarked ? "Сохранено" : "Сохранить";

            notify(data.bookmarked
                ? "Статья добавлена в закладки."
                : "Статья удалена из закладок.");
        });
    });

    function updateEmptyState() {
        if (!comments) return;

        const empty = document.getElementById("no-comments-message");
        const hasComments = Boolean(comments.querySelector(".comment"));

        if (hasComments) {
            empty?.remove();
        } else if (!empty) {
            const message = document.createElement("p");
            message.id = "no-comments-message";
            message.className = "login-hint";
            message.textContent = "Комментариев пока нет. Будьте первым.";
            comments.append(message);
        }
    }

    function setEditing(element, editing) {
        element.querySelector(".comment-content").hidden = editing;
        element.querySelector(".comment-actions").hidden = editing;
        element.querySelector(".comment-edit").hidden = !editing;

        if (editing) {
            element.querySelector(".comment-edit textarea").focus();
        } else {
            element.querySelector(".edit-comment-button")?.focus();
        }
    }

    function makeButton(className, text) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = className;
        button.textContent = text;
        return button;
    }

    function createComment(data) {
        const element = document.createElement("div");
        element.className = "comment";
        element.dataset.commentId = data.id;
        element.dataset.url =
            `${comments.dataset.baseUrl.replace(/\/?$/, "/")}${data.id}/`;

        const head = document.createElement("div");
        head.className = "comment__head";

        const username = document.createElement("strong");
        username.className = "comment-username";
        username.textContent = data.username;

        const date = document.createElement("span");
        date.className = "comment-date";
        date.textContent = data.created_at
            ? new Date(data.created_at).toLocaleString("ru-RU")
            : "Только что";

        head.append(username, date);

        const content = document.createElement("div");
        content.className = "comment-content";
        content.textContent = data.content;

        const actions = document.createElement("div");
        actions.className = "comment-actions";
        actions.append(
            makeButton("edit-comment-button", "Редактировать"),
            makeButton("delete-comment-button", "Удалить")
        );

        const editor = document.createElement("div");
        editor.className = "comment-edit";
        editor.hidden = true;

        const textarea = document.createElement("textarea");
        textarea.rows = 4;
        textarea.value = data.content;
        textarea.dataset.savedValue = data.content;
        textarea.setAttribute("aria-label", "Текст комментария");

        editor.append(
            textarea,
            makeButton("save-comment-button", "Сохранить"),
            document.createTextNode(" "),
            makeButton("cancel-comment-button", "Отмена")
        );

        element.append(head, content, actions, editor);
        return element;
    }

    commentForm?.addEventListener("submit", (event) => {
        event.preventDefault();

        const textarea = document.getElementById("comment-content");
        const content = textarea.value.trim();
        const button = commentForm.querySelector("button[type='submit']");

        if (!content) {
            notify("Напишите комментарий перед отправкой.");
            textarea.focus();
            return;
        }

        run(button, async () => {
            textarea.readOnly = true;

            try {
                const data = await request(commentForm.dataset.url, "POST", {
                    article: Number(commentForm.dataset.articleId),
                    content,
                });

                comments.prepend(createComment(data));
                textarea.value = "";
                updateEmptyState();
                notify("Комментарий опубликован.");
            } finally {
                textarea.readOnly = false;
            }
        });
    });

    comments?.addEventListener("click", async (event) => {
        const button = event.target.closest("button");
        const element = button?.closest(".comment");

        if (!button || !element) return;

        const editor = element.querySelector(".comment-edit");
        const textarea = editor?.querySelector("textarea");

        if (button.classList.contains("edit-comment-button")) {
            setEditing(element, true);
            return;
        }

        if (button.classList.contains("cancel-comment-button")) {
            textarea.value = textarea.dataset.savedValue ?? textarea.defaultValue;
            setEditing(element, false);
            return;
        }

        if (button.classList.contains("save-comment-button")) {
            const content = textarea.value.trim();

            if (!content) {
                notify("Комментарий не может быть пустым.");
                textarea.focus();
                return;
            }

            const cancel = editor.querySelector(".cancel-comment-button");

            await run(button, async () => {
                textarea.readOnly = true;
                cancel.disabled = true;

                try {
                    const data = await request(element.dataset.url, "PATCH", { content });

                    element.querySelector(".comment-content").textContent = data.content;
                    textarea.value = data.content;
                    textarea.dataset.savedValue = data.content;
                    setEditing(element, false);
                    notify("Комментарий обновлён.");
                } finally {
                    textarea.readOnly = false;
                    cancel.disabled = false;
                }
            });

            return;
        }

        if (button.classList.contains("delete-comment-button")) {
            const approved = window.NewsUI
                ? await window.NewsUI.confirm("Удалить этот комментарий? Восстановить его не получится.")
                : window.confirm("Удалить комментарий?");

            if (!approved) return;

            await run(button, async () => {
                await request(element.dataset.url, "DELETE");
                element.remove();
                updateEmptyState();
                document.getElementById("comment-content")?.focus();
                notify("Комментарий удалён.");
            });
        }
    });

    comments?.querySelectorAll(".comment-edit textarea").forEach((textarea) => {
        textarea.setAttribute("aria-label", "Текст комментария");
        textarea.dataset.savedValue = textarea.value;
    });
});