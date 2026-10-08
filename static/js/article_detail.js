document.addEventListener("DOMContentLoaded", () => {
    const csrfInput = document.querySelector(
        "[name=csrfmiddlewaretoken]"
    );

    if (!csrfInput) {
        return;
    }

    const csrfToken = csrfInput.value;

    const likeButton = document.getElementById("like-button");
    const bookmarkButton = document.getElementById("bookmark-button");
    const likesCount = document.getElementById("likes-count");

    if (likeButton) {
        likeButton.addEventListener("click", async () => {
            const response = await fetch(
                likeButton.dataset.url,
                {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken,
                    },
                }
            );

            if (!response.ok) {
                return;
            }

            const data = await response.json();

            likeButton.textContent = data.liked
                ? "Убрать лайк"
                : "Поставить лайк";

            likesCount.textContent = data.likes_count;
        });
    }

    if (bookmarkButton) {
        bookmarkButton.addEventListener("click", async () => {
            const response = await fetch(
                bookmarkButton.dataset.url,
                {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken,
                    },
                }
            );

            if (!response.ok) {
                return;
            }

            const data = await response.json();

            bookmarkButton.textContent = data.bookmarked
                ? "Убрать из закладок"
                : "Сохранить в закладки";
        });
    }


    const commentForm = document.getElementById("comment-form");
    const commentsContainer = document.getElementById("comments");

    if (commentForm) {
        commentForm.addEventListener("submit", async (event) => {
            event.preventDefault();

            const textarea = document.getElementById(
                "comment-content"
            );

            const content = textarea.value.trim();

            if (!content) {
                return;
            }

            const response = await fetch(
                commentForm.dataset.url,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken,
                    },
                    body: JSON.stringify({
                        article: Number(
                            commentForm.dataset.articleId
                        ),
                        content: content,
                    }),
                }
            );

            if (!response.ok) {
                return;
            }

            const comment = await response.json();

            const element = createCommentElement(comment);

            commentsContainer.prepend(element);

            textarea.value = "";
        });
    }


    if (commentsContainer) {
        commentsContainer.addEventListener(
            "click",
            async (event) => {
                const commentElement = event.target.closest(
                    ".comment"
                );

                if (!commentElement) {
                    return;
                }

                const editBlock = commentElement.querySelector(
                    ".comment-edit"
                );

                if (
                    event.target.classList.contains(
                        "edit-comment-button"
                    )
                ) {
                    editBlock.hidden = false;
                }

                if (
                    event.target.classList.contains(
                        "cancel-comment-button"
                    )
                ) {
                    editBlock.hidden = true;
                }

                if (
                    event.target.classList.contains(
                        "save-comment-button"
                    )
                ) {
                    const textarea = editBlock.querySelector(
                        "textarea"
                    );

                    const content = textarea.value.trim();

                    if (!content) {
                        return;
                    }

                    const response = await fetch(
                        commentElement.dataset.url,
                        {
                            method: "PATCH",
                            headers: {
                                "Content-Type": "application/json",
                                "X-CSRFToken": csrfToken,
                            },
                            body: JSON.stringify({
                                content: content,
                            }),
                        }
                    );

                    if (!response.ok) {
                        return;
                    }

                    const comment = await response.json();

                    commentElement.querySelector(
                        ".comment-content"
                    ).textContent = comment.content;

                    editBlock.hidden = true;
                }

                if (
                    event.target.classList.contains(
                        "delete-comment-button"
                    )
                ) {
                    const response = await fetch(
                        commentElement.dataset.url,
                        {
                            method: "DELETE",
                            headers: {
                                "X-CSRFToken": csrfToken,
                            },
                        }
                    );

                    if (response.ok) {
                        commentElement.remove();
                    }
                }
            }
        );
    }


    function createCommentElement(comment) {
        const element = document.createElement("div");

        element.classList.add("comment");
        element.dataset.commentId = comment.id;

        const baseUrl = commentsContainer.dataset.baseUrl;

        element.dataset.url =
            `${baseUrl}${comment.id}/`;

        const username = document.createElement("p");
        const strong = document.createElement("strong");

        strong.classList.add("comment-username");
        strong.textContent = comment.username;

        username.appendChild(strong);

        const content = document.createElement("p");
        content.classList.add("comment-content");
        content.textContent = comment.content;

        const editButton = document.createElement("button");
        editButton.type = "button";
        editButton.classList.add("edit-comment-button");
        editButton.textContent = "Редактировать";

        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.classList.add("delete-comment-button");
        deleteButton.textContent = "Удалить";

        const editBlock = document.createElement("div");
        editBlock.classList.add("comment-edit");
        editBlock.hidden = true;

        const textarea = document.createElement("textarea");
        textarea.value = comment.content;

        const saveButton = document.createElement("button");
        saveButton.type = "button";
        saveButton.classList.add("save-comment-button");
        saveButton.textContent = "Сохранить";

        const cancelButton = document.createElement("button");
        cancelButton.type = "button";
        cancelButton.classList.add("cancel-comment-button");
        cancelButton.textContent = "Отмена";

        editBlock.append(
            textarea,
            saveButton,
            cancelButton
        );

        element.append(
            username,
            content,
            editButton,
            deleteButton,
            editBlock
        );

        return element;
    }
});