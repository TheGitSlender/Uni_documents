function validerFormulaire() {
    const dateNaissance = new Date(document.getElementById('dateNaissance').value);
    const motDePasse = document.getElementById('motDePasse').value;
    const confirmationMotDePasse = document.getElementById('confirmationMotDePasse').value;
    
    document.getElementById('ageError').style.display = 'none';
    document.getElementById('passwordError').style.display = 'none';
    
    let isValid = true;
    
    const today = new Date();
    const age = today.getFullYear() - dateNaissance.getFullYear();
    const monthDiff = today.getMonth() - dateNaissance.getMonth();
    
    if (age < 14 || (age === 14 && monthDiff < 0) || 
        (age === 14 && monthDiff === 0 && today.getDate() < dateNaissance.getDate())) {
        document.getElementById('ageError').style.display = 'block';
        isValid = false;
    }
    
    if (motDePasse !== confirmationMotDePasse) {
        document.getElementById('passwordError').style.display = 'block';
        isValid = false;
    }
    
    if (isValid) {
        alert("Formulaire validé avec succès!");
    }
}