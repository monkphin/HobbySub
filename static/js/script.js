document.addEventListener('DOMContentLoaded', function () {
   // Carousel
  const carouselElems = document.querySelectorAll('.carousel');
  M.Carousel.init(carouselElems, {
    duration: 200,
    dist: -30,
    shift: 0,
    padding: 20
  });

  // Modals
  const modalElems = document.querySelectorAll('.modal');
  M.Modal.init(modalElems);

  // Datepicker
  const dateElems = document.querySelectorAll('.datepicker');
  M.Datepicker.init(dateElems, {
    format: 'dd/mm/yyyy'
  });

  // Dropdowns
  const dropdownElems = document.querySelectorAll('.dropdown-trigger');
  M.Dropdown.init(dropdownElems);

  // Materialize Selects
  M.FormSelect.init(document.querySelectorAll('select'));

  // Update floating labels
  M.updateTextFields();

  // Toasts
  const toasts = document.querySelectorAll('.toast');
  toasts.forEach((toast) => {
    toast.addEventListener("click", () => toast.remove());
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(-10px)";
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  });

  // File input filename fix
  const fileInputs = document.querySelectorAll('.file-field input[type="file"]');
  fileInputs.forEach(fileInput => {
    fileInput.addEventListener('change', function () {
      const filePathInput = fileInput.closest('.file-field').querySelector('.file-path');
      if (filePathInput && fileInput.files.length > 0) {
        filePathInput.value = Array.from(fileInput.files).map(f => f.name).join(', ');
        filePathInput.dispatchEvent(new Event('change'));  // trigger Materialize label update
      }
    });
  });
});
