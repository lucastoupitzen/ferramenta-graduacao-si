export {controlaPopUp}

import { coresRestrições } from "../main";
function controlaPopUp(cell, apelidos) {

        let resposta = {};

        document.getElementById("popup").style.display = "block";
        
        document.getElementById("closePopup").addEventListener("click", function() {
            document.getElementById("popup").style.display = "none";
            coresRestrições();
        });
        
        document.getElementById("submitForm").addEventListener("click", function() {

            const campo1Value = document.querySelector(".campo1").value;
            const campo2Value = document.querySelector(".campo2").value;

            resposta = {
                professor1: campo1Value,
                professor2: campo2Value
            }
            
            campo1Value ? resposta.professor1 = apelidos[resposta.professor1] : ""
            campo2Value ? resposta.professor2 = apelidos[resposta.professor2] : ""
            
            let resp = []
            if(resposta.professor1 != "") resp.push(resposta.professor1)
            if(resposta.professor2 != "") resp.push(resposta.professor2)
    
            // Feche o pop-up
            document.getElementById("popup").style.display = "none";
            cell.html(resp.join(" / "));
            coresRestrições();

        });
    
    }

