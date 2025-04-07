document.addEventListener('DOMContentLoaded', function() {
    const elems = document.querySelectorAll('.carousel');
    M.Carousel.init(elems, {
      fullWidth: true,
      indicators: true
    });
  });