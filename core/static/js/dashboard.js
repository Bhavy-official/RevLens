document.addEventListener('DOMContentLoaded', () => {
    // Theme toggle
    const themeBtn = document.getElementById('theme-toggle');
    themeBtn.addEventListener('click', () => {
        document.body.classList.toggle('dark');
    });

    // ApexCharts Area
    const chartAreaEl = document.getElementById('chart0');
    if(chartAreaEl) {
        new ApexCharts(chartAreaEl, {
            chart: { type: 'area', height: 300, toolbar: { show: false } },
            dataLabels: { enabled: false },
            stroke: { curve: 'smooth', width: 2 },
            series: [
                { name: 'Positive', data: [30,40,35,50,49,60,70,91,125,150,160,180] },
                { name: 'Negative', data: [10,20,25,15,18,14,10,25,30,12,20,15] }
            ],
            xaxis: { categories: ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"] },
            colors: ["#10B981","#EF4444"]
        }).render();
    }

    // ApexCharts Donut
    const chartDonutEl = document.getElementById('chart1');
    if(chartDonutEl) {
        new ApexCharts(chartDonutEl, {
            chart: { type: 'donut', height: 260, toolbar: { show: false } },
            series: [65,25,10],
            labels: ['Positive','Neutral','Negative'],
            colors: ["#10B981","#6B7280","#EF4444"]
        }).render();
    }
});