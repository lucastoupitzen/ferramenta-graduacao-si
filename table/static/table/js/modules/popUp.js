export {popUp}

const popUp = {
    controla_popup:() => {
        document.getElementById("showPopup").addEventListener("click", function() {
            document.getElementById("popup").style.display = "block";
        });
        
        document.getElementById("closePopup").addEventListener("click", function() {
            document.getElementById("popup").style.display = "none";
        });
        
        document.getElementById("submitForm").addEventListener("click", function() {
            const campo1Value = document.getElementById("campo1").value;
            const campo2Value = document.getElementById("campo2").value;
            const campo3Value = document.getElementById("campo3").value;
        
        
            // Feche o pop-up
            document.getElementById("popup").style.display = "none";
        });
    
        const showPopupButton = document.getElementById("showPopup");
        const popup = document.getElementById("popup");
        const closePopupButton = document.getElementById("closePopup");
    
        showPopupButton.addEventListener("click", function() {
            popup.style.display = "block";
    
            // Adicione um ouvinte de eventos ao elemento de fundo semi-transparente (popup) para fechar o pop-up quando clicar fora dele
            popup.addEventListener("click", function(event) {
                if (event.target === popup) {
                    popup.style.display = "none";
                }
            });
        });
    
        closePopupButton.addEventListener("click", function() {
            popup.style.display = "none";
        });
    
        document.getElementById("submitForm").addEventListener("click", function() {
            const campo1Value = document.getElementById("campo1").value;
            const campo2Value = document.getElementById("campo2").value;
            const campo3Value = document.getElementById("campo3").value;
    
            // Feche o pop-up
            popup.style.display = "none";
        });
    
    }
}

