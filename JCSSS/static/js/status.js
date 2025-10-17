document.addEventListener("DOMContentLoaded", function () {
  const editButtons = document.querySelectorAll('[data-bs-target="#editStatusModal"]');
  const form = document.getElementById('updateStatusForm');
  const statusSelect = document.getElementById('statusSelect');
  const remarksInput = document.getElementById('remarksInput');
  const hiddenStatusId = document.getElementById('statusId');

  editButtons.forEach(button => {
    button.addEventListener('click', function () {
      const statusId = this.dataset.statusId;
      const currentStatus = this.dataset.status?.trim();
      const currentRemarks = this.dataset.remarks || "";

      // Dynamically set the form action
      form.action = `/csm/complaint/${statusId}/edit-status/`;

      // Update hidden input
      hiddenStatusId.value = statusId;

      // Fill remarks
      remarksInput.value = currentRemarks;

      // Select the correct status option
      let matched = false;
      for (let option of statusSelect.options) {
        if (option.text.trim().toUpperCase() === currentStatus.toUpperCase() ||
            option.value.trim().toUpperCase() === currentStatus.toUpperCase()) {
          option.selected = true;
          matched = true;
          break;
        }
      }

      if (!matched) {
        statusSelect.selectedIndex = 0; // fallback
      }
    });
  });
});