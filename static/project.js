

function addSetInfo(set_num, exerciseDiv) {
    const setDiv = document.createElement('div');  // Create a container for each set
    setDiv.classList.add("set-entry");

    // Create the label specifying which set it is
    const label = document.createElement("label");
    label.textContent = `Set ${set_num}`;  // Dynamically set the label text based on the set number
    setDiv.appendChild(label);

    // Add input fields for weights and reps
    addInput("weights[]", "lbs", setDiv, "short-input");
    addInput("reps[]", "reps", setDiv, "short-input");
    if (exerciseDiv) {
        // Append the new set div under the exercise div
        exerciseDiv.appendChild(setDiv);  // Append the set container to the exercise div
    }
}




// Function to handle delete button and confirmation
function deleteRoutineEvent() {
    const deleteButton = document.getElementById("delete-button");
    const deleteConfirmation = document.getElementById("delete-confirmation");
    const cancelButton = document.getElementById("cancel-button");

    deleteButton.addEventListener("click", function() {
        // Show the confirmation section and hide the original delete button
    deleteConfirmation.style.display = "block";  // Show confirmation buttons
    deleteButton.style.display = "none";         // Hide original delete button
    });
    cancelButton.addEventListener("click", function() {
        // Hide the confirmation buttons and show the original delete button again
        deleteConfirmation.style.display = "none";
        deleteButton.style.display = "inline";
    });
}

// get the exercises and corresponding sets from the backend for selected routine
// Function to fetch routine data
function getRoutineData(routineName) {
    return new Promise((resolve, reject) => {
        fetch('/full_routine', {
            method: 'POST',
            body: new URLSearchParams({
                'routine_name': routineName
            }),
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        })
        .then(response => response.json())  // The response should be JSON
        .then(data => {
            console.log("Fetched Routine Data:", data);  // Log the fetched data
            resolve(data);  // Resolve the promise with the routine data
        })
        .catch(error => {
            console.error("Error fetching full routine data:", error);
            reject(error);  // Reject the promise in case of an error
        });
    });
}

function validateRoutineData(routineData) {
    // Ensure routineData is an array and each element has the expected properties
    if (!Array.isArray(routineData) || !routineData.every(row => row.hasOwnProperty('exercise_name') && row.hasOwnProperty('sets'))) {
        console.error("Invalid routine data. Expected an array of objects with 'exercise_name' and 'sets' properties.");
        return;
    }
}
function editRoutineForm(routineData) {
    console.log("Routine Data Received:", routineData);  // log the data passed into the function
    console.log("Is routineData an array?", Array.isArray(routineData));
    validateRoutineData(routineData);
    const routineContainerElement = document.getElementById("edit-routine-container");
    if (!routineContainerElement) {
        console.error("Routine container not found!");
        return;
    }

    routineData.forEach(row => {
        const exerciseDiv = document.createElement('div');  // Create div for each exercise

        // Call inputExercise and wait for it to resolve before setting values
        inputExercise(exerciseDiv).then(exerciseInput => {
            // Ensure the input is returned before setting its value
            if (exerciseInput) {
                exerciseInput.value = row.exercise_name;  // Set the exercise name

                // Create an input field for sets and set the value
                const setsInput = addInput('sets[]', '', exerciseDiv, 'short-input');
                setsInput.value = row.sets;  // Set the number of sets

                // Append the entire exerciseDiv (with exercise name and sets) to the container
                routineContainerElement.appendChild(exerciseDiv);
            } else {
                console.error("exerciseInput was not returned correctly.");
            }
        }).catch(error => {
            console.error("Error creating exercise input:", error);
        });
    });
}

function followRoutineForm(routineData) {
    console.log(routineData);  // Log the data to verify it's correct
    validateRoutineData(routineData);
    let lastExerciseDiv = null;
    const routineContainerElement = document.getElementById("routine-container");

    if (!routineContainerElement) {
        console.error("Routine container not found!");
        return;
    }

    routineData.forEach(row => {
        // Create a div for each exercise
        const newExerciseDiv = document.createElement('div');
        let lastExerciseDiv = newExerciseDiv;
        // First, add the exercise name
        inputExercise(newExerciseDiv).then(exerciseInput => {
            if (exerciseInput) {
                // Set the exercise name
                exerciseInput.value = row.exercise_name;
                exerciseInput.disabled = true;  // Disable to prevent editing the exercise name
                lastExerciseDiv = newExerciseDiv;
            } else {
                console.error("exerciseInput was not returned correctly.");
            }

            // Now, for each set, add `lbs` and `reps` inputs
            for (let i = 0; i < row.sets; i++) {
                // Create and append input fields for weight and reps for each set
                addSetInfo(i + 1);
                if (lastExerciseDiv) {
                    addSetInfo(i + 1, lastExerciseDiv);
                }
            }
            // After creating the inputs for all sets, append the whole exerciseDiv to the container
            routineContainerElement.appendChild(lastExerciseDiv);
        }).catch(error => {
            console.error("Error creating exercise input:", error);
        });
    });
}









// display routine data in an html table
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
    const routineSelectcontainer = document.getElementById("routine-select-container");
    if (routineSelectcontainer) {
        routineSelectcontainer.innerHTML = `<select id="routine-select" name="routine-select" placeholder="routine-name" class="routine-select"></select>`;
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
            defaultOption.textContent = "select a routine";  // placeholder text
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

// set to date of first log


// fetch exercises in json from backend and create datalist
function exerciseDatalist() {
    return new Promise((resolve, reject) => {
        fetch("/json_exercises")
            .then(response => response.json())
            .then(exercises => {
                const datalist = document.createElement("datalist");
                const datalistId = "exercise-list-" + new Date().getTime(); // unique id for each datalist
                datalist.setAttribute("id", datalistId);

                // clear any existing options
                datalist.innerHTML = "";

                // populate the datalist with options from the exercises array
                exercises.forEach(exercise => {
                    const option = document.createElement("option");
                    option.value = exercise;  // the value is the exercise name
                    datalist.appendChild(option);
                });

                resolve(datalist);  // Resolve the promise with the populated datalist
            })
            .catch(error => {
                console.error("Error fetching exercise data:", error);
                reject(error);
            });
    });
}

// add exercise button clicked event listener
// attach the event listener for "add exercise" after it's added to the dom
// Function to handle adding exercise inputs
function addExerciseSetsEvent() {
    document.getElementById("add-exercise").addEventListener("click", function() {
        const exerciseContainer = document.getElementById("add-exercise-container");

        if (exerciseContainer) {
            // Create a new div for the exercise entry
            const newExerciseDiv = document.createElement("div");
            newExerciseDiv.classList.add("exercise-entry");

            // Call inputExercise to populate the new div with exercise inputs
            inputExercise(newExerciseDiv).then(() => {
                // After populating the exercise data list, add input for sets
                addInput("sets[]", "sets", newExerciseDiv, "short-input");

                // Append the new exercise div to the container
                exerciseContainer.appendChild(newExerciseDiv);
            }).catch(error => {
                console.error("Error populating exercise data:", error);
            });
        }
    });
}

function inputExercise(ExerciseDiv) {
    return new Promise((resolve, reject) => {
        // Ensure ExerciseDiv is defined
        if (!ExerciseDiv) {
            console.error("ExerciseDiv is not defined.");
            return reject("ExerciseDiv is not defined.");
        }

        // Create the input field for exercise
        const exerciseInput = document.createElement("input");
        const datalistId = "exercise-list-" + new Date().getTime(); // Unique id for each datalist
        exerciseInput.setAttribute("list", datalistId);  // Link the input field with the unique datalist
        exerciseInput.setAttribute("name", "exercises[]");
        exerciseInput.setAttribute("class", "long-input");

        // Set placeholder for the exercise input
        exerciseInput.setAttribute("placeholder", "Exercise Name");

        // Append the input element to the ExerciseDiv
        ExerciseDiv.appendChild(exerciseInput);

        // Fetch the exercise data and create the datalist
        exerciseDatalist()
            .then(datalist => {
                // Set the datalist ID to match the input's datalist attribute
                datalist.setAttribute("id", datalistId);
                
                // Append the datalist to the ExerciseDiv
                ExerciseDiv.appendChild(datalist);

                // Resolve the promise and return the exerciseInput element
                resolve(exerciseInput);
            })
            .catch(error => {
                console.error("Error fetching exercise data:", error);
                reject(error);
            });
    });
}

// input field to have in exercise containers
// placeholder parameter because i want the weight input to say lbs not weight
// made placeholder optional for easier implemention in the edit routine form but I might do it depending on the look while editing

function addInput(name, placeholder, newDiv, cssClass) {
    const input = document.createElement("input");

    // Set attributes for the input
    input.setAttribute("type", "text");  // Type text for versatility with letters and numbers
    input.setAttribute("name", name);  // Dynamic name (sets[] for multiple sets)
    if (placeholder) input.setAttribute("placeholder", placeholder);

    // Add the passed cssClass to the input to adjust its width
    input.classList.add(cssClass);

    // Append the new input field to the provided div
    newDiv.appendChild(input);

    // Return the input element so we can chain operations on it if needed
    return input;
}

