document.addEventListener('DOMContentLoaded', function() {
    // Elements
    const paymentForm = document.getElementById('payment-form');
    const loadingElement = document.getElementById('loading');
    const successMessage = document.getElementById('success-message');
    const paymentMethods = document.querySelectorAll('.payment-method');
    const paymentContents = document.querySelectorAll('.payment-method-content');
    const cardOptions = document.querySelectorAll('.card-option');
    const newCardButton = document.querySelector('.new-card-button');
    const returnBtn = document.getElementById('return-btn');
    const paypalReturnBtn = document.getElementById('paypal-return-btn');
    const otherReturnBtn = document.getElementById('other-return-btn');
    const paypalBtn = document.getElementById('paypal-btn');
    const otherPayBtn = document.getElementById('other-pay-btn');
    const applyPromoBtn = document.getElementById('apply-promo');
    
    // Form inputs
    const emailInput = document.querySelector('input[name="email"]');
    const nameInput = document.querySelector('input[name="name"]');
    const cardNumberInput = document.querySelector('input[name="card_number"]');
    const expiryInput = document.querySelector('input[name="expiry"]');
    const cvvInput = document.querySelector('input[name="cvv"]');
    const streetAddressInput = document.querySelector('input[name="street_address"]');
    const cityInput = document.querySelector('input[name="city"]');
    const stateInput = document.querySelector('input[name="state"]');
    const zipCodeInput = document.querySelector('input[name="zip_code"]');
    const countryInput = document.querySelector('select[name="country"]');
    const paypalEmailInput = document.getElementById('paypal-email');
    const paymentOptions = document.querySelectorAll('input[name="other_payment"]');
    
    // Error elements
    const emailError = document.getElementById('email-error');
    const nameError = document.getElementById('name-error');
    const cardError = document.getElementById('card-error');
    const expiryError = document.getElementById('expiry-error');
    const cvvError = document.getElementById('cvv-error');
    const addressError = document.getElementById('address-error');
    const cityError = document.getElementById('city-error');
    const stateError = document.getElementById('state-error');
    const zipError = document.getElementById('zip-error');
    const countryError = document.getElementById('country-error');
    const paypalEmailError = document.getElementById('paypal-email-error');
    
    // Switch between payment methods
    paymentMethods.forEach(method => {
        method.addEventListener('click', function() {
            const methodType = this.getAttribute('data-method');
            
            // Update active tab
            paymentMethods.forEach(m => m.classList.remove('active'));
            this.classList.add('active');
            
            // Show corresponding content
            paymentContents.forEach(content => content.classList.remove('active'));
            document.getElementById(`${methodType}-method`).classList.add('active');
        });
    });
    
    // Select saved card
    cardOptions.forEach(card => {
        card.addEventListener('click', function() {
            cardOptions.forEach(c => c.classList.remove('selected'));
            this.classList.add('selected');
            
            // If you want to auto-fill form with saved card data
            const cardId = this.getAttribute('data-card-id');
            // Here you could make an AJAX call to get card details or use pre-loaded data
            // populateCardFields(cardId);
        });
    });
    
    // Add new card
    if (newCardButton) {
        newCardButton.addEventListener('click', function() {
            cardOptions.forEach(c => c.classList.remove('selected'));
            
            // Clear form fields for new card
            cardNumberInput.value = '';
            expiryInput.value = '';
            cvvInput.value = '';
            
            // Focus on card number field
            cardNumberInput.focus();
        });
    }
    
    // Input formatting
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function() {
            // Format card number with spaces after every 4 digits
            let value = this.value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
            let formattedValue = '';
            
            for (let i = 0; i < value.length; i++) {
                if (i > 0 && i % 4 === 0) {
                    formattedValue += ' ';
                }
                formattedValue += value[i];
            }
            
            this.value = formattedValue;
        });
    }
    
    if (expiryInput) {
        expiryInput.addEventListener('input', function() {
            // Format expiry date as MM/YY
            let value = this.value.replace(/[^0-9]/gi, '');
            
            if (value.length > 2) {
                this.value = value.substring(0, 2) + '/' + value.substring(2, 4);
            } else {
                this.value = value;
            }
        });
    }
    
    // Form validation
    function validateEmail(email) {
        const re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    }
    
    function validateCardNumber(cardNumber) {
        // Simplified validation, just checking if it's 16 digits
        const digits = cardNumber.replace(/\s+/g, '');
        return digits.length === 16 && /^\d+$/.test(digits);
    }
    
    function validateExpiry(expiry) {
        // Check format MM/YY and if date is in the future
        const re = /^(0[1-9]|1[0-2])\/([0-9]{2})$/;
        if (!re.test(expiry)) return false;
        
        const [month, year] = expiry.split('/');
        const expiryDate = new Date(2000 + parseInt(year), parseInt(month) - 1, 1);
        const today = new Date();
        
        return expiryDate > today;
    }
    
    function validateCVV(cvv) {
        // Check if CVV is 3 or 4 digits
        return /^[0-9]{3,4}$/.test(cvv);
    }
    
    function validateForm() {
        let isValid = true;
        
        // Reset errors
        emailError.style.display = 'none';
        nameError.style.display = 'none';
        cardError.style.display = 'none';
        expiryError.style.display = 'none';
        cvvError.style.display = 'none';
        addressError.style.display = 'none';
        cityError.style.display = 'none';
        stateError.style.display = 'none';
        zipError.style.display = 'none';
        countryError.style.display = 'none';
        
        // Email validation
        if (!validateEmail(emailInput.value)) {
            emailError.style.display = 'block';
            isValid = false;
        }
        
        // Name validation
        if (nameInput.value.trim() === '') {
            nameError.style.display = 'block';
            isValid = false;
        }
        
        // Card validation
        if (!validateCardNumber(cardNumberInput.value)) {
            cardError.style.display = 'block';
            isValid = false;
        }
        
        // Expiry validation
        if (!validateExpiry(expiryInput.value)) {
            expiryError.style.display = 'block';
            isValid = false;
        }
        
        // CVV validation
        if (!validateCVV(cvvInput.value)) {
            cvvError.style.display = 'block';
            isValid = false;
        }
        
        // Address validation
        if (streetAddressInput.value.trim() === '') {
            addressError.style.display = 'block';
            isValid = false;
        }
        
        // City validation
        if (cityInput.value.trim() === '') {
            cityError.style.display = 'block';
            isValid = false;
        }
        
        // State validation
        if (stateInput.value.trim() === '') {
            stateError.style.display = 'block';
            isValid = false;
        }
        
        // ZIP validation
        if (zipCodeInput.value.trim() === '') {
            zipError.style.display = 'block';
            isValid = false;
        }
        
        // Country validation
        if (countryInput.value === '') {
            countryError.style.display = 'block';
            isValid = false;
        }
        
        return isValid;
    }
    
    function validatePaypalForm() {
        // Reset error
        paypalEmailError.style.display = 'none';
        
        // Email validation
        if (!validateEmail(paypalEmailInput.value)) {
            paypalEmailError.style.display = 'block';
            return false;
        }
        
        return true;
    }
    
    function validateOtherPaymentForm() {
        let selected = false;
        
        paymentOptions.forEach(option => {
            if (option.checked) {
                selected = true;
            }
        });
        
        return selected;
    }
    
    // Form submission
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (validateForm()) {
                // Show loading state
                loadingElement.style.display = 'flex';
                
                // Simulate payment processing
                setTimeout(function() {
                    // Hide loading state
                    loadingElement.style.display = 'none';
                    
                    // Show success message
                    successMessage.style.display = 'block';
                    
                    // Redirect to confirmation page after delay
                    setTimeout(function() {
                        window.location.href = '/';
                    }, 340);
                }, 2000);
            }
        });
    }
    
    // PayPal button
    if (paypalBtn) {
        paypalBtn.addEventListener('click', function() {
            if (validatePaypalForm()) {
                // Show loading
                loadingElement.style.display = 'flex';
                
                // Simulate redirection to PayPal
                setTimeout(function() {
                    window.location.href = 'https://www.paypal.com/checkoutnow';
                }, 1000);
            }
        });
    }
    
    // Other payment button
    if (otherPayBtn) {
        otherPayBtn.addEventListener('click', function() {
            if (validateOtherPaymentForm()) {
                // Handle other payment methods
                let selectedMethod;
                
                paymentOptions.forEach(option => {
                    if (option.checked) {
                        selectedMethod = option.value;
                    }
                });
                
                // Show loading
                loadingElement.style.display = 'flex';
                
                // Simulate processing
                setTimeout(function() {
                    // Handle different payment methods
                    switch (selectedMethod) {
                        case 'bank-transfer':
                            // Redirect to bank transfer page
                            window.location.href = '/bank-transfer/';
                            break;
                        case 'apple-pay':
                            // Open Apple Pay
                            alert('Opening Apple Pay...');
                            break;
                        case 'google-pay':
                            // Open Google Pay
                            alert('Opening Google Pay...');
                            break;
                        default:
                            // Default action
                            window.location.href = '/payment/';
                    }
                }, 1000);
            } else {
                alert('Please select a payment method');
            }
        });
    }
    
    // Return buttons
    if (returnBtn) {
        returnBtn.addEventListener('click', function() {
            window.location.href = '/cart/';
        });
    }
    
    if (paypalReturnBtn) {
        paypalReturnBtn.addEventListener('click', function() {
            window.location.href = '/cart/';
        });
    }
    
    if (otherReturnBtn) {
        otherReturnBtn.addEventListener('click', function() {
            window.location.href = '/cart/';
        });
    }
    
    // Apply promo code
    let promo_codes=['NEWUSER','GETDISC','GETSALE','SALES40','SAVE$$','PRICEY','FRESH']
    if (applyPromoBtn) {
        applyPromoBtn.addEventListener('click', function() {
            const promoCode = document.getElementById('promo').value.trim();
            
            if (promoCode !== '') {
                // Show loading
                loadingElement.style.display = 'flex';
                
                // Simulate promo code checking
                setTimeout(function() {
                    // Hide loading
                    loadingElement.style.display = 'none';
                    
                    // Check if promo code is valid (this would be done on the server)
                    if (promo_codes.includes(promoCode)) {
                        // Add discount to the summary
                        const summaryTotals = document.querySelector('.summary-totals');
                        
                        // Check if discount already exists
                        let discountRow = document.querySelector('.summary-row.discount');
                        
                        if (!discountRow) {
                            // Create new discount row
                            discountRow = document.createElement('div');
                            discountRow.className = 'summary-row discount';
                            discountRow.innerHTML = '<span>Discount</span><span>-$10.00</span>';
                            
                            // Insert before total
                            const totalRow = document.querySelector('.summary-row.total');
                            summaryTotals.insertBefore(discountRow, totalRow);
                            
                            // Update total
                            const totalAmount = document.querySelector('.summary-row.total span:last-child');
                            const currentTotal = parseFloat(totalAmount.textContent.replace('$', ''));
                            totalAmount.textContent = '$' + (currentTotal - 10).toFixed(2);
                            
                            // Show success message
                            alert('Promo code applied successfully!');
                        } else {
                            alert('Promo code already applied!');
                        }
                    } else {
                        alert('Invalid promo code');
                    }
                }, 1000);
            } else {
                alert('Please enter a promo code');
            }
        });
    }
});