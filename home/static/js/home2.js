
    // --- Theme toggle ---
    const btn = document.getElementById("theme-toggle");
    const themeIcon = document.getElementById("theme-icon");

    function getPreferredTheme() {
        const saved = localStorage.getItem("theme");
        if (saved) return saved;
        return window.matchMedia("(prefers-color-scheme: dark)").matches
            ? "dark"
            : "light";
    }

    function setTheme(next) {
        document.documentElement.setAttribute("data-theme", next);
        localStorage.setItem("theme", next);
        if (themeIcon) {
            themeIcon.textContent = next === "dark" ? "🌙" : "☀";
            btn.setAttribute("aria-pressed", next === "dark");
            btn.setAttribute("aria-label", `Switch to ${ next === "dark" ? "light" : "dark"} mode`);
    }
}

  if (btn) {
    setTheme(getPreferredTheme());
    btn.addEventListener("click", () => {
        const current = document.documentElement.getAttribute("data-theme") || "light";
        setTheme(current === "dark" ? "light" : "dark");
    });
}

// --- Mobile nav toggle ---
const navToggle = document.querySelector(".nav-toggle");
const nav = document.querySelector(".nav");
if (navToggle && nav) {
    navToggle.setAttribute("aria-expanded", "false");
    navToggle.addEventListener("click", () => {
        const isOpen = nav.classList.toggle("open");
        navToggle.setAttribute("aria-expanded", isOpen);
    });

    document.addEventListener("click", (e) => {
        if (nav.classList.contains("open") && !nav.contains(e.target) && !navToggle.contains(e.target)) {
            nav.classList.remove("open");
            navToggle.setAttribute("aria-expanded", "false");
        }
    });
}

// --- Hero fade-in ---
const heroCopy = document.querySelector(".hero-copy");
if (heroCopy) heroCopy.classList.add("fade-in");