document.addEventListener("DOMContentLoaded", function () {
  const editBtn = document.getElementById("enableEditCost");
  const form = document.getElementById("customerPricingForm");

  if (editBtn && form) {
    editBtn.addEventListener("click", function () {
      // Only select form inputs, not buttons
      const inputs = form.querySelectorAll("input:not([type='hidden']), select, textarea");
      const submitBtn = form.querySelector("button[type='submit']");
      
      // Check current disabled state based on the first input
      const currentlyDisabled = inputs.length > 0 ? inputs[0].disabled : false;

      // Toggle inputs
      inputs.forEach(el => {
        el.disabled = !currentlyDisabled;
      });

      // Toggle submit button separately
      if (submitBtn) submitBtn.disabled = !currentlyDisabled;

      // Update edit button icon + color
      if (currentlyDisabled) {
        editBtn.innerHTML = '<i class="fas fa-times"></i>';
        editBtn.classList.remove("btn-outline-primary");
        editBtn.classList.add("btn-outline-danger");
      } else {
        editBtn.innerHTML = '<i class="fas fa-edit"></i>';
        editBtn.classList.remove("btn-outline-danger");
        editBtn.classList.add("btn-outline-primary");
      }
    });
  }
});
