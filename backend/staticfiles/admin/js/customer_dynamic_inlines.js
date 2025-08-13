document.addEventListener('DOMContentLoaded', function () {
    const customerTypeField = document.getElementById('id_customer_type');

    function toggleInlines() {
        const type = customerTypeField.value;

        document.querySelectorAll('.owner-inline').forEach(el => el.style.display = 'none');
        document.querySelectorAll('.company-inline').forEach(el => el.style.display = 'none');
        document.querySelectorAll('.bank-inline').forEach(el => el.style.display = 'none');

        if (type === 'owner') {
            document.querySelectorAll('.owner-inline').forEach(el => el.style.display = '');
            document.querySelectorAll('.bank-inline').forEach(el => el.style.display = '');
        } else if (type === 'commercial') {
            document.querySelectorAll('.company-inline').forEach(el => el.style.display = '');
            document.querySelectorAll('.bank-inline').forEach(el => el.style.display = '');
        } else if (type === 'consultant') {
            document.querySelectorAll('.bank-inline').forEach(el => el.style.display = '');
        }
    }

    if (customerTypeField) {
        toggleInlines();
        customerTypeField.addEventListener('change', toggleInlines);
    }
});
