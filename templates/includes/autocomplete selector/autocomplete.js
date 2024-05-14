/**/
const conferences_churches = {
    //{% for key, conference in conferences.items() %}
    "{{ conference[0].conferenceName }}": [
        //{% for church in conference %}
        "{{ church.name | safe }}",
        //{% endfor %}
    ].sort(),        
    //{% endfor %}
};
//{% if selectTreasurer %}
const treasurers = {
    //{% for key, group in treasurers.items() %}
    "{{ key }}": [
        //{% for treasurer in group %}
        {
            name: "{{ treasurer.name if treasurer.name else ''}}",
            id: "{{ treasurer.id }}",
            phone: "{{ treasurer.phoneNumber if treasurer.phoneNumber else ''}}",
            email: "{{ treasurer.email if treasurer.email else ''}}",
        },
        //{% endfor %}
    ],        
    //{% endfor %}
}
//{% endif %}
const unsupportedConferences = [
    //{% for conference in unsupportedConferences %}
        "{{ conference.name }}",
    //{% endfor %}
];


// Initialize autocomplete for conference input field
$("#conference").autocomplete({
    minLength: 0,
    delay: 0,
    source: Object.keys(conferences_churches),
    select: function(event, ui) {
        // Call validateInputConference when an option is selected
        validateInputConference(null, ui.item.value);
    }
});
$("#conference").on("click", function() {
    $(this).autocomplete("search", $(this).val());
});

//{% if selectChurch %}
// Initialize autocomplete for church input field
$("#church").autocomplete({
    minLength: 0,
    delay: 0,
    source: function(request, response) {
        const selectedConference = $("#conference").val();
        const churches = conferences_churches[selectedConference] || [];
        response(churches.filter(church => church.toLowerCase().includes(request.term.toLowerCase())));
    },
    select: function(event, ui) {
        // Call validateInputChurch when an option is selected
        validateInputChurch(null, ui.item.value);
    }
});
$("#church").on("click", function() {
    $(this).autocomplete("search", $(this).val());
});
//{% endif %}

// Function to validate input and update border color
function validateInputConference(stuff, val) {
    validOptions = Object.keys(conferences_churches);
    const input = document.getElementById('conference');
    const value = val || input.value;

    validateInput(input, value, validOptions, value)
    //{% if selectChurch %}
    validateInputChurch(null, null, val)
    //{% endif %}
}
//{% if selectChurch %}
function validateInputChurch(stuff, val, conf) {
    const selectedConference = conf || document.getElementById('conference').value;
    const validOptions = conferences_churches[selectedConference] || [];

    const input = document.getElementById('church');
    const value = val || input.value;

    validateInput(input, value, validOptions, selectedConference)
    //{% if selectTreasurer %}
    updateTreasurerOptions(conf, val)
    //{% endif %}
}
//{% endif %}
function validateInput(inputBox, value, validOptions, confValue) {
    // Check if input value is empty
    if (value === '') {
        inputBox.style.border = '3px solid';
        inputBox.dataset.inDB = "empty";
        return;
    }

    // Check if input value is in the valid options array
    if (validOptions.includes(value)) {
        if (unsupportedConferences.includes(confValue) && value != "Conference Office") {
            inputBox.style.border = '3px solid gold';
            inputBox.dataset.inDB = "unsupported";
        } else {
            inputBox.style.border = '3px solid mediumspringgreen';
            inputBox.dataset.inDB = "valid";
        }
    } else {
        inputBox.style.border = '3px solid red';
        inputBox.dataset.inDB = "invalid";
    }
}

// Event listener for input value change
document.getElementById('conference').addEventListener('input', validateInputConference);
//{% if selectChurch %}
document.getElementById('church').addEventListener('input', validateInputChurch);
//{% endif %}

//{% if selectTreasurer %}
function updateTreasurerOptions(conf, church) {
    const selectedConference = conf || $("#conference").val();
    const selectedChurch = church || $("#church").val();
    const selectedTreasurers = treasurers[selectedConference+selectedChurch] || [];
    $("#treasurer").empty();
    selectedTreasurers.forEach(treasurer => {
        text = treasurer.name
        contactInfo = treasurer.phone && treasurer.email ? treasurer.phone + " - " + treasurer.email : treasurer.phone + treasurer.email;
        text = text && contactInfo ? text + " - " + contactInfo : text + contactInfo;
        $("#treasurer").append($("<option></option>").text(text).val(treasurer.id));
    });
    $("#treasurer").prop('disabled', false);
    if (selectedTreasurers.length == 0) {
        $("#treasurer").append($("<option></option>").text("No Treasurers Found").val(-1));
        $("#treasurer").prop('disabled', true);
    }
}
//{% endif %}

validateInputConference();
//{% if selectTreasurer %}
(function(value) {
    var selectElement = document.getElementById("treasurer");
    for (let i in selectElement.options) {
        if (selectElement.options[i].value == value) {
            selectElement.selectedIndex = i;
            break;
        }
    }
})({{ treasurer.id }});
//{% endif %}
