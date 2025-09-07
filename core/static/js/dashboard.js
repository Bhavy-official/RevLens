document.addEventListener("DOMContentLoaded", async () => {
    // 1️⃣ Theme Toggle
    const themeBtn = document.getElementById("theme-toggle");
    if (themeBtn) {
        themeBtn.addEventListener("click", () => {
            document.body.classList.toggle("dark");
        });
    }

    // 2️⃣ Prepare global chart references
    let areaChart = null;
    let donutChart = null;

    async function loadDashboardData(pid) {
    try {
        const res = await fetch(`/api/dashboard-data/${pid}/`);
        const data = await res.json();

        if (!res.ok) throw new Error(data.error || "Failed to load dashboard data");

        // Stats
        document.querySelector(".stats-cards .card:nth-child(1) .big-text").textContent =
            `+${((data.sentiment_counts.find(x => x.sentiment === "positive")?.count || 0) / data.total_reviews * 100).toFixed(1)}%`;
        document.querySelector(".stats-cards .card:nth-child(2) .big-text").textContent =
            `${data.avg_rating} / 5`;
        document.querySelector(".stats-cards .card:nth-child(3) .big-text").textContent =
            `${data.total_reviews}`;

        // Charts
        const labels = data.sentiment_counts.map(x => x.sentiment);
        const counts = data.sentiment_counts.map(x => x.count);

        if (areaChart) {
            areaChart.updateSeries([{ name: "Reviews", data: counts }]);
            areaChart.updateOptions({ xaxis: { categories: labels } });
        } else {
            areaChart = new ApexCharts(document.querySelector("#chart0"), {
                chart: { type: "area", height: 250 },
                dataLabels: { enabled: false },
                stroke: { curve: "smooth", width: 2 },
                series: [{ name: "Reviews", data: counts }],
                xaxis: { categories: labels },
                colors: ["#10B981", "#EF4444", "#6B7280"]
            });
            areaChart.render();
        }

        if (donutChart) {
            donutChart.updateSeries(counts);
            donutChart.updateOptions({ labels: labels });
        } else {
            donutChart = new ApexCharts(document.querySelector("#chart1"), {
                chart: { type: "donut", height: 250 },
                series: counts,
                labels: labels,
                colors: ["#10B981", "#6B7280", "#EF4444"]
            });
            donutChart.render();
        }

        // Recent reviews
        renderRecentReviews(data.recent_reviews);

    } catch (err) {
        console.error("Error loading dashboard data:", err);
    }
}


    // 3️⃣ Load product list & build sidebar
    const productList = document.getElementById("productList");
    try {
        const res = await fetch("/api/products/");
        const data = await res.json();

        if (data.products?.length) {
            data.products.forEach((p, idx) => {
                const btn = document.createElement("button");
                btn.className = "product-btn";
                btn.innerHTML = `
                    <div style="display:flex;flex-direction:column;align-items:flex-start;">
                        <span>${p.name}</span>
                        <small style="font-size:.75rem;color:#666;">${p.pid}</small>
                    </div>`;
                btn.addEventListener("click", () => {
                    document.querySelectorAll(".product-btn").forEach(b => b.classList.remove("active"));
                    btn.classList.add("active");
                    loadDashboardData(p.pid);
                });
                productList.insertBefore(btn, document.getElementById("openProductModal"));

                // Auto-select first product
                if (idx === 0) {
                    btn.classList.add("active");
                    loadDashboardData(p.pid);
                }
            });
        } else {
            console.warn("No products found.");
        }
    } catch (err) {
        console.error("Failed to fetch products:", err);
    }
});





function renderRecentReviews(reviews) {
    const tbody = document.getElementById("recent-reviews-body");
    tbody.innerHTML = "";

    if (!reviews || reviews.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center;">No reviews available</td></tr>`;
        return;
    }

    const rows = reviews.map(r => {
        const rating = parseInt(r.rating) || 0; // fallback if rating missing
        const stars = "⭐".repeat(rating) + "☆".repeat(5 - rating);

        const sentimentClass =
            r.sentiment === "positive" ? "positive" :
            r.sentiment === "negative" ? "negative" : "neutral";

        const text = r.text || "";
        const truncatedText = text.length > 120 ? text.substring(0, 120) + "..." : text;

        const dateStr = r.review_date || "-";

        return `
            <tr>
                <td>${dateStr}</td>
                <td>${r.reviewer || "Anonymous"}</td>
                <td>${stars}</td>
                <td>${truncatedText}</td>
                <td class="${sentimentClass}">${r.sentiment || "neutral"}</td>
            </tr>
        `;
    });

    tbody.innerHTML = rows.join(""); // render all at once
}
