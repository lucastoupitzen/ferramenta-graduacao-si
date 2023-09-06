export {save_edition};
import { cods_auto_ext, cods_auto_obrig, semestre} from "../main.js";

const save_edition = {
    
    extrairDados: (cell, col, row, isCod, type, vl) => {
        //Analisa sempre da célula do código do par
        if(!isCod) cell = $(cell).prev();
        
        const cods_auto =  $.extend(cods_auto_ext, cods_auto_obrig);
        const vUsercod  = type === "d" ? vl["cod"] : $(cell).html().trim();
        const vUserProf =  type === "d" ? vl["pf"]: $(cell).next().html().trim();
        const cod_db =  cods_auto.hasOwnProperty(vUsercod) ? cods_auto[vUsercod] : "";
        
        // Obtém todas as células da linha
        const rowCells = $(cell).closest("tr").find("td");

        // Obtém o conteúdo da última célula da linha
        // 33 é um número de turma arbitrário para linha 5
        // Assim como o 3 para as turmas do vespertinho
        const lastCellContent = row != 5 ? $(rowCells[rowCells.length - 1]).text() : 33;
        
        //No models a linha da tabela corresponde a um horário
        if (row === 1 || row === 2) {
            row--; // 10:15 - 12:00h
        } else if (row === 4 || row === 5) {
            row = 2; //14:00 - 15:45h
        } else if (row === 6) {
            row = 4; //16:15-18:00h
        } else if (row === 8 || row === 9) {
            row = 5; //19:00 - 20:45h
        } else if (row === 10 || row === 11) {
            row = 7; //21:00 - 22:45h
        }
        col = isCod ? col - 1 : col - 2;
        let infosParCell = {
            "cod_disc" : cod_db,
            "professor" : vUserProf,
            "horario": row,
            "dia": col,
            "cod_turma": lastCellContent,
            "tipo": type
        }
        
        if(type == "u") infosParCell = $.extend(infosParCell, vl);
        save_edition.requisicao(infosParCell);
    },
    requisicao: (content) => {
        const myEvent = { 
            info: content,
            semestre: semestre,
            csrfmiddlewaretoken: window.CSRF_TOKEN
        };

        $.ajax({
            url: $("#url-data").data("url"),
            type: "POST",
            dataType: "json",
            data: JSON.stringify(myEvent),
            headers: {
              "X-Requested-With": "XMLHttpRequest",
              "X-CSRFToken": getCookie("csrftoken"), 
            },
            success: (data) => {
              console.log(data);
            },
            error: (error) => {
              console.log(error);
            }
        });
    }

}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}