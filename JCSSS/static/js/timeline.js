// Timeline management module
let timelineUpdates = [];

const initialTimeline = [
  { date: '16/02/2025', title: 'Registration Complete', description: 'Complaint registered in the system and assigned to service team.', status: 'completed', attachments: [] },
  { date: '17/02/2025', title: 'Diagnosis In Progress', description: 'Technicians are currently diagnosing the issue with the equipment.', status: 'active', attachments: [] }
];

function initializeTimelineModule() {
  // Wait a bit for DOM to be fully loaded
  setTimeout(() => {
    initializeTimeline();
    setupComplaintForm();
  }, 200);
}

function initializeTimeline() {
  const complaintTimeline = document.getElementById('complaintTimeline');
  if (!complaintTimeline) {
    console.error('Timeline container not found');
    return;
  }
  
  complaintTimeline.innerHTML = '';
  
  initialTimeline.forEach(item => {
    addTimelineItem(item);
  });
  
  timelineUpdates.forEach(update => {
    addTimelineItem(update);
  });
}

function addTimelineItem(item) {
  const complaintTimeline = document.getElementById('complaintTimeline');
  const timelineItem = document.createElement('div');
  timelineItem.className = 'timeline-item';
  
  const markerClass = item.status === 'completed' ? 'completed' : 
                     item.status === 'active' ? 'active' : 'pending';
  
  timelineItem.innerHTML = `
    <div class="timeline-marker ${markerClass}">
      <i class="fas ${getStatusIcon(item.title)}"></i>
    </div>
    <div class="timeline-content">
      <div class="timeline-date">${item.date}</div>
      <div class="timeline-title">${item.title}</div>
      <p class="timeline-description">${item.description}</p>
      ${item.attachments && item.attachments.length > 0 ? 
        item.attachments.map(attachment => 
          `<a href="#" class="attachment-link" data-filename="${attachment.name}">
            <i class="fas fa-paperclip me-1"></i>${attachment.name}
          </a>`
        ).join('') : ''}
    </div>
  `;
  
  complaintTimeline.appendChild(timelineItem);
}

function getStatusIcon(status) {
  switch(status) {
    case 'Registration Complete': return 'fa-check';
    case 'Diagnosis In Progress': return 'fa-cog';
    case 'Repair Underway': return 'fa-tools';
    case 'Ready for Dispatch': return 'fa-shipping-fast';
    case 'Closed': return 'fa-flag-checkered';
    default: return 'fa-info-circle';
  }
}

function setupComplaintForm() {
  const updateComplaintForm = document.getElementById('updateComplaintForm');
  if (!updateComplaintForm) {
    console.error('Complaint form not found');
    return;
  }
  
  updateComplaintForm.addEventListener('submit', function(e) {
    e.preventDefault();
    
    const status = document.getElementById('statusName').value;
    const description = document.getElementById('statusDesc').value;
    const attachment = document.getElementById('attachment').files[0];
    
    // Create new timeline update
    const today = new Date();
    const dateString = `${today.getDate()}/${today.getMonth()+1}/${today.getFullYear()}`;
    
    const update = {
      date: dateString,
      title: status,
      description: description,
      status: 'active',
      attachments: attachment ? [{ name: attachment.name }] : []
    };
    
    // Add to timeline updates
    timelineUpdates.push(update);
    
    // Update timeline
    initializeTimeline();
    
    // Reset form
    updateComplaintForm.reset();
    
    // Show success message
    alert('Complaint status updated successfully!');
  });
}

function addLocationToTimeline(locationName, remarks) {
  const today = new Date();
  const dateString = `${today.getDate()}/${today.getMonth()+1}/${today.getFullYear()}`;
  
  const locationUpdate = {
    date: dateString,
    title: 'Repair Location Set',
    description: `Repair location set to ${locationName}. ${remarks ? 'Remarks: ' + remarks : ''}`,
    status: 'completed',
    attachments: []
  };
  
  timelineUpdates.push(locationUpdate);
  initializeTimeline();
}

// Export functions for other modules
window.addLocationToTimeline = addLocationToTimeline;
window.initializeTimeline = initializeTimeline;