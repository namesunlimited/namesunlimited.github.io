/* Mobile menu toggle for the shared site header (see tools/apply_shell.py). */
(function () {
  "use strict";
  var toggle = document.querySelector("[data-nav-toggle]");
  var nav = document.querySelector("[data-nav-tabs]");
  if (!toggle || !nav) return;
  toggle.addEventListener("click", function () {
    var open = nav.classList.toggle("is-open");
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && nav.classList.contains("is-open")) {
      nav.classList.remove("is-open");
      toggle.setAttribute("aria-expanded", "false");
      toggle.focus();
    }
  });
})();
