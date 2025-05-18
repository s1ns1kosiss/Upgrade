//make a order
document.getElementById('makeOrder').addEventListener('click', () => {
    const products = JSON.parse(localStorage.getItem('cart')) || [];
    fetch('/create_order/', { //here create order 
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': '{{ csrf_token }}'
      },
      body: JSON.stringify({ products })
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        localStorage.removeItem('cart');
        window.location.href = '/customerData';
      } else {
        alert('Error al crear la orden. Inténtalo de nuevo.');
      }
    });
  });