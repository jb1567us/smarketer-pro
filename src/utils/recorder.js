/**
 * recorder.js
 * Captures click and change events and sends them to Python via window.recordEvent binding.
 */
(function () {
    console.log("Recorder started.");

    function getSelector(el) {
        if (el.id) return `#${el.id}`;
        if (el.name) return `[name="${el.name}"]`;

        let path = [];
        while (el && el.nodeType === Node.ELEMENT_NODE) {
            let selector = el.nodeName.toLowerCase();
            if (el.className) {
                selector += "." + Array.from(el.classList).join(".");
            }
            path.unshift(selector);
            el = el.parentNode;
        }
        return path.join(" > ");
    }

    function getElementData(el, e) {
        return {
            selector: getSelector(el),
            tagName: el.tagName,
            id: el.id,
            name: el.name,
            type: el.type,
            className: el.className,
            innerText: el.innerText ? el.innerText.substring(0, 50).trim() : null,
            placeholder: el.placeholder || null,
            value: el.value || null,
            ariaLabel: el.getAttribute('aria-label') || null,
            x: e ? e.pageX : null,
            y: e ? e.pageY : null,
            timestamp: Date.now()
        };
    }

    document.addEventListener('click', (e) => {
        const eventData = {
            type: 'click',
            ...getElementData(e.target, e)
        };
        console.log("Captured click:", eventData);
        if (window.recordEvent) {
            window.recordEvent(JSON.stringify(eventData));
        }
    }, true);

    document.addEventListener('change', (e) => {
        const eventData = {
            type: 'change',
            ...getElementData(e.target, e)
        };
        console.log("Captured change:", eventData);
        if (window.recordEvent) {
            window.recordEvent(JSON.stringify(eventData));
        }
    }, true);
})();
