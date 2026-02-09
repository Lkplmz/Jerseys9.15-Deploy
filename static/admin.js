document.addEventListener("DOMContentLoaded", () => {
  const navItems = document.querySelectorAll(".nav-item");
  const contentSections = document.querySelectorAll(".content-section");

  navItems.forEach((item) => {
    item.addEventListener("click", (e) => {
      e.preventDefault();

      contentSections.forEach((section) => {
        section.classList.remove("active");
      });

      navItems.forEach((nav) => {
        nav.classList.remove("active");
      });

      const targetId = item.getAttribute("data-content");

      const targetSection = document.getElementById(targetId);

      if (targetSection) {
        targetSection.classList.add("active");
        item.classList.add("active");
      }
    });
  });
});
