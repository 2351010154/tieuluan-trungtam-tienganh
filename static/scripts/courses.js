const enroll_buttons = document.querySelectorAll('.course-enroll');
enroll_err_label = document.getElementById('enroll-error');

enroll_buttons.forEach((button) => {
    button.addEventListener("click", function() {
        enroll_err_label.classList.remove("show");
        enroll_err_label.textContent = "";

        courseInfoCard = button.closest('.course-info-card');
        course_id = courseInfoCard.dataset.courseId;

        title = document.getElementById('enroll-title');
        level = document.getElementById('enroll-level');

        try {
             classSelectLoader(course_id);
        } catch (error) {
            console.log('Error:', error);
        }

        level.disabled = false;

        fetch(`/api/courses/${course_id}`).then(response => response.json()).then(data => {
            title.textContent = data['name'];
            level.value = data['level'];
            console.log(data);
        }).catch(error => {
            console.log('Error:', error);
        })
        level.disabled = true;

    })
})

const enrollSelect = document.getElementById('enroll-class-select')
const instructorLabel = document.getElementById('enroll-instructor');
async function classSelectLoader(course_id) {
    const response = await fetch(`/api/courses/${course_id}/classes`);
    if (response.ok) {
        classes = await response.json();

        enrollSelect.innerHTML = "";

        if (classes.length != 0) {
            if (classes[0]['instructor'] != null) {
                instructorLabel.value = classes[0]['instructor'];
            }
        }

        classes.forEach((classItem) => {
            option = document.createElement('option');

            option.value = classItem['id'];
            option.textContent = classItem['name'];
            option.setAttribute('data-instructor', classItem['instructor']);

            enrollSelect.appendChild(option);
        })
    } else {
        console.log('Get classes fail');
    }

}


function courseRegister(user_id, class_id) {
        return fetch('/api/courses/register', {
                method: 'POST',
                body: JSON.stringify({
                    'user_id': user_id,
                    'class_id': class_id,
                }),
                headers: {
                'Content-Type': 'application/json'}
                })
}

enrollSelect.addEventListener('change', function() {
    selectedOption = enrollSelect.options[enrollSelect.selectedIndex];
    instructorName = selectedOption.getAttribute('data-instructor');
    instructorLabel.value = instructorName;
})

registerBtn = document.getElementById('course-register')
registerBtn.addEventListener('click', async function() {
          const response = await fetch('/api/user');
          const user = await response.json();
          const user_id = user['id'];
          const class_id = parseInt(enrollSelect.value);

          const register_response = await courseRegister(user_id, class_id);



          if (register_response.ok) {
                const json_response = await register_response.json();

                if (json_response['error']) {
                    enroll_err_label.classList.add("show");
                    enroll_err_label.textContent = json_response['error'];
                    return;
                }
                let modal = bootstrap.Modal.getInstance(document.getElementById("modal"));
                modal.hide();
          } else {
                enroll_err_label.classList.add("show");
                enroll_err_label.textContent = "Đã đăng ký khoá học này trước đó.";
          }
    }
)

let debounceTimeOut = null;
function debounceSearch() {
    var searchForm = document.getElementById('search-form');

    if (debounceTimeOut != null) {
        clearTimeout(debounceTimeOut);
    }
    debounceTimeOut = setTimeout(() => {
        searchForm.submit();
    },500);
}