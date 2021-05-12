function approveSolution(solutionId) {
    markSolution(true, solutionId);
}

function rejectSolution(solutionId) {
    markSolution(false, solutionId);
}

function markSolution(isCorrect, solutionId) {
    $.ajax({
        url: "/mark_solution",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        data: JSON.stringify({
            "solutionId": solutionId,
            "isCorrect": isCorrect
        }),
        success: reponse => {
            if (reponse.error) {
                console.log(response.error)
            } else {
                location.replace(document.referrer);
            };
        },
        error: (request, status, error) => {
            console.log(error);
        }
    });
}
