/* ─── DATA ─── */
    const DATA = {
        total:      {{ total }},
        fake:       {{ fake }},
        genuine:    {{ genuine }},
        positive:   {{ positive }},
        negative:   {{ negative }},
        confidence: {{ avg_confidence|default:0 }},
    };

    /* ─── ANIMATED COUNTERS ─── */
    function animateCount(el, target, duration, suffix) {
        duration = duration || 1200; suffix = suffix || '';
        const start = performance.now();
        const run = (now) => {
            const p    = Math.min((now - start) / duration, 1);
            const ease = 1 - Math.pow(1 - p, 3);
            el.textContent = Math.round(ease * target).toLocaleString() + suffix;
            if (p < 1) requestAnimationFrame(run);
        };
        requestAnimationFrame(run);
    }
    document.querySelectorAll('[data-count]').forEach(el =>
        animateCount(el, parseInt(el.dataset.count) || 0, 1200, '')
    );
    animateCount(document.getElementById('confNum'), DATA.confidence, 1400, '%');

    /* ─── ALL BAR ANIMATIONS ─── */
    window.addEventListener('load', () => {
        /* Stat card bars */
        document.querySelectorAll('.card-bar-fill').forEach(bar => {
            const key = bar.dataset.rel;
            const pct = bar.dataset.pct
                ? parseFloat(bar.dataset.pct)
                : DATA.total > 0 ? (DATA[key] / DATA.total) * 100 : 0;
            setTimeout(() => bar.style.width = pct + '%', 300);
        });
        /* Per-review confidence bars — staggered */
        document.querySelectorAll('.conf-bar-fill[data-w]').forEach((el, i) => {
            setTimeout(() => { el.style.width = el.dataset.w + '%'; }, 200 + i * 50);
        });
    });

    /* ─── CHART DEFAULTS ─── */
    Chart.defaults.color       = 'rgba(232,230,240,0.4)';
    Chart.defaults.font.family = "'DM Sans', sans-serif";
    Chart.defaults.font.size   = 11;
    Chart.defaults.font.weight = '400';
    const tip = {
        backgroundColor:'#09090f', borderColor:'rgba(255,255,255,0.09)', borderWidth:1,
        titleColor:'#e8e6f0', bodyColor:'rgba(232,230,240,0.55)',
        padding:12, cornerRadius:10,
        titleFont:{ family:"'DM Sans',sans-serif", size:12, weight:'500' },
        bodyFont: { family:"'DM Sans',sans-serif", size:11 },
    };

    /* Fake vs Genuine */
    new Chart(document.getElementById('fakeChart'), {
        type:'doughnut',
        data:{ labels:['Fake','Genuine'], datasets:[{
            data:[DATA.fake, DATA.genuine],
            backgroundColor:['rgba(192,132,252,.8)','rgba(74,222,128,.8)'],
            borderColor:    ['rgba(192,132,252,1)', 'rgba(74,222,128,1)'],
            borderWidth:2, hoverOffset:10,
        }]},
        options:{
            cutout:'68%',
            animation:{ animateRotate:true, duration:1000, easing:'easeOutQuart' },
            plugins:{
                legend:{ position:'bottom', labels:{ padding:18, usePointStyle:true, pointStyleWidth:10, color:'rgba(232,230,240,0.55)' } },
                tooltip:{ ...tip }
            }
        }
    });

    /* Sentiment */
    new Chart(document.getElementById('sentimentChart'), {
        type:'bar',
        data:{ labels:['Positive','Negative'], datasets:[{
            label:'Reviews',
            data:[DATA.positive, DATA.negative],
            backgroundColor:['rgba(124,92,219,.75)','rgba(248,113,113,.75)'],
            borderColor:    ['rgba(124,92,219,1)',   'rgba(248,113,113,1)'],
            borderWidth:2, borderRadius:8, borderSkipped:false,
        }]},
        options:{
            animation:{ duration:1000, easing:'easeOutQuart', delay: ctx => ctx.dataIndex*120 },
            scales:{
                x:{ grid:{color:'rgba(255,255,255,.04)'}, ticks:{color:'rgba(232,230,240,0.35)'}, border:{color:'rgba(255,255,255,0.06)'} },
                y:{ grid:{color:'rgba(255,255,255,.04)'}, ticks:{color:'rgba(232,230,240,0.35)'}, border:{color:'rgba(255,255,255,0.06)'}, beginAtZero:true }
            },
            plugins:{ legend:{display:false}, tooltip:{...tip} }
        }
    });

    /* Avg Confidence */
    new Chart(document.getElementById('confidenceChart'), {
        type:'doughnut',
        data:{ labels:['Confidence','Remaining'], datasets:[{
            data:[DATA.confidence, 100 - DATA.confidence],
            backgroundColor:['rgba(124,92,219,.9)','rgba(255,255,255,0.05)'],
            borderColor:    ['rgba(124,92,219,1)',  'rgba(255,255,255,0.04)'],
            borderWidth:2, hoverOffset:6,
        }]},
        options:{
            cutout:'72%',
            animation:{ animateRotate:true, duration:1200, easing:'easeOutQuart' },
            plugins:{ legend:{display:false}, tooltip:{...tip} }
        }
    });

    /* ─── FILTER PILLS ─── */
    document.querySelectorAll('.pill').forEach(pill => {
        pill.addEventListener('click', function () {
            document.querySelectorAll('.pill').forEach(p => p.classList.remove('active'));
            this.classList.add('active');
            const f = this.dataset.filter;
            document.querySelectorAll('.review-row').forEach(row => {
                const verdict = row.dataset.verdict;
                const conf    = parseFloat(row.dataset.conf);
                let show = true;
                if      (f === 'genuine') show = verdict === 'genuine';
                else if (f === 'fake')    show = verdict === 'fake';
                else if (f === 'high')    show = conf >= 80;
                else if (f === 'low')     show = conf < 50;
                row.style.display = show ? '' : 'none';
            });
        });
    });