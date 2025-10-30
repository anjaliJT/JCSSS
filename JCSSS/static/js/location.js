document.addEventListener("DOMContentLoaded", function () {
  const BASE_PATH = "/csm";
  const locationForm = document.getElementById("locationForm");
  const locationOptions = document.querySelectorAll(".location-option");
  const selectedLocationInput = document.getElementById("selectedLocation");
  const locationDataInput = document.getElementById("locationData");
  const enableEditBtn = document.getElementById("enableEditBtn");
  // const eventId = document.getElementById("eventId").value;

  const existingLocationId = locationDataInput?.value?.trim();
  const locationAlreadySet = existingLocationId && existingLocationId !== "None" && existingLocationId !== "";

  console.log("Existing Location ID:", existingLocationId || "none");

  // Handle location selection
  locationOptions.forEach(option => {
    option.addEventListener("click", function () {
      if (this.classList.contains("disabled")) return;
      locationOptions.forEach(o => o.classList.remove("border-primary", "bg-light"));
      this.classList.add("border-primary", "bg-light");
      selectedLocationInput.value = this.dataset.location;
      console.log("Selected Location:", selectedLocationInput.value);
    });
  });

  // Handle form submission
  locationForm.addEventListener("submit", function (e) {
    console.log("Submitting form...");
  console.log("Selected location before submit:", selectedLocationInput.value);
    if (!selectedLocationInput.value) {
      alert("Please select a location before saving.");
      e.preventDefault();
      return;
    }

    const newAction = locationAlreadySet
      ? `${BASE_PATH}/complaint/${existingLocationId}/update-location/`
      : `${BASE_PATH}/complaint/${eventId}/set-location/`;

    locationForm.action = newAction;
    console.log("Form submitting to:", newAction);
  });

  // Disable form if location already exists
  function toggleForm(disabled = true) {
    const inputs = locationForm.querySelectorAll("input, select, textarea, button");
    inputs.forEach(el => {
      if (el.id !== "enableEditBtn") el.disabled = disabled;
    });
  }

  if (locationAlreadySet) {
    console.log("Form disabled (existing location).");
    toggleForm(true);
    enableEditBtn.style.display = "inline-block";
  } else {
    toggleForm(false);
    enableEditBtn.style.display = "none";
  }

  // Enable form when "Change Location" clicked
  enableEditBtn.addEventListener("click", function () {
    toggleForm(false);
    enableEditBtn.style.display = "none";
    console.log("Editing enabled.");
  });
});
