document.addEventListener('DOMContentLoaded', function () {
    let count = 1;

    const btnincrease = document.getElementById('increase');
    const btndecrement = document.getElementById('decrement');
    const amount = document.getElementById('amount');

    btnincrease.addEventListener('click', () => {
        if (count < 50){
            count++
        }
        amount.innerHTML = `<strong>${count}</strong>`;
    });

    btndecrement.addEventListener('click', () => {
        if (count > 1) {
            count--;
            amount.innerHTML = `<strong>${count}</strong>`;
        }
    });
});