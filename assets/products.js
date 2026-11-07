/* One list for every product card on the site. Change a status here and every page follows.
   status: 'available' (can order) · 'enquire' (check availability) · 'unavailable' (not now) · 'planned' (in development)
   Keep this list in step with what RYNOR can actually supply. All products are currently not available. */
window.RYNOR_PRODUCTS = [
  { id: 'bags', category: 'bags', title: 'CAPD dialysis fluid bags · 2 L', image: 'fluid-bags', status: 'unavailable',
    summary: '2 litre dialysis fluid bags for continuous ambulatory peritoneal dialysis (CAPD), used with CAPD tubing.',
    details: ['Size: 2 L', 'For CAPD', 'Pack details on request'] },
  { id: 'bags-apd', category: 'bags', title: 'APD dialysis fluid bags · 5 L', image: 'fluid-bags', status: 'unavailable',
    summary: '5 litre dialysis fluid bags for automated peritoneal dialysis (APD), planned for use with the RYNOR machine.',
    details: ['Size: 5 L', 'For APD', 'In development with the machine'] },
  { id: 'tubing', category: 'tubing', title: 'CAPD tubing', image: 'tubing', status: 'unavailable',
    summary: 'Tubing for CAPD exchanges with the 2 L fluid bags. Configuration and compatibility confirmed before supply.',
    details: ['For CAPD', 'Configuration confirmed on enquiry', 'Compatibility to be confirmed'] },
  { id: 'tubing-apd', category: 'tubing', title: 'APD tubing set', image: 'apd-tubing', status: 'unavailable',
    summary: 'Cycler tubing set for automated peritoneal dialysis, connecting the 5 L fluid bags, the APD machine and the patient line.',
    details: ['For APD', 'For use with the RYNOR cycler', 'In development with the machine'] },
  { id: 'transfer', category: 'transfer-sets', title: 'PD transfer sets', image: 'transfer-sets', status: 'unavailable',
    summary: 'Transfer sets connecting the catheter to the exchange system.',
    details: ['Connector configuration on request', 'Pack details on request'] },
  { id: 'catheters', category: 'catheters', title: 'Peritoneal dialysis catheters', image: 'catheters', status: 'unavailable',
    summary: 'Planned catheter portfolio with swan-neck and curled variants.',
    details: ['Swan-neck variants', 'Curled variants', 'Sizes and specifications in development'] },
  { id: 'caps', category: 'caps', title: 'Mini-caps', image: 'caps', status: 'unavailable',
    summary: 'Protective mini-caps that close the connection after each exchange, used by CAPD and APD patients.',
    details: ['For CAPD and APD', 'Single use', 'Pack details on request'] },
  { id: 'exit-site', category: 'caps', title: 'Exit-site care kit', image: 'exit-site-care', status: 'unavailable',
    summary: 'Sterile gauze, dressings and antiseptic for cleaning and protecting the catheter exit site, as advised by your PD nurse.',
    details: ['Sterile gauze and dressings', 'Antiseptic for exit-site cleaning', 'For daily catheter care'] },
  { id: 'hand-hygiene', category: 'caps', title: 'Hand rub & face masks', image: 'hand-hygiene', status: 'unavailable',
    summary: 'Alcohol-based hand rub and face masks, used before every connection to keep exchanges clean.',
    details: ['Alcohol-based hand rub', 'Face masks', 'Used before every connection'] },
  { id: 'swabs', category: 'caps', title: 'Alcohol swabs & surface wipes', image: 'swabs', status: 'unavailable',
    summary: 'Alcohol swabs and disinfectant wipes for cleaning the work surface and equipment before an exchange.',
    details: ['Alcohol swabs', 'Surface disinfectant wipes', 'For a clean exchange area'] }
];
window.RYNOR_STATUS = {
  available: ['Available to order', 'quote', 'Request a quote'],
  enquire: ['Check availability', 'quote', 'Request a quote'],
  unavailable: ['Not currently available', 'notify', 'Notify me'],
  planned: ['In development', 'notify', 'Notify me']
};
