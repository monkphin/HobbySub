document.addEventListener('DOMContentLoaded', function () {
  // SideNav
  const sidenav = document.querySelectorAll('.sidenav');
  M.Sidenav.init(sidenav, {
      edge: 'right'
  });


  // Carousel
  const carouselElems = document.querySelectorAll('.carousel');
  M.Carousel.init(carouselElems, {
    duration: 200,
    dist: -30,
    shift: 0,
    padding: 20
  });

  // Modals
  const modalElems = document.querySelectorAll('.modal');
  M.Modal.init(modalElems);

  // Datepicker
  const dateElems = document.querySelectorAll('.datepicker');
  M.Datepicker.init(dateElems, {
    format: 'dd/mm/yyyy'
  });

  // Dropdowns
  const dropdowns = document.querySelectorAll('.dropdown-trigger');
  M.Dropdown.init(dropdowns, {
    coverTrigger: false,
    constrainWidth: false
  });

  // Materialize Selects
  M.FormSelect.init(document.querySelectorAll('select'));

  // Update floating labels
  M.updateTextFields();

  // Toasts
  const toasts = document.querySelectorAll('.toast');
  toasts.forEach((toast) => {
    toast.addEventListener("click", () => toast.remove());
    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(-10px)";
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  });

  // File input filename fix
  const fileInputs = document.querySelectorAll('.file-field input[type="file"]');
  fileInputs.forEach(fileInput => {
    fileInput.addEventListener('change', function () {
      const filePathInput = fileInput.closest('.file-field').querySelector('.file-path');
      if (filePathInput && fileInput.files.length > 0) {
        filePathInput.value = Array.from(fileInput.files).map(f => f.name).join(', ');
        filePathInput.dispatchEvent(new Event('change'));
      }
    });
  });
});


let deleteType = null;
let deleteId = null;

function openDeleteModal(type, id = null) {
  deleteType = type;
  deleteId = id;
  const modal = document.getElementById('delete-modal');
  document.getElementById('delete-password').value = '';
  document.getElementById('delete-error').innerText = '';

  document.getElementById('delete-password').addEventListener('input', () => {
    document.getElementById('delete-error').innerText = '';
  }, { once: true });

  if (type === 'account') {
    document.getElementById('delete-modal-title').innerText = 'Confirm Account Deletion';
  } else if (type === 'address') {
    document.getElementById('delete-modal-title').innerText = 'Confirm Address Deletion';
  } else if (type === 'subscription') {
    document.getElementById('delete-modal-title').innerText = 'Confirm Subscription Cancellation';
  }
  const instance = M.Modal.getInstance(modal) || M.Modal.init(modal);
  instance.open();

  if (deleteType === 'address') {
    const addressCards = document.querySelectorAll('.personal-address');
    if (addressCards.length === 1) {
      document.getElementById('delete-warning').innerText = "This is your only address. You’ll need to add another before ordering.";
    } else {
      document.getElementById('delete-warning').innerText = "";
    }
  }
}

function closeDeleteModal() {
  const modal = document.getElementById('delete-modal');
  const instance = M.Modal.getInstance(modal);
  instance.close();
}

function submitDelete() {
  const password = document.getElementById('delete-password').value.trim();
  const errorBox = document.getElementById('delete-error');

  if (!password) {
    errorBox.innerText = "Password is required.";
    return;
  }
  let url = '';

  if (deleteType === 'account') {
    url = GLOBALS.urls.deleteAccount;
  } else if (deleteType === 'address') {
    url = GLOBALS.urls.deleteAddressBase + deleteId + '/';
  } else if (deleteType === 'subscription') {
    url = GLOBALS.urls.cancelSubscription;
  }

  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': GLOBALS.csrfToken,
    },
    body: JSON.stringify({ password: password }),
  })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        if (deleteType === 'account') {
          window.location.href = '/'; // Redirect home
        } else {
          window.location.reload(); // Reload page
        }
      } else {
        document.getElementById('delete-error').innerText = data.error;
      }
    })
    .catch(error => {
      console.error('Error:', error);
      document.getElementById('delete-error').innerText = "Something went wrong.";
    });
}
