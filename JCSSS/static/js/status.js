document.addEventListener("DOMContentLoaded", function () {
  const editButtons = document.querySelectorAll('[data-bs-target="#editStatusModal"]');
  const form = document.getElementById('updateStatusForm');
  const statusSelect = document.getElementById('statusSelect');
  const remarksInput = document.getElementById('remarksInput');
  const hiddenStatusId = document.getElementById('statusId');
  const saveBtn = document.getElementById('saveEditBtn'); // <-- NEW

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

  // ✅ Confirmation popup for Save button
  saveBtn.addEventListener("click", function () {
    openPopup("Are you sure you want to save changes?", function () {
      form.submit();
    });
  });
});
