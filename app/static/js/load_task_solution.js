function loadFile(taskId) {
    var file = document.getElementById("file").files[0];
    var fr = new FileReader();
    
    function receivedText() {
        $.ajax({
            url: `/submit_solution/${taskId}`,
            type: "POST",
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            data: JSON.stringify({
                "content": fr.result,
                "extension": getFileExtension(file.name)
            }),
            success: response => {
                if (response.error) { console.log(response.error) }
                else { document.location.reload()};
            },
            error: (request, status, error) => {
                console.log(error);
            }
        });
    } 

    fr.onload = receivedText;
    fr.readAsText(file);
}

function getFileExtension(filename) {
    return filename.substring(filename.lastIndexOf(".")+1);
}
