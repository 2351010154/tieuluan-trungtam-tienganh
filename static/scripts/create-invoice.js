const invoice_id_submit = document.getElementById('invoice-id-submit');
const invoice_total = document.getElementById('invoice-total');
const invoice_content = document.getElementById('invoice-table-content');

const invoice_err = document.getElementById('invoice-err');

const url = new URL(window.location.href);
const user_id_param = url.searchParams.get("user_id");
const receipt_id_param = url.searchParams.get("receipt_id");

let total = 0;
courses_cached = [];

if (user_id_param) {
    invoice_id_submit.value = user_id_param;
    loadPendingEnrollment(user_id_param);
}

invoice_id_submit.addEventListener('keyup', async function(event) {
    invoice_err.classList.remove("show");
    invoice_total.textContent = "";
    if (event.key === 'Enter') {
        total = 0;
        user_id = invoice_id_submit.value;
        await loadEnrollmentForUser(user_id);
    }
})


async function loadPendingEnrollment(user_id) {
    response = await fetch(`/api/enrollments/${user_id}?receipt_id=${receipt_id_param}&status=Pending`);
    enrollment_json = await response.json();
    loadEnrollmentTable(enrollment_json);
}

async function loadEnrollmentForUser(user_id) {
    response = await fetch(`/api/enrollments/${user_id}?no_receipt=true`);
    if (!response.ok) {
        alert('Mã số sinh viên không hợp lệ');
        return;
    }
    enrollment_json = await response.json();
    loadEnrollmentTable(enrollment_json);
}

async function loadEnrollmentTable(enrollment_json) {
    invoice_content.innerHTML = "";
    total = 0;

    if (enrollment_json.length === 0) {
        invoice_content.innerHTML = `
                    <tr>
                        <td colspan="6" class="text-center">Chưa có khoá học nào được thêm</td>
                    </tr>
        `;
        return;
    }

    i = 0;
    for (const enrollment of enrollment_json) {
        row = createRow(enrollment,i)
        invoice_content.appendChild(row);
        console.log(`adding price: ${enrollment['course_price']}`);
        updateInvoiceTotal(enrollment['course_price']);
        i++;
    }


}

function updateInvoiceTotal(amount) {
    total += amount ? amount : 0;
    formattedTotal = total.toLocaleString();
    invoice_total.textContent = formattedTotal;
}

function createRow(enrollment, idx) {
    let row = document.createElement('tr');
    row.setAttribute('data-receipt-id', enrollment['receipt_id']);

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

    let deleteCell = document.createElement('td');

    if (!user_id_param) {
        deleteCell.innerHTML = `
            <button class="delete-course-btn" onclick="deleteCourse(this); updateInvoiceTotal();">
                <i class="bi bi-trash fs-5"></i>
            </button>
        `;

    }

    row.appendChild(idCell);
    row.appendChild(courseNameCell);
    row.appendChild(levelCell);
    row.appendChild(classCell);
    row.appendChild(priceCell);
    row.appendChild(deleteCell);

    return row
}

async function deleteCourse(button) {
    row = button.closest('tr');
    user_id = invoice_id_submit.value;
    class_id = row.children[3].getAttribute('data-class-id');
    course_price = row.children[4].getAttribute('data-price');
    try {
        const response = await fetch(`/api/enrollment/${user_id}/${class_id}`,{
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        const data = await response.json();
        if (data['error']) {
            console.log('error: ', data['error']);
            return;
        }
        row.remove();
        console.log(`removing price: ${course_price}`);
        updateInvoiceTotal(-course_price);
    } catch (error) {
        console.log('error: ', error);
        return;
    }
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
            send_receipt_response = await sendReceiptEmail(invoice_id_submit.value, table_html);
            if (!send_receipt_response.ok) {
                console.log('error sending receipt email');
                return;
            }
            send_receipt_data = send_receipt_response.json();
            if (send_receipt_data['error']) {
                console.log('error:', send_receipt_data['error']);
                return;
            }


            alert('Thanh toán hoá đơn thành công');
            window.close();
        } else {
            alert('error paying invoice');
        }
    })
}

async function sendReceiptEmail(user_id, receipt_html) {
    try {
      const response = await fetch('/api/send-receipt',{
            method: 'POST',
            body: JSON.stringify({
                'user_id': user_id,
                'table_html': receipt_html,
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        });
        return response;
    } catch(err) {
        console.log('error sending receipt: ', err);
    }
}

const add_course_btn = document.getElementById('invoice-add-course');
const confirm_add_course_btn = document.getElementById('add-courses-confirm-btn');
const course_select = document.getElementById('courses-select');

if (add_course_btn) {
    add_course_btn.addEventListener('click', async function() {
        if (courses_cached.length === 0) {
            const response = await fetch('/api/courses');
            const courses_json = await response.json();
            if (courses_json.length === 0) {
            alert('Không có khoá học nào để thêm');
            }

            courses_cached = courses_json;
        }

        loadModalCourses(courses_cached);
    });
}


async function loadModalCourses(courses) {
    if (course_select.options.length === 0) {
        for (const c of courses) {
        classes = await getClassesForCourse(c['id']);
            for (const cls of classes) {
                const option = document.createElement('option');
                option.value = c['id'];

                option.textContent = `${c['name']} - ${cls['name']}`;
                option.setAttribute('data-class-id', cls['id']);
                course_select.appendChild(option);
            }
        }
    }
}

async function getClassesForCourse(course_id) {
    response = await fetch(`/api/courses/${course_id}/classes`)
    if (!response.ok) {
        alert('error getting classes ');
        return;
    }
    classes_json = await response.json();

    return classes_json;
}


confirm_add_course_btn.addEventListener('click', async function() {
    const selectedCourses = course_select.selectedOptions;
    user_id = invoice_id_submit.value;

    if (await addCourseToUser(user_id, selectedCourses)) {
        await loadEnrollmentForUser(user_id);
        addCourseModalReset(selectedCourses);
    }
});

function addCourseModalReset() {
    course_select.selectedIndex = -1;
    course_select.value = null;
    for (const option of course_select) {
        option.selected = false;
    }

    $(course_select).val(null).trigger('change.select2');


    add_courses_modal = bootstrap.Modal.getInstance(document.getElementById('add-courses-to-user-modal'));
    add_courses_modal.hide();
}

async function addCourseToUser(user_id, selectedCourses) {
    const selectedArray = Array.from(selectedCourses);
    class_ids = selectedArray.map(option => option.getAttribute('data-class-id'))
    console.log(class_ids);
    if (user_id === "") {
        alert('Vui lòng nhập mã số sinh viên trước khi thêm khoá học');
        return false;
    }

    if (selectedCourses.length === 0) {
        alert('Vui lòng chọn ít nhất một khoá học để thêm');
        return false;
    }

    const response = await fetch('/api/enrollments', {
        method: 'POST',
        body: JSON.stringify({
            'user_id': user_id,
            'class_ids': class_ids
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    })

    if (!response.ok) {
        alert('error add course to user');
        return false;
    }
    data = await response.json();
    if (data['error']) {
        alert(data['error']);
        return false;
    }
    return true;
}