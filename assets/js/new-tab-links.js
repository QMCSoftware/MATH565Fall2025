document.addEventListener("DOMContentLoaded", () => {
  const isPdf = (url) => {
    try {
      const u = new URL(url, window.location.href);
      return u.pathname.toLowerCase().endsWith(".pdf");
    } catch {
      return false;
    }
  };

  document.querySelectorAll("a[href]").forEach((link) => {
    const href = link.getAttribute("href");

    // Skip in-page anchors, javascript:, mailto:, tel:
    if (
      href.startsWith("#") ||
      href.startsWith("javascript:") ||
      href.startsWith("mailto:") ||
      href.startsWith("tel:")
    ) return;

    let url;
    try {
      url = new URL(href, window.location.href);
    } catch {
      return;
    }

    const isExternal = url.hostname !== window.location.hostname;

    // Open external links or PDFs in a new tab
    if (isExternal || isPdf(href)) {
      link.setAttribute("target", "_blank");
      link.setAttribute("rel", "noopener noreferrer");

      // Append icon for external links only
      if (isExternal) {
        const icon = document.createElement("span");
        icon.textContent = " ↗";
        icon.style.fontSize = "0.85em";
        icon.style.color = "inherit";
        icon.style.marginLeft = "0.15em";
        link.appendChild(icon);
      }
    }
  });
});