function subscribe(courseId) {
    $.ajax({
        url: `/subscribe/${courseId}`,
        type: "POST",
        success: response => {
            var title = response.isSubscribed ? "Отписаться" : "Записаться";
            $("#subscribeButton").text(title);
        },
        error: (request, status, error) => {
            console.log(error);
        }
    });
}
