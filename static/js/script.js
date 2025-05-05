document.addEventListener('DOMContentLoaded', function () {
  // === Materialize Component Initializations ===
  M.Sidenav.init(document.querySelectorAll('.sidenav'), { edge: 'right' });
  M.Carousel.init(document.querySelectorAll('.carousel'), { duration: 200, dist: -30, shift: 0, padding: 20 });
  M.Modal.init(document.querySelectorAll('.modal'));
  M.Datepicker.init(document.querySelectorAll('.datepicker'), { format: 'dd/mm/yyyy' });
  M.Dropdown.init(document.querySelectorAll('.dropdown-trigger'), { coverTrigger: false, constrainWidth: false });
  M.FormSelect.init(document.querySelectorAll('select'));
  M.updateTextFields();

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

  document.querySelectorAll('.cancel-subscription-btn').forEach(button => {
    button.addEventListener('click', () => openModal('cancel_subscription'));
  });

  const emailChangeBtn = document.getElementById('change-email-btn');
  if (emailChangeBtn) {
    emailChangeBtn.addEventListener('click', openChangeEmailModal);
  }
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
      message.innerText = 'Please enter your password to delete this saved address.';
      const addressCards = document.querySelectorAll('.personal-address');
      if (addressCards.length === 1 && warning) {
        warning.innerText = "This is your only address. You’ll need to add another before ordering.";
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
  const instance = M.Modal.getInstance(modal);
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

  switch (action) {
    case 'delete_account':
      url = GLOBALS.urls.deleteAccount;
      break;
    case 'delete_address':
      url = `${GLOBALS.urls.deleteAddressBase}${modalContext.id}/`;
      break;
    case 'cancel_subscription':
      url = GLOBALS.urls.cancelSubscription;
      break;
    case 'change_email':
      url = GLOBALS.urls.changeEmail;
      break;
    default:
      errorEl.innerText = 'Invalid action.';
      return;
  }

  const payload = { password };
  if (action === 'change_email') {
    payload.new_email = modalContext.newEmail;
  }

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': GLOBALS.csrfToken,
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
    .catch(err => {
      errorEl.innerText = 'Sorry — there was a problem completing your request.';
    });
}
