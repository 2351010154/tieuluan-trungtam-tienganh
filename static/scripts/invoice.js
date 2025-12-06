const invoice_id_submit = document.getElementById('invoice-id-submit');
const invoice_total = document.getElementById('invoice-total');
const invoice_content = document.getElementById('invoice-table-content');

const invoice_err = document.getElementById('invoice-err');

const url = new URL(window.location.href);
const user_id_param = url.searchParams.get("user_id");
const receipt_id_param = url.searchParams.get("receipt_id");

if (user_id_param) {
    invoice_id_submit.value = user_id_param;
    loadPendingEnrollment(user_id_param);
}

invoice_id_submit.addEventListener('keyup', async function(event) {
    invoice_err.classList.remove("show");
    invoice_total.textContent = "";
    if (event.key === 'Enter') {
        user_id = invoice_id_submit.value;
        await loadEnrollmentForUser(user_id);
    }
})


async function loadPendingEnrollment(user_id) {
    response = await fetch(`/api/enrollment/${user_id}?receipt_id=${receipt_id_param}&status=Pending`);
    enrollment_json = await response.json();
    loadEnrollmentTable(enrollment_json);
}

async function loadEnrollmentForUser(user_id) {
    response = await fetch(`/api/enrollment/${user_id}?no_receipt=true`);
    if (!response.ok) {
        alert('Mã số sinh viên không hợp lệ');
        return;
    }
    enrollment_json = await response.json();
    loadEnrollmentTable(enrollment_json);
}

async function loadEnrollmentTable(enrollment_json) {
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

function createRow(enrollment, idx) {
    row = document.createElement('tr');
    row.setAttribute('data-receipt-id', enrollment['receipt_id']);

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

const invoice_create = document.getElementById('invoice-create');
if (invoice_create) {
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
}

const pay_btn = document.getElementById('invoice-pay-btn');
if (pay_btn) {
    pay_btn.addEventListener('click', async function() {
        rows = invoice_content.getElementsByTagName('tr');

        receipt_id = rows[0].getAttribute('data-receipt-id');

        const response = await fetch(`/api/receipts/${receipt_id}/status`, {
            method: 'PUT',
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

            const table_html = document.getElementById('invoice-table').outerHTML;
            send_receipt_response = await fetch('/api/send-receipt',{
                method: 'POST',
                body: JSON.stringify({
                    'user_id': invoice_id_submit.value,
                    'table_html': table_html,
                }),
                headers: {
                    'Content-Type': 'application/json'
                }
            })

            if (!send_receipt_response.ok) {
                console.log('error sending receipt email');
                return;
            }

            alert('Thanh toán hóa đơn thành công');
        } else {
            alert('error paying invoice');
        }
    })
}