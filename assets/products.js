/* One list for every product card on the site. Change a status here and every page follows.
   status: 'available' (can order) · 'enquire' (check availability) · 'unavailable' (not now) · 'planned' (in development)
   Keep this list in step with what RYNOR can actually supply. */
window.RYNOR_PRODUCTS = [
  { id: 'bags', category: 'bags', title: 'CAPD dialysis fluid bags · 2 L', image: 'fluid-bags', status: 'unavailable',
    summary: '2 litre dialysis fluid bags for continuous ambulatory peritoneal dialysis (CAPD), used with CAPD tubing.',
    details: ['Size: 2 L', 'For CAPD', 'Pack details on request'] },
  { id: 'bags-apd', category: 'bags', title: 'APD dialysis fluid bags · 5 L', image: 'fluid-bags', status: 'planned',
    summary: '5 litre dialysis fluid bags planned for automated peritoneal dialysis (APD) with the RYNOR machine.',
    details: ['Size: 5 L', 'For APD', 'In development with the machine'] },
  { id: 'tubing', category: 'tubing', title: 'CAPD tubing', image: 'tubing', status: 'unavailable',
    summary: 'Tubing for CAPD exchanges with the 2 L fluid bags. Configuration and compatibility confirmed before supply.',
    details: ['Configuration confirmed on enquiry', 'Compatibility to be confirmed'] },
  { id: 'transfer', category: 'transfer-sets', title: 'PD transfer sets', image: 'transfer-sets', status: 'enquire',
    summary: 'Transfer sets connecting the catheter to the exchange system.',
    details: ['Connector configuration on request', 'Pack details on request'] },
  { id: 'catheters', category: 'catheters', title: 'Peritoneal dialysis catheters', image: 'catheters', status: 'planned',
    summary: 'Planned catheter portfolio with swan-neck and curled variants.',
    details: ['Swan-neck variants', 'Curled variants', 'Sizes and specifications in development'] },
  { id: 'caps', category: 'caps', title: 'Mini-caps & disinfection accessories', image: 'caps', status: 'planned',
    summary: 'Protective mini-caps and disinfection accessories for daily PD care.',
    details: ['Mini-caps', 'Disinfection accessories', 'Packaging in development'] }
];
window.RYNOR_STATUS = {
  available: ['Available to order', 'quote', 'Request a quote'],
  enquire: ['Check availability', 'quote', 'Request a quote'],
  unavailable: ['Not currently available', 'notify', 'Notify me'],
  planned: ['In development', 'notify', 'Notify me']
};
