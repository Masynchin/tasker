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
            createTokenField();
            updateButtonType();
        },
        error: (request, status, error) => {
            console.log(error);
        }
    });

    button = document.getElementById("button");
    button.setAttribute("type", "submit");
    button.innerHTML = "Подтвердить данные";
    button.onclick = confirmDataIdentity;
}

function createTokenField() {
    var label = document.createElement("label");
    label.setAttribute("for", "confirmationToken");
    label.classList.add("form-label");
    label.innerHTML = "Токен из письма";

    var input = document.createElement("input");
    input.id = "confirmationToken"
    input.type = "text";
    input.setAttribute("name", "confirmationToken");
    input.classList.add("form-control");

    var form = document.getElementById("form");
    form.appendChild(label);
    form.appendChild(input);
}

function updateButtonType() {
    button = document.getElementById("button");
    button.setAttribute("type", "submit");
    button.innerHTML = "Подтвердить данные";
    button.onclick = confirmDataIdentity;
}

function confirmDataIdentity() {
    var confirmation_token = document.getElementById("confirmationToken").value;
    var email = document.getElementById("email").value;
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;
    var role = $("input[type='radio'][name='role']:checked").val();

    $.ajax({
        url: "/check_register_data_indentity",
        type: "POST",
        dataType: "json",
        data: JSON.stringify({
            "email": email,
            "confirmation_token": confirmation_token,
            "username": username,
            "password": password,
            "role": role
        }),
        success: response => {
            if (response.error) {
                console.log(response.error);
                alertConfirmationError(response.error);
            } else {
                document.getElementById("form").submit();
            }
        },
        error: (request, status, error) => {
            console.log(error);
        }
    });
}

function alertConfirmationError(errorDescription) {
    var alert = document.createElement("alert");
    alert.classList.add("alert");
    alert.classList.add("alert-danger");
    alert.role = "alert";
    alert.innerHTML = errorDescription;

    document.getElementById("form").appendChild(alert);
}
