// Actions and Modals Management
document.addEventListener('DOMContentLoaded', function() {
  initializeActions();
  initializeDemoData();
});

function initializeActions() {
  // Location selection
  initializeLocationSelection();
  
  // Modal save handlers
  setupModalHandlers();
  
  // Customer approval handlers
  setupCustomerHandlers();
}

function initializeLocationSelection() {
  document.querySelectorAll('.location-option').forEach(option => {
    option.addEventListener('click', function() {
      document.querySelectorAll('.location-option').forEach(opt => {
        opt.classList.remove('selected');
      });
      this.classList.add('selected');
    });
  });
}

function setupModalHandlers() {
  // Save Location
  document.getElementById('saveLocation').addEventListener('click', function() {
    const selectedLocation = document.querySelector('.location-option.selected');
    if (selectedLocation) {
      const locationName = selectedLocation.querySelector('.location-title').textContent;
      const locationNotes = document.getElementById('locationNotes').value;
      
      // Update UI everywhere
      updateLocationInUI(locationName);
      
      // Add to timeline
      addTimelineUpdate('Repair Location Set', 
        `Repair location updated to ${locationName}. ${locationNotes ? 'Notes: ' + locationNotes : ''}`
      );
      
      bootstrap.Modal.getInstance(document.getElementById('locationModal')).hide();
      showToast('Location updated successfully');
    }
  });

  // Save Cost
  document.getElementById('saveCost').addEventListener('click', function() {
    const description = document.getElementById('costDescription').value;
    const amount = document.getElementById('costAmount').value;
    const category = document.getElementById('costCategory').value;
    
    if (description && amount) {
      addCostItem(description, parseInt(amount), category);
      updateCostSummary();
      bootstrap.Modal.getInstance(document.getElementById('costModal')).hide();
      showToast('Cost added successfully');
      
      // Clear form
      document.getElementById('costDescription').value = '';
      document.getElementById('costAmount').value = '';
    } else {
      alert('Please fill in description and amount');
    }
  });

  // Save Status
  document.getElementById('saveStatus').addEventListener('click', function() {
    const status = document.getElementById('statusSelect').value;
    const message = document.getElementById('statusMessage').value;
    
    addTimelineUpdate(status, message || 'Status updated by technician');
    bootstrap.Modal.getInstance(document.getElementById('statusModal')).hide();
    showToast('Status updated successfully');
    
    // Clear form
    document.getElementById('statusMessage').value = '';
  });

  // Send Quote
  document.getElementById('sendQuote').addEventListener('click', function() {
    const price = document.getElementById('customerPrice').value;
    const message = document.getElementById('quoteMessage').value;
    
    // Update quote status everywhere
    updateQuoteStatusInUI('Sent', price);
    
    // Add to timeline
    addTimelineUpdate('Quote Sent', `Repair quote of ₹${price} sent to customer. ${message}`);
    
    // Switch to customer view
    document.body.classList.add('customer-view');
    document.getElementById('userRole').value = 'customer';
    
    bootstrap.Modal.getInstance(document.getElementById('pricingModal')).hide();
    showToast('Quote sent to customer successfully');
  });
}

function setupCustomerHandlers() {
  document.getElementById('approveCostBtn').addEventListener('click', function() {
    showToast('Thank you! Repair will proceed with your approval.');
    addTimelineUpdate('Cost Approved', 'Customer approved the repair cost estimate');
  });

  document.getElementById('rejectCostBtn').addEventListener('click', function() {
    showToast('We will contact you shortly to discuss the estimate.');
    addTimelineUpdate('Cost Rejected', 'Customer requested changes to the cost estimate');
  });
}

function updateLocationInUI(locationName) {
  // Update header badge
  const headerBadge = document.getElementById('headerLocationBadge');
  headerBadge.innerHTML = `<i class="fas fa-map-marker-alt me-1"></i>${locationName}`;
  
  // Update system info card
  const currentLocation = document.getElementById('currentLocation');
  currentLocation.textContent = locationName;
  
  // Update product location badge if exists
  const productBadge = document.getElementById('productLocationBadge');
  if (productBadge) {
    productBadge.textContent = locationName;
  }
}

function updateQuoteStatusInUI(status, price) {
  // Update header badge
  const quoteBadge = document.getElementById('quoteStatusBadge');
  quoteBadge.innerHTML = `<i class="fas fa-paper-plane me-1"></i>Quote ${status}`;
  quoteBadge.style.display = 'inline-block';
  
  // Update system info card
  const quoteStatus = document.getElementById('currentQuoteStatus');
  quoteStatus.textContent = `${status} (₹${price})`;
  
  // Update customer cost display
  const customerCost = document.querySelector('.customer-cost');
  if (customerCost) {
    customerCost.textContent = `₹${price}`;
  }
}

function addTimelineUpdate(title, description) {
  const timeline = document.getElementById('complaintTimeline');
  const timelineItem = document.createElement('div');
  timelineItem.className = 'timeline-item';
  
  const now = new Date();
  const timeString = now.toLocaleDateString() + ' ' + now.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
  
  timelineItem.innerHTML = `
    <div class="timeline-marker active">
      <i class="fas fa-info"></i>
    </div>
    <div class="timeline-content">
      <div class="timeline-date">${timeString}</div>
      <div class="timeline-title">${title}</div>
      <p class="timeline-description">${description}</p>
    </div>
  `;
  
  timeline.prepend(timelineItem);
}

function addCostItem(description, amount, category) {
  const costHistory = document.getElementById('repairCostHistory');
  const costItem = document.createElement('div');
  costItem.className = 'cost-history-item';
  
  const now = new Date();
  const timeString = now.toLocaleDateString();
  
  costItem.innerHTML = `
    <div class="d-flex justify-content-between align-items-start">
      <div>
        <div class="fw-bold small">${description}</div>
        <div class="text-muted smaller">${timeString} • ${category}</div>
      </div>
      <div class="text-warning fw-bold">₹${amount}</div>
    </div>
  `;
  
  costHistory.prepend(costItem);
}

function updateCostSummary() {
  // This would calculate totals from all cost items
  // For demo, we'll just show a simple update
  const totalCostElement = document.querySelector('.oem-cost');
  if (totalCostElement) {
    totalCostElement.textContent = '₹4,750'; // Updated total
  }
}

function initializeDemoData() {
  // Add initial timeline items
  addTimelineUpdate('Complaint Registered', 'Customer reported connectivity issues with the drone controller');
  addTimelineUpdate('Diagnosis Started', 'Initial assessment of the equipment began at our service center');
  addTimelineUpdate('Parts Ordered', 'Required replacement parts have been ordered from supplier');
  
  // Add initial cost items
  addCostItem('Initial Diagnosis', 500, 'Labor');
  addCostItem('Replacement Motor', 2000, 'Parts');
  addCostItem('Circuit Board Repair', 2000, 'Parts');
}

function showToast(message) {
  // Simple toast notification
  const toast = document.createElement('div');
  toast.className = 'position-fixed bottom-0 end-0 p-3';
  toast.style.zIndex = '9999';
  toast.innerHTML = `
    <div class="toast show align-items-center text-white bg-success border-0" role="alert">
      <div class="d-flex">
        <div class="toast-body">${message}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    </div>
  `;
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.remove();
  }, 3000);
}