;
(function () {
    // Wait for logic to be defined if async (it's not, but safe)
    if (window.scrapeSaatchi) {
        window.scrapeSaatchi(window.artworkLinks);
    } else {
        console.error("Scraper logic not found");
    }
})();
