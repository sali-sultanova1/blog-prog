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
    let activeController = null;
    let requestVersion = 0;

    searchStatus.setAttribute("role", "status");
    searchStatus.setAttribute("aria-live", "polite");

    async function loadArticles(page = 1) {
        clearTimeout(searchTimer);

        activeController?.abort();
        const controller = new AbortController();
        activeController = controller;

        const version = ++requestVersion;
        const requestedPage = page;

        const url = new URL(apiUrl, window.location.origin);
        const query = searchInput.value.trim();
        const category = categorySelect.value;
        const tag = tagSelect.value;

        if (query) url.searchParams.set("search", query);
        if (category) url.searchParams.set("category", category);
        if (tag) url.searchParams.set("tag", tag);

        url.searchParams.set("page", requestedPage);

        searchStatus.textContent = "Загрузка публикаций…";
        resultsContainer.setAttribute("aria-busy", "true");
        previousButton.disabled = true;
        nextButton.disabled = true;

        try {
            const response = await fetch(url, {
                signal: controller.signal,
                headers: { "Accept": "application/json" },
            });

            if (!response.ok) throw new Error("Request failed");

            const data = await response.json();

            if (!Array.isArray(data.results)) {
                throw new Error("Invalid response");
            }

            if (version !== requestVersion) return;

            currentPage = requestedPage;

            renderArticles(data.results);
            renderPagination(data);
            document.querySelector("[data-server-pagination]")?.setAttribute("hidden", "");

            searchStatus.textContent = `Найдено: ${data.count}`;

            updateBrowserUrl(query, category, tag);
        } catch (error) {
            if (error.name === "AbortError" || version !== requestVersion) return;

            searchStatus.textContent =
                "Не удалось обновить публикации. Показаны предыдущие результаты. Нажмите «Найти», чтобы повторить.";

            pagination.hidden = true;
        } finally {
            if (version === requestVersion) {
                resultsContainer.removeAttribute("aria-busy");
            }
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

        if (currentPage > 1) {
            url.searchParams.set("page", currentPage);
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

    const initialPage = Number(new URLSearchParams(window.location.search).get("page"));
    loadArticles(Number.isInteger(initialPage) && initialPage > 0 ? initialPage : 1);
});