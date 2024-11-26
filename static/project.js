// Helper function to return the list of months (name only)
function months() {
    return [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];
}

// Inner HTML for date form
function dateForm(formId) {
    const formContainer = document.getElementById(formId);
    if (formContainer) {
        // Construct the HTML dynamically using JavaScript
        formContainer.innerHTML = `
            <label for='month-${formId}'>Month:</label>
            <select id='month-${formId}' name='month-${formId}'>
                ${months().map((month, index) => `<option value='${index + 1}'>${month}</option>`).join('')}
            </select>
            
            <label for='day-${formId}'>Day:</label>
            <select id='day-${formId}' name='day-${formId}'></select>
            
            <label for='year-${formId}'>Year:</label>
            <select id='year-${formId}' name='year-${formId}'></select>
        `;
        // After rendering the form, populate the year and day fields
        populateYearDropdown(formId);
        updateDays(formId);
    } else {
        console.error(`Element with id '${formId}' not found`);
    }
}

// Define elements with unique id from HTML
function defineDateElements(formId) {
    const monthElement = document.getElementById(`month-${formId}`);
    const dayElement = document.getElementById(`day-${formId}`);
    const yearElement = document.getElementById(`year-${formId}`);
    return { monthElement, dayElement, yearElement };
}

// Update the number of days based on the selected month and year
function updateDays(formId) {
    const elements = defineDateElements(formId);
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
}

// Populate the year dropdown with a range of years (e.g., current year to next 10 years)
function populateYearDropdown(formId) {
    const elements = defineDateElements(formId);
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
}

// Set today's date in the form (for default selection)
function setToday(formId) {
    const elements = defineDateElements(formId);
    const today = new Date();

    // Set the current month, day, and year
    elements.monthElement.value = today.getMonth() + 1; // Months are zero-based
    elements.yearElement.value = today.getFullYear();
    elements.dayElement.value = today.getDate();
}

// Example of how to initialize the form and set today's date
window.onload = function() {
    const formId = 'entry-date';  // Use a unique ID for each form
    dateForm(formId);  // Create the date form
    setToday(formId);  // Set today's date as default
};
