/* Names Unlimited — shared generator UI logic
   Each page includes a <div data-generator> block configured via
   data-* attributes. This script wires up the controls, runs the
   generator, and renders the ledger output. */

(function () {
  function initGenerator(root) {
    const mode = root.dataset.mode || "names"; // "names" | "username"
    const state = {
      type: root.dataset.defaultType || "full",
      gender: root.dataset.defaultGender || "both",
      count: parseInt(root.dataset.defaultCount || "50", 10),
      results: []
    };

    const typeButtons = root.querySelectorAll("[data-type]");
    const genderButtons = root.querySelectorAll("[data-gender]");
    const countInput = root.querySelector("[data-count-input]");
    const countChips = root.querySelectorAll("[data-count-chip]");
    const generateBtn = root.querySelector("[data-generate]");
    const list = root.querySelector("[data-name-list]");
    const countLabel = root.querySelector("[data-entry-count]");
    const searchBox = root.querySelector("[data-search]");
    const copyBtn = root.querySelector("[data-copy]");
    const downloadBtn = root.querySelector("[data-download]");
    const emptyState = root.querySelector("[data-empty]");

    function setActive(buttons, val, dataAttr) {
      buttons.forEach((b) => {
        b.classList.toggle("is-on", b.dataset[dataAttr] === val);
      });
    }

    typeButtons.forEach((b) =>
      b.addEventListener("click", () => {
        state.type = b.dataset.type;
        setActive(typeButtons, state.type, "type");
      })
    );
    genderButtons.forEach((b) =>
      b.addEventListener("click", () => {
        state.gender = b.dataset.gender;
        setActive(genderButtons, state.gender, "gender");
      })
    );
    countChips.forEach((b) =>
      b.addEventListener("click", () => {
        state.count = parseInt(b.dataset.countChip, 10);
        if (countInput) countInput.value = state.count;
      })
    );
    if (countInput) {
      countInput.addEventListener("input", () => {
        const v = parseInt(countInput.value, 10);
        state.count = isNaN(v) ? 0 : Math.max(1, Math.min(5000, v));
      });
    }

    function render(items) {
      if (!items.length) {
        list.innerHTML = "";
        if (emptyState) emptyState.style.display = "flex";
        return;
      }
      if (emptyState) emptyState.style.display = "none";
      list.innerHTML = items
        .map(
          (n, i) =>
            `<li><span class="no">${String(i + 1).padStart(3, "0")}</span><span class="nm">${escapeHtml(n)}</span></li>`
        )
        .join("");
    }

    function escapeHtml(str) {
      const d = document.createElement("div");
      d.textContent = str;
      return d.innerHTML;
    }

    function updateCountLabel() {
      if (countLabel) countLabel.innerHTML = `<b>${state.results.length}</b> ${mode === "username" ? "usernames" : "names"} generated`;
    }

    if (generateBtn) {
      generateBtn.addEventListener("click", () => {
        const n = Math.max(1, Math.min(5000, state.count || 50));
        state.results =
          mode === "username"
            ? generateUsernameList(n)
            : generateNameList({ type: state.type, gender: state.gender, count: n });
        render(state.results);
        updateCountLabel();
        if (searchBox) searchBox.value = "";
      });
    }

    if (searchBox) {
      searchBox.addEventListener("input", () => {
        const q = searchBox.value.trim().toLowerCase();
        const filtered = q ? state.results.filter((n) => n.toLowerCase().includes(q)) : state.results;
        render(filtered);
      });
    }

    if (copyBtn) {
      copyBtn.addEventListener("click", async () => {
        if (!state.results.length) return;
        try {
          await navigator.clipboard.writeText(state.results.join("\n"));
          const old = copyBtn.textContent;
          copyBtn.textContent = "Copied ✓";
          setTimeout(() => (copyBtn.textContent = old), 1400);
        } catch (e) {
          alert("Couldn't copy automatically — select and copy the list manually.");
        }
      });
    }

    if (downloadBtn) {
      downloadBtn.addEventListener("click", () => {
        if (!state.results.length) return;
        const header = mode === "username" ? "username" : "name";
        const csv = [header, ...state.results].join("\n");
        const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${(root.dataset.filename || "names")}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      });
    }

    // reflect initial defaults on the buttons
    setActive(typeButtons, state.type, "type");
    setActive(genderButtons, state.gender, "gender");
  }

  function initMobileNav() {
    const toggle = document.querySelector("[data-nav-toggle]");
    const nav = document.querySelector("[data-nav-tabs]");
    if (!toggle || !nav) return;
    toggle.addEventListener("click", () => nav.classList.toggle("is-open"));
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-generator]").forEach(initGenerator);
    initMobileNav();
  });
})();
