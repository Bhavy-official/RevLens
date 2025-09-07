(function () {
    const root = document.documentElement;
    const key = 'theme';
    const stored = localStorage.getItem(key);
    if (stored === 'dark' || (!stored && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        root.classList.add('dark');
    }
    function toggle() {
        root.classList.toggle('dark');
        localStorage.setItem(key, root.classList.contains('dark') ? 'dark' : 'light');
    }
    document.querySelectorAll('.theme-toggle').forEach(btn => btn.addEventListener('click', toggle));
    document.getElementById('year').textContent = String(new Date().getFullYear());

    const carousel = document.getElementById('carousel');
    if (carousel) {
        let idx = 0; const step = () => {
            const cards = carousel.children; if (!cards.length) return;
            idx = (idx + 1) % cards.length;
            const card = cards[idx];
            carousel.scrollTo({ left: card.offsetLeft - 16, behavior: 'smooth' });
        };
        const id = setInterval(step, 3500);
        carousel.addEventListener('mouseenter', () => clearInterval(id), { once: true });
    }
})();