 const hamburger = document.querySelector('#toggle-btn');

 hamburger.addEventListener("click",function() {
    document.querySelector("#sidebar").classList.toggle("expand");
 });

const delete_buttons = document.querySelectorAll('.delete-course-btn');
delete_buttons.forEach((button) => {
    button.addEventListener('click', async function() {
                let courseCard = button.closest('.course-card');
                let user_id = courseCard.getAttribute('data-user-id');
        class_id = courseCard.getAttribute('data-class-id');

        if (await deleteCourseFromUser(user_id, class_id)) {
            window.location.reload();
        }
    })
})

async function deleteCourseFromUser(user_id, class_id) {
    try {
            const response = await fetch(`/api/enrollment/${user_id}/${class_id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            }
        });
                const data = await response.json();
        if (data['error']) {
            console.log('error: ', data['error']);
            return false;
        }
    } catch (error) {
        console.log('error: ', error);
        return false;
    }
    return true;
}

//detailsBtn = document.getElementById('view-details');
//detailsBtn.addEventListener('click', function() {
//    console.log('test');
//
//})


$(document).ready(function() {
    $('.select2').select2({
        theme: 'bootstrap-5'
    });
});
