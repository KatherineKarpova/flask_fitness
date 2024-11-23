// inner html for date form
function dateForm(formId) {
    // ensure each date form has it's own unique id
    const formContainer = document.getElementById(formId);
    if (formContainer) {
        formContainer.innerHTML = `
        <label for="month-${formId}">Month:</label>
        <input list="month-list-${formId}" id="month-${formId}" name="month" placeholder="month">
        <datalist id="month-list-${formId}">
            {% for month in months %}
                <option value="{{ month[0] }}">
            {% endfor %}
        </datalist>
        
        <label for="day-${formId}">Day:</label>
        <select id="day-${formId}" name="day"></select>
        
        <label for="year-${formId}">Year:</label>
        <select id="year-${formId}" name="year"></select>
        `;
    } 
    else {
        console.error(`Element with id "${formId}" not found`);
    }
};

function defineDateElements(formId) {
    // define elements with unique id from html
    const monthElement = document.getElementById(`month-${formId}`);
    const dayElement = document.getElementById(`day-${formId}`);
    const yearElement = document.getElementById(`year-${formId}`);
    return { monthElement, dayElement, yearElement };
}

// update the number of days based on the today's month and year
function updateDays(elements){

    // convert month and year from strs to ints
    const month = parseInt(elements.monthElement.value, 10);
    const year = parseInt(elements.yearElement.value, 10);
    // find number of days in the selected month/year
    const daysInMonth = new Date(year, month, 0).getDate();

    elements.dayElement.innerHTML = '';

    // populate day dropdown with the correct number of days based on month/year
    for (let day = 1; day <= daysInMonth; day++) {
        const option = document.createElement('option');
        option.value = day < 10 ? '0' + day : day;
        option.textContent = day < 10 ? '0' + day : day;
        elements.dayElement.appendChild(option);
    }
}


function updateTodayDate(formId) {

        // define elements from select date form
        
        elements = defineDateElements(formId);

        // set default date that of today
        function setToday() {
            const today = new Date();
            elements.monthElement.value = today.getMonth() + 1;
            elements.dayElement.value = today.getDate();
            elements.yearElement.value = today.getFullYear();
        }
        setToday();

        // update the number of days based on selected month/year
        updateDays(elements);

        // update day dropdown if month or year changes
        elements.monthElement.addEventListener('change', () => updateDays(elements));
        elements.yearElement.addEventListener('change', () => updateDays(elements));

        // call to reload page after if changes
    }

    function endDate(formId) {
        // call html form with unique id
        dateFrom(formId);
        defineDateElements(formId);


    }