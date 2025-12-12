
document.addEventListener('DOMContentLoaded', function() {

    const btnSaveRules = document.getElementById('btnSaveRules');
    if (btnSaveRules) {

        btnSaveRules.addEventListener('click', function() {
            const maxStudentInput = document.getElementById('maxStudent');
            const maxStudent = maxStudentInput.value;

            if (maxStudent <= 0) {
                Swal.fire('Lỗi', 'Sĩ số phải lớn hơn 0!', 'error');
                return;
            }

            const originalText = btnSaveRules.innerHTML;
            btnSaveRules.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-2"></i>Đang lưu...';
            btnSaveRules.disabled = true;

            let payload = {
                'max_students': maxStudent
            };

            const feeInputs = document.querySelectorAll('.tuition-input');
            feeInputs.forEach(input => {
                const key = input.getAttribute('data-level');
                const value = input.value;
                payload[key] = value;
            });

            fetch('/api/rules', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                if (data.msg === 'success') {
                    Swal.fire({
                        icon: 'success',
                        title: 'Thành công',
                        text: 'Đã cập nhật quy định!',
                        showConfirmButton: false,
                        timer: 1500
                    });
                } else {
                    Swal.fire('Lỗi', 'Không thể lưu quy định.', 'error');
                }
            })
            .catch(err => {
                console.error(err);
                Swal.fire('Lỗi', 'Lỗi kết nối server!', 'error');
            })
            .finally(() => {
                btnSaveRules.innerHTML = originalText;
                btnSaveRules.disabled = false;
            });
        });
    }
});