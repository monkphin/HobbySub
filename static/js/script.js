document.addEventListener('DOMContentLoaded', function() {
  const elems = document.querySelectorAll('.carousel');
  M.Carousel.init(elems, {
    duration: 200,
    dist: -30,
    shift: 0,
    padding: 20
  });
});
  document.addEventListener('DOMContentLoaded', function() {
    var modals = document.querySelectorAll('.modal');
    M.Modal.init(modals);
  });

  document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.datepicker');
    M.Datepicker.init(elems, {
      format: 'dd/mm/yyyy'
    });
  });

  document.addEventListener('DOMContentLoaded', function() {
    const elems = document.querySelectorAll('.dropdown-trigger');
    M.Dropdown.init(elems);
  });

  document.addEventListener("DOMContentLoaded", function() {
    const toasts = document.querySelectorAll(".toast");
    toasts.forEach((toast) => {
      // Click to dismiss
      toast.addEventListener("click", () => toast.remove());

      // Auto dismiss after 4 seconds
      setTimeout(() => {
        toast.style.opacity = "0";
        toast.style.transform = "translateY(-10px)";
        setTimeout(() => toast.remove(), 300);
      }, 4000);
    });
  });