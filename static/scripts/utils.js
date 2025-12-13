window.openPaymentWindow = function openPaymentWindow(enrollment_id) {
  window.open(`/invoice?enrollment_id=${enrollment_id}`, '_blank');
}

window.createRow = function(enrollment, idx) {
    let row = document.createElement('tr');
    if (enrollment['receipt_id']) {
        row.setAttribute('data-receipt-id', enrollment['receipt_id']);
    }

    let idCell = document.createElement('td');
    idCell.textContent = idx + 1;
    let courseNameCell = document.createElement('td');
    courseNameCell.textContent = enrollment['course_name'];

    courseNameCell.setAttribute('data-enrollment-id', enrollment['id']);

    let levelCell = document.createElement('td');
    levelCell.textContent = enrollment['course_level'];
    let classCell = document.createElement('td');
    classCell.textContent = enrollment['class_name'];

    classCell.setAttribute('data-class-id', enrollment['class_id']);

    let priceCell = document.createElement('td');
    priceCell.textContent = enrollment['course_price'].toLocaleString();

    priceCell.setAttribute('data-price', enrollment['course_price']);

    row.appendChild(idCell);
    row.appendChild(courseNameCell);
    row.appendChild(levelCell);
    row.appendChild(classCell);
    row.appendChild(priceCell);

    return row
}