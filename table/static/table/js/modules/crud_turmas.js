export {save_edition};
import { cods_auto_ext, cods_auto_obrig, semestre, openModal, editable} from "../main.js";

const save_edition = {
    
    extrairDados: (cell, col, row, isCod, type, vl) => {
        //Analisa sempre da célula do código do par
        const dia = isCod ? col - 1 : col - 2;
        if(!isCod) {
            cell = $(cell).prev();
            col--;
        }
        
        const cods_auto =  $.extend(cods_auto_ext, cods_auto_obrig);
        const vUsercod  = type === "d" ? vl["cod"] : $(cell).html().trim();
        const vUserProf =  type === "d" ? vl["pf"]: $(cell).next().html().trim();
    
        const cod_db =  cods_auto.hasOwnProperty(vUsercod) ? cods_auto[vUsercod] : "";
        
        // Obtém todas as células da linha
        const rowCells = $(cell).closest("tr").find("td");

        // Obtém o conteúdo da última célula da linha
        let lastCellContent = $(rowCells[rowCells.length - 1]).text();
        
        //No models a linha da tabela corresponde a um horário  
        if (row === 1 || row === 2) row--; // 10:15 - 12:00h e 8:00 - 10:15

        if(vl["extra"]){
            if(row == 4) row = 5
            else if(row == 5) row = 7
        }else{
            if(row === 5) lastCellContent = 33;

            if (row === 4 || row === 5) row = 2; //14:00 - 15:45h
            else if (row === 6) row = 4; //16:15-18:00h
            else if (row === 8 || row === 9) row = 5; //19:00 - 20:45h
            else if (row === 10 || row === 11) row = 7; //21:00 - 22:45h

        }

        if(vUsercod == "ACH0042 RP2") {
            var nomesSeparados = vUserProf.split(" / ");
            if(vl["ant_prof"]) {
                var anteriores = vl["ant_prof"].split(" / ");
                var aux = nomesSeparados
                nomesSeparados = nomesSeparados.filter(item => !anteriores.includes(item));
                anteriores = anteriores.filter(item => !aux.includes(item));
                console.log(nomesSeparados)
                console.log(anteriores)
            }
            let indice = 1
            nomesSeparados.forEach((nome) => {
                let infosParCell = {
                    "cod_disc" : cod_db,
                    "professor" : nome, 
                    "horario": row,
                    "dia": dia,
                    "cod_turma": lastCellContent,
                    "tipo": type,
                    "posicao": indice,
                    "extra": vl["extra"]
                }
                console.log(type)
                if(type === "u") {
                    vl["ant_prof"] = anteriores[indice - 1]
                    infosParCell = $.extend(infosParCell, vl);
                }    
                indice++;
                save_edition.requisicao(infosParCell, cell, row, col);
            })

        } else {
            let infosParCell = {
                "cod_disc" : cod_db,
                "professor" : vUserProf,
                "horario": row,
                "dia": dia,
                "cod_turma": lastCellContent,
                "tipo": type,
                "extra": vl["extra"]
            }
            
            if(type === "u") infosParCell = $.extend(infosParCell, vl);
            console.log("Aqui está o infosParCell") 
            console.log(infosParCell)
            save_edition.requisicao(infosParCell, cell, row, col);
        }
        
        
        
    },
    requisicao: (content, cell_cod, row, col) => {
        console.log(content)
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
                const erros = data["erros"]
                const alertas = data["alertas"]
                const cells_prof_modif = data["cells_modif"]
                const cred_err = erros.hasOwnProperty("credito")
                const prof_hr_err = erros.hasOwnProperty("prof_msm_hr")
                
                cells_prof_modif.forEach(element => {
                    let new_row = element["row"];
                    let new_col = element["col"] + 1;
                    let celula;
                    if(content["extra"]) celula = $('#tbl_ext tr:eq(' + new_row + ') td:eq(' + new_col + ')');
                    else celula = $('#tbl1 tr:eq(' + new_row + ') td:eq(' + new_col + ')');
                    
                    $(celula).html(element["new_value"]);
                });

                if(prof_hr_err){
                    const cell = $(cell_cod).next();
                    col++;
                    if(content["tipo"] === "u" && content.hasOwnProperty('ant_prof')){
                        $(cell).html(content["ant_prof"]);

                    }else if(content["tipo"] === "i"){
                        $(cell).html(""); 
                    }
                    openModal("ERRO", erros["prof_msm_hr"]);
                    $('#myModal').on('hidden.bs.modal', function () {
                        editable.edit(cell.get(0), row, col, content["extra"]);
                        location.reload(true)
                        return;
                    });
                    
                }else if(cred_err) {
                    if(content["tipo"] == "u" && content.hasOwnProperty('ant_cod')){
                        $(cell_cod).html(content["ant_cod"]);

                    }else if(content["tipo"] == "i"){
                        $(cell_cod).html("");
                    }

                    openModal("ERRO", erros["credito"]);
                    $('#myModal').on('hidden.bs.modal', function () {
                        editable.edit(cell_cod, row, col, content["extra"]);
                        location.reload(true)
                        return;
                    });       
                }else if(Object.keys(alertas).length !== 0){

                    let alerta_msg = "";

                    if(alertas.hasOwnProperty("aula_manha_noite")){
                        alerta_msg += alertas["aula_manha_noite"]
                    }

                    if(alertas.hasOwnProperty("alert2")){
                        //Alerta de quando um msm professor dá aula no noturno 2
                        // e no matutino 1 no dia posterior
                        alerta_msg += alertas["alert2"]
                    }
                    openModal("Warning(s)", alerta_msg);
                } else {
                    location.reload(true)
                }
            },
            error: (error) => {
                alert("Ocorreu um erro ao manipular as informações");
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
