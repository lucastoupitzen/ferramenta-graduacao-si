// código daptado de rp1Table.js
const auto_profs = JSON.parse(document.getElementById("auto_profs").textContent);

function openModal(title, messages) {
    const modalBody = document.getElementById("modalBody");
    modalBody.innerText = messages;
    $("#myModalLabel").html(title);
    const myModal = new bootstrap.Modal(document.getElementById("myModal"));
    myModal.show();
}

$(document).ready(function() {
    $(".icone").mouseover(function() {
        $(this).css("color", "blue");
    });

    $(".icone").mouseout(function() {
        $(this).css("color", "");
    });

    //Abre popUp
    $(document).on('click', '.icone', function (e) {              
        const cell = $(this).closest('td');
        const row = cell.closest('tr');

        //carrega o nome no popup
        $("#prof_tadi").val("");

        row.find('.n_completo').each(function(){
            $("#prof_tadi").val($(this).text().trim());
        });

        $("#popup").show();
        $("#submitForm").off("click").on("click", function(){
            controlaPopUp(cell.prev(), auto_profs);
        });
    });


    $(function() {
        $("#prof_tadi").autocomplete({
            source: function(request, response) {
                let results = $.ui.autocomplete.filter(Object.keys(auto_profs), request.term);
                response(results);
            },
            minLength: 2
        })
    });

    $("#closePopup").on("click", function(){
        $("#popup").hide()
    })

    function controlaPopUp(cell, apelidos){

        let resposta = {};
        const campo1Value = document.querySelector(".campo1").value;
    
        resposta = {
            professor: campo1Value,
        }
        
        campo1Value ? resposta.professor = apelidos[resposta.professor] : ""

        
        let resp = []
        if(resposta.professor1 != "") resp.push(resposta.professor)

        //valida nomes
        let validInput = true;
        const lProfs = [campo1Value];
        let nomeEncontrado = false; 
        const idAlerta = "#0";

        $(idAlerta).hide()
        if (auto_profs.hasOwnProperty(lProfs[0])) nomeEncontrado = true;
        if(lProfs[0] === "") nomeEncontrado = true;

        if (!nomeEncontrado) {
            $(idAlerta).html("Nome inválido");
            $(idAlerta).css("color", "red");
            $(idAlerta).css("font-size", "12px");
            $(idAlerta).show()
            validInput = false;
        }       

        if(validInput){
            const myEvent = { 
                id: $(cell).prev().text(),
                lProfs: lProfs,
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
                    console.log(data)
                    const erros = data["erros"]
                    const alertas = data["alertas"]
                    const cred_err = erros.hasOwnProperty("credito")
                    const prof_hr_err = erros.hasOwnProperty("prof_msm_hr")
                    if(prof_hr_err){
                        openModal("ERRO", erros["prof_msm_hr"]);
                        $('#myModal').on('hidden.bs.modal', function () {
                            editable.edit(cell.get(0), row, col, content["extra"]);
                            return;
                        });
                    }
                    else if(cred_err) {
                        openModal("ERRO", erros["credito"]);
                        $('#myModal').on('hidden.bs.modal', function () {
                            editable.edit(cell_cod, row, col, content["extra"]);
                            return;
                        });       
                    }
                    else if(Object.keys(alertas).length !== 0){

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
                    }
                },
                error: (error) => {
                    alert("Ocorreu um erro ao manipular as informações");
                }
            });

            const row = cell.closest('tr');
            row.find('.n_completo').remove();
            lProfs.forEach(nome => {
                row.append('<td class="d-none n_completo">'+nome+'</td>')
            });
            $("#popup").hide();
            cell.html(resp.join(","));
        }
    }
});

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