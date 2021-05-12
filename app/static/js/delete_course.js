function deleteCourse(courseId) {
    $.ajax({
        url: `/delete_course/${courseId}`,
        type: "POST",
        success: response => {
            window.history.back();
        },
        error: (request, status, error) => {
            console.log(error);
        }
    });
}
