// Costs management module
let repairCosts = [];
let customerPrice = 0;
let isCustomerPriceSent = false;

function initializeCostsModule() {
  // Wait for DOM to be ready
  setTimeout(() => {
    setupCostButtons();
    updateCostSummary();
    updateRepairCostHistory();
    setupCustomerApproval();
  }, 300);
}

function setupCostButtons() {
  const addRepairCostBtn = document.getElementById('addRepairCostBtn');
  const sendToCustomerBtn = document.getElementById('sendToCustomerBtn');
  
  if (addRepairCostBtn) {
    addRepairCostBtn.addEventListener('click', addRepairCost);
  }
  
  if (sendToCustomerBtn) {
    sendToCustomerBtn.addEventListener('click', sendToCustomer);
  }
}

function addRepairCost() {
  const description = document.getElementById('repairDescription').value;
  const cost = parseFloat(document.getElementById('repairCost').value) || 0;
  const attachment = document.getElementById('repairAttachment').files[0];
  
  if (!description || cost === 0) {
    alert('Please enter description and cost value.');
    return;
  }
  
  const repairCost = {
    id: Date.now(),
    description: description,
    cost: cost,
    attachment: attachment,
    date: new Date().toLocaleDateString()
  };
  
  repairCosts.push(repairCost);
  updateCostSummary();
  updateRepairCostHistory();
  clearRepairCostForm();
  
  alert('Repair cost added successfully!');
}

function sendToCustomer() {
  const customerPriceValue = parseFloat(document.getElementById('customerPrice').value) || 0;
  const invoice = document.getElementById('customerInvoice').files[0];
  
  if (customerPriceValue === 0) {
    alert('Please enter a valid price for the customer.');
    return;
  }
  
  if (!invoice) {
    alert('Please attach an invoice for the customer.');
    return;
  }
  
  customerPrice = customerPriceValue;
  isCustomerPriceSent = true;
  updateCostSummary();
  
  // Clear form
  document.getElementById('customerPrice').value = '';
  document.getElementById('customerInvoice').value = '';
  
  // Switch to customer view
  document.getElementById('userRole').value = 'customer';
  document.body.className = 'customer-view';
  if (window.updateCustomerView) {
    window.updateCustomerView();
  }
  
  alert('Price estimate has been sent to the customer!');
}

function updateCostSummary() {
  const totalRepairCost = repairCosts.reduce((sum, item) => sum + item.cost, 0);
  const totalRepairCostElement = document.getElementById('totalRepairCost');
  const priceToCustomerElement = document.getElementById('priceToCustomer');
  const customerTotalCostElement = document.getElementById('customerTotalCost');
  const profitLossIndicator = document.getElementById('profitLossIndicator');
  
  if (totalRepairCostElement) {
    totalRepairCostElement.textContent = `₹${totalRepairCost.toFixed(2)}`;
  }
  
  if (priceToCustomerElement) {
    priceToCustomerElement.textContent = `₹${customerPrice.toFixed(2)}`;
  }
  
  if (customerTotalCostElement) {
    customerTotalCostElement.textContent = `₹${customerPrice.toFixed(2)}`;
  }
  
  // Update profit/loss indicator
  if (profitLossIndicator) {
    const profitLoss = customerPrice - totalRepairCost;
    profitLossIndicator.innerHTML = '';
    
    if (profitLoss > 0) {
      profitLossIndicator.className = 'profit-loss profit';
      profitLossIndicator.textContent = `Profit: ₹${profitLoss.toFixed(2)}`;
    } else if (profitLoss < 0) {
      profitLossIndicator.className = 'profit-loss loss';
      profitLossIndicator.textContent = `Loss: ₹${Math.abs(profitLoss).toFixed(2)}`;
    } else {
      profitLossIndicator.className = 'profit-loss';
      profitLossIndicator.textContent = 'Break Even';
    }
  }
}

function updateRepairCostHistory() {
  const repairCostHistory = document.getElementById('repairCostHistory');
  if (!repairCostHistory) return;
  
  repairCostHistory.innerHTML = '';
  
  if (repairCosts.length === 0) {
    repairCostHistory.innerHTML = '<div class="text-muted text-center">No repair costs added yet</div>';
    return;
  }
  
  repairCosts.forEach(cost => {
    const costItem = document.createElement('div');
    costItem.className = 'cost-history-item';
    costItem.innerHTML = `
      <div class="d-flex justify-content-between align-items-start">
        <div>
          <div class="fw-bold small">${cost.description}</div>
          <div class="text-muted smaller">${cost.date}</div>
          ${cost.attachment ? 
            `<a href="#" class="attachment-link smaller">
              <i class="fas fa-paperclip me-1"></i>Attachment
            </a>` : ''
          }
        </div>
        <div class="text-warning fw-bold">₹${cost.cost.toFixed(2)}</div>
      </div>
    `;
    repairCostHistory.appendChild(costItem);
  });
}

function clearRepairCostForm() {
  document.getElementById('repairDescription').value = '';
  document.getElementById('repairCost').value = '';
  document.getElementById('repairAttachment').value = '';
}

function setupCustomerApproval() {
  const approveCostBtn = document.getElementById('approveCostBtn');
  const rejectCostBtn = document.getElementById('rejectCostBtn');
  
  if (approveCostBtn) {
    approveCostBtn.addEventListener('click', function() {
      alert('Thank you for approving the cost estimate. Repair will now proceed.');
    });
  }
  
  if (rejectCostBtn) {
    rejectCostBtn.addEventListener('click', function() {
      alert('Cost estimate has been rejected. Our team will contact you shortly.');
    });
  }
}

// Export variables and functions for other modules
window.repairCosts = repairCosts;
window.customerPrice = customerPrice;
window.isCustomerPriceSent = isCustomerPriceSent;
window.updateCostSummary = updateCostSummary;