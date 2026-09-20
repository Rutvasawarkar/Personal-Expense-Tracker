document.addEventListener("DOMContentLoaded", function () {

    /* =========================
       Elements
       ========================= */

    const chatForm = document.getElementById("chat-form");
    const chatButton = document.getElementById("chat-button");
    const messageInput = document.getElementById("message");

    const questionButtons = document.querySelectorAll(".question-item");

    const expenseForm = document.getElementById("expense-form");
    const dateInput = document.getElementById("date");

    const searchInput = document.getElementById("expense-search");
    const categoryFilter = document.getElementById("category-filter");

    const expenseRows = document.querySelectorAll(".expense-row");
    const visibleCount = document.getElementById("visible-count");
    const noFilterResults = document.getElementById("no-filter-results");


    /* =========================
       Set today's date
       ========================= */

    if (dateInput && !dateInput.value) {

        const today = new Date();

        const year = today.getFullYear();

        const month = String(
            today.getMonth() + 1
        ).padStart(2, "0");

        const day = String(
            today.getDate()
        ).padStart(2, "0");

        dateInput.value = `${year}-${month}-${day}`;
    }


    /* =========================
       Quick questions
       ========================= */

    questionButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            const question = button.dataset.question;

            if (messageInput) {

                messageInput.value = question;

                messageInput.focus();

                messageInput.classList.add("question-selected");

                setTimeout(function () {

                    messageInput.classList.remove(
                        "question-selected"
                    );

                }, 500);
            }

        });

    });


    /* =========================
       Agent button
       ========================= */

    if (chatForm && chatButton) {

        chatForm.addEventListener("submit", function () {

            if (messageInput.value.trim() === "") {
                return;
            }

            chatButton.disabled = true;

            chatButton.textContent = "Processing...";

        });

    }


    /* =========================
       Add expense button
       ========================= */

    if (expenseForm) {

        expenseForm.addEventListener("submit", function () {

            const submitButton =
                expenseForm.querySelector("button");

            if (submitButton) {

                submitButton.disabled = true;

                submitButton.textContent = "Saving...";

            }

        });

    }


    /* =========================
       Delete confirmation
       ========================= */

    const deleteForms =
        document.querySelectorAll(".delete-form");

    deleteForms.forEach(function (form) {

        form.addEventListener("submit", function (event) {

            const confirmed = window.confirm(
                "Are you sure you want to delete this transaction?"
            );

            if (!confirmed) {

                event.preventDefault();

            }

        });

    });


    /* =========================
       Expense table filtering
       ========================= */

    function filterExpenses() {

        if (!expenseRows.length) {
            return;
        }

        const searchTerm =
            searchInput.value.trim().toLowerCase();

        const selectedCategory =
            categoryFilter.value.toLowerCase();

        let matchedRows = 0;


        expenseRows.forEach(function (row) {

            const rowCategory =
                row.dataset.category;

            const rowText =
                row.textContent.toLowerCase();


            const matchesSearch =
                rowText.includes(searchTerm);

            const matchesCategory =
                selectedCategory === "all" ||
                rowCategory === selectedCategory;


            if (matchesSearch && matchesCategory) {

                row.style.display = "";

                matchedRows++;

            } else {

                row.style.display = "none";

            }

        });


        visibleCount.textContent = matchedRows;


        if (matchedRows === 0) {

            noFilterResults.style.display = "table-row";

        } else {

            noFilterResults.style.display = "none";

        }

    }


    if (searchInput) {

        searchInput.addEventListener(
            "input",
            filterExpenses
        );

    }


    if (categoryFilter) {

        categoryFilter.addEventListener(
            "change",
            filterExpenses
        );

    }


    /* =========================
       Initial filter state
       ========================= */

    if (noFilterResults) {

        noFilterResults.style.display = "none";

    }

});