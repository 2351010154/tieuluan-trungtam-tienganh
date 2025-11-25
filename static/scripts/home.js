 const hamburger = document.querySelector('#toggle-btn');

 hamburger.addEventListener("click",function() {
    document.querySelector("#sidebar").classList.toggle("expand");
 })

const enroll_buttons = document.querySelectorAll('.course-enroll');

enroll_buttons.forEach((button) => {
    button.addEventListener("click", function() {
        courseCard = button.closest('.course-info-card');
        course_id = courseCard.dataset.courseId;

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
function classSelectLoader(course_id) {
    fetch(`/api/courses/${course_id}/classes`).then(response => response.json())
    .then(classes => {

        //rset options
        enrollSelect.innerHTML = '';
        if (classes.length != 0) {
                if (classes[0]['instructor'] != null) {
            instructorLabel.value = classes[0]['instructor'];
            }
        }

        classes.forEach((classItem) => {



            option = document.createElement('option');

            option.value = classItem['id']
            option.textContent = classItem['name']
            option.setAttribute('data-instructor', classItem['instructor'])

            enrollSelect.appendChild(option);
        });

    }).catch(error => {
        console.log('Error:', error);
    })
}
enrollSelect.addEventListener('change', function() {
    selectedOption = enrollSelect.options[enrollSelect.selectedIndex];
    instructorName = selectedOption.getAttribute('data-instructor');
    instructorLabel.value = instructorName;
})




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


