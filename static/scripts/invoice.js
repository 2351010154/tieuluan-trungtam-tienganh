
window.openPaymentWindow = function openPaymentWindow(enrollment_id) {
  window.open(`/invoice?enrollment_id=${enrollment_id}`, '_blank');
}