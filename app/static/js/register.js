function askEmailConfirmation() {
    var email = document.getElementById("email").value;
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;
    var role = $("input[type='radio'][name='role']:checked").val();

    $.ajax({
        url: "/create_token_confirmation",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        data: JSON.stringify({
            "email": email,
            "username": username,
            "password": password,
            "role": role
        }),
        success: response => {
            deleteRegisterButton();
            showEmailSendMessage();
        },
        error: (request, status, error) => {
            console.log(error);
        }
    });
}


function deleteRegisterButton() {
    document.getElementById("button").remove();
}


function showEmailSendMessage() {
    alert = document.createElement("h1");
    alert.classList.add("alert");
    alert.innerHTML = "Письмо отправлено на почту!";
    document.getElementById("form").replaceWith(alert);
}
