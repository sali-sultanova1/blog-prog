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
        searchStatus.textContent = "Загрузка...";

        try {
            const response = await fetch(url);

            if (!response.ok) {
                throw new Error("Не удалось загрузить статьи.");
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

        if (articles.length === 0) {
            const message = document.createElement("p");
            message.textContent = "По вашему запросу статьи не найдены.";
            resultsContainer.appendChild(message);
            return;
        }

        for (const article of articles) {
            resultsContainer.appendChild(createArticleElement(article));
        }
    }

    function createArticleElement(article) {
        const articleElement = document.createElement("article");
        const articleUrl = articleUrlTemplate.replace("__slug__", encodeURIComponent(article.slug));

        if (article.cover_image) {
            const image = document.createElement("img");
            image.src = article.cover_image;
            image.alt = article.title;
            image.style.maxWidth = "400px";
            articleElement.appendChild(image);
        }

        const title = document.createElement("h2");
        const titleLink = document.createElement("a");

        titleLink.href = articleUrl;
        titleLink.textContent = article.title;
        title.appendChild(titleLink);
        articleElement.appendChild(title);

        const authorParagraph = document.createElement("p");
        authorParagraph.append("Автор: ");

        if (isAuthenticated) {
            const authorLink = document.createElement("a");

            authorLink.href = authorUrlTemplate.replace(
                "__username__",
                encodeURIComponent(article.author)
            );

            authorLink.textContent = article.author;
            authorParagraph.appendChild(authorLink);
        } else {
            authorParagraph.append(article.author);
        }

        articleElement.appendChild(authorParagraph);

        const publishedParagraph = document.createElement("p");

        if (article.published_at) {
            const publishedDate = new Date(article.published_at);
            publishedParagraph.textContent = `Опубликовано: ${publishedDate.toLocaleString("ru-RU")}`;
        }

        articleElement.appendChild(publishedParagraph);

        const stats = document.createElement("p");
        stats.textContent = `Лайков: ${article.likes_count ?? 0} · Комментариев: ${article.comments_count ?? 0}`;
        articleElement.appendChild(stats);

        const summary = document.createElement("p");
        summary.textContent = article.summary;
        articleElement.appendChild(summary);

        const categories = document.createElement("p");
        const categoriesTitle = document.createElement("strong");

        categoriesTitle.textContent = "Категории: ";
        categories.appendChild(categoriesTitle);
        categories.append(article.category_names.length ? article.category_names.join(", ") : "Не указаны");
        articleElement.appendChild(categories);

        const tags = document.createElement("p");
        const tagsTitle = document.createElement("strong");

        tagsTitle.textContent = "Теги: ";
        tags.appendChild(tagsTitle);
        tags.append(article.tag_names.length ? article.tag_names.join(", ") : "Не указаны");
        articleElement.appendChild(tags);

        const readParagraph = document.createElement("p");
        const readLink = document.createElement("a");

        readLink.href = articleUrl;
        readLink.textContent = "Читать статью";
        readParagraph.appendChild(readLink);
        articleElement.appendChild(readParagraph);

        return articleElement;
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