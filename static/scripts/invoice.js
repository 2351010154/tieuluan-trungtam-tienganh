

const enrollment_id_param = new URLSearchParams(window.location.search).get('enrollment_id');


async function get_access_token() {
    try {
        const response = await fetch('/api/get-paypal-token');
        const json_response = await response.json();
        if (json_response['error']) {
            console.log("error getting token:", json_response['error']);
            return;
        }
        return json_response['access_token'];
    } catch (error) {
        console.log("Error fetching access token:", error);
        return null;
    }
}

const amount = document.getElementById('total-amount').getAttribute('data-price');
const paypalButtons = window.paypal.Buttons({
    style: {
        shape: "rect",
        layout: "vertical",
        color: "silver",
        label: "paypal",
    },

    async createOrder() {
        const token = await get_access_token();
        if (!token) {
            alert("error getting access token");
            return;
        }

        console.log("amount to pay:", amount);
        let order_data_json = {
            'intent': 'CAPTURE',
            'purchase_units': [{
                'amount': {
                    'currency_code': 'USD',
                    'value': '100.00'
                }
            }]
        }

        const body = JSON.stringify(order_data_json);

        response = await fetch('https://api-m.sandbox.paypal.com/v2/checkout/orders', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
                'PayPal-Request-Id': crypto.randomUUID()
            },
            body: body
        });

        const data = await response.json();
        console.log("order created:", data);
        return data.id;
    },

    async onApprove(data, actions) {
        const token = await get_access_token();
        if (!token) {
            alert("error getting access token");
            return;
        }

        const orderID = data.orderID;
        console.log("order ID:", orderID);

        try {
            response = await fetch(`https://api-m.sandbox.paypal.com/v2/checkout/orders/${orderID}/capture`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                }
            })

            const orderData = await response.json();
            const orderError = orderData?.details?.[0];

            console.log("capture response:", orderData);
            console.log("order error:", orderError);

            if (orderError?.issue === 'INSTRUMENT_DECLINED') {
                return actions.restart();
            } else if (orderError) {
                throw new Error(`${orderError.description} (${orderError.debug_id})`);
            } else {

                try {
                    const user = await get_user_info();
                    const receipt_json = await create_receipt(user.id, enrollment_id_param, amount);
                    const confirm_receipt_json = await confirm_receipt(receipt_json['receipt_id']);

                    const send_receipt_email_json = await sendReceiptEmail(user.id);

                    alert('Thanh toán thành công!');

                } catch (err) {
                    console.log("error processing receipt:", err);
                }

            }
        } catch (err) {
            console.log(err);
        }
    }
})
paypalButtons.render('#paypal-button-container');

async function sendReceiptEmail(user_id) {
    try {
        let html = await createReceiptHtml(enrollment_id_param);
        console.log("receipt html:", html);
        const response = await fetch('/api/send-receipt', {
            method: 'POST',
            body: JSON.stringify({
                'user_id': user_id,
                'table_html': html
            }),
            headers: {
                'Content-Type': 'application/json',
            }
        });
        const json_response = await response.json();
        if (json_response['error']) {
            console.log("error sending receipt email:", json_response['error']);
            return;
        }
        console.log("receipt email sent:", json_response);
        return json_response;
    } catch (err) {
        console.log("error:", err);
    }
}

async function createReceiptHtml(enrollment_id) {
    const response = await fetch(`/api/enrollment/${enrollment_id}`);
    const enrollment = await response.json();

    let row = await createReceiptRow(enrollment);
    let html = `
        <table class=table>
            <thead class="table-dark">
            <tr>
                <th scope="col">Mã</th>
                <th scope="col">Tên khoá học</th>
                <th scope="col">Cấp độ</th>
                <th scope="col">Lớp</th>
                <th scope="col">Giá</th>
                <th scope="col"></th>
            </tr>
            </thead>

            <tbody>
                ${row.outerHTML}
            </tbody>
        </table>
    `
    return html
}

async function createReceiptRow(enrollment) {
    const row = createRow(enrollment, 0);
    return row;
}

async function confirm_receipt(receipt_id) {
    try {
        response = await fetch(`/api/receipts/${receipt_id}/status`, {
            method: 'PUT',
            body: JSON.stringify({
                'status': 'PAID'
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const json_response = await response.json();
        if (json_response['error']) {
            console.log("error confirming receipt:", json_response['error']);
            return;
        }
        console.log("receipt confirmed:", json_response);
        return json_response;
    } catch (err) {
        console.log("error:", err);
    }

}

async function create_receipt(user_id ,enrollment_id, price) {
    try {
        const response = await fetch('/api/invoice',{
            method: 'POST',
            body: JSON.stringify({
                'user_id': user_id,
                'enrollment_ids': [enrollment_id],
                'prices': [price]
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
        const json_response = await response.json();
        if (json_response['error']) {
            console.log("error creating receipt:", json_response['error']);
            return;
        }
        console.log("receipt created:", json_response);
        return json_response;
    } catch (err) {
        console.log("error:", err);
        return null;
    }
}


async function get_user_info() {
    try {
        const response = await fetch('/api/user');
        const json_response = await response.json();
        if (json_response['error']) {
            console.log("error getting user:", json_response['error']);
            return;
        }
        return json_response;
    } catch (error) {
        console.log("error:", error);
        return null;
    }
}