const invoice_id_submit = document.getElementById('invoice-id-submit');
const invoice_total = document.getElementById('invoice-total');
const invoice_content = document.getElementById('invoice-table-content');

const invoice_err = document.getElementById('invoice-err');

invoice_id_submit.addEventListener('keyup', async function(event) {
    invoice_err.classList.remove("show");
    invoice_total.textContent = "";
    if (event.key === 'Enter') {
        user_id = invoice_id_submit.value;

        response = await fetch(`/api/enrollment/${user_id}?no_receipt=true`);
        if (!response.ok) {
            alert('Mã số sinh viên không hợp lệ');
            return;
        }
        enrollment_json = await response.json();

        invoice_content.innerHTML = "";

        if (enrollment_json.length === 0) {
            invoice_content.innerHTML = `
                        <tr>
                            <td colspan="5" class="text-center">Chưa có khoá học nào được thêm</td>
                        </tr>
            `;
            return;
        }

        i = 0;
        for (const enrollment of enrollment_json) {
            row = createRow(enrollment,i)
            invoice_content.appendChild(row);
            i++;
        }

        total = enrollment_json.reduce((total, enrollment) => total + enrollment['course_price'], 0).toLocaleString();
        invoice_total.textContent = total;

    }
})

function createRow(enrollment, idx) {
    row = document.createElement('tr');
    idCell = document.createElement('td');
    idCell.textContent = idx + 1;
    courseNameCell = document.createElement('td');
    courseNameCell.textContent = enrollment['course_name'];

    courseNameCell.setAttribute('data-enrollment-id', enrollment['id']);

    levelCell = document.createElement('td');
    levelCell.textContent = enrollment['course_level'];
    classCell = document.createElement('td');
    classCell.textContent = enrollment['class_name'];
    priceCell = document.createElement('td');
    priceCell.textContent = enrollment['course_price'].toLocaleString();

    priceCell.setAttribute('data-price', enrollment['course_price']);

    row.appendChild(idCell);
    row.appendChild(courseNameCell);
    row.appendChild(levelCell);
    row.appendChild(classCell);
    row.appendChild(priceCell);
    return row
}

invoice_create = document.getElementById('invoice-create');
invoice_create.addEventListener('click', async function() {
    user_id = invoice_id_submit.value;

    enrollment_ids = [];
    prices = []

    rows = invoice_content.getElementsByTagName('tr');

    for (const row of rows) {
        try {
            enrollment_id = row.children[1].getAttribute('data-enrollment-id');
        } catch (error) {
            invoice_err.classList.add("show");
            invoice_err.textContent = "Không có khoá học để tạo hoá đơn.";
            return;
        }


        price = row.children[4].getAttribute('data-price');
        enrollment_ids.push(enrollment_id);
        prices.push(price);
    }



    const response = await fetch('/api/invoice', {
        method: 'POST',
        body: JSON.stringify({
            'user_id': user_id,
            'enrollment_ids': enrollment_ids,
            'prices': prices
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    })

    if (response.ok) {
        const result = await response.json();
        if (result['error']) {
         alert(result['error']);
         return;
        }
        alert('Tạo hóa đơn thành công');
    } else {
        console.log('error creating invoice')
    }
})