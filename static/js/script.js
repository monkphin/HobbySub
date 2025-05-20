document.addEventListener('DOMContentLoaded', function () {

  // === Materialize Component Initializations ===
  M.Sidenav.init(document.querySelectorAll('.sidenav'), { edge: 'right' });
  M.Carousel.init(document.querySelectorAll('.carousel'), { duration: 200, dist: -30, shift: 0, padding: 20 });
  M.Modal.init(document.querySelectorAll('.modal'));
  M.Dropdown.init(document.querySelectorAll('.dropdown-trigger'), { coverTrigger: false, constrainWidth: false });
  M.FormSelect.init(document.querySelectorAll('select'));
  M.updateTextFields();

  document.querySelectorAll('.materialize-textarea').forEach(textarea => {
    M.textareaAutoResize(textarea);
  });

// === Materialize Datepicker Initialization ===
M.Datepicker.init(document.querySelectorAll('.datepicker'), {
  format: 'dd/mm/yyyy',      // Ensures it matches '%d/%m/%Y' in Django forms
  autoClose: true,           // Closes the date picker after selection
  showClearBtn: true,        // Allows clearing the date if needed
  firstDay: 1,               // Start the week on Monday
  i18n: {
      cancel: 'Cancel',
      clear: 'Clear',
      done: 'Select',
      months: [
          'January', 'February', 'March', 'April', 'May', 'June', 
          'July', 'August', 'September', 'October', 'November', 'December'
      ],
      monthsShort: [
          'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
      ],
      weekdays: [
          'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'
      ],
      weekdaysShort: [
          'Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'
      ],
      weekdaysAbbrev: ['S', 'M', 'T', 'W', 'T', 'F', 'S']
  }
});

// Form Button Disable on Submit
  document.querySelectorAll('form').forEach(form => {
      form.addEventListener('submit', function (event) {
          const submitButton = form.querySelector('button[type="submit"]');

          if (submitButton) {
              
              // Disable the button and indicate it's processing
              submitButton.disabled = true;
              submitButton.style.opacity = '0.5';

              // If the form fails (redirect, error, or otherwise), re-enable after 3 seconds
              setTimeout(() => {
                  if (submitButton.disabled) {
                      submitButton.disabled = false;
                      submitButton.style.opacity = '1';
                  }
              }, 3000);
          }
      });
  });

  // Toasts
  document.querySelectorAll('.toast').forEach((toast) => {
    toast.addEventListener("click", () => toast.remove());
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(-10px)";
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  });

  // File input display
  document.querySelectorAll('.file-field input[type="file"]').forEach(fileInput => {
    fileInput.addEventListener('change', function () {
      const filePathInput = fileInput.closest('.file-field').querySelector('.file-path');
      if (filePathInput && fileInput.files.length > 0) {
        filePathInput.value = Array.from(fileInput.files).map(f => f.name).join(', ');
        filePathInput.dispatchEvent(new Event('change'));
      }
    });
  });

  // Modal trigger bindings
  document.querySelectorAll('.delete-address-btn').forEach(button => {
    button.addEventListener('click', () => {
      openModal('delete_address', button.dataset.id);
    });
  });

  const modalCancelBtn = document.getElementById('modal-cancel-btn');
  const modalConfirmBtn = document.getElementById('modal-confirm-btn');
  if (modalCancelBtn) modalCancelBtn.addEventListener('click', closeModal);
  if (modalConfirmBtn) modalConfirmBtn.addEventListener('click', submitModalAction);

  const accountDeleteBtn = document.getElementById('delete-account-btn');
  if (accountDeleteBtn) {
    accountDeleteBtn.addEventListener('click', () => openModal('delete_account'));
  }

  // Subscription cancellation button
document.querySelectorAll('.cancel-subscription-btn').forEach(button => {
    button.addEventListener('click', () => {
        const subscriptionId = button.dataset.subscriptionId;       

        if (!subscriptionId) {
            M.toast({ html: "Failed to identify subscription. Please try again.", classes: "red" });
            return;
        }

        openModal('cancel_subscription');
        modalContext.id = subscriptionId;
    });
});


  // === Modal trigger bindings for Box and Product Deletion ===
  document.querySelectorAll('.delete-box-btn').forEach(button => {
    button.addEventListener('click', () => {
      openModal('delete_box', button.dataset.id);
    });
  });

  // Product deletion button
  document.querySelectorAll('.delete-product-btn').forEach(button => {
    button.addEventListener('click', () => {
      const isOrphaned = button.closest('form')?.id === 'orphaned-products-form';

      if (isOrphaned) {
        openModal('delete_single_product', button.dataset.id);  // Pass product ID
      } else {
        openModal('delete_product', button.dataset.id);
      }
    });
  });

  // === Modal trigger bindings for Toggle Active State ===
  document.querySelectorAll('.admin-toggle-state-btn').forEach(button => {
    button.addEventListener('click', () => {
      openModal('admin_toggle_user_state', button.dataset.id);
    });
  });

  // Handle orphaned product action buttons
  document.querySelectorAll('.orphan-action-btn').forEach(button => {
    button.addEventListener('click', function () {
      const action = this.dataset.action;
      setOrphanedAction(action);
    });
  });

  // === Modal trigger binding for Admin Save User ===
  document.querySelectorAll('.admin-update-user-btn').forEach(button => {
    button.addEventListener('click', () => {
      openModal('admin_save_user', button.dataset.id);
    });
  });

  // === Modal trigger for Orphaned Bulk Delete ===
  const orphanedBulkDeleteBtn = document.getElementById('orphaned-bulk-delete-btn');
  if (orphanedBulkDeleteBtn) {
    orphanedBulkDeleteBtn.addEventListener('click', () => {
      const checked = document.querySelectorAll('input[name="product_ids"]:checked');
      if (checked.length === 0) {
        M.toast({ html: 'Please select at least one product to delete.', classes: 'red' });
        return;
      }

      // Set the hidden action field in the form
      setOrphanedAction('delete');

      // Open confirmation modal
      openModal('orphaned_bulk_delete');
    });
  }

  // === Modal trigger bindings for Email Change ===
  const emailChangeBtn = document.getElementById('change-email-btn');
  if (emailChangeBtn) {
    emailChangeBtn.addEventListener('click', openChangeEmailModal);
  }
});

// === Modal trigger bindings for Password Reset ===
document.querySelectorAll('.admin-password-reset-btn').forEach(button => {
  button.addEventListener('click', () => {
    openModal('admin_password_reset', button.dataset.id);
  });
});

let modalContext = {
  action: null,
  id: null,
  newEmail: null,
};

function openModal(action, id = null) {
  modalContext = { action, id, newEmail: null };

  const modal = document.getElementById('confirmation-modal');
  const title = document.getElementById('modal-title');
  const message = document.getElementById('modal-message');
  const warning = document.getElementById('delete-warning');
  const form = document.getElementById('modal-password-form');

  // show form when opening modal
  form.style.display = 'block';

  document.getElementById('modal-password').value = '';
  document.getElementById('modal-error').innerText = '';
  if (warning) warning.innerText = '';

  switch (action) {
    case 'delete_account':
      title.innerText = 'Confirm Account Deletion';
      message.innerText = 'Please enter your password to permanently delete your account.';
      break;
    case 'delete_address':
        title.innerText = 'Confirm Address Deletion';
        
        // Find the parent card that has the class
        const button = document.querySelector(`button[data-id="${id}"]`);
        const addressElement = button.closest('.address-card');

        if (!addressElement) {
            M.toast({ html: "Address not found. Please refresh the page.", classes: "red" });
            closeModal();
            return;
        }

        const isGift = addressElement.classList.contains('gift-address');
        message.innerText = `Please enter your password to delete this ${isGift ? 'gift' : 'personal'} address.`;

        // Specific warning and clarification based on type
        if (!isGift) {
            const addressCards = document.querySelectorAll('.personal-address');
            if (addressCards.length === 1 && warning) {
                warning.innerText = "This is your only personal address. You’ll need to add another before ordering.";
            } else {
                warning.innerText = "This will affect your default delivery options.";
            }
        } else {
            warning.innerText = "This is your only gift order address.";
        }
        break;

    case 'cancel_subscription':
      title.innerText = 'Cancel Subscription';
      message.innerText = 'Please enter your password to cancel your subscription.';
      break;
    case 'change_email':
      title.innerText = 'Confirm Email Change';
      message.innerText = 'Please confirm your password to update your email address.';
      break;
    case 'orphaned_bulk_delete':
      title.innerText = 'Confirm Bulk Deletion';
      message.innerText = 'Please enter your password to delete the selected orphaned products.';
      break;
    case 'delete_single_product':
      title.innerText = 'Confirm Product Deletion';
      message.innerText = 'Please enter your password to delete this orphaned product.';
      break;
    case 'admin_password_reset':
      title.innerText = 'Admin-Initiated Password Reset';
      message.innerText = 'Are you sure you want to send a password reset email to this user?';
      break;
    case 'admin_toggle_user_state':
      title.innerText = 'Toggle User Account State';
      message.innerText = 'Are you sure you want to toggle this user\'s active state?';
      break;
    default:
      title.innerText = 'Confirm Action';
      message.innerText = 'Please enter your password to proceed.';
  }

  const instance = M.Modal.getInstance(modal) || M.Modal.init(modal);
  instance.open();
}

function openChangeEmailModal() {
  const emailInput = document.getElementById('id_email');
  const newEmail = emailInput?.value.trim();

  if (!window.originalEmail) {
    window.originalEmail = emailInput.defaultValue;
  }

  if (!newEmail) {
    M.toast({ html: 'Email cannot be empty.', classes: 'red' });
    return;
  }

  if (newEmail === window.originalEmail) {
    M.toast({ html: 'Email has not changed.', classes: 'red' });
    return;
  }

  openModal('change_email');
  modalContext.newEmail = newEmail;
  }

  function closeModal() {
    const modal = document.getElementById('confirmation-modal');
    const form = document.getElementById('modal-password-form');

    // Hide the form when closing
    form.style.display = 'none';

    const instance = M.Modal.getInstance(modal) || M.Modal.init(modal);
    instance.close();
  }

function submitModalAction() {
  const password = document.getElementById('modal-password').value;
  const errorEl = document.getElementById('modal-error');
  errorEl.innerText = '';

  if (!password) {
    errorEl.innerText = 'Password is required.';
    return;
  }

  let url = '';
  const action = modalContext.action;

  // Initialize payload object
  let payload = {
    password: password
  };

  switch (action) {
    case 'delete_account':
      url = GLOBALS.urls.deleteAccount;
      break;
    case 'delete_address':
      url = `${GLOBALS.urls.deleteAddressBase}${modalContext.id}/`;
      break;
    case 'cancel_subscription':
      url = GLOBALS.urls.cancelSubscription;
      payload.subscription_id = modalContext.id;
      break;
    case 'delete_box':
      url = `/dashboard/box_admin/${modalContext.id}/delete/`;
      break;
    case 'delete_product':
      url = `/dashboard/products/${modalContext.id}/delete/`;
      break;
    case 'admin_password_reset':
      url = `/dashboard/user_admin/password-reset/${modalContext.id}/`;
      break;
    case 'admin_save_user':
      url = `/dashboard/user_admin/${modalContext.id}/edit/`;

      // Collect form data from the page
      const formData = {
        username: document.getElementById('username').value,
        email: document.getElementById('email').value,
        is_staff: document.querySelector('input[name="is_staff"]').checked
      };

      // Merge form data into the main payload
      Object.assign(payload, formData);
      break;
    case 'admin_toggle_user_state':
      url = `/dashboard/user_admin/${modalContext.id}/toggle-state/`;
      break;
    case 'change_email':
      url = GLOBALS.urls.changeEmail;
      payload.new_email = modalContext.newEmail;
      break;

    case 'orphaned_bulk_delete':
      const formEl = document.getElementById('orphaned-products-form');
      const bulkFormData = new FormData(formEl);
      bulkFormData.append('password', password);
      fetch(GLOBALS.urls.orphanedBulkDelete, {
        method: 'POST',
        headers: {
          'X-CSRFToken': GLOBALS.csrfToken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: bulkFormData,
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            window.location.reload();
          } else {
            errorEl.innerText = data.error || 'Failed to delete products.';
          }
        })
        .catch(() => {
          errorEl.innerText = 'Sorry - there was a problem completing your request.';
        });
      return;
    case 'delete_single_product':
      const singleDeleteFormData = new FormData();
      singleDeleteFormData.append('delete_single', modalContext.id);
      singleDeleteFormData.append('password', password);

      fetch(GLOBALS.urls.orphanedBulkDelete, {
        method: 'POST',
        headers: {
          'X-CSRFToken': GLOBALS.csrfToken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: singleDeleteFormData,
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            window.location.reload();
          } else {
            errorEl.innerText = data.error || 'Failed to delete product.';
          }
        })
        .catch(() => {
          errorEl.innerText = 'Sorry — there was a problem completing your request.';
        });
      return;
    }
  
  fetch(url, {
    method: 'POST',
    headers: {
      'X-CSRFToken': GLOBALS.csrfToken,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload),
  })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        if (action === 'delete_account') {
          window.location.href = '/';
        } else {
          window.location.reload();
        }
      } else {
        errorEl.innerText = data.error || 'Failed to complete action.';
      }
    })
    .catch(() => {
      errorEl.innerText = 'Sorry — there was a problem completing your request.';
    });
}

function setOrphanedAction(action) {
  const hiddenField = document.getElementById('orphaned-action');
  if (hiddenField) {
    hiddenField.value = action;
  }
}
