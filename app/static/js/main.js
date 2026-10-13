/**
 * AcademiaPro - Client-Side Interactive Script
 */

document.addEventListener("DOMContentLoaded", function () {
    console.log("[+] AcademiaPro Client UI Initialized.");

    // 1. Table Search Utility
    const searchInputs = document.querySelectorAll(".table-search-input");
    searchInputs.forEach((input) => {
        input.addEventListener("keyup", function () {
            const targetTableId = this.getAttribute("data-target");
            const filterValue = this.value.toLowerCase();
            const table = document.getElementById(targetTableId);
            if (!table) return;

            const rows = table.querySelectorAll("tbody tr");
            rows.forEach((row) => {
                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(filterValue) ? "" : "none";
            });
        });
    });

    // 2. Tab state in URL hash
    const hash = window.location.hash;
    if (hash) {
        const triggerTab = document.querySelector(`button[data-bs-target="${hash}"]`);
        if (triggerTab) {
            const tabInstance = new bootstrap.Tab(triggerTab);
            tabInstance.show();
        }
    }

    const tabButtons = document.querySelectorAll('button[data-bs-toggle="tab"]');
    tabButtons.forEach((tab) => {
        tab.addEventListener("shown.bs.tab", function (e) {
            const target = e.target.getAttribute("data-bs-target");
            if (target) {
                history.replaceState(null, null, target);
            }
        });
    });
});
