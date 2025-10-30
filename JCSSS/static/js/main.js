// Main application controller
document.addEventListener('DOMContentLoaded', function() {
  // Initialize all modules
  initializeApp();
});

function initializeApp() {
  // Load OEM panels
  loadOemPanels();
  
  // Initialize modules after a short delay to ensure DOM is ready
  setTimeout(() => {
    initializeTimelineModule();
    initializeCostsModule();
    initializeLocationModule();
  }, 100);
  
  // Set up role selector
  const roleSelector = document.getElementById('userRole');
  roleSelector.addEventListener('change', handleRoleChange);
  
  // Initialize with customer view
  document.body.className = 'customer-view';
}

function loadOemPanels() {
  const oemPanelsContainer = document.getElementById('oemPanels');
  
  // For static deployment, we'll include the HTML directly
  // In a production environment, you would use fetch() or include server-side
  oemPanelsContainer.innerHTML = `
    <!-- Set Repair Location -->
    <div class="card oem-only">
      <div class="card-header">
        <i class="fas fa-map-marker-alt me-2"></i>Set Repair Location
      </div>
      <div class="card-body">
        <div id="locationSelection">
          <div class="location-option" data-location="oem_site">
            <div class="location-icon">
              <i class="fas fa-warehouse"></i>
            </div>
            <h6 class="mb-1">OEM Site</h6>
            <p class="small text-muted mb-0">Repair will be conducted at our service center</p>
          </div>
          
          <div class="location-option" data-location="virtual_assistance">
            <div class="location-icon">
              <i class="fas fa-desktop"></i>
            </div>
            <h6 class="mb-1">Virtual Assistance</h6>
            <p class="small text-muted mb-0">Remote diagnosis and guidance</p>
          </div>
          
          <div class="location-option" data-location="customer_site">
            <div class="location-icon">
              <i class="fas fa-home"></i>
            </div>
            <h6 class="mb-1">Customer Site</h6>
            <p class="small text-muted mb-0">On-site repair at customer location</p>
          </div>
        </div>
        
        <div class="mb-3">
          <label for="locationRemarks" class="form-label">Location Remarks (Optional)</label>
          <textarea class="form-control" id="locationRemarks" rows="2" placeholder="Add any specific instructions or notes about the location..."></textarea>
        </div>
        
        <div class="d-grid">
          <button type="button" class="btn btn-primary" id="saveLocationBtn">
            <i class="fas fa-save me-2"></i>Save Location
          </button>
        </div>
      </div>
    </div>

    <!-- Update Complaint Status -->
    <div class="card oem-only">
      <div class="card-header">
        <i class="fas fa-edit me-2"></i>Update Complaint Status
      </div>
      <div class="card-body">
        <form id="updateComplaintForm">
          <div class="mb-3">
            <label for="statusName" class="form-label">Status</label>
            <select class="form-select" id="statusName">
              <option value="Diagnosis">Diagnosis</option>
              <option value="Repair">Repair</option>
              <option value="Ready for Dispatch">Ready for Dispatch</option>
              <option value="Closed">Closed</option>
            </select>
          </div>
          <div class="mb-3">
            <label for="statusDesc" class="form-label">Remarks / Description</label>
            <textarea class="form-control" id="statusDesc" rows="3" placeholder="Add remarks or update description..."></textarea>
          </div>
          <div class="mb-3">
            <label for="attachment" class="form-label">Attachment</label>
            <input type="file" class="form-control" id="attachment">
          </div>
          <div class="d-grid">
            <button type="submit" class="btn btn-primary">
              <i class="fas fa-save me-2"></i>Update Status
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Add Repair Cost -->
    <div class="card oem-only">
      <div class="card-header">
        <i class="fas fa-tools me-2"></i>Add Repair Cost
      </div>
      <div class="card-body">
        <form id="repairCostForm">
          <div class="mb-3">
            <label for="repairDescription" class="form-label">Repair Description</label>
            <textarea class="form-control" id="repairDescription" rows="2" placeholder="Describe the repair work..."></textarea>
          </div>
          
          <div class="mb-3">
            <label for="repairCost" class="form-label">Repair Cost (₹)</label>
            <input type="number" class="form-control" id="repairCost" placeholder="0.00" min="0" step="0.01">
          </div>
          
          <div class="mb-3">
            <label for="repairAttachment" class="form-label">Attachment (Optional)</label>
            <input type="file" class="form-control" id="repairAttachment">
          </div>
          
          <div class="d-grid">
            <button type="button" class="btn btn-warning" id="addRepairCostBtn">
              <i class="fas fa-plus-circle me-2"></i>Add Repair Cost
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Set Customer Pricing -->
    <div class="card oem-only">
      <div class="card-header">
        <i class="fas fa-tag me-2"></i>Set Customer Pricing
      </div>
      <div class="card-body">
        <form id="customerPricingForm">
          <div class="mb-3">
            <label for="customerPrice" class="form-label">Total Price to Customer (₹)</label>
            <input type="number" class="form-control" id="customerPrice" placeholder="0.00" min="0" step="0.01">
          </div>
          
          <div class="mb-3">
            <label for="customerInvoice" class="form-label">Invoice Attachment</label>
            <input type="file" class="form-control" id="customerInvoice">
          </div>
          
          <div class="d-grid">
            <button type="button" class="btn btn-success" id="sendToCustomerBtn">
              <i class="fas fa-paper-plane me-2"></i>Send to Customer
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Cost Summary -->
    <div class="card oem-only">
      <div class="card-header">
        <i class="fas fa-chart-bar me-2"></i>Cost Summary
      </div>
      <div class="card-body">
        <div class="cost-breakdown-section">
          <div class="cost-item">
            <span class="cost-label">Total Repair Cost:</span>
            <span class="cost-value oem-cost" id="totalRepairCost">₹0</span>
          </div>
          <div class="cost-item">
            <span class="cost-label">Price to Customer:</span>
            <span class="cost-value customer-cost" id="priceToCustomer">₹0</span>
          </div>
          <div class="profit-loss" id="profitLossIndicator">
            <!-- Profit/Loss indicator will be shown here -->
          </div>
        </div>
        
        <!-- Repair Cost History -->
        <div class="mt-3">
          <h6 class="mb-2">Repair Cost History</h6>
          <div class="repair-cost-history" id="repairCostHistory">
            <!-- Repair cost history items will be added here -->
          </div>
        </div>
      </div>
    </div>
  `;
}

function handleRoleChange(event) {
  const selectedRole = event.target.value;
  document.body.className = selectedRole + '-view';
  
  // Update customer view when switching to customer
  if (selectedRole === 'customer') {
    updateCustomerView();
  }
}

function updateCustomerView() {
  const customerTotalCostElement = document.getElementById('customerTotalCost');
  const invoiceLink = document.getElementById('customerInvoiceLink');
  const approveCostBtn = document.getElementById('approveCostBtn');
  const rejectCostBtn = document.getElementById('rejectCostBtn');
  
  if (customerTotalCostElement) {
    customerTotalCostElement.textContent = `₹${window.customerPrice || 0}`;
  }
  
  // Show/hide elements based on whether price is sent
  if (window.isCustomerPriceSent) {
    if (invoiceLink) invoiceLink.style.display = 'inline-flex';
    if (approveCostBtn) approveCostBtn.style.display = 'block';
    if (rejectCostBtn) rejectCostBtn.style.display = 'block';
  } else {
    if (invoiceLink) invoiceLink.style.display = 'none';
    if (approveCostBtn) approveCostBtn.style.display = 'none';
    if (rejectCostBtn) rejectCostBtn.style.display = 'none';
  }
}

// Export functions for other modules
window.updateCustomerView = updateCustomerView;
window.loadOemPanels = loadOemPanels;