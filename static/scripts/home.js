 const hamburger = document.querySelector('#toggle-btn');

 hamburger.addEventListener("click",function() {
    document.querySelector("#sidebar").classList.toggle("expand");
 });

delete_buttons = document.querySelectorAll('.delete-course-btn');
delete_buttons.forEach((button) => {
    button.addEventListener('click', async function() {
        courseCard = button.closest('.course-card');
        user_id = courseCard.getAttribute('data-user-id');
        class_id = courseCard.getAttribute('data-class-id');

        try {
            response = await fetch(`/api/enrollment/${user_id}/${class_id}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            data = await response.json();
            if (data['error']) {
                console.log('error: ', data['error']);
            } else {
                window.location.reload();
            }
        } catch (error) {
            console.log('error: ', error);
        }
    })
})


//detailsBtn = document.getElementById('view-details');
//detailsBtn.addEventListener('click', function() {
//    console.log('test');
//
//})





