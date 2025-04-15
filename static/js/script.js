document.addEventListener('DOMContentLoaded', function() {
    const elems = document.querySelectorAll('.carousel');
    M.Carousel.init(elems, {
      fullWidth: true,
      indicators: true
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