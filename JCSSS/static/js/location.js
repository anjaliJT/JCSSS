document.addEventListener("DOMContentLoaded", function () {

    const BASE_PATH = "/csm";

    const locationForm = document.getElementById("locationForm");
    const locationOptions = document.querySelectorAll(".location-option");
    const selectedLocationInput = document.getElementById("selectedLocation");
    const locationDataInput = document.getElementById("locationData");
    const enableEditBtn = document.getElementById("enableEditBtn");

    // 🔹 Get existing location (edit case)
    const existingLocation = locationDataInput?.value?.trim();
    const locationAlreadySet =
        existingLocation && existingLocation !== "None" && existingLocation !== "";

    console.log("Existing Location:", existingLocation || "none");

    /* --------------------------------------------------
       1️⃣ Preselect existing location
    -------------------------------------------------- */
    if (locationAlreadySet) {
        locationOptions.forEach(option => {
            if (option.dataset.location === existingLocation) {
                option.classList.add("selected", "border-primary", "bg-light");
                selectedLocationInput.value = existingLocation;
            }
        });
    }

    /* --------------------------------------------------
       2️⃣ Handle location selection (click)
    -------------------------------------------------- */
    locationOptions.forEach(option => {
        option.addEventListener("click", function () {
            if (this.classList.contains("disabled")) return;

            locationOptions.forEach(o =>
                o.classList.remove("selected", "border-primary", "bg-light")
            );

            this.classList.add("selected", "border-primary", "bg-light");
            selectedLocationInput.value = this.dataset.location;

            console.log("Selected Location:", selectedLocationInput.value);
        });
    });

    /* --------------------------------------------------
       3️⃣ Enable / Disable form logic
    -------------------------------------------------- */
    function toggleForm(disabled = true) {
        const inputs = locationForm.querySelectorAll("input, select, textarea, button");
        inputs.forEach(el => {
            if (el.id !== "enableEditBtn") {
                el.disabled = disabled;
            }
        });
    }

    if (locationAlreadySet) {
        toggleForm(true);
        if (enableEditBtn) enableEditBtn.style.display = "inline-block";
    } else {
        toggleForm(false);
        if (enableEditBtn) enableEditBtn.style.display = "none";
    }

    /* --------------------------------------------------
       4️⃣ Enable edit on button click
    -------------------------------------------------- */
    if (enableEditBtn) {
        enableEditBtn.addEventListener("click", function () {
            toggleForm(false);
            enableEditBtn.style.display = "none";
            console.log("Editing enabled.");
        });
    }

    /* --------------------------------------------------
       5️⃣ Handle form submission
    -------------------------------------------------- */
    locationForm.addEventListener("submit", function (e) {
        console.log("Submitting form...");
        console.log("Selected location:", selectedLocationInput.value);

        if (!selectedLocationInput.value) {
            alert("Please select a location before saving.");
            e.preventDefault();
            return;
        }

        // ⚠️ eventId must exist in template if used
        // <input type="hidden" id="eventId" value="{{ event.id }}">

        const eventIdInput = document.getElementById("eventId");
        const eventId = eventIdInput ? eventIdInput.value : null;

        locationForm.addEventListener("submit", function (e) {
    if (!selectedLocationInput.value) {
        alert("Please select a location before saving.");
        e.preventDefault();
        return;
    }
    // ✅ Let Django handle the action
});

        console.log("Form action set to:", newAction);
    });

});