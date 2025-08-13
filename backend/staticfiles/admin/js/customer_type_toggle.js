document.addEventListener('DOMContentLoaded', function () {
    const customerTypeField = document.querySelector('#id_customer_type');
    if (!customerTypeField) return;

    function toggleSections() {
        const type = customerTypeField.value;

        // hide all inlines
        const inlineGroups = document.querySelectorAll('.inline-group');
        inlineGroups.forEach(el => el.style.display = 'none');

        // show based on type
        if (type === 'owner') {
            showIfExists('person');          // شخص مالك
            showIfExists('authorizedperson'); // مفوضين
        } else if (type === 'commercial' || type === 'consultant') {
            showIfExists('company');
            showIfExists('legalperson');
            showIfExists('contactperson');
        }
    }

    function showIfExists(modelName) {
        const el = document.querySelector(`#${modelName}-group`);
        if (el) el.style.display = '';
    }

    customerTypeField.addEventListener('change', toggleSections);
    toggleSections();
});
