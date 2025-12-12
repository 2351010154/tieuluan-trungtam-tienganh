pay_btns = document.querySelectorAll('.receipt-details-btn');
console.log(pay_btns);
pay_btns.forEach((button) => {
    button.addEventListener('click', async function() {
        currentRow = button.closest('tr');
        user_id = currentRow.getAttribute('data-user-id');
        receipt_id = currentRow.getAttribute('data-receipt-id');
        window.open(`/create-invoice?user_id=${user_id}&receipt_id=${receipt_id}`, '_blank');
    })
})