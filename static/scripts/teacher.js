document.addEventListener('DOMContentLoaded', function() {
    const gradeRows = document.querySelectorAll('.grade-row');

    function updateRowCalculation(row) {
        const midterm = parseFloat(row.querySelector('.grade-midterm').value) || 0;
        const final = parseFloat(row.querySelector('.grade-final').value) || 0;
        const attendance = parseFloat(row.querySelector('.grade-attendance').value) || 0;

        const avg = (midterm + final + attendance) / 3;
        const avgCell = row.querySelector('td:nth-last-child(2)');
        avgCell.textContent = roundedAvg;

        if (avg >= 5) {
            avgCell.classList.remove('text-danger');
            avgCell.classList.add('text-primary');
        } else {
            avgCell.classList.remove('text-primary');
            avgCell.classList.add('text-danger');
        }

        const resultCell = row.querySelector('td:last-child');
        if (avg >= 5) {
            resultCell.innerHTML = `<span class="badge" style="background-color: #DCFCE7; color: #166534; padding: 6px 12px; border-radius: 6px;">ĐẠT</span>`;
        } else {
            resultCell.innerHTML = `<span class="badge" style="background-color: #FEF3C7; color: #92400E; padding: 6px 12px; border-radius: 6px;">RỚT</span>`;
        }
    }

    const btnSaveGrades = document.getElementById('btnSaveGrades');
    if (btnSaveGrades) {
        btnSaveGrades.addEventListener('click', async function() {
            const classId = document.getElementById('gradeClassSelect').value;
            const rows = document.querySelectorAll('.grade-row');

            let grades = [];
            rows.forEach(row => {
                const userId = row.getAttribute('data-user-id');
                const midterm = row.querySelector('.grade-midterm').value;
                const final = row.querySelector('.grade-final').value;
                const attendance = row.querySelector('.grade-attendance').value;

                grades.push({
                    user_id: userId,
                    midterm: midterm,
                    final: final,
                    attendance: attendance
                });
            });
            gradeRows.forEach(row => {
        const inputs = row.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                updateRowCalculation(row);
            });
        });
    });

            const originalText = btnSaveGrades.innerHTML;
            btnSaveGrades.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang lưu...';
            btnSaveGrades.disabled = true;

            try {
                const response = await fetch('/api/update-grades', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ class_id: classId, grades: grades })
                });

                const result = await response.json();

                if (result.msg === 'success') {
                    Swal.fire({
                        icon: 'success',
                        title: 'Thành công',
                        text: 'Đã cập nhật bảng điểm!',
                        timer: 1500,
                        showConfirmButton: false
                    }).then(() => window.location.reload());
                } else {
                    Swal.fire('Lỗi', 'Không thể lưu bảng điểm.', 'error');
                }
            } catch (error) {
                console.error(error);
                Swal.fire('Lỗi', 'Lỗi kết nối server.', 'error');
            } finally {
                btnSaveGrades.innerHTML = originalText;
                btnSaveGrades.disabled = false;
            }
        });
    }

    // --- PHẦN 2: XỬ LÝ LƯU ĐIỂM DANH ---
    const btnSaveAttendance = document.getElementById('btnSaveAttendance');
    if (btnSaveAttendance) {
        btnSaveAttendance.addEventListener('click', async function() {
            const classId = document.getElementById('attendClassSelect').value;
            const dateVal = document.getElementById('attendDate').value;
            const checkboxes = document.querySelectorAll('.attendance-checkbox');

            let students = [];
            checkboxes.forEach(cb => {
                students.push({
                    user_id: cb.getAttribute('data-user-id'),
                    is_present: cb.checked
                });
            });

            const originalText = btnSaveAttendance.innerHTML;
            btnSaveAttendance.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang lưu...';
            btnSaveAttendance.disabled = true;

            try {
                const response = await fetch('/api/save-attendance', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        class_id: classId,
                        date: dateVal,
                        students: students
                    })
                });

                const result = await response.json();

                if (result.msg === 'success') {
                    Swal.fire({
                        icon: 'success',
                        title: 'Thành công',
                        text: 'Đã lưu điểm danh!',
                        timer: 1500,
                        showConfirmButton: false
                    }).then(() => window.location.reload());
                } else {
                    Swal.fire('Lỗi', 'Không thể lưu điểm danh.', 'error');
                }
            } catch (error) {
                console.error(error);
                Swal.fire('Lỗi', 'Lỗi kết nối server.', 'error');
            } finally {
                btnSaveAttendance.innerHTML = originalText;
                btnSaveAttendance.disabled = false;
            }
        });
    }
});