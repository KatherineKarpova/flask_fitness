// get the exercises and corresponding sets from the backend for selected routine
function fullRoutine(routineName) {
    // routine data from the backend
    fetch('/full_routine', {
        method: 'POST',
        body: new URLSearchParams({
            'routine_name': routineName
        }),
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    })
    .then(response => response.json())  // the response should be JSON
    .then(data => {
        console.log('Routine Data:', data);
        if (data.error) {
            alert(data.error);  // show error message if routine not found
        } else {
            routineTable(data);  // display data if routine is found
        }
    })
    .catch(error => {
        console.error('error fetching routine data:', error);
    });
}

// function to display routine data in an html table
function routineTable(data) {
    const routineContainer = document.getElementById('routine-table-container');
    routineContainer.innerHTML = '';  // Clear any previous table data

    const table = document.createElement('table');
    table.classList.add('routine-table');

    const header = table.createTHead();
    const headerRow = header.insertRow();
    headerRow.innerHTML = `
        <th>exercise</th>
        <th>sets</th>
    `;

    const body = table.createTBody();
    data.forEach(row => {
        const rowElement = body.insertRow();
        rowElement.innerHTML = `
            <td>${row.exercise_name}</td>
            <td>${row.sets}</td>
        `;
    });

    routineContainer.appendChild(table);
}

// reuse html to select routine 
function routineSelect(){
    const routineSelectcontainer = document.getElementById("routine-select");
    if (routineSelectcontainer) {
        routineSelectcontainer.innerHTML = `<select id="routine-select" name="routine" placeholder="routine-name" class="routine-select"></select>`;
    }
}
// function to fetch routines from the server and populate the select menu
function getRoutines() {
    // fetch the routine data from the flask backend
    fetch("/routine_names")
        .then(response => response.json())  // parse json response
        .then(routines => {
            console.log(routines); 

            // get the select element by id
            const select = document.getElementById("routine-select");
            // create a non-selectable default option
            const defaultOption = document.createElement("option");
            defaultOption.value = "";  // no value, placeholder only
            defaultOption.textContent = "Follow a routine";  // placeholder text
            defaultOption.disabled = true;  // disable it so it can't be selected
            defaultOption.selected = true;  // set it as the default selected option
            select.appendChild(defaultOption);  // append it to the select element
           
            // loop through the routine names and create an option for each
            routines.forEach(routine => {
                const option = document.createElement("option");
                option.value = routine;  // set the routine name as the value
                option.textContent = routine; // set the routine name as the displayed text
                select.appendChild(option);  // append the option to the select element
            });
        })
        .catch(error => {
            console.error("error fetching routine names:", error);
        });
}

// helper function to return the list of months (name only)
function months() {
    return [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];
};

// inner html for date form
function dateForm(formId) {
    const formContainer = document.getElementById(formId);
    if (formContainer) {
        // construct the html dynamically using javascript
        formContainer.innerHTML = `
            <select id="month-${formId}" name="month-${formId}" class="month">
                ${months().map((month, index) => `<option value="${index + 1}">${month}</option>`).join("")}
            </select>
            <select id="day-${formId}" name="day-${formId}" class="day"></select>
            <select id="year-${formId}" name="year-${formId}" class="year"></select>
        `;
        // after rendering the form, populate the year and day fields
    } else {
        console.error(`element with id "${formId}" not found`);
    }
};

// define elements with unique id from html
function defineDateElements(formId) {
    const monthElement = document.getElementById(`month-${formId}`);
    const dayElement = document.getElementById(`day-${formId}`);
    const yearElement = document.getElementById(`year-${formId}`);
    return { monthElement, dayElement, yearElement };
};

// update the number of days based on the selected month and year
function updateDays(elements) {
    const month = parseInt(elements.monthElement.value, 10);
    const year = parseInt(elements.yearElement.value, 10);

    // ensure that the month and year are valid before proceeding
    if (isNaN(month) || isNaN(year)) {
        return;
    }

    // find the number of days in the selected month/year
    const daysInMonth = new Date(year, month, 0).getDate();

    // clear the existing day options
    elements.dayElement.innerHTML = "";

    // populate the day dropdown with the correct number of days based on month/year
    for (let day = 1; day <= daysInMonth; day++) {
        const paddedDay = day < 10 ? "0" + day : day; // ensure days are zero-padded if necessary
        const option = document.createElement("option");
        option.value = paddedDay;
        option.textContent = paddedDay;
        elements.dayElement.appendChild(option);
    }
};

// populate the year dropdown with a range of years (e.g., current year to next 10 years)
function populateYearDropdown(elements) {
    const currentYear = new Date().getFullYear();
    const years = [];

    // populate with 10 years forward from the current year
    for (let i = 0; i < 5; i++) {
        years.push(currentYear - i);
    }

    // clear the year dropdown before populating
    elements.yearElement.innerHTML = "";

    // add options to the year dropdown
    years.forEach(year => {
        const option = document.createElement("option");
        option.value = year;
        option.textContent = year;
        elements.yearElement.appendChild(option);
    });
};

// set today's date in the form (for default selection)
function setToday(elements) {
    const today = new Date();

    // set the current month, day, and year
    elements.monthElement.value = today.getMonth() + 1; // months are zero-based, so add 1
    // elements.dayElement.value = today.getDate();
    elements.yearElement.value = today.getFullYear();
    const paddedDay = today.getDate() < 10 ? "0" + today.getDate() : today.getDate();
    elements.dayElement.value = paddedDay;
}; 

// add exercise input with a datalist of names via json return
function addExercise(newExerciseDiv) {
    return new Promise((resolve, reject) => {
        // create the input field for exercise
        const exerciseInput = document.createElement("input");
        const datalistId = "exercise-list-" + new Date().getTime(); // unique id for each datalist
        exerciseInput.setAttribute("list", datalistId);  // link the input field with the unique datalist
        exerciseInput.setAttribute("name", "exercises[]");
        exerciseInput.setAttribute("class", "long-input");
        exerciseInput.setAttribute("placeholder", "exercise");

        // add the input element to the new div
        newExerciseDiv.appendChild(exerciseInput);

        // create a datalist and set a unique id
        const datalist = document.createElement("datalist");
        datalist.setAttribute("id", datalistId);

        // fetch the exercise data from the flask backend
        fetch("/json_exercises")
            .then(response => response.json())
            .then(exercises => {
                // clear any existing options
                datalist.innerHTML = "";

                // populate the datalist with options from the exercises array
                exercises.forEach(exercise => {
                    const option = document.createElement("option");
                    option.value = exercise;  // the value is the exercise name
                    datalist.appendChild(option);
                });

                // now append the datalist to the new exercise div (after it has been populated)
                newExerciseDiv.appendChild(datalist);

                // ensure the promise is resolved only after the datalist is appended
                resolve();
            })
            .catch(error => {
                console.error("error fetching exercise data:", error);
                reject(error);
            });
    });
}

// input field to have in exercise containers
// placeholder parameter because i want the weight input to say lbs not weight
function addInputList(companion, placeholder, newDiv, cssClass) {
    const input = document.createElement("input");

    // set attributes for the input
    input.setAttribute("type", "number");
    input.setAttribute("name", `${companion}s[]`);  // using template literals to create dynamic name
    input.setAttribute("placeholder", `${placeholder}`);

    // add the passed cssClass to the input to adjust width
    input.classList.add(cssClass);

    // append the new input field to the div
    newDiv.appendChild(input);
}

