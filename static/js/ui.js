(() => {
    "use strict";

    const notice = document.getElementById("ui-notice");
    const dialog = document.getElementById("confirm-dialog");
    let noticeTimer;
    let confirmationPending = false;

    function notify(message) {
        if (!notice) return;

        clearTimeout(noticeTimer);
        notice.textContent = message;
        notice.hidden = false;

        noticeTimer = setTimeout(() => {
            notice.hidden = true;
        }, 7000);
    }

    function confirmAction(message) {
        if (!dialog || typeof dialog.showModal !== "function") {
            return Promise.resolve(window.confirm(message));
        }

        if (confirmationPending) return Promise.resolve(false);
        confirmationPending = true;

        return new Promise((resolve) => {
            const previousFocus = document.activeElement;

            document.getElementById("confirm-description").textContent = message;
            dialog.returnValue = "cancel";

            dialog.addEventListener("close", () => {
                confirmationPending = false;
                previousFocus?.focus();
                resolve(dialog.returnValue === "confirm");
            }, { once: true });

            dialog.showModal();
        });
    }

    window.NewsUI = { notify, confirm: confirmAction };

    /* Mobile navigation */

    const menu = document.getElementById("site-menu");
    const mobile = window.matchMedia("(max-width: 960px)");

    function syncMenu() {
        if (menu) menu.open = !mobile.matches;
    }

    syncMenu();
    mobile.addEventListener("change", syncMenu);

    document.addEventListener("keydown", (event) => {
        if (event.key === "Escape" && mobile.matches && menu?.open) {
            menu.open = false;
            menu.querySelector("summary").focus();
        }
    });

    document.addEventListener("click", (event) => {
        if (
            mobile.matches &&
            menu?.open &&
            !menu.contains(event.target)
        ) {
            menu.open = false;
        }
    });

    /* Filter dropdowns.
       Original selects remain the source of values for article_list.js. */

    const syncSelects = [];

    document.querySelectorAll(".filter-panel select").forEach((select, index) => {
        const label = document.querySelector(`label[for="${select.id}"]`);
        const details = document.createElement("details");
        details.className = "custom-select";

        const summary = document.createElement("summary");
        const value = document.createElement("span");
        value.className = "custom-select__value";
        value.id = `filter-value-${index}`;
        summary.append(value);

        const options = document.createElement("div");
        options.className = "custom-select__options";
        options.id = `filter-options-${index}`;
        options.setAttribute("role", "listbox");
        options.setAttribute("aria-label", label?.textContent.trim() || "Фильтр");

        summary.setAttribute("aria-controls", options.id);
        summary.setAttribute("aria-haspopup", "listbox");

        if (label) {
            label.id ||= `filter-label-${index}`;
            label.removeAttribute("for");
            summary.setAttribute("aria-labelledby", `${label.id} ${value.id}`);
        }

        const buttons = Array.from(select.options).map((option) => {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "custom-select__option";
            button.textContent = option.textContent.trim();
            button.dataset.value = option.value;
            button.disabled = option.disabled;
            button.setAttribute("role", "option");

            button.addEventListener("click", () => {
                select.value = option.value;
                sync();
                details.open = false;
                summary.focus();
                select.dispatchEvent(new Event("change", { bubbles: true }));
            });

            options.append(button);
            return button;
        });

        function sync() {
            value.textContent = select.selectedOptions[0]?.textContent.trim() || "Выбрать";

            buttons.forEach((button) => {
                const selected = button.dataset.value === select.value;
                button.setAttribute("aria-selected", String(selected));
                button.tabIndex = selected ? 0 : -1;
            });
        }

        function focusSelected() {
            const selected = buttons.find(
                (button) => button.dataset.value === select.value && !button.disabled
            );
            (selected || buttons.find((button) => !button.disabled))?.focus();
        }

        details.addEventListener("toggle", () => {
            summary.setAttribute("aria-expanded", String(details.open));

            if (details.open) {
                document.querySelectorAll(".custom-select[open]").forEach((other) => {
                    if (other !== details) other.open = false;
                });
                focusSelected();
            }
        });

        summary.addEventListener("keydown", (event) => {
            if (event.key === "ArrowDown" || event.key === "ArrowUp") {
                event.preventDefault();
                details.open = true;
                focusSelected();
            }
        });

        options.addEventListener("keydown", (event) => {
            const available = buttons.filter((button) => !button.disabled);
            const current = available.indexOf(document.activeElement);
            let next;

            if (event.key === "ArrowDown") next = (current + 1) % available.length;
            if (event.key === "ArrowUp") next = (current - 1 + available.length) % available.length;
            if (event.key === "Home") next = 0;
            if (event.key === "End") next = available.length - 1;

            if (next !== undefined && available.length) {
                event.preventDefault();
                available[next].focus();
            }

            if (event.key === "Escape") {
                event.preventDefault();
                details.open = false;
                summary.focus();
            }
        });

        details.addEventListener("focusout", () => {
            setTimeout(() => {
                if (!details.contains(document.activeElement)) details.open = false;
            }, 0);
        });

        document.addEventListener("click", (event) => {
            if (!details.contains(event.target)) details.open = false;
        });

        details.append(summary, options);
        select.insertAdjacentElement("afterend", details);
        select.hidden = true;
        select.addEventListener("change", sync);

        summary.setAttribute("aria-expanded", "false");
        syncSelects.push(sync);
        sync();
    });

    document.getElementById("reset-filters")?.addEventListener("click", () => {
        setTimeout(() => syncSelects.forEach((sync) => sync()), 0);
    });

    /* Regular POST forms. API forms have their own handlers. */

    document.querySelectorAll("form[method='post']").forEach((form) => {
        if (form.dataset.url) return;

        let approved = false;
        let submitting = false;

        form.addEventListener("submit", async (event) => {
            if (event.defaultPrevented) return;

            if (submitting) {
                event.preventDefault();
                return;
            }

            if (form.dataset.confirm && !approved) {
                event.preventDefault();

                if (await confirmAction(form.dataset.confirm)) {
                    approved = true;
                    if (event.submitter) {
                        form.requestSubmit(event.submitter);
                    } else {
                        form.requestSubmit();
                    }
                }

                return;
            }

            approved = false;
            submitting = true;
            form.setAttribute("aria-busy", "true");

            /* Delay disabling until the browser has collected form values. */
            setTimeout(() => {
                const button = event.submitter;
                if (!button) return;

                button.dataset.originalLabel = button.textContent;
                button.disabled = true;
                button.textContent = "Отправка…";
            }, 0);
        });

        window.addEventListener("pageshow", () => {
            submitting = false;
            approved = false;
            form.removeAttribute("aria-busy");

            form.querySelectorAll("[data-original-label]").forEach((button) => {
                button.textContent = button.dataset.originalLabel;
                button.disabled = false;
                delete button.dataset.originalLabel;
            });
        });
    });

    /* Make server-side form errors easy to find. */

    const firstInvalid = document.querySelector(
        ".field--error input:not([type='hidden']), .field--error textarea"
    );

    if (firstInvalid) firstInvalid.focus();
})();