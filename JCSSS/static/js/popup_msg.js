  function handleConfirmation(event, options) {
    event.preventDefault();

    const btn = event.target;

    // If element is disabled, skip
    if (btn.disabled) return;

    const message = options.message || "Are you sure?";

    openPopup(message, function () {

      // If formId exists → submit form
      if (options.formId) {
        const form = document.getElementById(options.formId);

        if (!form.dataset.submitted) {
          form.dataset.submitted = "true";
          form.submit();
        }
        return;
      }

      // If redirect URL exists → navigate
      if (options.redirectUrl) {
        window.location.href = options.redirectUrl;
        return;
      }
    });
  }

  // ----------- Wrapper functions -----------

  function addCustomerCost(event) {
    handleConfirmation(event, {
      message: "Are you sure you want to add Customer cost?",
      formId: "customerPricingForm"
    });
  }

  function addRepairCost(event) {
    handleConfirmation(event, {
      message: "Are you sure you want to add repair cost?",
      formId: "addRepairCostForm"
    });
  }

  function statusEdit(event) {
    handleConfirmation(event, {
      message: "Are you sure you want to update status?",
      formId: "updateStatus"
    });
  }

  function deleteRepairCost(event) {
    handleConfirmation(event, {
      message: "Are you sure you want to delete this cost?",
      formId: "deleteRepairCost"
    });
  }

  // NEW → Link / redirect confirmation
  // function complainNavigation(event, targetUrl) {
  //   handleConfirmation(event, {
  //     message: "Are you sure you want to create a new Complaint?",
  //     redirectUrl: targetUrl
  //   });
  // }
  // user management
  function userNavigation(event, targetUrl) {
    handleConfirmation(event, {
        message: "Are you sure you want to create a new User?",
        redirectUrl: targetUrl
      });
    }
  
    function userEditNavigation(event, targetUrl) {
    handleConfirmation(event, {
        message: "Are you sure you want to edit details?",
        redirectUrl: targetUrl
      });
    }


  // create OEM 
//   function confirmFormSubmit(event) {
//     handleConfirmation(event, {
//       message: "Are you sure you want to update user details?",
//       formId: "createUserForm"
//     });
// }
