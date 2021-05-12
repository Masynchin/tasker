function confirmInvite() {
    var invite = document.getElementById("invite").value;

    $.ajax({
        url: "/confirm_course_invite",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        data: JSON.stringify({
            "invite": invite
        }),
        success: response => {
            if (response.error){
                popupErrorAlert(response.error);
            } else {
                window.location.href = `/course/${response.courseId}`;
            };
        },
        error: (request, status, error) => {
            return false;
        }
    });
}


function popupErrorAlert(errorDescription) {
    if (document.getElementById("alert")) { return };

    var alert = document.createElement("alert");
    alert.classList.add("alert");
    alert.classList.add("alert-danger");
    alert.role = "alert";
    alert.id = "alert";
    alert.innerHTML = errorDescription;

    var pseudoForm = document.getElementById("pseudo-form");
    var button = document.getElementById("button");
    pseudoForm.insertBefore(alert, button);
}
