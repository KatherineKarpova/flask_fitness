// Function to get routine names and populate the select options
function get_routines() {
    // Fetch the routine data from the Flask backend
    fetch("/routine_names")
        .then(response => response.json()) // Parse JSON response
        .then(routines => {
            // Get the select element where options will be added
            const select = document.getElementById('routine-select');  // Adjust the ID if needed

            // Clear any existing options first to prevent duplicates
            select.innerHTML = '';

            // Add the default "Select a routine" option
            const defaultOption = document.createElement('option');
            defaultOption.text = 'follow a routine';
            select.appendChild(defaultOption);

            // Loop through the routine names and create an option for each
            routines.forEach(routine => {
                const option = document.createElement('option');
                option.value = routine;  // Set the routine name as the value
                option.textContent = routine; // Set the routine name as the displayed text
                select.appendChild(option);  // Append the option to the select element
            });
        })
        .catch(error => {
            console.error("Error fetching routine names:", error);
        });
}

// Helper function to return the list of months (name only)
function months() {
    return [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];
};

// Inner HTML for date form
function dateForm(formId) {
    const formContainer = document.getElementById(formId);
    if (formContainer) {
        // Construct the HTML dynamically using JavaScript
        formContainer.innerHTML = `
            <select id='month-${formId}' name='month-${formId}' class="month">
                ${months().map((month, index) => `<option value='${index + 1}'>${month}</option>`).join('')}
            </select>
            <select id='day-${formId}' name='day-${formId}' class="day"></select>
            <select id='year-${formId}' name='year-${formId}' class="year"></select>
        `;
        // After rendering the form, populate the year and day fields
    } else {
        console.error(`Element with id '${formId}' not found`);
    }
};

// Define elements with unique id from HTML
function defineDateElements(formId) {
    const monthElement = document.getElementById(`month-${formId}`);
    const dayElement = document.getElementById(`day-${formId}`);
    const yearElement = document.getElementById(`year-${formId}`);
    return { monthElement, dayElement, yearElement };
};

// Update the number of days based on the selected month and year
function updateDays(elements) {
    const month = parseInt(elements.monthElement.value, 10);
    const year = parseInt(elements.yearElement.value, 10);

    // Ensure that the month and year are valid before proceeding
    if (isNaN(month) || isNaN(year)) {
        return;
    }

    // Find the number of days in the selected month/year
    const daysInMonth = new Date(year, month, 0).getDate();

    // Clear the existing day options
    elements.dayElement.innerHTML = '';

    // Populate the day dropdown with the correct number of days based on month/year
    for (let day = 1; day <= daysInMonth; day++) {
        const paddedDay = day < 10 ? '0' + day : day; // Ensure days are zero-padded if necessary
        const option = document.createElement('option');
        option.value = paddedDay;
        option.textContent = paddedDay;
        elements.dayElement.appendChild(option);
    }
};

// Populate the year dropdown with a range of years (e.g., current year to next 10 years)
function populateYearDropdown(elements) {
    const currentYear = new Date().getFullYear();
    const years = [];

    // Populate with 10 years forward from the current year
    for (let i = 0; i < 5; i++) {
        years.push(currentYear - i);
    }

    // Clear the year dropdown before populating
    elements.yearElement.innerHTML = '';

    // Add options to the year dropdown
    years.forEach(year => {
        const option = document.createElement('option');
        option.value = year;
        option.textContent = year;
        elements.yearElement.appendChild(option);
    });
};

// Set today's date in the form (for default selection)
function setToday(elements) {
    const today = new Date();

    // Set the current month, day, and year
    elements.monthElement.value = today.getMonth() + 1; // Months are zero-based, so add 1
    // elements.dayElement.value = today.getDate();
    elements.yearElement.value = today.getFullYear();
    const paddedDay = today.getDate() < 10 ? '0' + today.getDate() : today.getDate();
    elements.dayElement.value = paddedDay;
}; 
// add exercise input with a datalist of names via json return
function addExercise(newExerciseDiv) {
    return new Promise((resolve, reject) => {
        // Create the input field for exercise
        const exerciseInput = document.createElement("input");
        const datalistId = "exercise-list-" + new Date().getTime(); // Unique id for each datalist
        exerciseInput.setAttribute("list", datalistId);  // Link the input field with the unique datalist
        exerciseInput.setAttribute("name", "exercise");
        exerciseInput.setAttribute("class", "exercise-input");
        exerciseInput.setAttribute("placeholder", "exercise");

        // Add the input element to the new div
        newExerciseDiv.appendChild(exerciseInput);

        // Create a datalist and set a unique id
        const datalist = document.createElement("datalist");
        datalist.setAttribute("id", datalistId);

        // Fetch the exercise data from the Flask backend
        fetch("/json_exercises")
            .then(response => response.json())
            .then(exercises => {
                // Clear any existing options
                datalist.innerHTML = '';

                // Populate the datalist with options from the exercises array
                exercises.forEach(exercise => {
                    const option = document.createElement('option');
                    option.value = exercise;  // The value is the exercise name
                    datalist.appendChild(option);
                });

                // Now append the datalist to the new exercise div (after it has been populated)
                newExerciseDiv.appendChild(datalist);

                // Ensure the Promise is resolved only after the datalist is appended
                resolve();
            })
            .catch(error => {
                console.error('Error fetching exercise data:', error);
                reject(error);
            });
    });
}


function addInputField(companion, placeholder, newDiv, cssClass) {
    const companionInput = document.createElement("input");

    // Set attributes for the input
    companionInput.setAttribute("type", "text");
    companionInput.setAttribute("name", `${companion}s[]`);  // Using template literals to create dynamic name
    companionInput.setAttribute("placeholder", `${placeholder}`);

    // Add the passed cssClass to the input to adjust width
    companionInput.classList.add(cssClass);

    // Append the new input field to the div
    newDiv.appendChild(companionInput);
}
