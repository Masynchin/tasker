function performSearch() {
    var requestText = $("#searchInput").val();
    if(requestText) {
        $.ajax({
            url: `/search_courses?q=${requestText}`,
            type: "POST",
            success: response => {
                if (response.error) { console.log(response.error) }
                else { drawCoursesCards(response.courses) };
            },
            error: (request, status, error) => {
                console.log(error);
            }
        })
    };
}

function drawCoursesCards(courses) {
    var cardsGrid = document.getElementById("cardsGrid");
    clearCardsGrid(cardsGrid);
    if (Array.isArray(courses) && courses.length) {
        courses.forEach(function(course) {
            drawCourseCard(cardsGrid, course);
        });
    } else {
        respondEmptyResult(cardsGrid);
    };
}

function clearCardsGrid(cardsGrid) {
    while (cardsGrid.firstChild) {
        cardsGrid.removeChild(cardsGrid.lastChild);
    }
}

function drawCourseCard(cardsGrid, course) {
    var cardLink = document.createElement("a");
    cardLink.classList.add("course-link");
    cardLink.href = `/course/${course.id}`;

    card = document.createElement("div");
    card.classList.add("card");
    card.classList.add("course-card");
    card.classList.add("border-dark");

    cardBody = document.createElement("div");
    cardBody.classList.add("card-body");

    cardTitle = document.createElement("h2");
    cardTitle.classList.add("card-title");
    cardTitle.innerHTML = course.title;

    cardDescription = document.createElement("p");
    cardDescription.classList.add("card-text");
    cardDescription.innerHTML = course.description;

    cardBody.appendChild(cardTitle);
    cardBody.appendChild(cardDescription);
    card.appendChild(cardBody);
    cardLink.appendChild(card);
    cardsGrid.appendChild(cardLink);
}


function respondEmptyResult(cardsGrid) {
    cardsGrid.innerHTML = "<h3>\
        К сожалению, открытых курсов с таким названием не найдено\
    </h3>";
}
