// ── Finio JS ──

function openModal(id) {
  const overlay = document.getElementById(id);
  if (overlay) {
    overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
}

function closeModal(id) {
  const overlay = document.getElementById(id);
  if (overlay) {
    overlay.classList.remove('open');
    document.body.style.overflow = '';
  }
}

// Close modal on overlay click
document.addEventListener('click', function(e) {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
    document.body.style.overflow = '';
  }
});

// Close on Escape key
document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') {
    document.querySelectorAll('.modal-overlay.open').forEach(m => {
      m.classList.remove('open');
    });
    document.body.style.overflow = '';
  }
});

// Auto-dismiss messages
setTimeout(() => {
  document.querySelectorAll('.message').forEach(m => {
    m.style.opacity = '0';
    m.style.transition = 'opacity 0.5s';
    setTimeout(() => m.remove(), 500);
  });
}, 5000);

// ── Plaid Link ──
function connectBank() {
  fetch('/get-link-token/')
    .then(r => r.json())
    .then(data => {
      if (data.error) {
        alert('Plaid not configured: ' + data.error);
        return;
      }
      const handler = Plaid.create({
        token: data.link_token,
        onSuccess: function(public_token, metadata) {
          const institution = metadata.institution ? metadata.institution.name : 'Unknown Bank';
          fetch('/exchange-token/', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ public_token, institution_name: institution }),
          })
          .then(r => r.json())
          .then(res => {
            if (res.success) {
              window.location.href = '/sync/';
            } else {
              alert('Error: ' + (res.error || 'Unknown error'));
            }
          });
        },
        onExit: function(err) {
          if (err) console.error('Plaid exit error:', err);
        },
      });
      handler.open();
    })
    .catch(err => {
      console.error('Link token error:', err);
      alert('Could not connect to Plaid. Check your API keys in Settings.');
    });
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Load Plaid Link script dynamically
function loadPlaid() {
  if (!window.Plaid) {
    const s = document.createElement('script');
    s.src = 'https://cdn.plaid.com/link/v2/stable/link-initialize.js';
    document.head.appendChild(s);
  }
}
loadPlaid();
