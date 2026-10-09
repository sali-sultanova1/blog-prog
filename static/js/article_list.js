document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("article-filter-form");
    const searchInput = document.getElementById("q");
    const categorySelect = document.getElementById("category");
    const tagSelect = document.getElementById("tag");
    const resetLink = document.getElementById("reset-filters");
    const resultsContainer = document.getElementById("article-results");
    const searchStatus = document.getElementById("search-status");
    const pagination = document.getElementById("api-pagination");
    const previousButton = document.getElementById("previous-page");
    const nextButton = document.getElementById("next-page");
    const pageNumber = document.getElementById("page-number");

    if (!form || !resultsContainer) {
        return;
    }

    const apiUrl = resultsContainer.dataset.apiUrl;
    const articleUrlTemplate = resultsContainer.dataset.articleUrl;
    const authorUrlTemplate = resultsContainer.dataset.authorUrl;
    const isAuthenticated = resultsContainer.dataset.authenticated === "true";

    let currentPage = 1;
    let searchTimer = null;

    async function loadArticles(page = 1) {
        currentPage = page;

        const url = new URL(apiUrl, window.location.origin);
        const query = searchInput.value.trim();
        const category = categorySelect.value;
        const tag = tagSelect.value;

        if (query) {
            url.searchParams.set("search", query);
        }

        if (category) {
            url.searchParams.set("category", category);
        }

        if (tag) {
            url.searchParams.set("tag", tag);
        }

        url.searchParams.set("page", currentPage);

        searchStatus.textContent = "Загрузка…";

        try {
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error("Articles request failed");
            }

            const data = await response.json();

            renderArticles(data.results);
            renderPagination(data);

            searchStatus.textContent = `Найдено: ${data.count}`;

            updateBrowserUrl(query, category, tag);
        } catch (error) {
            searchStatus.textContent = "Не удалось загрузить статьи.";
        }
    }

    function renderArticles(articles) {
        resultsContainer.replaceChildren();

        if (!articles.length) {
            const empty = document.createElement("div");
            empty.className = "empty-state";

            const title = document.createElement("h2");
            title.textContent = "Ничего не найдено";

            const text = document.createElement("p");
            text.textContent = "Попробуйте изменить запрос или выбрать другие фильтры.";

            empty.append(title, text);
            resultsContainer.appendChild(empty);
            return;
        }

        articles.forEach((article, index) => {
            resultsContainer.appendChild(createArticleElement(article, index));
        });
    }

    function createArticleElement(article, index) {
        const element = document.createElement("article");

        element.className = "story-card";

        if (index === 0) {
            element.classList.add("story-card--feature");
        }

        const articleUrl = articleUrlTemplate.replace(
            "__slug__",
            encodeURIComponent(article.slug)
        );

        const media = document.createElement("a");
        media.className = "story-media";
        media.href = articleUrl;

        if (article.cover_image) {
            const image = document.createElement("img");
            image.src = article.cover_image;
            image.alt = article.title;
            media.appendChild(image);
        } else {
            const placeholder = document.createElement("div");
            placeholder.className = "story-placeholder";
            placeholder.textContent = "N";
            media.appendChild(placeholder);
        }

        const body = document.createElement("div");
        body.className = "story-body";

        const topline = document.createElement("div");
        topline.className = "story-topline";

        const category = document.createElement("span");
        category.className = "category-chip";
        category.textContent = article.category_names?.[0] || "История";
        topline.appendChild(category);

        const title = document.createElement("h2");
        title.className = "story-title";

        const titleLink = document.createElement("a");
        titleLink.href = articleUrl;
        titleLink.textContent = article.title;

        title.appendChild(titleLink);

        body.append(topline, title);

        if (article.summary) {
            const summary = document.createElement("p");
            summary.className = "story-summary";
            summary.textContent = article.summary;
            body.appendChild(summary);
        }

        if (article.tag_names?.length) {
            const tags = document.createElement("div");
            tags.className = "story-tags";

            article.tag_names.forEach((name) => {
                const tag = document.createElement("span");
                tag.className = "tag-chip";
                tag.textContent = `#${name}`;
                tags.appendChild(tag);
            });

            body.appendChild(tags);
        }

        const meta = document.createElement("div");
        meta.className = "story-meta";

        const author = document.createElement("span");
        author.append("Автор: ");

        if (isAuthenticated) {
            const authorLink = document.createElement("a");

            authorLink.href = authorUrlTemplate.replace(
                "__username__",
                encodeURIComponent(article.author)
            );

            authorLink.textContent = article.author;
            author.appendChild(authorLink);
        } else {
            author.append(article.author);
        }

        const date = document.createElement("span");

        if (article.published_at) {
            date.textContent = new Date(article.published_at)
                .toLocaleDateString("ru-RU");
        }

        const likes = document.createElement("span");
        likes.className = "story-stat";
        likes.textContent = `♥ ${article.likes_count ?? 0}`;

        const comments = document.createElement("span");
        comments.className = "story-stat";
        comments.textContent = `◌ ${article.comments_count ?? 0}`;

        meta.append(author, date, likes, comments);

        body.appendChild(meta);

        element.append(media, body);

        return element;
    }

    function renderPagination(data) {
        const hasPrevious = Boolean(data.previous);
        const hasNext = Boolean(data.next);

        if (!hasPrevious && !hasNext && currentPage === 1) {
            pagination.hidden = true;
            return;
        }

        pagination.hidden = false;

        previousButton.disabled = !hasPrevious;
        nextButton.disabled = !hasNext;

        pageNumber.textContent = `Страница ${currentPage}`;
    }

    function updateBrowserUrl(query, category, tag) {
        const url = new URL(window.location.href);

        url.search = "";

        if (query) {
            url.searchParams.set("q", query);
        }

        if (category) {
            url.searchParams.set("category", category);
        }

        if (tag) {
            url.searchParams.set("tag", tag);
        }

        window.history.replaceState({}, "", url);
    }

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        loadArticles(1);
    });

    searchInput.addEventListener("input", () => {
        clearTimeout(searchTimer);

        searchTimer = setTimeout(() => {
            loadArticles(1);
        }, 300);
    });

    categorySelect.addEventListener("change", () => {
        loadArticles(1);
    });

    tagSelect.addEventListener("change", () => {
        loadArticles(1);
    });

    resetLink.addEventListener("click", (event) => {
        event.preventDefault();

        searchInput.value = "";
        categorySelect.value = "";
        tagSelect.value = "";

        loadArticles(1);
    });

    previousButton.addEventListener("click", () => {
        if (currentPage > 1) {
            loadArticles(currentPage - 1);
        }
    });

    nextButton.addEventListener("click", () => {
        loadArticles(currentPage + 1);
    });

    loadArticles();
});