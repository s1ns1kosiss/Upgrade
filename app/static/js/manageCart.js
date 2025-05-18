document.addEventListener('DOMContentLoaded', () => {
  const buyButton = document.getElementById('buy-button');

  if (buyButton) {
  buyButton.addEventListener('click', (event) => {
      if (buyButton.hasAttribute('disabled')) {
          event.preventDefault(); 
      } else {
          window.location.href = buyButton.getAttribute('href');
      }
  });
  }
});

document.addEventListener('DOMContentLoaded', function () {
  var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.forEach(function (tooltipTriggerEl) {
    new bootstrap.Tooltip(tooltipTriggerEl);
  });
  // Microinteracción bounce en botón de pago
  document.querySelectorAll('.bounce-hover').forEach(btn => {
    btn.addEventListener('mouseenter', function() {
      btn.classList.add('animate__animated', 'animate__bounce');
    });
    btn.addEventListener('mouseleave', function() {
      btn.classList.remove('animate__animated', 'animate__bounce');
    });
    btn.addEventListener('click', function() {
      btn.classList.add('animate__animated', 'animate__bounce');
      setTimeout(() => btn.classList.remove('animate__animated', 'animate__bounce'), 700);
    });
  });
});