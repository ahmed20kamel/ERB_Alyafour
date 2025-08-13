document.addEventListener('DOMContentLoaded', function () {
    function toggleInlines() {
        const type = document.querySelector('#id_customer_type')?.value;

        const inlines = Array.from(document.querySelectorAll('fieldset.module'));
        inlines.forEach(fieldset => {
            const title = fieldset.querySelector('h2')?.innerText || "";
            const isOwner = title.includes('Owner Profile') || title.includes('Authorized Persons');
            const isCompany = title.includes('Company Profile') || title.includes('Contact Persons') || title.includes('Legal Person');

            if (type === 'owner') {
                fieldset.style.display = isCompany ? 'none' : 'block';
            } else if (type === 'commercial' || type === 'consultant') {
                fieldset.style.display = isOwner ? 'none' : 'block';
            } else {
                fieldset.style.display = 'none';
            }
        });
    }

    const typeField = document.querySelector('#id_customer_type');
    if (typeField) {
        typeField.addEventListener('change', toggleInlines);
        toggleInlines();  // أول تنفيذ عند تحميل الصفحة
    }
});
