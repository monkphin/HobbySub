document.addEventListener('DOMContentLoaded', function () {

  // === Materialize initializations ===
  M.Sidenav.init(document.querySelectorAll('.sidenav'), { edge: 'right' });
  M.Carousel.init(document.querySelectorAll('.carousel'), { duration: 200, dist: -30, shift: 0, padding: 20 });
  M.Modal.init(document.querySelectorAll('.modal'));
  M.Datepicker.init(document.querySelectorAll('.datepicker'), { format: 'dd/mm/yyyy' });
  M.Dropdown.init(document.querySelectorAll('.dropdown-trigger'), { coverTrigger: false, constrainWidth: false });
  M.FormSelect.init(document.querySelectorAll('select'));
  M.updateTextFields();

  // === Toast auto-remove ===
  const toasts = document.querySelectorAll('.toast');
  toasts.forEach(toast => {
    toast.addEventListener("click", () => toast.remove());
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(-10px)";
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  });

  // === File input display fix ===
  document.querySelectorAll('.file-field input[type="file"]').forEach(fileInput => {
    fileInput.addEventListener('change', () => {
      const filePathInput = fileInput.closest('.file-field').querySelector('.file-path');
      if (filePathInput && fileInput.files.length > 0) {
        filePathInput.value = Array.from(fileInput.files).map(f => f.name).join(', ');
        filePathInput.dispatchEvent(new Event('change'));
      }
    });
  });
});

// === Modal context tracking ===
let modalContext = {
  action: null,
  id: null,
};

// === Open confirmation modal ===
function openModal(action, id = null) {
  modalContext.action = action;
  modalContext.id = id;

  const modal = document.getElementById('confirmation-modal');
  const title = document.getElementById('modal-title');
  const message = document.getElementById('modal-message');
  document.getElementById('modal-password').value = '';
  document.getElementById('modal-error').innerText = '';

  switch (action) {
    case 'delete_account':
      title.innerText = 'Confirm Account Deletion';
      message.innerText = 'Please enter your password to permanently delete your account.';
      break;
    case 'delete_address':
      title.innerText = 'Confirm Address Deletion';
      message.innerText = 'Please enter your password to delete this saved address.';
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

// === Close modal ===
function closeModal() {
  const modal = document.getElementById('confirmation-modal');
  const instance = M.Modal.getInstance(modal);
  instance.close();
}

// == Change Email Confirmation modal
function openChangeEmailModal() {
  const emailInput = document.getElementById('id_email');
  const newEmail = emailInput?.value.trim();

  // ✅ Set originalEmail now (not too early)
  if (!window.originalEmail) {
    window.originalEmail = emailInput.defaultValue;
  }

  console.log("Original:", window.originalEmail);
  console.log("Typed:", newEmail);

  if (!newEmail) {
    M.toast({ html: 'Email cannot be empty.', classes: 'red' });
    return;
  }

  if (newEmail === window.originalEmail) {
    M.toast({ html: 'Email has not changed.', classes: 'red' });
    return;
  }

  modalContext.action = 'change_email';
  modalContext.newEmail = newEmail;

  // Set modal contents
  document.getElementById('modal-title').innerText = 'Confirm Email Change';
  document.getElementById('modal-message').innerText = 'Enter your password to confirm.';
  document.getElementById('modal-password').value = '';
  document.getElementById('modal-error').innerText = '';

  const modal = document.getElementById('confirmation-modal');
  const instance = M.Modal.getInstance(modal) || M.Modal.init(modal);
  instance.open();
}

// === Submit modal action ===
function submitModalAction() {
  const password = document.getElementById('modal-password').value;
  let url = '';

  switch (modalContext.action) {
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
      url = GLOBALS.urls.changeEmail;  // Optional future use
      break;
    default:
      console.error("Unknown action:", modalContext.action);
      return;
  }

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': GLOBALS.csrfToken,
    },
    body: JSON.stringify(
      modalContext.action === 'change_email'
        ? { password, new_email: modalContext.newEmail }
        : { password }
    ),
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        if (modalContext.action === 'delete_account') {
          window.location.href = '/';
        } else {
          window.location.reload();
        }
      } else {
        document.getElementById('modal-error').innerText = data.error;
      }
    })
    .catch(err => {
      console.error('Request failed:', err);
      document.getElementById('modal-error').innerText = 'Something went wrong.';
    });
}