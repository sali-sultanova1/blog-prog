document.addEventListener("DOMContentLoaded", () => {
    const csrfInput = document.querySelector("[name=csrfmiddlewaretoken]");
    const csrfToken = csrfInput?.value;

    const likeButton = document.getElementById("like-button");
    const bookmarkButton = document.getElementById("bookmark-button");
    const likesCount = document.getElementById("likes-count");

    if (likeButton && csrfToken) {
        likeButton.addEventListener("click", async () => {
            const response = await fetch(likeButton.dataset.url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                },
            });

            if (!response.ok) {
                return;
            }

            const data = await response.json();

            likeButton.classList.toggle("is-active", data.liked);
            likesCount.textContent = data.likes_count;
        });
    }

    if (bookmarkButton && csrfToken) {
        bookmarkButton.addEventListener("click", async () => {
            const response = await fetch(bookmarkButton.dataset.url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                },
            });

            if (!response.ok) {
                return;
            }

            const data = await response.json();

            bookmarkButton.classList.toggle(
                "is-active",
                data.bookmarked
            );

            const label = bookmarkButton.querySelector("span");

            if (label) {
                label.textContent = data.bookmarked
                    ? "Сохранено"
                    : "Сохранить";
            }
        });
    }

    const commentForm = document.getElementById("comment-form");
    const commentsContainer = document.getElementById("comments");

    if (commentForm && commentsContainer && csrfToken) {
        commentForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const textarea = document.getElementById("comment-content");
            const content = textarea.value.trim();

            if (!content) {
                return;
            }

            const response = await fetch(commentForm.dataset.url, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({
                    article: Number(commentForm.dataset.articleId),
                    content,
                }),
            });

            if (!response.ok) {
                return;
            }

            const comment = await response.json();

            const noCommentsMessage = document.getElementById(
                "no-comments-message"
            );

            if (noCommentsMessage) {
                noCommentsMessage.remove();
            }

            commentsContainer.prepend(
                createCommentElement(comment)
            );

            textarea.value = "";
        });
    }

    if (commentsContainer && csrfToken) {
        commentsContainer.addEventListener("click", async (event) => {
            const commentElement = event.target.closest(".comment");

            if (!commentElement) {
                return;
            }

            const editBlock = commentElement.querySelector(".comment-edit");

            if (event.target.classList.contains("edit-comment-button")) {
                setCommentEditing(commentElement, true);
            }

            if (event.target.classList.contains("cancel-comment-button")) {
                setCommentEditing(commentElement, false);
            }

            if (event.target.classList.contains("save-comment-button")) {
                const textarea = editBlock.querySelector("textarea");
                const content = textarea.value.trim();

                if (!content) {
                    return;
                }

                const response = await fetch(commentElement.dataset.url, {
                    method: "PATCH",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken,
                    },
                    body: JSON.stringify({
                        content,
                    }),
                });

                if (!response.ok) {
                    return;
                }

                const comment = await response.json();

                const contentElement = commentElement.querySelector(
                    ".comment-content"
                );

                contentElement.textContent = comment.content;

                setCommentEditing(commentElement, false);
            }

            if (event.target.classList.contains("delete-comment-button")) {
                const response = await fetch(commentElement.dataset.url, {
                    method: "DELETE",
                    headers: {
                        "X-CSRFToken": csrfToken,
                    },
                });

                if (response.ok) {
                    commentElement.remove();
                }
            }
        });
    }

    function setCommentEditing(commentElement, editing) {
        const content = commentElement.querySelector(".comment-content");
        const actions = commentElement.querySelector(".comment-actions");
        const editBlock = commentElement.querySelector(".comment-edit");

        if (content) {
            content.hidden = editing;
        }

        if (actions) {
            actions.hidden = editing;
        }

        if (editBlock) {
            editBlock.hidden = !editing;

            if (editing) {
                const textarea = editBlock.querySelector("textarea");

                if (textarea) {
                    textarea.focus();
                    textarea.setSelectionRange(
                        textarea.value.length,
                        textarea.value.length
                    );
                }
            }
        }
    }

    function createCommentElement(comment) {
        const element = document.createElement("div");

        element.className = "comment";
        element.dataset.commentId = comment.id;
        element.dataset.url =
            `${commentsContainer.dataset.baseUrl}${comment.id}/`;

        const head = document.createElement("div");
        head.className = "comment__head";

        const username = document.createElement("strong");
        username.className = "comment-username";
        username.textContent = comment.username;

        const date = document.createElement("span");
        date.className = "comment-date";
        date.textContent = comment.created_at
            ? new Date(comment.created_at).toLocaleString("ru-RU")
            : "Только что";

        head.append(username, date);

        const content = document.createElement("div");
        content.className = "comment-content";
        content.textContent = comment.content;

        const actions = document.createElement('div')
        actions.className = 'comment-actions'

        const editButton = document.createElement('button')
        editButton.type = 'button'
        editButton.className = 'edit-comment-button'
        editButton.textContent = 'Редактировать'

        const deleteButton = document.createElement('button')
        deleteButton.type = 'button'
        deleteButton.className = 'delete-comment-button'
        deleteButton.textContent = 'Удалить'

        actions.append(editButton, deleteButton)
        
        const editBlock = document.createElement("div");
        editBlock.className = "comment-edit";
        editBlock.hidden = true;

        const textarea = document.createElement("textarea");
        textarea.value = comment.content;

        const saveButton = document.createElement("button");
        saveButton.type = "button";
        saveButton.className = "save-comment-button";
        saveButton.textContent = "Сохранить";

        const cancelButton = document.createElement("button");
        cancelButton.type = "button";
        cancelButton.className = "cancel-comment-button";
        cancelButton.textContent = "Отмена";

        editBlock.append(textarea, saveButton, cancelButton);

        element.append(head, content, actions, editBlock);

        return element;
    }
});