// static/main.js

console.log("Sanity check!");

// new
// Get Stripe publishable key
var endpointUrl = 'http://127.0.0.1:8000/ar/api/payment/config/';
fetch(endpointUrl)
.then((result) => { return result.json(); })
.then((data) => {
  // Initialize Stripe.js
  console.log(data);
  const stripe = Stripe(data.publicKey);
  
// new
  // Event handler
  document.querySelector("#submitBtn").addEventListener("click", () => {
    // Get Checkout Session ID
    var data1 = {
        'live_session_list':[11,82],
        'subscriptionID':41,
      
    };
  
    var end='http://127.0.0.1:8000/ar/api/payment/create-checkout-session/'
    fetch(end, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Token 100a83af62dace4da77f73b50835adcb25a94dad'
      },
      body: JSON.stringify(data1)
    })
    .then((result) => { return result.json(); })
    .then((data) => {
      console.log(data);
      // Redirect to Stripe Checkout
      return stripe.redirectToCheckout({sessionId: data.sessionId})
    })
    .then((res) => {
      console.log(res);
    });
  });

  document.querySelector("#connectBtn").addEventListener("click", () => {
    // Get Checkout Session ID
    console.log(" connect");
    var end='http://127.0.0.1:8000/en/api/payment/authorize/'
    fetch(end)

    var connectBtn = document.getElementById('connectBtn');
  
  // Attach a click event listener to the button
  connectBtn.addEventListener('click', function() {
    fetch(end)
  });
  });




});
