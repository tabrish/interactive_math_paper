window.onload = () => {
  const popup = document.createElement("div");
  popup.className = "popup";
  document.body.appendChild(popup);

  // Add interactivity to all anchor tags
  document.querySelectorAll("a").forEach((link) => {
    link.addEventListener("mouseenter", function () {
      const href = this.getAttribute("href");

      if (href && href.startsWith("#")) {
        const targetId = href.substring(1);
        const targetEl = document.getElementById(targetId);

        if (targetEl) {
          popup.innerHTML = targetEl.innerHTML;
          showPopup(this);

          // Optional: process MathJax
          if (window.MathJax && window.MathJax.typesetPromise) {
            MathJax.typesetPromise([popup]).catch((err) => {
              console.log("MathJax error in popup:", err);
            });
          }
        }
      }
    });

    link.addEventListener("mouseleave", function () {
      popup.style.display = "none";
    });
  });

  function showPopup(element) {
    popup.style.display = "block";

    const rect = element.getBoundingClientRect();
    popup.style.left = rect.left + window.scrollX + "px";
    popup.style.top = rect.bottom + window.scrollY + 2 + "px";

    const popupRect = popup.getBoundingClientRect();
    if (popupRect.right > window.innerWidth) {
      popup.style.left =
        window.innerWidth - popupRect.width - 10 + window.scrollX + "px";
    }
    if (popupRect.bottom > window.innerHeight) {
      popup.style.top = rect.top + window.scrollY - popupRect.height - 2 + "px";
    }
  }

  // Hide popup when clicking outside
  document.addEventListener("click", function (e) {
    if (!popup.contains(e.target)) {
      popup.style.display = "none";
    }
  });
};
