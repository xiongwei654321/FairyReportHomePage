// ═══ 汉堡菜单 ═══
(function () {
    var burger = document.getElementById('navBurger');
    var mobile = document.getElementById('navMobile');
    if (burger && mobile) {
        burger.addEventListener('click', function () {
            mobile.classList.toggle('open');
        });
    }
})();

// ═══ 优势卡片 Tooltip ═══
(function () {
    var showTimer = null;
    var hideTimer = null;
    var activeCard = null;
    var touchStartX = 0;
    var touchStartY = 0;
    var touchMoved = false;
    var pendingCard = null;

    function ensureTip() {
        var el = document.getElementById('__adv_float_tip__');
        if (el) return el;
        el = document.createElement('div');
        el.id = '__adv_float_tip__';
        el.style.cssText = [
            'position:fixed',
            'z-index:99999',
            'background:#1c2128',
            'color:#cdd9e5',
            'border-radius:10px',
            'padding:16px 18px',
            'width:300px',
            'max-width:calc(100vw - 32px)',
            'box-shadow:0 8px 32px rgba(0,0,0,0.4),0 0 0 1px rgba(255,255,255,0.07)',
            'font-size:13px',
            'line-height:1.7',
            'pointer-events:none',
            'font-family:system-ui,-apple-system,sans-serif',
            'opacity:0',
            'transform:translateY(-6px)',
            'transition:opacity 0.16s ease,transform 0.16s ease'
        ].join(';');
        document.body.appendChild(el);
        return el;
    }

    function positionTip(el, card) {
        var rect = card.getBoundingClientRect();
        var pw = window.innerWidth;
        var ph = window.innerHeight;
        var w = 300;
        var left = rect.left + rect.width / 2 - w / 2;
        var top = rect.bottom + 10;
        if (left + w > pw - 16) left = pw - w - 16;
        if (left < 16) left = 16;
        var h = el.offsetHeight;
        if (top + h > ph - 16) top = rect.top - h - 10;
        el.style.left = left + 'px';
        el.style.top = top + 'px';
    }

    function showTip(card) {
        clearTimeout(hideTimer);
        showTimer = setTimeout(function () {
            var el = ensureTip();
            var icon = card.getAttribute('data-tip-icon') || '';
            var title = card.getAttribute('data-tip-title') || '';
            var content = card.getAttribute('data-tip') || '';
            el.innerHTML =
                '<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">' +
                    '<span style="font-size:15px;line-height:1">' + icon + '</span>' +
                    '<span style="font-size:13px;font-weight:600;color:#e6edf3">' + title + '</span>' +
                '</div>' +
                '<div style="height:1px;background:rgba(255,255,255,0.07);margin-bottom:10px"></div>' +
                '<div style="color:#8b949e;line-height:1.75">' + content + '</div>';
            positionTip(el, card);
            requestAnimationFrame(function () {
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            });
        }, 120);
    }

    function hideTip() {
        clearTimeout(showTimer);
        hideTimer = setTimeout(function () {
            var el = document.getElementById('__adv_float_tip__');
            if (el) {
                el.style.opacity = '0';
                el.style.transform = 'translateY(-6px)';
            }
        }, 0);
    }

    function hideTipImmediate() {
        clearTimeout(showTimer);
        clearTimeout(hideTimer);
        var el = document.getElementById('__adv_float_tip__');
        if (el) {
            el.style.opacity = '0';
            el.style.transform = 'translateY(-6px)';
        }
        activeCard = null;
    }

    document.querySelectorAll('.adv-card-has-tip').forEach(function (card) {
        // Desktop: mouse hover
        card.addEventListener('mouseenter', function () { showTip(card); });
        card.addEventListener('mouseleave', hideTip);

        // Mobile: track touch start position
        card.addEventListener('touchstart', function (e) {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
            touchMoved = false;
            pendingCard = card;
        }, { passive: true });

        // Scrolling cancels tooltip
        card.addEventListener('touchmove', function (e) {
            var dx = e.touches[0].clientX - touchStartX;
            var dy = e.touches[0].clientY - touchStartY;
            if (Math.abs(dx) > 8 || Math.abs(dy) > 8) {
                touchMoved = true;
                hideTipImmediate();
            }
        }, { passive: true });

        // Tap toggles tooltip
        card.addEventListener('touchend', function () {
            if (!touchMoved && pendingCard === card) {
                if (activeCard === card) {
                    hideTipImmediate();
                } else {
                    hideTipImmediate();
                    activeCard = card;
                    showTip(card);
                }
            }
            pendingCard = null;
        });
    });

    // Close tooltip on scroll
    window.addEventListener('scroll', hideTipImmediate, { passive: true });

    // Close tooltip when tapping outside
    document.addEventListener('touchstart', function (e) {
        if (activeCard && !activeCard.contains(e.target)) {
            hideTipImmediate();
        }
    }, { passive: true });
})();

// ═══ Flash 消息自动隐藏 ═══
(function () {
    var flash = document.getElementById('flashMsg');
    if (flash) {
        setTimeout(function () {
            flash.style.opacity = '0';
            setTimeout(function () { flash.remove(); }, 300);
        }, 3000);
    }
})();
