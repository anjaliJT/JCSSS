document.addEventListener("DOMContentLoaded", function () {
  const editButtons = document.querySelectorAll('[data-bs-target="#editStatusModal"]');
  const form = document.getElementById('updateStatusForm');
  const statusSelect = document.getElementById('statusSelect');
  const remarksInput = document.getElementById('remarksInput');
  const hiddenStatusId = document.getElementById('statusId');
  const saveBtn = document.getElementById('saveEditBtn');

  editButtons.forEach(button => {
    button.addEventListener('click', function () {
      const statusId = this.dataset.statusId;
      const currentStatus = this.dataset.status?.trim();
      const currentRemarks = this.dataset.remarks || "";

      form.action = `/csm/complaint/${statusId}/edit-status/`;
      hiddenStatusId.value = statusId;
      remarksInput.value = currentRemarks;

      let matched = false;
      for (let option of statusSelect.options) {
        if (
          option.text.trim().toUpperCase() === currentStatus.toUpperCase() ||
          option.value.trim().toUpperCase() === currentStatus.toUpperCase()
        ) {
          option.selected = true;
          matched = true;
          break;
        }
      }

      if (!matched) {
        statusSelect.selectedIndex = 0;
      }
    });
  });

  // ---------- Confirmation behaviour (uses centralized openPopup) ----------
  if (!form) return; // nothing to do if form not present

  // Helper to actually submit with protection
  function submitStatusForm(triggeringBtn) {
    // Double-submit protection
    if (form.dataset.submitted === "true") return;

    // Mark as submitted so subsequent submit handlers won't re-open popup
    form.dataset.submitted = "true";

    // disable button to give visual feedback (if provided)
    if (triggeringBtn) triggeringBtn.disabled = true;

    // finally submit
    form.submit();
  }

  // Save button click -> show confirmation popup
  if (saveBtn) {
    saveBtn.addEventListener("click", function (e) {
      e.preventDefault();
      const btn = e.currentTarget || e.target;

      // If already disabled or already submitted, skip
      if (btn.disabled || form.dataset.submitted === "true") return;

      openPopup("Are you sure you want to save changes?", function () {
        submitStatusForm(btn);
      });
    });
  }

  // Also catch the form's submit event (so Enter key works inside modal)
  form.addEventListener("submit", function (e) {
    // If already submitted, allow native submit to proceed
    if (form.dataset.submitted === "true") return;

    // Prevent default and show confirmation instead
    e.preventDefault();

    openPopup("Are you sure you want to save changes?", function () {
      submitStatusForm(saveBtn || null);
    });
  });
});
