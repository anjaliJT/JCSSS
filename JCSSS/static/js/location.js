document.addEventListener("DOMContentLoaded", function() {
  const locationOptions = document.querySelectorAll(".location-option");
  const selectedLocationInput = document.getElementById("selectedLocation");
  const locationFormHide = document.getElementById("locationFormHide");
  const locationDataInput = document.getElementById("locationData");

  console.log("locationDataInput:", locationDataInput ? locationDataInput.value : "not found");
  console.log("locationFormHide:", locationFormHide ? "found" : "not found");

  


  // Handle location selection
  locationOptions.forEach(option => {
    option.addEventListener("click", function() {
      locationOptions.forEach(o => o.classList.remove("border-primary", "bg-light"));
      this.classList.add("border-primary", "bg-light");
      selectedLocationInput.value = this.dataset.location;
    });
  });

  // Prevent submit if no location selected
  locationFormHide.addEventListener("submit", function(e) {
    if (!selectedLocationInput.value) {
      alert("Please select a location before saving.");
      e.preventDefault();
    }
  });

  // Hide form if location already exists
const locationData = locationDataInput ? locationDataInput.value : "";
  if (locationData && locationFormHide) {
    console.log("Hiding form because locationData =", locationData);
    locationFormHide.style.display = "none";
  }
});
